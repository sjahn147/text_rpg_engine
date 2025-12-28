"""
상태 변경 상호작용 핸들러 (open, close, light, extinguish, activate, deactivate, lock, unlock)
"""
from typing import Dict, Any, Optional
from app.handlers.object_interaction_base import ObjectInteractionHandlerBase
from app.handlers.action_result import ActionResult


class StateChangeInteractionHandler(ObjectInteractionHandlerBase):
    """상태 변경 상호작용 핸들러"""
    
    async def _change_state(
        self,
        entity_id: str,
        target_id: str,
        session_id: str,
        new_state: str,
        success_message: str
    ) -> ActionResult:
        """상태 변경 공통 로직"""
        runtime_object_id, game_object_id = await self._parse_object_id(target_id, session_id)
        
        if not game_object_id:
            return ActionResult.failure_result("오브젝트를 찾을 수 없습니다.")
        
        updated_state = await self._update_object_state(
            runtime_object_id,
            game_object_id,
            session_id,
            state=new_state
        )
        
        if not updated_state:
            return ActionResult.failure_result("오브젝트 상태를 업데이트할 수 없습니다.")
        
        object_name = updated_state.get('object_name', '오브젝트')
        
        return ActionResult.success_result(
            success_message.format(object_name=object_name),
            data={"state": new_state}
        )
    
    async def handle_open(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 열기"""
        session_id = parameters.get("session_id") if parameters else None
        if not session_id:
            return ActionResult.failure_result("세션 ID가 필요합니다.")
        
        return await self._change_state(
            entity_id,
            target_id,
            session_id,
            "open",
            "{object_name}을(를) 열었습니다."
        )
    
    async def handle_close(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 닫기"""
        session_id = parameters.get("session_id") if parameters else None
        if not session_id:
            return ActionResult.failure_result("세션 ID가 필요합니다.")
        
        return await self._change_state(
            entity_id,
            target_id,
            session_id,
            "closed",
            "{object_name}을(를) 닫았습니다."
        )
    
    async def handle_light(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 불 켜기"""
        session_id = parameters.get("session_id") if parameters else None
        if not session_id:
            return ActionResult.failure_result("세션 ID가 필요합니다.")
        
        return await self._change_state(
            entity_id,
            target_id,
            session_id,
            "lit",
            "{object_name}에 불을 켰습니다."
        )
    
    async def handle_extinguish(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 불 끄기"""
        session_id = parameters.get("session_id") if parameters else None
        if not session_id:
            return ActionResult.failure_result("세션 ID가 필요합니다.")
        
        return await self._change_state(
            entity_id,
            target_id,
            session_id,
            "unlit",
            "{object_name}의 불을 껐습니다."
        )
    
    async def handle_activate(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 활성화"""
        session_id = parameters.get("session_id") if parameters else None
        if not session_id:
            return ActionResult.failure_result("세션 ID가 필요합니다.")
        
        return await self._change_state(
            entity_id,
            target_id,
            session_id,
            "activated",
            "{object_name}을(를) 활성화했습니다."
        )
    
    async def handle_deactivate(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 비활성화"""
        session_id = parameters.get("session_id") if parameters else None
        if not session_id:
            return ActionResult.failure_result("세션 ID가 필요합니다.")
        
        return await self._change_state(
            entity_id,
            target_id,
            session_id,
            "deactivated",
            "{object_name}을(를) 비활성화했습니다."
        )
    
    async def handle_lock(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 잠그기"""
        session_id = parameters.get("session_id") if parameters else None
        if not session_id:
            return ActionResult.failure_result("세션 ID가 필요합니다.")
        
        return await self._change_state(
            entity_id,
            target_id,
            session_id,
            "locked",
            "{object_name}을(를) 잠갔습니다."
        )
    
    async def handle_unlock(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 잠금 해제"""
        session_id = parameters.get("session_id") if parameters else None
        if not session_id:
            return ActionResult.failure_result("세션 ID가 필요합니다.")
        
        return await self._change_state(
            entity_id,
            target_id,
            session_id,
            "unlocked",
            "{object_name}의 잠금을 해제했습니다."
        )
    
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """기본 핸들러 (open)"""
        return await self.handle_open(entity_id, target_id, parameters)

