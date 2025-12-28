"""
아이템 사용 핸들러
인벤토리 아이템 사용 처리
"""
from typing import Dict, Any, Optional
from app.handlers.action_handler_base import ActionHandlerBase
from app.handlers.action_result import ActionResult


class UseItemHandler(ActionHandlerBase):
    """아이템 사용 핸들러"""
    
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """인벤토리 아이템 사용"""
        try:
            if not parameters or "item_id" not in parameters:
                return ActionResult.failure_result("사용할 아이템을 지정해주세요.")
            
            if not self.inventory_manager:
                return ActionResult.failure_result("InventoryManager가 초기화되지 않았습니다.")
            
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
            
            # Effect Carrier ID 확인 (단일 또는 여러 개)
            effect_carrier_id = item_template.get('effect_carrier_id')  # 단일 Effect Carrier
            effect_carrier_ids = item_properties.get('effect_carrier_ids', [])  # 여러 Effect Carrier (조합된 아이템)
            
            is_consumable = item_template.get('consumable', True)
            
            # 아이템 효과 적용
            if hp_restore > 0 or mp_restore > 0:
                if not self.entity_manager:
                    return ActionResult.failure_result("EntityManager가 초기화되지 않았습니다.")
                
                restore_result = await self.entity_manager.restore_hp_mp(
                    entity_id,
                    hp=hp_restore,
                    mp=mp_restore
                )
                
                if not restore_result.success:
                    return ActionResult.failure_result(restore_result.message)
            
            # EffectCarrier 적용
            # 1. 단일 Effect Carrier (effect_carrier_id)
            if effect_carrier_id and self.effect_carrier_manager and session_id:
                effect_result = await self.effect_carrier_manager.grant_effect_to_entity(
                    session_id=session_id,
                    entity_id=entity_id,
                    effect_id=effect_carrier_id,
                    source=f"use_item:{item_id}"
                )
                if not effect_result.success:
                    self.logger.warning(f"Effect Carrier 적용 실패: {effect_result.message}")
            
            # 2. 여러 Effect Carrier (조합된 아이템: item_properties.effect_carrier_ids)
            effect_carrier_ids = item_properties.get('effect_carrier_ids', [])
            if effect_carrier_ids and self.effect_carrier_manager and session_id:
                # 모든 Effect Carrier를 엔티티에 부여 (동시 작용)
                for ec_id in effect_carrier_ids:
                    effect_result = await self.effect_carrier_manager.grant_effect_to_entity(
                        session_id=session_id,
                        entity_id=entity_id,
                        effect_id=ec_id,
                        source=f"combined_item:{item_id}"
                    )
                    if not effect_result.success:
                        self.logger.warning(f"Effect Carrier 적용 실패 (ID: {ec_id}): {effect_result.message}")
            
            # 인벤토리에서 아이템 제거 (소비 가능 아이템인 경우)
            if is_consumable:
                remove_result = await self.inventory_manager.remove_item_from_inventory(
                    entity_id,
                    item_id,
                    quantity=1
                )
                
                if not remove_result:
                    return ActionResult.failure_result("인벤토리에서 아이템을 제거할 수 없습니다.")
            
            # TimeSystem 연동
            time_cost = item_properties.get('interactions', {}).get('use', {}).get('time_cost', 5)
            if time_cost > 0:
                from app.systems.time_system import TimeSystem
                time_system = TimeSystem()
                try:
                    await time_system.advance_time(minutes=time_cost)
                except Exception as e:
                    self.logger.warning(f"TimeSystem 연동 실패: {str(e)}")
            
            # 아이템 이름 확인 (조합된 아이템은 custom_name 또는 base_name 사용)
            item_name = item_id
            if item_properties.get('custom_name'):
                item_name = item_properties['custom_name']
            elif item_properties.get('base_name'):
                item_name = item_properties['base_name']
            else:
                # base_properties에서 이름 가져오기
                pool = await self.db.pool
                async with pool.acquire() as conn:
                    bp_row = await conn.fetchrow(
                        """
                        SELECT name FROM game_data.base_properties WHERE property_id = $1
                        """,
                        item_template.get('base_property_id')
                    )
                    if bp_row:
                        item_name = bp_row['name']
            
            message = f"{item_name}을(를) 사용했습니다."
            if hp_restore > 0 or mp_restore > 0:
                message += f" HP {hp_restore}, MP {mp_restore} 회복."
            
            # Effect Carrier 적용 개수 표시
            applied_carriers = []
            if effect_carrier_id:
                applied_carriers.append(effect_carrier_id)
            applied_carriers.extend(effect_carrier_ids)
            if applied_carriers:
                message += f" ({len(applied_carriers)}개의 효과 적용)"
            
            # 아이템 사용 데이터 생성
            use_item_data = {
                "entity_id": entity_id,
                "item_id": item_id,
                "target_id": target_id,
                "hp_restored": hp_restore,
                "mp_restored": mp_restore,
                "effect_carrier_id": effect_carrier_id,
                "effect_carrier_ids": effect_carrier_ids,
                "applied_carriers_count": len(applied_carriers)
            }
            
            return ActionResult.success_result(
                message=message,
                data=use_item_data,
                effects=[{"type": "use_item", "item_id": item_id}]
            )
            
        except Exception as e:
            self.logger.error(f"Use item action failed: {str(e)}")
            return ActionResult.failure_result(f"아이템 사용 실패: {str(e)}")

