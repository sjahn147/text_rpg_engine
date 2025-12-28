"""
행동 결과 모델 및 타입 정의
순환 import 방지를 위해 별도 모듈로 분리
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


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
    
    # 셀 이동
    MOVE_TO_CELL = "move_to_cell"
    
    # 아이템 장착/해제
    EQUIP_ITEM = "equip_item"
    UNEQUIP_ITEM = "unequip_item"

