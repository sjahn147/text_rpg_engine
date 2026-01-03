"""
액션 조회 서비스
"""
from typing import Dict, Any, List, Optional
import json
import uuid
from app.core.game_session import GameSession
from app.services.gameplay.base_service import BaseGameplayService
from common.utils.logger import logger
from app.common.utils.uuid_helper import normalize_uuid, to_uuid


class ActionService(BaseGameplayService):
    """액션 조회 서비스"""
    
    def _can_transition_state(
        self,
        current_state: str,
        target_state: str,
        possible_states: List[str],
        state_transitions: Optional[Dict[str, List[str]]] = None
    ) -> bool:
        """
        상태 전이가 가능한지 확인
        
        Args:
            current_state: 현재 상태
            target_state: 목표 상태
            possible_states: 가능한 상태 목록
            state_transitions: 명시적 상태 전이 규칙 (선택사항)
        
        Returns:
            bool: 전이 가능 여부
        """
        if not current_state or not target_state:
            return False
        
        # 명시적 전이 규칙이 있으면 우선 사용
        if state_transitions:
            allowed_transitions = state_transitions.get(current_state, [])
            return target_state in allowed_transitions
        
        # possible_states 기반 자동 전이 규칙
        if current_state in possible_states and target_state in possible_states:
            # 인접 상태로만 전이 가능 (순서 기반)
            try:
                current_idx = possible_states.index(current_state)
                target_idx = possible_states.index(target_state)
                # 인접 상태만 허용 (차이가 1 이하)
                return abs(current_idx - target_idx) <= 1
            except ValueError:
                # 상태가 목록에 없으면 False
                return False
        
        return False
    
    def _check_action_conditions(
        self,
        action_config: Dict[str, Any],
        current_state: str,
        possible_states: List[str]
    ) -> bool:
        """
        액션 수행 가능 여부 확인
        
        Args:
            action_config: 액션 설정
            current_state: 현재 상태
            possible_states: 가능한 상태 목록
        
        Returns:
            bool: 액션 수행 가능 여부
        """
        can_perform = True
        
        # required_state 확인
        required_state = action_config.get('required_state')
        if required_state and current_state != required_state:
            self.logger.debug(
                f"액션 수행 불가: required_state={required_state}, current_state={current_state}"
            )
            can_perform = False
        
        # forbidden_states 확인
        forbidden_states = action_config.get('forbidden_states', [])
        if current_state in forbidden_states:
            self.logger.debug(
                f"액션 수행 불가: current_state={current_state} is in forbidden_states={forbidden_states}"
            )
            can_perform = False
        
        # 상태별 허용 액션 목록 확인
        allowed_in_states = action_config.get('allowed_in_states', [])
        if allowed_in_states and current_state not in allowed_in_states:
            self.logger.debug(
                f"액션 수행 불가: current_state={current_state} not in allowed_in_states={allowed_in_states}"
            )
            can_perform = False
        
        # 상태별 금지 액션 목록 확인
        forbidden_in_states = action_config.get('forbidden_in_states', [])
        if forbidden_in_states and current_state in forbidden_in_states:
            self.logger.debug(
                f"액션 수행 불가: current_state={current_state} is in forbidden_in_states={forbidden_in_states}"
            )
            can_perform = False
        
        # 상태 전이 규칙 확인
        target_state = action_config.get('target_state')
        if target_state and possible_states:
            state_transitions = action_config.get('state_transitions')
            can_transition = self._can_transition_state(
                current_state=current_state,
                target_state=target_state,
                possible_states=possible_states,
                state_transitions=state_transitions
            )
            if not can_transition:
                self.logger.debug(
                    f"액션 수행 불가: 상태 전이 불가능 (current_state={current_state}, target_state={target_state})"
                )
                can_perform = False
        
        return can_perform
    
    def _generate_actions_from_interaction_type(
        self,
        object_actions: List[Dict[str, Any]],
        object_id: str,
        object_name: str,
        interaction_type: str,
        current_state: Optional[str],
        possible_states: List[str],
        properties: Dict[str, Any]
    ) -> None:
        """
        interaction_type과 possible_states를 기반으로 동적으로 액션 생성
        
        Args:
            object_actions: 액션을 추가할 리스트
            object_id: 오브젝트 ID
            object_name: 오브젝트 이름
            interaction_type: 상호작용 타입
            current_state: 현재 상태
            possible_states: 가능한 상태 목록
            properties: 오브젝트 속성
        """
        if not interaction_type or interaction_type == 'none':
            return
        
        # 액션 타입별 텍스트 매핑
        action_text_map = {
            'examine': '조사하기',
            'inspect': '상세 조사하기',
            'search': '찾아보기',
            'open': '열기',
            'close': '닫기',
            'light': '불 켜기',
            'extinguish': '불 끄기',
            'activate': '활성화하기',
            'deactivate': '비활성화하기',
            'lock': '잠그기',
            'unlock': '잠금 해제하기',
            'sit': '앉기',
            'stand': '일어서기',
            'lie': '눕기',
            'get_up': '일어나기',
            'climb': '오르기',
            'descend': '내려가기',
            'rest': '쉬기',
            'sleep': '잠자기',
            'meditate': '명상하기',
            'eat': '먹기',
            'drink': '마시기',
            'consume': '소비하기',
            'read': '읽기',
            'study': '공부하기',
            'write': '쓰기',
            'pickup': '아이템 획득',
            'place': '아이템 놓기',
            'take': '가져가기',
            'put': '넣기',
            'combine': '조합하기',
            'craft': '제작하기',
            'cook': '요리하기',
            'repair': '수리하기',
            'destroy': '파괴하기',
            'break': '부수기',
            'dismantle': '분해하기',
            'use': '사용하기',
        }
        
        # possible_states 기반 동적 액션 생성
        if possible_states and len(possible_states) > 0:
            # 상태 전이 기반 액션 생성
            # possible_states를 기반으로 현재 상태에서 전이 가능한 모든 상태로의 액션 생성
            current_state_normalized = (current_state or '').lower()
            possible_states_lower = [s.lower() for s in possible_states]
            
            # 상태 전이 쌍 정의
            state_transition_pairs = [
                ('closed', 'open', 'open'),
                ('open', 'closed', 'close'),
                ('unlit', 'lit', 'light'),
                ('lit', 'unlit', 'extinguish'),
                ('locked', 'unlocked', 'unlock'),
                ('unlocked', 'locked', 'lock'),
                ('inactive', 'active', 'activate'),
                ('active', 'inactive', 'deactivate'),
            ]
            
            # 현재 상태에서 전이 가능한 액션 생성
            for from_state, to_state, action_type in state_transition_pairs:
                # 현재 상태가 from_state이고, to_state가 possible_states에 있는 경우
                if (current_state_normalized == from_state.lower() and 
                    to_state.lower() in possible_states_lower):
                    # 상태 전이 가능 여부 확인
                    can_transition = self._can_transition_state(
                        current_state=current_state or from_state,
                        target_state=to_state,
                        possible_states=possible_states
                    )
                    if can_transition:
                        action_text = action_text_map.get(action_type, action_type)
                        object_actions.append({
                            "action_id": f"{action_type}_object_{object_id}",
                            "action_type": action_type,
                            "text": f"{object_name} {action_text}",
                            "target_id": object_id,
                            "target_name": object_name,
                            "target_type": "object",
                        })
        
        # interaction_type 기반 액션 생성 (possible_states가 없는 경우)
        if not possible_states or len(possible_states) == 0:
            interaction_action_map = {
                'openable': ['open', 'close'],
                'lightable': ['light', 'extinguish'],
                'restable': ['rest'],
                'sitable': ['sit'],
                'readable': ['read'],
                'writable': ['write'],
                'usable': ['use'],
                'pickupable': ['pickup'],
                'consumable': ['consume'],
                'craftable': ['craft'],
                'repairable': ['repair'],
            }
            
            actions = interaction_action_map.get(interaction_type, [])
            for action_type in actions:
                action_text = action_text_map.get(action_type, action_type)
                object_actions.append({
                    "action_id": f"{action_type}_object_{object_id}",
                    "action_type": action_type,
                    "text": f"{object_name} {action_text}",
                    "target_id": object_id,
                    "target_name": object_name,
                    "target_type": "object",
                })
        
        # properties 기반 추가 액션 생성
        # contents가 있는 경우 pickup 액션
        contents = properties.get('contents', [])
        if contents and len(contents) > 0:
            # 이미 pickup 액션이 있는지 확인
            has_pickup = any(a.get('action_type') == 'pickup' for a in object_actions)
            if not has_pickup:
                object_actions.append({
                    "action_id": f"pickup_object_{object_id}",
                    "action_type": "pickup",
                    "text": f"{object_name}에서 아이템 획득",
                    "target_id": object_id,
                    "target_name": object_name,
                    "target_type": "object",
                    "description": f"{len(contents)}개의 항목이 있습니다.",
                })
    
    async def get_available_actions(self, session_id: str) -> List[Dict[str, Any]]:
        """
        사용 가능한 액션 조회
        
        Returns:
            List[Dict[str, Any]]: 액션 목록
        """
        try:
            # UUID 형식 검증
            try:
                uuid.UUID(session_id)
            except ValueError:
                raise ValueError(f"잘못된 세션 ID 형식: {session_id}")
            
            session = GameSession(session_id)
            player_entities = await session.get_player_entities()
            
            if not player_entities:
                raise ValueError("세션을 찾을 수 없습니다.")
            
            # current_position JSONB에서 runtime_cell_id 추출
            current_position = player_entities[0].get('current_position', {})
            if isinstance(current_position, str):
                try:
                    current_position = json.loads(current_position)
                except json.JSONDecodeError:
                    self.logger.error(f"current_position JSON 파싱 실패: {current_position}")
                    current_position = {}
            elif current_position is None:
                current_position = {}
            
            current_cell_id = current_position.get('runtime_cell_id')
            
            if not current_cell_id:
                # current_cell_id가 없으면 기본 관찰 액션만 반환
                self.logger.warning(f"플레이어의 현재 셀을 찾을 수 없습니다. session_id: {session_id}, current_position: {current_position}")
                # 최소한의 관찰 액션은 제공
                return [{
                    "action_id": "observe_room",
                    "action_type": "observe",
                    "text": "주변 관찰하기",
                    "target_id": None,
                    "target_name": None,
                    "target_type": None,
                    "description": "주변을 자세히 관찰합니다.",
                }]
            
            # UUID 형식 검증
            try:
                uuid.UUID(str(current_cell_id))
            except (ValueError, TypeError):
                self.logger.error(f"잘못된 runtime_cell_id 형식: {current_cell_id}")
                raise ValueError(f"현재 셀 ID 형식이 올바르지 않습니다: {current_cell_id}")
            
            # 현재 셀 정보 조회
            try:
                cell_contents = await self.cell_manager.get_cell_contents(current_cell_id)
            except Exception as e:
                self.logger.error(f"셀 컨텐츠 조회 실패: {str(e)}, cell_id: {current_cell_id}")
                raise ValueError(f"셀 정보를 조회할 수 없습니다: {str(e)}")
            
            actions = []
            
            # 연결된 셀로 이동 액션
            # 현재 셀의 game_cell_id를 통해 connected_cells 정보 조회
            try:
                cell_data_result = await self.cell_manager.get_cell(current_cell_id)
            except Exception as e:
                self.logger.error(f"셀 조회 실패: {str(e)}, cell_id: {current_cell_id}")
                cell_data_result = None
            
            if cell_data_result and cell_data_result.success and cell_data_result.cell:
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
                    
                    # 없으면 생성 (get_or_create_cell_reference는 runtime_cells를 먼저 생성하고 cell_references를 생성함)
                    if not runtime_target_cell_id:
                        try:
                            cell_ref = await self.reference_layer_repo.get_or_create_cell_reference(
                                game_cell_id=target_game_cell_id,
                                session_id=session_id
                            )
                            runtime_target_cell_id = cell_ref.get('runtime_cell_id')
                        except Exception as e:
                            self.logger.error(f"연결된 셀 참조 생성 실패: {str(e)}, game_cell_id: {target_game_cell_id}")
                            # 생성 실패 시 해당 셀로의 이동 액션을 건너뜀
                            continue
                    
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
            entities = cell_contents.get('entities', [])
            
            # 관찰하기 액션은 항상 표시 (오브젝트나 NPC가 없어도 주변을 관찰할 수 있음)
            discovered_items = []
            
            # 오브젝트 이름 수집
            if len(objects) > 0:
                object_names = [obj.get('object_name', 'Object') for obj in objects]
                discovered_items.extend(object_names)
            
            # NPC 이름 수집 (플레이어 제외)
            if len(entities) > 0:
                npc_names = [
                    entity.get('entity_name', 'Entity') 
                    for entity in entities 
                    if entity.get('entity_type') != 'player'
                ]
                discovered_items.extend(npc_names)
            
            # 발견된 항목이 있으면 상세 설명, 없으면 일반 설명
            if len(discovered_items) > 0:
                actions.append({
                    "action_id": "observe_room",
                    "action_type": "observe",
                    "text": "주변 관찰하기",
                    "target_id": None,
                    "target_name": None,
                    "target_type": None,
                    "description": f"주변을 관찰하여 {', '.join(discovered_items)} 등이 보입니다.",
                })
            else:
                # 오브젝트나 NPC가 없어도 관찰 액션 제공
                actions.append({
                    "action_id": "observe_room",
                    "action_type": "observe",
                    "text": "주변 관찰하기",
                    "target_id": None,
                    "target_name": None,
                    "target_type": None,
                    "description": "주변을 자세히 관찰합니다.",
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
                
                # 오브젝트의 properties.interactions를 기반으로 동적 액션 생성
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
                
                # properties.interactions 확인
                interactions = properties.get('interactions', {})
                if isinstance(interactions, str):
                    interactions = json.loads(interactions)
                
                # possible_states 확인 (상태 전이 규칙)
                # possible_states는 최상위 레벨 또는 properties에 있을 수 있음
                possible_states = obj.get('possible_states', [])
                if not possible_states:
                    possible_states = properties.get('possible_states', [])
                if isinstance(possible_states, str):
                    possible_states = json.loads(possible_states)
                elif possible_states is None:
                    possible_states = []
                
                # 액션 타입별 텍스트 매핑
                action_text_map = {
                    'examine': '조사하기',
                    'inspect': '상세 조사하기',
                    'search': '찾아보기',
                    'open': '열기',
                    'close': '닫기',
                    'light': '불 켜기',
                    'extinguish': '불 끄기',
                    'activate': '활성화하기',
                    'deactivate': '비활성화하기',
                    'lock': '잠그기',
                    'unlock': '잠금 해제하기',
                    'sit': '앉기',
                    'stand': '일어서기',
                    'lie': '눕기',
                    'get_up': '일어나기',
                    'climb': '오르기',
                    'descend': '내려가기',
                    'rest': '쉬기',
                    'sleep': '잠자기',
                    'meditate': '명상하기',
                    'eat': '먹기',
                    'drink': '마시기',
                    'consume': '소비하기',
                    'read': '읽기',
                    'study': '공부하기',
                    'write': '쓰기',
                    'pickup': '아이템 획득',
                    'place': '아이템 놓기',
                    'take': '가져가기',
                    'put': '넣기',
                    'combine': '조합하기',
                    'craft': '제작하기',
                    'cook': '요리하기',
                    'repair': '수리하기',
                    'destroy': '파괴하기',
                    'break': '부수기',
                    'dismantle': '분해하기',
                    'use': '사용하기',
                }
                
                # interactions에 정의된 모든 액션 생성
                for action_type, action_config in interactions.items():
                    if not isinstance(action_config, dict):
                        continue
                    
                    # 액션 가능 여부 확인 (강화된 검증 로직 사용)
                    can_perform = self._check_action_conditions(
                        action_config=action_config,
                        current_state=current_state or '',
                        possible_states=possible_states or []
                    )
                    
                    if not can_perform:
                        continue
                    
                    # 액션 텍스트 생성
                    action_text = action_config.get('text') or action_text_map.get(action_type, action_type)
                    if not action_text.endswith('하기') and not action_text.endswith('기'):
                        action_text = f"{object_name} {action_text}"
                    else:
                        action_text = f"{object_name} {action_text}"
                    
                    object_actions.append({
                        "action_id": f"{action_type}_object_{object_id}",
                        "action_type": action_type,
                        "text": action_text,
                        "target_id": object_id,
                        "target_name": object_name,
                        "target_type": "object",
                        "description": action_config.get('description', ''),
                    })
                
                # interaction_type 기반 레거시 지원 (interactions가 없는 경우)
                # possible_states와 properties를 기반으로 동적 액션 생성
                if not interactions:
                    # interaction_type과 possible_states를 기반으로 동적 액션 생성
                    self._generate_actions_from_interaction_type(
                        object_actions=object_actions,
                        object_id=object_id,
                        object_name=object_name,
                        interaction_type=interaction_type,
                        current_state=current_state,
                        possible_states=possible_states,
                        properties=properties
                    )
                
                # contents가 있는 경우 줍기 액션 (interactions에 정의되지 않은 경우)
                # _generate_actions_from_interaction_type에서 이미 처리되지만, 중복 방지를 위해 확인
                contents = properties.get('contents', [])
                if contents and len(contents) > 0:
                    # 이미 pickup 액션이 있는지 확인
                    has_pickup = any(a.get('action_type') == 'pickup' for a in object_actions)
                    if not has_pickup and 'pickup' not in interactions:
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
            
        except ValueError as e:
            self.logger.error(f"액션 조회 실패 (ValueError): {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"액션 조회 실패: {str(e)}", exc_info=True)
            raise ValueError(f"액션 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def get_available_actions_for_object(
        self,
        game_object_id: str,
        session_id: str,
        object_state: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        특정 오브젝트에 대한 가능한 액션 조회
        
        Args:
            game_object_id: 게임 오브젝트 ID
            session_id: 세션 ID
            object_state: 오브젝트 상태 (없으면 조회)
            
        Returns:
            List[Dict[str, Any]]: 가능한 액션 목록
        """
        try:
            # UUID 형식 검증
            session_id = normalize_uuid(session_id)
            
            # object_state가 없으면 조회
            if not object_state:
                if not self.object_state_manager:
                    raise ValueError("ObjectStateManager가 초기화되지 않았습니다")
                
                # reference_layer에서 runtime_object_id 조회
                pool = await self.db.pool
                async with pool.acquire() as conn:
                    object_ref = await conn.fetchrow(
                        """
                        SELECT runtime_object_id
                        FROM reference_layer.object_references
                        WHERE game_object_id = $1 AND session_id = $2
                        """,
                        game_object_id,
                        to_uuid(session_id)
                    )
                    
                    runtime_object_id = str(object_ref['runtime_object_id']) if object_ref else None
                
                state_result = await self.object_state_manager.get_object_state(
                    runtime_object_id=runtime_object_id,
                    game_object_id=game_object_id,
                    session_id=session_id
                )
                
                if not state_result.success:
                    raise ValueError(f"오브젝트 상태 조회 실패: {state_result.message}")
                
                object_state = state_result.object_state
            
            # 오브젝트 정보 추출
            object_name = object_state.get('object_name', 'Object')
            interaction_type = object_state.get('interaction_type', 'examine')
            possible_states = object_state.get('possible_states', [])
            if isinstance(possible_states, str):
                possible_states = json.loads(possible_states)
            elif possible_states is None:
                possible_states = []
            
            properties = object_state.get('properties', {})
            if isinstance(properties, str):
                properties = json.loads(properties)
            
            current_state = object_state.get('current_state') or properties.get('state')
            
            # 오브젝트 액션 생성
            object_actions = []
            
            # 기본 조사 액션 (항상 가능)
            object_actions.append({
                "action_id": f"examine_object_{game_object_id}",
                "action_type": "examine",
                "text": f"{object_name} 조사하기",
                "target_id": game_object_id,
                "target_name": object_name,
                "target_type": "object",
                "description": object_state.get('object_description', ''),
            })
            
            # properties.interactions 확인
            interactions = properties.get('interactions', {})
            if isinstance(interactions, str):
                interactions = json.loads(interactions)
            
            # interactions에 정의된 모든 액션 생성
            for action_type, action_config in interactions.items():
                if not isinstance(action_config, dict):
                    continue
                
                # 액션 가능 여부 확인
                can_perform = self._check_action_conditions(
                    action_config=action_config,
                    current_state=current_state or '',
                    possible_states=possible_states or []
                )
                
                if not can_perform:
                    continue
                
                # 액션 텍스트 생성
                action_text_map = {
                    'examine': '조사하기', 'inspect': '상세 조사하기', 'search': '찾아보기',
                    'open': '열기', 'close': '닫기', 'light': '불 켜기', 'extinguish': '불 끄기',
                    'activate': '활성화하기', 'deactivate': '비활성화하기',
                    'lock': '잠그기', 'unlock': '잠금 해제하기',
                    'sit': '앉기', 'stand': '일어서기', 'lie': '눕기', 'get_up': '일어나기',
                    'climb': '오르기', 'descend': '내려가기',
                    'rest': '쉬기', 'sleep': '잠자기', 'meditate': '명상하기',
                    'eat': '먹기', 'drink': '마시기', 'consume': '소비하기',
                    'read': '읽기', 'study': '공부하기', 'write': '쓰기',
                    'pickup': '아이템 획득', 'place': '아이템 놓기',
                    'take': '가져가기', 'put': '넣기', 'combine': '조합하기',
                    'craft': '제작하기', 'cook': '요리하기', 'repair': '수리하기',
                    'destroy': '파괴하기', 'break': '부수기', 'dismantle': '분해하기',
                    'use': '사용하기',
                }
                
                action_text = action_config.get('text') or action_text_map.get(action_type, action_type)
                if not action_text.endswith('하기') and not action_text.endswith('기'):
                    action_text = f"{object_name} {action_text}"
                else:
                    action_text = f"{object_name} {action_text}"
                
                object_actions.append({
                    "action_id": f"{action_type}_object_{game_object_id}",
                    "action_type": action_type,
                    "text": action_text,
                    "target_id": game_object_id,
                    "target_name": object_name,
                    "target_type": "object",
                    "description": action_config.get('description', ''),
                })
            
            # interaction_type 기반 레거시 지원 (interactions가 없는 경우)
            if not interactions:
                self._generate_actions_from_interaction_type(
                    object_actions=object_actions,
                    object_id=game_object_id,
                    object_name=object_name,
                    interaction_type=interaction_type,
                    current_state=current_state,
                    possible_states=possible_states,
                    properties=properties
                )
            
            # contents가 있는 경우 줍기 액션
            contents = properties.get('contents', [])
            if contents and len(contents) > 0:
                has_pickup = any(a.get('action_type') == 'pickup' for a in object_actions)
                if not has_pickup and 'pickup' not in interactions:
                    object_actions.append({
                        "action_id": f"pickup_object_{game_object_id}",
                        "action_type": "pickup",
                        "text": f"{object_name}에서 아이템 획득",
                        "target_id": game_object_id,
                        "target_name": object_name,
                        "target_type": "object",
                        "description": f"{len(contents)}개의 항목이 있습니다.",
                    })
            
            return object_actions
            
        except Exception as e:
            self.logger.error(f"오브젝트 액션 조회 실패: {str(e)}", exc_info=True)
            raise ValueError(f"오브젝트 액션 조회 중 오류가 발생했습니다: {str(e)}")

