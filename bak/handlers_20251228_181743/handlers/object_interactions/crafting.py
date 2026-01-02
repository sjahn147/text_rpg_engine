"""
조합/제작 상호작용 핸들러 (combine, craft, cook, repair)
"""
from typing import Dict, Any, Optional
from app.handlers.object_interaction_base import ObjectInteractionHandlerBase
from app.handlers.action_handler import ActionResult


class CraftingInteractionHandler(ObjectInteractionHandlerBase):
    """조합/제작 상호작용 핸들러"""
    
    async def handle_combine(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트와 아이템 조합하기"""
        # TODO: 구현 예정 (COMBINE_WITH_OBJECT)
        return ActionResult.failure_result("아직 구현되지 않은 기능입니다.")
    
    async def handle_craft(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에서 제작하기"""
        # TODO: 구현 예정 (재료 + 오브젝트 → 결과, 시간 소모)
        return ActionResult.failure_result("아직 구현되지 않은 기능입니다.")
    
    async def handle_cook(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에서 요리하기"""
        # TODO: 구현 예정 (재료 → 음식, 시간 소모)
        return ActionResult.failure_result("아직 구현되지 않은 기능입니다.")
    
    async def handle_repair(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 수리하기"""
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
        repair_config = interactions.get('repair', {})
        
        # 필요한 재료 확인
        required_items = repair_config.get('required_items', [])
        for item_id in required_items:
            # 인벤토리에서 재료 소모
            remove_result = await self.inventory_manager.remove_item_from_inventory(
                entity_id,
                item_id,
                quantity=1
            )
            if not remove_result:
                return ActionResult.failure_result(f"수리에 필요한 재료가 없습니다: {item_id}")
        
        # 오브젝트 상태 업데이트
        updated_state = await self._update_object_state(
            runtime_object_id,
            game_object_id,
            session_id,
            state="repaired"
        )
        
        if not updated_state:
            # 실패 시 재료 복구
            for item_id in required_items:
                await self.inventory_manager.add_item_to_inventory(entity_id, item_id, quantity=1)
            return ActionResult.failure_result("오브젝트 상태를 업데이트할 수 없습니다.")
        
        object_name = object_state.get('object_name', '오브젝트')
        
        # TODO: TimeSystem 연동
        
        return ActionResult.success_result(
            f"{object_name}을(를) 수리했습니다.",
            data={"state": "repaired", "required_items": required_items}
        )
    
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """기본 핸들러 (combine)"""
        return await self.handle_combine(entity_id, target_id, parameters)

