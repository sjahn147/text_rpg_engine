"""
오브젝트 관련 서비스
"""
from typing import Dict, Any, List, Optional
import uuid
from uuid import UUID
from app.services.gameplay.base_service import BaseGameplayService
from common.utils.logger import logger
from app.common.utils.uuid_helper import normalize_uuid, to_uuid


class ObjectService(BaseGameplayService):
    """오브젝트 관련 서비스"""
    
    async def get_object_state(self, object_id: str, session_id: str) -> Dict[str, Any]:
        """
        오브젝트 상태 조회
        
        Args:
            object_id: 오브젝트 ID (game_object_id 또는 runtime_object_id)
            session_id: 게임 세션 ID
            
        Returns:
            Dict[str, Any]: 오브젝트 상태 정보
        """
        try:
            # UUID 형식 검증
            session_id = normalize_uuid(session_id)
            
            # object_id가 runtime_object_id인지 game_object_id인지 확인
            runtime_object_id = None
            game_object_id = object_id
            
            try:
                # UUID 형식이면 runtime_object_id로 간주
                uuid.UUID(object_id)
                runtime_object_id = object_id
                
                # reference_layer에서 game_object_id 조회
                pool = await self.db.pool
                async with pool.acquire() as conn:
                    object_ref = await conn.fetchrow(
                        """
                        SELECT game_object_id
                        FROM reference_layer.object_references
                        WHERE runtime_object_id = $1 AND session_id = $2
                        """,
                        to_uuid(runtime_object_id),
                        to_uuid(session_id)
                    )
                    
                    if object_ref:
                        game_object_id = object_ref['game_object_id']
                    else:
                        raise ValueError(f"오브젝트 참조를 찾을 수 없습니다: {object_id}")
            except ValueError:
                # UUID 형식이 아니면 game_object_id로 간주
                pass
            
            # ObjectStateManager를 사용하여 상태 조회
            state_result = await self.object_state_manager.get_object_state(
                runtime_object_id=runtime_object_id,
                game_object_id=game_object_id,
                session_id=session_id
            )
            
            if not state_result.success:
                raise ValueError(f"오브젝트 상태 조회 실패: {state_result.message}")
            
            return {
                "success": True,
                "object_id": game_object_id,
                "runtime_object_id": runtime_object_id,
                "state": state_result.object_state
            }
            
        except Exception as e:
            self.logger.error(f"오브젝트 상태 조회 실패: {str(e)}", exc_info=True)
            raise ValueError(f"오브젝트 상태 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def get_object_actions(self, object_id: str, session_id: str) -> Dict[str, Any]:
        """
        가능한 액션 조회 (상태 기반)
        
        Args:
            object_id: 오브젝트 ID (game_object_id 또는 runtime_object_id)
            session_id: 게임 세션 ID
            
        Returns:
            Dict[str, Any]: 가능한 액션 목록
        """
        try:
            # UUID 형식 검증
            session_id = normalize_uuid(session_id)
            
            # 오브젝트 상태 조회
            state_result = await self.get_object_state(object_id, session_id)
            if not state_result.get('success'):
                raise ValueError(f"오브젝트 상태 조회 실패: {state_result.get('message', 'Unknown error')}")
            
            object_state = state_result.get('state', {})
            game_object_id = state_result.get('object_id')
            
            # ActionService를 사용하여 가능한 액션 조회
            actions = await self.action_service.get_available_actions_for_object(
                game_object_id=game_object_id,
                session_id=session_id,
                object_state=object_state
            )
            
            return {
                "success": True,
                "object_id": game_object_id,
                "actions": actions
            }
            
        except Exception as e:
            self.logger.error(f"오브젝트 액션 조회 실패: {str(e)}", exc_info=True)
            raise ValueError(f"오브젝트 액션 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def get_categorized_actions(self, session_id: str) -> Dict[str, Any]:
        """
        카테고리별 액션 조회
        
        Args:
            session_id: 게임 세션 ID
            
        Returns:
            Dict[str, Any]: 카테고리별 액션 목록
        """
        try:
            # UUID 형식 검증
            session_id = normalize_uuid(session_id)
            
            # ActionService를 사용하여 모든 가능한 액션 조회
            all_actions = await self.action_service.get_available_actions(session_id)
            
            # 카테고리별로 분류
            categorized_actions = {
                "entity": [],      # 엔티티 상호작용
                "cell": [],        # 셀 상호작용
                "object": [],      # 오브젝트 상호작용
                "item": [],        # 아이템 조작
                "time": []         # 시간 관련
            }
            
            # ActionType 카테고리 매핑
            category_map = {
                # Entity Interactions
                "dialogue": "entity",
                "trade": "entity",
                "attack": "entity",
                "investigate": "entity",
                
                # Cell Interactions
                "visit": "cell",
                "move": "cell",
                "move_to_cell": "cell",
                
                # Object Interactions
                "examine_object": "object",
                "inspect_object": "object",
                "search_object": "object",
                "open_object": "object",
                "close_object": "object",
                "light_object": "object",
                "extinguish_object": "object",
                "activate_object": "object",
                "deactivate_object": "object",
                "lock_object": "object",
                "unlock_object": "object",
                "sit_at_object": "object",
                "stand_from_object": "object",
                "lie_on_object": "object",
                "get_up_from_object": "object",
                "climb_object": "object",
                "descend_from_object": "object",
                "rest_at_object": "object",
                "sleep_at_object": "object",
                "meditate_at_object": "object",
                "eat_from_object": "object",
                "drink_from_object": "object",
                "consume_object": "object",
                "read_object": "object",
                "study_object": "object",
                "write_object": "object",
                "pickup_from_object": "object",
                "place_in_object": "object",
                "take_from_object": "object",
                "put_in_object": "object",
                "combine_with_object": "object",
                "craft_at_object": "object",
                "cook_at_object": "object",
                "repair_object": "object",
                "destroy_object": "object",
                "break_object": "object",
                "dismantle_object": "object",
                "use_object": "object",
                
                # Item Interactions
                "use_item": "item",
                "equip_item": "item",
                "unequip_item": "item",
                "pickup": "item",
                
                # Time Interactions
                "wait": "time"
            }
            
            # 액션을 카테고리별로 분류
            for action in all_actions:
                action_type = action.get('action_type', '').lower()
                category = category_map.get(action_type, "object")  # 기본값은 object
                
                if category in categorized_actions:
                    categorized_actions[category].append(action)
                else:
                    # 알 수 없는 카테고리는 object에 추가
                    categorized_actions["object"].append(action)
            
            return {
                "success": True,
                "session_id": session_id,
                "categorized_actions": categorized_actions,
                "total_actions": len(all_actions)
            }
            
        except Exception as e:
            self.logger.error(f"카테고리별 액션 조회 실패: {str(e)}", exc_info=True)
            raise ValueError(f"카테고리별 액션 조회 중 오류가 발생했습니다: {str(e)}")

