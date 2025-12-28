#!/usr/bin/env python3
"""
행동 실행 시나리오 테스트
플레이어의 다양한 행동을 Manager 클래스들을 통해 테스트
"""

import sys
import os
import asyncio
import uuid
from datetime import datetime

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

class ActionExecutionScenario:
    def __init__(self):
        self.db_connection = None
        self.session_id = str(uuid.uuid4())
        self.player_id = None
        self.cell_id = None
        
    async def setup(self):
        """시나리오 초기 설정"""
        logger.info("=== 행동 실행 시나리오 설정 시작 ===")
        
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
        
        logger.info("=== 행동 실행 시나리오 설정 완료 ===")
    
    async def _create_session(self):
        """테스트 세션 생성"""
        await self.db_connection.execute_query(
            """
            INSERT INTO runtime_data.active_sessions (session_id, session_name, session_state, created_at)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (session_id) DO NOTHING
            """,
            self.session_id, "행동 실행 테스트", "active", datetime.now()
        )
        logger.info(f"[SUCCESS] 테스트 세션 생성: {self.session_id}")
    
    async def create_test_entities(self):
        """테스트용 엔티티 생성"""
        logger.info("=== 테스트 엔티티 생성 시작 ===")
        
        # 플레이어 엔티티 생성
        player_result = await self.entity_manager.create_entity(
            static_entity_id="NPC_VILLAGER_001",
            session_id=self.session_id
        )
        
        if player_result.status == "success" and player_result.entity_data:
            self.player_id = player_result.entity_data.entity_id
            logger.info(f"[SUCCESS] 플레이어 엔티티 생성: {self.player_id}")
        else:
            logger.error(f"플레이어 엔티티 생성 실패: {player_result.message}")
            raise Exception(f"플레이어 엔티티 생성 실패: {player_result.message}")
        
        logger.info("=== 테스트 엔티티 생성 완료 ===")
    
    async def create_test_cell(self):
        """테스트용 셀 생성"""
        logger.info("=== 테스트 셀 생성 시작 ===")
        
        # 마을 광장 셀 생성
        cell_result = await self.cell_manager.create_cell(
            static_cell_id="CELL_VILLAGE_CENTER_001",
            session_id=self.session_id
        )
        
        if cell_result.success and cell_result.cell:
            self.cell_id = cell_result.cell.cell_id
            logger.info(f"[SUCCESS] 테스트 셀 생성: {self.cell_id}")
        else:
            logger.error(f"셀 생성 실패: {cell_result.message}")
            raise Exception(f"셀 생성 실패: {cell_result.message}")
        
        # 플레이어를 셀에 배치
        enter_result = await self.cell_manager.enter_cell(self.player_id, self.cell_id)
        if enter_result.success:
            logger.info(f"[SUCCESS] 플레이어를 셀에 배치: {self.player_id} -> {self.cell_id}")
        else:
            logger.warning(f"플레이어 셀 배치 실패: {enter_result.message}")
        
        logger.info("=== 테스트 셀 생성 완료 ===")
    
    async def test_basic_actions(self):
        """기본 행동 테스트"""
        logger.info("=== 기본 행동 테스트 시작 ===")
        
        # 1. 대기 행동
        wait_result = await self.action_handler.execute_action(
            action_type="wait",
            player_id=self.player_id,
            session_id=self.session_id
        )
        
        assert wait_result is not None, "대기 행동 실패"
        logger.info(f"[SUCCESS] 대기 행동: {wait_result}")
        
        # 2. 조사 행동
        investigate_result = await self.action_handler.execute_action(
            action_type="investigate",
            player_id=self.player_id,
            session_id=self.session_id
        )
        
        assert investigate_result is not None, "조사 행동 실패"
        logger.info(f"[SUCCESS] 조사 행동: {investigate_result}")
        
        logger.info("=== 기본 행동 테스트 완료 ===")
    
    async def test_movement_actions(self):
        """이동 행동 테스트"""
        logger.info("=== 이동 행동 테스트 시작 ===")
        
        # 1. 이동 행동
        move_result = await self.action_handler.execute_action(
            action_type="move",
            player_id=self.player_id,
            target_id=self.cell_id,
            session_id=self.session_id
        )
        
        assert move_result is not None, "이동 행동 실패"
        logger.info(f"[SUCCESS] 이동 행동: {move_result}")
        
        logger.info("=== 이동 행동 테스트 완료 ===")
    
    async def test_available_actions(self):
        """사용 가능한 행동 조회 테스트"""
        logger.info("=== 사용 가능한 행동 조회 테스트 시작 ===")
        
        # 사용 가능한 행동 조회
        available_actions = await self.action_handler.get_available_actions(
            player_id=self.player_id,
            current_cell_id=self.cell_id
        )
        
        assert len(available_actions) > 0, "사용 가능한 행동이 없습니다"
        logger.info(f"[SUCCESS] 사용 가능한 행동: {len(available_actions)}개")
        
        for action in available_actions:
            logger.info(f"  - {action}")
        
        logger.info("=== 사용 가능한 행동 조회 테스트 완료 ===")
    
    async def verify_action_logs(self):
        """행동 로그 검증"""
        logger.info("=== 행동 로그 검증 시작 ===")
        
        # 행동 로그 조회
        logs = await self.db_connection.execute_query(
            """
            SELECT action, success, message, timestamp
            FROM runtime_data.action_logs
            WHERE session_id = $1 AND player_id = $2
            ORDER BY timestamp DESC
            LIMIT 10
            """,
            self.session_id, self.player_id
        )
        
        assert len(logs) > 0, "행동 로그가 없습니다"
        logger.info(f"[SUCCESS] 행동 로그 조회: {len(logs)}개")
        
        for log in logs:
            logger.info(f"  - {log['action']}: {log['message']} ({log['timestamp']})")
        
        logger.info("=== 행동 로그 검증 완료 ===")
    
    async def cleanup(self):
        """시나리오 정리"""
        logger.info("=== 행동 실행 시나리오 정리 시작 ===")
        
        if self.db_connection:
            await self.db_connection.close()
        
        logger.info("=== 행동 실행 시나리오 정리 완료 ===")

async def run_action_execution_scenario():
    """행동 실행 시나리오 실행"""
    scenario = ActionExecutionScenario()
    
    try:
        await scenario.setup()
        await scenario.create_test_entities()
        await scenario.create_test_cell()
        await scenario.test_basic_actions()
        await scenario.test_movement_actions()
        await scenario.test_available_actions()
        await scenario.verify_action_logs()
        
        logger.info("=== 행동 실행 시나리오 성공 ===")
        return True
        
    except Exception as e:
        logger.error(f"=== 행동 실행 시나리오 실패: {e} ===")
        return False
        
    finally:
        await scenario.cleanup()

if __name__ == "__main__":
    result = asyncio.run(run_action_execution_scenario())
    if result:
        print("행동 실행 시나리오 성공!")
    else:
        print("행동 실행 시나리오 실패!")
        sys.exit(1)
