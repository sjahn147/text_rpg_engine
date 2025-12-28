"""
Handler 인터페이스 정의
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, List
from enum import Enum
from pydantic import BaseModel


class ActionType(str, Enum):
    """액션 타입"""
    INVESTIGATE = "investigate"
    DIALOGUE = "dialogue"
    TRADE = "trade"
    VISIT = "visit"
    WAIT = "wait"
    MOVE = "move"
    ATTACK = "attack"
    USE_ITEM = "use_item"


class ActionResult(BaseModel):
    """액션 결과"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    effects: Optional[List[Dict[str, Any]]] = None


class IActionHandler(ABC):
    """액션 핸들러 인터페이스"""
    
    @abstractmethod
    async def execute_action(
        self,
        action_type: ActionType,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> ActionResult:
        """액션 실행"""
        pass

