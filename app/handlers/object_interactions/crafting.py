"""
조합/제작 상호작용 핸들러 (combine, craft, cook, repair)
"""
import random
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from app.handlers.object_interaction_base import ObjectInteractionHandlerBase
from app.handlers.action_result import ActionResult
from database.repositories.game_data import GameDataRepository
from common.utils.jsonb_handler import serialize_jsonb_data, parse_jsonb_data


class CraftingInteractionHandler(ObjectInteractionHandlerBase):
    """조합/제작 상호작용 핸들러"""
    
    async def handle_combine(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """
        아이템 조합 (Effect Carrier 기반 자유 조합)
        
        모든 아이템을 자유롭게 조합할 수 있으며, Effect Carrier를 가진 아이템들의
        Effect Carrier를 모두 포함한 새 아이템을 생성합니다.
        """
        if not self.inventory_manager:
            return ActionResult.failure_result("InventoryManager가 초기화되지 않았습니다.")
        
        session_id = parameters.get("session_id") if parameters else None
        if not session_id:
            return ActionResult.failure_result("세션 ID가 필요합니다.")
        
        # 입력 아이템 수집 (parameters에서 가져오기)
        input_items = parameters.get("items", []) if parameters else []
        
        # 최소/최대 개수 확인
        if len(input_items) < 2:
            return ActionResult.failure_result("조합하려면 최소 2개의 아이템이 필요합니다.")
        if len(input_items) > 5:
            return ActionResult.failure_result("조합은 최대 5개의 아이템까지만 가능합니다.")
        
        # 1. 각 아이템의 Effect Carrier 수집
        item_carriers = await self._collect_item_effect_carriers(input_items)
        
        # 2. 성공률 계산 (개수 페널티 적용)
        success_rate = self._calculate_combination_success_rate(input_items, item_carriers)
        
        # 3. 성공/실패 판정
        is_success = random.random() < success_rate
        
        if not is_success:
            # 4. 실패: 일부 재료만 소모
            consumed_items = self._determine_consumed_items_on_failure(input_items, item_carriers)
            
            # 재료 소모
            for item_id in consumed_items:
                await self.inventory_manager.remove_item_from_inventory(
                    entity_id,
                    item_id,
                    quantity=1
                )
            
            return ActionResult.failure_result(
                f"조합 실패 (성공률: {success_rate:.1%}). 일부 재료가 소모되었습니다.",
                data={
                    "success_rate": success_rate,
                    "consumed_items": consumed_items
                }
            )
        
        # 5. 성공: 모든 재료 소모
        for item_id in input_items:
            await self.inventory_manager.remove_item_from_inventory(
                entity_id,
                item_id,
                quantity=1
            )
        
        # 6. 조합된 아이템 생성
        result_item_id = await self._create_combined_item(
            input_items,
            item_carriers,
            session_id
        )
        
        if not result_item_id:
            # 실패 시 재료 복구
            for item_id in input_items:
                await self.inventory_manager.add_item_to_inventory(entity_id, item_id, quantity=1)
            return ActionResult.failure_result("조합된 아이템 생성에 실패했습니다.")
        
        # 7. 결과 아이템을 인벤토리에 추가
        await self.inventory_manager.add_item_to_inventory(
            entity_id,
            result_item_id,
            quantity=1
        )
        
        # 8. TimeSystem 연동
        time_cost = 10  # 기본 10분
        if time_cost > 0:
            from app.systems.time_system import TimeSystem
            time_system = TimeSystem()
            try:
                await time_system.advance_time(minutes=time_cost)
            except Exception as e:
                self.logger.warning(f"TimeSystem 연동 실패: {str(e)}")
        
        effect_carrier_count = len(item_carriers)
        message = f"조합 성공! {result_item_id}을(를) 획득했습니다."
        if effect_carrier_count > 0:
            message += f" ({effect_carrier_count}개의 효과 포함)"
        
        return ActionResult.success_result(
            message,
            data={
                "result_item_id": result_item_id,
                "consumed_items": input_items,
                "effect_carrier_ids": [ic["carrier"].effect_id for ic in item_carriers],
                "success_rate": success_rate
            }
        )
    
    async def _collect_item_effect_carriers(
        self,
        input_items: List[str]
    ) -> List[Dict[str, Any]]:
        """
        입력 아이템들의 Effect Carrier 수집
        
        Returns:
            [{"item_id": str, "carrier": EffectCarrierData}, ...]
            EffectCarrierData는 effect_carrier_manager의 결과에서 가져옴
        """
        item_carriers = []
        game_data_repo = GameDataRepository(self.db)
        
        for item_id in input_items:
            # 아이템 템플릿 조회
            item_template = await game_data_repo.get_item(item_id)
            if not item_template:
                continue
            
            # item_properties 파싱
            item_properties = item_template.get('item_properties', {})
            if isinstance(item_properties, str):
                import json
                item_properties = json.loads(item_properties)
            
            # Effect Carrier ID 확인
            effect_carrier_id = item_template.get('effect_carrier_id')
            
            # item_properties.effect_carrier_ids도 확인 (조합된 아이템)
            effect_carrier_ids = item_properties.get('effect_carrier_ids', [])
            
            # 단일 Effect Carrier가 있으면 추가
            if effect_carrier_id:
                if self.effect_carrier_manager:
                    carrier_result = await self.effect_carrier_manager.get_effect_carrier(str(effect_carrier_id))
                    if carrier_result.success and carrier_result.data:
                        item_carriers.append({
                            "item_id": item_id,
                            "carrier": carrier_result.data
                        })
                    else:
                        self.logger.warning(f"Effect Carrier 조회 실패: {effect_carrier_id}, result: {carrier_result}")
            
            # 여러 Effect Carrier가 있는 경우 모두 수집 (조합된 아이템)
            if effect_carrier_ids:
                for ec_id in effect_carrier_ids:
                    if self.effect_carrier_manager:
                        carrier_result = await self.effect_carrier_manager.get_effect_carrier(ec_id)
                        if carrier_result.success and carrier_result.data:
                            # 중복 방지
                            if not any(ic["carrier"].effect_id == ec_id for ic in item_carriers):
                                item_carriers.append({
                                    "item_id": item_id,
                                    "carrier": carrier_result.data
                                })
            
        
        return item_carriers
    
    def _calculate_combination_success_rate(
        self,
        input_items: List[str],
        item_carriers: List[Dict[str, Any]]
    ) -> float:
        """
        조합 성공률 계산
        
        공식:
        - 기본 성공률: 50%
        - 개수 페널티: 아이템당 8% 감소
        - Effect Carrier 보너스: Effect Carrier당 3% 증가
        - 범위: 10%~90%
        """
        base_success_rate = 0.5  # 기본 50%
        
        # 개수 페널티
        item_count = len(input_items)
        penalty_per_item = 0.08  # 아이템당 8% 페널티
        total_penalty = item_count * penalty_per_item
        
        # Effect Carrier 보너스
        carrier_count = len(item_carriers)
        bonus_per_carrier = 0.03  # Effect Carrier당 3% 보너스
        total_bonus = carrier_count * bonus_per_carrier
        
        # 최종 성공률
        success_rate = base_success_rate - total_penalty + total_bonus
        success_rate = max(0.1, min(0.9, success_rate))  # 10%~90% 범위
        
        return success_rate
    
    def _determine_consumed_items_on_failure(
        self,
        input_items: List[str],
        item_carriers: List[Dict[str, Any]]
    ) -> List[str]:
        """
        실패 시 소모될 재료 결정
        
        규칙:
        1. Effect Carrier가 없는 아이템 우선 소모
        2. 최소 1개, 최대 입력 개수의 50% 소모
        """
        # Effect Carrier가 없는 아이템 찾기
        items_with_carrier = {ic["item_id"] for ic in item_carriers}
        items_without_carrier = [item_id for item_id in input_items 
                                if item_id not in items_with_carrier]
        
        if items_without_carrier:
            # Effect Carrier 없는 아이템 중 1개 랜덤 선택
            return [random.choice(items_without_carrier)]
        else:
            # 모두 Effect Carrier가 있으면 랜덤으로 1개 선택
            consume_count = max(1, len(input_items) // 2)
            return random.sample(input_items, min(consume_count, len(input_items)))
    
    async def _create_combined_item(
        self,
        input_items: List[str],
        item_carriers: List[Dict[str, Any]],
        session_id: str
    ) -> Optional[str]:
        """
        조합된 아이템 생성
        
        Args:
            input_items: 입력 아이템 ID 목록
            item_carriers: Effect Carrier 정보 목록
            session_id: 세션 ID
        
        Returns:
            새로 생성된 아이템 ID
        """
        try:
            game_data_repo = GameDataRepository(self.db)
            
            # 1. 첫 번째 아이템의 속성 상속
            first_item = await game_data_repo.get_item(input_items[0])
            if not first_item:
                return None
            
            item_type = first_item.get('item_type', 'consumable')
            stack_size = first_item.get('stack_size', 1)
            consumable = first_item.get('consumable', True)
            base_property_id = first_item.get('base_property_id', f"BASE_COMBINED_{uuid.uuid4().hex[:8]}")
            
            # 2. Effect Carrier ID 수집
            effect_carrier_ids = [ic["carrier"].effect_id for ic in item_carriers]
            
            # 3. 새 아이템 ID 생성
            short_uuid = uuid.uuid4().hex[:8].upper()
            new_item_id = f"ITEM_COMBINED_{short_uuid}"
            
            # 4. item_properties 구성
            item_properties = {
                "combined_from": input_items,
                "effect_carrier_ids": effect_carrier_ids,
                "base_name": "Combined Item",
                "custom_name": None,
                "combination_date": datetime.now().isoformat()
            }
            
            # 5. 아이템 템플릿 생성
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # base_property가 없으면 생성
                prop_check = await conn.fetchrow(
                    """
                    SELECT property_id FROM game_data.base_properties WHERE property_id = $1
                    """,
                    base_property_id
                )
                
                if not prop_check:
                    # 기본 base_property 생성
                    await conn.execute(
                        """
                        INSERT INTO game_data.base_properties
                        (property_id, name, description, type, base_effects, requirements)
                        VALUES ($1, $2, $3, $4, $5::jsonb, $6::jsonb)
                        """,
                        base_property_id,
                        "Combined Item Base",
                        "조합으로 생성된 아이템",
                        "item",
                        "{}",
                        "{}"
                    )
                
                # 아이템 생성
                await conn.execute(
                    """
                    INSERT INTO game_data.items
                    (item_id, base_property_id, item_type, stack_size, consumable, 
                     effect_carrier_id, item_properties, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """,
                    new_item_id,
                    base_property_id,
                    item_type,
                    stack_size,
                    consumable,
                    None,  # 단일 Effect Carrier 없음 (여러 개는 item_properties에)
                    serialize_jsonb_data(item_properties)
                )
            
            self.logger.info(f"조합된 아이템 생성 완료: {new_item_id} (Effect Carrier {len(effect_carrier_ids)}개)")
            return new_item_id
            
        except Exception as e:
            self.logger.error(f"조합된 아이템 생성 실패: {str(e)}")
            return None
    
    async def handle_craft(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에서 제작하기"""
        # combine과 유사하지만 제작 레시피 사용
        return await self.handle_combine(entity_id, target_id, parameters)
    
    async def handle_cook(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에서 요리하기"""
        # combine과 유사하지만 요리 레시피 사용 (더 긴 시간 소모)
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
        cook_config = interactions.get('cook', {})
        
        # 필요한 재료 확인 (인벤토리)
        required_items = cook_config.get('required_items', [])
        
        # 재료 소모
        for item_id in required_items:
            remove_result = await self.inventory_manager.remove_item_from_inventory(
                entity_id,
                item_id,
                quantity=1
            )
            if not remove_result:
                # 실패 시 재료 복구
                for consumed in required_items[:required_items.index(item_id)]:
                    await self.inventory_manager.add_item_to_inventory(entity_id, consumed, quantity=1)
                return ActionResult.failure_result(f"요리에 필요한 재료가 없습니다: {item_id}")
        
        # 결과 음식 아이템 생성
        result_item_id = cook_config.get('result_item_id')
        if not result_item_id:
            # 재료 복구
            for item_id in required_items:
                await self.inventory_manager.add_item_to_inventory(entity_id, item_id, quantity=1)
            return ActionResult.failure_result("요리 결과 아이템이 정의되지 않았습니다.")
        
        # 결과 아이템을 인벤토리에 추가
        await self.inventory_manager.add_item_to_inventory(
            entity_id,
            result_item_id,
            quantity=1
        )
        
        # TimeSystem 연동 (요리는 더 긴 시간 소모)
        time_cost = cook_config.get('time_cost', 60)
        if time_cost > 0:
            from app.systems.time_system import TimeSystem
            time_system = TimeSystem()
            try:
                await time_system.advance_time(minutes=time_cost)
            except Exception as e:
                self.logger.warning(f"TimeSystem 연동 실패: {str(e)}")
        
        object_name = object_state.get('object_name', '오브젝트')
        
        return ActionResult.success_result(
            f"{object_name}에서 요리를 완료했습니다. {result_item_id}을(를) 획득했습니다.",
            data={
                "result_item_id": result_item_id,
                "consumed_items": required_items
            }
        )
    
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
        
        # TimeSystem 연동
        time_cost = repair_config.get('time_cost', 30)
        if time_cost > 0:
            from app.systems.time_system import TimeSystem
            time_system = TimeSystem()
            try:
                await time_system.advance_time(minutes=time_cost)
            except Exception as e:
                self.logger.warning(f"TimeSystem 연동 실패: {str(e)}")
        
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

