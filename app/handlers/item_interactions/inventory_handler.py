"""
인벤토리 관리 핸들러
아이템 버리기 등 인벤토리 관리 처리
"""
from typing import Dict, Any, Optional
from app.handlers.action_handler_base import ActionHandlerBase
from app.handlers.action_result import ActionResult


class InventoryItemHandler(ActionHandlerBase):
    """인벤토리 관리 핸들러"""
    
    async def handle_drop_item(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """아이템 버리기"""
        if not parameters or "item_id" not in parameters:
            return ActionResult.failure_result("버릴 아이템을 지정해주세요.")
        
        if not self.inventory_manager:
            return ActionResult.failure_result("InventoryManager가 초기화되지 않았습니다.")
        
        if not self.cell_manager:
            return ActionResult.failure_result("CellManager가 초기화되지 않았습니다.")
        
        item_id = parameters["item_id"]
        session_id = parameters.get("session_id") if parameters else None
        
        if not session_id:
            return ActionResult.failure_result("세션 ID가 필요합니다.")
        
        # 인벤토리에서 아이템 확인
        pool = await self.db.pool
        async with pool.acquire() as conn:
            entity_state = await conn.fetchrow(
                """
                SELECT inventory, current_position
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
            
            # 현재 셀 조회
            current_position = json.loads(entity_state['current_position']) if isinstance(entity_state['current_position'], str) else entity_state['current_position']
            current_cell_id = current_position.get('runtime_cell_id')
            
            if not current_cell_id:
                return ActionResult.failure_result("현재 위치한 셀을 찾을 수 없습니다.")
        
        # 인벤토리에서 아이템 제거
        remove_result = await self.inventory_manager.remove_item_from_inventory(
            entity_id,
            item_id,
            quantity=1
        )
        
        if not remove_result:
            return ActionResult.failure_result("인벤토리에서 아이템을 제거할 수 없습니다.")
        
        # 셀 contents에 아이템 추가 (간단한 구현: 셀의 contents JSONB에 item_id 추가)
        # TODO: 더 정교한 구현은 오브젝트 생성 또는 셀 contents 구조에 맞춰 구현 필요
        async with pool.acquire() as conn:
            cell_state = await conn.fetchrow(
                """
                SELECT contents
                FROM runtime_data.runtime_cells
                WHERE runtime_cell_id = $1
                """,
                current_cell_id
            )
            
            if cell_state:
                contents = json.loads(cell_state['contents']) if isinstance(cell_state['contents'], str) else cell_state['contents']
                if not contents:
                    contents = {"items": []}
                
                if "items" not in contents:
                    contents["items"] = []
                
                if item_id not in contents["items"]:
                    contents["items"].append(item_id)
                
                await conn.execute(
                    """
                    UPDATE runtime_data.runtime_cells
                    SET contents = $1::jsonb,
                        updated_at = NOW()
                    WHERE runtime_cell_id = $2
                    """,
                    json.dumps(contents),
                    current_cell_id
                )
        
        from database.repositories.game_data import GameDataRepository
        game_data_repo = GameDataRepository(self.db)
        item_template = await game_data_repo.get_item(item_id)
        item_name = item_template.get('item_name', item_id) if item_template else item_id
        
        return ActionResult.success_result(
            f"{item_name}을(를) 버렸습니다.",
            data={"item_id": item_id, "cell_id": current_cell_id}
        )
    
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """기본 핸들러 (drop_item)"""
        return await self.handle_drop_item(entity_id, target_id, parameters)

