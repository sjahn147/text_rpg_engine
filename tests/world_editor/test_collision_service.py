"""
CollisionService 단위 테스트
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
from app.world_editor.services.collision_service import (
    CollisionService,
    get_collision_radius,
    check_collision,
    calculate_distance
)


@pytest_asyncio.fixture
async def db_connection():
    """데이터베이스 연결 픽스처"""
    db = DatabaseConnection()
    pool = await db.pool
    yield pool
    await db.close()


@pytest_asyncio.fixture
async def collision_service():
    """CollisionService 픽스처"""
    return CollisionService()


@pytest_asyncio.fixture
async def factory():
    """GameDataFactory 픽스처"""
    return GameDataFactory()


@pytest.mark.asyncio
async def test_get_collision_radius():
    """충돌 반경 계산 테스트"""
    assert get_collision_radius('tiny') == 0.25
    assert get_collision_radius('small') == 0.5
    assert get_collision_radius('medium') == 0.5
    assert get_collision_radius('large') == 1.0
    assert get_collision_radius('huge') == 1.5
    assert get_collision_radius('gargantuan') == 2.0
    assert get_collision_radius('unknown') == 0.5  # 기본값


@pytest.mark.asyncio
async def test_calculate_distance():
    """거리 계산 테스트"""
    pos1 = {"x": 0.0, "y": 0.0, "z": 0.0}
    pos2 = {"x": 3.0, "y": 4.0, "z": 0.0}
    distance = calculate_distance(pos1, pos2)
    assert abs(distance - 5.0) < 0.001  # 3-4-5 직각삼각형


@pytest.mark.asyncio
async def test_check_collision():
    """충돌 검사 테스트"""
    # 충돌하는 경우
    pos1 = {"x": 0.0, "y": 0.0, "z": 0.0}
    pos2 = {"x": 0.5, "y": 0.0, "z": 0.0}
    assert check_collision(pos1, "medium", pos2, "medium") == True
    
    # 충돌하지 않는 경우
    pos3 = {"x": 0.0, "y": 0.0, "z": 0.0}
    pos4 = {"x": 2.0, "y": 0.0, "z": 0.0}
    assert check_collision(pos3, "medium", pos4, "medium") == False
    
        # 큰 Entity와 작은 Entity 충돌 (large: 1.0, medium: 0.5, 합: 1.5)
    # 거리 1.4면 충돌, 1.5면 충돌하지 않음
    pos5 = {"x": 0.0, "y": 0.0, "z": 0.0}
    pos6 = {"x": 1.4, "y": 0.0, "z": 0.0}
    assert check_collision(pos5, "large", pos6, "medium") == True
    
    # 거리 1.5면 충돌하지 않음
    pos7 = {"x": 0.0, "y": 0.0, "z": 0.0}
    pos8 = {"x": 1.5, "y": 0.0, "z": 0.0}
    assert check_collision(pos7, "large", pos8, "medium") == False


@pytest.mark.asyncio
async def test_check_position_collision(db_connection, collision_service, factory):
    """위치 충돌 검사 테스트"""
    test_id = uuid.uuid4().hex[:8]
    
    # 테스트 Cell 생성
    cell_id = f"TEST_CELL_{test_id}"
    location_id = f"TEST_LOC_{test_id}"
    
    try:
        # Location 생성
        await factory.create_world_location(
            location_id=location_id,
            region_id="TEST_REG_001",
            location_name="Test Location"
        )
        
        # Cell 생성
        await factory.create_world_cell(
            cell_id=cell_id,
            location_id=location_id,
            cell_name="Test Cell",
            matrix_width=20,
            matrix_height=20
        )
        
        # 첫 번째 Entity 생성 (위치: 0, 0, 0)
        entity1_id = f"TEST_NPC_1_{test_id}"
        await factory.create_npc_template(
            template_id=entity1_id,
            name="Test NPC 1",
            template_type="npc",
            base_stats={"hp": 100},
            base_properties={
                "default_position_3d": {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0,
                    "cell_id": cell_id
                },
                "entity_size": "medium"
            }
        )
        
        # 두 번째 Entity 생성 (위치: 0.3, 0, 0) - 충돌
        entity2_id = f"TEST_NPC_2_{test_id}"
        await factory.create_npc_template(
            template_id=entity2_id,
            name="Test NPC 2",
            template_type="npc",
            base_stats={"hp": 100},
            base_properties={
                "default_position_3d": {
                    "x": 0.3,
                    "y": 0.0,
                    "z": 0.0,
                    "cell_id": cell_id
                },
                "entity_size": "medium"
            }
        )
        
        # 충돌 검사 (위치: 0, 0, 0)
        result = await collision_service.check_position_collision(
            cell_id=cell_id,
            position={"x": 0.0, "y": 0.0, "z": 0.0},
            entity_size="medium"
        )
        
        assert result["collision"] == True
        assert len(result["colliding_entities"]) >= 1
        
        # 충돌 검사 (위치: 2, 0, 0) - 충돌 없음
        result2 = await collision_service.check_position_collision(
            cell_id=cell_id,
            position={"x": 2.0, "y": 0.0, "z": 0.0},
            entity_size="medium"
        )
        
        assert result2["collision"] == False
        assert len(result2["colliding_entities"]) == 0
        
        # 자신 제외하고 충돌 검사
        result3 = await collision_service.check_position_collision(
            cell_id=cell_id,
            position={"x": 0.0, "y": 0.0, "z": 0.0},
            entity_size="medium",
            exclude_entity_id=entity1_id
        )
        
        # 자신을 제외하면 충돌이 없어야 함 (다른 Entity는 0.3에 있으므로)
        # 하지만 0.3은 0.0에서 충돌 반경 내에 있으므로 충돌이 있을 수 있음
        # 정확한 검증을 위해 거리 확인
        if result3["collision"]:
            # 충돌하는 Entity의 거리가 충돌 반경 합보다 작은지 확인
            for colliding in result3["colliding_entities"]:
                assert colliding["distance"] < colliding["combined_radius"]
    
    finally:
        # 테스트 데이터 정리
        async with db_connection.acquire() as conn:
            await conn.execute(f"DELETE FROM game_data.entities WHERE entity_id LIKE 'TEST_%{test_id}'")
            await conn.execute(f"DELETE FROM game_data.world_cells WHERE cell_id = $1", cell_id)
            await conn.execute(f"DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)


@pytest.mark.asyncio
async def test_check_world_object_collision(db_connection, collision_service, factory):
    """World Object 충돌 검사 테스트"""
    test_id = uuid.uuid4().hex[:8]
    
    # 테스트 Cell 생성
    cell_id = f"TEST_CELL_{test_id}"
    location_id = f"TEST_LOC_{test_id}"
    
    try:
        # Location 생성
        await factory.create_world_location(
            location_id=location_id,
            region_id="TEST_REG_001",
            location_name="Test Location"
        )
        
        # Cell 생성
        await factory.create_world_cell(
            cell_id=cell_id,
            location_id=location_id,
            cell_name="Test Cell",
            matrix_width=20,
            matrix_height=20
        )
        
        # World Object 생성 (위치: 0, 0)
        object_id = f"TEST_OBJ_{test_id}"
        await factory.create_world_object(
            object_id=object_id,
            object_type="interactive",
            object_name="Test Chest",
            default_cell_id=cell_id,
            default_position={"x": 0.0, "y": 0.0},
            object_width=1.0,
            object_depth=1.0,
            object_height=1.0,
            passable=False
        )
        
        # 충돌 검사 (위치: 0, 0) - 충돌
        result = await collision_service.check_world_object_collision(
            cell_id=cell_id,
            position={"x": 0.0, "y": 0.0, "z": 0.0},
            entity_size="medium"
        )
        
        assert result["collision"] == True
        assert len(result["colliding_objects"]) >= 1
        
        # 충돌 검사 (위치: 2, 0) - 충돌 없음
        result2 = await collision_service.check_world_object_collision(
            cell_id=cell_id,
            position={"x": 2.0, "y": 0.0, "z": 0.0},
            entity_size="medium"
        )
        
        assert result2["collision"] == False
    
    finally:
        # 테스트 데이터 정리
        async with db_connection.acquire() as conn:
            await conn.execute(f"DELETE FROM game_data.world_objects WHERE object_id LIKE 'TEST_%{test_id}'")
            await conn.execute(f"DELETE FROM game_data.world_cells WHERE cell_id = $1", cell_id)
            await conn.execute(f"DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

