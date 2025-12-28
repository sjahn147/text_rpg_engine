"""
정보 확인 상호작용 핸들러 (examine, inspect, search)
"""
from typing import Dict, Any, Optional
from app.handlers.object_interaction_base import ObjectInteractionHandlerBase
from app.handlers.action_result import ActionResult


class InformationInteractionHandler(ObjectInteractionHandlerBase):
    """정보 확인 상호작용 핸들러"""
    
    async def handle_examine(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 조사"""
        if not target_id:
            return ActionResult.failure_result("대상 오브젝트 ID가 필요합니다.")
        
        session_id = parameters.get("session_id") if parameters else None
        if not session_id:
            return ActionResult.failure_result("세션 ID가 필요합니다.")
        
        runtime_object_id, game_object_id = await self._parse_object_id(target_id, session_id)
        
        if not game_object_id:
            return ActionResult.failure_result("오브젝트를 찾을 수 없습니다.")
        
        object_state = await self._get_object_state(runtime_object_id, game_object_id, session_id)
        
        if not object_state:
            return ActionResult.failure_result("오브젝트 상태를 조회할 수 없습니다.")
        
        description = object_state.get('object_description', '')
        
        if not description:
            object_name = object_state.get('object_name', '오브젝트')
            description = f"{object_name}을(를) 자세히 살펴봅니다."
        
        current_state = object_state.get('current_state', 'default')
        if current_state != 'default':
            description += f"\n현재 상태: {current_state}"
        
        contents = object_state.get('contents', [])
        if contents:
            description += f"\n내부에 {len(contents)}개의 항목이 있습니다."
        
        return ActionResult.success_result(
            description,
            data={
                "object_id": game_object_id,
                "runtime_object_id": runtime_object_id,
                "object_name": object_state.get('object_name'),
                "current_state": current_state,
                "contents": contents
            }
        )
    
    async def handle_inspect(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 상세 조사 (특정 부분)"""
        # examine와 유사하지만 더 상세한 정보 제공
        return await self.handle_examine(entity_id, target_id, parameters)
    
    async def handle_search(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에서 숨겨진 내용 찾기"""
        if not target_id:
            return ActionResult.failure_result("대상 오브젝트 ID가 필요합니다.")
        
        session_id = parameters.get("session_id") if parameters else None
        if not session_id:
            return ActionResult.failure_result("세션 ID가 필요합니다.")
        
        runtime_object_id, game_object_id = await self._parse_object_id(target_id, session_id)
        
        if not game_object_id:
            return ActionResult.failure_result("오브젝트를 찾을 수 없습니다.")
        
        object_state = await self._get_object_state(runtime_object_id, game_object_id, session_id)
        
        if not object_state:
            return ActionResult.failure_result("오브젝트 상태를 조회할 수 없습니다.")
        
        contents = object_state.get('contents', [])
        
        if contents:
            return ActionResult.success_result(
                f"숨겨진 {len(contents)}개의 항목을 발견했습니다!",
                data={"contents": contents}
            )
        else:
            return ActionResult.success_result(
                "아무것도 찾지 못했습니다.",
                data={"contents": []}
            )
    
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """기본 핸들러 (examine)"""
        return await self.handle_examine(entity_id, target_id, parameters)

