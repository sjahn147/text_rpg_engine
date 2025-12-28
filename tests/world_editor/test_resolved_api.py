"""
Resolved API 테스트 (Phase 4)
모든 참조를 해결한 Location/Cell 조회 API 테스트
"""
import pytest
import pytest_asyncio
from app.world_editor.services.location_service import LocationService
from app.world_editor.services.cell_service import CellService
from database.connection import DatabaseConnection
from common.utils.jsonb_handler import serialize_jsonb_data


@pytest_asyncio.fixture
async def db_connection():
    """데이터베이스 연결 fixture"""
    db = DatabaseConnection()
    await db.initialize()
    yield db
    await db.close()


@pytest_asyncio.fixture
async def location_service(db_connection):
    """LocationService fixture"""
    return LocationService(db_connection)


@pytest_asyncio.fixture
async def cell_service(db_connection):
    """CellService fixture"""
    return CellService(db_connection)


@pytest_asyncio.fixture
async def test_entities(db_connection):
    """테스트용 엔티티들 생성"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        entities = []
        
        # Owner 엔티티
        owner_id = "TEST_RESOLVED_OWNER_001"
        owner_name = "해결된 주인"
        await conn.execute("""
            INSERT INTO game_data.entities 
            (entity_id, entity_type, entity_name, entity_description, base_stats, default_equipment, 
             default_abilities, default_inventory, entity_properties, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
            ON CONFLICT (entity_id) DO UPDATE SET entity_name = $3
        """, 
        owner_id, 'npc', owner_name, '테스트용 주인', 
        serialize_jsonb_data({}), serialize_jsonb_data({}), 
        serialize_jsonb_data({}), serialize_jsonb_data({}), 
        serialize_jsonb_data({}))
        entities.append({"entity_id": owner_id, "entity_name": owner_name})
        
        # Quest giver 엔티티
        quest_giver_id = "TEST_RESOLVED_QUEST_GIVER_001"
        quest_giver_name = "퀘스트 제공자"
        await conn.execute("""
            INSERT INTO game_data.entities 
            (entity_id, entity_type, entity_name, entity_description, base_stats, default_equipment, 
             default_abilities, default_inventory, entity_properties, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
            ON CONFLICT (entity_id) DO UPDATE SET entity_name = $3
        """, 
        quest_giver_id, 'npc', quest_giver_name, '테스트용 퀘스트 제공자', 
        serialize_jsonb_data({}), serialize_jsonb_data({}), 
        serialize_jsonb_data({}), serialize_jsonb_data({}), 
        serialize_jsonb_data({}))
        entities.append({"entity_id": quest_giver_id, "entity_name": quest_giver_name})
        
        yield entities
        
        # Cleanup
        await conn.execute("DELETE FROM game_data.entities WHERE entity_id IN ($1, $2)", owner_id, quest_giver_id)


@pytest_asyncio.fixture
async def test_region(db_connection):
    """테스트용 Region 생성"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        region_id = "TEST_RESOLVED_REGION_001"
        
        await conn.execute("""
            INSERT INTO game_data.world_regions 
            (region_id, region_name, region_description, region_type, region_properties, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
            ON CONFLICT (region_id) DO UPDATE SET region_name = $2
        """,
        region_id, '해결된 테스트 지역', 'Resolved API 테스트용', 'village', serialize_jsonb_data({}))
        
        yield region_id
        
        # Cleanup
        await conn.execute("DELETE FROM game_data.world_regions WHERE region_id = $1", region_id)


@pytest_asyncio.fixture
async def test_entry_point_cell(db_connection, test_region):
    """Entry point로 사용할 테스트용 Cell 생성"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        # 먼저 Location 생성
        location_id = "TEST_RESOLVED_LOC_ENTRY_001"
        await conn.execute("""
            INSERT INTO game_data.world_locations 
            (location_id, region_id, location_name, location_description, location_type, location_properties, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
            ON CONFLICT (location_id) DO UPDATE SET location_name = $3
        """,
        location_id, test_region, 'Entry Point Location', '테스트용', 'shop', serialize_jsonb_data({}))
        
        # Cell 생성
        cell_id = "TEST_RESOLVED_CELL_001"
        await conn.execute("""
            INSERT INTO game_data.world_cells 
            (cell_id, location_id, cell_name, matrix_width, matrix_height, cell_description, 
             cell_properties, cell_status, cell_type, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
            ON CONFLICT (cell_id) DO UPDATE SET cell_name = $3
        """,
        cell_id, location_id, 'Entry Point Cell', 10, 10, '테스트용', 
        serialize_jsonb_data({}), 'active', 'indoor')
        
        yield cell_id
        
        # Cleanup
        await conn.execute("DELETE FROM game_data.world_cells WHERE cell_id = $1", cell_id)
        await conn.execute("DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)


@pytest_asyncio.fixture
async def test_location_with_references(db_connection, test_region, test_entities, test_entry_point_cell):
    """참조가 있는 테스트용 Location 생성"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        location_id = "TEST_RESOLVED_LOC_001"
        
        location_properties = {
            "ownership": {
                "owner_entity_id": test_entities[0]["entity_id"],
                "ownership_type": "private"
            },
            "quests": {
                "quest_givers": [test_entities[1]["entity_id"]]
            },
            "accessibility": {
                "entry_points": [
                    {"direction": "north", "cell_id": test_entry_point_cell}
                ]
            }
        }
        
        await conn.execute("""
            INSERT INTO game_data.world_locations 
            (location_id, region_id, location_name, location_description, location_type, location_properties, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
            ON CONFLICT (location_id) DO UPDATE SET location_properties = $6
        """,
        location_id, test_region, '참조가 있는 위치', 'Resolved API 테스트용', 'shop', 
        serialize_jsonb_data(location_properties))
        
        yield location_id
        
        # Cleanup
        await conn.execute("DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)


@pytest_asyncio.fixture
async def test_cell_with_references(db_connection, test_location_with_references, test_entities):
    """참조가 있는 테스트용 Cell 생성"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        cell_id = "TEST_RESOLVED_CELL_001"
        exit_cell_id = "TEST_RESOLVED_CELL_002"
        
        # Exit cell 생성
        await conn.execute("""
            INSERT INTO game_data.world_cells 
            (cell_id, location_id, cell_name, matrix_width, matrix_height, cell_description, 
             cell_properties, cell_status, cell_type, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
            ON CONFLICT (cell_id) DO UPDATE SET cell_name = $3
        """,
        exit_cell_id, test_location_with_references, '출구 셀', 10, 10, '테스트용', 
        serialize_jsonb_data({}), 'active', 'indoor')
        
        # Main cell 생성 (exit 참조 포함)
        cell_properties = {
            "ownership": {
                "owner_entity_id": test_entities[0]["entity_id"],
                "is_private": False
            },
            "structure": {
                "exits": [
                    {"direction": "north", "cell_id": exit_cell_id, "requires_key": False}
                ]
            }
        }
        
        await conn.execute("""
            INSERT INTO game_data.world_cells 
            (cell_id, location_id, cell_name, matrix_width, matrix_height, cell_description, 
             cell_properties, cell_status, cell_type, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
            ON CONFLICT (cell_id) DO UPDATE SET cell_properties = $7
        """,
        cell_id, test_location_with_references, '참조가 있는 셀', 10, 10, 'Resolved API 테스트용', 
        serialize_jsonb_data(cell_properties), 'active', 'indoor')
        
        yield cell_id
        
        # Cleanup
        await conn.execute("DELETE FROM game_data.world_cells WHERE cell_id IN ($1, $2)", cell_id, exit_cell_id)


@pytest.mark.asyncio
async def test_get_location_resolved(location_service, test_location_with_references, test_entities):
    """Location resolved API가 모든 참조를 해결하는지 확인"""
    resolved = await location_service.get_location_resolved(test_location_with_references)
    
    assert resolved is not None
    assert resolved.location_id == test_location_with_references
    
    # owner_entity 확인
    assert resolved.owner_entity is not None
    assert resolved.owner_entity["entity_id"] == test_entities[0]["entity_id"]
    assert resolved.owner_entity["entity_name"] == test_entities[0]["entity_name"]
    
    # quest_giver_entities 확인
    assert resolved.quest_giver_entities is not None
    assert len(resolved.quest_giver_entities) == 1
    assert resolved.quest_giver_entities[0]["entity_id"] == test_entities[1]["entity_id"]
    assert resolved.quest_giver_entities[0]["entity_name"] == test_entities[1]["entity_name"]
    
    # entry_point_cells 확인
    assert resolved.entry_point_cells is not None
    assert len(resolved.entry_point_cells) == 1
    assert resolved.entry_point_cells[0]["cell_id"] == "TEST_RESOLVED_CELL_001"
    assert resolved.entry_point_cells[0]["direction"] == "north"


@pytest.mark.asyncio
async def test_get_cell_resolved(cell_service, test_cell_with_references, test_entities):
    """Cell resolved API가 모든 참조를 해결하는지 확인"""
    resolved = await cell_service.get_cell_resolved(test_cell_with_references)
    
    assert resolved is not None
    assert resolved.cell_id == test_cell_with_references
    
    # owner_entity 확인
    assert resolved.owner_entity is not None
    assert resolved.owner_entity["entity_id"] == test_entities[0]["entity_id"]
    assert resolved.owner_entity["entity_name"] == test_entities[0]["entity_name"]
    
    # exit_cells 확인
    assert resolved.exit_cells is not None
    assert len(resolved.exit_cells) == 1
    assert resolved.exit_cells[0]["cell_id"] == "TEST_RESOLVED_CELL_002"
    assert resolved.exit_cells[0]["direction"] == "north"


@pytest.mark.asyncio
async def test_get_location_resolved_without_references(location_service, test_region, db_connection):
    """참조가 없는 Location의 resolved API 확인"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        location_id = "TEST_RESOLVED_LOC_NO_REF_001"
        
        await conn.execute("""
            INSERT INTO game_data.world_locations 
            (location_id, region_id, location_name, location_description, location_type, location_properties, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
        """,
        location_id, test_region, '참조 없는 위치', '테스트용', 'shop', serialize_jsonb_data({}))
        
        try:
            resolved = await location_service.get_location_resolved(location_id)
            
            assert resolved is not None
            assert resolved.location_id == location_id
            assert resolved.owner_entity is None
            assert resolved.quest_giver_entities is None
            assert resolved.entry_point_cells is None
        finally:
            await conn.execute("DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)


@pytest.mark.asyncio
async def test_get_cell_resolved_without_references(cell_service, test_location_with_references, db_connection):
    """참조가 없는 Cell의 resolved API 확인"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        cell_id = "TEST_RESOLVED_CELL_NO_REF_001"
        
        await conn.execute("""
            INSERT INTO game_data.world_cells 
            (cell_id, location_id, cell_name, matrix_width, matrix_height, cell_description, 
             cell_properties, cell_status, cell_type, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
        """,
        cell_id, test_location_with_references, '참조 없는 셀', 10, 10, '테스트용', 
        serialize_jsonb_data({}), 'active', 'indoor')
        
        try:
            resolved = await cell_service.get_cell_resolved(cell_id)
            
            assert resolved is not None
            assert resolved.cell_id == cell_id
            assert resolved.owner_entity is None
            assert resolved.exit_cells is None
            assert resolved.entrance_cells is None
            assert resolved.connection_cells is None
        finally:
            await conn.execute("DELETE FROM game_data.world_cells WHERE cell_id = $1", cell_id)

