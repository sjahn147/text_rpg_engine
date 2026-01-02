"""
핵심 게임 행동 처리 모듈
"""
from typing import Dict, Any, List, Optional, Tuple
import asyncio
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

from app.managers.entity_manager import EntityManager, EntityType, EntityStatus
from app.managers.cell_manager import CellManager, CellType, CellStatus
from app.managers.effect_carrier_manager import EffectCarrierManager
from app.managers.object_state_manager import ObjectStateManager
from app.managers.inventory_manager import InventoryManager
from app.handlers.object_interactions import (
    InformationInteractionHandler,
    StateChangeInteractionHandler,
    PositionInteractionHandler,
    RecoveryInteractionHandler,
    ConsumptionInteractionHandler,
    LearningInteractionHandler,
    ItemManipulationInteractionHandler,
    CraftingInteractionHandler,
    DestructionInteractionHandler,
)
from app.handlers.entity_interactions import (
    DialogueHandler,
    TradeHandler,
    CombatHandler,
)
from app.handlers.cell_interactions import (
    InvestigationHandler,
    VisitHandler,
    MovementHandler,
)
from app.handlers.item_interactions import (
    UseItemHandler,
    ConsumptionItemHandler,
    EquipmentItemHandler,
    InventoryItemHandler,
)
from app.handlers.time_interactions import (
    WaitHandler,
)
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from common.utils.logger import logger
from common.utils.jsonb_handler import parse_jsonb_data


class ActionResult(BaseModel):
    """행동 결과 모델"""
    success: bool = Field(..., description="행동 성공 여부")
    message: str = Field(..., description="결과 메시지")
    data: Optional[Dict[str, Any]] = Field(default=None, description="추가 데이터")
    effects: Optional[List[Dict[str, Any]]] = Field(default=None, description="행동 효과")
    
    @staticmethod
    def success_result(message: str, data: Optional[Dict[str, Any]] = None, 
                     effects: Optional[List[Dict[str, Any]]] = None) -> "ActionResult":
        return ActionResult(success=True, message=message, data=data, effects=effects)
    
    @staticmethod
    def failure_result(message: str, data: Optional[Dict[str, Any]] = None) -> "ActionResult":
        return ActionResult(success=False, message=message, data=data)


class ActionType(str, Enum):
    """행동 타입 열거형"""
    INVESTIGATE = "investigate"
    DIALOGUE = "dialogue"
    TRADE = "trade"
    VISIT = "visit"
    WAIT = "wait"
    MOVE = "move"
    ATTACK = "attack"
    USE_ITEM = "use_item"
    
    # 오브젝트 상호작용 액션들
    # 1. 정보 확인 (Information)
    EXAMINE_OBJECT = "examine_object"
    INSPECT_OBJECT = "inspect_object"
    SEARCH_OBJECT = "search_object"
    
    # 2. 상태 변경 (State Change)
    OPEN_OBJECT = "open_object"
    CLOSE_OBJECT = "close_object"
    LIGHT_OBJECT = "light_object"
    EXTINGUISH_OBJECT = "extinguish_object"
    ACTIVATE_OBJECT = "activate_object"
    DEACTIVATE_OBJECT = "deactivate_object"
    LOCK_OBJECT = "lock_object"
    UNLOCK_OBJECT = "unlock_object"
    
    # 3. 위치 변경 (Position)
    SIT_AT_OBJECT = "sit_at_object"
    STAND_FROM_OBJECT = "stand_from_object"
    LIE_ON_OBJECT = "lie_on_object"
    GET_UP_FROM_OBJECT = "get_up_from_object"
    CLIMB_OBJECT = "climb_object"
    DESCEND_FROM_OBJECT = "descend_from_object"
    
    # 4. 회복 (Recovery)
    REST_AT_OBJECT = "rest_at_object"
    SLEEP_AT_OBJECT = "sleep_at_object"
    MEDITATE_AT_OBJECT = "meditate_at_object"
    
    # 5. 소비 (Consumption)
    EAT_FROM_OBJECT = "eat_from_object"
    DRINK_FROM_OBJECT = "drink_from_object"
    CONSUME_OBJECT = "consume_object"
    
    # 6. 학습/정보 (Learning)
    READ_OBJECT = "read_object"
    STUDY_OBJECT = "study_object"
    WRITE_OBJECT = "write_object"
    
    # 7. 아이템 조작 (Item Manipulation)
    PICKUP_FROM_OBJECT = "pickup_from_object"
    PLACE_IN_OBJECT = "place_in_object"
    TAKE_FROM_OBJECT = "take_from_object"
    PUT_IN_OBJECT = "put_in_object"
    
    # 8. 조합/제작 (Crafting)
    COMBINE_WITH_OBJECT = "combine_with_object"
    CRAFT_AT_OBJECT = "craft_at_object"
    COOK_AT_OBJECT = "cook_at_object"
    REPAIR_OBJECT = "repair_object"
    
    # 9. 파괴/변형 (Destruction)
    DESTROY_OBJECT = "destroy_object"
    BREAK_OBJECT = "break_object"
    DISMANTLE_OBJECT = "dismantle_object"
    
    # 기타
    USE_OBJECT = "use_object"


class ActionHandler:
    """핵심 게임 행동 처리 클래스"""
    
    def __init__(self, 
                 db_connection: DatabaseConnection,
                 game_data_repo: GameDataRepository,
                 runtime_data_repo: RuntimeDataRepository,
                 reference_layer_repo: ReferenceLayerRepository,
                 entity_manager: EntityManager, 
                 cell_manager: CellManager,
                 effect_carrier_manager: Optional[EffectCarrierManager] = None,
                 object_state_manager: Optional[ObjectStateManager] = None,
                 inventory_manager: Optional[InventoryManager] = None):
        """
        ActionHandler 초기화
        
        Args:
            db_connection: 데이터베이스 연결
            game_data_repo: 게임 데이터 저장소
            runtime_data_repo: 런타임 데이터 저장소
            reference_layer_repo: 참조 레이어 저장소
            entity_manager: 엔티티 관리자
            cell_manager: 셀 관리자
            effect_carrier_manager: Effect Carrier 관리자 (선택사항)
            object_state_manager: 오브젝트 상태 관리자 (선택사항)
            inventory_manager: 인벤토리 관리자 (선택사항)
        """
        self.db = db_connection
        self.game_data = game_data_repo
        self.runtime_data = runtime_data_repo
        self.reference_layer = reference_layer_repo
        self.entity_manager = entity_manager
        self.cell_manager = cell_manager
        self.effect_carrier_manager = effect_carrier_manager
        self.object_state_manager = object_state_manager
        self.inventory_manager = inventory_manager
        self.logger = logger
        
        # 오브젝트 상호작용 핸들러 초기화
        self._init_object_interaction_handlers()
        
        # Entity Interactions 핸들러 초기화
        self._init_entity_interaction_handlers()
        
        # Cell Interactions 핸들러 초기화
        self._init_cell_interaction_handlers()
        
        # Item Interactions 핸들러 초기화
        self._init_item_interaction_handlers()
        
        # Time Interactions 핸들러 초기화
        self._init_time_interaction_handlers()
        
        # 행동 처리 메서드 매핑
        self.action_handlers = {
            # Entity Interactions
            ActionType.DIALOGUE: self.dialogue_handler.handle,
            ActionType.TRADE: self.trade_handler.handle,
            ActionType.ATTACK: self.combat_handler.handle,
            
            # Cell Interactions
            ActionType.INVESTIGATE: self.investigation_handler.handle,
            ActionType.VISIT: self.visit_handler.handle,
            ActionType.MOVE: self.movement_handler.handle,
            
            # Item Interactions
            ActionType.USE_ITEM: self.use_item_handler.handle,
            # TODO: EAT_ITEM, DRINK_ITEM, CONSUME_ITEM, EQUIP_ITEM, UNEQUIP_ITEM, DROP_ITEM 추가 필요
            
            # Time Interactions
            ActionType.WAIT: self.wait_handler.handle,
            # 오브젝트 상호작용 핸들러
            # 1. 정보 확인 (Information)
            ActionType.EXAMINE_OBJECT: self.handle_examine_object,
            ActionType.INSPECT_OBJECT: self.handle_inspect_object,
            ActionType.SEARCH_OBJECT: self.handle_search_object,
            
            # 2. 상태 변경 (State Change)
            ActionType.OPEN_OBJECT: self.handle_open_object,
            ActionType.CLOSE_OBJECT: self.handle_close_object,
            ActionType.LIGHT_OBJECT: self.handle_light_object,
            ActionType.EXTINGUISH_OBJECT: self.handle_extinguish_object,
            ActionType.ACTIVATE_OBJECT: self.handle_activate_object,
            ActionType.DEACTIVATE_OBJECT: self.handle_deactivate_object,
            ActionType.LOCK_OBJECT: self.handle_lock_object,
            ActionType.UNLOCK_OBJECT: self.handle_unlock_object,
            
            # 3. 위치 변경 (Position)
            ActionType.SIT_AT_OBJECT: self.handle_sit_at_object,
            ActionType.STAND_FROM_OBJECT: self.handle_stand_from_object,
            ActionType.LIE_ON_OBJECT: self.handle_lie_on_object,
            ActionType.GET_UP_FROM_OBJECT: self.handle_get_up_from_object,
            ActionType.CLIMB_OBJECT: self.handle_climb_object,
            ActionType.DESCEND_FROM_OBJECT: self.handle_descend_from_object,
            
            # 4. 회복 (Recovery)
            ActionType.REST_AT_OBJECT: self.handle_rest_at_object,
            ActionType.SLEEP_AT_OBJECT: self.handle_sleep_at_object,
            ActionType.MEDITATE_AT_OBJECT: self.handle_meditate_at_object,
            
            # 5. 소비 (Consumption)
            ActionType.EAT_FROM_OBJECT: self.handle_eat_from_object,
            ActionType.DRINK_FROM_OBJECT: self.handle_drink_from_object,
            ActionType.CONSUME_OBJECT: self.handle_consume_object,
            
            # 6. 학습/정보 (Learning)
            ActionType.READ_OBJECT: self.handle_read_object,
            ActionType.STUDY_OBJECT: self.handle_study_object,
            ActionType.WRITE_OBJECT: self.handle_write_object,
            
            # 7. 아이템 조작 (Item Manipulation)
            ActionType.PICKUP_FROM_OBJECT: self.handle_pickup_from_object,
            ActionType.PLACE_IN_OBJECT: self.handle_place_in_object,
            ActionType.TAKE_FROM_OBJECT: self.handle_take_from_object,
            ActionType.PUT_IN_OBJECT: self.handle_put_in_object,
            
            # 8. 조합/제작 (Crafting)
            ActionType.COMBINE_WITH_OBJECT: self.handle_combine_with_object,
            ActionType.CRAFT_AT_OBJECT: self.handle_craft_at_object,
            ActionType.COOK_AT_OBJECT: self.handle_cook_at_object,
            ActionType.REPAIR_OBJECT: self.handle_repair_object,
            
            # 9. 파괴/변형 (Destruction)
            ActionType.DESTROY_OBJECT: self.handle_destroy_object,
            ActionType.BREAK_OBJECT: self.handle_break_object,
            ActionType.DISMANTLE_OBJECT: self.handle_dismantle_object,
            
            # 기타
            ActionType.USE_OBJECT: self.handle_use_object,
        }
    
    async def execute_action(self, action_type: ActionType, 
                           entity_id: str, 
                           target_id: Optional[str] = None,
                           parameters: Optional[Dict[str, Any]] = None,
                           session_id: str = None) -> ActionResult:
        """행동 실행"""
        try:
            self.logger.info(f"Executing action: {action_type} by player {entity_id}")
            
            # 행동 처리 메서드 호출
            handler = self.action_handlers.get(action_type)
            if not handler:
                return ActionResult.failure_result(f"Unknown action type: {action_type}")
            
            result = await handler(entity_id, target_id, parameters)
            
            # 행동 로그 기록 (세션 ID 전달)
            action_name = str(action_type)  # action_type은 이미 문자열
            await self._log_action(entity_id, action_name, result, session_id)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Action execution failed: {str(e)}")
            return ActionResult.failure_result(f"Action execution failed: {str(e)}")
    
    async def handle_investigate(self, entity_id: str, 
                               target_id: Optional[str] = None,
                               parameters: Optional[Dict[str, Any]] = None) -> ActionResult:
        """조사 행동 처리 (라우터)"""
        if not hasattr(self, 'investigation_handler'):
            return ActionResult.failure_result("investigation_handler 핸들러가 초기화되지 않았습니다.")
        return await self.investigation_handler.handle(entity_id, target_id, parameters)
    
    async def handle_dialogue(self, entity_id: str, 
                            target_id: Optional[str] = None,
                            parameters: Optional[Dict[str, Any]] = None) -> ActionResult:
        """대화 행동 처리 (라우터)"""
        if not hasattr(self, 'dialogue_handler'):
            return ActionResult.failure_result("dialogue_handler 핸들러가 초기화되지 않았습니다.")
        return await self.dialogue_handler.handle(entity_id, target_id, parameters)
    
    async def handle_trade(self, entity_id: str, 
                         target_id: Optional[str] = None,
                         parameters: Optional[Dict[str, Any]] = None) -> ActionResult:
        """거래 행동 처리 (라우터)"""
        if not hasattr(self, 'trade_handler'):
            return ActionResult.failure_result("trade_handler 핸들러가 초기화되지 않았습니다.")
        return await self.trade_handler.handle(entity_id, target_id, parameters)
    
    async def handle_visit(self, entity_id: str, 
                         target_id: Optional[str] = None,
                         parameters: Optional[Dict[str, Any]] = None) -> ActionResult:
        """방문 행동 처리 (라우터)"""
        if not hasattr(self, 'visit_handler'):
            return ActionResult.failure_result("visit_handler 핸들러가 초기화되지 않았습니다.")
        return await self.visit_handler.handle(entity_id, target_id, parameters)
    
    async def handle_wait(self, entity_id: str, 
                        target_id: Optional[str] = None,
                        parameters: Optional[Dict[str, Any]] = None) -> ActionResult:
        """대기 행동 처리 (라우터)"""
        if not hasattr(self, 'wait_handler'):
            return ActionResult.failure_result("wait_handler 핸들러가 초기화되지 않았습니다.")
        return await self.wait_handler.handle(entity_id, target_id, parameters)
    
    async def handle_move(self, entity_id: str, 
                        target_id: Optional[str] = None,
                        parameters: Optional[Dict[str, Any]] = None) -> ActionResult:
        """이동 행동 처리 (라우터)"""
        if not hasattr(self, 'movement_handler'):
            return ActionResult.failure_result("movement_handler 핸들러가 초기화되지 않았습니다.")
        return await self.movement_handler.handle(entity_id, target_id, parameters)
    
    async def handle_attack(self, entity_id: str, 
                          target_id: Optional[str] = None,
                          parameters: Optional[Dict[str, Any]] = None) -> ActionResult:
        """공격 행동 처리 (라우터)"""
        if not hasattr(self, 'combat_handler'):
            return ActionResult.failure_result("combat_handler 핸들러가 초기화되지 않았습니다.")
        return await self.combat_handler.handle(entity_id, target_id, parameters)
    
    async def handle_use_item(self, entity_id: str, 
                            target_id: Optional[str] = None,
                            parameters: Optional[Dict[str, Any]] = None) -> ActionResult:
        """아이템 사용 행동 처리 (라우터)"""
        if not hasattr(self, 'use_item_handler'):
            return ActionResult.failure_result("use_item_handler 핸들러가 초기화되지 않았습니다.")
        return await self.use_item_handler.handle(entity_id, target_id, parameters)
    
    async def _log_action(self, entity_id: str, action: str, result: ActionResult, session_id: str = None):
        """행동 로그 기록"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # 세션 ID가 제공되지 않으면 에러 발생
                if not session_id:
                    raise ValueError("session_id는 필수입니다. 세션 중심 설계에 따라 유효한 세션 ID를 제공해야 합니다.")
                
                # 먼저 세션 생성 (존재하지 않는 경우)
                await conn.execute("""
                    INSERT INTO runtime_data.active_sessions 
                    (session_id, session_name, session_state, created_at, updated_at)
                    VALUES ($1, $2, $3, NOW(), NOW())
                    ON CONFLICT (session_id) DO NOTHING
                """, 
                session_id,
                f"Session {session_id[:8]}",
                "active"
                )
                
                # 행동 로그 저장 (log_id는 자동 생성, 올바른 스키마 사용)
                await conn.execute("""
                    INSERT INTO runtime_data.action_logs 
                    (session_id, entity_id, action, success, message, timestamp)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, 
                session_id, 
                entity_id,
                action, 
                result.success, 
                result.message, 
                datetime.now()
                )
        except Exception as e:
            self.logger.error(f"Failed to log action: {str(e)}")
    
    async def _load_action_responses(self, target_name: str) -> Dict[str, List[str]]:
        """DB에서 액션별 응답 템플릿 로드"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # game_data.dialogue_contexts 테이블에서 액션별 응답 로드
                responses = await conn.fetch("""
                    SELECT title, content, available_topics
                    FROM game_data.dialogue_contexts
                    WHERE entity_id IS NULL OR entity_id = ''
                    ORDER BY priority DESC
                """)
                
                # 응답을 주제별로 분류
                action_responses = {
                    "greeting": [],
                    "trade": [],
                    "farewell": []
                }
                
                for response in responses:
                    title = response['title'].lower()
                    content = response['content']
                    topics = parse_jsonb_data(response['available_topics']) or {}
                    
                    # 주제별 응답 분류
                    if 'greeting' in title or 'greeting' in topics:
                        action_responses['greeting'].append(f"{target_name}: {content}")
                    
                    if 'trade' in title or 'trade' in topics:
                        action_responses['trade'].append(f"{target_name}: {content}")
                    
                    if 'farewell' in title or 'farewell' in topics:
                        action_responses['farewell'].append(f"{target_name}: {content}")
                
                # 기본 응답이 없으면 기본값 설정
                if not any(action_responses.values()):
                    action_responses = self._get_default_action_responses(target_name)
                
                return action_responses
                
        except Exception as e:
            self.logger.error(f"Failed to load action responses: {str(e)}")
            return self._get_default_action_responses(target_name)
    
    def _get_default_action_responses(self, target_name: str) -> Dict[str, List[str]]:
        """기본 액션 응답 템플릿 반환"""
        return {
            "greeting": [
                f"{target_name}: 안녕하세요! 무엇을 도와드릴까요?",
                f"{target_name}: 오, 새로운 얼굴이군요!",
                f"{target_name}: 여기서 뭘 하고 계신가요?"
            ],
            "trade": [
                f"{target_name}: 거래를 원하시는군요. 무엇을 사고 싶으신가요?",
                f"{target_name}: 상점에 오신 것을 환영합니다!",
                f"{target_name}: 좋은 물건들이 많이 있습니다."
            ],
            "farewell": [
                f"{target_name}: 안녕히 가세요!",
                f"{target_name}: 또 만나요!",
                f"{target_name}: 조심히 가세요!"
            ]
        }
    
    async def get_available_actions(self, entity_id: str, 
                                  current_cell_id: str) -> List[Dict[str, Any]]:
        """사용 가능한 행동 목록 조회"""
        try:
            # 기본 행동들
            available_actions = [
                {"type": "investigate", "name": "조사", "description": "현재 위치를 조사합니다."},
                {"type": "wait", "name": "대기", "description": "시간을 기다립니다."}
            ]
            
            # 셀 컨텐츠에 따른 추가 행동
            content_result = await self.cell_manager.load_cell_content(current_cell_id)
            if content_result.success and content_result.content:
                content = content_result.content
                
                # 엔티티가 있으면 대화/거래 가능
                if content.entities:
                    available_actions.extend([
                        {"type": "dialogue", "name": "대화", "description": "NPC와 대화합니다."},
                        {"type": "trade", "name": "거래", "description": "NPC와 거래합니다."}
                    ])
                
                # 이벤트가 있으면 특별 행동 가능
                if content.events:
                    available_actions.append({
                        "type": "special_event", 
                        "name": "이벤트", 
                        "description": "특별한 이벤트를 확인합니다."
                    })
            
            return available_actions
            
        except Exception as e:
            self.logger.error(f"Failed to get available actions: {str(e)}")
            return []
    
    def _init_object_interaction_handlers(self):
        """오브젝트 상호작용 핸들러 초기화"""
        if not self.object_state_manager:
            return
        
        # 각 카테고리별 핸들러 생성
        handler_kwargs = {
            'db_connection': self.db,
            'object_state_manager': self.object_state_manager,
            'entity_manager': self.entity_manager,
            'inventory_manager': self.inventory_manager,
            'effect_carrier_manager': self.effect_carrier_manager,
        }
        
        self.info_handler = InformationInteractionHandler(**handler_kwargs)
        self.state_handler = StateChangeInteractionHandler(**handler_kwargs)
        self.position_handler = PositionInteractionHandler(**handler_kwargs)
        self.recovery_handler = RecoveryInteractionHandler(**handler_kwargs)
        self.consumption_handler = ConsumptionInteractionHandler(**handler_kwargs)
        self.learning_handler = LearningInteractionHandler(**handler_kwargs)
        self.item_handler = ItemManipulationInteractionHandler(**handler_kwargs)
        self.crafting_handler = CraftingInteractionHandler(**handler_kwargs)
        self.destruction_handler = DestructionInteractionHandler(**handler_kwargs)
    
    def _init_entity_interaction_handlers(self):
        """엔티티 상호작용 핸들러 초기화"""
        handler_kwargs = {
            'db_connection': self.db,
            'entity_manager': self.entity_manager,
            'cell_manager': self.cell_manager,
            'inventory_manager': self.inventory_manager,
            'effect_carrier_manager': self.effect_carrier_manager,
        }
        
        self.dialogue_handler = DialogueHandler(**handler_kwargs)
        self.trade_handler = TradeHandler(**handler_kwargs)
        self.combat_handler = CombatHandler(**handler_kwargs)
    
    def _init_cell_interaction_handlers(self):
        """셀 상호작용 핸들러 초기화"""
        handler_kwargs = {
            'db_connection': self.db,
            'entity_manager': self.entity_manager,
            'cell_manager': self.cell_manager,
            'inventory_manager': self.inventory_manager,
        }
        
        self.investigation_handler = InvestigationHandler(**handler_kwargs)
        self.visit_handler = VisitHandler(**handler_kwargs)
        self.movement_handler = MovementHandler(**handler_kwargs)
    
    def _init_item_interaction_handlers(self):
        """아이템 상호작용 핸들러 초기화"""
        handler_kwargs = {
            'db_connection': self.db,
            'entity_manager': self.entity_manager,
            'cell_manager': self.cell_manager,
            'inventory_manager': self.inventory_manager,
            'effect_carrier_manager': self.effect_carrier_manager,
        }
        
        self.use_item_handler = UseItemHandler(**handler_kwargs)
        self.consumption_item_handler = ConsumptionItemHandler(**handler_kwargs)
        self.equipment_item_handler = EquipmentItemHandler(**handler_kwargs)
        self.inventory_item_handler = InventoryItemHandler(**handler_kwargs)
    
    def _init_time_interaction_handlers(self):
        """시간 상호작용 핸들러 초기화"""
        handler_kwargs = {
            'db_connection': self.db,
            'entity_manager': self.entity_manager,
            'cell_manager': self.cell_manager,
            # TODO: TimeSystem 추가 필요
            'time_system': None,
        }
        
        self.wait_handler = WaitHandler(**handler_kwargs)
    
    # ============================================
    # 오브젝트 상호작용 핸들러 (라우터 - 분리된 핸들러로 위임)
    # ============================================
    
    async def handle_examine_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 조사"""
        if not hasattr(self, 'info_handler'):
            return ActionResult.failure_result("정보 확인 핸들러가 초기화되지 않았습니다.")
        return await self.info_handler.handle_examine(entity_id, target_id, parameters)
    
    async def handle_open_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 열기"""
        if not hasattr(self, 'state_handler'):
            return ActionResult.failure_result("상태 변경 핸들러가 초기화되지 않았습니다.")
        return await self.state_handler.handle_open(entity_id, target_id, parameters)
    
    async def handle_close_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 닫기"""
        if not hasattr(self, 'state_handler'):
            return ActionResult.failure_result("상태 변경 핸들러가 초기화되지 않았습니다.")
        return await self.state_handler.handle_close(entity_id, target_id, parameters)
    
    async def handle_light_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 불 켜기"""
        if not hasattr(self, 'state_handler'):
            return ActionResult.failure_result("상태 변경 핸들러가 초기화되지 않았습니다.")
        return await self.state_handler.handle_light(entity_id, target_id, parameters)
    
    async def handle_rest_at_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에서 휴식"""
        if not hasattr(self, 'recovery_handler'):
            return ActionResult.failure_result("회복 핸들러가 초기화되지 않았습니다.")
        return await self.recovery_handler.handle_rest(entity_id, target_id, parameters)
    
    async def handle_sit_at_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에 앉기"""
        if not hasattr(self, 'position_handler'):
            return ActionResult.failure_result("위치 변경 핸들러가 초기화되지 않았습니다.")
        return await self.position_handler.handle_sit(entity_id, target_id, parameters)
    
    async def handle_eat_from_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """eat from object"""
        if not hasattr(self, 'consumption_handler'):
            return ActionResult.failure_result("consumption_handler 핸들러가 초기화되지 않았습니다.")
        return await self.consumption_handler.handle_eat(entity_id, target_id, parameters)
    
    async def handle_pickup_from_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에서 아이템 줍기"""
        if not hasattr(self, 'item_handler'):
            return ActionResult.failure_result("아이템 조작 핸들러가 초기화되지 않았습니다.")
        return await self.item_handler.handle_pickup(entity_id, target_id, parameters)
    
    async def handle_extinguish_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """extinguish object"""
        if not hasattr(self, 'state_handler'):
            return ActionResult.failure_result("state_handler 핸들러가 초기화되지 않았습니다.")
        return await self.state_handler.handle_extinguish(entity_id, target_id, parameters)
    
    async def handle_sleep_at_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """sleep at object"""
        if not hasattr(self, 'recovery_handler'):
            return ActionResult.failure_result("recovery_handler 핸들러가 초기화되지 않았습니다.")
        return await self.recovery_handler.handle_sleep(entity_id, target_id, parameters)
    
    async def handle_stand_from_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """stand from object"""
        if not hasattr(self, 'position_handler'):
            return ActionResult.failure_result("position_handler 핸들러가 초기화되지 않았습니다.")
        return await self.position_handler.handle_stand(entity_id, target_id, parameters)
    
    async def handle_drink_from_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """drink from object"""
        if not hasattr(self, 'consumption_handler'):
            return ActionResult.failure_result("consumption_handler 핸들러가 초기화되지 않았습니다.")
        return await self.consumption_handler.handle_drink(entity_id, target_id, parameters)
    
    async def handle_read_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """read object"""
        if not hasattr(self, 'learning_handler'):
            return ActionResult.failure_result("learning_handler 핸들러가 초기화되지 않았습니다.")
        return await self.learning_handler.handle_read(entity_id, target_id, parameters)
    
    async def handle_write_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """write object"""
        if not hasattr(self, 'learning_handler'):
            return ActionResult.failure_result("learning_handler 핸들러가 초기화되지 않았습니다.")
        return await self.learning_handler.handle_write(entity_id, target_id, parameters)
    
    async def handle_use_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 사용하기"""
        if not self.object_state_manager:
            return ActionResult.failure_result("ObjectStateManager가 초기화되지 않았습니다.")
        
        if not target_id:
            return ActionResult.failure_result("대상 오브젝트 ID가 필요합니다.")
        
        session_id = parameters.get("session_id") if parameters else None
        if not session_id:
            return ActionResult.failure_result("세션 ID가 필요합니다.")
        
        # target_id 파싱
        import re
        is_uuid = bool(re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', target_id, re.I))
        runtime_object_id = target_id if is_uuid else None
        game_object_id = target_id if not is_uuid else None
        
        if runtime_object_id and not game_object_id:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                ref = await conn.fetchrow(
                    """
                    SELECT game_object_id FROM reference_layer.object_references
                    WHERE runtime_object_id = $1 AND session_id = $2
                    """,
                    runtime_object_id,
                    session_id
                )
                if ref:
                    game_object_id = ref['game_object_id']
        
        if not game_object_id:
            return ActionResult.failure_result("오브젝트를 찾을 수 없습니다.")
        
        # 오브젝트 상태 조회
        state_result = await self.object_state_manager.get_object_state(
            runtime_object_id,
            game_object_id,
            session_id
        )
        
        if not state_result.success:
            return ActionResult.failure_result(state_result.message)
        
        object_state = state_result.object_state
        properties = object_state.get('properties', {})
        interactions = properties.get('interactions', {})
        use_config = interactions.get('use', {})
        
        # 상태 변경
        new_state = use_config.get('state_change')
        if new_state:
            update_result = await self.object_state_manager.update_object_state(
                runtime_object_id,
                game_object_id,
                session_id,
                state=new_state
            )
            if not update_result.success:
                return ActionResult.failure_result(update_result.message)
        
        # EffectCarrier 적용
        effect_carrier_id = use_config.get('effect_carrier_id')
        if effect_carrier_id and self.effect_carrier_manager:
            # TODO: EffectCarrierManager로 효과 적용
            pass
        
        object_name = object_state.get('object_name', '오브젝트')
        
        # TODO: TimeSystem 연동 (선택적)
        
        return ActionResult.success_result(
            f"{object_name}을(를) 사용했습니다.",
            data={"state": new_state, "effect_carrier_id": effect_carrier_id}
        )
    
    async def handle_place_in_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """place in object"""
        if not hasattr(self, 'item_handler'):
            return ActionResult.failure_result("item_handler 핸들러가 초기화되지 않았습니다.")
        return await self.item_handler.handle_place(entity_id, target_id, parameters)
    
    async def handle_combine_with_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """combine with object"""
        if not hasattr(self, 'crafting_handler'):
            return ActionResult.failure_result("crafting_handler 핸들러가 초기화되지 않았습니다.")
        return await self.crafting_handler.handle_combine(entity_id, target_id, parameters)
    
    async def handle_repair_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """repair object"""
        if not hasattr(self, 'crafting_handler'):
            return ActionResult.failure_result("crafting_handler 핸들러가 초기화되지 않았습니다.")
        return await self.crafting_handler.handle_repair(entity_id, target_id, parameters)
    
    async def handle_destroy_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """destroy object"""
        if not hasattr(self, 'destruction_handler'):
            return ActionResult.failure_result("destruction_handler 핸들러가 초기화되지 않았습니다.")
        return await self.destruction_handler.handle_destroy(entity_id, target_id, parameters)
    
    async def _parse_object_id(
        self,
        target_id: str,
        session_id: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        오브젝트 ID 파싱 (runtime_object_id, game_object_id 반환)
        
        Args:
            target_id: 대상 오브젝트 ID (UUID 또는 game_object_id)
            session_id: 세션 ID
        
        Returns:
            (runtime_object_id, game_object_id) 튜플
        """
        import re
        is_uuid = bool(re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', target_id, re.I))
        
        runtime_object_id = target_id if is_uuid else None
        game_object_id = target_id if not is_uuid else None
        
        # game_object_id가 없으면 reference_layer에서 조회
        if runtime_object_id and not game_object_id:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                ref = await conn.fetchrow(
                    """
                    SELECT game_object_id FROM reference_layer.object_references
                    WHERE runtime_object_id = $1 AND session_id = $2
                    """,
                    runtime_object_id,
                    session_id
                )
                if ref:
                    game_object_id = ref['game_object_id']
        
        return runtime_object_id, game_object_id
    
    # ============================================
    # 오브젝트 상호작용 핸들러 (라우터 - 분리된 핸들러로 위임)
    # ============================================
    
    async def handle_inspect_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """inspect object"""
        if not hasattr(self, 'info_handler'):
            return ActionResult.failure_result("info_handler 핸들러가 초기화되지 않았습니다.")
        return await self.info_handler.handle_inspect(entity_id, target_id, parameters)
    
    async def handle_search_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """search object"""
        if not hasattr(self, 'info_handler'):
            return ActionResult.failure_result("info_handler 핸들러가 초기화되지 않았습니다.")
        return await self.info_handler.handle_search(entity_id, target_id, parameters)
    
    async def handle_activate_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """activate object"""
        if not hasattr(self, 'state_handler'):
            return ActionResult.failure_result("state_handler 핸들러가 초기화되지 않았습니다.")
        return await self.state_handler.handle_activate(entity_id, target_id, parameters)
    
    async def handle_deactivate_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """deactivate object"""
        if not hasattr(self, 'state_handler'):
            return ActionResult.failure_result("state_handler 핸들러가 초기화되지 않았습니다.")
        return await self.state_handler.handle_deactivate(entity_id, target_id, parameters)
    
    async def handle_lock_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """lock object"""
        if not hasattr(self, 'state_handler'):
            return ActionResult.failure_result("state_handler 핸들러가 초기화되지 않았습니다.")
        return await self.state_handler.handle_lock(entity_id, target_id, parameters)
    
    async def handle_unlock_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """unlock object"""
        if not hasattr(self, 'state_handler'):
            return ActionResult.failure_result("state_handler 핸들러가 초기화되지 않았습니다.")
        return await self.state_handler.handle_unlock(entity_id, target_id, parameters)
    
    async def handle_lie_on_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """lie on object"""
        if not hasattr(self, 'position_handler'):
            return ActionResult.failure_result("position_handler 핸들러가 초기화되지 않았습니다.")
        return await self.position_handler.handle_lie(entity_id, target_id, parameters)
    
    async def handle_get_up_from_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """get up from object"""
        if not hasattr(self, 'position_handler'):
            return ActionResult.failure_result("position_handler 핸들러가 초기화되지 않았습니다.")
        return await self.position_handler.handle_get_up(entity_id, target_id, parameters)
    
    async def handle_climb_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """climb object"""
        if not hasattr(self, 'position_handler'):
            return ActionResult.failure_result("position_handler 핸들러가 초기화되지 않았습니다.")
        return await self.position_handler.handle_climb(entity_id, target_id, parameters)
    
    async def handle_descend_from_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """descend from object"""
        if not hasattr(self, 'position_handler'):
            return ActionResult.failure_result("position_handler 핸들러가 초기화되지 않았습니다.")
        return await self.position_handler.handle_descend(entity_id, target_id, parameters)
    
    async def handle_meditate_at_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """meditate at object"""
        if not hasattr(self, 'recovery_handler'):
            return ActionResult.failure_result("recovery_handler 핸들러가 초기화되지 않았습니다.")
        return await self.recovery_handler.handle_meditate(entity_id, target_id, parameters)
    
    async def handle_consume_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """consume object"""
        if not hasattr(self, 'consumption_handler'):
            return ActionResult.failure_result("consumption_handler 핸들러가 초기화되지 않았습니다.")
        return await self.consumption_handler.handle_consume(entity_id, target_id, parameters)
    
    async def handle_study_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """study object"""
        if not hasattr(self, 'learning_handler'):
            return ActionResult.failure_result("learning_handler 핸들러가 초기화되지 않았습니다.")
        return await self.learning_handler.handle_study(entity_id, target_id, parameters)
    
    async def handle_take_from_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """take from object"""
        if not hasattr(self, 'item_handler'):
            return ActionResult.failure_result("item_handler 핸들러가 초기화되지 않았습니다.")
        return await self.item_handler.handle_take(entity_id, target_id, parameters)
    
    async def handle_put_in_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """put in object"""
        if not hasattr(self, 'item_handler'):
            return ActionResult.failure_result("item_handler 핸들러가 초기화되지 않았습니다.")
        return await self.item_handler.handle_put(entity_id, target_id, parameters)
    
    async def handle_craft_at_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """craft at object"""
        if not hasattr(self, 'crafting_handler'):
            return ActionResult.failure_result("crafting_handler 핸들러가 초기화되지 않았습니다.")
        return await self.crafting_handler.handle_craft(entity_id, target_id, parameters)
    
    async def handle_cook_at_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """cook at object"""
        if not hasattr(self, 'crafting_handler'):
            return ActionResult.failure_result("crafting_handler 핸들러가 초기화되지 않았습니다.")
        return await self.crafting_handler.handle_cook(entity_id, target_id, parameters)
    
    async def handle_break_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """break object"""
        if not hasattr(self, 'destruction_handler'):
            return ActionResult.failure_result("destruction_handler 핸들러가 초기화되지 않았습니다.")
        return await self.destruction_handler.handle_break(entity_id, target_id, parameters)
    
    async def handle_dismantle_object(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """dismantle object"""
        if not hasattr(self, 'destruction_handler'):
            return ActionResult.failure_result("destruction_handler 핸들러가 초기화되지 않았습니다.")
        return await self.destruction_handler.handle_dismantle(entity_id, target_id, parameters)
    
