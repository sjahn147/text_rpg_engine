"""
아이템 장착 핸들러
아이템 장착/해제 처리
"""
from typing import Dict, Any, Optional
from app.handlers.action_handler_base import ActionHandlerBase
from app.handlers.action_result import ActionResult


class EquipmentItemHandler(ActionHandlerBase):
    """아이템 장착 핸들러"""
    
    async def handle_equip_item(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """아이템 장착"""
        if not parameters or "item_id" not in parameters:
            return ActionResult.failure_result("장착할 아이템을 지정해주세요.")
        
        if not self.inventory_manager:
            return ActionResult.failure_result("InventoryManager가 초기화되지 않았습니다.")
        
        item_id = parameters["item_id"]
        
        # 인벤토리에서 아이템 확인
        pool = await self.db.pool
        async with pool.acquire() as conn:
            entity_state = await conn.fetchrow(
                """
                SELECT inventory, equipped_items
                FROM runtime_data.entity_states
                WHERE runtime_entity_id = $1
                """,
                entity_id
            )
            
            if not entity_state:
                return ActionResult.failure_result("엔티티 상태를 찾을 수 없습니다.")
            
            import json
            inventory = json.loads(entity_state['inventory']) if isinstance(entity_state['inventory'], str) else entity_state['inventory']
            quantities = inventory.get("quantities", {})
            
            if quantities.get(item_id, 0) < 1:
                return ActionResult.failure_result(f"인벤토리에 '{item_id}' 아이템이 없습니다.")
        
        # 아이템 템플릿 조회하여 장착 가능 여부 확인
        from database.repositories.game_data import GameDataRepository
        game_data_repo = GameDataRepository(self.db)
        item_template = await game_data_repo.get_item(item_id)
        
        if not item_template:
            return ActionResult.failure_result(f"아이템 템플릿을 찾을 수 없습니다: {item_id}")
        
        item_type = item_template.get('item_type', '')
        item_properties = item_template.get('item_properties', {})
        if isinstance(item_properties, str):
            import json
            item_properties = json.loads(item_properties)
        
        # 장착 가능 여부 확인 (equipment 타입만 장착 가능)
        equipment_slot = item_properties.get('equipment_slot')
        if not equipment_slot:
            return ActionResult.failure_result(f"'{item_id}'는 장착할 수 없는 아이템입니다.")
        
        # 기존 장착 아이템 확인 및 해제
        equipped_items = json.loads(entity_state['equipped_items']) if isinstance(entity_state['equipped_items'], str) else entity_state['equipped_items']
        if not equipped_items:
            equipped_items = {}
        
        old_item_id = equipped_items.get(equipment_slot)
        if old_item_id:
            # 기존 장착 아이템을 인벤토리에 추가
            await self.inventory_manager.add_item_to_inventory(entity_id, old_item_id, quantity=1)
        
        # 아이템 장착 (인벤토리에서 제거, 장착 슬롯에 추가)
        remove_result = await self.inventory_manager.remove_item_from_inventory(
            entity_id,
            item_id,
            quantity=1
        )
        
        if not remove_result:
            return ActionResult.failure_result("인벤토리에서 아이템을 제거할 수 없습니다.")
        
        # equipped_items 업데이트
        equipped_items[equipment_slot] = item_id
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE runtime_data.entity_states
                SET equipped_items = $1::jsonb,
                    updated_at = NOW()
                WHERE runtime_entity_id = $2
                """,
                json.dumps(equipped_items),
                entity_id
            )
        
        item_name = item_template.get('item_name', item_id)
        
        return ActionResult.success_result(
            f"{item_name}을(를) {equipment_slot} 슬롯에 장착했습니다.",
            data={"equipment_slot": equipment_slot, "item_id": item_id}
        )
    
    async def handle_unequip_item(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """아이템 해제"""
        if not parameters or "item_id" not in parameters:
            return ActionResult.failure_result("해제할 아이템을 지정해주세요.")
        
        if not self.inventory_manager:
            return ActionResult.failure_result("InventoryManager가 초기화되지 않았습니다.")
        
        item_id = parameters["item_id"]
        
        # 장착 슬롯에서 아이템 확인
        pool = await self.db.pool
        async with pool.acquire() as conn:
            entity_state = await conn.fetchrow(
                """
                SELECT equipped_items
                FROM runtime_data.entity_states
                WHERE runtime_entity_id = $1
                """,
                entity_id
            )
            
            if not entity_state:
                return ActionResult.failure_result("엔티티 상태를 찾을 수 없습니다.")
            
            import json
            equipped_items = json.loads(entity_state['equipped_items']) if isinstance(entity_state['equipped_items'], str) else entity_state['equipped_items']
            if not equipped_items:
                return ActionResult.failure_result("장착된 아이템이 없습니다.")
        
        # 장착된 아이템 찾기
        equipment_slot = None
        for slot, equipped_item_id in equipped_items.items():
            if equipped_item_id == item_id:
                equipment_slot = slot
                break
        
        if not equipment_slot:
            return ActionResult.failure_result(f"'{item_id}'는 장착되어 있지 않습니다.")
        
        # 인벤토리에 추가
        await self.inventory_manager.add_item_to_inventory(entity_id, item_id, quantity=1)
        
        # 장착 슬롯에서 제거
        del equipped_items[equipment_slot]
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE runtime_data.entity_states
                SET equipped_items = $1::jsonb,
                    updated_at = NOW()
                WHERE runtime_entity_id = $2
                """,
                json.dumps(equipped_items),
                entity_id
            )
        
        from database.repositories.game_data import GameDataRepository
        game_data_repo = GameDataRepository(self.db)
        item_template = await game_data_repo.get_item(item_id)
        item_name = item_template.get('item_name', item_id) if item_template else item_id
        
        return ActionResult.success_result(
            f"{item_name}을(를) {equipment_slot} 슬롯에서 해제했습니다.",
            data={"equipment_slot": equipment_slot, "item_id": item_id}
        )
    
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """기본 핸들러 (equip_item)"""
        return await self.handle_equip_item(entity_id, target_id, parameters)

