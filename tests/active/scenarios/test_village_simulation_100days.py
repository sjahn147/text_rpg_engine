"""
100일 마을 시뮬레이션 테스트

목적:
- 100일간 마을 시뮬레이션 실행
- NPC 일과 루틴 검증 (기상, 활동, 귀가, 수면)
- 데이터 누적 및 통계 검증
- 최종 MVP 검증
"""
import pytest
import pytest_asyncio
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
from common.utils.logger import logger


@pytest.mark.asyncio
class TestVillageSimulation100Days:
    """100일 마을 시뮬레이션 테스트"""
    
    async def test_village_simulation_100days(self, db_with_templates, entity_manager, cell_manager, dialogue_manager, action_handler, test_session):
        """
        시나리오: 100일 마을 시뮬레이션
        1. 마을 생성 (10x10 셀)
        2. NPC 3명 배치
        3. 일과 루틴 실행 (TimeSystem)
        4. 100일 반복
        5. 데이터 누적 검증
        """
        session_id = test_session['session_id']
        
        logger.info(f"[VILLAGE] Starting 100-day village simulation")
        logger.info(f"[VILLAGE] Session ID: {session_id}")
        
        # 1. 마을 생성 (10x10 셀)
        village_cells = await self._create_village_grid(cell_manager, session_id, 10, 10)
        logger.info(f"[VILLAGE] Created {len(village_cells)} village cells")
        
        # 셀이 생성되지 않았으면 테스트 실패
        assert len(village_cells) > 0, "Failed to create village cells. Check if CELL_VILLAGE_SQUARE_001 template exists in database."
        
        # 2. NPC 3명 배치
        npcs = await self._create_village_npcs(entity_manager, session_id, village_cells)
        logger.info(f"[VILLAGE] Created {len(npcs)} NPCs")
        
        # 3. 시뮬레이션 통계 초기화
        simulation_stats = {
            "total_days": 0,
            "total_dialogues": 0,
            "total_actions": 0,
            "npc_interactions": {},
            "daily_activities": [],
            "village_events": []
        }
        
        # 4. 100일 시뮬레이션 실행
        for day in range(1, 101):
            logger.info(f"[VILLAGE] Day {day}/100 - Starting daily routine")
            
            daily_stats = await self._simulate_daily_routine(
                day, npcs, village_cells, 
                entity_manager, cell_manager, 
                dialogue_manager, action_handler, 
                session_id
            )
            
            # 통계 누적
            simulation_stats["total_days"] = day
            simulation_stats["total_dialogues"] += daily_stats["dialogues"]
            simulation_stats["total_actions"] += daily_stats["actions"]
            simulation_stats["daily_activities"].append(daily_stats)
            
            # NPC별 상호작용 통계
            for npc_id, interactions in daily_stats["npc_interactions"].items():
                if npc_id not in simulation_stats["npc_interactions"]:
                    simulation_stats["npc_interactions"][npc_id] = 0
                simulation_stats["npc_interactions"][npc_id] += interactions
            
            # 진행 상황 로깅 (10일마다)
            if day % 10 == 0:
                logger.info(f"[VILLAGE] Day {day} completed - Dialogues: {simulation_stats['total_dialogues']}, Actions: {simulation_stats['total_actions']}")
        
        # 5. 최종 통계 검증
        await self._validate_simulation_results(simulation_stats)
        
        logger.info(f"[VILLAGE] 100-day simulation completed successfully!")
        logger.info(f"[VILLAGE] Final stats: {simulation_stats['total_dialogues']} dialogues, {simulation_stats['total_actions']} actions")
    
    async def _create_village_grid(self, cell_manager, session_id: str, width: int, height: int) -> List[str]:
        """마을 격자 생성 (10x10 셀)"""
        cells = []
        
        for x in range(width):
            for y in range(height):
                # 셀 생성 (실제 존재하는 템플릿 사용 - 다른 테스트에서 사용하는 CELL_SHOP_INTERIOR_001 사용)
                result = await cell_manager.create_cell(
                    static_cell_id="CELL_SHOP_INTERIOR_001",
                    session_id=session_id
                )
                
                if result.success and result.cell:
                    cells.append(result.cell.cell_id)
                    logger.debug(f"[VILLAGE] Created cell at ({x}, {y}): {result.cell.cell_id}")
                else:
                    logger.warning(f"[VILLAGE] Failed to create cell at ({x}, {y}): {result.message if result else 'Unknown error'}")
        
        return cells
    
    async def _create_village_npcs(self, entity_manager, session_id: str, village_cells: List[str]) -> List[Dict[str, Any]]:
        """마을 NPC 3명 생성"""
        npc_templates = ["NPC_VILLAGER_001", "NPC_MERCHANT_001", "NPC_GOBLIN_001"]
        npcs = []
        
        # village_cells가 비어있으면 빈 리스트 반환
        if not village_cells:
            logger.warning("[VILLAGE] No village cells available, cannot create NPCs")
            return npcs
        
        for i, template in enumerate(npc_templates):
            # NPC 생성
            result = await entity_manager.create_entity(
                static_entity_id=template,
                session_id=session_id,
                custom_position={"x": float(i * 2), "y": float(i * 2)}
            )
            
            if result.status == "success":
                npc_data = {
                    "entity_id": result.entity_id,
                    "name": result.entity_data.name,
                    "template": template,
                    "current_cell": village_cells[i % len(village_cells)],
                    "daily_routine": self._get_npc_routine(template)
                }
                npcs.append(npc_data)
            else:
                logger.warning(f"[VILLAGE] Failed to create NPC {template}: {result.message if hasattr(result, 'message') else 'Unknown error'}")
        
        return npcs
    
    def _get_npc_routine(self, template: str) -> Dict[str, Any]:
        """NPC별 일과 루틴 정의"""
        routines = {
            "NPC_VILLAGER_001": {
                "morning": "기상 및 아침 준비",
                "day": "농사일 및 마을 돌아다니기",
                "evening": "가족과 함께 저녁",
                "night": "수면"
            },
            "NPC_MERCHANT_001": {
                "morning": "상점 준비",
                "day": "상점 운영 및 거래",
                "evening": "장부 정리",
                "night": "수면"
            },
            "NPC_GOBLIN_001": {
                "morning": "기상 및 음식 찾기",
                "day": "마을 주변 배회",
                "evening": "은신처로 귀가",
                "night": "수면"
            }
        }
        return routines.get(template, routines["NPC_VILLAGER_001"])
    
    async def _simulate_daily_routine(self, day: int, npcs: List[Dict], village_cells: List[str], 
                                    entity_manager, cell_manager, dialogue_manager, action_handler, 
                                    session_id: str) -> Dict[str, Any]:
        """하루 일과 루틴 시뮬레이션"""
        daily_stats = {
            "day": day,
            "dialogues": 0,
            "actions": 0,
            "npc_interactions": {},
            "activities": []
        }
        
        # 아침 (06:00-12:00)
        morning_activities = await self._simulate_time_period(
            "morning", npcs, village_cells, 
            entity_manager, cell_manager, dialogue_manager, action_handler, 
            session_id
        )
        daily_stats["dialogues"] += morning_activities["dialogues"]
        daily_stats["actions"] += morning_activities["actions"]
        daily_stats["activities"].extend(morning_activities["activities"])
        
        # 낮 (12:00-18:00)
        day_activities = await self._simulate_time_period(
            "day", npcs, village_cells, 
            entity_manager, cell_manager, dialogue_manager, action_handler, 
            session_id
        )
        daily_stats["dialogues"] += day_activities["dialogues"]
        daily_stats["actions"] += day_activities["actions"]
        daily_stats["activities"].extend(day_activities["activities"])
        
        # 저녁 (18:00-22:00)
        evening_activities = await self._simulate_time_period(
            "evening", npcs, village_cells, 
            entity_manager, cell_manager, dialogue_manager, action_handler, 
            session_id
        )
        daily_stats["dialogues"] += evening_activities["dialogues"]
        daily_stats["actions"] += evening_activities["actions"]
        daily_stats["activities"].extend(evening_activities["activities"])
        
        # 밤 (22:00-06:00)
        night_activities = await self._simulate_time_period(
            "night", npcs, village_cells, 
            entity_manager, cell_manager, dialogue_manager, action_handler, 
            session_id
        )
        daily_stats["dialogues"] += night_activities["dialogues"]
        daily_stats["actions"] += night_activities["actions"]
        daily_stats["activities"].extend(night_activities["activities"])
        
        # NPC별 상호작용 통계
        for npc in npcs:
            npc_id = npc["entity_id"]
            daily_stats["npc_interactions"][npc_id] = (
                morning_activities.get("npc_interactions", {}).get(npc_id, 0) +
                day_activities.get("npc_interactions", {}).get(npc_id, 0) +
                evening_activities.get("npc_interactions", {}).get(npc_id, 0) +
                night_activities.get("npc_interactions", {}).get(npc_id, 0)
            )
        
        return daily_stats
    
    async def _simulate_time_period(self, period: str, npcs: List[Dict], village_cells: List[str],
                                  entity_manager, cell_manager, dialogue_manager, action_handler,
                                  session_id: str) -> Dict[str, Any]:
        """특정 시간대 시뮬레이션"""
        period_stats = {
            "period": period,
            "dialogues": 0,
            "actions": 0,
            "activities": [],
            "npc_interactions": {}
        }
        
        for npc in npcs:
            npc_id = npc["entity_id"]
            routine = npc["daily_routine"][period]
            
            # NPC 활동 시뮬레이션
            activity = await self._simulate_npc_activity(
                npc, period, routine, village_cells,
                entity_manager, cell_manager, dialogue_manager, action_handler,
                session_id
            )
            
            period_stats["dialogues"] += activity["dialogues"]
            period_stats["actions"] += activity["actions"]
            period_stats["activities"].append(activity)
            period_stats["npc_interactions"][npc_id] = activity["interactions"]
        
        return period_stats
    
    async def _simulate_npc_activity(self, npc: Dict, period: str, routine: str, village_cells: List[str],
                                    entity_manager, cell_manager, dialogue_manager, action_handler,
                                    session_id: str) -> Dict[str, Any]:
        """NPC 개별 활동 시뮬레이션"""
        activity = {
            "npc_id": npc["entity_id"],
            "npc_name": npc["name"],
            "period": period,
            "routine": routine,
            "dialogues": 0,
            "actions": 0,
            "interactions": 0,
            "activities": []
        }
        
        # 랜덤 활동 결정 (간단한 AI)
        import random
        
        # 30% 확률로 대화 시도
        if random.random() < 0.3:
            dialogue_result = await self._attempt_dialogue(npc, dialogue_manager, session_id)
            if dialogue_result:
                activity["dialogues"] += 1
                activity["interactions"] += 1
                activity["activities"].append(f"대화: {dialogue_result}")
        
        # 50% 확률로 이동 시도
        if random.random() < 0.5:
            move_result = await self._attempt_movement(npc, village_cells, cell_manager, session_id)
            if move_result:
                activity["actions"] += 1
                activity["activities"].append(f"이동: {move_result}")
        
        # 20% 확률로 기타 행동
        if random.random() < 0.2:
            other_action = await self._attempt_other_action(npc, action_handler, session_id)
            if other_action:
                activity["actions"] += 1
                activity["activities"].append(f"기타 행동: {other_action}")
        
        return activity
    
    async def _attempt_dialogue(self, npc: Dict, dialogue_manager, session_id: str) -> str:
        """대화 시도"""
        try:
            # 간단한 대화 시뮬레이션
            start_result = await dialogue_manager.start_dialogue(
                player_id=npc["entity_id"],  # 자기 자신과 대화 (시뮬레이션)
                npc_id=npc["entity_id"],
                session_id=session_id
            )
            
            if start_result.success:
                # 대화 계속
                continue_result = await dialogue_manager.continue_dialogue(
                    player_id=npc["entity_id"],
                    npc_id=npc["entity_id"],
                    session_id=session_id,
                    topic="greeting"
                )
                
                if continue_result.success:
                    # 대화 종료
                    end_result = await dialogue_manager.end_dialogue(
                        player_id=npc["entity_id"],
                        npc_id=npc["entity_id"]
                    )
                    
                    if end_result.success:
                        return f"{npc['name']}이(가) 대화를 나눴습니다"
            
            return None
        except Exception as e:
            logger.warning(f"Dialogue attempt failed for {npc['name']}: {str(e)}")
            return None
    
    async def _attempt_movement(self, npc: Dict, village_cells: List[str], cell_manager, session_id: str) -> str:
        """이동 시도"""
        try:
            # 랜덤 셀 선택
            import random
            target_cell = random.choice(village_cells)
            
            # 셀 간 이동 시뮬레이션
            move_result = await cell_manager.move_entity_between_cells(
                entity_id=npc["entity_id"],
                from_cell_id=npc["current_cell"],
                to_cell_id=target_cell
            )
            
            if move_result.success:
                npc["current_cell"] = target_cell
                return f"{npc['name']}이(가) {target_cell}로 이동했습니다"
            
            return None
        except Exception as e:
            logger.warning(f"Movement attempt failed for {npc['name']}: {str(e)}")
            return None
    
    async def _attempt_other_action(self, npc: Dict, action_handler, session_id: str) -> str:
        """기타 행동 시도"""
        try:
            # 간단한 행동 시뮬레이션
            actions = ["investigate", "wait", "use_item"]
            import random
            action = random.choice(actions)
            
            if action == "investigate":
                result = await action_handler.handle_investigate(
                    entity_id=npc["entity_id"],
                    parameters={"cell_id": npc["current_cell"]}
                )
            elif action == "wait":
                result = await action_handler.handle_wait(
                    entity_id=npc["entity_id"],
                    parameters={"hours": 1}
                )
            elif action == "use_item":
                result = await action_handler.handle_use_item(
                    entity_id=npc["entity_id"],
                    parameters={"item_id": "ITEM_POTION_HEAL_001"}
                )
            
            if result and result.success:
                return f"{npc['name']}이(가) {action} 행동을 수행했습니다"
            
            return None
        except Exception as e:
            logger.warning(f"Other action attempt failed for {npc['name']}: {str(e)}")
            return None
    
    async def _validate_simulation_results(self, stats: Dict[str, Any]) -> None:
        """시뮬레이션 결과 검증"""
        logger.info(f"[VILLAGE] Validating simulation results...")
        
        # 기본 통계 검증
        assert stats["total_days"] == 100, f"Expected 100 days, got {stats['total_days']}"
        assert stats["total_dialogues"] > 0, "No dialogues occurred during simulation"
        assert stats["total_actions"] > 0, "No actions occurred during simulation"
        
        # NPC 상호작용 검증
        assert len(stats["npc_interactions"]) > 0, "No NPC interactions recorded"
        
        # 일일 활동 검증
        assert len(stats["daily_activities"]) == 100, f"Expected 100 daily activities, got {len(stats['daily_activities'])}"
        
        # 최소 활동량 검증
        min_dialogues = 50  # 100일 중 최소 50번의 대화
        min_actions = 100   # 100일 중 최소 100번의 행동
        
        assert stats["total_dialogues"] >= min_dialogues, f"Expected at least {min_dialogues} dialogues, got {stats['total_dialogues']}"
        assert stats["total_actions"] >= min_actions, f"Expected at least {min_actions} actions, got {stats['total_actions']}"
        
        logger.info(f"[VILLAGE] Simulation validation passed!")
        logger.info(f"[VILLAGE] Final statistics:")
        logger.info(f"[VILLAGE] - Total days: {stats['total_days']}")
        logger.info(f"[VILLAGE] - Total dialogues: {stats['total_dialogues']}")
        logger.info(f"[VILLAGE] - Total actions: {stats['total_actions']}")
        logger.info(f"[VILLAGE] - NPC interactions: {len(stats['npc_interactions'])}")
        logger.info(f"[VILLAGE] - Daily activities: {len(stats['daily_activities'])}")
