"""
소비 상호작용 핸들러 (eat, drink, consume)
"""
from typing import Dict, Any, Optional
from app.handlers.object_interaction_base import ObjectInteractionHandlerBase
from app.handlers.action_handler import ActionResult


class ConsumptionInteractionHandler(ObjectInteractionHandlerBase):
    """소비 상호작용 핸들러"""
    
    async def handle_eat(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에서 음식 먹기"""
        # TODO: 구현 예정 (EAT_FROM_OBJECT)
        return ActionResult.failure_result("아직 구현되지 않은 기능입니다.")
    
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
            # TODO: EffectCarrierManager로 효과 적용
            pass
        
        object_name = object_state.get('object_name', '오브젝트')
        
        # TODO: TimeSystem 연동
        
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

