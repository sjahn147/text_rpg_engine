"""
가상 마을 시뮬레이션 통합 테스트
실제 데이터베이스와 연동하여 마을 시뮬레이션을 테스트
"""

import pytest
import pytest_asyncio
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

from app.entity.entity_manager import EntityManager, EntityType
from app.world.cell_manager import CellManager, CellType
from app.interaction.action_handler import ActionHandler
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from common.utils.logger import logger

class TimeSystem:
    """시간 시스템 테스트용"""
    
    def __init__(self, time_speed: int = 1):
        self.current_time = 6  # 06:00 시작
        self.day = 1
        self.time_speed = time_speed
        self.is_running = False
    
    async def start(self):
        """시간 시스템 시작"""
        self.is_running = True
        while self.is_running:
            await self.tick()
            await asyncio.sleep(0.1 / self.time_speed)
    
    async def stop(self):
        """시간 시스템 중지"""
        self.is_running = False
    
    async def tick(self):
        """시간 틱 (1시간씩 진행)"""
        self.current_time += 1
        if self.current_time >= 24:
            self.current_time = 0
            self.day += 1
    
    def get_time_period(self) -> str:
        """현재 시간대 반환"""
        if 6 <= self.current_time < 8:
            return "dawn"
        elif 8 <= self.current_time < 12:
            return "morning"
        elif 12 <= self.current_time < 14:
            return "lunch"
        elif 14 <= self.current_time < 18:
            return "afternoon"
        elif 18 <= self.current_time < 20:
            return "evening"
        elif 20 <= self.current_time < 22:
            return "night"
        else:
            return "late_night"
    
    def get_time_string(self) -> str:
        """현재 시간을 문자열로 반환"""
        hour = self.current_time
        minute = 0
        return f"{hour:02d}:{minute:02d}"

class EntityBehavior:
    """엔티티 행동 테스트용"""
    
    def __init__(self, entity_id: str, entity_name: str, entity_type: EntityType,
                 current_cell_id: str, entity_manager: EntityManager,
                 cell_manager: CellManager, action_handler: ActionHandler):
        self.entity_id = entity_id
        self.entity_name = entity_name
        self.entity_type = entity_type
        self.current_cell_id = current_cell_id
        self.entity_manager = entity_manager
        self.cell_manager = cell_manager
        self.action_handler = action_handler
        self.logger = logger
        
        # 엔티티 상태
        self.is_awake = True
        self.energy = 100
        self.mood = 50
        
        # 엔티티별 행동 스케줄
        self.schedule = self._get_entity_schedule()
    
    def _get_entity_schedule(self) -> Dict[str, List[str]]:
        """엔티티별 행동 스케줄 반환"""
        if self.entity_name == "상인 토마스":
            return {
                "dawn": ["wake_up", "move"],
                "morning": ["work", "trade"],
                "lunch": ["eat", "talk"],
                "afternoon": ["work", "trade"],
                "evening": ["move", "rest"],
                "night": ["talk", "eat"],
                "late_night": ["sleep"]
            }
        elif self.entity_name == "농부 존":
            return {
                "dawn": ["wake_up", "move"],
                "morning": ["work", "work"],
                "lunch": ["eat", "talk"],
                "afternoon": ["work", "work"],
                "evening": ["move", "rest"],
                "night": ["talk", "eat"],
                "late_night": ["sleep"]
            }
        else:
            # 기본 스케줄
            return {
                "dawn": ["wake_up"],
                "morning": ["work"],
                "lunch": ["eat"],
                "afternoon": ["work"],
                "evening": ["rest"],
                "night": ["talk"],
                "late_night": ["sleep"]
            }
    
    async def execute_actions_for_time_period(self, time_period: str) -> List[Dict[str, any]]:
        """특정 시간대의 행동들을 실행"""
        actions = self.schedule.get(time_period, [])
        results = []
        
        for action_type in actions:
            try:
                result = await self._execute_action(action_type)
                results.append({
                    "entity_id": self.entity_id,
                    "entity_name": self.entity_name,
                    "action_type": action_type,
                    "success": result.get("success", False),
                    "message": result.get("message", ""),
                    "timestamp": datetime.now()
                })
                
                await asyncio.sleep(0.01)  # 행동 간 잠시 대기
                
            except Exception as e:
                self.logger.error(f"Entity {self.entity_name} action {action_type} failed: {str(e)}")
                results.append({
                    "entity_id": self.entity_id,
                    "entity_name": self.entity_name,
                    "action_type": action_type,
                    "success": False,
                    "message": f"Action failed: {str(e)}",
                    "timestamp": datetime.now()
                })
        
        return results
    
    async def _execute_action(self, action_type: str) -> Dict[str, any]:
        """개별 행동 실행"""
        if action_type == "wake_up":
            self.is_awake = True
            self.energy = min(100, self.energy + 20)
            return {"success": True, "message": f"{self.entity_name}이(가) 일어났습니다."}
        elif action_type == "work":
            self.energy = max(0, self.energy - 10)
            self.mood = min(100, self.mood + 5)
            return {"success": True, "message": f"{self.entity_name}이(가) 일하고 있습니다."}
        elif action_type == "eat":
            self.energy = min(100, self.energy + 30)
            self.mood = min(100, self.mood + 10)
            return {"success": True, "message": f"{self.entity_name}이(가) 식사하고 있습니다."}
        elif action_type == "sleep":
            self.is_awake = False
            self.energy = min(100, self.energy + 40)
            return {"success": True, "message": f"{self.entity_name}이(가) 잠들었습니다."}
        else:
            return {"success": True, "message": f"{self.entity_name}이(가) {action_type}하고 있습니다."}
    
    def get_status(self) -> Dict[str, any]:
        """엔티티 현재 상태 반환"""
        return {
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "is_awake": self.is_awake,
            "energy": self.energy,
            "mood": self.mood,
            "current_cell_id": self.current_cell_id
        }

class VillageSimulationTest:
    """가상 마을 시뮬레이션 테스트 클래스"""
    
    def __init__(self):
        self.logger = logger
        
        self.db = DatabaseConnection()
        self.game_data_repo = GameDataRepository(db_connection)
        self.runtime_data_repo = RuntimeDataRepository(db_connection)
        self.reference_layer_repo = ReferenceLayerRepository(db_connection)
        
        # Manager 초기화
        self.entity_manager = EntityManager(self.db, self.game_data_repo, self.runtime_data_repo, self.reference_layer_repo)
        self.cell_manager = CellManager(self.db, self.game_data_repo, self.runtime_data_repo, self.reference_layer_repo, self.entity_manager)
        self.action_handler = ActionHandler(self.db, self.entity_manager, self.cell_manager)
        
        # 시간 시스템
        self.time_system = TimeSystem(time_speed=10)  # 10배속
        
        # 엔티티 행동 시스템
        self.entity_behaviors: Dict[str, EntityBehavior] = {}
        
        # 시뮬레이션 메트릭스
        self.metrics = {
            "total_actions": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "interactions": 0,
            "errors": [],
            "execution_time": 0,
            "simulation_days": 0
        }
    
    async def initialize_database(self):
        """데이터베이스 연결 초기화"""
        try:
            await self.db.pool
            self.logger.info("데이터베이스 연결 초기화 완료")
        except Exception as e:
            self.logger.error(f"데이터베이스 연결 초기화 실패: {str(e)}")
            raise
    
    async def initialize_village(self):
        """마을 초기화 - 엔티티와 셀 생성"""
        await self.initialize_database()
        
        self.logger.info("가상 마을 초기화 시작...")
        
        # 엔티티 생성
        entities = [
            {"name": "상인 토마스", "type": EntityType.NPC, "cell_id": "CELL_SHOP_WEAPON_001"},
            {"name": "농부 존", "type": EntityType.NPC, "cell_id": "CELL_FARMER_HOUSE_001"},
            {"name": "여관주인 마리아", "type": EntityType.NPC, "cell_id": "CELL_VILLAGE_CENTER_001"},
            {"name": "수호병 알렉스", "type": EntityType.NPC, "cell_id": "CELL_VILLAGE_CENTER_001"},
            {"name": "여행자 엘라", "type": EntityType.NPC, "cell_id": "CELL_VILLAGE_FOUNTAIN_001"}
        ]
        
        for entity_data in entities:
            entity_result = await self.entity_manager.create_entity(
                name=entity_data["name"],
                entity_type=entity_data["type"],
                properties={"energy": 100, "mood": 50, "is_awake": True}
            )
            
            if entity_result.success:
                self.entity_behaviors[entity_result.entity.entity_id] = EntityBehavior(
                    entity_id=entity_result.entity.entity_id,
                    entity_name=entity_data["name"],
                    entity_type=entity_data["type"],
                    current_cell_id=entity_data["cell_id"],
                    entity_manager=self.entity_manager,
                    cell_manager=self.cell_manager,
                    action_handler=self.action_handler
                )
                self.logger.info(f"엔티티 생성 완료: {entity_data['name']}")
            else:
                self.logger.error(f"엔티티 생성 실패: {entity_data['name']}")
        
        self.logger.info(f"가상 마을 초기화 완료! {len(self.entity_behaviors)}명의 엔티티 생성")
    
    async def run_simulation(self, days: int = 1):
        """시뮬레이션 실행"""
        self.logger.info(f"가상 마을 시뮬레이션 시작! {days}일간 실행")
        start_time = datetime.now()
        
        try:
            time_task = asyncio.create_task(self.time_system.start())
            
            for day in range(1, days + 1):
                self.logger.info(f"Day {day} 시작")
                await self._simulate_day(day)
                self.metrics["simulation_days"] = day
            
            await self.time_system.stop()
            time_task.cancel()
            
        except Exception as e:
            self.logger.error(f"시뮬레이션 실행 중 오류: {str(e)}")
            self.metrics["errors"].append(str(e))
        
        finally:
            end_time = datetime.now()
            self.metrics["execution_time"] = (end_time - start_time).total_seconds()
            await self._print_simulation_results()
    
    async def _simulate_day(self, day: int):
        """하루 시뮬레이션"""
        for hour in range(24):
            current_time_period = self.time_system.get_time_period()
            
            for entity_id, behavior in self.entity_behaviors.items():
                try:
                    results = await behavior.execute_actions_for_time_period(current_time_period)
                    
                    for result in results:
                        self.metrics["total_actions"] += 1
                        if result["success"]:
                            self.metrics["successful_actions"] += 1
                        else:
                            self.metrics["failed_actions"] += 1
                            
                        self.logger.info(f"{self.time_system.get_time_string()} | {result['entity_name']} | {result['action_type']} | {result['message']}")
                
                except Exception as e:
                    self.logger.error(f"엔티티 {entity_id} 행동 실행 중 오류: {str(e)}")
                    self.metrics["errors"].append(f"Entity {entity_id}: {str(e)}")
            
            await asyncio.sleep(0.01)  # 시뮬레이션 속도 조절
    
    async def _print_simulation_results(self):
        """시뮬레이션 결과 출력"""
        self.logger.info("시뮬레이션 결과:")
        self.logger.info(f"  시뮬레이션 일수: {self.metrics['simulation_days']}일")
        self.logger.info(f"  총 행동 수: {self.metrics['total_actions']}")
        self.logger.info(f"  성공한 행동: {self.metrics['successful_actions']}")
        self.logger.info(f"  실패한 행동: {self.metrics['failed_actions']}")
        self.logger.info(f"  상호작용 수: {self.metrics['interactions']}")
        self.logger.info(f"  실행 시간: {self.metrics['execution_time']:.2f}초")
        
        if self.metrics["errors"]:
            self.logger.info(f"  오류 수: {len(self.metrics['errors'])}")
            for error in self.metrics["errors"][:5]:
                self.logger.info(f"    - {error}")
        
        if self.metrics["total_actions"] > 0:
            success_rate = (self.metrics["successful_actions"] / self.metrics["total_actions"]) * 100
            self.logger.info(f"  성공률: {success_rate:.1f}%")
    
    def get_entity_status(self) -> Dict[str, any]:
        """모든 엔티티 상태 반환"""
        status = {}
        for entity_id, behavior in self.entity_behaviors.items():
            status[entity_id] = behavior.get_status()
        return status

class TestVillageSimulationIntegration:
    """가상 마을 시뮬레이션 통합 테스트"""
    
    @pytest_asyncio.fixture
    async def simulation(self):
        """시뮬레이션 인스턴스 생성"""
        sim = VillageSimulationTest()
        await sim.initialize_village()
        return sim
    
    @pytest.mark.asyncio
    async def test_village_initialization(self, simulation):
        """마을 초기화 테스트"""
        assert len(simulation.entity_behaviors) == 5
        assert "상인 토마스" in [b.entity_name for b in simulation.entity_behaviors.values()]
        assert "농부 존" in [b.entity_name for b in simulation.entity_behaviors.values()]
        assert "여관주인 마리아" in [b.entity_name for b in simulation.entity_behaviors.values()]
        assert "수호병 알렉스" in [b.entity_name for b in simulation.entity_behaviors.values()]
        assert "여행자 엘라" in [b.entity_name for b in simulation.entity_behaviors.values()]
    
    @pytest.mark.asyncio
    async def test_time_system(self, simulation):
        """시간 시스템 테스트"""
        assert simulation.time_system.current_time == 6
        assert simulation.time_system.day == 1
        
        # 시간 진행 테스트
        await simulation.time_system.tick()
        assert simulation.time_system.current_time == 7
        
        # 시간대 테스트
        assert simulation.time_system.get_time_period() == "dawn"
        simulation.time_system.current_time = 10
        assert simulation.time_system.get_time_period() == "morning"
    
    @pytest.mark.asyncio
    async def test_entity_behavior_schedule(self, simulation):
        """엔티티 행동 스케줄 테스트"""
        merchant_behavior = None
        for behavior in simulation.entity_behaviors.values():
            if behavior.entity_name == "상인 토마스":
                merchant_behavior = behavior
                break
        
        assert merchant_behavior is not None
        assert "wake_up" in merchant_behavior.schedule["dawn"]
        assert "work" in merchant_behavior.schedule["morning"]
        assert "sleep" in merchant_behavior.schedule["late_night"]
    
    @pytest.mark.asyncio
    async def test_entity_action_execution(self, simulation):
        """엔티티 행동 실행 테스트"""
        behavior = list(simulation.entity_behaviors.values())[0]
        
        # 일어나기 행동 테스트
        result = await behavior._execute_action("wake_up")
        assert result["success"] == True
        assert behavior.is_awake == True
        assert behavior.energy == 100
        
        # 일하기 행동 테스트
        result = await behavior._execute_action("work")
        assert result["success"] == True
        assert behavior.energy == 90  # 10 감소
        assert behavior.mood == 55  # 5 증가
    
    @pytest.mark.asyncio
    async def test_simulation_metrics(self, simulation):
        """시뮬레이션 메트릭스 테스트"""
        assert simulation.metrics["total_actions"] == 0
        assert simulation.metrics["successful_actions"] == 0
        assert simulation.metrics["failed_actions"] == 0
        assert simulation.metrics["simulation_days"] == 0
        
        # 메트릭스 업데이트 시뮬레이션
        simulation.metrics["total_actions"] = 100
        simulation.metrics["successful_actions"] = 95
        simulation.metrics["failed_actions"] = 5
        simulation.metrics["simulation_days"] = 1
        
        assert simulation.metrics["total_actions"] == 100
        assert simulation.metrics["successful_actions"] == 95
        assert simulation.metrics["failed_actions"] == 5
        assert simulation.metrics["simulation_days"] == 1
    
    @pytest.mark.asyncio
    async def test_one_day_simulation(self, simulation):
        """1일 시뮬레이션 테스트"""
        await simulation.run_simulation(days=1)
        
        # 시뮬레이션 완료 확인
        assert simulation.metrics["simulation_days"] == 1
        assert simulation.metrics["total_actions"] > 0
        assert simulation.metrics["execution_time"] > 0
        
        # 엔티티 상태 확인
        entity_status = simulation.get_entity_status()
        assert len(entity_status) == 5
        
        for entity_id, status in entity_status.items():
            assert "entity_name" in status
            assert "energy" in status
            assert "mood" in status
            assert "is_awake" in status
    
    @pytest.mark.asyncio
    async def test_entity_status_tracking(self, simulation):
        """엔티티 상태 추적 테스트"""
        behavior = list(simulation.entity_behaviors.values())[0]
        
        # 초기 상태
        status = behavior.get_status()
        assert status["energy"] == 100
        assert status["mood"] == 50
        assert status["is_awake"] == True
        
        # 행동 후 상태 변화
        await behavior._execute_action("work")
        status = behavior.get_status()
        assert status["energy"] == 90
        assert status["mood"] == 55
        
        await behavior._execute_action("eat")
        status = behavior.get_status()
        assert status["energy"] == 100
        assert status["mood"] == 65
