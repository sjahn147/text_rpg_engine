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
        context = {
            "entity_id": entity_id,
            "target_id": target_id,
            "operation": "handle_eat"
        }
        
        try:
            # 필수 매니저 검증
            manager_check = self._validate_required_managers(
                {"entity_manager": self.entity_manager},
                "음식 먹기"
            )
            if manager_check:
                return manager_check
            
            # 파라미터 검증
            param_check = self._validate_parameters(parameters, ["session_id"], "음식 먹기")
            if param_check:
                return param_check
            
            session_id = parameters["session_id"]
            context["session_id"] = session_id
            
            self.logger.debug(f"음식 먹기 시작: entity_id={entity_id}, target_id={target_id}, session_id={session_id}")
            
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
        
            # 오브젝트의 contents에서 아이템 ID 추출
            contents = object_state.get('current_state', {}).get('contents', [])
            if not contents:
                self.logger.warning(
                    f"오브젝트에 아이템이 없음: runtime_object_id={runtime_object_id}, "
                    f"game_object_id={game_object_id}"
                )
                return ActionResult.failure_result("오브젝트에 먹을 수 있는 아이템이 없습니다.")
            
            # 첫 번째 아이템 사용 (또는 parameters에서 지정)
            item_id = parameters.get("item_id") if parameters else contents[0]
            if item_id not in contents:
                self.logger.warning(
                    f"아이템이 오브젝트에 없음: item_id={item_id}, contents={contents}",
                    extra={"item_id": item_id, "contents": contents, "context": context}
                )
                return ActionResult.failure_result(f"오브젝트에 '{item_id}' 아이템이 없습니다.")
            
            context["item_id"] = item_id
            
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
                    self.logger.warning(
                        f"아이템 템플릿을 찾을 수 없음: item_id={item_id}",
                        extra={"item_id": item_id, "context": context}
                    )
                    return ActionResult.failure_result(f"아이템 템플릿을 찾을 수 없습니다: {item_id}")
            
            # 아이템 속성에서 효과 확인
            item_properties = item_template.get('item_properties', {})
            if isinstance(item_properties, str):
                import json
                try:
                    item_properties = json.loads(item_properties)
                except json.JSONDecodeError as e:
                    self.logger.error(
                        f"아이템 속성 JSON 파싱 실패: {str(e)}",
                        exc_info=True,
                        extra={"item_id": item_id, "item_properties": item_properties, "context": context}
                    )
                    return ActionResult.failure_result("아이템 속성을 읽을 수 없습니다.")
            
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
            
            # EffectCarrier 적용
            if effect_carrier_id and self.effect_carrier_manager:
                try:
                    effect_result = await self.effect_carrier_manager.grant_effect_to_entity(
                        session_id=session_id,
                        entity_id=entity_id,
                        effect_id=effect_carrier_id,
                        source=f"eat_from_object:{item_id}"
                    )
                    if not effect_result.success:
                        self.logger.warning(
                            f"Effect Carrier 적용 실패: {effect_result.message}",
                            extra={
                                "effect_carrier_id": effect_carrier_id,
                                "item_id": item_id,
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
            
            # TimeSystem 연동
            time_cost = item_properties.get('interactions', {}).get('eat', {}).get('time_cost', 5)
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
            
            item_name = item_template.get('item_name', item_id)
            object_name = object_state.get('object_name', '오브젝트')
            
            self.logger.info(
                f"음식 먹기 완료: entity_id={entity_id}, item_name={item_name}, "
                f"object_name={object_name}, hp_restored={hp_restore}, mp_restored={mp_restore}, "
                f"time_cost={time_cost}"
            )
            
            return ActionResult.success_result(
                f"{object_name}에서 {item_name}을(를) 먹었습니다. {restore_result.message}",
                data={
                    "item_id": item_id,
                    "hp_restored": hp_restore,
                    "mp_restored": mp_restore,
                    "effect_carrier_id": effect_carrier_id,
                    "time_cost": time_cost
                }
            )
        
        except Exception as e:
            return self._handle_error(e, context, "음식 먹기 중 오류가 발생했습니다.")
    
    async def handle_drink(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에서 마시기"""
        context = {
            "entity_id": entity_id,
            "target_id": target_id,
            "operation": "handle_drink"
        }
        
        try:
            # 필수 매니저 검증
            manager_check = self._validate_required_managers(
                {"entity_manager": self.entity_manager},
                "마시기"
            )
            if manager_check:
                return manager_check
            
            # 파라미터 검증
            param_check = self._validate_parameters(parameters, ["session_id"], "마시기")
            if param_check:
                return param_check
            
            session_id = parameters["session_id"]
            context["session_id"] = session_id
            
            self.logger.debug(f"마시기 시작: entity_id={entity_id}, target_id={target_id}, session_id={session_id}")
            
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
            
            # EffectCarrier 적용
            effect_carrier_id = drink_config.get('effect_carrier_id')
            if effect_carrier_id and self.effect_carrier_manager:
                try:
                    effect_result = await self.effect_carrier_manager.grant_effect_to_entity(
                        session_id=session_id,
                        entity_id=entity_id,
                        effect_id=effect_carrier_id,
                        source=f"drink_from_object:{game_object_id}"
                    )
                    if not effect_result.success:
                        self.logger.warning(
                            f"Effect Carrier 적용 실패: {effect_result.message}",
                            extra={
                                "effect_carrier_id": effect_carrier_id,
                                "game_object_id": game_object_id,
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
            
            object_name = object_state.get('object_name', '오브젝트')
            
            # TimeSystem 연동
            time_cost = drink_config.get('time_cost', 5)
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
                f"마시기 완료: entity_id={entity_id}, object_name={object_name}, "
                f"mp_restored={mp_restore}, time_cost={time_cost}"
            )
            
            return ActionResult.success_result(
                f"{object_name}을(를) 마셨습니다. {restore_result.message}",
                data={"state": "consumed", "mp_restored": mp_restore, "time_cost": time_cost}
            )
        
        except Exception as e:
            return self._handle_error(e, context, "마시기 중 오류가 발생했습니다.")
    
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

