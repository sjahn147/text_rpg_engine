"""
회복 상호작용 핸들러 (rest, sleep, meditate)
"""
from typing import Dict, Any, Optional
from app.handlers.object_interaction_base import ObjectInteractionHandlerBase
from app.handlers.action_result import ActionResult


class RecoveryInteractionHandler(ObjectInteractionHandlerBase):
    """회복 상호작용 핸들러"""
    
    async def handle_rest(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에서 휴식"""
        context = {
            "entity_id": entity_id,
            "target_id": target_id,
            "operation": "handle_rest"
        }
        
        try:
            # 필수 매니저 검증
            manager_check = self._validate_required_managers(
                {"entity_manager": self.entity_manager},
                "휴식"
            )
            if manager_check:
                return manager_check
            
            # 파라미터 검증
            param_check = self._validate_parameters(parameters, ["session_id"], "휴식")
            if param_check:
                return param_check
            
            session_id = parameters["session_id"]
            context["session_id"] = session_id
            
            self.logger.debug(f"휴식 시작: entity_id={entity_id}, target_id={target_id}, session_id={session_id}")
            
            runtime_object_id, game_object_id = await self._parse_object_id(target_id, session_id)
            context["runtime_object_id"] = runtime_object_id
            context["game_object_id"] = game_object_id
            
            if not game_object_id:
                self.logger.warning(f"오브젝트를 찾을 수 없음: target_id={target_id}, session_id={session_id}")
                return ActionResult.failure_result("오브젝트를 찾을 수 없습니다.")
            
            object_state = await self._get_object_state(runtime_object_id, game_object_id, session_id)
            
            if not object_state:
                self.logger.warning(
                    f"오브젝트 상태 조회 실패: runtime_object_id={runtime_object_id}, "
                    f"game_object_id={game_object_id}, session_id={session_id}"
                )
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
                self.logger.error(
                    f"오브젝트 상태 업데이트 실패: runtime_object_id={runtime_object_id}, "
                    f"game_object_id={game_object_id}",
                    extra={"context": context}
                )
                return ActionResult.failure_result("오브젝트 상태를 업데이트할 수 없습니다.")
            
            # 엔티티 HP/MP 회복
            restore_result = await self.entity_manager.restore_hp_mp(
                entity_id,
                hp=hp_restore,
                mp=mp_restore
            )
            
            if not restore_result.success:
                self.logger.warning(
                    f"HP/MP 회복 실패: {restore_result.message}",
                    extra={"hp_restore": hp_restore, "mp_restore": mp_restore, "context": context}
                )
                return ActionResult.failure_result(restore_result.message)
            
            object_name = object_state.get('object_name', '오브젝트')
            
            # TimeSystem 연동 (30분)
            time_cost = rest_config.get('time_cost', 30)
            if time_cost > 0:
                from app.systems.time_system import TimeSystem
                time_system = TimeSystem()
                try:
                    await time_system.advance_time(minutes=time_cost)
                    self.logger.debug(f"TimeSystem 연동 성공: {time_cost}분 진행")
                except Exception as e:
                    self.logger.warning(
                        f"TimeSystem 연동 실패: {str(e)}",
                        exc_info=True,
                        extra={"time_cost": time_cost, "context": context}
                    )
                    # TimeSystem 실패는 치명적이지 않으므로 계속 진행
            
            self.logger.info(
                f"휴식 완료: entity_id={entity_id}, object_name={object_name}, "
                f"hp_restored={hp_restore}, mp_restored={mp_restore}, time_cost={time_cost}"
            )
            
            return ActionResult.success_result(
                f"{object_name}에서 휴식했습니다. {restore_result.message}",
                data={
                    "state": "occupied",
                    "hp_restored": hp_restore,
                    "mp_restored": mp_restore,
                    "time_cost": time_cost
                }
            )
        
        except Exception as e:
            return self._handle_error(e, context, "휴식 중 오류가 발생했습니다.")
    
    async def handle_sleep(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에서 잠자기"""
        context = {
            "entity_id": entity_id,
            "target_id": target_id,
            "operation": "handle_sleep"
        }
        
        try:
            # 필수 매니저 검증
            manager_check = self._validate_required_managers(
                {"entity_manager": self.entity_manager},
                "잠자기"
            )
            if manager_check:
                return manager_check
            
            # 파라미터 검증
            param_check = self._validate_parameters(parameters, ["session_id"], "잠자기")
            if param_check:
                return param_check
            
            session_id = parameters["session_id"]
            context["session_id"] = session_id
            
            self.logger.debug(f"잠자기 시작: entity_id={entity_id}, target_id={target_id}, session_id={session_id}")
            
            runtime_object_id, game_object_id = await self._parse_object_id(target_id, session_id)
            context["runtime_object_id"] = runtime_object_id
            context["game_object_id"] = game_object_id
            
            if not game_object_id:
                self.logger.warning(f"오브젝트를 찾을 수 없음: target_id={target_id}, session_id={session_id}")
                return ActionResult.failure_result("오브젝트를 찾을 수 없습니다.")
            
            object_state = await self._get_object_state(runtime_object_id, game_object_id, session_id)
            
            if not object_state:
                self.logger.warning(
                    f"오브젝트 상태 조회 실패: runtime_object_id={runtime_object_id}, "
                    f"game_object_id={game_object_id}, session_id={session_id}"
                )
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
                self.logger.error(
                    f"오브젝트 상태 업데이트 실패: runtime_object_id={runtime_object_id}, "
                    f"game_object_id={game_object_id}",
                    extra={"context": context}
                )
                return ActionResult.failure_result("오브젝트 상태를 업데이트할 수 없습니다.")
            
            # 엔티티 HP/MP 회복
            restore_result = await self.entity_manager.restore_hp_mp(
                entity_id,
                hp=hp_restore,
                mp=mp_restore
            )
            
            if not restore_result.success:
                self.logger.warning(
                    f"HP/MP 회복 실패: {restore_result.message}",
                    extra={"hp_restore": hp_restore, "mp_restore": mp_restore, "context": context}
                )
                return ActionResult.failure_result(restore_result.message)
            
            object_name = object_state.get('object_name', '오브젝트')
            
            # TimeSystem 연동 (480분 = 8시간)
            time_cost = sleep_config.get('time_cost', 480)
            if time_cost > 0:
                from app.systems.time_system import TimeSystem
                time_system = TimeSystem()
                try:
                    await time_system.advance_time(minutes=time_cost)
                    self.logger.debug(f"TimeSystem 연동 성공: {time_cost}분 진행")
                except Exception as e:
                    self.logger.warning(
                        f"TimeSystem 연동 실패: {str(e)}",
                        exc_info=True,
                        extra={"time_cost": time_cost, "context": context}
                    )
                    # TimeSystem 실패는 치명적이지 않으므로 계속 진행
            
            # 피로도 감소 처리
            # Note: EntityManager에 피로도 관리 기능이 추가되면 여기서 처리
            # 현재는 effects에 fatigue 값이 있으면 로그만 남김
            if fatigue_reduce < 0:
                self.logger.info(
                    f"피로도 감소: {abs(fatigue_reduce)} (EntityManager 피로도 관리 기능 필요)",
                    extra={"fatigue_reduce": fatigue_reduce, "context": context}
                )
            
            self.logger.info(
                f"잠자기 완료: entity_id={entity_id}, object_name={object_name}, "
                f"hp_restored={hp_restore}, mp_restored={mp_restore}, "
                f"fatigue_reduced={fatigue_reduce}, time_cost={time_cost}"
            )
            
            return ActionResult.success_result(
                f"{object_name}에서 잠을 잤습니다. {restore_result.message}",
                data={
                    "state": "slept_in",
                    "hp_restored": hp_restore,
                    "mp_restored": mp_restore,
                    "fatigue_reduced": fatigue_reduce
                }
            )
        
        except Exception as e:
            return self._handle_error(e, context, "잠자기 중 오류가 발생했습니다.")
    
    async def handle_meditate(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에서 명상"""
        context = {
            "entity_id": entity_id,
            "target_id": target_id,
            "operation": "handle_meditate"
        }
        
        try:
            # 필수 매니저 검증
            manager_check = self._validate_required_managers(
                {"entity_manager": self.entity_manager},
                "명상"
            )
            if manager_check:
                return manager_check
            
            # 파라미터 검증
            param_check = self._validate_parameters(parameters, ["session_id"], "명상")
            if param_check:
                return param_check
            
            session_id = parameters["session_id"]
            context["session_id"] = session_id
            
            self.logger.debug(f"명상 시작: entity_id={entity_id}, target_id={target_id}, session_id={session_id}")
            
            runtime_object_id, game_object_id = await self._parse_object_id(target_id, session_id)
            context["runtime_object_id"] = runtime_object_id
            context["game_object_id"] = game_object_id
            
            if not game_object_id:
                self.logger.warning(f"오브젝트를 찾을 수 없음: target_id={target_id}, session_id={session_id}")
                return ActionResult.failure_result("오브젝트를 찾을 수 없습니다.")
            
            object_state = await self._get_object_state(runtime_object_id, game_object_id, session_id)
            
            if not object_state:
                self.logger.warning(
                    f"오브젝트 상태 조회 실패: runtime_object_id={runtime_object_id}, "
                    f"game_object_id={game_object_id}, session_id={session_id}"
                )
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
                self.logger.error(
                    f"오브젝트 상태 업데이트 실패: runtime_object_id={runtime_object_id}, "
                    f"game_object_id={game_object_id}",
                    extra={"context": context}
                )
                return ActionResult.failure_result("오브젝트 상태를 업데이트할 수 없습니다.")
            
            # 엔티티 MP 회복
            restore_result = await self.entity_manager.restore_hp_mp(entity_id, mp=mp_restore)
            
            if not restore_result.success:
                self.logger.warning(
                    f"MP 회복 실패: {restore_result.message}",
                    extra={"mp_restore": mp_restore, "context": context}
                )
                return ActionResult.failure_result(restore_result.message)
            
            object_name = object_state.get('object_name', '오브젝트')
            
            # EffectCarrier 적용
            effect_carrier_id = meditate_config.get('effect_carrier_id')
            if effect_carrier_id and self.effect_carrier_manager:
                try:
                    effect_result = await self.effect_carrier_manager.grant_effect_to_entity(
                        session_id=session_id,
                        entity_id=entity_id,
                        effect_id=effect_carrier_id,
                        source=f"meditate_object:{game_object_id}"
                    )
                    if not effect_result.success:
                        self.logger.warning(
                            f"Effect Carrier 적용 실패: {effect_result.message}",
                            extra={
                                "effect_carrier_id": effect_carrier_id,
                                "entity_id": entity_id,
                                "context": context
                            }
                        )
                    else:
                        self.logger.debug(
                            f"Effect Carrier 적용 성공: effect_carrier_id={effect_carrier_id}",
                            extra={"effect_carrier_id": effect_carrier_id, "context": context}
                        )
                except Exception as e:
                    self.logger.warning(
                        f"Effect Carrier 적용 중 예외 발생: {str(e)}",
                        exc_info=True,
                        extra={"effect_carrier_id": effect_carrier_id, "context": context}
                    )
                    # EffectCarrier 실패는 치명적이지 않으므로 계속 진행
            
            self.logger.info(
                f"명상 완료: entity_id={entity_id}, object_name={object_name}, "
                f"mp_restored={mp_restore}, effect_carrier_id={effect_carrier_id}"
            )
            
            return ActionResult.success_result(
                f"{object_name}에서 명상했습니다. {restore_result.message}",
                data={
                    "state": "meditated",
                    "mp_restored": mp_restore,
                    "effect_carrier_id": effect_carrier_id
                }
            )
        
        except Exception as e:
            return self._handle_error(e, context, "명상 중 오류가 발생했습니다.")
    
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """기본 핸들러 (rest)"""
        return await self.handle_rest(entity_id, target_id, parameters)

