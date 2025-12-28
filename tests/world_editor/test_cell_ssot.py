"""
Cell Service SSOT 테스트
owner_name이 JOIN으로 해결되는지 확인
"""
import pytest
import pytest_asyncio
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
async def cell_service(db_connection):
    """CellService fixture"""
    return CellService(db_connection)


@pytest_asyncio.fixture
async def test_entity(db_connection):
    """테스트용 엔티티 생성"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        entity_id = "TEST_CELL_OWNER_001"
        entity_name = "셀 테스트 주인"
        
        await conn.execute("""
            INSERT INTO game_data.entities 
            (entity_id, entity_type, entity_name, entity_description, base_stats, default_equipment, 
             default_abilities, default_inventory, entity_properties, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
            ON CONFLICT (entity_id) DO UPDATE SET entity_name = $3
        """, 
        entity_id, 'npc', entity_name, '테스트용 셀 주인 NPC', 
        serialize_jsonb_data({}), serialize_jsonb_data({}), 
        serialize_jsonb_data({}), serialize_jsonb_data({}), 
        serialize_jsonb_data({}))
        
        yield {"entity_id": entity_id, "entity_name": entity_name}
        
        # Cleanup
        await conn.execute("DELETE FROM game_data.entities WHERE entity_id = $1", entity_id)


@pytest_asyncio.fixture
async def test_location(db_connection):
    """테스트용 Location 생성"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        region_id = "TEST_REGION_CELL_SSOT_001"
        location_id = "TEST_LOC_CELL_SSOT_001"
        
        # Region 생성
        await conn.execute("""
            INSERT INTO game_data.world_regions 
            (region_id, region_name, region_description, region_type, region_properties, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
            ON CONFLICT (region_id) DO UPDATE SET region_name = $2
        """,
        region_id, '셀 테스트 지역', 'SSOT 테스트용', 'village', serialize_jsonb_data({}))
        
        # Location 생성
        await conn.execute("""
            INSERT INTO game_data.world_locations 
            (location_id, region_id, location_name, location_description, location_type, location_properties, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
            ON CONFLICT (location_id) DO UPDATE SET location_name = $3
        """,
        location_id, region_id, '셀 테스트 위치', 'SSOT 테스트용', 'shop', serialize_jsonb_data({}))
        
        yield location_id
        
        # Cleanup
        await conn.execute("DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)
        await conn.execute("DELETE FROM game_data.world_regions WHERE region_id = $1", region_id)


@pytest_asyncio.fixture
async def test_cell(db_connection, test_location, test_entity):
    """테스트용 Cell 생성 (owner_entity_id 포함)"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        cell_id = "TEST_CELL_SSOT_001"
        
        # owner_entity_id를 포함한 cell_properties
        cell_properties = {
            "ownership": {
                "owner_entity_id": test_entity["entity_id"],
                # owner_name은 저장하지 않음 (SSOT 준수)
                "is_private": False
            }
        }
        
        await conn.execute("""
            INSERT INTO game_data.world_cells 
            (cell_id, location_id, cell_name, matrix_width, matrix_height, cell_description, 
             cell_properties, cell_status, cell_type, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
            ON CONFLICT (cell_id) DO UPDATE SET cell_properties = $7
        """,
        cell_id, test_location, '테스트 셀', 10, 10, 'SSOT 테스트용', 
        serialize_jsonb_data(cell_properties), 'active', 'indoor')
        
        yield cell_id
        
        # Cleanup
        await conn.execute("DELETE FROM game_data.world_cells WHERE cell_id = $1", cell_id)


@pytest.mark.asyncio
async def test_get_cell_with_owner_name_join(cell_service, test_cell, test_entity):
    """Cell 조회 시 owner_name이 JOIN으로 해결되는지 확인"""
    cell = await cell_service.get_cell(test_cell)
    
    assert cell is not None
    assert cell.cell_id == test_cell
    assert cell.owner_name == test_entity["entity_name"]  # JOIN으로 해결됨
    
    # cell_properties에 owner_name이 없어야 함 (SSOT 준수)
    if cell.cell_properties and 'ownership' in cell.cell_properties:
        ownership = cell.cell_properties.get('ownership', {})
        assert 'owner_name' not in ownership, "owner_name은 Properties에 저장되지 않아야 함"


@pytest.mark.asyncio
async def test_get_cell_without_owner(cell_service, test_location):
    """owner가 없는 Cell 조회 시 owner_name이 None인지 확인"""
    pool = await cell_service.db.pool
    async with pool.acquire() as conn:
        cell_id = "TEST_CELL_NO_OWNER_001"
        
        # owner가 없는 cell_properties
        cell_properties = {
            "ownership": {
                "is_private": False
            }
        }
        
        await conn.execute("""
            INSERT INTO game_data.world_cells 
            (cell_id, location_id, cell_name, matrix_width, matrix_height, cell_description, 
             cell_properties, cell_status, cell_type, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
        """,
        cell_id, test_location, '주인 없는 셀', 10, 10, '테스트용', 
        serialize_jsonb_data(cell_properties), 'active', 'indoor')
        
        try:
            cell = await cell_service.get_cell(cell_id)
            
            assert cell is not None
            assert cell.cell_id == cell_id
            assert cell.owner_name is None  # owner가 없으면 None
        finally:
            # Cleanup
            await conn.execute("DELETE FROM game_data.world_cells WHERE cell_id = $1", cell_id)


@pytest.mark.asyncio
async def test_get_cell_owner_name_sync(cell_service, test_cell, test_entity, db_connection):
    """엔티티 이름 변경 시 owner_name이 자동으로 업데이트되는지 확인 (SSOT)"""
    # 1. 초기 조회
    cell = await cell_service.get_cell(test_cell)
    assert cell.owner_name == test_entity["entity_name"]
    
    # 2. 엔티티 이름 변경
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        new_name = "변경된 셀 주인 이름"
        await conn.execute("""
            UPDATE game_data.entities 
            SET entity_name = $1 
            WHERE entity_id = $2
        """, new_name, test_entity["entity_id"])
    
    # 3. 다시 조회 - owner_name이 자동으로 업데이트되어야 함
    cell = await cell_service.get_cell(test_cell)
    assert cell.owner_name == new_name, "JOIN으로 해결되므로 엔티티 이름 변경 시 자동 반영되어야 함"


@pytest.mark.asyncio
async def test_get_all_cells_with_owner_name(cell_service, test_cell, test_entity):
    """모든 Cell 조회 시 owner_name이 JOIN으로 해결되는지 확인"""
    cells = await cell_service.get_all_cells()
    
    test_cell_obj = next((c for c in cells if c.cell_id == test_cell), None)
    assert test_cell_obj is not None
    assert test_cell_obj.owner_name == test_entity["entity_name"]


@pytest.mark.asyncio
async def test_get_cells_by_location_with_owner_name(cell_service, test_cell, test_entity, test_location):
    """Location별 Cell 조회 시 owner_name이 JOIN으로 해결되는지 확인"""
    cells = await cell_service.get_cells_by_location(test_location)
    
    test_cell_obj = next((c for c in cells if c.cell_id == test_cell), None)
    assert test_cell_obj is not None
    assert test_cell_obj.owner_name == test_entity["entity_name"]

