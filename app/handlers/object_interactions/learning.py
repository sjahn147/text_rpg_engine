"""
학습/정보 상호작용 핸들러 (read, study, write)
"""
from typing import Dict, Any, Optional
from app.handlers.object_interaction_base import ObjectInteractionHandlerBase
from app.handlers.action_result import ActionResult


class LearningInteractionHandler(ObjectInteractionHandlerBase):
    """학습/정보 상호작용 핸들러"""
    
    async def handle_read(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 읽기"""
        context = {
            "entity_id": entity_id,
            "target_id": target_id,
            "operation": "handle_read"
        }
        
        try:
            # 파라미터 검증
            param_check = self._validate_parameters(parameters, ["session_id"], "읽기")
            if param_check:
                return param_check
            
            session_id = parameters["session_id"]
            context["session_id"] = session_id
            
            self.logger.debug(f"읽기 시작: entity_id={entity_id}, target_id={target_id}, session_id={session_id}")
            
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
            read_config = interactions.get('read', {})
            
            # 읽기 내용
            content = read_config.get('content', object_state.get('object_description', ''))
            
            # EffectCarrier 적용
            effect_carrier_id = read_config.get('effect_carrier_id')
            if effect_carrier_id and self.effect_carrier_manager:
                try:
                    effect_result = await self.effect_carrier_manager.grant_effect_to_entity(
                        session_id=session_id,
                        entity_id=entity_id,
                        effect_id=effect_carrier_id,
                        source=f"read_object:{game_object_id}"
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
            time_cost = read_config.get('time_cost', 30)
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
                f"읽기 완료: entity_id={entity_id}, object_name={object_name}, "
                f"time_cost={time_cost}"
            )
            
            return ActionResult.success_result(
                f"{object_name}을(를) 읽었습니다.\n\n{content}",
                data={"content": content, "effect_carrier_id": effect_carrier_id, "time_cost": time_cost}
            )
        
        except Exception as e:
            return self._handle_error(e, context, "읽기 중 오류가 발생했습니다.")
    
    async def handle_study(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트 공부하기"""
        context = {
            "entity_id": entity_id,
            "target_id": target_id,
            "operation": "handle_study"
        }
        
        try:
            # 파라미터 검증
            param_check = self._validate_parameters(parameters, ["session_id"], "공부하기")
            if param_check:
                return param_check
            
            session_id = parameters["session_id"]
            context["session_id"] = session_id
            
            self.logger.debug(f"공부하기 시작: entity_id={entity_id}, target_id={target_id}, session_id={session_id}")
            
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
            study_config = interactions.get('study', {})
            
            # 공부 내용 (read보다 더 상세)
            content = study_config.get('content', object_state.get('object_description', ''))
            
            # EffectCarrier 적용 (공부는 효과를 더 많이 적용)
            effect_carrier_id = study_config.get('effect_carrier_id')
            if effect_carrier_id and self.effect_carrier_manager:
                try:
                    effect_result = await self.effect_carrier_manager.grant_effect_to_entity(
                        session_id=session_id,
                        entity_id=entity_id,
                        effect_id=effect_carrier_id,
                        source=f"study_object:{game_object_id}"
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
            
            # TimeSystem 연동 (공부는 read보다 더 많은 시간 소모)
            time_cost = study_config.get('time_cost', 120)  # 기본 2시간
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
                f"공부하기 완료: entity_id={entity_id}, object_name={object_name}, "
                f"time_cost={time_cost}"
            )
            
            return ActionResult.success_result(
                f"{object_name}을(를) 공부했습니다.\n\n{content}",
                data={"content": content, "effect_carrier_id": effect_carrier_id, "time_cost": time_cost}
            )
        
        except Exception as e:
            return self._handle_error(e, context, "공부하기 중 오류가 발생했습니다.")
    
    async def handle_write(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """오브젝트에 쓰기"""
        context = {
            "entity_id": entity_id,
            "target_id": target_id,
            "operation": "handle_write"
        }
        
        try:
            # 파라미터 검증
            param_check = self._validate_parameters(parameters, ["session_id", "content"], "쓰기")
            if param_check:
                return param_check
            
            session_id = parameters["session_id"]
            content = parameters["content"]
            context["session_id"] = session_id
            
            self.logger.debug(f"쓰기 시작: entity_id={entity_id}, target_id={target_id}, session_id={session_id}")
            
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
            
            # 오브젝트 상태 업데이트
            updated_state = await self._update_object_state(
                runtime_object_id,
                game_object_id,
                session_id,
                state="written",
                properties={"written_content": content}
            )
            
            if not updated_state:
                self.logger.error(
                    f"오브젝트 상태 업데이트 실패: runtime_object_id={runtime_object_id}, "
                    f"game_object_id={game_object_id}",
                    extra={"context": context}
                )
                return ActionResult.failure_result("오브젝트 상태를 업데이트할 수 없습니다.")
            
            object_name = object_state.get('object_name', '오브젝트')
            
            # TimeSystem 연동
            write_config = properties.get('interactions', {}).get('write', {})
            time_cost = write_config.get('time_cost', 15)
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
            
            # 아이템 생성 (필요시) - write_config에 result_item_id가 있으면 생성
            result_item_id = write_config.get('result_item_id')
            if result_item_id and self.inventory_manager:
                try:
                    await self.inventory_manager.add_item_to_inventory(
                        entity_id,
                        result_item_id,
                        quantity=1
                    )
                    self.logger.debug(f"아이템 생성 성공: result_item_id={result_item_id}")
                except Exception as e:
                    self.logger.warning(
                        f"아이템 생성 실패: {str(e)}",
                        exc_info=True,
                        extra={"result_item_id": result_item_id, "context": context}
                    )
                    # 아이템 생성 실패는 치명적이지 않으므로 계속 진행
            
            self.logger.info(
                f"쓰기 완료: entity_id={entity_id}, object_name={object_name}, "
                f"time_cost={time_cost}"
            )
            
            return ActionResult.success_result(
                f"{object_name}에 내용을 작성했습니다.",
                data={"state": "written", "content": content, "time_cost": time_cost}
            )
        
        except Exception as e:
            return self._handle_error(e, context, "쓰기 중 오류가 발생했습니다.")
    
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """기본 핸들러 (read)"""
        return await self.handle_read(entity_id, target_id, parameters)

