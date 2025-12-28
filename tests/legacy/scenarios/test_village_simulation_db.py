#!/usr/bin/env python3
"""
마을 시뮬레이션 DB 통합 테스트
실제 DB를 통한 100일 시뮬레이션 테스트
"""

import sys
import os
import asyncio
import uuid
from datetime import datetime, timedelta

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.connection import DatabaseConnection
from app.entity.entity_manager import EntityManager
from app.world.cell_manager import CellManager
from app.interaction.action_handler import ActionHandler
from app.effect_carrier.effect_carrier_manager import EffectCarrierManager
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from common.utils.logger import get_logger

logger = get_logger(__name__)

class VillageSimulationDB:
    def __init__(self):
        self.db_connection = None
        self.session_id = str(uuid.uuid4())
        self.entities = {}
        self.cells = {}
        self.simulation_days = 100
        
    async def setup(self):
        """시뮬레이션 초기 설정"""
        logger.info("=== 마을 시뮬레이션 DB 통합 설정 시작 ===")
        
        # DB 연결
        self.db_connection = DatabaseConnection()
        await self.db_connection.initialize()
        
        # Repository 초기화
        self.game_data_repo = GameDataRepository(self.db_connection)
        self.runtime_data_repo = RuntimeDataRepository(self.db_connection)
        self.reference_layer_repo = ReferenceLayerRepository(self.db_connection)
        
        # Manager 초기화
        self.effect_carrier_manager = EffectCarrierManager(
            self.db_connection, self.game_data_repo, 
            self.runtime_data_repo, self.reference_layer_repo
        )
        
        self.entity_manager = EntityManager(
            self.db_connection, self.game_data_repo, 
            self.runtime_data_repo, self.reference_layer_repo,
            self.effect_carrier_manager
        )
        
        self.cell_manager = CellManager(
            self.db_connection, self.game_data_repo, 
            self.runtime_data_repo, self.reference_layer_repo,
            self.entity_manager
        )
        
        self.action_handler = ActionHandler(
            self.db_connection, self.game_data_repo, 
            self.runtime_data_repo, self.reference_layer_repo,
            self.entity_manager, self.cell_manager, self.effect_carrier_manager
        )
        
        # 세션 생성
        await self._create_session()
        
        logger.info("=== 마을 시뮬레이션 DB 통합 설정 완료 ===")
    
    async def _create_session(self):
        """시뮬레이션 세션 생성"""
        await self.db_connection.execute_query(
            """
            INSERT INTO runtime_data.active_sessions (session_id, session_name, session_state, created_at)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (session_id) DO NOTHING
            """,
            self.session_id, "마을 시뮬레이션 100일", "active", datetime.now()
        )
        logger.info(f"[SUCCESS] 시뮬레이션 세션 생성: {self.session_id}")
    
    async def create_village_entities(self):
        """마을 엔티티 생성"""
        logger.info("=== 마을 엔티티 생성 시작 ===")
        
        # 마을 주민들 생성
        entity_templates = [
            "NPC_VILLAGER_001",  # 마을 주민
            "NPC_MERCHANT_001", # 상인
        ]
        
        for template in entity_templates:
            result = await self.entity_manager.create_entity(
                static_entity_id=template,
                session_id=self.session_id
            )
            
            if result.status == "success" and result.entity_data:
                self.entities[template] = result.entity_data.entity_id
                logger.info(f"[SUCCESS] {template} 엔티티 생성: {result.entity_data.entity_id}")
            else:
                logger.warning(f"엔티티 생성 실패: {template} - {result.message}")
        
        logger.info("=== 마을 엔티티 생성 완료 ===")
    
    async def create_village_cells(self):
        """마을 셀 생성"""
        logger.info("=== 마을 셀 생성 시작 ===")
        
        # 마을 셀들 생성
        cell_templates = [
            "CELL_VILLAGE_CENTER_001",  # 마을 광장
            "CELL_SHOP_INTERIOR_001",   # 상점 내부
        ]
        
        for template in cell_templates:
            result = await self.cell_manager.create_cell(
                static_cell_id=template,
                session_id=self.session_id
            )
            
            if result.success and result.cell:
                self.cells[template] = result.cell.cell_id
                logger.info(f"[SUCCESS] {template} 셀 생성: {result.cell.cell_id}")
            else:
                logger.warning(f"셀 생성 실패: {template} - {result.message}")
        
        logger.info("=== 마을 셀 생성 완료 ===")
    
    async def run_simulation(self):
        """시뮬레이션 실행"""
        logger.info(f"=== {self.simulation_days}일 시뮬레이션 시작 ===")
        
        for day in range(1, self.simulation_days + 1):
            await self._simulate_day(day)
            
            if day % 10 == 0:
                logger.info(f"[PROGRESS] {day}일 완료")
        
        logger.info(f"=== {self.simulation_days}일 시뮬레이션 완료 ===")
    
    async def _simulate_day(self, day):
        """하루 시뮬레이션"""
        # 각 엔티티의 일상 행동 시뮬레이션
        for entity_template, entity_id in self.entities.items():
            # 랜덤한 행동 선택
            actions = ["wait", "investigate", "move"]
            action = actions[day % len(actions)]
            
            try:
                if action == "move" and self.cells:
                    # 이동 행동
                    target_cell_id = list(self.cells.values())[day % len(self.cells)]
                    await self.action_handler.execute_action(
                        action_type="move",
                        player_id=entity_id,
                        target_id=target_cell_id,
                        session_id=self.session_id
                    )
                else:
                    # 기타 행동
                    await self.action_handler.execute_action(
                        action_type=action,
                        player_id=entity_id,
                        session_id=self.session_id
                    )
            except Exception as e:
                logger.warning(f"엔티티 {entity_id} 행동 실패: {e}")
    
    async def analyze_simulation_results(self):
        """시뮬레이션 결과 분석"""
        logger.info("=== 시뮬레이션 결과 분석 시작 ===")
        
        # 1. 엔티티 활동 통계
        entity_stats = await self.db_connection.execute_query(
            """
            SELECT COUNT(*) as total_entities
            FROM runtime_data.runtime_entities
            WHERE session_id = $1
            """,
            self.session_id
        )
        
        logger.info(f"[SUCCESS] 총 엔티티 수: {entity_stats[0]['total_entities']}")
        
        # 2. 셀 활동 통계
        cell_stats = await self.db_connection.execute_query(
            """
            SELECT COUNT(*) as total_cells
            FROM runtime_data.runtime_cells
            WHERE session_id = $1
            """,
            self.session_id
        )
        
        logger.info(f"[SUCCESS] 총 셀 수: {cell_stats[0]['total_cells']}")
        
        # 3. 행동 로그 통계
        action_stats = await self.db_connection.execute_query(
            """
            SELECT action, COUNT(*) as count
            FROM runtime_data.action_logs
            WHERE session_id = $1
            GROUP BY action
            ORDER BY count DESC
            """,
            self.session_id
        )
        
        logger.info(f"[SUCCESS] 행동 통계:")
        for stat in action_stats:
            logger.info(f"  - {stat['action']}: {stat['count']}회")
        
        # 4. 세션 데이터 확인
        session_data = await self.db_connection.execute_query(
            """
            SELECT session_name, session_state, created_at
            FROM runtime_data.active_sessions
            WHERE session_id = $1
            """,
            self.session_id
        )
        
        if session_data:
            session = session_data[0]
            logger.info(f"[SUCCESS] 세션 정보: {session['session_name']} ({session['session_state']})")
        
        logger.info("=== 시뮬레이션 결과 분석 완료 ===")
    
    async def cleanup(self):
        """시뮬레이션 정리"""
        logger.info("=== 마을 시뮬레이션 DB 통합 정리 시작 ===")
        
        if self.db_connection:
            await self.db_connection.close()
        
        logger.info("=== 마을 시뮬레이션 DB 통합 정리 완료 ===")

async def run_village_simulation_db():
    """마을 시뮬레이션 DB 통합 실행"""
    simulation = VillageSimulationDB()
    
    try:
        await simulation.setup()
        await simulation.create_village_entities()
        await simulation.create_village_cells()
        await simulation.run_simulation()
        await simulation.analyze_simulation_results()
        
        logger.info("=== 마을 시뮬레이션 DB 통합 성공 ===")
        return True
        
    except Exception as e:
        logger.error(f"=== 마을 시뮬레이션 DB 통합 실패: {e} ===")
        return False
        
    finally:
        await simulation.cleanup()

if __name__ == "__main__":
    result = asyncio.run(run_village_simulation_db())
    if result:
        print("마을 시뮬레이션 DB 통합 성공!")
    else:
        print("마을 시뮬레이션 DB 통합 실패!")
        sys.exit(1)
