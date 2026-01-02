"""
데이터 무결성 검증 통합 서비스
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from database.connection import DatabaseConnection
from common.utils.logger import logger
from common.utils.jsonb_handler import serialize_jsonb_data, parse_jsonb_data


@dataclass
class IntegrityCheckResult:
    """무결성 검사 결과"""
    can_delete: bool
    blocking_references: List[Dict[str, Any]]
    error_message: str = ""
    
    def __init__(self, can_delete: bool, blocking_references: List[Dict[str, Any]], error_message: str = ""):
        self.can_delete = can_delete
        self.blocking_references = blocking_references
        self.error_message = error_message


class IntegrityService:
    """데이터 무결성 검증 통합 서비스"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db = db_connection or DatabaseConnection()
    
    async def validate_entity_references(self, entity_id: str) -> Dict[str, List[str]]:
        """
        엔티티가 참조되는 Location/Cell 목록 반환 (SSOT 참조 무결성 검증)
        
        Returns:
            {
                "locations_as_owner": ["LOC_001", ...],
                "cells_as_owner": ["CELL_001", ...],
                "locations_in_quest_givers": ["LOC_002", ...]
            }
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 1. Location의 owner로 참조되는 경우
            locations_as_owner = await conn.fetch("""
                SELECT location_id, location_name
                FROM game_data.world_locations
                WHERE location_properties->'ownership'->>'owner_entity_id' = $1
            """, entity_id)
            
            # 2. Cell의 owner로 참조되는 경우
            cells_as_owner = await conn.fetch("""
                SELECT cell_id, cell_name
                FROM game_data.world_cells
                WHERE cell_properties->'ownership'->>'owner_entity_id' = $1
            """, entity_id)
            
            # 3. Location의 quest_givers에 포함된 경우
            locations_in_quest_givers = await conn.fetch("""
                SELECT location_id, location_name
                FROM game_data.world_locations
                WHERE location_properties->'quests'->'quest_givers' @> $1::jsonb
            """, serialize_jsonb_data([entity_id]))
            
            return {
                "locations_as_owner": [row['location_id'] for row in locations_as_owner],
                "cells_as_owner": [row['cell_id'] for row in cells_as_owner],
                "locations_in_quest_givers": [row['location_id'] for row in locations_in_quest_givers]
            }
    
    async def can_delete_entity(self, entity_id: str) -> IntegrityCheckResult:
        """
        엔티티 삭제 가능 여부 검사
        
        Returns:
            IntegrityCheckResult: 삭제 가능 여부 및 차단 참조 정보
        """
        blocking = []
        references = await self.validate_entity_references(entity_id)
        
        # 1. Location owner 참조 확인
        if references["locations_as_owner"]:
            blocking.append({
                "type": "location_owner",
                "items": references["locations_as_owner"],
                "message": f"다음 Location의 소유자로 참조됨: {', '.join(references['locations_as_owner'])}"
            })
        
        # 2. Cell owner 참조 확인
        if references["cells_as_owner"]:
            blocking.append({
                "type": "cell_owner",
                "items": references["cells_as_owner"],
                "message": f"다음 Cell의 소유자로 참조됨: {', '.join(references['cells_as_owner'])}"
            })
        
        # 3. Quest giver 참조 확인
        if references["locations_in_quest_givers"]:
            blocking.append({
                "type": "quest_giver",
                "items": references["locations_in_quest_givers"],
                "message": f"다음 Location의 퀘스트 제공자로 참조됨: {', '.join(references['locations_in_quest_givers'])}"
            })
        
        # 4. Runtime 세션 참조 확인 (추가 가능)
        # TODO: runtime_data 레이어에서 활성 참조 확인
        
        error_message = "\n".join([b["message"] for b in blocking]) if blocking else ""
        
        return IntegrityCheckResult(
            can_delete=len(blocking) == 0,
            blocking_references=blocking,
            error_message=error_message
        )
    
    async def validate_cell_references(self, cell_id: str) -> Dict[str, List[str]]:
        """
        Cell이 참조되는 Location/Cell 목록 반환 (SSOT 참조 무결성 검증)
        
        Returns:
            {
                "locations_in_entry_points": ["LOC_001", ...],
                "cells_in_exits": ["CELL_002", ...],
                "cells_in_entrances": ["CELL_003", ...],
                "cells_in_connections": ["CELL_004", ...]
            }
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 1. Location의 entry_points에 참조되는 경우
            locations_in_entry_points = await conn.fetch("""
                SELECT location_id, location_name
                FROM game_data.world_locations
                WHERE location_properties->'accessibility'->'entry_points' @> $1::jsonb
            """, serialize_jsonb_data([{"cell_id": cell_id}]))
            
            # 2. 다른 Cell의 exits에 참조되는 경우
            cells_in_exits = await conn.fetch("""
                SELECT cell_id, cell_name
                FROM game_data.world_cells
                WHERE cell_properties->'structure'->'exits' @> $1::jsonb
            """, serialize_jsonb_data([{"cell_id": cell_id}]))
            
            # 3. 다른 Cell의 entrances에 참조되는 경우
            cells_in_entrances = await conn.fetch("""
                SELECT cell_id, cell_name
                FROM game_data.world_cells
                WHERE cell_properties->'structure'->'entrances' @> $1::jsonb
            """, serialize_jsonb_data([{"cell_id": cell_id}]))
            
            # 4. 다른 Cell의 connections에 참조되는 경우
            cells_in_connections = await conn.fetch("""
                SELECT cell_id, cell_name
                FROM game_data.world_cells
                WHERE cell_properties->'structure'->'connections' @> $1::jsonb
            """, serialize_jsonb_data([{"cell_id": cell_id}]))
            
            return {
                "locations_in_entry_points": [row['location_id'] for row in locations_in_entry_points],
                "cells_in_exits": [row['cell_id'] for row in cells_in_exits],
                "cells_in_entrances": [row['cell_id'] for row in cells_in_entrances],
                "cells_in_connections": [row['cell_id'] for row in cells_in_connections]
            }
    
    async def can_delete_cell(self, cell_id: str) -> IntegrityCheckResult:
        """
        Cell 삭제 가능 여부 검사
        
        Returns:
            IntegrityCheckResult: 삭제 가능 여부 및 차단 참조 정보
        """
        blocking = []
        references = await self.validate_cell_references(cell_id)
        
        # 1. Location entry point 참조 확인
        if references["locations_in_entry_points"]:
            blocking.append({
                "type": "location_entry_point",
                "items": references["locations_in_entry_points"],
                "message": f"다음 Location의 진입점으로 참조됨: {', '.join(references['locations_in_entry_points'])}"
            })
        
        # 2. Cell exit 참조 확인
        if references["cells_in_exits"]:
            blocking.append({
                "type": "cell_exit",
                "items": references["cells_in_exits"],
                "message": f"다음 Cell의 출구로 참조됨: {', '.join(references['cells_in_exits'])}"
            })
        
        # 3. Cell entrance 참조 확인
        if references["cells_in_entrances"]:
            blocking.append({
                "type": "cell_entrance",
                "items": references["cells_in_entrances"],
                "message": f"다음 Cell의 입구로 참조됨: {', '.join(references['cells_in_entrances'])}"
            })
        
        # 4. Cell connection 참조 확인
        if references["cells_in_connections"]:
            blocking.append({
                "type": "cell_connection",
                "items": references["cells_in_connections"],
                "message": f"다음 Cell의 연결로 참조됨: {', '.join(references['cells_in_connections'])}"
            })
        
        error_message = "\n".join([b["message"] for b in blocking]) if blocking else ""
        
        return IntegrityCheckResult(
            can_delete=len(blocking) == 0,
            blocking_references=blocking,
            error_message=error_message
        )
    
    async def validate_location_references(self, location_id: str) -> Dict[str, List[str]]:
        """
        Location이 참조되는 Region/Cell 목록 반환 (SSOT 참조 무결성 검증)
        
        Returns:
            {
                "regions": ["REG_001", ...],  # 현재는 region_id가 FK이므로 자동 처리
                "cells_in_entry_points": ["CELL_001", ...]  # entry_points에서 참조되는 셀들
            }
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 1. Region 참조는 FK로 처리되므로 별도 검사 불필요
            # 2. 다른 Location의 entry_points에서 참조되는 경우 (향후 확장 가능)
            # 3. Cell의 entry_points에서 참조되는 경우는 없음 (Cell은 Location 하위)
            
            # 현재는 Region FK만 확인하면 됨
            return {
                "regions": [],  # FK로 자동 처리
                "cells_in_entry_points": []  # 향후 확장 가능
            }
    
    async def can_delete_location(self, location_id: str) -> IntegrityCheckResult:
        """
        Location 삭제 가능 여부 검사
        
        Returns:
            IntegrityCheckResult: 삭제 가능 여부 및 차단 참조 정보
        """
        blocking = []
        references = await self.validate_location_references(location_id)
        
        # Region 참조는 FK로 자동 처리되므로 별도 검사 불필요
        # 향후 확장 가능한 참조 검사 추가 가능
        
        error_message = "\n".join([b["message"] for b in blocking]) if blocking else ""
        
        return IntegrityCheckResult(
            can_delete=len(blocking) == 0,
            blocking_references=blocking,
            error_message=error_message
        )

