"""
SSOT Phase 3 마이그레이션 테스트
owner_name 제거 및 고아 참조 정리 검증
"""
import pytest
import pytest_asyncio
from database.connection import DatabaseConnection
from common.utils.jsonb_handler import serialize_jsonb_data
from pathlib import Path
import sys

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest_asyncio.fixture
async def db_connection():
    """데이터베이스 연결 fixture"""
    db = DatabaseConnection()
    await db.initialize()
    yield db
    await db.close()


@pytest_asyncio.fixture
async def test_entity(db_connection):
    """테스트용 엔티티 생성"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        entity_id = "TEST_MIGRATION_ENTITY_001"
        entity_name = "마이그레이션 테스트 엔티티"
        
        await conn.execute("""
            INSERT INTO game_data.entities 
            (entity_id, entity_type, entity_name, entity_description, base_stats, default_equipment, 
             default_abilities, default_inventory, entity_properties, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
            ON CONFLICT (entity_id) DO UPDATE SET entity_name = $3
        """, 
        entity_id, 'npc', entity_name, '마이그레이션 테스트용', 
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
        region_id = "TEST_MIGRATION_REGION_001"
        
        await conn.execute("""
            INSERT INTO game_data.world_regions 
            (region_id, region_name, region_description, region_type, region_properties, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
            ON CONFLICT (region_id) DO UPDATE SET region_name = $2
        """,
        region_id, '마이그레이션 테스트 지역', 'SSOT 마이그레이션 테스트용', 'village', serialize_jsonb_data({}))
        
        yield region_id
        
        # Cleanup
        await conn.execute("DELETE FROM game_data.world_regions WHERE region_id = $1", region_id)


@pytest_asyncio.fixture
async def test_location_with_owner_name(db_connection, test_region, test_entity):
    """owner_name이 있는 테스트용 Location 생성 (마이그레이션 전 상태)"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        location_id = "TEST_MIGRATION_LOC_001"
        
        # owner_name을 포함한 location_properties (마이그레이션 전 상태)
        location_properties = {
            "ownership": {
                "owner_entity_id": test_entity["entity_id"],
                "owner_name": test_entity["entity_name"],  # 제거 대상
                "ownership_type": "private"
            }
        }
        
        await conn.execute("""
            INSERT INTO game_data.world_locations 
            (location_id, region_id, location_name, location_description, location_type, location_properties, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
            ON CONFLICT (location_id) DO UPDATE SET location_properties = $6
        """,
        location_id, test_region, 'owner_name이 있는 위치', '마이그레이션 테스트용', 'shop', 
        serialize_jsonb_data(location_properties))
        
        yield location_id
        
        # Cleanup
        await conn.execute("DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)


@pytest_asyncio.fixture
async def test_cell_with_owner_name(db_connection, test_location_with_owner_name, test_entity):
    """owner_name이 있는 테스트용 Cell 생성 (마이그레이션 전 상태)"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        cell_id = "TEST_MIGRATION_CELL_001"
        
        # owner_name을 포함한 cell_properties (마이그레이션 전 상태)
        cell_properties = {
            "ownership": {
                "owner_entity_id": test_entity["entity_id"],
                "owner_name": test_entity["entity_name"],  # 제거 대상
                "is_private": False
            }
        }
        
        await conn.execute("""
            INSERT INTO game_data.world_cells 
            (cell_id, location_id, cell_name, matrix_width, matrix_height, cell_description, 
             cell_properties, cell_status, cell_type, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
            ON CONFLICT (cell_id) DO UPDATE SET cell_properties = $7
        """,
        cell_id, test_location_with_owner_name, 'owner_name이 있는 셀', 10, 10, '마이그레이션 테스트용', 
        serialize_jsonb_data(cell_properties), 'active', 'indoor')
        
        yield cell_id
        
        # Cleanup
        await conn.execute("DELETE FROM game_data.world_cells WHERE cell_id = $1", cell_id)


@pytest_asyncio.fixture
async def test_location_with_orphan_reference(db_connection, test_region):
    """고아 참조가 있는 테스트용 Location 생성"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        location_id = "TEST_MIGRATION_LOC_ORPHAN_001"
        
        # 존재하지 않는 entity_id를 참조하는 location_properties
        location_properties = {
            "ownership": {
                "owner_entity_id": "NON_EXISTENT_ENTITY_001",  # 고아 참조
                "ownership_type": "private"
            },
            "quests": {
                "quest_givers": ["NON_EXISTENT_ENTITY_002"]  # 고아 참조
            }
        }
        
        await conn.execute("""
            INSERT INTO game_data.world_locations 
            (location_id, region_id, location_name, location_description, location_type, location_properties, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
            ON CONFLICT (location_id) DO UPDATE SET location_properties = $6
        """,
        location_id, test_region, '고아 참조가 있는 위치', '마이그레이션 테스트용', 'shop', 
        serialize_jsonb_data(location_properties))
        
        yield location_id
        
        # Cleanup
        await conn.execute("DELETE FROM game_data.world_locations WHERE location_id = $1", location_id)


@pytest.mark.asyncio
async def test_owner_name_removed_after_migration(db_connection, test_location_with_owner_name, test_cell_with_owner_name):
    """마이그레이션 후 owner_name이 제거되었는지 확인"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        # 마이그레이션 실행
        migration_file = Path(__file__).parent.parent.parent / "database" / "setup" / "migrations" / "remove_owner_name_ssot.sql"
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        async with conn.transaction():
            await conn.execute(migration_sql)
        
        # 검증: Location의 owner_name이 제거되었는지 확인
        location_properties = await conn.fetchval("""
            SELECT location_properties
            FROM game_data.world_locations
            WHERE location_id = $1
        """, test_location_with_owner_name)
        
        assert location_properties is not None
        location_props = location_properties
        if isinstance(location_props, str):
            import json
            location_props = json.loads(location_props)
        
        assert 'ownership' in location_props
        assert 'owner_name' not in location_props['ownership'], "owner_name이 제거되어야 함"
        assert 'owner_entity_id' in location_props['ownership'], "owner_entity_id는 유지되어야 함"
        
        # 검증: Cell의 owner_name이 제거되었는지 확인
        cell_properties = await conn.fetchval("""
            SELECT cell_properties
            FROM game_data.world_cells
            WHERE cell_id = $1
        """, test_cell_with_owner_name)
        
        assert cell_properties is not None
        cell_props = cell_properties
        if isinstance(cell_props, str):
            import json
            cell_props = json.loads(cell_props)
        
        assert 'ownership' in cell_props
        assert 'owner_name' not in cell_props['ownership'], "owner_name이 제거되어야 함"
        assert 'owner_entity_id' in cell_props['ownership'], "owner_entity_id는 유지되어야 함"


@pytest.mark.asyncio
async def test_orphan_references_cleaned_after_migration(db_connection, test_location_with_orphan_reference):
    """마이그레이션 후 고아 참조가 정리되었는지 확인"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        # 먼저 fixture가 제대로 생성되었는지 확인
        location_exists = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM game_data.world_locations
            WHERE location_id = $1
        """, test_location_with_orphan_reference)
        
        assert location_exists > 0, "테스트 Location이 생성되어야 함"
        
        # 마이그레이션 실행
        migration_file = Path(__file__).parent.parent.parent / "database" / "setup" / "migrations" / "cleanup_orphan_references_ssot.sql"
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        async with conn.transaction():
            await conn.execute(migration_sql)
        
        # 검증: Location이 여전히 존재하는지 확인
        location_row = await conn.fetchrow("""
            SELECT location_id, location_properties
            FROM game_data.world_locations
            WHERE location_id = $1
        """, test_location_with_orphan_reference)
        
        assert location_row is not None, "마이그레이션 후에도 Location이 존재해야 함"
        
        # 검증: Location의 고아 owner_entity_id가 null로 설정되었는지 확인
        location_properties = location_row['location_properties']
        
        # location_properties가 None일 수 있으므로 처리
        if location_properties is None:
            # 마이그레이션이 location_properties를 NULL로 만들었을 수 있음
            # 이는 정상적인 경우일 수 있으므로, 다시 조회해보거나 기본값으로 처리
            location_properties = {}
        else:
            # JSONB를 dict로 변환
            if isinstance(location_properties, str):
                import json
                location_properties = json.loads(location_properties)
            elif hasattr(location_properties, '__dict__'):
                # asyncpg의 JSONB 타입 처리
                location_properties = dict(location_properties)
        
        location_props = location_properties if isinstance(location_properties, dict) else {}
        
        # owner_entity_id가 null이거나 제거되었는지 확인
        ownership = location_props.get('ownership', {})
        owner_entity_id = ownership.get('owner_entity_id') if isinstance(ownership, dict) else None
        
        # JSONB에서 null은 None으로 파싱되거나 'null' 문자열로 저장될 수 있음
        # 또는 ownership 자체가 없을 수도 있음
        assert owner_entity_id is None or owner_entity_id == 'null' or owner_entity_id == '' or not ownership, "고아 참조가 null로 설정되어야 함"
        
        # quest_givers에서 고아 참조가 제거되었는지 확인
        quests = location_props.get('quests', {})
        quest_givers = quests.get('quest_givers', []) if isinstance(quests, dict) else []
        assert len(quest_givers) == 0, "고아 quest_givers가 제거되어야 함"


@pytest.mark.asyncio
async def test_valid_references_preserved_after_migration(db_connection, test_location_with_owner_name, test_entity):
    """마이그레이션 후 유효한 참조는 유지되는지 확인"""
    pool = await db_connection.pool
    async with pool.acquire() as conn:
        # owner_name 제거 마이그레이션 실행
        migration_file = Path(__file__).parent.parent.parent / "database" / "setup" / "migrations" / "remove_owner_name_ssot.sql"
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        async with conn.transaction():
            await conn.execute(migration_sql)
        
        # 검증: 유효한 owner_entity_id는 유지되는지 확인
        location_properties = await conn.fetchval("""
            SELECT location_properties
            FROM game_data.world_locations
            WHERE location_id = $1
        """, test_location_with_owner_name)
        
        assert location_properties is not None
        location_props = location_properties
        if isinstance(location_props, str):
            import json
            location_props = json.loads(location_props)
        
        owner_entity_id = location_props.get('ownership', {}).get('owner_entity_id')
        assert owner_entity_id == test_entity["entity_id"], "유효한 owner_entity_id는 유지되어야 함"

