"""
Phase 1: DB 스키마 마이그레이션 단위 테스트

각 마이그레이션의 무결성을 보장하기 위한 테스트
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


@pytest_asyncio.fixture
async def db_connection():
    """데이터베이스 연결 픽스처"""
    db = DatabaseConnection()
    pool = await db.pool
    yield pool
    await db.close()


@pytest.mark.asyncio
async def test_entity_default_position_3d_column_exists(db_connection):
    """Entity 테이블에 default_position_3d 컬럼이 존재하는지 확인"""
    async with db_connection.acquire() as conn:
        result = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_schema = 'game_data' 
            AND table_name = 'entities' 
            AND column_name = 'default_position_3d'
            AND data_type = 'jsonb'
        """)
        assert result == 1, "default_position_3d 컬럼이 존재하지 않거나 타입이 올바르지 않습니다"


@pytest.mark.asyncio
async def test_entity_size_column_exists(db_connection):
    """Entity 테이블에 entity_size 컬럼이 존재하는지 확인"""
    async with db_connection.acquire() as conn:
        result = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_schema = 'game_data' 
            AND table_name = 'entities' 
            AND column_name = 'entity_size'
            AND data_type = 'character varying'
            AND character_maximum_length = 20
        """)
        assert result == 1, "entity_size 컬럼이 존재하지 않거나 타입이 올바르지 않습니다"


@pytest.mark.asyncio
async def test_entity_size_constraint(db_connection):
    """Entity 크기 제약조건이 올바르게 설정되었는지 확인"""
    async with db_connection.acquire() as conn:
        # 허용된 값들
        valid_sizes = ['tiny', 'small', 'medium', 'large', 'huge', 'gargantuan']
        
        for size in valid_sizes:
            # 테스트용 임시 엔티티 생성
            test_id = f"TEST_ENTITY_{size}"
            try:
                await conn.execute("""
                    INSERT INTO game_data.entities 
                    (entity_id, entity_type, entity_name, entity_size)
                    VALUES ($1, 'npc', 'Test Entity', $2)
                """, test_id, size)
                
                # 값이 올바르게 저장되었는지 확인
                stored_size = await conn.fetchval("""
                    SELECT entity_size FROM game_data.entities WHERE entity_id = $1
                """, test_id)
                assert stored_size == size, f"{size} 값이 올바르게 저장되지 않았습니다"
                
            finally:
                # 테스트 데이터 정리
                await conn.execute("DELETE FROM game_data.entities WHERE entity_id = $1", test_id)
        
        # 잘못된 값 거부 확인
        invalid_size = 'invalid_size'
        with pytest.raises(Exception):  # 제약조건 위반 예외
            await conn.execute("""
                INSERT INTO game_data.entities 
                (entity_id, entity_type, entity_name, entity_size)
                VALUES ($1, 'npc', 'Test Entity', $2)
            """, "TEST_INVALID", invalid_size)


@pytest.mark.asyncio
async def test_entity_size_default_value(db_connection):
    """Entity 크기 기본값이 'medium'인지 확인"""
    async with db_connection.acquire() as conn:
        test_id = "TEST_DEFAULT_SIZE"
        try:
            await conn.execute("""
                INSERT INTO game_data.entities 
                (entity_id, entity_type, entity_name)
                VALUES ($1, 'npc', 'Test Entity')
            """, test_id)
            
            default_size = await conn.fetchval("""
                SELECT entity_size FROM game_data.entities WHERE entity_id = $1
            """, test_id)
            assert default_size == 'medium', f"기본값이 'medium'이 아닙니다: {default_size}"
        finally:
            await conn.execute("DELETE FROM game_data.entities WHERE entity_id = $1", test_id)


@pytest.mark.asyncio
async def test_entity_position_index_exists(db_connection):
    """Entity 위치 인덱스가 존재하는지 확인"""
    async with db_connection.acquire() as conn:
        result = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM pg_indexes 
            WHERE schemaname = 'game_data' 
            AND tablename = 'entities' 
            AND indexname = 'idx_entities_position_cell'
        """)
        assert result == 1, "idx_entities_position_cell 인덱스가 존재하지 않습니다"


@pytest.mark.asyncio
async def test_world_object_properties_columns_exist(db_connection):
    """World Objects 테이블에 모든 새로운 컬럼이 존재하는지 확인"""
    async with db_connection.acquire() as conn:
        expected_columns = [
            'wall_mounted', 'passable', 'movable',
            'object_height', 'object_width', 'object_depth', 'object_weight'
        ]
        
        for column in expected_columns:
            result = await conn.fetchval("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_schema = 'game_data' 
                AND table_name = 'world_objects' 
                AND column_name = $1
            """, column)
            assert result == 1, f"{column} 컬럼이 존재하지 않습니다"


@pytest.mark.asyncio
async def test_world_object_dimensions_constraint(db_connection):
    """World Objects 크기 제약조건이 올바르게 설정되었는지 확인"""
    async with db_connection.acquire() as conn:
        test_id = "TEST_OBJECT_DIMENSIONS"
        try:
            # 양수 값은 허용되어야 함
            await conn.execute("""
                INSERT INTO game_data.world_objects 
                (object_id, object_type, object_name, 
                 object_height, object_width, object_depth, object_weight)
                VALUES ($1, 'test', 'Test Object', 1.0, 1.0, 1.0, 10.0)
            """, test_id)
            
            # 음수 값은 거부되어야 함
            with pytest.raises(Exception):  # 제약조건 위반 예외
                await conn.execute("""
                    INSERT INTO game_data.world_objects 
                    (object_id, object_type, object_name, object_height)
                    VALUES ($1, 'test', 'Test Object', -1.0)
                """, "TEST_NEGATIVE")
        finally:
            await conn.execute("DELETE FROM game_data.world_objects WHERE object_id = $1", test_id)


@pytest.mark.asyncio
async def test_world_object_default_values(db_connection):
    """World Objects 기본값이 올바르게 설정되었는지 확인"""
    async with db_connection.acquire() as conn:
        test_id = "TEST_DEFAULT_VALUES"
        try:
            await conn.execute("""
                INSERT INTO game_data.world_objects 
                (object_id, object_type, object_name)
                VALUES ($1, 'test', 'Test Object')
            """, test_id)
            
            result = await conn.fetchrow("""
                SELECT wall_mounted, passable, movable, 
                       object_height, object_width, object_depth, object_weight
                FROM game_data.world_objects 
                WHERE object_id = $1
            """, test_id)
            
            assert result['wall_mounted'] is False
            assert result['passable'] is False
            assert result['movable'] is False
            assert result['object_height'] == 1.0
            assert result['object_width'] == 1.0
            assert result['object_depth'] == 1.0
            assert result['object_weight'] == 0.0
        finally:
            await conn.execute("DELETE FROM game_data.world_objects WHERE object_id = $1", test_id)


@pytest.mark.asyncio
async def test_map_metadata_hierarchy_columns_exist(db_connection):
    """Map Metadata 테이블에 계층 구조 컬럼이 존재하는지 확인"""
    async with db_connection.acquire() as conn:
        expected_columns = ['map_level', 'parent_entity_id', 'parent_entity_type']
        
        for column in expected_columns:
            result = await conn.fetchval("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_schema = 'game_data' 
                AND table_name = 'map_metadata' 
                AND column_name = $1
            """, column)
            assert result == 1, f"{column} 컬럼이 존재하지 않습니다"


@pytest.mark.asyncio
async def test_map_level_constraint(db_connection):
    """Map 레벨 제약조건이 올바르게 설정되었는지 확인"""
    async with db_connection.acquire() as conn:
        valid_levels = ['world', 'region', 'location', 'cell']
        
        for level in valid_levels:
            test_id = f"TEST_MAP_{level}"
            try:
                await conn.execute("""
                    INSERT INTO game_data.map_metadata 
                    (map_id, map_name, map_level)
                    VALUES ($1, 'Test Map', $2)
                """, test_id, level)
                
                stored_level = await conn.fetchval("""
                    SELECT map_level FROM game_data.map_metadata WHERE map_id = $1
                """, test_id)
                assert stored_level == level, f"{level} 값이 올바르게 저장되지 않았습니다"
            finally:
                await conn.execute("DELETE FROM game_data.map_metadata WHERE map_id = $1", test_id)
        
        # 잘못된 값 거부 확인
        invalid_level = 'invalid_level'
        with pytest.raises(Exception):  # 제약조건 위반 예외
            await conn.execute("""
                INSERT INTO game_data.map_metadata 
                (map_id, map_name, map_level)
                VALUES ($1, 'Test Map', $2)
            """, "TEST_INVALID", invalid_level)


@pytest.mark.asyncio
async def test_map_metadata_default_level(db_connection):
    """Map Metadata 기본 레벨이 'world'인지 확인"""
    async with db_connection.acquire() as conn:
        test_id = "TEST_DEFAULT_LEVEL"
        try:
            await conn.execute("""
                INSERT INTO game_data.map_metadata 
                (map_id, map_name)
                VALUES ($1, 'Test Map')
            """, test_id)
            
            default_level = await conn.fetchval("""
                SELECT map_level FROM game_data.map_metadata WHERE map_id = $1
            """, test_id)
            assert default_level == 'world', f"기본값이 'world'가 아닙니다: {default_level}"
        finally:
            await conn.execute("DELETE FROM game_data.map_metadata WHERE map_id = $1", test_id)


@pytest.mark.asyncio
async def test_all_indexes_exist(db_connection):
    """모든 인덱스가 올바르게 생성되었는지 확인"""
    async with db_connection.acquire() as conn:
        expected_indexes = [
            ('entities', 'idx_entities_position_cell'),
            ('entities', 'idx_entities_size'),
            ('world_objects', 'idx_world_objects_passable'),
            ('world_objects', 'idx_world_objects_movable'),
            ('world_objects', 'idx_world_objects_wall_mounted'),
            ('map_metadata', 'idx_map_metadata_level'),
            ('map_metadata', 'idx_map_metadata_parent'),
            ('map_metadata', 'idx_map_metadata_parent_type'),
        ]
        
        for table_name, index_name in expected_indexes:
            result = await conn.fetchval("""
                SELECT COUNT(*) 
                FROM pg_indexes 
                WHERE schemaname = 'game_data' 
                AND tablename = $1 
                AND indexname = $2
            """, table_name, index_name)
            assert result == 1, f"{index_name} 인덱스가 존재하지 않습니다"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

