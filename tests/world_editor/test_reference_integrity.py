"""
참조 무결성 검증 테스트
Entity/Cell 삭제 시 참조 검증이 올바르게 작동하는지 확인
"""
import pytest
import pytest_asyncio
from app.world_editor.services.entity_service import EntityService
from app.world_editor.services.cell_service import CellService
from app.world_editor.services.location_service import LocationService
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
async def entity_service(db_connection):
    """EntityService fixture"""
    return EntityService(db_connection)


@pytest_asyncio.fixture
async def cell_service(db_connection):
    """CellService fixture"""
    return CellService(db_connection)


@pytest_asyncio.fixture
async def location_service(db_connection):
    """LocationService fixture"""
    return LocationService(db_connection)


@pytest_asyncio.fixture
async def test_entity(db_connection):
    """테스트용 엔티티 생성"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        entity_id = "TEST_ENTITY_REF_001"
        entity_name = "참조 테스트 엔티티"
        
        await conn.execute("""
            INSERT INTO game_data.entities 
            (entity_id, entity_type, entity_name, entity_description, base_stats, default_equipment, 
             default_abilities, default_inventory, entity_properties, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
            ON CONFLICT (entity_id) DO UPDATE SET entity_name = $3
        """, 
        entity_id, 'npc', entity_name, '참조 무결성 테스트용', 
        serialize_jsonb_data({}), serialize_jsonb_data({}), 
        serialize_jsonb_data({}), serialize_jsonb_data({}), 
        serialize_jsonb_data({}))
        
        yield {"entity_id": entity_id, "entity_name": entity_name}
        
        # Cleanup
        await conn.execute("DELETE FROM game_data.entities WHERE entity_id = $1", entity_id)


@pytest_asyncio.fixture
async def test_region(db_connection):
    """테스트용 Region 생성"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        region_id = "TEST_REGION_REF_001"
        
        await conn.execute("""
            INSERT INTO game_data.world_regions 
            (region_id, region_name, region_description, region_type, region_properties, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
            ON CONFLICT (region_id) DO UPDATE SET region_name = $2
        """,
        region_id, '참조 테스트 지역', '참조 무결성 테스트용', 'village', serialize_jsonb_data({}))
        
        yield region_id
        
        # Cleanup
        await conn.execute("DELETE FROM game_data.world_regions WHERE region_id = $1", region_id)


@pytest_asyncio.fixture
async def test_location_with_owner(db_connection, test_region, test_entity):
    """owner가 있는 테스트용 Location 생성"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        location_id = "TEST_LOC_OWNER_REF_001"
        
        location_properties = {
            "ownership": {
                "owner_entity_id": test_entity["entity_id"],
                "ownership_type": "private"
            },
            "quests": {
                "quest_givers": [test_entity["entity_id"]]  # quest_givers에도 포함
            }
        }
        
        await conn.execute("""
            INSERT INTO game_data.world_locations 
            (location_id, region_id, location_name, location_description, location_type, location_properties, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
            ON CONFLICT (location_id) DO UPDATE SET location_properties = $6
        """,
        location_id, test_region, '주인이 있는 위치', '참조 테스트용', 'shop', 
        serialize_jsonb_data(location_properties))
        
        yield location_id
        
        # Cleanup
        await conn.execute("DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)


@pytest_asyncio.fixture
async def test_cell_with_owner(db_connection, test_location_with_owner, test_entity):
    """owner가 있는 테스트용 Cell 생성"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        cell_id = "TEST_CELL_OWNER_REF_001"
        
        cell_properties = {
            "ownership": {
                "owner_entity_id": test_entity["entity_id"],
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
        cell_id, test_location_with_owner, '주인이 있는 셀', 10, 10, '참조 테스트용', 
        serialize_jsonb_data(cell_properties), 'active', 'indoor')
        
        yield cell_id
        
        # Cleanup
        await conn.execute("DELETE FROM game_data.world_cells WHERE cell_id = $1", cell_id)


@pytest_asyncio.fixture
async def test_location_with_entry_point(db_connection, test_region, test_cell_with_owner):
    """entry_point가 있는 테스트용 Location 생성"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        location_id = "TEST_LOC_ENTRY_REF_001"
        
        location_properties = {
            "accessibility": {
                "entry_points": [
                    {"direction": "north", "cell_id": test_cell_with_owner}
                ]
            }
        }
        
        await conn.execute("""
            INSERT INTO game_data.world_locations 
            (location_id, region_id, location_name, location_description, location_type, location_properties, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
            ON CONFLICT (location_id) DO UPDATE SET location_properties = $6
        """,
        location_id, test_region, '진입점이 있는 위치', '참조 테스트용', 'shop', 
        serialize_jsonb_data(location_properties))
        
        yield location_id
        
        # Cleanup
        await conn.execute("DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)


@pytest_asyncio.fixture
async def test_cell_with_exit(db_connection, test_location_with_owner, test_cell_with_owner):
    """exit이 있는 테스트용 Cell 생성"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        cell_id = "TEST_CELL_EXIT_REF_001"
        
        cell_properties = {
            "structure": {
                "exits": [
                    {"direction": "north", "cell_id": test_cell_with_owner, "requires_key": False}
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
        cell_id, test_location_with_owner, '출구가 있는 셀', 10, 10, '참조 테스트용', 
        serialize_jsonb_data(cell_properties), 'active', 'indoor')
        
        yield cell_id
        
        # Cleanup
        await conn.execute("DELETE FROM game_data.world_cells WHERE cell_id = $1", cell_id)


@pytest.mark.asyncio
async def test_validate_entity_references(entity_service, test_entity, test_location_with_owner, test_cell_with_owner):
    """엔티티 참조 검증이 올바르게 작동하는지 확인"""
    references = await entity_service.validate_entity_references(test_entity["entity_id"])
    
    assert test_location_with_owner in references["locations_as_owner"]
    assert test_cell_with_owner in references["cells_as_owner"]
    assert test_location_with_owner in references["locations_in_quest_givers"]


@pytest.mark.asyncio
async def test_delete_entity_with_references_fails(entity_service, test_entity, test_location_with_owner, test_cell_with_owner):
    """참조된 엔티티 삭제 시 에러 발생 확인"""
    with pytest.raises(ValueError) as exc_info:
        await entity_service.delete_entity(test_entity["entity_id"])
    
    error_message = str(exc_info.value)
    assert "참조되고 있어 삭제할 수 없습니다" in error_message
    assert test_location_with_owner in error_message
    assert test_cell_with_owner in error_message


@pytest.mark.asyncio
async def test_delete_entity_after_removing_references(entity_service, test_entity, test_location_with_owner, test_cell_with_owner, location_service, cell_service, db_connection):
    """참조 제거 후 엔티티 삭제 가능 확인"""
    # 1. 참조 제거
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        # Location의 owner 제거
        await conn.execute("""
            UPDATE game_data.world_locations
            SET location_properties = jsonb_set(
                location_properties,
                '{ownership}',
                jsonb_set(
                    COALESCE(location_properties->'ownership', '{}'::jsonb),
                    '{owner_entity_id}',
                    'null'::jsonb
                )
            )
            WHERE location_id = $1
        """, test_location_with_owner)
        
        # Location의 quest_givers 제거
        await conn.execute("""
            UPDATE game_data.world_locations
            SET location_properties = jsonb_set(
                location_properties,
                '{quests,quest_givers}',
                '[]'::jsonb
            )
            WHERE location_id = $1
        """, test_location_with_owner)
        
        # Cell의 owner 제거
        await conn.execute("""
            UPDATE game_data.world_cells
            SET cell_properties = jsonb_set(
                cell_properties,
                '{ownership}',
                jsonb_set(
                    COALESCE(cell_properties->'ownership', '{}'::jsonb),
                    '{owner_entity_id}',
                    'null'::jsonb
                )
            )
            WHERE cell_id = $1
        """, test_cell_with_owner)
    
    # 2. 이제 삭제 가능해야 함
    result = await entity_service.delete_entity(test_entity["entity_id"])
    assert result is True


@pytest.mark.asyncio
async def test_validate_cell_references(cell_service, test_cell_with_owner, test_location_with_entry_point, test_cell_with_exit):
    """Cell 참조 검증이 올바르게 작동하는지 확인"""
    references = await cell_service.validate_cell_references(test_cell_with_owner)
    
    assert test_location_with_entry_point in references["locations_in_entry_points"]
    # test_cell_with_exit의 exits가 test_cell_with_owner를 참조하므로
    # test_cell_with_exit이 cells_in_exits에 포함되어야 함
    assert test_cell_with_exit in references["cells_in_exits"]


@pytest.mark.asyncio
async def test_delete_cell_with_references_fails(cell_service, test_cell_with_owner, test_location_with_entry_point, test_cell_with_exit):
    """참조된 Cell 삭제 시 에러 발생 확인"""
    with pytest.raises(ValueError) as exc_info:
        await cell_service.delete_cell(test_cell_with_owner)
    
    error_message = str(exc_info.value)
    assert "참조되고 있어 삭제할 수 없습니다" in error_message
    assert test_location_with_entry_point in error_message or test_cell_with_exit in error_message


@pytest.mark.asyncio
async def test_delete_cell_after_removing_references(cell_service, test_cell_with_owner, test_location_with_entry_point, test_cell_with_exit, location_service, db_connection):
    """참조 제거 후 Cell 삭제 가능 확인"""
    # 1. 참조 제거
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        # Location의 entry_points 제거
        await conn.execute("""
            UPDATE game_data.world_locations
            SET location_properties = jsonb_set(
                location_properties,
                '{accessibility,entry_points}',
                '[]'::jsonb
            )
            WHERE location_id = $1
        """, test_location_with_entry_point)
        
        # Cell의 exits 제거
        await conn.execute("""
            UPDATE game_data.world_cells
            SET cell_properties = jsonb_set(
                cell_properties,
                '{structure,exits}',
                '[]'::jsonb
            )
            WHERE cell_id = $1
        """, test_cell_with_exit)
    
    # 2. 이제 삭제 가능해야 함
    result = await cell_service.delete_cell(test_cell_with_owner)
    assert result is True


@pytest.mark.asyncio
async def test_delete_entity_without_references_succeeds(entity_service, db_connection):
    """참조가 없는 엔티티는 삭제 가능"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        entity_id = "TEST_ENTITY_NO_REF_001"
        
        await conn.execute("""
            INSERT INTO game_data.entities 
            (entity_id, entity_type, entity_name, entity_description, base_stats, default_equipment, 
             default_abilities, default_inventory, entity_properties, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
        """, 
        entity_id, 'npc', '참조 없는 엔티티', '테스트용', 
        serialize_jsonb_data({}), serialize_jsonb_data({}), 
        serialize_jsonb_data({}), serialize_jsonb_data({}), 
        serialize_jsonb_data({}))
        
        try:
            result = await entity_service.delete_entity(entity_id)
            assert result is True
        finally:
            # Cleanup (이미 삭제되었을 수 있음)
            await conn.execute("DELETE FROM game_data.entities WHERE entity_id = $1", entity_id)


@pytest.mark.asyncio
async def test_delete_cell_without_references_succeeds(cell_service, test_location_with_owner, db_connection):
    """참조가 없는 Cell은 삭제 가능"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        cell_id = "TEST_CELL_NO_REF_001"
        
        await conn.execute("""
            INSERT INTO game_data.world_cells 
            (cell_id, location_id, cell_name, matrix_width, matrix_height, cell_description, 
             cell_properties, cell_status, cell_type, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
        """,
        cell_id, test_location_with_owner, '참조 없는 셀', 10, 10, '테스트용', 
        serialize_jsonb_data({}), 'active', 'indoor')
        
        try:
            result = await cell_service.delete_cell(cell_id)
            assert result is True
        finally:
            # Cleanup (이미 삭제되었을 수 있음)
            await conn.execute("DELETE FROM game_data.world_cells WHERE cell_id = $1", cell_id)

