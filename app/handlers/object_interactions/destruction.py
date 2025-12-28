"""
파괴/변형 상호작용 핸들러 (destroy, break, dismantle)
"""
from typing import Dict, Any, Optional
from app.handlers.object_interaction_base import ObjectInteractionHandlerBase
from app.handlers.action_result import ActionResult


class DestructionInteractionHandler(ObjectInteractionHandlerBase):
    """파괴/변형 상호작용 핸들러"""
    
    async def handle_destroy(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 파괴하기"""
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
        destroy_config = interactions.get('destroy', {})
        
        # 파괴 시 생성되는 아이템
        result_items = destroy_config.get('result_items', [])
        
        # 오브젝트 상태 업데이트
        updated_state = await self._update_object_state(
            runtime_object_id,
            game_object_id,
            session_id,
            state="destroyed"
        )
        
        if not updated_state:
            return ActionResult.failure_result("오브젝트 상태를 업데이트할 수 없습니다.")
        
        # 결과 아이템을 인벤토리에 추가
        if result_items and self.inventory_manager:
            for item_id in result_items:
                await self.inventory_manager.add_item_to_inventory(
                    entity_id,
                    item_id,
                    quantity=1
                )
        
        object_name = object_state.get('object_name', '오브젝트')
        
        # TimeSystem 연동
        time_cost = destroy_config.get('time_cost', 10)
        if time_cost > 0:
            from app.systems.time_system import TimeSystem
            time_system = TimeSystem()
            try:
                await time_system.advance_time(minutes=time_cost)
            except Exception as e:
                self.logger.warning(f"TimeSystem 연동 실패: {str(e)}")
        
        return ActionResult.success_result(
            f"{object_name}을(를) 파괴했습니다.",
            data={"state": "destroyed", "result_items": result_items}
        )
    
    async def handle_break(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 부수기"""
        # destroy와 유사하지만 파편 생성
        return await self.handle_destroy(entity_id, target_id, parameters)
    
    async def handle_dismantle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 분해하기"""
        if not self.inventory_manager:
            return ActionResult.failure_result("InventoryManager가 초기화되지 않았습니다.")
        
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
        dismantle_config = interactions.get('dismantle', {})
        
        # 분해 결과 부품 아이템
        result_items = dismantle_config.get('result_items', [])
        
        if not result_items:
            return ActionResult.failure_result("분해 결과 아이템이 정의되지 않았습니다.")
        
        # 오브젝트 상태 업데이트 (분해됨)
        updated_state = await self._update_object_state(
            runtime_object_id,
            game_object_id,
            session_id,
            state="dismantled"
        )
        
        if not updated_state:
            return ActionResult.failure_result("오브젝트 상태를 업데이트할 수 없습니다.")
        
        # 결과 부품 아이템을 인벤토리에 추가
        for item_id in result_items:
            await self.inventory_manager.add_item_to_inventory(
                entity_id,
                item_id,
                quantity=1
            )
        
        # TimeSystem 연동 (분해는 시간 소모)
        time_cost = dismantle_config.get('time_cost', 30)
        if time_cost > 0:
            from app.systems.time_system import TimeSystem
            time_system = TimeSystem()
            try:
                await time_system.advance_time(minutes=time_cost)
            except Exception as e:
                self.logger.warning(f"TimeSystem 연동 실패: {str(e)}")
        
        object_name = object_state.get('object_name', '오브젝트')
        
        return ActionResult.success_result(
            f"{object_name}을(를) 분해했습니다. {len(result_items)}개의 부품을 획득했습니다.",
            data={"state": "dismantled", "result_items": result_items}
        )
    
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """기본 핸들러 (destroy)"""
        return await self.handle_destroy(entity_id, target_id, parameters)

