"""
아이템 소비 핸들러
인벤토리 아이템 먹기/마시기/소비 처리
"""
from typing import Dict, Any, Optional
from app.handlers.action_handler_base import ActionHandlerBase
from app.handlers.action_result import ActionResult


class ConsumptionItemHandler(ActionHandlerBase):
    """아이템 소비 핸들러"""
    
    async def handle_eat_item(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """인벤토리에서 아이템 먹기"""
        if not parameters or "item_id" not in parameters:
            return ActionResult.failure_result("먹을 아이템을 지정해주세요.")
        
        if not self.inventory_manager:
            return ActionResult.failure_result("InventoryManager가 초기화되지 않았습니다.")
        
        if not self.entity_manager:
            return ActionResult.failure_result("EntityManager가 초기화되지 않았습니다.")
        
        item_id = parameters["item_id"]
        session_id = parameters.get("session_id") if parameters else None
        
        # 인벤토리에서 아이템 확인
        pool = await self.db.pool
        async with pool.acquire() as conn:
            entity_state = await conn.fetchrow(
                """
                SELECT inventory
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
        
        # 아이템 템플릿 조회
        from database.repositories.game_data import GameDataRepository
        game_data_repo = GameDataRepository(self.db)
        item_template = await game_data_repo.get_item(item_id)
        
        if not item_template:
            return ActionResult.failure_result(f"아이템 템플릿을 찾을 수 없습니다: {item_id}")
        
        # 아이템 속성에서 효과 확인
        item_properties = item_template.get('item_properties', {})
        if isinstance(item_properties, str):
            import json
            item_properties = json.loads(item_properties)
        
        effects = item_properties.get('effects', {})
        hp_restore = effects.get('hp', 0)
        mp_restore = effects.get('mp', 0)
        effect_carrier_id = item_properties.get('effect_carrier_id')
        
        # HP/MP 회복 효과 적용
        restore_result = await self.entity_manager.restore_hp_mp(
            entity_id,
            hp=hp_restore,
            mp=mp_restore
        )
        
        if not restore_result.success:
            return ActionResult.failure_result(restore_result.message)
        
        # EffectCarrier 적용
        if effect_carrier_id and self.effect_carrier_manager and session_id:
            effect_result = await self.effect_carrier_manager.grant_effect_to_entity(
                session_id=session_id,
                entity_id=entity_id,
                effect_id=effect_carrier_id,
                source=f"eat_item:{item_id}"
            )
            if not effect_result.success:
                self.logger.warning(f"Effect Carrier 적용 실패: {effect_result.message}")
        
        # 인벤토리에서 아이템 제거 (소비 가능 아이템)
        remove_result = await self.inventory_manager.remove_item_from_inventory(
            entity_id,
            item_id,
            quantity=1
        )
        
        if not remove_result:
            return ActionResult.failure_result("인벤토리에서 아이템을 제거할 수 없습니다.")
        
        # TimeSystem 연동
        time_cost = item_properties.get('interactions', {}).get('eat', {}).get('time_cost', 5)
        if time_cost > 0:
            from app.systems.time_system import TimeSystem
            time_system = TimeSystem()
            try:
                await time_system.advance_time(minutes=time_cost)
            except Exception as e:
                self.logger.warning(f"TimeSystem 연동 실패: {str(e)}")
        
        item_name = item_template.get('item_name', item_id)
        
        return ActionResult.success_result(
            f"{item_name}을(를) 먹었습니다. {restore_result.message}",
            data={
                "item_id": item_id,
                "hp_restored": hp_restore,
                "mp_restored": mp_restore,
                "effect_carrier_id": effect_carrier_id
            }
        )
    
    async def handle_drink_item(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """인벤토리에서 아이템 마시기"""
        # handle_eat_item과 동일한 로직
        return await self.handle_eat_item(entity_id, target_id, parameters)
    
    async def handle_consume_item(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """인벤토리에서 아이템 소비"""
        # handle_eat_item과 동일한 로직
        return await self.handle_eat_item(entity_id, target_id, parameters)
    
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """기본 핸들러 (eat_item)"""
        return await self.handle_eat_item(entity_id, target_id, parameters)

