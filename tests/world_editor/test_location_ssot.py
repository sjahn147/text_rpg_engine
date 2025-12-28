"""
Location Service SSOT 테스트
owner_name이 JOIN으로 해결되는지 확인
"""
import pytest
import pytest_asyncio
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
async def location_service(db_connection):
    """LocationService fixture"""
    return LocationService(db_connection)


@pytest_asyncio.fixture
async def test_entity(db_connection):
    """테스트용 엔티티 생성"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        entity_id = "TEST_OWNER_001"
        entity_name = "테스트 주인"
        
        await conn.execute("""
            INSERT INTO game_data.entities 
            (entity_id, entity_type, entity_name, entity_description, base_stats, default_equipment, 
             default_abilities, default_inventory, entity_properties, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
            ON CONFLICT (entity_id) DO UPDATE SET entity_name = $3
        """, 
        entity_id, 'npc', entity_name, '테스트용 주인 NPC', 
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
        region_id = "TEST_REGION_SSOT_001"
        
        await conn.execute("""
            INSERT INTO game_data.world_regions 
            (region_id, region_name, region_description, region_type, region_properties, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
            ON CONFLICT (region_id) DO UPDATE SET region_name = $2
        """,
        region_id, '테스트 지역', 'SSOT 테스트용', 'village', serialize_jsonb_data({}))
        
        yield region_id
        
        # Cleanup
        await conn.execute("DELETE FROM game_data.world_regions WHERE region_id = $1", region_id)


@pytest_asyncio.fixture
async def test_location(db_connection, test_region, test_entity):
    """테스트용 Location 생성 (owner_entity_id 포함)"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        location_id = "TEST_LOC_SSOT_001"
        
        # owner_entity_id를 포함한 location_properties
        location_properties = {
            "ownership": {
                "owner_entity_id": test_entity["entity_id"],
                # owner_name은 저장하지 않음 (SSOT 준수)
                "ownership_type": "private",
                "tax_rate": 0.05
            }
        }
        
        await conn.execute("""
            INSERT INTO game_data.world_locations 
            (location_id, region_id, location_name, location_description, location_type, location_properties, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
            ON CONFLICT (location_id) DO UPDATE SET location_properties = $6
        """,
        location_id, test_region, '테스트 위치', 'SSOT 테스트용', 'shop', 
        serialize_jsonb_data(location_properties))
        
        yield location_id
        
        # Cleanup
        await conn.execute("DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)


@pytest.mark.asyncio
async def test_get_location_with_owner_name_join(location_service, test_location, test_entity):
    """Location 조회 시 owner_name이 JOIN으로 해결되는지 확인"""
    location = await location_service.get_location(test_location)
    
    assert location is not None
    assert location.location_id == test_location
    assert location.owner_name == test_entity["entity_name"]  # JOIN으로 해결됨
    
    # location_properties에 owner_name이 없어야 함 (SSOT 준수)
    if location.location_properties and 'ownership' in location.location_properties:
        ownership = location.location_properties.get('ownership', {})
        assert 'owner_name' not in ownership, "owner_name은 Properties에 저장되지 않아야 함"


@pytest.mark.asyncio
async def test_get_location_without_owner(location_service, test_region):
    """owner가 없는 Location 조회 시 owner_name이 None인지 확인"""
    pool = await location_service.db.pool
    async with pool.acquire() as conn:
        location_id = "TEST_LOC_NO_OWNER_001"
        
        # owner가 없는 location_properties
        location_properties = {
            "ownership": {
                "ownership_type": "public"
            }
        }
        
        await conn.execute("""
            INSERT INTO game_data.world_locations 
            (location_id, region_id, location_name, location_description, location_type, location_properties, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
        """,
        location_id, test_region, '주인 없는 위치', '테스트용', 'public', 
        serialize_jsonb_data(location_properties))
        
        try:
            location = await location_service.get_location(location_id)
            
            assert location is not None
            assert location.location_id == location_id
            assert location.owner_name is None  # owner가 없으면 None
        finally:
            # Cleanup
            await conn.execute("DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)


@pytest.mark.asyncio
async def test_get_location_owner_name_sync(location_service, test_location, test_entity, db_connection):
    """엔티티 이름 변경 시 owner_name이 자동으로 업데이트되는지 확인 (SSOT)"""
    # 1. 초기 조회
    location = await location_service.get_location(test_location)
    assert location.owner_name == test_entity["entity_name"]
    
    # 2. 엔티티 이름 변경
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        new_name = "변경된 주인 이름"
        await conn.execute("""
            UPDATE game_data.entities 
            SET entity_name = $1 
            WHERE entity_id = $2
        """, new_name, test_entity["entity_id"])
    
    # 3. 다시 조회 - owner_name이 자동으로 업데이트되어야 함
    location = await location_service.get_location(test_location)
    assert location.owner_name == new_name, "JOIN으로 해결되므로 엔티티 이름 변경 시 자동 반영되어야 함"


@pytest.mark.asyncio
async def test_get_all_locations_with_owner_name(location_service, test_location, test_entity):
    """모든 Location 조회 시 owner_name이 JOIN으로 해결되는지 확인"""
    locations = await location_service.get_all_locations()
    
    test_loc = next((loc for loc in locations if loc.location_id == test_location), None)
    assert test_loc is not None
    assert test_loc.owner_name == test_entity["entity_name"]


@pytest.mark.asyncio
async def test_get_locations_by_region_with_owner_name(location_service, test_location, test_entity, test_region):
    """Region별 Location 조회 시 owner_name이 JOIN으로 해결되는지 확인"""
    locations = await location_service.get_locations_by_region(test_region)
    
    test_loc = next((loc for loc in locations if loc.location_id == test_location), None)
    assert test_loc is not None
    assert test_loc.owner_name == test_entity["entity_name"]

