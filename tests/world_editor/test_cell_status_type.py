"""
Cell Status 및 Cell Type 테스트
"""
import pytest
import pytest_asyncio
from database.connection import DatabaseConnection
from app.world_editor.services.cell_service import CellService
from app.world_editor.schemas import CellCreate, CellUpdate


@pytest_asyncio.fixture
async def db_connection():
    """데이터베이스 연결 픽스처"""
    db = DatabaseConnection()
    await db.initialize()
    yield db
    await db.close()


@pytest_asyncio.fixture
async def cell_service(db_connection):
    """Cell Service 픽스처"""
    return CellService(db_connection)


@pytest_asyncio.fixture
async def test_location(db_connection):
    """테스트용 Location 생성"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        location_id = "TEST_LOCATION_CELL_STATUS_001"
        region_id = "TEST_REGION_CELL_STATUS_001"
        
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
        
        yield location_id
        
        # 정리
        await conn.execute("""
            DELETE FROM game_data.world_cells WHERE location_id = $1
        """, location_id)
        await conn.execute("""
            DELETE FROM game_data.world_locations WHERE location_id = $1
        """, location_id)
        await conn.execute("""
            DELETE FROM game_data.world_regions WHERE region_id = $1
        """, region_id)


@pytest.mark.asyncio
async def test_create_cell_with_status_type(cell_service, test_location):
    """Cell 생성 시 Status 및 Type 설정 테스트"""
    cell_data = CellCreate(
        cell_id="TEST_CELL_STATUS_001",
        location_id=test_location,
        cell_name="Test Cell",
        matrix_width=10,
        matrix_height=10,
        cell_status="locked",
        cell_type="shop"
    )
    
    cell = await cell_service.create_cell(cell_data)
    
    assert cell is not None
    assert cell.cell_status == "locked"
    assert cell.cell_type == "shop"


@pytest.mark.asyncio
async def test_get_cell_with_status_type(cell_service, test_location):
    """Cell 조회 시 Status 및 Type 포함 확인"""
    # Cell 생성
    cell_data = CellCreate(
        cell_id="TEST_CELL_STATUS_002",
        location_id=test_location,
        cell_name="Test Cell 2",
        matrix_width=10,
        matrix_height=10,
        cell_status="dangerous",
        cell_type="dungeon"
    )
    await cell_service.create_cell(cell_data)
    
    # 조회
    cell = await cell_service.get_cell("TEST_CELL_STATUS_002")
    
    assert cell is not None
    assert cell.cell_status == "dangerous"
    assert cell.cell_type == "dungeon"


@pytest.mark.asyncio
async def test_update_cell_status_type(cell_service, test_location):
    """Cell Status 및 Type 업데이트 테스트"""
    # Cell 생성
    cell_data = CellCreate(
        cell_id="TEST_CELL_STATUS_003",
        location_id=test_location,
        cell_name="Test Cell 3",
        matrix_width=10,
        matrix_height=10,
        cell_status="active",
        cell_type="indoor"
    )
    await cell_service.create_cell(cell_data)
    
    # 업데이트
    update_data = CellUpdate(
        cell_status="inactive",
        cell_type="outdoor"
    )
    updated = await cell_service.update_cell("TEST_CELL_STATUS_003", update_data)
    
    assert updated is not None
    assert updated.cell_status == "inactive"
    assert updated.cell_type == "outdoor"
    # 다른 필드는 유지
    assert updated.cell_name == "Test Cell 3"


@pytest.mark.asyncio
async def test_get_cells_by_location_with_status_type(cell_service, test_location):
    """Location별 Cell 조회 시 Status 및 Type 포함 확인"""
    # 여러 Cell 생성
    cell1 = CellCreate(
        cell_id="TEST_CELL_STATUS_004",
        location_id=test_location,
        cell_name="Test Cell 4",
        matrix_width=10,
        matrix_height=10,
        cell_status="active",
        cell_type="tavern"
    )
    cell2 = CellCreate(
        cell_id="TEST_CELL_STATUS_005",
        location_id=test_location,
        cell_name="Test Cell 5",
        matrix_width=10,
        matrix_height=10,
        cell_status="locked",
        cell_type="temple"
    )
    
    await cell_service.create_cell(cell1)
    await cell_service.create_cell(cell2)
    
    # 조회
    cells = await cell_service.get_cells_by_location(test_location)
    
    assert len(cells) >= 2
    cell4 = next((c for c in cells if c.cell_id == "TEST_CELL_STATUS_004"), None)
    cell5 = next((c for c in cells if c.cell_id == "TEST_CELL_STATUS_005"), None)
    
    assert cell4 is not None
    assert cell4.cell_status == "active"
    assert cell4.cell_type == "tavern"
    
    assert cell5 is not None
    assert cell5.cell_status == "locked"
    assert cell5.cell_type == "temple"


@pytest.mark.asyncio
async def test_cell_default_status_type(cell_service, test_location):
    """Cell 생성 시 기본값 확인 (Status/Type 미지정 시)"""
    cell_data = CellCreate(
        cell_id="TEST_CELL_STATUS_006",
        location_id=test_location,
        cell_name="Test Cell 6",
        matrix_width=10,
        matrix_height=10
        # cell_status, cell_type 미지정
    )
    
    cell = await cell_service.create_cell(cell_data)
    
    assert cell is not None
    # 기본값 확인
    assert cell.cell_status == "active"
    assert cell.cell_type == "indoor"

