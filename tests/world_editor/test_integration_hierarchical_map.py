"""
계층적 맵 시스템 통합 테스트

Region → Location → Cell → Entity 전체 워크플로우 테스트
"""
import pytest
import pytest_asyncio
from pathlib import Path
import sys
import uuid
import json

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from database.connection import DatabaseConnection
from database.factories.game_data_factory import GameDataFactory
from app.world_editor.services.map_hierarchy_service import MapHierarchyService
from app.world_editor.services.position_service import PositionService
from app.world_editor.services.collision_service import CollisionService


@pytest_asyncio.fixture
async def db_connection():
    """데이터베이스 연결 픽스처"""
    db = DatabaseConnection()
    pool = await db.pool
    yield pool
    await db.close()


@pytest_asyncio.fixture
async def factory():
    """GameDataFactory 픽스처"""
    return GameDataFactory()


@pytest_asyncio.fixture
async def map_hierarchy_service():
    """MapHierarchyService 픽스처"""
    return MapHierarchyService()


@pytest_asyncio.fixture
async def position_service():
    """PositionService 픽스처"""
    return PositionService()


@pytest_asyncio.fixture
async def collision_service():
    """CollisionService 픽스처"""
    return CollisionService()


@pytest.mark.asyncio
async def test_full_hierarchical_workflow(
    db_connection,
    factory,
    map_hierarchy_service,
    position_service,
    collision_service
):
    """
    전체 계층적 맵 워크플로우 테스트
    
    Region 생성 → Location 배치 → Cell 배치 → Entity 배치 → 충돌 검사
    """
    test_id = uuid.uuid4().hex[:8]
    
    region_id = f"TEST_REG_{test_id}"
    location_id = f"TEST_LOC_{test_id}"
    cell_id = f"TEST_CELL_{test_id}"
    entity_id = f"TEST_ENTITY_{test_id}"
    
    try:
        # 1. Region 생성
        await factory.create_world_region(
            region_id=region_id,
            region_name="Test Region",
            region_type="empire"
        )
        
        # 2. Location 생성 및 Region Map에 배치
        await factory.create_world_location(
            location_id=location_id,
            region_id=region_id,
            location_name="Test Location"
        )
        
        location_position = {"x": 100.0, "y": 200.0}
        await map_hierarchy_service.place_location_in_region(
            region_id,
            location_id,
            location_position
        )
        
        # Location 위치 확인
        locations = await map_hierarchy_service.get_region_locations(region_id)
        assert len(locations) == 1
        assert locations[0]["location_id"] == location_id
        assert locations[0]["position"]["x"] == 100.0
        assert locations[0]["position"]["y"] == 200.0
        
        # 3. Cell 생성 및 Location Map에 배치
        await factory.create_world_cell(
            cell_id=cell_id,
            location_id=location_id,
            cell_name="Test Cell",
            matrix_width=20,
            matrix_height=20
        )
        
        cell_position = {"x": 50.0, "y": 75.0}
        await map_hierarchy_service.place_cell_in_location(
            location_id,
            cell_id,
            cell_position
        )
        
        # Cell 위치 확인
        cells = await map_hierarchy_service.get_location_cells(location_id)
        assert len(cells) == 1
        assert cells[0]["cell_id"] == cell_id
        assert cells[0]["position"]["x"] == 50.0
        assert cells[0]["position"]["y"] == 75.0
        
        # 4. Entity 생성 및 Cell에 배치
        await factory.create_npc_template(
            template_id=entity_id,
            name="Test NPC",
            template_type="npc",
            base_stats={"health": 100, "mana": 50},
            base_properties={},
            behavior_properties={}
        )
        
        # Entity 위치 설정
        entity_position = {
            "x": 5.0,
            "y": 4.0,
            "z": 0.0,
            "rotation_y": 0,
            "cell_id": cell_id
        }
        
        async with db_connection.acquire() as conn:
            await conn.execute("""
                UPDATE game_data.entities
                SET default_position_3d = $1::jsonb, entity_size = $2
                WHERE entity_id = $3
            """, json.dumps(entity_position), "medium", entity_id)
        
        # Entity 위치 확인
        entities = await position_service.get_entities_by_cell(cell_id)
        assert len(entities) == 1
        assert entities[0]["entity_id"] == entity_id
        # PositionService는 "position" 키를 사용
        pos = entities[0].get("position")
        assert pos is not None, f"Entity position is None: {entities[0]}"
        assert pos.get("x") == 5.0, f"Expected x=5.0, got {pos}"
        
        # 5. 충돌 검사
        collision_result = await collision_service.check_position_collision(
            cell_id,
            {"x": 5.0, "y": 4.0, "z": 0.0},
            "medium",
            exclude_entity_id=entity_id
        )
        # CollisionService는 dict를 반환
        assert collision_result["collision"] == False
        
        # 충돌하는 위치 테스트 (같은 위치)
        collision_result2 = await collision_service.check_position_collision(
            cell_id,
            {"x": 5.0, "y": 4.0, "z": 0.0},
            "medium",
            exclude_entity_id=None  # 자기 자신과 충돌 검사
        )
        assert collision_result2["collision"] == True
        
        print("✅ 전체 계층적 맵 워크플로우 테스트 통과")
    
    finally:
        # 테스트 데이터 정리
        async with db_connection.acquire() as conn:
            await conn.execute(f"DELETE FROM game_data.pin_positions WHERE game_data_id LIKE 'TEST_%{test_id}'")
            await conn.execute(f"DELETE FROM game_data.entities WHERE entity_id = $1", entity_id)
            await conn.execute(f"DELETE FROM game_data.world_cells WHERE cell_id = $1", cell_id)
            await conn.execute(f"DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)
            await conn.execute(f"DELETE FROM game_data.world_regions WHERE region_id = $1", region_id)


@pytest.mark.asyncio
async def test_region_map_metadata_update(
    db_connection,
    factory,
    map_hierarchy_service
):
    """Region Map 메타데이터 업데이트 통합 테스트"""
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
        
        assert result["map_name"] == "Custom Region Map"
        assert result["width"] == 2000
        assert result["height"] == 1500
        
        # 다시 조회하여 확인
        map_data = await map_hierarchy_service.get_region_map(region_id)
        assert map_data["map_name"] == "Custom Region Map"
        assert map_data["width"] == 2000
        
        print("✅ Region Map 메타데이터 업데이트 테스트 통과")
    
    finally:
        async with db_connection.acquire() as conn:
            await conn.execute(f"DELETE FROM game_data.map_metadata WHERE parent_entity_id = $1", region_id)
            await conn.execute(f"DELETE FROM game_data.world_regions WHERE region_id = $1", region_id)


@pytest.mark.asyncio
async def test_location_cell_batch_placement(
    db_connection,
    factory,
    map_hierarchy_service
):
    """Location에 여러 Cell 배치 통합 테스트"""
    test_id = uuid.uuid4().hex[:8]
    
    region_id = f"TEST_REG_{test_id}"
    location_id = f"TEST_LOC_{test_id}"
    cell_ids = [f"TEST_CELL_{test_id}_{i}" for i in range(3)]
    
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
        
        # 여러 Cell 생성 및 배치
        positions = [
            {"x": 50.0, "y": 50.0},
            {"x": 150.0, "y": 50.0},
            {"x": 100.0, "y": 150.0},
        ]
        
        for i, cell_id in enumerate(cell_ids):
            await factory.create_world_cell(
                cell_id=cell_id,
                location_id=location_id,
                cell_name=f"Test Cell {i+1}",
                matrix_width=20,
                matrix_height=20
            )
            
            await map_hierarchy_service.place_cell_in_location(
                location_id,
                cell_id,
                positions[i]
            )
        
        # 모든 Cell 위치 확인
        cells = await map_hierarchy_service.get_location_cells(location_id)
        assert len(cells) == 3
        
        for i, cell in enumerate(cells):
            assert cell["position"]["x"] == positions[i]["x"]
            assert cell["position"]["y"] == positions[i]["y"]
        
        print("✅ Location에 여러 Cell 배치 테스트 통과")
    
    finally:
        async with db_connection.acquire() as conn:
            await conn.execute(f"DELETE FROM game_data.pin_positions WHERE game_data_id LIKE 'TEST_%{test_id}%'")
            for cell_id in cell_ids:
                await conn.execute(f"DELETE FROM game_data.world_cells WHERE cell_id = $1", cell_id)
            await conn.execute(f"DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)
            await conn.execute(f"DELETE FROM game_data.world_regions WHERE region_id = $1", region_id)


@pytest.mark.asyncio
async def test_entity_position_query_performance(
    db_connection,
    factory,
    position_service
):
    """Entity 위치 쿼리 성능 테스트"""
    test_id = uuid.uuid4().hex[:8]
    
    region_id = f"TEST_REG_{test_id}"
    location_id = f"TEST_LOC_{test_id}"
    cell_id = f"TEST_CELL_{test_id}"
    entity_ids = [f"TEST_ENTITY_{test_id}_{i}" for i in range(10)]
    
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
        
        # 여러 Entity 생성 및 위치 설정
        import time
        start_time = time.time()
        
        async with db_connection.acquire() as conn:
            for i, entity_id in enumerate(entity_ids):
                await factory.create_npc_template(
                    template_id=entity_id,
                    name=f"Test NPC {i+1}",
                    template_type="npc",
                    base_stats={"health": 100, "mana": 50},
                    base_properties={},
                    behavior_properties={}
                )
                
                entity_position = {
                    "x": float(i % 5),
                    "y": float(i // 5),
                    "z": 0.0,
                    "rotation_y": 0,
                    "cell_id": cell_id
                }
                
                await conn.execute("""
                    UPDATE game_data.entities
                    SET default_position_3d = $1::jsonb, entity_size = $2
                    WHERE entity_id = $3
                """, json.dumps(entity_position), "medium", entity_id)
        
        creation_time = time.time() - start_time
        print(f"Entity 생성 시간: {creation_time:.3f}초")
        
        # 위치 쿼리 성능 테스트
        start_time = time.time()
        entities = await position_service.get_entities_by_cell(cell_id)
        query_time = time.time() - start_time
        
        assert len(entities) == 10
        print(f"Entity 위치 쿼리 시간: {query_time:.3f}초")
        
        # 반경 내 Entity 조회 성능 테스트
        start_time = time.time()
        entities_in_radius = await position_service.get_entities_in_radius(
            cell_id,
            {"x": 2.0, "y": 2.0, "z": 0.0},
            2.0
        )
        radius_query_time = time.time() - start_time
        
        print(f"반경 내 Entity 조회 시간: {radius_query_time:.3f}초")
        
        # 성능 검증 (쿼리가 1초 이내에 완료되어야 함)
        assert query_time < 1.0, f"쿼리가 너무 느립니다: {query_time:.3f}초"
        assert radius_query_time < 1.0, f"반경 쿼리가 너무 느립니다: {radius_query_time:.3f}초"
        
        print("✅ Entity 위치 쿼리 성능 테스트 통과")
    
    finally:
        async with db_connection.acquire() as conn:
            for entity_id in entity_ids:
                await conn.execute(f"DELETE FROM game_data.entities WHERE entity_id = $1", entity_id)
            await conn.execute(f"DELETE FROM game_data.world_cells WHERE cell_id = $1", cell_id)
            await conn.execute(f"DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)
            await conn.execute(f"DELETE FROM game_data.world_regions WHERE region_id = $1", region_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

