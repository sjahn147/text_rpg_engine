"""
액션 조회 서비스
"""
from typing import Dict, Any, List
import json
from app.core.game_session import GameSession
from app.services.gameplay.base_service import BaseGameplayService
from common.utils.logger import logger


class ActionService(BaseGameplayService):
    """액션 조회 서비스"""
    
    async def get_available_actions(self, session_id: str) -> List[Dict[str, Any]]:
        """
        사용 가능한 액션 조회
        
        Returns:
            List[Dict[str, Any]]: 액션 목록
        """
        try:
            session = GameSession(session_id)
            player_entities = await session.get_player_entities()
            
            if not player_entities:
                raise ValueError("세션을 찾을 수 없습니다.")
            
            # current_position JSONB에서 runtime_cell_id 추출
            current_position = player_entities[0].get('current_position', {})
            if isinstance(current_position, str):
                current_position = json.loads(current_position)
            current_cell_id = current_position.get('runtime_cell_id')
            
            if not current_cell_id:
                raise ValueError("현재 셀을 찾을 수 없습니다.")
            
            # 현재 셀 정보 조회
            cell_contents = await self.cell_manager.get_cell_contents(current_cell_id)
            
            actions = []
            
            # 연결된 셀로 이동 액션
            # 현재 셀의 game_cell_id를 통해 connected_cells 정보 조회
            cell_data_result = await self.cell_manager.get_cell(current_cell_id)
            if cell_data_result.success and cell_data_result.cell:
                cell_properties = cell_data_result.cell.properties
                connected_cells_info = cell_properties.get('connected_cells', [])
                
                for connected_cell in connected_cells_info:
                    target_game_cell_id = connected_cell['cell_id']
                    direction = connected_cell.get('direction', '어딘가')
                    description = connected_cell.get('description', f"{direction} 방향으로 이동")
                    
                    # 런타임 셀 ID 조회 또는 생성
                    # 먼저 세션의 셀 참조에서 game_cell_id로 조회
                    cell_refs = await self.reference_layer_repo.get_cell_references_by_session(session_id)
                    runtime_target_cell_id = None
                    for cell_ref in cell_refs:
                        if cell_ref['game_cell_id'] == target_game_cell_id:
                            runtime_target_cell_id = cell_ref['runtime_cell_id']
                            break
                    
                    # 없으면 생성
                    if not runtime_target_cell_id:
                        import uuid
                        runtime_target_cell_id = str(uuid.uuid4())
                        await self.reference_layer_repo.create_cell_reference({
                            'runtime_cell_id': runtime_target_cell_id,
                            'game_cell_id': target_game_cell_id,
                            'session_id': session_id
                        })
                        # runtime_cells에도 추가
                        pool = await self.db.pool
                        async with pool.acquire() as conn:
                            await conn.execute(
                                """
                                INSERT INTO runtime_data.runtime_cells
                                (runtime_cell_id, game_cell_id, session_id, created_at)
                                VALUES ($1, $2, $3, NOW())
                                ON CONFLICT (runtime_cell_id) DO NOTHING
                                """,
                                runtime_target_cell_id,
                                target_game_cell_id,
                                session_id
                            )
                    
                    if runtime_target_cell_id:
                        actions.append({
                            "action_id": f"move_to_cell_{runtime_target_cell_id}",
                            "action_type": "move",
                            "text": f"{description} ({direction})",
                            "target_id": runtime_target_cell_id,
                            "target_name": connected_cell.get('cell_name', target_game_cell_id),
                            "target_type": "cell",
                            "description": description,
                        })
            
            # 엔티티와 대화 액션
            for entity in cell_contents.get('entities', []):
                if entity.get('entity_type') == 'npc' and entity.get('dialogue_id'):
                    actions.append({
                        "action_id": f"dialogue_{entity['runtime_entity_id']}",
                        "action_type": "dialogue",
                        "text": f"{entity.get('entity_name', 'NPC')}와 대화하기",
                        "target_id": entity['runtime_entity_id'],
                        "target_name": entity.get('entity_name', 'NPC'),
                    })
            
            # 엔티티 관찰 및 상호작용 액션
            for entity in cell_contents.get('entities', []):
                entity_name = entity.get('entity_name', 'Entity')
                entity_id = entity['runtime_entity_id']
                
                # 관찰하기 액션 (항상 가능)
                actions.append({
                    "action_id": f"examine_entity_{entity_id}",
                    "action_type": "examine",
                    "text": f"{entity_name} 관찰하기",
                    "target_id": entity_id,
                    "target_name": entity_name,
                    "target_type": "entity",
                    "description": entity.get('description', ''),
                })
                
                # 대화하기 액션
                if entity.get('dialogue_id'):
                    actions.append({
                        "action_id": f"dialogue_{entity_id}",
                        "action_type": "dialogue",
                        "text": f"{entity_name}와 대화하기",
                        "target_id": entity_id,
                        "target_name": entity_name,
                        "target_type": "entity",
                    })
                
                # 상호작용하기 액션
                if entity.get('can_interact'):
                    actions.append({
                        "action_id": f"interact_entity_{entity_id}",
                        "action_type": "interact",
                        "text": f"{entity_name}와 상호작용하기",
                        "target_id": entity_id,
                        "target_name": entity_name,
                        "target_type": "entity",
                    })
            
            # 일반적인 액션 추가 (TRPG 스타일)
            objects = cell_contents.get('objects', [])
            if len(objects) > 0:
                # 관찰하기 - 모든 오브젝트 발견
                object_names = [obj.get('object_name', 'Object') for obj in objects]
                actions.append({
                    "action_id": "observe_room",
                    "action_type": "observe",
                    "text": "주변 관찰하기",
                    "target_id": None,
                    "target_name": None,
                    "target_type": None,
                    "description": f"주변을 관찰하여 {', '.join(object_names)} 등을 발견합니다.",
                })
            
            # 발견된 오브젝트별 구체적인 액션 추가
            for obj in objects:
                object_id = obj.get('runtime_object_id') or obj.get('object_id')
                if not object_id:
                    continue
                    
                object_name = obj.get('object_name', 'Object')
                properties = obj.get('properties', {})
                if isinstance(properties, str):
                    properties = json.loads(properties)
                
                # interaction_type은 최상위 레벨 또는 properties에 있을 수 있음
                interaction_type = obj.get('interaction_type') or properties.get('interaction_type', 'examine')
                
                # 런타임 상태에서 current_state 확인
                current_state = None
                if self.object_state_manager:
                    try:
                        game_object_id = obj.get('game_object_id')
                        if game_object_id and session_id:
                            state_result = await self.object_state_manager.get_object_state(
                                runtime_object_id=object_id,
                                game_object_id=game_object_id,
                                session_id=session_id
                            )
                            if state_result.success and state_result.object_state:
                                state_dict = state_result.object_state
                                current_state = state_dict.get('state') or state_dict.get('current_state')
                    except Exception as e:
                        self.logger.warning(f"Failed to get object state for {object_id}: {str(e)}")
                
                # properties에서 current_state 확인 (fallback)
                if not current_state:
                    current_state = properties.get('current_state') or properties.get('state', 'closed')
                
                # 오브젝트의 interaction_type에 따른 액션 생성
                object_actions = []
                
                # 기본 조사 액션 (항상 가능)
                object_actions.append({
                    "action_id": f"examine_object_{object_id}",
                    "action_type": "examine",
                    "text": f"{object_name} 조사하기",
                    "target_id": object_id,
                    "target_name": object_name,
                    "target_type": "object",
                    "description": obj.get('description', ''),
                })
                
                # interaction_type에 따른 특수 액션
                if interaction_type == 'openable':
                    # 열기/닫기
                    if current_state in ['closed', None]:
                        object_actions.append({
                            "action_id": f"open_object_{object_id}",
                            "action_type": "open",
                            "text": f"{object_name} 열기",
                            "target_id": object_id,
                            "target_name": object_name,
                            "target_type": "object",
                        })
                    else:
                        object_actions.append({
                            "action_id": f"close_object_{object_id}",
                            "action_type": "close",
                            "text": f"{object_name} 닫기",
                            "target_id": object_id,
                            "target_name": object_name,
                            "target_type": "object",
                        })
                
                elif interaction_type == 'lightable':
                    # 불 켜기/끄기
                    if current_state in ['unlit', None]:
                        object_actions.append({
                            "action_id": f"light_object_{object_id}",
                            "action_type": "light",
                            "text": f"{object_name} 불 켜기",
                            "target_id": object_id,
                            "target_name": object_name,
                            "target_type": "object",
                        })
                    else:
                        object_actions.append({
                            "action_id": f"extinguish_object_{object_id}",
                            "action_type": "extinguish",
                            "text": f"{object_name} 불 끄기",
                            "target_id": object_id,
                            "target_name": object_name,
                            "target_type": "object",
                        })
                
                elif interaction_type == 'restable' or interaction_type == 'rest':
                    # 쉬기
                    object_actions.append({
                        "action_id": f"rest_object_{object_id}",
                        "action_type": "rest",
                        "text": f"{object_name}에서 쉬기",
                        "target_id": object_id,
                        "target_name": object_name,
                        "target_type": "object",
                    })
                
                elif interaction_type == 'sitable' or interaction_type == 'sit':
                    # 앉기
                    object_actions.append({
                        "action_id": f"sit_object_{object_id}",
                        "action_type": "sit",
                        "text": f"{object_name}에 앉기",
                        "target_id": object_id,
                        "target_name": object_name,
                        "target_type": "object",
                    })
                
                # contents가 있는 경우 줍기 액션
                contents = properties.get('contents', [])
                if contents and len(contents) > 0:
                    object_actions.append({
                        "action_id": f"pickup_object_{object_id}",
                        "action_type": "pickup",
                        "text": f"{object_name}에서 아이템 획득",
                        "target_id": object_id,
                        "target_name": object_name,
                        "target_type": "object",
                        "description": f"{len(contents)}개의 항목이 있습니다.",
                    })
                
                # 오브젝트 액션들을 메인 액션 리스트에 추가
                actions.extend(object_actions)
            
            return actions
            
        except Exception as e:
            self.logger.error(f"액션 조회 실패: {str(e)}")
            raise

