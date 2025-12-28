#!/usr/bin/env python3
"""
대화 상호작용 시나리오 테스트
NPC와 플레이어 간의 실제 대화를 Manager 클래스들을 통해 테스트
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
from app.interaction.dialogue_manager import DialogueManager
from app.interaction.action_handler import ActionHandler
from app.effect_carrier.effect_carrier_manager import EffectCarrierManager
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from common.utils.logger import get_logger

logger = get_logger(__name__)

class DialogueInteractionScenario:
    def __init__(self):
        self.db_connection = None
        self.session_id = str(uuid.uuid4())
        self.player_id = None
        self.npc_id = None
        self.cell_id = None
        
    async def setup(self):
        """시나리오 초기 설정"""
        logger.info("=== 대화 상호작용 시나리오 설정 시작 ===")
        
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
        
        self.dialogue_manager = DialogueManager(
            self.db_connection, self.game_data_repo, 
            self.runtime_data_repo, self.reference_layer_repo,
            self.entity_manager, self.effect_carrier_manager
        )
        
        self.action_handler = ActionHandler(
            self.db_connection, self.game_data_repo, 
            self.runtime_data_repo, self.reference_layer_repo,
            self.entity_manager, self.cell_manager, self.effect_carrier_manager
        )
        
        # 세션 생성
        await self._create_session()
        
        logger.info("=== 대화 상호작용 시나리오 설정 완료 ===")
    
    async def _create_session(self):
        """테스트 세션 생성"""
        await self.db_connection.execute_query(
            """
            INSERT INTO runtime_data.active_sessions (session_id, session_name, session_state, created_at)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (session_id) DO NOTHING
            """,
            self.session_id, "대화 상호작용 테스트", "active", datetime.now()
        )
        logger.info(f"[SUCCESS] 테스트 세션 생성: {self.session_id}")
    
    async def create_test_entities(self):
        """테스트용 엔티티 생성"""
        logger.info("=== 테스트 엔티티 생성 시작 ===")
        
        # 플레이어 엔티티 생성 (마을 주민을 플레이어로 사용)
        player_result = await self.entity_manager.create_entity(
            static_entity_id="NPC_VILLAGER_001",
            session_id=self.session_id
        )
        self.player_id = player_result.entity_id
        logger.info(f"[SUCCESS] 플레이어 엔티티 생성: {player_result}")
        
        # NPC 엔티티 생성 (상인)
        npc_result = await self.entity_manager.create_entity(
            static_entity_id="NPC_MERCHANT_001",
            session_id=self.session_id
        )
        self.npc_id = npc_result.entity_id
        logger.info(f"[SUCCESS] NPC 엔티티 생성: {npc_result}")
        
        logger.info("=== 테스트 엔티티 생성 완료 ===")
    
    async def create_test_cell(self):
        """테스트용 셀 생성"""
        logger.info("=== 테스트 셀 생성 시작 ===")
        
        # 상점 셀 생성
        cell_result = await self.cell_manager.create_cell(
            static_cell_id="CELL_SHOP_INTERIOR_001",
            session_id=self.session_id
        )
        self.cell_id = cell_result.cell.cell_id
        logger.info(f"[SUCCESS] 테스트 셀 생성: {cell_result}")
        
        # 플레이어와 NPC를 셀에 배치
        await self.cell_manager.enter_cell(self.player_id, self.cell_id)
        await self.cell_manager.enter_cell(self.npc_id, self.cell_id)
        
        logger.info("=== 테스트 셀 생성 완료 ===")
    
    async def test_dialogue_interaction(self):
        """대화 상호작용 테스트"""
        logger.info("=== 대화 상호작용 테스트 시작 ===")
        
        # 1. 대화 시작
        dialogue_result = await self.dialogue_manager.start_dialogue(
            player_id=self.player_id,
            npc_id=self.npc_id,
            session_id=self.session_id
        )
        
        assert dialogue_result is not None, "대화 시작 실패"
        logger.info(f"[SUCCESS] 대화 시작: {dialogue_result}")
        
        # 2. 대화 계속 (플레이어 응답)
        player_response = "안녕하세요! 상점에 어떤 물건들이 있나요?"
        dialogue_continue = await self.dialogue_manager.continue_dialogue(
            player_id=self.player_id,
            npc_id=self.npc_id,
            topic="greeting",
            session_id=self.session_id,
            player_message=player_response
        )
        
        assert dialogue_continue is not None, "대화 계속 실패"
        logger.info(f"[SUCCESS] 플레이어 응답: {player_response}")
        logger.info(f"[SUCCESS] NPC 응답: {dialogue_continue}")
        
        # 3. 대화 주제 확인
        available_topics = await self.dialogue_manager.get_available_topics(
            npc_id=self.npc_id
        )
        
        assert len(available_topics) > 0, "사용 가능한 대화 주제가 없습니다"
        logger.info(f"[SUCCESS] 사용 가능한 대화 주제: {len(available_topics)}개")
        
        # 4. 대화 종료
        end_result = await self.dialogue_manager.end_dialogue(
            player_id=self.player_id,
            npc_id=self.npc_id
        )
        
        assert end_result is not None, "대화 종료 실패"
        logger.info(f"[SUCCESS] 대화 종료: {end_result}")
        
        logger.info("=== 대화 상호작용 테스트 완료 ===")
    
    async def test_action_interaction(self):
        """행동 상호작용 테스트"""
        logger.info("=== 행동 상호작용 테스트 시작 ===")
        
        # 1. 조사 행동
        investigate_result = await self.action_handler.execute_action(
            action_type="investigate",
            player_id=self.player_id,
            target_id=self.npc_id,
            session_id=self.session_id
        )
        
        assert investigate_result is not None, "조사 행동 실패"
        logger.info(f"[SUCCESS] 조사 행동: {investigate_result}")
        
        # 2. 대화 행동
        dialogue_action = await self.action_handler.execute_action(
            action_type="dialogue",
            player_id=self.player_id,
            target_id=self.npc_id,
            session_id=self.session_id
        )
        
        assert dialogue_action is not None, "대화 행동 실패"
        logger.info(f"[SUCCESS] 대화 행동: {dialogue_action}")
        
        # 3. 거래 행동
        trade_action = await self.action_handler.execute_action(
            action_type="trade",
            player_id=self.player_id,
            target_id=self.npc_id,
            session_id=self.session_id
        )
        
        assert trade_action is not None, "거래 행동 실패"
        logger.info(f"[SUCCESS] 거래 행동: {trade_action}")
        
        logger.info("=== 행동 상호작용 테스트 완료 ===")
    
    async def verify_dialogue_history(self):
        """대화 기록 검증"""
        logger.info("=== 대화 기록 검증 시작 ===")
        
        # 대화 기록 조회
        dialogue_history = await self.dialogue_manager.get_dialogue_history(
            session_id=self.session_id,
            player_id=self.player_id,
            npc_id=self.npc_id
        )
        
        assert len(dialogue_history) > 0, "대화 기록이 없습니다"
        logger.info(f"[SUCCESS] 대화 기록 조회: {len(dialogue_history)}개")
        
        # 각 대화 기록 검증
        for record in dialogue_history:
            assert 'speaker_type' in record, "대화 기록에 화자 정보가 없습니다"
            assert 'message' in record, "대화 기록에 메시지가 없습니다"
            assert 'timestamp' in record, "대화 기록에 시간 정보가 없습니다"
        
        logger.info("=== 대화 기록 검증 완료 ===")
    
    async def cleanup(self):
        """시나리오 정리"""
        logger.info("=== 대화 상호작용 시나리오 정리 시작 ===")
        
        if self.db_connection:
            await self.db_connection.close()
        
        logger.info("=== 대화 상호작용 시나리오 정리 완료 ===")

async def run_dialogue_interaction_scenario():
    """대화 상호작용 시나리오 실행"""
    scenario = DialogueInteractionScenario()
    
    try:
        await scenario.setup()
        await scenario.create_test_entities()
        await scenario.create_test_cell()
        await scenario.test_dialogue_interaction()
        await scenario.test_action_interaction()
        await scenario.verify_dialogue_history()
        
        logger.info("=== 대화 상호작용 시나리오 성공 ===")
        return True
        
    except Exception as e:
        logger.error(f"=== 대화 상호작용 시나리오 실패: {e} ===")
        return False
        
    finally:
        await scenario.cleanup()

if __name__ == "__main__":
    result = asyncio.run(run_dialogue_interaction_scenario())
    if result:
        print("대화 상호작용 시나리오 성공!")
    else:
        print("대화 상호작용 시나리오 실패!")
        sys.exit(1)
