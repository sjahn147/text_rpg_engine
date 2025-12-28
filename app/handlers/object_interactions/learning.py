"""
학습/정보 상호작용 핸들러 (read, study, write)
"""
from typing import Dict, Any, Optional
from app.handlers.object_interaction_base import ObjectInteractionHandlerBase
from app.handlers.action_result import ActionResult


class LearningInteractionHandler(ObjectInteractionHandlerBase):
    """학습/정보 상호작용 핸들러"""
    
    async def handle_read(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 읽기"""
        session_id = parameters.get("session_id") if parameters else None
        if not session_id:
            return ActionResult.failure_result("세션 ID가 필요합니다.")
        
        runtime_object_id, game_object_id = await self._parse_object_id(target_id, session_id)
        
        if not game_object_id:
            return ActionResult.failure_result("오브젝트를 찾을 수 없습니다.")
        
        object_state = await self._get_object_state(runtime_object_id, game_object_id, session_id)
        
        if not object_state:
            return ActionResult.failure_result("오브젝트 상태를 조회할 수 없습니다.")
        
        properties = object_state.get('properties', {})
        interactions = properties.get('interactions', {})
        read_config = interactions.get('read', {})
        
        # 읽기 내용
        content = read_config.get('content', object_state.get('object_description', ''))
        
        # EffectCarrier 적용
        effect_carrier_id = read_config.get('effect_carrier_id')
        if effect_carrier_id and self.effect_carrier_manager:
            session_id = parameters.get("session_id") if parameters else None
            if session_id:
                effect_result = await self.effect_carrier_manager.grant_effect_to_entity(
                    session_id=session_id,
                    entity_id=entity_id,
                    effect_id=effect_carrier_id,
                    source=f"read_object:{game_object_id}"
                )
                if not effect_result.success:
                    self.logger.warning(f"Effect Carrier 적용 실패: {effect_result.message}")
        
        object_name = object_state.get('object_name', '오브젝트')
        
        # TimeSystem 연동
        time_cost = read_config.get('time_cost', 30)
        if time_cost > 0:
            from app.systems.time_system import TimeSystem
            time_system = TimeSystem()
            try:
                await time_system.advance_time(minutes=time_cost)
            except Exception as e:
                self.logger.warning(f"TimeSystem 연동 실패: {str(e)}")
        
        return ActionResult.success_result(
            f"{object_name}을(를) 읽었습니다.\n\n{content}",
            data={"content": content, "effect_carrier_id": effect_carrier_id}
        )
    
    async def handle_study(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 공부하기"""
        # read와 유사하지만 시간 대량 소모
        return await self.handle_read(entity_id, target_id, parameters)
    
    async def handle_write(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에 쓰기"""
        session_id = parameters.get("session_id") if parameters else None
        if not session_id:
            return ActionResult.failure_result("세션 ID가 필요합니다.")
        
        content = parameters.get("content") if parameters else None
        if not content:
            return ActionResult.failure_result("작성할 내용이 필요합니다.")
        
        runtime_object_id, game_object_id = await self._parse_object_id(target_id, session_id)
        
        if not game_object_id:
            return ActionResult.failure_result("오브젝트를 찾을 수 없습니다.")
        
        # 오브젝트 상태 업데이트
        updated_state = await self._update_object_state(
            runtime_object_id,
            game_object_id,
            session_id,
            state="written",
            properties={"written_content": content}
        )
        
        if not updated_state:
            return ActionResult.failure_result("오브젝트 상태를 업데이트할 수 없습니다.")
        
        object_name = updated_state.get('object_name', '오브젝트')
        
        # TimeSystem 연동
        write_config = properties.get('interactions', {}).get('write', {})
        time_cost = write_config.get('time_cost', 15)
        if time_cost > 0:
            from app.systems.time_system import TimeSystem
            time_system = TimeSystem()
            try:
                await time_system.advance_time(minutes=time_cost)
            except Exception as e:
                self.logger.warning(f"TimeSystem 연동 실패: {str(e)}")
        
        # 아이템 생성 (필요시) - write_config에 result_item_id가 있으면 생성
        result_item_id = write_config.get('result_item_id')
        if result_item_id and self.inventory_manager:
            await self.inventory_manager.add_item_to_inventory(
                entity_id,
                result_item_id,
                quantity=1
            )
        
        return ActionResult.success_result(
            f"{object_name}에 내용을 작성했습니다.",
            data={"state": "written", "content": content}
        )
    
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """기본 핸들러 (read)"""
        return await self.handle_read(entity_id, target_id, parameters)

