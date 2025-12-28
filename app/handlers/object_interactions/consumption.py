"""
소비 상호작용 핸들러 (eat, drink, consume)
"""
from typing import Dict, Any, Optional
from app.handlers.object_interaction_base import ObjectInteractionHandlerBase
from app.handlers.action_result import ActionResult


class ConsumptionInteractionHandler(ObjectInteractionHandlerBase):
    """소비 상호작용 핸들러"""
    
    async def handle_eat(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에서 음식 먹기"""
        if not self.entity_manager:
            return ActionResult.failure_result("EntityManager가 초기화되지 않았습니다.")
        
        session_id = parameters.get("session_id") if parameters else None
        if not session_id:
            return ActionResult.failure_result("세션 ID가 필요합니다.")
        
        runtime_object_id, game_object_id = await self._parse_object_id(target_id, session_id)
        
        if not game_object_id:
            return ActionResult.failure_result("오브젝트를 찾을 수 없습니다.")
        
        object_state = await self._get_object_state(runtime_object_id, game_object_id, session_id)
        
        if not object_state:
            return ActionResult.failure_result("오브젝트 상태를 조회할 수 없습니다.")
        
        # 오브젝트의 contents에서 아이템 ID 추출
        contents = object_state.get('current_state', {}).get('contents', [])
        if not contents:
            return ActionResult.failure_result("오브젝트에 먹을 수 있는 아이템이 없습니다.")
        
        # 첫 번째 아이템 사용 (또는 parameters에서 지정)
        item_id = parameters.get("item_id") if parameters else contents[0]
        if item_id not in contents:
            return ActionResult.failure_result(f"오브젝트에 '{item_id}' 아이템이 없습니다.")
        
        # 아이템 템플릿 조회
        pool = await self.db.pool
        async with pool.acquire() as conn:
            item_template = await conn.fetchrow(
                """
                SELECT item_id, item_name, item_type, item_properties
                FROM game_data.items
                WHERE item_id = $1
                """,
                item_id
            )
            
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
        
        # 오브젝트에서 아이템 제거
        updated_contents = [item for item in contents if item != item_id]
        updated_state = await self._update_object_state(
            runtime_object_id,
            game_object_id,
            session_id,
            contents=updated_contents
        )
        
        if not updated_state:
            return ActionResult.failure_result("오브젝트 상태를 업데이트할 수 없습니다.")
        
        # 엔티티 HP/MP 회복
        restore_result = await self.entity_manager.restore_hp_mp(
            entity_id,
            hp=hp_restore,
            mp=mp_restore
        )
        
        if not restore_result.success:
            return ActionResult.failure_result(restore_result.message)
        
        # EffectCarrier 적용
        if effect_carrier_id and self.effect_carrier_manager:
            effect_result = await self.effect_carrier_manager.grant_effect_to_entity(
                session_id=session_id,
                entity_id=entity_id,
                effect_id=effect_carrier_id,
                source=f"eat_from_object:{item_id}"
            )
            if not effect_result.success:
                self.logger.warning(f"Effect Carrier 적용 실패: {effect_result.message}")
        
        # TimeSystem 연동
        time_cost = item_properties.get('interactions', {}).get('eat', {}).get('time_cost', 5)
        if time_cost > 0:
            # TimeSystem은 session_id를 통해 접근해야 함
            from app.systems.time_system import TimeSystem
            time_system = TimeSystem()
            try:
                await time_system.advance_time(minutes=time_cost)
            except Exception as e:
                self.logger.warning(f"TimeSystem 연동 실패: {str(e)}")
        
        item_name = item_template.get('item_name', item_id)
        object_name = object_state.get('object_name', '오브젝트')
        
        return ActionResult.success_result(
            f"{object_name}에서 {item_name}을(를) 먹었습니다. {restore_result.message}",
            data={
                "item_id": item_id,
                "hp_restored": hp_restore,
                "mp_restored": mp_restore,
                "effect_carrier_id": effect_carrier_id
            }
        )
    
    async def handle_drink(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에서 마시기"""
        if not self.entity_manager:
            return ActionResult.failure_result("EntityManager가 초기화되지 않았습니다.")
        
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
        drink_config = interactions.get('drink', {})
        
        mp_restore = drink_config.get('effects', {}).get('mp', 20)
        
        # 오브젝트 상태 업데이트
        updated_state = await self._update_object_state(
            runtime_object_id,
            game_object_id,
            session_id,
            state="consumed"
        )
        
        if not updated_state:
            return ActionResult.failure_result("오브젝트 상태를 업데이트할 수 없습니다.")
        
        # 엔티티 MP 회복
        restore_result = await self.entity_manager.restore_hp_mp(entity_id, mp=mp_restore)
        
        if not restore_result.success:
            return ActionResult.failure_result(restore_result.message)
        
        # EffectCarrier 적용
        effect_carrier_id = drink_config.get('effect_carrier_id')
        if effect_carrier_id and self.effect_carrier_manager:
            effect_result = await self.effect_carrier_manager.grant_effect_to_entity(
                session_id=session_id,
                entity_id=entity_id,
                effect_id=effect_carrier_id,
                source=f"drink_from_object:{game_object_id}"
            )
            if not effect_result.success:
                self.logger.warning(f"Effect Carrier 적용 실패: {effect_result.message}")
        
        object_name = object_state.get('object_name', '오브젝트')
        
        # TimeSystem 연동
        time_cost = drink_config.get('time_cost', 5)
        if time_cost > 0:
            from app.systems.time_system import TimeSystem
            time_system = TimeSystem()
            try:
                await time_system.advance_time(minutes=time_cost)
            except Exception as e:
                self.logger.warning(f"TimeSystem 연동 실패: {str(e)}")
        
        return ActionResult.success_result(
            f"{object_name}을(를) 마셨습니다. {restore_result.message}",
            data={"state": "consumed", "mp_restored": mp_restore}
        )
    
    async def handle_consume(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 일반 소비"""
        return await self.handle_eat(entity_id, target_id, parameters)
    
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """기본 핸들러 (eat)"""
        return await self.handle_eat(entity_id, target_id, parameters)

