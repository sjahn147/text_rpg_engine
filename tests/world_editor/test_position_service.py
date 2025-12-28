"""
PositionService 단위 테스트
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
from app.world_editor.services.position_service import PositionService


@pytest_asyncio.fixture
async def db_connection():
    """데이터베이스 연결 픽스처"""
    db = DatabaseConnection()
    pool = await db.pool
    yield pool
    await db.close()


@pytest_asyncio.fixture
async def position_service():
    """PositionService 픽스처"""
    return PositionService()


@pytest_asyncio.fixture
async def factory():
    """GameDataFactory 픽스처"""
    return GameDataFactory()


@pytest.mark.asyncio
async def test_get_entities_by_cell(db_connection, position_service, factory):
    """Cell 내 Entity 목록 조회 테스트"""
    test_id = uuid.uuid4().hex[:8]
    
    cell_id = f"TEST_CELL_{test_id}"
    location_id = f"TEST_LOC_{test_id}"
    
    try:
        # Location 및 Cell 생성
        await factory.create_world_location(
            location_id=location_id,
            region_id="TEST_REG_001",
            location_name="Test Location"
        )
        
        await factory.create_world_cell(
            cell_id=cell_id,
            location_id=location_id,
            cell_name="Test Cell",
            matrix_width=20,
            matrix_height=20
        )
        
        # 여러 Entity 생성 (다른 위치에)
        for i in range(3):
            entity_id = f"TEST_NPC_{i}_{test_id}"
            await factory.create_npc_template(
                template_id=entity_id,
                name=f"Test NPC {i}",
                template_type="npc",
                base_stats={"hp": 100},
                base_properties={
                    "default_position_3d": {
                        "x": float(i * 2),
                        "y": float(i),
                        "z": 0.0,
                        "cell_id": cell_id
                    },
                    "entity_size": "medium"
                }
            )
        
        # Entity 목록 조회
        entities = await position_service.get_entities_by_cell(cell_id, sort_by_position=True)
        
        assert len(entities) == 3
        # y 좌표 내림차순으로 정렬되어야 함
        assert entities[0]["position"]["y"] >= entities[1]["position"]["y"]
        
        # 영역 필터 테스트
        area_filter = {"x_min": 0, "x_max": 2, "y_min": 0, "y_max": 2}
        filtered_entities = await position_service.get_entities_by_cell(
            cell_id,
            sort_by_position=True,
            area_filter=area_filter
        )
        
        # 필터링된 결과는 2개 이하여야 함
        assert len(filtered_entities) <= 2
    
    finally:
        # 테스트 데이터 정리
        async with db_connection.acquire() as conn:
            await conn.execute(f"DELETE FROM game_data.entities WHERE entity_id LIKE 'TEST_%{test_id}'")
            await conn.execute(f"DELETE FROM game_data.world_cells WHERE cell_id = $1", cell_id)
            await conn.execute(f"DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)


@pytest.mark.asyncio
async def test_get_entities_in_radius(db_connection, position_service, factory):
    """반경 내 Entity 조회 테스트"""
    test_id = uuid.uuid4().hex[:8]
    
    cell_id = f"TEST_CELL_{test_id}"
    location_id = f"TEST_LOC_{test_id}"
    
    try:
        # Location 및 Cell 생성
        await factory.create_world_location(
            location_id=location_id,
            region_id="TEST_REG_001",
            location_name="Test Location"
        )
        
        await factory.create_world_cell(
            cell_id=cell_id,
            location_id=location_id,
            cell_name="Test Cell",
            matrix_width=20,
            matrix_height=20
        )
        
        # 중심 위치 (5, 5) 주변에 Entity 배치
        center = {"x": 5.0, "y": 5.0, "z": 0.0}
        
        # 반경 내 Entity (거리 1.0)
        entity1_id = f"TEST_NPC_1_{test_id}"
        await factory.create_npc_template(
            template_id=entity1_id,
            name="Test NPC 1",
            template_type="npc",
            base_stats={"hp": 100},
            base_properties={
                "default_position_3d": {
                    "x": 5.0,
                    "y": 6.0,  # 거리 1.0
                    "z": 0.0,
                    "cell_id": cell_id
                },
                "entity_size": "medium"
            }
        )
        
        # 반경 밖 Entity (거리 3.0)
        entity2_id = f"TEST_NPC_2_{test_id}"
        await factory.create_npc_template(
            template_id=entity2_id,
            name="Test NPC 2",
            template_type="npc",
            base_stats={"hp": 100},
            base_properties={
                "default_position_3d": {
                    "x": 5.0,
                    "y": 8.0,  # 거리 3.0
                    "z": 0.0,
                    "cell_id": cell_id
                },
                "entity_size": "medium"
            }
        )
        
        # 반경 2.0 내 Entity 조회
        entities = await position_service.get_entities_in_radius(
            cell_id, center, radius=2.0
        )
        
        # 반경 내 Entity는 1개여야 함
        assert len(entities) == 1
        assert entities[0]["entity_id"] == entity1_id
        assert entities[0]["distance"] <= 2.0
    
    finally:
        # 테스트 데이터 정리
        async with db_connection.acquire() as conn:
            await conn.execute(f"DELETE FROM game_data.entities WHERE entity_id LIKE 'TEST_%{test_id}'")
            await conn.execute(f"DELETE FROM game_data.world_cells WHERE cell_id = $1", cell_id)
            await conn.execute(f"DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)


@pytest.mark.asyncio
async def test_get_world_objects_by_cell(db_connection, position_service, factory):
    """Cell 내 World Object 목록 조회 테스트"""
    test_id = uuid.uuid4().hex[:8]
    
    cell_id = f"TEST_CELL_{test_id}"
    location_id = f"TEST_LOC_{test_id}"
    
    try:
        # Location 및 Cell 생성
        await factory.create_world_location(
            location_id=location_id,
            region_id="TEST_REG_001",
            location_name="Test Location"
        )
        
        await factory.create_world_cell(
            cell_id=cell_id,
            location_id=location_id,
            cell_name="Test Cell",
            matrix_width=20,
            matrix_height=20
        )
        
        # 여러 World Object 생성
        for i in range(2):
            object_id = f"TEST_OBJ_{i}_{test_id}"
            await factory.create_world_object(
                object_id=object_id,
                object_type="interactive",
                object_name=f"Test Object {i}",
                default_cell_id=cell_id,
                default_position={"x": float(i * 2), "y": float(i)},
                object_width=1.0,
                object_depth=1.0,
                object_height=1.0
            )
        
        # World Object 목록 조회
        objects = await position_service.get_world_objects_by_cell(cell_id, sort_by_position=True)
        
        assert len(objects) == 2
        # y 좌표 내림차순으로 정렬되어야 함
        assert objects[0]["position"]["y"] >= objects[1]["position"]["y"]
    
    finally:
        # 테스트 데이터 정리
        async with db_connection.acquire() as conn:
            await conn.execute(f"DELETE FROM game_data.world_objects WHERE object_id LIKE 'TEST_%{test_id}'")
            await conn.execute(f"DELETE FROM game_data.world_cells WHERE cell_id = $1", cell_id)
            await conn.execute(f"DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

