"""
위치 변경 상호작용 핸들러 (sit, stand, lie, get_up, climb, descend)
"""
from typing import Dict, Any, Optional
from app.handlers.object_interaction_base import ObjectInteractionHandlerBase
from app.handlers.action_handler import ActionResult


class PositionInteractionHandler(ObjectInteractionHandlerBase):
    """위치 변경 상호작용 핸들러"""
    
    async def _change_position_state(
        self,
        entity_id: str,
        target_id: str,
        session_id: str,
        new_state: str,
        success_message: str
    ) -> ActionResult:
        """위치 상태 변경 공통 로직"""
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
    
    async def handle_sit(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에 앉기"""
        session_id = parameters.get("session_id") if parameters else None
        if not session_id:
            return ActionResult.failure_result("세션 ID가 필요합니다.")
        
        return await self._change_position_state(
            entity_id,
            target_id,
            session_id,
            "occupied",
            "{object_name}에 앉았습니다."
        )
    
    async def handle_stand(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에서 일어서기"""
        session_id = parameters.get("session_id") if parameters else None
        if not session_id:
            return ActionResult.failure_result("세션 ID가 필요합니다.")
        
        return await self._change_position_state(
            entity_id,
            target_id,
            session_id,
            "unused",
            "{object_name}에서 일어났습니다."
        )
    
    async def handle_lie(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에 눕기"""
        session_id = parameters.get("session_id") if parameters else None
        if not session_id:
            return ActionResult.failure_result("세션 ID가 필요합니다.")
        
        return await self._change_position_state(
            entity_id,
            target_id,
            session_id,
            "lying",
            "{object_name}에 눕습니다."
        )
    
    async def handle_get_up(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에서 일어나기"""
        return await self.handle_stand(entity_id, target_id, parameters)
    
    async def handle_climb(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 오르기"""
        session_id = parameters.get("session_id") if parameters else None
        if not session_id:
            return ActionResult.failure_result("세션 ID가 필요합니다.")
        
        return await self._change_position_state(
            entity_id,
            target_id,
            session_id,
            "climbed",
            "{object_name}에 올랐습니다."
        )
    
    async def handle_descend(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에서 내려오기"""
        session_id = parameters.get("session_id") if parameters else None
        if not session_id:
            return ActionResult.failure_result("세션 ID가 필요합니다.")
        
        return await self._change_position_state(
            entity_id,
            target_id,
            session_id,
            "unused",
            "{object_name}에서 내려왔습니다."
        )
    
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """기본 핸들러 (sit)"""
        return await self.handle_sit(entity_id, target_id, parameters)

