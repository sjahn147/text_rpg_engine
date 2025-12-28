"""
셀 조회 및 이동 서비스
"""
from typing import Dict, Any, Optional
from app.core.game_session import GameSession
from app.services.gameplay.base_service import BaseGameplayService
from common.utils.logger import logger


class CellService(BaseGameplayService):
    """셀 조회 및 이동 서비스"""
    
    async def get_current_cell(self, session_id: str) -> Dict[str, Any]:
        """
        현재 셀 정보 조회
        
        Returns:
            CellInfo 딕셔너리
        """
        try:
            session = GameSession(session_id)
            player_entities = await session.get_player_entities()
            
            if not player_entities:
                raise ValueError("세션을 찾을 수 없습니다.")
            
            # current_position JSONB에서 runtime_cell_id 추출
            current_position = player_entities[0].get('current_position', {})
            if isinstance(current_position, str):
                import json
                current_position = json.loads(current_position)
            current_cell_id = current_position.get('runtime_cell_id')
            if not current_cell_id:
                raise ValueError("현재 셀을 찾을 수 없습니다.")
            
            # 셀 정보 조회
            cell_contents = await self.cell_manager.get_cell_contents(current_cell_id)
            
            if not cell_contents:
                raise ValueError("셀 컨텐츠를 조회할 수 없습니다.")
            
            # 셀 기본 정보 조회 (game_data에서)
            pool = await self.db.pool
            async with pool.acquire() as conn:
                cell_data = await conn.fetchrow(
                    """
                    SELECT 
                        c.cell_id,
                        c.cell_name,
                        c.cell_description as description,
                        c.cell_properties,
                        l.location_name,
                        r.region_name
                    FROM game_data.world_cells c
                    JOIN game_data.world_locations l ON c.location_id = l.location_id
                    JOIN game_data.world_regions r ON l.region_id = r.region_id
                    WHERE c.cell_id = (
                        SELECT game_cell_id FROM reference_layer.cell_references
                        WHERE runtime_cell_id = $1
                    )
                    """,
                    current_cell_id
                )
                
                if not cell_data:
                    raise ValueError("셀 데이터를 찾을 수 없습니다.")
            
            # 연결된 셀 조회 (cell_properties에서)
            connected_cells = []
            cell_properties = cell_data.get('cell_properties')
            if cell_properties:
                if isinstance(cell_properties, str):
                    import json
                    cell_properties = json.loads(cell_properties)
                connected_cells = cell_properties.get('connected_cells', [])
            
            # 응답 구성 (objects에 object_id 추가 및 interaction_type 보장)
            objects = cell_contents.get('objects', [])
            for obj in objects:
                # object_id를 runtime_object_id로 설정 (프론트엔드 호환성)
                if 'object_id' not in obj:
                    obj['object_id'] = obj.get('runtime_object_id', obj.get('game_object_id', ''))
                
                # interaction_type이 properties에 없으면 최상위 레벨에서 가져오기
                if 'interaction_type' not in obj.get('properties', {}):
                    if 'interaction_type' in obj:
                        if 'properties' not in obj:
                            obj['properties'] = {}
                        obj['properties']['interaction_type'] = obj['interaction_type']
            
            cell_info = {
                "cell_id": current_cell_id,
                "cell_name": cell_data['cell_name'],
                "description": cell_data['description'] or "",
                "location_name": cell_data['location_name'],
                "region_name": cell_data['region_name'],
                "entities": cell_contents.get('entities', []),
                "objects": objects,
                "connected_cells": connected_cells,
            }
            
            return cell_info
            
        except Exception as e:
            self.logger.error(f"셀 조회 실패: {str(e)}")
            raise
    
    async def move_player(
        self,
        session_id: str,
        target_cell_id: str
    ) -> Dict[str, Any]:
        """
        플레이어 이동
        
        Returns:
            {
                "success": bool,
                "game_state": {...},
                "message": str
            }
        """
        try:
            session = GameSession(session_id)
            player_entities = await session.get_player_entities()
            
            if not player_entities:
                raise ValueError("세션을 찾을 수 없습니다.")
            
            player_id = player_entities[0]['runtime_entity_id']
            
            # 이동 처리 (GameSession의 move_player 사용)
            success = await session.move_player(
                player_id=player_id,
                target_cell_id=target_cell_id,
                new_position={"x": 0, "y": 0, "z": 0}
            )
            
            if not success:
                raise ValueError("이동에 실패했습니다.")
            
            # 업데이트된 게임 상태 조회
            game_state = await self.get_game_state(session_id)
            
            return {
                "success": True,
                "game_state": game_state,
                "message": "이동했습니다."
            }
            
        except Exception as e:
            self.logger.error(f"플레이어 이동 실패: {str(e)}")
            raise
    
    async def get_game_state(self, session_id: str) -> Dict[str, Any]:
        """게임 상태 조회 (GameService와 동일한 로직)"""
        from app.services.gameplay.game_service import GameService
        game_service = GameService(self.db)
        return await game_service.get_game_state(session_id)

