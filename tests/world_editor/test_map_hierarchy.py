"""
MapHierarchyService 단위 테스트
"""
import pytest
import pytest_asyncio
from pathlib import Path
import sys
import uuid

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from database.connection import DatabaseConnection
from database.factories.game_data_factory import GameDataFactory
from app.world_editor.services.map_hierarchy_service import MapHierarchyService


@pytest_asyncio.fixture
async def db_connection():
    """데이터베이스 연결 픽스처"""
    db = DatabaseConnection()
    pool = await db.pool
    yield pool
    await db.close()


@pytest_asyncio.fixture
async def map_hierarchy_service():
    """MapHierarchyService 픽스처"""
    return MapHierarchyService()


@pytest_asyncio.fixture
async def factory():
    """GameDataFactory 픽스처"""
    return GameDataFactory()


@pytest.mark.asyncio
async def test_get_region_map(db_connection, map_hierarchy_service, factory):
    """Region Map 조회 테스트"""
    test_id = uuid.uuid4().hex[:8]
    
    region_id = f"TEST_REG_{test_id}"
    
    try:
        # Region 생성
        await factory.create_world_region(
            region_id=region_id,
            region_name="Test Region",
            region_type="empire"
        )
        
        # Region Map 조회 (기본값 반환)
        map_data = await map_hierarchy_service.get_region_map(region_id)
        
        assert map_data is not None
        assert map_data["map_level"] == "region"
        assert map_data["parent_entity_id"] == region_id
        assert map_data["parent_entity_type"] == "region"
        assert map_data["width"] == 1000
        assert map_data["height"] == 1000
    
    finally:
        # 테스트 데이터 정리
        async with db_connection.acquire() as conn:
            await conn.execute(f"DELETE FROM game_data.map_metadata WHERE parent_entity_id = $1", region_id)
            await conn.execute(f"DELETE FROM game_data.world_regions WHERE region_id = $1", region_id)


@pytest.mark.asyncio
async def test_get_region_locations(db_connection, map_hierarchy_service, factory):
    """Region 내 Location 목록 조회 테스트"""
    test_id = uuid.uuid4().hex[:8]
    
    region_id = f"TEST_REG_{test_id}"
    location_id = f"TEST_LOC_{test_id}"
    
    try:
        # Region 및 Location 생성
        await factory.create_world_region(
            region_id=region_id,
            region_name="Test Region",
            region_type="empire"
        )
        
        await factory.create_world_location(
            location_id=location_id,
            region_id=region_id,
            location_name="Test Location"
        )
        
        # Location 위치 설정
        pin_id = f"PIN_{uuid.uuid4().hex[:8].upper()}"
        async with db_connection.acquire() as conn:
            await conn.execute("""
                INSERT INTO game_data.pin_positions
                (pin_id, pin_name, game_data_id, pin_type, x, y, icon_type, color, size)
                VALUES ($1, $2, $3, 'location', $4, $5, 'default', '#FF6B9D', 10)
                ON CONFLICT (game_data_id, pin_type) 
                DO UPDATE SET x = EXCLUDED.x, y = EXCLUDED.y
            """, pin_id, "Test Location Pin", location_id, 100.0, 200.0)
        
        # Location 목록 조회
        locations = await map_hierarchy_service.get_region_locations(region_id)
        
        assert len(locations) == 1
        assert locations[0]["location_id"] == location_id
        assert locations[0]["position"]["x"] == 100.0
        assert locations[0]["position"]["y"] == 200.0
    
    finally:
        # 테스트 데이터 정리
        async with db_connection.acquire() as conn:
            await conn.execute(f"DELETE FROM game_data.pin_positions WHERE game_data_id LIKE 'TEST_%{test_id}'")
            await conn.execute(f"DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)
            await conn.execute(f"DELETE FROM game_data.world_regions WHERE region_id = $1", region_id)


@pytest.mark.asyncio
async def test_place_location_in_region(db_connection, map_hierarchy_service, factory):
    """Region Map에 Location 배치 테스트"""
    test_id = uuid.uuid4().hex[:8]
    
    region_id = f"TEST_REG_{test_id}"
    location_id = f"TEST_LOC_{test_id}"
    
    try:
        # Region 및 Location 생성
        await factory.create_world_region(
            region_id=region_id,
            region_name="Test Region",
            region_type="empire"
        )
        
        await factory.create_world_location(
            location_id=location_id,
            region_id=region_id,
            location_name="Test Location"
        )
        
        # Location 배치
        result = await map_hierarchy_service.place_location_in_region(
            region_id,
            location_id,
            {"x": 150.0, "y": 250.0}
        )
        
        assert result["location_id"] == location_id
        assert result["position"]["x"] == 150.0
        assert result["position"]["y"] == 250.0
        assert result["status"] == "placed"
        
        # 위치 확인
        async with db_connection.acquire() as conn:
            pin = await conn.fetchrow("""
                SELECT x, y, pin_type
                FROM game_data.pin_positions
                WHERE game_data_id = $1 AND pin_type = 'location'
            """, location_id)
            
            assert pin is not None
            assert pin["x"] == 150.0
            assert pin["y"] == 250.0
    
    finally:
        # 테스트 데이터 정리
        async with db_connection.acquire() as conn:
            await conn.execute(f"DELETE FROM game_data.pin_positions WHERE game_data_id LIKE 'TEST_%{test_id}'")
            await conn.execute(f"DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)
            await conn.execute(f"DELETE FROM game_data.world_regions WHERE region_id = $1", region_id)


@pytest.mark.asyncio
async def test_get_location_map(db_connection, map_hierarchy_service, factory):
    """Location Map 조회 테스트"""
    test_id = uuid.uuid4().hex[:8]
    
    region_id = f"TEST_REG_{test_id}"
    location_id = f"TEST_LOC_{test_id}"
    
    try:
        # Region 및 Location 생성
        await factory.create_world_region(
            region_id=region_id,
            region_name="Test Region",
            region_type="empire"
        )
        
        await factory.create_world_location(
            location_id=location_id,
            region_id=region_id,
            location_name="Test Location"
        )
        
        # Location Map 조회 (기본값 반환)
        map_data = await map_hierarchy_service.get_location_map(location_id)
        
        assert map_data is not None
        assert map_data["map_level"] == "location"
        assert map_data["parent_entity_id"] == location_id
        assert map_data["parent_entity_type"] == "location"
        assert map_data["width"] == 800
        assert map_data["height"] == 800
    
    finally:
        # 테스트 데이터 정리
        async with db_connection.acquire() as conn:
            await conn.execute(f"DELETE FROM game_data.map_metadata WHERE parent_entity_id = $1", location_id)
            await conn.execute(f"DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)
            await conn.execute(f"DELETE FROM game_data.world_regions WHERE region_id = $1", region_id)


@pytest.mark.asyncio
async def test_get_location_cells(db_connection, map_hierarchy_service, factory):
    """Location 내 Cell 목록 조회 테스트"""
    test_id = uuid.uuid4().hex[:8]
    
    region_id = f"TEST_REG_{test_id}"
    location_id = f"TEST_LOC_{test_id}"
    cell_id = f"TEST_CELL_{test_id}"
    
    try:
        # Region, Location, Cell 생성
        await factory.create_world_region(
            region_id=region_id,
            region_name="Test Region",
            region_type="empire"
        )
        
        await factory.create_world_location(
            location_id=location_id,
            region_id=region_id,
            location_name="Test Location"
        )
        
        await factory.create_world_cell(
            cell_id=cell_id,
            location_id=location_id,
            cell_name="Test Cell",
            matrix_width=20,
            matrix_height=20
        )
        
        # Cell 위치 설정
        pin_id = f"PIN_{uuid.uuid4().hex[:8].upper()}"
        async with db_connection.acquire() as conn:
            await conn.execute("""
                INSERT INTO game_data.pin_positions
                (pin_id, pin_name, game_data_id, pin_type, x, y, icon_type, color, size)
                VALUES ($1, $2, $3, 'cell', $4, $5, 'default', '#FF6B9D', 10)
                ON CONFLICT (game_data_id, pin_type) 
                DO UPDATE SET x = EXCLUDED.x, y = EXCLUDED.y
            """, pin_id, "Test Cell Pin", cell_id, 50.0, 75.0)
        
        # Cell 목록 조회
        cells = await map_hierarchy_service.get_location_cells(location_id)
        
        assert len(cells) == 1
        assert cells[0]["cell_id"] == cell_id
        assert cells[0]["position"]["x"] == 50.0
        assert cells[0]["position"]["y"] == 75.0
    
    finally:
        # 테스트 데이터 정리
        async with db_connection.acquire() as conn:
            await conn.execute(f"DELETE FROM game_data.pin_positions WHERE game_data_id LIKE 'TEST_%{test_id}'")
            await conn.execute(f"DELETE FROM game_data.world_cells WHERE cell_id = $1", cell_id)
            await conn.execute(f"DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)
            await conn.execute(f"DELETE FROM game_data.world_regions WHERE region_id = $1", region_id)


@pytest.mark.asyncio
async def test_place_cell_in_location(db_connection, map_hierarchy_service, factory):
    """Location Map에 Cell 배치 테스트"""
    test_id = uuid.uuid4().hex[:8]
    
    region_id = f"TEST_REG_{test_id}"
    location_id = f"TEST_LOC_{test_id}"
    cell_id = f"TEST_CELL_{test_id}"
    
    try:
        # Region, Location, Cell 생성
        await factory.create_world_region(
            region_id=region_id,
            region_name="Test Region",
            region_type="empire"
        )
        
        await factory.create_world_location(
            location_id=location_id,
            region_id=region_id,
            location_name="Test Location"
        )
        
        await factory.create_world_cell(
            cell_id=cell_id,
            location_id=location_id,
            cell_name="Test Cell",
            matrix_width=20,
            matrix_height=20
        )
        
        # Cell 배치
        result = await map_hierarchy_service.place_cell_in_location(
            location_id,
            cell_id,
            {"x": 60.0, "y": 80.0}
        )
        
        assert result["cell_id"] == cell_id
        assert result["position"]["x"] == 60.0
        assert result["position"]["y"] == 80.0
        assert result["status"] == "placed"
        
        # 위치 확인
        async with db_connection.acquire() as conn:
            pin = await conn.fetchrow("""
                SELECT x, y, pin_type
                FROM game_data.pin_positions
                WHERE game_data_id = $1 AND pin_type = 'cell'
            """, cell_id)
            
            assert pin is not None
            assert pin["x"] == 60.0
            assert pin["y"] == 80.0
    
    finally:
        # 테스트 데이터 정리
        async with db_connection.acquire() as conn:
            await conn.execute(f"DELETE FROM game_data.pin_positions WHERE game_data_id LIKE 'TEST_%{test_id}'")
            await conn.execute(f"DELETE FROM game_data.world_cells WHERE cell_id = $1", cell_id)
            await conn.execute(f"DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)
            await conn.execute(f"DELETE FROM game_data.world_regions WHERE region_id = $1", region_id)


@pytest.mark.asyncio
async def test_update_map_metadata(db_connection, map_hierarchy_service, factory):
    """맵 메타데이터 업데이트 테스트"""
    test_id = uuid.uuid4().hex[:8]
    
    region_id = f"TEST_REG_{test_id}"
    
    try:
        # Region 생성
        await factory.create_world_region(
            region_id=region_id,
            region_name="Test Region",
            region_type="empire"
        )
        
        # 맵 메타데이터 업데이트
        metadata = {
            "map_name": "Custom Region Map",
            "width": 2000,
            "height": 1500,
            "background_color": "#000000",
            "grid_enabled": True,
            "grid_size": 100
        }
        
        result = await map_hierarchy_service.update_map_metadata(
            'region',
            region_id,
            'region',
            metadata
        )
        
        assert result is not None
        assert result["map_name"] == "Custom Region Map"
        assert result["width"] == 2000
        assert result["height"] == 1500
        
        # 데이터베이스에서 확인
        async with db_connection.acquire() as conn:
            map_row = await conn.fetchrow("""
                SELECT map_name, width, height, map_level, parent_entity_id
                FROM game_data.map_metadata
                WHERE parent_entity_id = $1 AND map_level = 'region'
            """, region_id)
            
            assert map_row is not None
            assert map_row["map_name"] == "Custom Region Map"
            assert map_row["width"] == 2000
    
    finally:
        # 테스트 데이터 정리
        async with db_connection.acquire() as conn:
            await conn.execute(f"DELETE FROM game_data.map_metadata WHERE parent_entity_id = $1", region_id)
            await conn.execute(f"DELETE FROM game_data.world_regions WHERE region_id = $1", region_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

