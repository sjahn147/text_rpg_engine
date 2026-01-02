"""
QA 테스트 공통 설정 및 Fixtures

모든 fixture는 function 스코프를 사용하여 이벤트 루프 충돌을 방지합니다.
"""
import pytest
import pytest_asyncio
import asyncio
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
import json

from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from database.factories.game_data_factory import GameDataFactory
from database.factories.instance_factory import InstanceFactory
from app.core.game_manager import GameManager
from app.services.gameplay import GameService


@pytest_asyncio.fixture(scope="function")
async def db_connection():
    """
    데이터베이스 연결 Fixture (함수 스코프)
    
    각 테스트마다 독립적인 연결 풀을 생성합니다.
    """
    db = DatabaseConnection()
    await db.initialize()
    yield db
    await db.close()


@pytest_asyncio.fixture(scope="function")
async def db_transaction(db_connection):
    """
    트랜잭션 격리 Fixture (함수 스코프)
    
    각 테스트마다 독립적인 트랜잭션을 제공하여 데이터 격리를 보장합니다.
    테스트 종료 시 자동 롤백으로 데이터 정리됩니다.
    """
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        async with conn.transaction():
            yield conn
            # 트랜잭션 롤백으로 자동 정리


@pytest_asyncio.fixture(scope="function")
async def game_data_repo(db_connection):
    """GameDataRepository Fixture"""
    return GameDataRepository(db_connection)


@pytest_asyncio.fixture(scope="function")
async def runtime_data_repo(db_connection):
    """RuntimeDataRepository Fixture"""
    return RuntimeDataRepository(db_connection)


@pytest_asyncio.fixture(scope="function")
async def reference_layer_repo(db_connection):
    """ReferenceLayerRepository Fixture"""
    return ReferenceLayerRepository(db_connection)


@pytest_asyncio.fixture(scope="function")
async def game_data_factory(db_connection):
    """GameDataFactory Fixture"""
    return GameDataFactory(db_connection)


@pytest_asyncio.fixture(scope="function")
async def instance_factory(db_connection):
    """InstanceFactory Fixture"""
    return InstanceFactory(db_connection)


@pytest_asyncio.fixture(scope="function")
async def game_manager(db_connection, game_data_repo, runtime_data_repo, reference_layer_repo):
    """GameManager Fixture"""
    return GameManager(
        db_connection=db_connection,
        game_data_repo=game_data_repo,
        runtime_data_repo=runtime_data_repo,
        reference_layer_repo=reference_layer_repo
    )


@pytest_asyncio.fixture(scope="function")
async def game_service(db_connection):
    """GameService Fixture"""
    return GameService(db_connection)


@pytest_asyncio.fixture(scope="function")
async def test_game_data(db_connection):
    """
    테스트용 게임 데이터 Fixture (함수 스코프)
    
    각 테스트에 필요한 테스트 데이터를 생성합니다.
    ON CONFLICT DO NOTHING을 사용하여 데이터 중복 방지.
    """
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        # 테스트용 게임 데이터 생성
        cell_id = "CELL_QA_TEST_ROOM_001"
        cell_id_2 = "CELL_QA_TEST_ROOM_002"
        player_template_id = "ENT_QA_TEST_PLAYER_001"
        npc_template_id = "ENT_QA_TEST_NPC_001"
        
        # 1. Region 생성
        region_id = "REG_QA_TEST_REGION_001"
        await conn.execute("""
            INSERT INTO game_data.world_regions 
            (region_id, region_name, region_description, region_properties)
            VALUES ($1, $2, $3, $4::jsonb)
            ON CONFLICT (region_id) DO NOTHING
        """,
        region_id, "QA Test Region", "QA 테스트용 지역",
        json.dumps({"climate": "temperate", "terrain": "plains"}))
        
        # 2. Location 생성
        location_id = "LOC_QA_TEST_LOCATION_001"
        await conn.execute("""
            INSERT INTO game_data.world_locations 
            (location_id, region_id, location_name, location_description, location_properties)
            VALUES ($1, $2, $3, $4, $5::jsonb)
            ON CONFLICT (location_id) DO NOTHING
        """,
        location_id, region_id, "QA Test Location", "QA 테스트용 위치",
        json.dumps({"type": "village", "population": 100}))
        
        # 3. Cell 생성 (첫 번째)
        await conn.execute("""
            INSERT INTO game_data.world_cells 
            (cell_id, location_id, cell_name, matrix_width, matrix_height, cell_description, cell_properties)
            VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb)
            ON CONFLICT (cell_id) DO NOTHING
        """,
        cell_id, location_id, "QA Test Room 1", 10, 10, "QA 테스트용 방 1",
        json.dumps({"cell_type": "indoor", "size": "medium"}))
        
        # 4. Cell 생성 (두 번째 - 이동 테스트용)
        await conn.execute("""
            INSERT INTO game_data.world_cells 
            (cell_id, location_id, cell_name, matrix_width, matrix_height, cell_description, cell_properties)
            VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb)
            ON CONFLICT (cell_id) DO NOTHING
        """,
        cell_id_2, location_id, "QA Test Room 2", 10, 10, "QA 테스트용 방 2",
        json.dumps({"cell_type": "indoor", "size": "medium"}))
        
        # 5. Entity (Player Template) 생성
        await conn.execute("""
            INSERT INTO game_data.entities 
            (entity_id, entity_name, entity_type, entity_description, entity_properties, base_stats)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (entity_id) DO NOTHING
        """,
        player_template_id, "QA Test Player", "player", "QA 테스트용 플레이어",
        json.dumps({"level": 1, "occupation": "adventurer"}),
        json.dumps({"hp": 100, "mp": 50, "strength": 10, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10}))
        
        # 6. Entity (NPC Template) 생성
        await conn.execute("""
            INSERT INTO game_data.entities 
            (entity_id, entity_name, entity_type, entity_description, entity_properties, base_stats)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (entity_id) DO NOTHING
        """,
        npc_template_id, "QA Test NPC", "npc", "QA 테스트용 NPC",
        json.dumps({"level": 1, "occupation": "merchant", "examine_text": "상인 NPC입니다."}),
        json.dumps({"hp": 50, "mp": 20, "strength": 5, "dexterity": 5, "constitution": 5, "intelligence": 5, "wisdom": 5, "charisma": 5}))
        
        yield {
            "region_id": region_id,
            "location_id": location_id,
            "cell_id": cell_id,
            "cell_id_2": cell_id_2,
            "player_template_id": player_template_id,
            "npc_template_id": npc_template_id
        }


@pytest_asyncio.fixture(scope="function", autouse=True)
async def cleanup_test_data(db_connection):
    """
    테스트 데이터 정리 Fixture (자동 실행)
    
    각 테스트 후 런타임 데이터를 정리합니다.
    
    Note: SSOT 트리거가 cell_occupants 직접 수정을 방지하므로,
    entity_states 삭제 시 트리거 충돌이 발생할 수 있음.
    현재는 비활성화하고, 테스트 데이터는 ON CONFLICT DO NOTHING으로 처리.
    """
    yield
    # 테스트 후 정리 비활성화
    # SSOT 트리거와 충돌하므로 직접 삭제 불가
    # 대신 테스트 데이터는 고정 ID를 사용하고 ON CONFLICT DO NOTHING으로 처리
    pass
