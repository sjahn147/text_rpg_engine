"""
실제 DB 연결을 통한 시나리오 테스트
Mock 의존성을 제거하고 실제 PostgreSQL 데이터베이스 사용
"""
import pytest
import pytest_asyncio
import asyncio
import uuid
from datetime import datetime
from app.entity.entity_manager import EntityManager, EntityType, EntityStatus
from app.world.cell_manager import CellManager, CellType, CellStatus
from app.interaction.dialogue_manager import DialogueManager
from app.interaction.action_handler import ActionHandler
from app.effect_carrier.effect_carrier_manager import EffectCarrierManager
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from common.utils.logger import logger


class TestRealDBScenarios:
    """실제 DB 연결을 통한 시나리오 테스트"""
    
    @pytest_asyncio.fixture(scope="class")
    async def db_connection(self):
        """실제 DB 연결"""
        db = DatabaseConnection()
        await db.initialize()
        yield db
        await db.close()
    
    @pytest_asyncio.fixture(scope="class")
    async def repositories(self, db_connection):
        """Repository 인스턴스들"""
        return {
            'game_data': GameDataRepository(db_connection),
            'runtime_data': RuntimeDataRepository(db_connection),
            'reference_layer': ReferenceLayerRepository(db_connection)
        }
    
    @pytest_asyncio.fixture(scope="class")
    async def managers(self, db_connection, repositories):
        """Manager 인스턴스들"""
        effect_carrier_manager = EffectCarrierManager(
            db_connection=db_connection,
            game_data_repo=repositories['game_data'],
            runtime_data_repo=repositories['runtime_data'],
            reference_layer_repo=repositories['reference_layer']
        )
        
        return {
            'entity_manager': EntityManager(
                db_connection=db_connection,
                game_data_repo=repositories['game_data'],
                runtime_data_repo=repositories['runtime_data'],
                reference_layer_repo=repositories['reference_layer'],
                effect_carrier_manager=effect_carrier_manager
            ),
            'cell_manager': CellManager(
                db_connection=db_connection,
                game_data_repo=repositories['game_data'],
                runtime_data_repo=repositories['runtime_data'],
                reference_layer_repo=repositories['reference_layer'],
                entity_manager=None  # 순환 참조 방지
            ),
            'dialogue_manager': DialogueManager(
                db_connection=db_connection,
                game_data_repo=repositories['game_data'],
                runtime_data_repo=repositories['runtime_data'],
                reference_layer_repo=repositories['reference_layer'],
                entity_manager=None,
                effect_carrier_manager=effect_carrier_manager
            ),
            'action_handler': ActionHandler(
                db_connection=db_connection,
                game_data_repo=repositories['game_data'],
                runtime_data_repo=repositories['runtime_data'],
                reference_layer_repo=repositories['reference_layer'],
                entity_manager=None,
                cell_manager=None,
                effect_carrier_manager=effect_carrier_manager
            ),
            'effect_carrier_manager': effect_carrier_manager
        }
    
    @pytest_asyncio.fixture(scope="class")
    async def test_session(self, managers):
        """테스트용 세션 생성"""
        session_id = str(uuid.uuid4())
        
        # 테스트 세션을 DB에 생성
        pool = await managers['entity_manager'].db.pool
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO runtime_data.active_sessions (session_id, session_name, session_state, created_at)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (session_id) DO NOTHING
            """, session_id, "test-session", "active", datetime.now())
        
        return session_id
    
    @pytest.mark.asyncio
    async def test_entity_creation_scenario(self, managers, test_session):
        """엔티티 생성 시나리오 - 정적 데이터 → 런타임 인스턴스"""
        logger.info("=== 엔티티 생성 시나리오 시작 ===")
        
        # 1. 정적 엔티티 템플릿에서 런타임 인스턴스 생성
        static_entity_id = "NPC_MERCHANT_001"
        custom_properties = {"health": 100, "level": 5, "shop_items": ["sword", "potion"]}
        custom_position = {"x": 10.0, "y": 20.0}
        
        result = await managers['entity_manager'].create_entity(
            static_entity_id=static_entity_id,
            session_id=test_session,
            custom_properties=custom_properties,
            custom_position=custom_position
        )
        
        assert result.success, f"엔티티 생성 실패: {result.message}"
        assert result.entity is not None
        assert result.entity.entity_type == EntityType.NPC
        assert result.entity.properties == custom_properties
        assert result.entity.position == custom_position
        
        logger.info(f"[SUCCESS] 엔티티 생성 완료: {result.entity.entity_id}")
        
        # 2. 생성된 엔티티 조회
        get_result = await managers['entity_manager'].get_entity(result.entity.entity_id)
        assert get_result.success, f"엔티티 조회 실패: {get_result.message}"
        assert get_result.entity.entity_id == result.entity.entity_id
        
        logger.info(f"[SUCCESS] 엔티티 조회 완료: {get_result.entity.name}")
        
        # 3. 엔티티 상태 업데이트
        update_result = await managers['entity_manager'].update_entity(
            result.entity.entity_id,
            properties={"health": 80, "level": 6},
            position={"x": 15.0, "y": 25.0}
        )
        
        assert update_result.success, f"엔티티 업데이트 실패: {update_result.message}"
        
        logger.info(f"[SUCCESS] 엔티티 업데이트 완료")
        
        # 4. 정리
        delete_result = await managers['entity_manager'].delete_entity(result.entity.entity_id)
        assert delete_result.success, f"엔티티 삭제 실패: {delete_result.message}"
        
        logger.info(f"[SUCCESS] 엔티티 삭제 완료")
        logger.info("=== 엔티티 생성 시나리오 완료 ===")
    
    @pytest.mark.asyncio
    async def test_cell_management_scenario(self, managers, test_session):
        """셀 관리 시나리오 - 셀 생성, 이동, 삭제"""
        logger.info("=== 셀 관리 시나리오 시작 ===")
        
        # 1. 정적 셀 템플릿에서 런타임 인스턴스 생성
        static_cell_id = "CELL_VILLAGE_CENTER_001"
        
        result = await managers['cell_manager'].create_cell(
            static_cell_id=static_cell_id,
            session_id=test_session
        )
        
        assert result.success, f"셀 생성 실패: {result.message}"
        assert result.cell is not None
        assert result.cell.cell_type == CellType.INDOOR
        
        logger.info(f"[SUCCESS] 셀 생성 완료: {result.cell.cell_id}")
        
        # 2. 생성된 셀 조회
        get_result = await managers['cell_manager'].get_cell(result.cell.cell_id)
        assert get_result.success, f"셀 조회 실패: {get_result.message}"
        assert get_result.cell.cell_id == result.cell.cell_id
        
        logger.info(f"[SUCCESS] 셀 조회 완료: {get_result.cell.cell_id}")
        
        # 3. 셀 상태 업데이트
        update_result = await managers['cell_manager'].update_cell(
            result.cell.cell_id,
            properties={"lighting": "bright", "temperature": 22}
        )
        
        assert update_result.success, f"셀 업데이트 실패: {update_result.message}"
        
        logger.info(f"[SUCCESS] 셀 업데이트 완료")
        
        # 4. 정리
        delete_result = await managers['cell_manager'].delete_cell(result.cell.cell_id)
        assert delete_result.success, f"셀 삭제 실패: {delete_result.message}"
        
        logger.info(f"[SUCCESS] 셀 삭제 완료")
        logger.info("=== 셀 관리 시나리오 완료 ===")
    
    @pytest.mark.asyncio
    async def test_dialogue_interaction_scenario(self, managers, test_session):
        """대화 상호작용 시나리오 - NPC와 플레이어 대화"""
        logger.info("=== 대화 상호작용 시나리오 시작 ===")
        
        # 1. 플레이어와 NPC 생성
        player_result = await managers['entity_manager'].create_entity(
            static_entity_id="NPC_PLAYER_001",
            session_id=test_session,
            custom_properties={"health": 100, "level": 1},
            custom_position={"x": 0.0, "y": 0.0}
        )
        
        assert player_result.success, f"플레이어 생성 실패: {player_result.message}"
        
        npc_result = await managers['entity_manager'].create_entity(
            static_entity_id="NPC_MERCHANT_001",
            session_id=test_session,
            custom_properties={"health": 100, "level": 5},
            custom_position={"x": 10.0, "y": 10.0}
        )
        
        assert npc_result.success, f"NPC 생성 실패: {npc_result.message}"
        
        logger.info(f"[SUCCESS] 플레이어와 NPC 생성 완료")
        
        # 2. 대화 시작
        dialogue_result = await managers['dialogue_manager'].start_dialogue(
            player_id=player_result.entity.entity_id,
            npc_id=npc_result.entity.entity_id,
            session_id=test_session
        )
        
        assert dialogue_result.success, f"대화 시작 실패: {dialogue_result.message}"
        
        logger.info(f"[SUCCESS] 대화 시작 완료")
        
        # 3. 대화 계속
        continue_result = await managers['dialogue_manager'].continue_dialogue(
            player_id=player_result.entity.entity_id,
            npc_id=npc_result.entity.entity_id,
            topic="greeting",
            player_message="안녕하세요!",
            session_id=test_session
        )
        
        assert continue_result.success, f"대화 계속 실패: {continue_result.message}"
        
        logger.info(f"[SUCCESS] 대화 계속 완료")
        
        # 4. 대화 기록 조회
        history_result = await managers['dialogue_manager'].get_dialogue_history(
            player_id=player_result.entity.entity_id,
            npc_id=npc_result.entity.entity_id
        )
        
        assert history_result.success, f"대화 기록 조회 실패: {history_result.message}"
        assert len(history_result.history) > 0, "대화 기록이 없습니다"
        
        logger.info(f"[SUCCESS] 대화 기록 조회 완료: {len(history_result.history)}개 메시지")
        
        # 5. 정리
        await managers['entity_manager'].delete_entity(player_result.entity.entity_id)
        await managers['entity_manager'].delete_entity(npc_result.entity.entity_id)
        
        logger.info(f"[SUCCESS] 정리 완료")
        logger.info("=== 대화 상호작용 시나리오 완료 ===")
    
    @pytest.mark.asyncio
    async def test_action_execution_scenario(self, managers, test_session):
        """행동 실행 시나리오 - 플레이어 행동 및 결과"""
        logger.info("=== 행동 실행 시나리오 시작 ===")
        
        # 1. 플레이어 생성
        player_result = await managers['entity_manager'].create_entity(
            static_entity_id="NPC_PLAYER_001",
            session_id=test_session,
            custom_properties={"health": 100, "level": 1},
            custom_position={"x": 0.0, "y": 0.0}
        )
        
        assert player_result.success, f"플레이어 생성 실패: {player_result.message}"
        
        logger.info(f"[SUCCESS] 플레이어 생성 완료")
        
        # 2. 조사 행동 실행
        investigate_result = await managers['action_handler'].execute_action(
            action_type="investigate",
            player_id=player_result.entity.entity_id,
            target_id="village_square",
            session_id=test_session
        )
        
        assert investigate_result.success, f"조사 행동 실패: {investigate_result.message}"
        
        logger.info(f"[SUCCESS] 조사 행동 완료")
        
        # 3. 대기 행동 실행
        wait_result = await managers['action_handler'].execute_action(
            action_type="wait",
            player_id=player_result.entity.entity_id,
            target_id=None,
            session_id=test_session
        )
        
        assert wait_result.success, f"대기 행동 실패: {wait_result.message}"
        
        logger.info(f"[SUCCESS] 대기 행동 완료")
        
        # 4. 사용 가능한 행동 조회
        actions_result = await managers['action_handler'].get_available_actions(
            player_id=player_result.entity.entity_id
        )
        
        assert actions_result.success, f"행동 목록 조회 실패: {actions_result.message}"
        assert len(actions_result.actions) > 0, "사용 가능한 행동이 없습니다"
        
        logger.info(f"[SUCCESS] 행동 목록 조회 완료: {len(actions_result.actions)}개 행동")
        
        # 5. 정리
        await managers['entity_manager'].delete_entity(player_result.entity.entity_id)
        
        logger.info(f"[SUCCESS] 정리 완료")
        logger.info("=== 행동 실행 시나리오 완료 ===")
    
    @pytest.mark.asyncio
    async def test_full_game_flow_scenario(self, managers, test_session):
        """전체 게임 플로우 시나리오"""
        logger.info("=== 전체 게임 플로우 시나리오 시작 ===")
        
        # 1. 플레이어 생성
        player_result = await managers['entity_manager'].create_entity(
            static_entity_id="NPC_PLAYER_001",
            session_id=test_session,
            custom_properties={"health": 100, "level": 1},
            custom_position={"x": 0.0, "y": 0.0}
        )
        
        assert player_result.success, f"플레이어 생성 실패: {player_result.message}"
        
        # 2. 셀 생성
        cell_result = await managers['cell_manager'].create_cell(
            static_cell_id="CELL_VILLAGE_CENTER_001",
            session_id=test_session
        )
        
        assert cell_result.success, f"셀 생성 실패: {cell_result.message}"
        
        # 3. 플레이어를 셀에 배치
        enter_result = await managers['cell_manager'].enter_cell(
            cell_id=cell_result.cell.cell_id,
            entity_id=player_result.entity.entity_id,
            entity_type="player"
        )
        
        assert enter_result.success, f"셀 진입 실패: {enter_result.message}"
        
        # 4. NPC 생성
        npc_result = await managers['entity_manager'].create_entity(
            static_entity_id="NPC_MERCHANT_001",
            session_id=test_session,
            custom_properties={"health": 100, "level": 5},
            custom_position={"x": 10.0, "y": 10.0}
        )
        
        assert npc_result.success, f"NPC 생성 실패: {npc_result.message}"
        
        # 5. 대화 시작
        dialogue_result = await managers['dialogue_manager'].start_dialogue(
            player_id=player_result.entity.entity_id,
            npc_id=npc_result.entity.entity_id,
            session_id=test_session
        )
        
        assert dialogue_result.success, f"대화 시작 실패: {dialogue_result.message}"
        
        # 6. 행동 실행
        action_result = await managers['action_handler'].execute_action(
            action_type="investigate",
            player_id=player_result.entity.entity_id,
            target_id="village_square",
            session_id=test_session
        )
        
        assert action_result.success, f"행동 실행 실패: {action_result.message}"
        
        logger.info(f"[SUCCESS] 전체 게임 플로우 완료")
        
        # 7. 정리
        await managers['entity_manager'].delete_entity(player_result.entity.entity_id)
        await managers['entity_manager'].delete_entity(npc_result.entity.entity_id)
        await managers['cell_manager'].delete_cell(cell_result.cell.cell_id)
        
        logger.info(f"[SUCCESS] 정리 완료")
        logger.info("=== 전체 게임 플로우 시나리오 완료 ===")
