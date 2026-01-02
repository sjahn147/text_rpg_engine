"""
회복 상호작용 핸들러 (rest, sleep, meditate)
"""
from typing import Dict, Any, Optional
from app.handlers.object_interaction_base import ObjectInteractionHandlerBase
from app.handlers.action_handler import ActionResult


class RecoveryInteractionHandler(ObjectInteractionHandlerBase):
    """회복 상호작용 핸들러"""
    
    async def handle_rest(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에서 휴식"""
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
        rest_config = interactions.get('rest', {})
        
        # HP/MP 회복량 (기본값)
        hp_restore = rest_config.get('effects', {}).get('hp', 50)
        mp_restore = rest_config.get('effects', {}).get('mp', 30)
        
        # 오브젝트 상태 업데이트
        updated_state = await self._update_object_state(
            runtime_object_id,
            game_object_id,
            session_id,
            state="occupied"
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
        
        object_name = object_state.get('object_name', '오브젝트')
        
        return ActionResult.success_result(
            f"{object_name}에서 휴식했습니다. {restore_result.message}",
            data={
                "state": "occupied",
                "hp_restored": hp_restore,
                "mp_restored": mp_restore
            }
        )
    
    async def handle_sleep(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에서 잠자기"""
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
        sleep_config = interactions.get('sleep', {})
        
        # HP/MP 회복량 (기본값, sleep은 rest보다 많음)
        hp_restore = sleep_config.get('effects', {}).get('hp', 100)
        mp_restore = sleep_config.get('effects', {}).get('mp', 50)
        fatigue_reduce = sleep_config.get('effects', {}).get('fatigue', -100)
        
        # 오브젝트 상태 업데이트
        updated_state = await self._update_object_state(
            runtime_object_id,
            game_object_id,
            session_id,
            state="slept_in"
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
        
        object_name = object_state.get('object_name', '오브젝트')
        
        # TODO: TimeSystem 연동 (480분 = 8시간)
        # TODO: 피로도 감소 처리
        
        return ActionResult.success_result(
            f"{object_name}에서 잠을 잤습니다. {restore_result.message}",
            data={
                "state": "slept_in",
                "hp_restored": hp_restore,
                "mp_restored": mp_restore,
                "fatigue_reduced": fatigue_reduce
            }
        )
    
    async def handle_meditate(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에서 명상"""
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
        meditate_config = interactions.get('meditate', {})
        
        mp_restore = meditate_config.get('effects', {}).get('mp', 50)
        
        # 오브젝트 상태 업데이트
        updated_state = await self._update_object_state(
            runtime_object_id,
            game_object_id,
            session_id,
            state="meditated"
        )
        
        if not updated_state:
            return ActionResult.failure_result("오브젝트 상태를 업데이트할 수 없습니다.")
        
        # 엔티티 MP 회복
        restore_result = await self.entity_manager.restore_hp_mp(entity_id, mp=mp_restore)
        
        if not restore_result.success:
            return ActionResult.failure_result(restore_result.message)
        
        object_name = object_state.get('object_name', '오브젝트')
        
        return ActionResult.success_result(
            f"{object_name}에서 명상했습니다. {restore_result.message}",
            data={"state": "meditated", "mp_restored": mp_restore}
        )
    
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """기본 핸들러 (rest)"""
        return await self.handle_rest(entity_id, target_id, parameters)

