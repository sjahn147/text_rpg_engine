"""
마을 시뮬레이션 테스트
- 100회 연속 실행을 통한 시뮬레이션 검증
- DB 트랜잭션을 통한 모든 상호작용 추적
- 기존 Manager 클래스들을 활용한 NPC 자동 행동
"""
import pytest
import asyncio
import logging
import uuid
from typing import Dict, List, Any
from datetime import datetime

from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from app.entity.entity_manager import EntityManager, EntityType, EntityStatus
from app.world.cell_manager import CellManager, CellType, CellStatus
from app.interaction.dialogue_manager import DialogueManager
from app.interaction.action_handler import ActionHandler
from app.effect_carrier.effect_carrier_manager import EffectCarrierManager
from app.systems.time_system import TimeSystem, TimePeriod
from app.systems.npc_behavior import NPCBehavior

logger = logging.getLogger(__name__)


class VillageSimulationTest:
    """마을 시뮬레이션 테스트 클래스"""
    
    def __init__(self):
        self.logger = logger
        
        # DB 연결 및 리포지토리 초기화
        self.db = DatabaseConnection()
        self.game_data_repo = GameDataRepository(self.db)
        self.runtime_data_repo = RuntimeDataRepository(self.db)
        self.reference_layer_repo = ReferenceLayerRepository(self.db)
        
        # Manager 초기화
        self.effect_carrier_manager = EffectCarrierManager(
            db_connection=self.db,
            game_data_repo=self.game_data_repo,
            runtime_data_repo=self.runtime_data_repo,
            reference_layer_repo=self.reference_layer_repo
        )
        
        self.entity_manager = EntityManager(
            db_connection=self.db,
            game_data_repo=self.game_data_repo,
            runtime_data_repo=self.runtime_data_repo,
            reference_layer_repo=self.reference_layer_repo,
            effect_carrier_manager=self.effect_carrier_manager
        )
        
        self.cell_manager = CellManager(
            db_connection=self.db,
            game_data_repo=self.game_data_repo,
            runtime_data_repo=self.runtime_data_repo,
            reference_layer_repo=self.reference_layer_repo,
            entity_manager=self.entity_manager
        )
        
        self.dialogue_manager = DialogueManager(
            db_connection=self.db,
            game_data_repo=self.game_data_repo,
            runtime_data_repo=self.runtime_data_repo,
            reference_layer_repo=self.reference_layer_repo,
            entity_manager=self.entity_manager,
            effect_carrier_manager=self.effect_carrier_manager
        )
        
        self.action_handler = ActionHandler(
            db_connection=self.db,
            game_data_repo=self.game_data_repo,
            runtime_data_repo=self.runtime_data_repo,
            reference_layer_repo=self.reference_layer_repo,
            entity_manager=self.entity_manager,
            cell_manager=self.cell_manager,
            effect_carrier_manager=self.effect_carrier_manager
        )
        
        # 시스템 초기화
        self.time_system = TimeSystem(time_speed=10)  # 10배속
        self.npc_behavior = NPCBehavior(
            db_connection=self.db,
            entity_manager=self.entity_manager,
            cell_manager=self.cell_manager,
            dialogue_manager=self.dialogue_manager,
            action_handler=self.action_handler,
            time_system=self.time_system
        )
        
        # 시간 시스템 설정 로드 (초기화 시점에서는 기본값 사용)
        self.time_system._set_default_time_periods()
        
        # 테스트 세션 ID 생성
        self.session_id = str(uuid.uuid4())
        
        # 시뮬레이션 메트릭스
        self.metrics = {
            "total_actions": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "interactions": 0,
            "cell_movements": 0,
            "dialogues": 0,
            "errors": [],
            "execution_time": 0,
            "simulation_days": 0
        }
        
        # NPC ID 목록
        self.npc_ids = [
            "MERCHANT_THOMAS_001",
            "FARMER_JOHN_001", 
            "INNKEEPER_MARIA_001",
            "GUARD_ALEX_001",
            "TRAVELER_ELLA_001"
        ]
        
        # 셀 ID 목록
        self.cell_ids = [
            "CELL_SQUARE_CENTER_001",
            "CELL_SQUARE_FOUNTAIN_001",
            "CELL_WEAPON_SHOP_001",
            "CELL_GENERAL_SHOP_001",
            "CELL_MERCHANT_HOUSE_001",
            "CELL_FARMER_HOUSE_001"
        ]
    
    async def initialize_database(self):
        """데이터베이스 연결 초기화"""
        try:
            await self.db.initialize()
            self.logger.info("데이터베이스 연결 초기화 완료")
        except Exception as e:
            self.logger.error(f"데이터베이스 연결 초기화 실패: {str(e)}")
            raise
    
    async def create_village_cells(self):
        """마을 셀 생성 - 정적 템플릿에서 런타임 인스턴스 생성"""
        try:
            # 정적 셀 템플릿 ID들
            static_cell_ids = [
                "CELL_SQUARE_CENTER_001",
                "CELL_SQUARE_FOUNTAIN_001", 
                "CELL_WEAPON_SHOP_001",
                "CELL_GENERAL_SHOP_001",
                "CELL_MERCHANT_HOUSE_001",
                "CELL_FARMER_HOUSE_001"
            ]
            
            # 각 정적 셀 템플릿에 대해 런타임 인스턴스 생성
            for i, static_cell_id in enumerate(static_cell_ids):
                # cell_manager를 사용하여 런타임 셀 인스턴스 생성
                result = await self.cell_manager.create_cell(static_cell_id, self.session_id)
                
                if not result.success:
                    raise Exception(f"셀 생성 실패: {result.message}")
                
                self.cell_ids[i] = result.cell.cell_id
            
            self.logger.info("마을 셀 생성 완료")
            self.logger.info(f"Created cells: {self.cell_ids}")
            
            # NPC 행동 시스템에 셀 매핑 설정
            cell_mapping = {
                "CELL_SQUARE_CENTER_001": self.cell_ids[0],
                "CELL_SQUARE_FOUNTAIN_001": self.cell_ids[1],
                "CELL_WEAPON_SHOP_001": self.cell_ids[2],
                "CELL_GENERAL_SHOP_001": self.cell_ids[3],
                "CELL_MERCHANT_HOUSE_001": self.cell_ids[4],
                "CELL_FARMER_HOUSE_001": self.cell_ids[5]
            }
            self.npc_behavior.set_cell_mapping(cell_mapping)
            
            # DB에서 NPC 행동 스케줄 로드
            await self.npc_behavior.load_npc_behavior_schedules(self.session_id)
            
        except Exception as e:
            self.logger.error(f"마을 셀 생성 실패: {str(e)}")
            raise
    
    async def create_village_npcs(self):
        """마을 NPC 생성"""
        try:
            # 상인 토마스
            await self.entity_manager.create_entity(
                name="상인 토마스",
                entity_type=EntityType.NPC,
                properties={
                    "profession": "merchant",
                    "gold": 1000,
                    "shop_items": ["sword", "shield", "potion"],
                    "personality": "friendly_commercial"
                }
            )
            
            # 농부 존
            await self.entity_manager.create_entity(
                name="농부 존",
                entity_type=EntityType.NPC,
                properties={
                    "profession": "farmer",
                    "energy": 100,
                    "crops": ["wheat", "corn", "potato"],
                    "personality": "simple_honest"
                }
            )
            
            # 여관주인 마리아
            await self.entity_manager.create_entity(
                name="여관주인 마리아",
                entity_type=EntityType.NPC,
                properties={
                    "profession": "innkeeper",
                    "rooms": 5,
                    "price": 10,
                    "personality": "warm_generous"
                }
            )
            
            # 수호병 알렉스
            await self.entity_manager.create_entity(
                name="수호병 알렉스",
                entity_type=EntityType.NPC,
                properties={
                    "profession": "guard",
                    "weapon": "sword",
                    "patrol_route": ["gate", "square"],
                    "personality": "responsible_strict"
                }
            )
            
            # 여행자 엘라
            await self.entity_manager.create_entity(
                name="여행자 엘라",
                entity_type=EntityType.NPC,
                properties={
                    "profession": "traveler",
                    "destination": "next_town",
                    "stories": ["adventure", "mystery"],
                    "personality": "curious_adventurous"
                }
            )
            
            self.logger.info("마을 NPC 생성 완료")
            
        except Exception as e:
            self.logger.error(f"마을 NPC 생성 실패: {str(e)}")
            raise
    
    async def initialize_village(self):
        """마을 초기화"""
        try:
            await self.initialize_database()
            await self.create_village_cells()
            await self.create_village_npcs()
            
            self.logger.info("마을 초기화 완료")
            
        except Exception as e:
            self.logger.error(f"마을 초기화 실패: {str(e)}")
            raise
    
    async def run_simulation_hour(self, hour: int):
        """1시간 시뮬레이션 실행"""
        try:
            # 시간 진행
            time_state = await self.time_system.tick_hour()
            
            self.logger.info(f"Simulating hour {hour}: {time_state.time_period.value}")
            
            # 모든 NPC의 루틴 실행
            for npc_id in self.npc_ids:
                try:
                    success = await self.npc_behavior.execute_daily_routine(npc_id)
                    
                    if success:
                        self.metrics["successful_actions"] += 1
                    else:
                        self.metrics["failed_actions"] += 1
                        self.metrics["errors"].append(f"Routine failed for {npc_id} at hour {hour}")
                    
                    self.metrics["total_actions"] += 1
                    
                except Exception as e:
                    self.metrics["failed_actions"] += 1
                    self.metrics["errors"].append(f"Error for {npc_id} at hour {hour}: {str(e)}")
                    self.logger.error(f"Error executing routine for {npc_id}: {str(e)}")
            
            # 시간 진행 대기 (시뮬레이션 속도 조절)
            await asyncio.sleep(0.1)
            
        except Exception as e:
            self.logger.error(f"Error in simulation hour {hour}: {str(e)}")
            raise
    
    async def run_simulation_day(self, day: int):
        """1일 시뮬레이션 실행"""
        try:
            self.logger.info(f"Starting simulation for day {day}")
            
            # 24시간 시뮬레이션
            for hour in range(24):
                await self.run_simulation_hour(hour)
            
            self.metrics["simulation_days"] = day
            self.logger.info(f"Day {day} simulation completed")
            
        except Exception as e:
            self.logger.error(f"Error in simulation day {day}: {str(e)}")
            raise
    
    async def run_100_day_simulation(self):
        """100일 시뮬레이션 실행"""
        try:
            start_time = datetime.now()
            self.logger.info("Starting 100-day village simulation")
            
            # 100일 시뮬레이션
            for day in range(1, 101):
                await self.run_simulation_day(day)
                
                # 진행 상황 로깅 (매 10일마다)
                if day % 10 == 0:
                    self.logger.info(f"Simulation progress: {day}/100 days completed")
            
            end_time = datetime.now()
            self.metrics["execution_time"] = (end_time - start_time).total_seconds()
            
            self.logger.info(f"100-day simulation completed in {self.metrics['execution_time']:.2f} seconds")
            
        except Exception as e:
            self.logger.error(f"Error in 100-day simulation: {str(e)}")
            raise
    
    async def analyze_simulation_results(self):
        """시뮬레이션 결과 분석"""
        try:
            # DB에서 데이터 조회
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # 액션 로그 수 조회
                action_count = await conn.fetchval("SELECT COUNT(*) FROM runtime_data.action_logs")
                
                # 대화 기록 수 조회
                dialogue_count = await conn.fetchval("SELECT COUNT(*) FROM runtime_data.dialogue_history")
                
                # 셀 이동 수 조회
                cell_movement_count = await conn.fetchval("SELECT COUNT(*) FROM runtime_data.cell_occupants")
                
                # 엔티티 상태 수 조회
                entity_count = await conn.fetchval("SELECT COUNT(*) FROM runtime_data.runtime_entities")
            
            # 결과 분석
            results = {
                "total_actions": self.metrics["total_actions"],
                "successful_actions": self.metrics["successful_actions"],
                "failed_actions": self.metrics["failed_actions"],
                "success_rate": (self.metrics["successful_actions"] / self.metrics["total_actions"] * 100) if self.metrics["total_actions"] > 0 else 0,
                "db_action_logs": action_count,
                "db_dialogue_sessions": dialogue_count,
                "db_cell_movements": cell_movement_count,
                "db_entities": entity_count,
                "execution_time": self.metrics["execution_time"],
                "simulation_days": self.metrics["simulation_days"],
                "errors": len(self.metrics["errors"])
            }
            
            self.logger.info("Simulation results analysis:")
            for key, value in results.items():
                self.logger.info(f"  {key}: {value}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error analyzing simulation results: {str(e)}")
            raise
    
    async def cleanup(self):
        """정리 작업"""
        try:
            await self.db.close()
            self.logger.info("Cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")


# 테스트 함수들
@pytest.mark.asyncio
async def test_village_simulation_100_days():
    """100일 마을 시뮬레이션 테스트"""
    simulation = VillageSimulationTest()
    
    try:
        # 마을 초기화
        await simulation.initialize_village()
        
        # 100일 시뮬레이션 실행
        await simulation.run_100_day_simulation()
        
        # 결과 분석
        results = await simulation.analyze_simulation_results()
        
        # 검증
        assert results["simulation_days"] == 100, f"Expected 100 days, got {results['simulation_days']}"
        assert results["success_rate"] > 80, f"Success rate too low: {results['success_rate']:.2f}%"
        assert results["db_action_logs"] > 0, "No action logs found in database"
        assert results["db_dialogue_sessions"] > 0, "No dialogue sessions found in database"
        assert results["db_cell_movements"] > 0, "No cell movements found in database"
        assert results["execution_time"] < 600, f"Execution time too long: {results['execution_time']:.2f} seconds"
        
        print(f"[SUCCESS] 100-day simulation completed successfully!")
        print(f"   - Success rate: {results['success_rate']:.2f}%")
        print(f"   - DB action logs: {results['db_action_logs']}")
        print(f"   - DB dialogue sessions: {results['db_dialogue_sessions']}")
        print(f"   - DB cell movements: {results['db_cell_movements']}")
        print(f"   - Execution time: {results['execution_time']:.2f} seconds")
        
    finally:
        await simulation.cleanup()


@pytest.mark.asyncio
async def test_npc_daily_routine():
    """NPC 하루 일과 테스트"""
    simulation = VillageSimulationTest()
    
    try:
        # 마을 초기화
        await simulation.initialize_village()
        
        # 1일 시뮬레이션 실행
        await simulation.run_simulation_day(1)
        
        # 결과 분석
        results = await simulation.analyze_simulation_results()
        
        # 검증
        assert results["simulation_days"] == 1, f"Expected 1 day, got {results['simulation_days']}"
        assert results["total_actions"] > 0, "No actions executed"
        assert results["success_rate"] > 70, f"Success rate too low: {results['success_rate']:.2f}%"
        
        print(f"✅ NPC daily routine test completed!")
        print(f"   - Total actions: {results['total_actions']}")
        print(f"   - Success rate: {results['success_rate']:.2f}%")
        
    finally:
        await simulation.cleanup()


@pytest.mark.asyncio
async def test_npc_interactions():
    """NPC 상호작용 테스트"""
    simulation = VillageSimulationTest()
    
    try:
        # 마을 초기화
        await simulation.initialize_village()
        
        # 점심시간 시뮬레이션 (상호작용 시간)
        for hour in range(12, 14):  # 12:00-14:00
            await simulation.run_simulation_hour(hour)
        
        # 결과 분석
        results = await simulation.analyze_simulation_results()
        
        # 검증
        assert results["db_dialogue_sessions"] > 0, "No dialogue sessions found"
        assert results["db_cell_movements"] > 0, "No cell movements found"
        
        print(f"✅ NPC interactions test completed!")
        print(f"   - Dialogue sessions: {results['db_dialogue_sessions']}")
        print(f"   - Cell movements: {results['db_cell_movements']}")
        
    finally:
        await simulation.cleanup()
