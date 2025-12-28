"""
InteractionService 단위 테스트
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
from app.world_editor.services.interaction_service import InteractionService


@pytest_asyncio.fixture
async def db_connection():
    """데이터베이스 연결 픽스처"""
    db = DatabaseConnection()
    pool = await db.pool
    yield pool
    await db.close()


@pytest_asyncio.fixture
async def interaction_service():
    """InteractionService 픽스처"""
    return InteractionService()


@pytest_asyncio.fixture
async def factory():
    """GameDataFactory 픽스처"""
    return GameDataFactory()


@pytest.mark.asyncio
async def test_can_entity_pass_through(db_connection, interaction_service, factory):
    """Entity 통과 가능 여부 테스트"""
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
        
        # Entity 생성
        entity_id = f"TEST_NPC_{test_id}"
        await factory.create_npc_template(
            template_id=entity_id,
            name="Test NPC",
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
        
        # 통과 가능한 객체 생성
        passable_object_id = f"TEST_OBJ_PASSABLE_{test_id}"
        await factory.create_world_object(
            object_id=passable_object_id,
            object_type="interactive",
            object_name="Passable Object",
            default_cell_id=cell_id,
            default_position={"x": 5.0, "y": 5.0},
            passable=True
        )
        
        # 통과 불가능한 객체 생성
        non_passable_object_id = f"TEST_OBJ_NON_PASSABLE_{test_id}"
        await factory.create_world_object(
            object_id=non_passable_object_id,
            object_type="interactive",
            object_name="Non-Passable Object",
            default_cell_id=cell_id,
            default_position={"x": 10.0, "y": 10.0},
            passable=False
        )
        
        # 통과 가능한 객체 테스트
        result1 = await interaction_service.can_entity_pass_through(entity_id, passable_object_id)
        assert result1["can_pass"] == True
        assert result1["object_info"]["passable"] == True
        
        # 통과 불가능한 객체 테스트
        result2 = await interaction_service.can_entity_pass_through(entity_id, non_passable_object_id)
        assert result2["can_pass"] == False
        assert result2["object_info"]["passable"] == False
    
    finally:
        # 테스트 데이터 정리
        async with db_connection.acquire() as conn:
            await conn.execute(f"DELETE FROM game_data.entities WHERE entity_id LIKE 'TEST_%{test_id}'")
            await conn.execute(f"DELETE FROM game_data.world_objects WHERE object_id LIKE 'TEST_%{test_id}'")
            await conn.execute(f"DELETE FROM game_data.world_cells WHERE cell_id = $1", cell_id)
            await conn.execute(f"DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)


@pytest.mark.asyncio
async def test_can_entity_move_object(db_connection, interaction_service, factory):
    """Entity 객체 이동 가능 여부 테스트"""
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
        
        # 강한 Entity 생성 (힘 20)
        strong_entity_id = f"TEST_NPC_STRONG_{test_id}"
        await factory.create_npc_template(
            template_id=strong_entity_id,
            name="Strong NPC",
            template_type="npc",
            base_stats={"hp": 100, "strength": 20},
            base_properties={
                "default_position_3d": {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0,
                    "cell_id": cell_id
                },
                "entity_size": "large"  # 크기 보정으로 힘 증가
            }
        )
        
        # 약한 Entity 생성 (힘 5)
        weak_entity_id = f"TEST_NPC_WEAK_{test_id}"
        await factory.create_npc_template(
            template_id=weak_entity_id,
            name="Weak NPC",
            template_type="npc",
            base_stats={"hp": 100, "strength": 5},
            base_properties={
                "default_position_3d": {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0,
                    "cell_id": cell_id
                },
                "entity_size": "small"  # 크기 보정으로 힘 감소
            }
        )
        
        # 이동 가능한 가벼운 객체 생성 (무게 10)
        light_object_id = f"TEST_OBJ_LIGHT_{test_id}"
        await factory.create_world_object(
            object_id=light_object_id,
            object_type="interactive",
            object_name="Light Object",
            default_cell_id=cell_id,
            default_position={"x": 5.0, "y": 5.0},
            movable=True,
            object_weight=10.0
        )
        
        # 이동 가능한 무거운 객체 생성 (무게 50)
        heavy_object_id = f"TEST_OBJ_HEAVY_{test_id}"
        await factory.create_world_object(
            object_id=heavy_object_id,
            object_type="interactive",
            object_name="Heavy Object",
            default_cell_id=cell_id,
            default_position={"x": 10.0, "y": 10.0},
            movable=True,
            object_weight=50.0
        )
        
        # 이동 불가능한 객체 생성
        immovable_object_id = f"TEST_OBJ_IMMOVABLE_{test_id}"
        await factory.create_world_object(
            object_id=immovable_object_id,
            object_type="interactive",
            object_name="Immovable Object",
            default_cell_id=cell_id,
            default_position={"x": 15.0, "y": 15.0},
            movable=False,
            object_weight=0.0
        )
        
        # 강한 Entity가 가벼운 객체 이동
        result1 = await interaction_service.can_entity_move_object(strong_entity_id, light_object_id)
        assert result1["can_move"] == True
        
        # 강한 Entity가 무거운 객체 이동
        result2 = await interaction_service.can_entity_move_object(strong_entity_id, heavy_object_id)
        # large 크기 보정 (1.5) * 힘 20 = 30, 무게 50보다 작으므로 False
        assert result2["can_move"] == False
        
        # 약한 Entity가 가벼운 객체 이동
        result3 = await interaction_service.can_entity_move_object(weak_entity_id, light_object_id)
        # small 크기 보정 (0.75) * 힘 5 = 3.75, 무게 10보다 작으므로 False
        assert result3["can_move"] == False
        
        # 이동 불가능한 객체
        result4 = await interaction_service.can_entity_move_object(strong_entity_id, immovable_object_id)
        assert result4["can_move"] == False
    
    finally:
        # 테스트 데이터 정리
        async with db_connection.acquire() as conn:
            await conn.execute(f"DELETE FROM game_data.entities WHERE entity_id LIKE 'TEST_%{test_id}'")
            await conn.execute(f"DELETE FROM game_data.world_objects WHERE object_id LIKE 'TEST_%{test_id}'")
            await conn.execute(f"DELETE FROM game_data.world_cells WHERE cell_id = $1", cell_id)
            await conn.execute(f"DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)


@pytest.mark.asyncio
async def test_validate_wall_mounted_placement(db_connection, interaction_service, factory):
    """벽 부착 객체 배치 검증 테스트"""
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
        
        # 벽 부착 객체 생성
        wall_object_id = f"TEST_OBJ_WALL_{test_id}"
        await factory.create_world_object(
            object_id=wall_object_id,
            object_type="interactive",
            object_name="Wall Object",
            default_cell_id=cell_id,
            default_position={"x": 0.3, "y": 0.3},  # 벽 근처
            wall_mounted=True
        )
        
        # 벽 부착이 아닌 객체 생성
        non_wall_object_id = f"TEST_OBJ_NON_WALL_{test_id}"
        await factory.create_world_object(
            object_id=non_wall_object_id,
            object_type="interactive",
            object_name="Non-Wall Object",
            default_cell_id=cell_id,
            default_position={"x": 10.0, "y": 10.0},
            wall_mounted=False
        )
        
        # 벽 근처 배치 (유효)
        result1 = await interaction_service.validate_wall_mounted_placement(
            wall_object_id,
            {"x": 0.3, "y": 0.3, "z": 0.0},
            cell_id
        )
        assert result1["valid"] == True
        
        # 벽에서 멀리 배치 (무효)
        result2 = await interaction_service.validate_wall_mounted_placement(
            wall_object_id,
            {"x": 10.0, "y": 10.0, "z": 0.0},
            cell_id
        )
        assert result2["valid"] == False
        assert len(result2["suggestions"]) > 0
        
        # 벽 부착이 아닌 객체는 항상 유효
        result3 = await interaction_service.validate_wall_mounted_placement(
            non_wall_object_id,
            {"x": 10.0, "y": 10.0, "z": 0.0},
            cell_id
        )
        assert result3["valid"] == True
    
    finally:
        # 테스트 데이터 정리
        async with db_connection.acquire() as conn:
            await conn.execute(f"DELETE FROM game_data.world_objects WHERE object_id LIKE 'TEST_%{test_id}'")
            await conn.execute(f"DELETE FROM game_data.world_cells WHERE cell_id = $1", cell_id)
            await conn.execute(f"DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

