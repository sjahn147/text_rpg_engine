"""
맵 시스템 서비스
"""
from typing import Dict, Any, List, Optional
from app.services.gameplay.base_service import BaseGameplayService
from common.utils.logger import logger
from app.common.utils.uuid_helper import normalize_uuid, to_uuid
from common.utils.jsonb_handler import parse_jsonb_data


class MapService(BaseGameplayService):
    """맵 시스템 서비스"""
    
    async def get_map_data(self, session_id: str) -> Dict[str, Any]:
        """
        맵 데이터 조회 (계층적 구조: 지역 → 위치 → 셀)
        
        Args:
            session_id: 게임 세션 ID
            
        Returns:
            Dict[str, Any]: 맵 데이터 (계층적 구조)
        """
        try:
            session_id = normalize_uuid(session_id)
            
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # 지역 조회
                regions = await conn.fetch(
                    """
                    SELECT 
                        region_id,
                        region_name,
                        region_type,
                        region_properties
                    FROM game_data.world_regions
                    ORDER BY region_name
                    """
                )
                
                # 위치 조회
                locations = await conn.fetch(
                    """
                    SELECT 
                        location_id,
                        location_name,
                        location_type,
                        region_id,
                        location_properties
                    FROM game_data.world_locations
                    ORDER BY location_name
                    """
                )
                
                # 셀 조회
                cells = await conn.fetch(
                    """
                    SELECT 
                        cell_id,
                        cell_name,
                        cell_description,
                        location_id,
                        cell_properties
                    FROM game_data.world_cells
                    ORDER BY cell_name
                    """
                )
                
                # 계층적 구조 생성
                region_map = {}
                for region in regions:
                    region_id = region['region_id']
                    region_map[region_id] = {
                        "region_id": region_id,
                        "region_name": region['region_name'],
                        "region_type": region.get('region_type'),
                        "properties": parse_jsonb_data(region.get('region_properties', {})),
                        "locations": []
                    }
                
                # 위치를 지역에 매핑
                location_map = {}
                for location in locations:
                    location_id = location['location_id']
                    region_id = location.get('region_id')
                    
                    location_data = {
                        "location_id": location_id,
                        "location_name": location['location_name'],
                        "location_type": location.get('location_type'),
                        "properties": parse_jsonb_data(location.get('location_properties', {})),
                        "cells": []
                    }
                    
                    location_map[location_id] = location_data
                    
                    if region_id and region_id in region_map:
                        region_map[region_id]["locations"].append(location_data)
                
                # 셀을 위치에 매핑
                for cell in cells:
                    cell_id = cell['cell_id']
                    location_id = cell.get('location_id')
                    
                    cell_data = {
                        "cell_id": cell_id,
                        "cell_name": cell['cell_name'],
                        "cell_description": cell.get('cell_description'),
                        "properties": parse_jsonb_data(cell.get('cell_properties', {}))
                    }
                    
                    if location_id and location_id in location_map:
                        location_map[location_id]["cells"].append(cell_data)
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "map_data": {
                        "regions": list(region_map.values())
                    }
                }
                
        except Exception as e:
            self.logger.error(f"맵 데이터 조회 실패: {str(e)}", exc_info=True)
            raise ValueError(f"맵 데이터 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def get_discovered_cells(self, session_id: str) -> Dict[str, Any]:
        """
        발견한 셀 목록 조회
        
        Args:
            session_id: 게임 세션 ID
            
        Returns:
            Dict[str, Any]: 발견한 셀 목록
        """
        try:
            session_id = normalize_uuid(session_id)
            
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # action_logs에서 이동/방문 행동을 기반으로 발견한 셀 추론
                # 실제로는 별도 테이블이 필요하지만, 현재는 action_logs 기반으로 추론
                discovered = await conn.fetch(
                    """
                    SELECT DISTINCT
                        message,
                        timestamp
                    FROM runtime_data.action_logs
                    WHERE session_id = $1 
                        AND (action = 'move' OR action = 'visit' OR action = 'investigate')
                        AND success = true
                    ORDER BY timestamp DESC
                    """,
                    to_uuid(session_id)
                )
                
                # 현재 위치의 셀도 포함
                current_cell = await conn.fetchrow(
                    """
                    SELECT 
                        cr.game_cell_id,
                        c.cell_id,
                        c.cell_name,
                        c.cell_description
                    FROM runtime_data.entity_states es
                    LEFT JOIN reference_layer.cell_references cr 
                        ON (es.current_position->>'runtime_cell_id')::uuid = cr.runtime_cell_id
                        AND es.session_id = cr.session_id
                    LEFT JOIN game_data.world_cells c 
                        ON cr.game_cell_id = c.cell_id
                    WHERE es.session_id = $1
                        AND es.runtime_entity_id IN (
                            SELECT runtime_entity_id 
                            FROM reference_layer.entity_references 
                            WHERE session_id = $1 
                                AND entity_type = 'player'
                            LIMIT 1
                        )
                    LIMIT 1
                    """,
                    to_uuid(session_id)
                )
                
                discovered_cells = []
                
                # 현재 셀 추가
                if current_cell and current_cell.get('cell_id'):
                    discovered_cells.append({
                        "cell_id": current_cell['cell_id'],
                        "cell_name": current_cell.get('cell_name', 'Unknown'),
                        "cell_description": current_cell.get('cell_description'),
                        "is_current": True
                    })
                
                # 발견 이력 추가
                for discovery in discovered:
                    message = discovery.get('message', '')
                    if message:
                        discovered_cells.append({
                            "description": message,
                            "timestamp": discovery.get('timestamp').isoformat() if discovery.get('timestamp') else None,
                            "is_current": False
                        })
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "discovered_cells": discovered_cells
                }
                
        except Exception as e:
            self.logger.error(f"발견한 셀 목록 조회 실패: {str(e)}", exc_info=True)
            raise ValueError(f"발견한 셀 목록 조회 중 오류가 발생했습니다: {str(e)}")

