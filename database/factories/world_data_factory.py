"""
World Data Factory

world_design.md 파일을 파싱하여 계층적 게임 데이터를 생성하는 Factory
"""
from typing import Optional, Dict, Any, List
import json
import re
from pathlib import Path

from .game_data_factory import GameDataFactory
from ..connection import DatabaseConnection


class WorldDataFactory(GameDataFactory):
    """
    World Design 문서를 파싱하여 계층적 게임 데이터를 생성하는 Factory
    
    GameDataFactory를 확장하여 Region 단위 일괄 생성 기능 제공
    """
    
    def __init__(self):
        super().__init__()
    
    async def create_region_with_children(
        self,
        region_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Region과 하위 엔티티들을 일괄 생성
        
        Args:
            region_config: Region 설정 딕셔너리
                {
                    "region_id": "REG_...",
                    "region_name": "...",
                    "region_type": "...",
                    "description": "...",
                    "properties": {...},
                    "locations": [
                        {
                            "location_id": "LOC_...",
                            "location_name": "...",
                            "description": "...",
                            "properties": {...},
                            "cells": [
                                {
                                    "cell_id": "CELL_...",
                                    "cell_name": "...",
                                    "description": "...",
                                    "properties": {...},
                                    "matrix_width": 20,
                                    "matrix_height": 20,
                                    "characters": [
                                        {
                                            "entity_id": "NPC_...",
                                            "entity_name": "...",
                                            "entity_type": "npc",
                                            "base_stats": {...},
                                            "entity_properties": {...},
                                            "default_position_3d": {...},
                                            "entity_size": "medium"
                                        }
                                    ],
                                    "world_objects": [
                                        {
                                            "object_id": "OBJ_...",
                                            "object_type": "interactive",
                                            "object_name": "...",
                                            "properties": {...}
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
        
        Returns:
            생성된 엔티티들의 ID 딕셔너리
            {
                "region_id": "...",
                "location_ids": [...],
                "cell_ids": [...],
                "entity_ids": [...],
                "object_ids": [...]
            }
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                result = {
                    "region_id": None,
                    "location_ids": [],
                    "cell_ids": [],
                    "entity_ids": [],
                    "object_ids": []
                }
                
                # 1. Region 생성
                region_id = await self.create_world_region(
                    region_id=region_config["region_id"],
                    region_name=region_config["region_name"],
                    region_type=region_config.get("region_type", "region"),
                    description=region_config.get("description", ""),
                    properties=region_config.get("properties", {})
                )
                result["region_id"] = region_id
                
                # 2. Locations 생성
                locations = region_config.get("locations", [])
                for location_config in locations:
                    location_id = await self.create_world_location(
                        location_id=location_config["location_id"],
                        region_id=region_id,
                        location_name=location_config["location_name"],
                        description=location_config.get("description", ""),
                        properties=location_config.get("properties", {})
                    )
                    result["location_ids"].append(location_id)
                    
                    # 3. Cells 생성
                    cells = location_config.get("cells", [])
                    for cell_config in cells:
                        cell_id = await self.create_world_cell(
                            cell_id=cell_config["cell_id"],
                            location_id=location_id,
                            cell_name=cell_config.get("cell_name", ""),
                            matrix_width=cell_config.get("matrix_width", 20),
                            matrix_height=cell_config.get("matrix_height", 20),
                            cell_description=cell_config.get("description", ""),
                            cell_properties=cell_config.get("properties", {})
                        )
                        result["cell_ids"].append(cell_id)
                        
                        # 4. Characters (Entities) 생성
                        characters = cell_config.get("characters", [])
                        for char_config in characters:
                            entity_id = await self._create_character_in_cell(
                                char_config, cell_id
                            )
                            if entity_id:
                                result["entity_ids"].append(entity_id)
                        
                        # 5. World Objects 생성
                        world_objects = cell_config.get("world_objects", [])
                        for obj_config in world_objects:
                            object_id = await self._create_world_object_in_cell(
                                obj_config, cell_id
                            )
                            if object_id:
                                result["object_ids"].append(object_id)
                
                return result
    
    async def _create_character_in_cell(
        self,
        char_config: Dict[str, Any],
        cell_id: str
    ) -> Optional[str]:
        """Cell 내 Character 생성 헬퍼 메서드"""
        try:
            entity_id = char_config["entity_id"]
            entity_name = char_config["entity_name"]
            entity_type = char_config.get("entity_type", "npc")
            base_stats = char_config.get("base_stats", {})
            entity_properties = char_config.get("entity_properties", {})
            default_position_3d = char_config.get("default_position_3d")
            entity_size = char_config.get("entity_size", "medium")
            
            # cell_id를 entity_properties에 추가
            entity_properties["cell_id"] = cell_id
            
            # default_position_3d에 cell_id 추가
            if default_position_3d:
                default_position_3d["cell_id"] = cell_id
            else:
                # 기본 위치 생성
                default_position_3d = {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0,
                    "rotation_y": 0,
                    "cell_id": cell_id
                }
            
            # NPC 템플릿 생성
            base_properties = {
                "default_position_3d": default_position_3d,
                "entity_size": entity_size
            }
            
            # behavior는 별도로 전달하고, 나머지 entity_properties는 additional_properties로 전달
            behavior = entity_properties.pop("behavior", {})
            additional_properties = entity_properties  # cell_id, occupation, personality, dialogue 등 포함
            
            return await self.create_npc_template(
                template_id=entity_id,
                name=entity_name,
                template_type=entity_type,
                base_stats=base_stats,
                base_properties=base_properties,
                behavior_properties=behavior,
                additional_properties=additional_properties
            )
        except Exception as e:
            print(f"Error creating character {char_config.get('entity_id', 'unknown')}: {e}")
            return None
    
    async def _create_world_object_in_cell(
        self,
        obj_config: Dict[str, Any],
        cell_id: str
    ) -> Optional[str]:
        """Cell 내 World Object 생성 헬퍼 메서드"""
        try:
            object_id = obj_config["object_id"]
            object_type = obj_config["object_type"]
            object_name = obj_config["object_name"]
            
            # default_position에 cell_id 정보 포함
            default_position = obj_config.get("default_position", {})
            if not default_position:
                default_position = {"x": 0.0, "y": 0.0}
            
            return await self.create_world_object(
                object_id=object_id,
                object_type=object_type,
                object_name=object_name,
                default_cell_id=cell_id,
                default_position=default_position,
                interaction_type=obj_config.get("interaction_type"),
                possible_states=obj_config.get("possible_states"),
                properties=obj_config.get("properties", {}),
                wall_mounted=obj_config.get("wall_mounted", False),
                passable=obj_config.get("passable", False),
                movable=obj_config.get("movable", False),
                object_height=obj_config.get("object_height", 1.0),
                object_width=obj_config.get("object_width", 1.0),
                object_depth=obj_config.get("object_depth", 1.0),
                object_weight=obj_config.get("object_weight", 0.0),
                object_description=obj_config.get("description", "")
            )
        except Exception as e:
            print(f"Error creating world object {obj_config.get('object_id', 'unknown')}: {e}")
            return None
    
    def parse_world_design_markdown(
        self,
        file_path: Path
    ) -> List[Dict[str, Any]]:
        """
        world_design.md 파일을 파싱하여 Region 설정 리스트 반환
        
        Args:
            file_path: world_design.md 파일 경로
        
        Returns:
            Region 설정 딕셔너리 리스트
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        regions = []
        
        # 마크다운 헤더를 기반으로 구조 파싱
        # 대륙 섹션 찾기
        continent_pattern = r'^#\s+(.+?)$'
        region_pattern = r'^##\s+(.+?)$'
        location_pattern = r'^###\s+(.+?)$'
        
        lines = content.split('\n')
        current_region = None
        current_location = None
        current_cell = None
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 대륙 헤더 (무시, 메타 정보)
            if re.match(continent_pattern, line):
                match = re.match(continent_pattern, line)
                continent_name = match.group(1) if match else ""
                # 대륙 정보는 메타데이터로 저장
                i += 1
                continue
            
            # Region 헤더 (##)
            if re.match(region_pattern, line):
                match = re.match(region_pattern, line)
                region_name = match.group(1) if match else ""
                
                # 이전 Region 저장
                if current_region:
                    regions.append(current_region)
                
                # 새 Region 시작
                current_region = {
                    "region_id": self._generate_region_id(region_name),
                    "region_name": region_name,
                    "region_type": "region",
                    "description": "",
                    "properties": {},
                    "locations": []
                }
                current_location = None
                current_cell = None
                i += 1
                continue
            
            # Location 헤더 (###)
            if re.match(location_pattern, line):
                match = re.match(location_pattern, line)
                location_name = match.group(1) if match else ""
                
                if not current_region:
                    # Region 없이 Location이 나온 경우, 기본 Region 생성
                    current_region = {
                        "region_id": self._generate_region_id("Unknown"),
                        "region_name": "Unknown",
                        "region_type": "region",
                        "description": "",
                        "properties": {},
                        "locations": []
                    }
                
                # 이전 Location 저장
                if current_location:
                    current_region["locations"].append(current_location)
                
                # 새 Location 시작
                current_location = {
                    "location_id": self._generate_location_id(region_name, location_name),
                    "location_name": location_name,
                    "description": "",
                    "properties": {},
                    "cells": []
                }
                current_cell = None
                i += 1
                continue
            
            # 설명 텍스트 수집
            if line and not line.startswith('#'):
                if current_cell:
                    # Cell 설명
                    if not current_cell.get("description"):
                        current_cell["description"] = line
                    else:
                        current_cell["description"] += "\n" + line
                elif current_location:
                    # Location 설명
                    if not current_location.get("description"):
                        current_location["description"] = line
                    else:
                        current_location["description"] += "\n" + line
                elif current_region:
                    # Region 설명
                    if not current_region.get("description"):
                        current_region["description"] = line
                    else:
                        current_region["description"] += "\n" + line
            
            i += 1
        
        # 마지막 Region 저장
        if current_location:
            current_region["locations"].append(current_location)
        if current_region:
            regions.append(current_region)
        
        return regions
    
    def _generate_region_id(self, region_name: str) -> str:
        """Region ID 생성 (REG_[대륙]_[지역]_[일련번호])"""
        # 한글을 로마자로 변환 (간단한 매핑)
        region_code = self._korean_to_code(region_name)
        return f"REG_{region_code}_01"
    
    def _generate_location_id(self, region_name: str, location_name: str) -> str:
        """Location ID 생성 (LOC_[지역]_[장소]_[일련번호])"""
        region_code = self._korean_to_code(region_name)
        location_code = self._korean_to_code(location_name)
        return f"LOC_{region_code}_{location_code}_01"
    
    def _korean_to_code(self, korean: str) -> str:
        """한글을 코드로 변환 (간단한 매핑)"""
        # 실제로는 더 정교한 변환이 필요하지만, 일단 간단한 매핑 사용
        mapping = {
            "안브레티아": "ANBRETIA",
            "헬라로스": "HELAROS",
            "그라로로스": "GRAROROS",
            "아르보이아": "ARBOIA",
            "해": "SEA",
            "섬": "ISLAND"
        }
        
        # 매핑에 있으면 사용, 없으면 첫 글자만 사용
        if korean in mapping:
            return mapping[korean]
        
        # 간단한 변환: 한글을 그대로 사용하되 공백 제거
        return korean.replace(" ", "_").upper()[:20]
    
    async def create_from_world_design(
        self,
        file_path: Path
    ) -> List[Dict[str, Any]]:
        """
        world_design.md 파일을 파싱하여 게임 데이터 생성
        
        Args:
            file_path: world_design.md 파일 경로
        
        Returns:
            생성된 Region들의 결과 리스트
        """
        # 1. 마크다운 파싱
        region_configs = self.parse_world_design_markdown(file_path)
        
        # 2. 각 Region 생성
        results = []
        for region_config in region_configs:
            result = await self.create_region_with_children(region_config)
            results.append(result)
        
        return results


