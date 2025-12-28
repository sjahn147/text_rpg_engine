"""
아이템 조작 상호작용 핸들러 (pickup, place, take, put)
"""
from typing import Dict, Any, Optional
from app.handlers.object_interaction_base import ObjectInteractionHandlerBase
from app.handlers.action_result import ActionResult


class ItemManipulationInteractionHandler(ObjectInteractionHandlerBase):
    """아이템 조작 상호작용 핸들러"""
    
    async def handle_pickup(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에서 아이템 줍기"""
        if not self.inventory_manager:
            return ActionResult.failure_result("InventoryManager가 초기화되지 않았습니다.")
        
        item_id = parameters.get("item_id") if parameters else None
        if not item_id:
            return ActionResult.failure_result("아이템 ID가 필요합니다.")
        
        session_id = parameters.get("session_id") if parameters else None
        if not session_id:
            return ActionResult.failure_result("세션 ID가 필요합니다.")
        
        runtime_object_id, game_object_id = await self._parse_object_id(target_id, session_id)
        
        if not game_object_id:
            return ActionResult.failure_result("오브젝트를 찾을 수 없습니다.")
        
        # 오브젝트 contents에서 아이템 제거
        remove_result = await self.object_state_manager.remove_from_contents(
            runtime_object_id,
            game_object_id,
            session_id,
            item_id
        )
        
        if not remove_result.success:
            return ActionResult.failure_result(remove_result.message)
        
        # 인벤토리에 아이템 추가
        add_result = await self.inventory_manager.add_item_to_inventory(
            entity_id,
            item_id,
            quantity=1
        )
        
        if not add_result:
            # 실패 시 contents 복구
            await self.object_state_manager.add_to_contents(
                runtime_object_id,
                game_object_id,
                session_id,
                item_id
            )
            return ActionResult.failure_result("인벤토리에 아이템을 추가할 수 없습니다.")
        
        # 오브젝트 이름 조회
        object_state = await self._get_object_state(runtime_object_id, game_object_id, session_id)
        object_name = object_state.get('object_name', '오브젝트') if object_state else '오브젝트'
        
        return ActionResult.success_result(
            f"{object_name}에서 {item_id}을(를) 획득했습니다.",
            data={"item_id": item_id}
        )
    
    async def handle_place(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에 아이템 놓기"""
        if not self.inventory_manager:
            return ActionResult.failure_result("InventoryManager가 초기화되지 않았습니다.")
        
        item_id = parameters.get("item_id") if parameters else None
        if not item_id:
            return ActionResult.failure_result("아이템 ID가 필요합니다.")
        
        session_id = parameters.get("session_id") if parameters else None
        if not session_id:
            return ActionResult.failure_result("세션 ID가 필요합니다.")
        
        # 인벤토리에서 아이템 제거
        remove_result = await self.inventory_manager.remove_item_from_inventory(
            entity_id,
            item_id,
            quantity=1
        )
        
        if not remove_result:
            return ActionResult.failure_result("인벤토리에 해당 아이템이 없습니다.")
        
        runtime_object_id, game_object_id = await self._parse_object_id(target_id, session_id)
        
        if not game_object_id:
            # 실패 시 인벤토리 복구
            await self.inventory_manager.add_item_to_inventory(entity_id, item_id, quantity=1)
            return ActionResult.failure_result("오브젝트를 찾을 수 없습니다.")
        
        # 오브젝트 contents에 아이템 추가
        add_result = await self.object_state_manager.add_to_contents(
            runtime_object_id,
            game_object_id,
            session_id,
            item_id
        )
        
        if not add_result.success:
            # 실패 시 인벤토리 복구
            await self.inventory_manager.add_item_to_inventory(entity_id, item_id, quantity=1)
            return ActionResult.failure_result(add_result.message)
        
        # 오브젝트 이름 조회
        object_state = await self._get_object_state(runtime_object_id, game_object_id, session_id)
        object_name = object_state.get('object_name', '오브젝트') if object_state else '오브젝트'
        
        return ActionResult.success_result(
            f"{object_name}에 {item_id}을(를) 놓았습니다.",
            data={"item_id": item_id}
        )
    
    async def handle_take(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에서 가져가기 (pickup과 동일)"""
        return await self.handle_pickup(entity_id, target_id, parameters)
    
    async def handle_put(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에 넣기 (place와 동일)"""
        return await self.handle_place(entity_id, target_id, parameters)
    
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """기본 핸들러 (pickup)"""
        return await self.handle_pickup(entity_id, target_id, parameters)

