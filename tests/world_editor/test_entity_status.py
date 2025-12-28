"""
Entity Status 테스트
"""
import pytest
import pytest_asyncio
from database.connection import DatabaseConnection
from app.world_editor.services.entity_service import EntityService
from app.world_editor.schemas import EntityCreate, EntityUpdate


@pytest_asyncio.fixture
async def db_connection():
    """데이터베이스 연결 픽스처"""
    db = DatabaseConnection()
    await db.initialize()
    yield db
    await db.close()


@pytest_asyncio.fixture
async def entity_service(db_connection):
    """Entity Service 픽스처"""
    return EntityService(db_connection)


@pytest_asyncio.fixture
async def test_cell(db_connection):
    """테스트용 Cell 생성"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        cell_id = "TEST_CELL_ENTITY_STATUS_001"
        location_id = "TEST_LOCATION_ENTITY_STATUS_001"
        region_id = "TEST_REGION_ENTITY_STATUS_001"
        
        # Region 생성
        await conn.execute("""
            INSERT INTO game_data.world_regions
            (region_id, region_name, region_type, region_description, region_properties)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (region_id) DO NOTHING
        """, region_id, "Test Region", "village", "Test region", "{}")
        
        # Location 생성
        await conn.execute("""
            INSERT INTO game_data.world_locations
            (location_id, region_id, location_name, location_type, location_description, location_properties)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (location_id) DO NOTHING
        """, location_id, region_id, "Test Location", "building", "Test location", "{}")
        
        # Cell 생성
        await conn.execute("""
            INSERT INTO game_data.world_cells
            (cell_id, location_id, cell_name, matrix_width, matrix_height, cell_properties)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (cell_id) DO NOTHING
        """, cell_id, location_id, "Test Cell", 10, 10, "{}")
        
        yield cell_id
        
        # 정리
        await conn.execute("""
            DELETE FROM game_data.entities WHERE entity_id LIKE 'TEST_ENTITY_STATUS_%'
        """)
        await conn.execute("""
            DELETE FROM game_data.world_cells WHERE cell_id = $1
        """, cell_id)
        await conn.execute("""
            DELETE FROM game_data.world_locations WHERE location_id = $1
        """, location_id)
        await conn.execute("""
            DELETE FROM game_data.world_regions WHERE region_id = $1
        """, region_id)


@pytest.mark.asyncio
async def test_create_entity_with_status(entity_service, test_cell):
    """Entity 생성 시 Status 설정 테스트"""
    entity_data = EntityCreate(
        entity_id="TEST_ENTITY_STATUS_001",
        entity_type="npc",
        entity_name="Test Entity",
        entity_status="inactive",
        entity_properties={"cell_id": test_cell}
    )
    
    entity = await entity_service.create_entity(entity_data)
    
    assert entity is not None
    assert entity.entity_status == "inactive"


@pytest.mark.asyncio
async def test_get_entity_with_status(entity_service, test_cell):
    """Entity 조회 시 Status 포함 확인"""
    # Entity 생성
    entity_data = EntityCreate(
        entity_id="TEST_ENTITY_STATUS_002",
        entity_type="npc",
        entity_name="Test Entity 2",
        entity_status="hidden",
        entity_properties={"cell_id": test_cell}
    )
    await entity_service.create_entity(entity_data)
    
    # 조회
    entity = await entity_service.get_entity("TEST_ENTITY_STATUS_002")
    
    assert entity is not None
    assert entity.entity_status == "hidden"


@pytest.mark.asyncio
async def test_update_entity_status(entity_service, test_cell):
    """Entity Status 업데이트 테스트"""
    # Entity 생성
    entity_data = EntityCreate(
        entity_id="TEST_ENTITY_STATUS_003",
        entity_type="npc",
        entity_name="Test Entity 3",
        entity_status="active",
        entity_properties={"cell_id": test_cell}
    )
    await entity_service.create_entity(entity_data)
    
    # 업데이트
    update_data = EntityUpdate(
        entity_status="dead"
    )
    updated = await entity_service.update_entity("TEST_ENTITY_STATUS_003", update_data)
    
    assert updated is not None
    assert updated.entity_status == "dead"
    # 다른 필드는 유지
    assert updated.entity_name == "Test Entity 3"


@pytest.mark.asyncio
async def test_get_entities_by_cell_with_status(entity_service, test_cell):
    """Cell별 Entity 조회 시 Status 포함 확인"""
    # 여러 Entity 생성
    entity1 = EntityCreate(
        entity_id="TEST_ENTITY_STATUS_004",
        entity_type="npc",
        entity_name="Test Entity 4",
        entity_status="active",
        entity_properties={"cell_id": test_cell}
    )
    entity2 = EntityCreate(
        entity_id="TEST_ENTITY_STATUS_005",
        entity_type="npc",
        entity_name="Test Entity 5",
        entity_status="inactive",
        entity_properties={"cell_id": test_cell}
    )
    
    await entity_service.create_entity(entity1)
    await entity_service.create_entity(entity2)
    
    # 조회
    entities = await entity_service.get_entities_by_cell(test_cell)
    
    assert len(entities) >= 2
    entity4 = next((e for e in entities if e.entity_id == "TEST_ENTITY_STATUS_004"), None)
    entity5 = next((e for e in entities if e.entity_id == "TEST_ENTITY_STATUS_005"), None)
    
    assert entity4 is not None
    assert entity4.entity_status == "active"
    
    assert entity5 is not None
    assert entity5.entity_status == "inactive"


@pytest.mark.asyncio
async def test_entity_default_status(entity_service, test_cell):
    """Entity 생성 시 기본값 확인 (Status 미지정 시)"""
    entity_data = EntityCreate(
        entity_id="TEST_ENTITY_STATUS_006",
        entity_type="npc",
        entity_name="Test Entity 6",
        entity_properties={"cell_id": test_cell}
        # entity_status 미지정
    )
    
    entity = await entity_service.create_entity(entity_data)
    
    assert entity is not None
    # 기본값 확인
    assert entity.entity_status == "active"

