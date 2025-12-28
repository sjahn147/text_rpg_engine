"""
Phase 2: GameDataFactory 확장 단위 테스트

새로운 필드 지원 (default_position_3d, entity_size, world_object properties) 검증
"""
import pytest
import pytest_asyncio
import asyncio
from pathlib import Path
import sys

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from database.connection import DatabaseConnection
from database.factories.game_data_factory import GameDataFactory


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


@pytest.mark.asyncio
async def test_create_npc_with_position_and_size(db_connection, factory):
    """NPC 생성 시 default_position_3d와 entity_size가 올바르게 저장되는지 확인"""
    template_id = "TEST_NPC_POSITION_001"
    
    default_position_3d = {
        "x": 5.0,
        "y": 4.0,
        "z": 0.0,
        "rotation_y": 90,
        "cell_id": "CELL_TEST_001"
    }
    
    base_properties = {
        "default_position_3d": default_position_3d,
        "entity_size": "large"
    }
    
    try:
        # NPC 생성
        result_id = await factory.create_npc_template(
            template_id=template_id,
            name="Test NPC with Position",
            template_type="merchant",
            base_stats={"hp": 100, "mp": 50},
            base_properties=base_properties
        )
        
        assert result_id == template_id
        
        # 데이터베이스에서 확인
        async with db_connection.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT default_position_3d, entity_size
                FROM game_data.entities
                WHERE entity_id = $1
            """, template_id)
            
            assert row is not None
            assert row['entity_size'] == 'large'
            
            import json
            stored_position = json.loads(row['default_position_3d']) if row['default_position_3d'] else None
            assert stored_position is not None
            assert stored_position['x'] == 5.0
            assert stored_position['y'] == 4.0
            assert stored_position['z'] == 0.0
            assert stored_position['rotation_y'] == 90
            assert stored_position['cell_id'] == "CELL_TEST_001"
    
    finally:
        # 테스트 데이터 정리
        async with db_connection.acquire() as conn:
            await conn.execute("DELETE FROM game_data.entities WHERE entity_id = $1", template_id)


@pytest.mark.asyncio
async def test_create_npc_with_default_size(db_connection, factory):
    """NPC 생성 시 entity_size가 없으면 기본값 'medium'이 설정되는지 확인"""
    template_id = "TEST_NPC_DEFAULT_SIZE_001"
    
    try:
        # entity_size 없이 NPC 생성
        result_id = await factory.create_npc_template(
            template_id=template_id,
            name="Test NPC Default Size",
            template_type="merchant",
            base_stats={"hp": 100, "mp": 50},
            base_properties={}  # entity_size 없음
        )
        
        assert result_id == template_id
        
        # 데이터베이스에서 확인
        async with db_connection.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT entity_size
                FROM game_data.entities
                WHERE entity_id = $1
            """, template_id)
            
            assert row is not None
            assert row['entity_size'] == 'medium'  # 기본값
    
    finally:
        # 테스트 데이터 정리
        async with db_connection.acquire() as conn:
            await conn.execute("DELETE FROM game_data.entities WHERE entity_id = $1", template_id)


@pytest.mark.asyncio
async def test_create_player_with_position_and_size(db_connection, factory):
    """Player 생성 시 default_position_3d와 entity_size가 올바르게 저장되는지 확인"""
    template_id = "TEST_PLAYER_POSITION_001"
    
    default_position_3d = {
        "x": 10.0,
        "y": 8.0,
        "z": 0.0,
        "rotation_y": 0,
        "cell_id": "CELL_START_001"
    }
    
    base_properties = {
        "default_position_3d": default_position_3d,
        "entity_size": "medium"
    }
    
    try:
        # Player 생성
        result_id = await factory.create_player_template(
            template_id=template_id,
            name="Test Player",
            base_stats={"hp": 150, "mp": 100},
            base_properties=base_properties
        )
        
        assert result_id == template_id
        
        # 데이터베이스에서 확인
        async with db_connection.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT default_position_3d, entity_size
                FROM game_data.entities
                WHERE entity_id = $1
            """, template_id)
            
            assert row is not None
            assert row['entity_size'] == 'medium'
            
            import json
            stored_position = json.loads(row['default_position_3d']) if row['default_position_3d'] else None
            assert stored_position is not None
            assert stored_position['x'] == 10.0
            assert stored_position['y'] == 8.0
    
    finally:
        # 테스트 데이터 정리
        async with db_connection.acquire() as conn:
            await conn.execute("DELETE FROM game_data.entities WHERE entity_id = $1", template_id)


@pytest.mark.asyncio
async def test_create_world_object_with_properties(db_connection, factory):
    """World Object 생성 시 새로운 properties가 올바르게 저장되는지 확인"""
    object_id = "TEST_OBJ_DOOR_001"
    region_id = "TEST_REGION_001"
    location_id = "TEST_LOCATION_001"
    cell_id = "CELL_TEST_001"
    
    default_position = {"x": 5.0, "y": 3.0}
    possible_states = {"closed": True, "open": False}
    properties = {"material": "wood", "durability": 100}
    
    try:
        # 필요한 Region, Location, Cell 먼저 생성
        await factory.create_world_region(
            region_id=region_id,
            region_name="Test Region"
        )
        await factory.create_world_location(
            location_id=location_id,
            region_id=region_id,
            location_name="Test Location"
        )
        await factory.create_world_cell(
            cell_id=cell_id,
            location_id=location_id,
            cell_name="Test Cell"
        )
        
        # World Object 생성
        result_id = await factory.create_world_object(
            object_id=object_id,
            object_type="interactive",
            object_name="Test Door",
            default_cell_id=cell_id,
            default_position=default_position,
            interaction_type="openable",
            possible_states=possible_states,
            properties=properties,
            wall_mounted=True,
            passable=False,
            movable=False,
            object_height=2.0,
            object_width=1.0,
            object_depth=0.2,
            object_weight=50.0,
            object_description="A test door"
        )
        
        assert result_id == object_id
        
        # 데이터베이스에서 확인
        async with db_connection.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT wall_mounted, passable, movable,
                       object_height, object_width, object_depth, object_weight,
                       default_position, possible_states, properties
                FROM game_data.world_objects
                WHERE object_id = $1
            """, object_id)
            
            assert row is not None
            assert row['wall_mounted'] is True
            assert row['passable'] is False
            assert row['movable'] is False
            assert row['object_height'] == 2.0
            assert row['object_width'] == 1.0
            assert row['object_depth'] == 0.2
            assert row['object_weight'] == 50.0
            
            import json
            stored_position = json.loads(row['default_position']) if row['default_position'] else None
            assert stored_position is not None
            assert stored_position['x'] == 5.0
            assert stored_position['y'] == 3.0
    
    finally:
        # 테스트 데이터 정리
        async with db_connection.acquire() as conn:
            await conn.execute("DELETE FROM game_data.world_objects WHERE object_id = $1", object_id)
            await conn.execute("DELETE FROM game_data.world_cells WHERE cell_id = $1", cell_id)
            await conn.execute("DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)
            await conn.execute("DELETE FROM game_data.world_regions WHERE region_id = $1", region_id)


@pytest.mark.asyncio
async def test_create_world_object_with_defaults(db_connection, factory):
    """World Object 생성 시 기본값이 올바르게 설정되는지 확인"""
    object_id = "TEST_OBJ_DEFAULT_001"
    
    try:
        # World Object 생성 (기본값만 사용)
        result_id = await factory.create_world_object(
            object_id=object_id,
            object_type="static",
            object_name="Test Static Object"
        )
        
        assert result_id == object_id
        
        # 데이터베이스에서 확인
        async with db_connection.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT wall_mounted, passable, movable,
                       object_height, object_width, object_depth, object_weight
                FROM game_data.world_objects
                WHERE object_id = $1
            """, object_id)
            
            assert row is not None
            assert row['wall_mounted'] is False
            assert row['passable'] is False
            assert row['movable'] is False
            assert row['object_height'] == 1.0
            assert row['object_width'] == 1.0
            assert row['object_depth'] == 1.0
            assert row['object_weight'] == 0.0
    
    finally:
        # 테스트 데이터 정리
        async with db_connection.acquire() as conn:
            await conn.execute("DELETE FROM game_data.world_objects WHERE object_id = $1", object_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

