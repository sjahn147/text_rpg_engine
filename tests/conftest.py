"""
pytest 설정 및 공통 픽스처
- DB 연결 관리
- 테스트 환경 설정
- 비동기 이벤트 루프 관리
"""
import pytest
import asyncio
import uuid
from typing import AsyncGenerator, Dict, Any
from database.connection_manager import connection_manager, test_db_manager
from database.connection import DatabaseConnection
from app.managers.entity_manager import EntityManager
from app.managers.cell_manager import CellManager
from app.managers.dialogue_manager import DialogueManager
from app.handlers.action_handler import ActionHandler
from app.managers.effect_carrier_manager import EffectCarrierManager
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository


@pytest.fixture(scope="session")
def event_loop():
    """세션 레벨 이벤트 루프"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_connection() -> AsyncGenerator[DatabaseConnection, None]:
    """테스트용 DB 연결"""
    test_id = str(uuid.uuid4())
    connection = None
    
    try:
        # 테스트별 독립적인 연결 생성
        connection = await test_db_manager.create_test_connection(test_id)
        yield connection
    finally:
        if connection:
            await test_db_manager.cleanup_test_connection(test_id)


@pytest.fixture(scope="function")
async def repositories(db_connection: DatabaseConnection) -> Dict[str, Any]:
    """리포지토리 인스턴스들"""
    return {
        'game_data_repo': GameDataRepository(db_connection),
        'runtime_data_repo': RuntimeDataRepository(db_connection),
        'reference_layer_repo': ReferenceLayerRepository(db_connection)
    }


@pytest.fixture(scope="function")
async def managers(db_connection: DatabaseConnection, repositories: Dict[str, Any]) -> Dict[str, Any]:
    """매니저 인스턴스들"""
    # EffectCarrierManager 먼저 생성
    effect_carrier_manager = EffectCarrierManager(
        db_connection=db_connection,
        game_data_repo=repositories['game_data_repo'],
        runtime_data_repo=repositories['runtime_data_repo'],
        reference_layer_repo=repositories['reference_layer_repo']
    )
    
    # EntityManager 생성
    entity_manager = EntityManager(
        db_connection=db_connection,
        game_data_repo=repositories['game_data_repo'],
        runtime_data_repo=repositories['runtime_data_repo'],
        reference_layer_repo=repositories['reference_layer_repo'],
        effect_carrier_manager=effect_carrier_manager
    )
    
    # CellManager 생성
    cell_manager = CellManager(
        db_connection=db_connection,
        game_data_repo=repositories['game_data_repo'],
        runtime_data_repo=repositories['runtime_data_repo'],
        reference_layer_repo=repositories['reference_layer_repo'],
        entity_manager=entity_manager
    )
    
    # DialogueManager 생성
    dialogue_manager = DialogueManager(
        db_connection=db_connection,
        game_data_repo=repositories['game_data_repo'],
        runtime_data_repo=repositories['runtime_data_repo'],
        reference_layer_repo=repositories['reference_layer_repo'],
        entity_manager=entity_manager,
        effect_carrier_manager=effect_carrier_manager
    )
    
    # ActionHandler 생성
    action_handler = ActionHandler(
        db_connection=db_connection,
        game_data_repo=repositories['game_data_repo'],
        runtime_data_repo=repositories['runtime_data_repo'],
        reference_layer_repo=repositories['reference_layer_repo'],
        entity_manager=entity_manager,
        cell_manager=cell_manager,
        effect_carrier_manager=effect_carrier_manager
    )
    
    return {
        'entity_manager': entity_manager,
        'cell_manager': cell_manager,
        'dialogue_manager': dialogue_manager,
        'action_handler': action_handler,
        'effect_carrier_manager': effect_carrier_manager
    }


@pytest.fixture(scope="function")
async def clean_database(db_connection: DatabaseConnection):
    """테스트 전 DB 정리"""
    try:
        # 테스트 데이터 정리
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 런타임 데이터 정리
            await conn.execute("DELETE FROM runtime_data.runtime_entities")
            await conn.execute("DELETE FROM runtime_data.runtime_cells")
            await conn.execute("DELETE FROM runtime_data.cell_occupants")
            await conn.execute("DELETE FROM runtime_data.dialogue_sessions")
            await conn.execute("DELETE FROM runtime_data.action_logs")
            await conn.execute("DELETE FROM runtime_data.effect_carriers")
            await conn.execute("DELETE FROM runtime_data.entity_effect_ownership")
            
        yield
        
    except Exception as e:
        print(f"Database cleanup failed: {str(e)}")
        raise


@pytest.fixture(scope="function")
async def test_session_id() -> str:
    """테스트용 세션 ID"""
    return str(uuid.uuid4())


# 비동기 테스트 마커
pytest_plugins = ["pytest_asyncio"]


def pytest_configure(config):
    """pytest 설정"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )


def pytest_collection_modifyitems(config, items):
    """테스트 수집 시 비동기 마커 자동 추가"""
    for item in items:
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)
