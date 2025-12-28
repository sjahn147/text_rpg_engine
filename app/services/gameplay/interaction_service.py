"""
상호작용 처리 서비스
"""
from typing import Dict, Any, Optional, List
import json
import uuid
from app.core.game_session import GameSession
from app.services.gameplay.base_service import BaseGameplayService
from common.utils.logger import logger


class InteractionService(BaseGameplayService):
    """상호작용 처리 서비스"""
    
    async def interact_with_entity(
        self,
        session_id: str,
        entity_id: str,
        action_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        엔티티와 상호작용
        
        Returns:
            {
                "success": bool,
                "message": str,
                "result": {...}
            }
        """
        try:
            session = GameSession(session_id)
            player_entities = await session.get_player_entities()
            
            if not player_entities:
                raise ValueError("세션을 찾을 수 없습니다.")
            
            player_id = player_entities[0]['runtime_entity_id']
            
            # 엔티티 정보 조회
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # 엔티티 참조 조회
                entity_ref = await conn.fetchrow(
                    """
                    SELECT er.runtime_entity_id, er.game_entity_id, er.entity_type
                    FROM reference_layer.entity_references er
                    WHERE er.runtime_entity_id = $1
                    """,
                    entity_id
                )
                
                if not entity_ref:
                    raise ValueError("엔티티를 찾을 수 없습니다.")
            
                # 게임 엔티티 정보 조회
                game_entity = await conn.fetchrow(
                    """
                    SELECT entity_id, entity_name, entity_description, entity_type, entity_properties
                    FROM game_data.entities
                    WHERE entity_id = $1
                    """,
                    entity_ref['game_entity_id']
                )
                
                if not game_entity:
                    raise ValueError("게임 엔티티를 찾을 수 없습니다.")
                
                # 액션 타입에 따른 처리
                action_type = action_type or 'interact'
                
                if action_type == 'examine':
                    # 관찰 시 상세 정보 제공
                    entity_properties = json.loads(game_entity['entity_properties']) if isinstance(game_entity['entity_properties'], str) else game_entity['entity_properties']
                    
                    # 플레이어 본인을 관찰하는 경우 특별한 메시지
                    is_self = (entity_ref['entity_type'] == 'player' and 
                              str(entity_ref['runtime_entity_id']) == str(player_id))
                    
                    if is_self:
                        description = "거울을 보는 것처럼 자신의 모습을 관찰합니다. "
                        if game_entity['entity_description']:
                            description += game_entity['entity_description']
                        else:
                            description += f"{game_entity['entity_name']}의 모습이 보입니다."
                    else:
                        description = game_entity['entity_description'] or f"{game_entity['entity_name']}을(를) 관찰합니다."
                    
                    details = []
                    details.append(f"타입: {game_entity['entity_type']}")
                    
                    if entity_properties:
                        occupation = entity_properties.get('occupation')
                        if occupation:
                            details.append(f"직업: {occupation}")
                        
                        mood = entity_properties.get('mood')
                        if mood:
                            details.append(f"기분: {mood}")
                        
                        level = entity_properties.get('level')
                        if level:
                            details.append(f"레벨: {level}")
                        
                        # 플레이어 본인인 경우 추가 정보
                        if is_self:
                            # 런타임 상태에서 현재 HP/MP 정보 가져오기
                            entity_state = await conn.fetchrow(
                                """
                                SELECT current_stats FROM runtime_data.entity_states
                                WHERE runtime_entity_id = $1
                                """,
                                player_id
                            )
                            if entity_state and entity_state.get('current_stats'):
                                stats = json.loads(entity_state['current_stats']) if isinstance(entity_state['current_stats'], str) else entity_state['current_stats']
                                hp = stats.get('hp', entity_properties.get('hp', 100))
                                mp = stats.get('mp', entity_properties.get('mp', 50))
                                details.append(f"체력: {hp} / {entity_properties.get('hp', 100)}")
                                details.append(f"마나: {mp} / {entity_properties.get('mp', 50)}")
                    
                    if details:
                        description += f"\n\n{chr(10).join(details)}"
                    
                    return {
                        "success": True,
                        "message": description,
                        "result": {
                            "action": "examine",
                            "entity_id": entity_id,
                            "description": description,
                            "entity_type": game_entity['entity_type'],
                            "properties": entity_properties,
                            "is_self": is_self
                        }
                    }
                elif action_type == 'dialogue':
                    # 대화 시작은 별도 엔드포인트로 처리
                    return {
                        "success": True,
                        "message": f"{game_entity['entity_name']}와 대화를 시작합니다.",
                        "result": {"action": "dialogue", "entity_id": entity_id}
                    }
                else:
                    return {
                        "success": True,
                        "message": f"{game_entity['entity_name']}와 상호작용했습니다.",
                        "result": {"action": action_type, "entity_id": entity_id}
                    }
                    
        except Exception as e:
            self.logger.error(f"엔티티 상호작용 실패: {str(e)}")
            raise
    
    async def interact_with_object(
        self,
        session_id: str,
        object_id: str,
        action_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        오브젝트와 상호작용
        
        Returns:
            {
                "success": bool,
                "message": str,
                "result": {...}
            }
        """
        try:
            session = GameSession(session_id)
            player_entities = await session.get_player_entities()
            
            if not player_entities:
                raise ValueError("세션을 찾을 수 없습니다.")
            
            player_id = player_entities[0]['runtime_entity_id']
            action_type = action_type or 'examine'
            
            # current_position JSONB에서 runtime_cell_id 추출
            current_position = player_entities[0].get('current_position', {})
            if isinstance(current_position, str):
                current_position = json.loads(current_position)
            current_cell_id = current_position.get('runtime_cell_id')
            
            if not current_cell_id:
                raise ValueError("현재 셀을 찾을 수 없습니다.")
            
            # 현재 셀의 오브젝트 목록 조회
            cell_contents = await self.cell_manager.get_cell_contents(current_cell_id)
            
            # 현재 셀의 오브젝트 목록에서 요청한 오브젝트 찾기
            target_object = None
            for obj in cell_contents.get('objects', []):
                # object_id가 runtime_object_id 또는 game_object_id와 일치하는지 확인
                if (obj.get('runtime_object_id') == object_id or 
                    obj.get('game_object_id') == object_id):
                    target_object = obj
                    break
            
            if not target_object:
                raise ValueError("현재 셀에서 오브젝트를 찾을 수 없습니다.")
            
            # ActionHandler를 통한 상호작용 처리
            # action_type을 ActionType enum으로 변환
            from app.handlers.action_result import ActionType
            
            action_type_map = {
                'examine': ActionType.EXAMINE_OBJECT,
                'open': ActionType.OPEN_OBJECT,
                'close': ActionType.CLOSE_OBJECT,
                'light': ActionType.LIGHT_OBJECT,
                'extinguish': ActionType.EXTINGUISH_OBJECT,
                'sit': ActionType.SIT_AT_OBJECT,
                'rest': ActionType.REST_AT_OBJECT,
                'sleep': ActionType.SLEEP_AT_OBJECT,
                'pickup': ActionType.PICKUP_FROM_OBJECT,
            }
            
            handler_action_type = action_type_map.get(action_type, ActionType.EXAMINE_OBJECT)
            
            # ActionHandler로 처리
            result = await self.action_handler.execute_action(
                entity_id=player_id,
                action_type=handler_action_type,
                target_id=target_object.get('runtime_object_id') or target_object.get('game_object_id'),
                parameters={"session_id": session_id}
            )
            
            if not result.success:
                raise ValueError(result.message)
            
            return {
                "success": True,
                "message": result.message,
                "result": result.data or {}
            }
            
        except Exception as e:
            self.logger.error(f"오브젝트 상호작용 실패: {str(e)}")
            raise
    
    async def pickup_from_object(
        self,
        session_id: str,
        object_id: str,
        item_id: str
    ) -> Dict[str, Any]:
        """
        오브젝트에서 아이템 획득
        
        Returns:
            {
                "success": bool,
                "message": str,
                "result": {...}
            }
        """
        try:
            session = GameSession(session_id)
            player_entities = await session.get_player_entities()
            
            if not player_entities:
                raise ValueError("세션을 찾을 수 없습니다.")
            
            player_id = player_entities[0]['runtime_entity_id']
            
            # ActionHandler를 통한 pickup 처리
            result = await self.action_handler.execute_action(
                entity_id=player_id,
                action_type=ActionType.PICKUP_FROM_OBJECT,
                target_id=object_id,
                parameters={
                    "session_id": session_id,
                    "item_id": item_id
                }
            )
            
            if not result.success:
                raise ValueError(result.message)
            
            return {
                "success": True,
                "message": result.message,
                "result": result.data or {}
            }
            
        except Exception as e:
            self.logger.error(f"아이템 획득 실패: {str(e)}")
            raise
    
    async def combine_items(
        self,
        session_id: str,
        item_ids: List[str]
    ) -> Dict[str, Any]:
        """
        아이템 조합
        
        Returns:
            {
                "success": bool,
                "message": str,
                "result": {...}
            }
        """
        try:
            session = GameSession(session_id)
            player_entities = await session.get_player_entities()
            
            if not player_entities:
                raise ValueError("세션을 찾을 수 없습니다.")
            
            player_id = player_entities[0]['runtime_entity_id']
            
            # 입력 검증
            if len(item_ids) < 2:
                raise ValueError("조합하려면 최소 2개의 아이템이 필요합니다.")
            if len(item_ids) > 5:
                raise ValueError("조합은 최대 5개의 아이템까지만 가능합니다.")
            
            # ActionHandler를 통한 조합 처리
            from app.handlers.action_result import ActionType
            
            result = await self.action_handler.execute_action(
                entity_id=player_id,
                action_type=ActionType.COMBINE_WITH_OBJECT,
                target_id=None,
                parameters={
                    "session_id": session_id,
                    "items": item_ids
                }
            )
            
            if not result.success:
                raise ValueError(result.message)
            
            return {
                "success": True,
                "message": result.message,
                "result": result.data or {}
            }
            
        except Exception as e:
            self.logger.error(f"아이템 조합 실패: {str(e)}")
            raise

