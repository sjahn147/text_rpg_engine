"""
Active 테스트를 위한 공통 픽스처
새로운 아키텍처 (Repository 패턴, 2-tier 스키마)에 맞춰 작성
"""
import pytest
import pytest_asyncio
import asyncio
import uuid
from typing import Dict, Any
from datetime import datetime

from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository

from app.managers.entity_manager import EntityManager
from app.managers.cell_manager import CellManager
from app.managers.dialogue_manager import DialogueManager
from app.handlers.action_handler import ActionHandler
from app.managers.effect_carrier_manager import EffectCarrierManager

from common.utils.logger import logger


# ============================================================================
# 1. 데이터베이스 픽스처
# ============================================================================

@pytest_asyncio.fixture(scope="function")
async def db_connection():
    """
    테스트용 데이터베이스 연결
    각 테스트 함수마다 새로운 연결 생성
    """
    db = DatabaseConnection()
    await db.initialize()
    logger.info("[OK] Test DB connection initialized")
    
    yield db
    
    await db.close()
    logger.info("[OK] Test DB connection closed")


@pytest_asyncio.fixture(scope="function")
async def db_with_templates(db_connection):
    """
    테스트용 정적 템플릿이 준비된 데이터베이스
    test_templates.sql이 이미 실행되었다고 가정
    """
    # 템플릿 데이터 존재 확인
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        entity_count = await conn.fetchval(
            "SELECT COUNT(*) FROM game_data.entities WHERE entity_id LIKE 'TEST_%' OR entity_id LIKE 'NPC_%'"
        )
        cell_count = await conn.fetchval(
            "SELECT COUNT(*) FROM game_data.world_cells WHERE cell_id LIKE 'CELL_%'"
        )
        
        logger.info(f"[DATA] Test templates loaded: {entity_count} entities, {cell_count} cells")
        
        if entity_count == 0 or cell_count == 0:
            logger.warning("[WARNING] Test templates not found! Please run database/setup/test_templates.sql")
    
    yield db_connection


# ============================================================================
# 2. Repository 픽스처
# ============================================================================

@pytest_asyncio.fixture(scope="function")
async def repositories(db_connection):
    """
    모든 Repository 인스턴스 제공
    """
    return {
        'game_data_repo': GameDataRepository(db_connection),
        'runtime_data_repo': RuntimeDataRepository(db_connection),
        'reference_layer_repo': ReferenceLayerRepository(db_connection)
    }


# ============================================================================
# 3. Manager 픽스처
# ============================================================================

@pytest_asyncio.fixture(scope="function")
async def effect_carrier_manager(db_connection, repositories):
    """Effect Carrier Manager 인스턴스"""
    return EffectCarrierManager(
        db_connection,
        repositories['game_data_repo'],
        repositories['runtime_data_repo'],
        repositories['reference_layer_repo']
    )


@pytest_asyncio.fixture(scope="function")
async def entity_manager(db_connection, repositories, effect_carrier_manager):
    """Entity Manager 인스턴스"""
    return EntityManager(
        db_connection,
        repositories['game_data_repo'],
        repositories['runtime_data_repo'],
        repositories['reference_layer_repo'],
        effect_carrier_manager
    )


@pytest_asyncio.fixture(scope="function")
async def cell_manager(db_connection, repositories, entity_manager):
    """Cell Manager 인스턴스"""
    return CellManager(
        db_connection,
        repositories['game_data_repo'],
        repositories['runtime_data_repo'],
        repositories['reference_layer_repo'],
        entity_manager
    )


@pytest_asyncio.fixture(scope="function")
async def dialogue_manager(db_connection, repositories, entity_manager):
    """Dialogue Manager 인스턴스"""
    return DialogueManager(
        db_connection,
        repositories['game_data_repo'],
        repositories['runtime_data_repo'],
        repositories['reference_layer_repo'],
        entity_manager
    )


@pytest_asyncio.fixture(scope="function")
async def action_handler(db_connection, repositories, entity_manager, cell_manager):
    """Action Handler 인스턴스"""
    return ActionHandler(
        db_connection,
        repositories['game_data_repo'],
        repositories['runtime_data_repo'],
        repositories['reference_layer_repo'],
        entity_manager,
        cell_manager
    )


@pytest_asyncio.fixture(scope="function")
async def all_managers(entity_manager, cell_manager, dialogue_manager, action_handler, effect_carrier_manager):
    """
    모든 Manager 인스턴스를 딕셔너리로 제공
    통합 테스트에서 사용
    """
    return {
        'entity_manager': entity_manager,
        'cell_manager': cell_manager,
        'dialogue_manager': dialogue_manager,
        'action_handler': action_handler,
        'effect_carrier_manager': effect_carrier_manager
    }


# ============================================================================
# 4. 테스트 세션 픽스처
# ============================================================================

@pytest_asyncio.fixture(scope="function")
async def test_session(db_connection):
    """
    테스트용 게임 세션 생성 및 정리
    """
    session_id = str(uuid.uuid4())
    
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        # 세션 생성 (신 스키마 구조)
        await conn.execute("""
            INSERT INTO runtime_data.active_sessions 
            (session_id, session_name, session_state, last_active_at)
            VALUES ($1, $2, $3, NOW())
        """, session_id, 'Test Session', 'active')
        
        logger.info(f"[SESSION] Test session created: {session_id}")
    
    yield {
        'session_id': session_id
    }
    
    # 세션 정리 (테스트 종료 후)
    async with pool.acquire() as conn:
        # 관련 런타임 데이터 삭제 (외래키 제약조건 순서 고려)
        # dialogue_history가 runtime_entities를 참조하므로 먼저 삭제
        await conn.execute("DELETE FROM runtime_data.dialogue_history WHERE session_id = $1", session_id)
        await conn.execute("DELETE FROM runtime_data.dialogue_states WHERE session_id = $1", session_id)
        await conn.execute("DELETE FROM runtime_data.runtime_entities WHERE session_id = $1", session_id)
        await conn.execute("DELETE FROM runtime_data.runtime_cells WHERE session_id = $1", session_id)
        await conn.execute("DELETE FROM runtime_data.active_sessions WHERE session_id = $1", session_id)
        
        logger.info(f"[CLEANUP] Test session cleaned up: {session_id}")


# ============================================================================
# 5. 테스트 데이터 픽스처
# ============================================================================

@pytest_asyncio.fixture(scope="function")
async def test_entities(db_with_templates, entity_manager, test_session):
    """
    테스트용 런타임 엔티티 생성
    """
    session_id = test_session['session_id']
    entities = {}
    
    # 테스트 플레이어 생성
    player_result = await entity_manager.create_entity(
        static_entity_id="TEST_PLAYER_001",
        session_id=session_id
    )
    if player_result.status == "success":
        entities['player'] = player_result.entity_id
        logger.info(f"👤 Test player created: {player_result.entity_id}")
    
    # 테스트 NPC 생성 (마을 주민)
    villager_result = await entity_manager.create_entity(
        static_entity_id="NPC_VILLAGER_001",
        session_id=session_id
    )
    if villager_result.status == "success":
        entities['villager'] = villager_result.entity_id
        logger.info(f"👤 Test villager created: {villager_result.entity_id}")
    
    # 테스트 NPC 생성 (상인)
    merchant_result = await entity_manager.create_entity(
        static_entity_id="NPC_MERCHANT_001",
        session_id=session_id
    )
    if merchant_result.status == "success":
        entities['merchant'] = merchant_result.entity_id
        logger.info(f"👤 Test merchant created: {merchant_result.entity_id}")
    
    yield entities
    
    # 정리는 test_session fixture에서 처리됨


@pytest_asyncio.fixture(scope="function")
async def test_cells(db_with_templates, cell_manager, test_session):
    """
    테스트용 런타임 셀 생성
    """
    session_id = test_session['session_id']
    cells = {}
    
    # 테스트 셀 생성 (마을 광장)
    village_result = await cell_manager.create_cell(
        static_cell_id="CELL_VILLAGE_SQUARE_001",
        session_id=session_id
    )
    if village_result.cell:
        cells['village_square'] = village_result.cell.cell_id
        logger.info(f"🏘️ Test cell created: {village_result.cell.cell_id}")
    
    # 테스트 셀 생성 (상점)
    shop_result = await cell_manager.create_cell(
        static_cell_id="CELL_SHOP_INTERIOR_001",
        session_id=session_id
    )
    if shop_result.cell:
        cells['shop'] = shop_result.cell.cell_id
        logger.info(f"🏘️ Test cell created: {shop_result.cell.cell_id}")
    
    yield cells
    
    # 정리는 test_session fixture에서 처리됨


# ============================================================================
# 6. 유틸리티 픽스처
# ============================================================================

@pytest.fixture
def assert_db_state():
    """
    데이터베이스 상태 검증 헬퍼
    """
    async def _assert_entity_exists(db_connection, entity_id: str) -> bool:
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM runtime_data.runtime_entities WHERE runtime_entity_id = $1)",
                entity_id
            )
            return result
    
    async def _assert_cell_exists(db_connection, cell_id: str) -> bool:
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM runtime_data.runtime_cells WHERE runtime_cell_id = $1)",
                cell_id
            )
            return result
    
    return {
        'entity_exists': _assert_entity_exists,
        'cell_exists': _assert_cell_exists
    }


# ============================================================================
# Pytest 설정
# ============================================================================

def pytest_configure(config):
    """Pytest 설정"""
    logger.info("Active test suite configuration loaded")


def pytest_collection_modifyitems(config, items):
    """테스트 아이템 수정"""
    for item in items:
        # asyncio 마크 자동 추가
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)

