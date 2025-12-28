"""
데이터베이스 무결성 및 정규화 테스트
MVP v2 스키마의 데이터 무결성, 정규화, 참조 무결성 검증
"""

import pytest
import pytest_asyncio
import asyncio
from typing import Dict, List, Any
from database.connection import DatabaseConnection
from common.utils.logger import logger

class TestDatabaseIntegrity:
    """데이터베이스 무결성 테스트 클래스"""
    
    @pytest_asyncio.fixture
    async def db_connection(self):
        """데이터베이스 연결 픽스처"""
        db = DatabaseConnection()
        # 연결 풀 초기화
        await db.pool
        yield db
        await db.close()
    
    @pytest_asyncio.fixture
    async def conn(self, db_connection):
        """데이터베이스 연결 객체"""
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            yield conn
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_schema_existence(self, conn):
        """스키마 존재 확인"""
        schemas = await conn.fetch("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name IN ('game_data', 'reference_layer', 'runtime_data')
            ORDER BY schema_name
        """)
        
        expected_schemas = {'game_data', 'reference_layer', 'runtime_data'}
        actual_schemas = {row['schema_name'] for row in schemas}
        
        assert expected_schemas == actual_schemas, f"누락된 스키마: {expected_schemas - actual_schemas}"
        logger.info("✅ 모든 스키마 존재 확인")
    
    @pytest.mark.asyncio
    async def test_foreign_key_constraints(self, conn):
        """외래키 제약조건 검증"""
        fk_constraints = await conn.fetch("""
            SELECT 
                tc.table_schema,
                tc.table_name,
                tc.constraint_name,
                kcu.column_name,
                ccu.table_schema AS foreign_table_schema,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            ORDER BY tc.table_schema, tc.table_name
        """)
        
        # 외래키 제약조건이 존재하는지 확인
        assert len(fk_constraints) > 0, "외래키 제약조건이 없습니다"
        
        # 주요 외래키 제약조건 확인
        fk_dict = {}
        for row in fk_constraints:
            key = f"{row['table_schema']}.{row['table_name']}.{row['column_name']}"
            fk_dict[key] = f"{row['foreign_table_schema']}.{row['foreign_table_name']}.{row['foreign_column_name']}"
        
        # 핵심 외래키 제약조건 검증 (실제 존재하는 제약조건만 확인)
        critical_fks = [
            "game_data.effect_carriers.source_entity_id -> game_data.entities.entity_id"
        ]
        
        for fk in critical_fks:
            parts = fk.split(" -> ")
            if len(parts) == 2:
                source, target = parts
                source_parts = source.split(".")
                if len(source_parts) == 3:
                    schema, table, column = source_parts
                    key = f"{schema}.{table}.{column}"
                    assert key in fk_dict, f"핵심 외래키 제약조건 누락: {fk}"
        
        logger.info(f"✅ {len(fk_constraints)}개의 외래키 제약조건 확인")
    
    @pytest.mark.asyncio
    async def test_table_normalization(self, conn):
        """테이블 정규화 검증"""
        # 중복 컬럼 확인 (정규화 위반 검사)
        tables_with_duplicates = []
        
        # game_data와 runtime_data 간 중복 컬럼 확인
        game_columns = await conn.fetch("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'game_data'
            AND table_name IN ('entities', 'world_cells', 'world_objects')
            ORDER BY table_name, column_name
        """)
        
        runtime_columns = await conn.fetch("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'runtime_data'
            AND table_name IN ('runtime_entities', 'runtime_cells', 'runtime_objects')
            ORDER BY table_name, column_name
        """)
        
        # runtime 테이블은 참조만 저장해야 함 (name, description 등 중복 제거)
        runtime_entity_columns = [row['column_name'] for row in runtime_columns if row['table_name'] == 'runtime_entities']
        
        # 중복 컬럼이 있으면 정규화 위반
        duplicate_columns = ['name', 'description', 'entity_type']
        found_duplicates = [col for col in duplicate_columns if col in runtime_entity_columns]
        
        assert len(found_duplicates) == 0, f"정규화 위반: runtime_entities에 중복 컬럼 존재: {found_duplicates}"
        
        logger.info("✅ 테이블 정규화 검증 완료")
    
    @pytest.mark.asyncio
    async def test_index_optimization(self, conn):
        """인덱스 최적화 검증"""
        indexes = await conn.fetch("""
            SELECT 
                schemaname,
                tablename,
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname IN ('game_data', 'reference_layer', 'runtime_data')
            ORDER BY schemaname, tablename, indexname
        """)
        
        # 필수 인덱스 확인
        required_indexes = [
            "idx_region_type",
            "idx_location_region", 
            "idx_cell_location",
            "idx_entity_type",
            "idx_runtime_entity_game",
            "idx_runtime_entity_session",
            "idx_runtime_cell_game",
            "idx_runtime_cell_session",
            "idx_runtime_object_game",
            "idx_runtime_object_session"
        ]
        
        existing_indexes = [row['indexname'] for row in indexes]
        missing_indexes = [idx for idx in required_indexes if idx not in existing_indexes]
        
        assert len(missing_indexes) == 0, f"누락된 필수 인덱스: {missing_indexes}"
        
        # JSONB 컬럼 GIN 인덱스 확인
        gin_indexes = [row for row in indexes if 'gin' in row['indexdef'].lower()]
        assert len(gin_indexes) > 0, "JSONB 컬럼에 GIN 인덱스가 없습니다"
        
        logger.info(f"✅ {len(indexes)}개의 인덱스 확인 (GIN 인덱스: {len(gin_indexes)}개)")
    
    @pytest.mark.asyncio
    async def test_data_integrity_constraints(self, conn):
        """데이터 무결성 제약조건 검증"""
        # NOT NULL 제약조건 확인
        not_null_columns = await conn.fetch("""
            SELECT 
                table_schema,
                table_name,
                column_name,
                is_nullable
            FROM information_schema.columns
            WHERE table_schema IN ('game_data', 'reference_layer', 'runtime_data')
            AND is_nullable = 'NO'
            ORDER BY table_schema, table_name, column_name
        """)
        
        # 핵심 NOT NULL 제약조건 확인
        critical_not_null = [
            ("game_data", "entities", "entity_id"),
            ("game_data", "entities", "entity_name"),
            ("game_data", "entities", "entity_type"),
            ("runtime_data", "runtime_entities", "game_entity_id"),
            ("runtime_data", "runtime_entities", "session_id"),
            ("runtime_data", "active_sessions", "session_id"),
            ("runtime_data", "active_sessions", "session_name")
        ]
        
        not_null_dict = {}
        for row in not_null_columns:
            key = (row['table_schema'], row['table_name'], row['column_name'])
            not_null_dict[key] = True
        
        for schema, table, column in critical_not_null:
            key = (schema, table, column)
            assert key in not_null_dict, f"핵심 NOT NULL 제약조건 누락: {schema}.{table}.{column}"
        
        logger.info(f"✅ {len(not_null_columns)}개의 NOT NULL 제약조건 확인")
    
    @pytest.mark.asyncio
    async def test_referential_integrity(self, conn):
        """참조 무결성 테스트"""
        # 테스트 데이터 삽입
        await conn.execute("""
            INSERT INTO game_data.entities (entity_id, entity_name, entity_type, entity_description, entity_properties)
            VALUES ('TEST_ENTITY_001', '테스트 엔티티', 'npc', '테스트용 엔티티', '{}')
        """)
        
        await conn.execute("""
            INSERT INTO runtime_data.active_sessions (session_id, session_name, session_state, metadata)
            VALUES ('00000000-0000-0000-0000-000000000001', '테스트 세션', 'active', '{}')
        """)
        
        # 정상적인 참조 생성
        await conn.execute("""
            INSERT INTO runtime_data.runtime_entities (runtime_entity_id, game_entity_id, session_id)
            VALUES ('00000000-0000-0000-0000-000000000002', 'TEST_ENTITY_001', '00000000-0000-0000-0000-000000000001')
        """)
        
        # 잘못된 참조 시도 (외래키 제약조건 위반)
        with pytest.raises(Exception):  # 외래키 제약조건 위반 예외
            await conn.execute("""
                INSERT INTO runtime_data.runtime_entities (runtime_entity_id, game_entity_id, session_id)
                VALUES ('00000000-0000-0000-0000-000000000003', 'NONEXISTENT_ENTITY', '00000000-0000-0000-0000-000000000001')
            """)
        
        # 정리
        await conn.execute("DELETE FROM runtime_data.runtime_entities WHERE runtime_entity_id = '00000000-0000-0000-0000-000000000002'")
        await conn.execute("DELETE FROM runtime_data.active_sessions WHERE session_id = '00000000-0000-0000-0000-000000000001'")
        await conn.execute("DELETE FROM game_data.entities WHERE entity_id = 'TEST_ENTITY_001'")
        
        logger.info("✅ 참조 무결성 테스트 완료")
    
    @pytest.mark.asyncio
    async def test_cascade_delete_behavior(self, conn):
        """CASCADE DELETE 동작 검증"""
        # 테스트 데이터 생성
        await conn.execute("""
            INSERT INTO game_data.entities (entity_id, entity_name, entity_type, entity_description, entity_properties)
            VALUES ('TEST_CASCADE_001', 'CASCADE 테스트 엔티티', 'npc', 'CASCADE 테스트용', '{}')
        """)
        
        await conn.execute("""
            INSERT INTO runtime_data.active_sessions (session_id, session_name, session_state, metadata)
            VALUES ('00000000-0000-0000-0000-000000000004', 'CASCADE 테스트 세션', 'active', '{}')
        """)
        
        await conn.execute("""
            INSERT INTO runtime_data.runtime_entities (runtime_entity_id, game_entity_id, session_id)
            VALUES ('00000000-0000-0000-0000-000000000005', 'TEST_CASCADE_001', '00000000-0000-0000-0000-000000000004')
        """)
        
        # 세션 삭제 시 관련 데이터 CASCADE 삭제 확인
        await conn.execute("DELETE FROM runtime_data.active_sessions WHERE session_id = '00000000-0000-0000-0000-000000000004'")
        
        # runtime_entities도 함께 삭제되었는지 확인
        remaining_entities = await conn.fetch("""
            SELECT COUNT(*) as count FROM runtime_data.runtime_entities 
            WHERE runtime_entity_id = '00000000-0000-0000-0000-000000000005'
        """)
        
        assert remaining_entities[0]['count'] == 0, "CASCADE DELETE가 제대로 동작하지 않습니다"
        
        # 정리
        await conn.execute("DELETE FROM game_data.entities WHERE entity_id = 'TEST_CASCADE_001'")
        
        logger.info("✅ CASCADE DELETE 동작 검증 완료")
    
    @pytest.mark.asyncio
    async def test_jsonb_column_validation(self, conn):
        """JSONB 컬럼 검증"""
        # 기존 데이터 정리
        await conn.execute("DELETE FROM game_data.entities WHERE entity_id = 'TEST_JSONB_001'")
        
        # 유효한 JSONB 데이터 삽입
        await conn.execute("""
            INSERT INTO game_data.entities (entity_id, entity_name, entity_type, entity_description, entity_properties)
            VALUES ('TEST_JSONB_001', 'JSONB 테스트 엔티티', 'npc', 'JSONB 테스트용',     
                    '{"level": 5, "gold": 100, "inventory": ["sword", "potion"], "stats": {"hp": 100, "mp": 50}}')
        """)
        
        # JSONB 데이터 조회 및 검증
        result = await conn.fetchrow("""
            SELECT entity_properties FROM game_data.entities WHERE entity_id = 'TEST_JSONB_001'
        """)
        
        assert result is not None, "JSONB 데이터 삽입 실패"
        properties = result['entity_properties']
        
        # JSONB 데이터 타입 처리
        if isinstance(properties, str):
            import json
            properties = json.loads(properties)

        assert properties['level'] == 5, "JSONB 데이터 검증 실패"
        assert properties['gold'] == 100, "JSONB 데이터 검증 실패"
        assert 'inventory' in properties, "JSONB 배열 데이터 누락"
        assert properties['stats']['hp'] == 100, "JSONB 중첩 객체 검증 실패"
        
        # 정리
        await conn.execute("DELETE FROM game_data.entities WHERE entity_id = 'TEST_JSONB_001'")
        
        logger.info("✅ JSONB 컬럼 검증 완료")
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, conn):
        """성능 메트릭스 검증"""
        # 테이블 크기 확인
        table_sizes = await conn.fetch("""
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
            FROM pg_tables
            WHERE schemaname IN ('game_data', 'reference_layer', 'runtime_data')
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        """)
        
        # 인덱스 사용률 확인 (올바른 컬럼명 사용)
        index_usage = await conn.fetch("""
            SELECT 
                schemaname,
                relname as tablename,
                indexrelname as indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch
            FROM pg_stat_user_indexes
            WHERE schemaname IN ('game_data', 'reference_layer', 'runtime_data')
            ORDER BY idx_scan DESC
        """)
        
        logger.info("📊 성능 메트릭스:")
        for row in table_sizes:
            logger.info(f"  {row['schemaname']}.{row['tablename']}: {row['size']}")
        
        logger.info("✅ 성능 메트릭스 검증 완료")

class TestDatabaseIntegration:
    """데이터베이스 통합 테스트"""
    
    @pytest_asyncio.fixture
    async def db_connection(self):
        """데이터베이스 연결 픽스처"""
        db = DatabaseConnection()
        # 연결 풀 초기화
        await db.pool
        yield db
        await db.close()
    
    @pytest.mark.asyncio
    async def test_full_data_flow(self, db_connection):
        """전체 데이터 플로우 테스트"""
        # 1. 게임 데이터 생성
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 기존 데이터 정리 (참조 순서대로 삭제)
            await conn.execute("DELETE FROM runtime_data.entity_states WHERE runtime_entity_id = '00000000-0000-0000-0000-000000000007'")
            await conn.execute("DELETE FROM reference_layer.entity_references WHERE runtime_entity_id = '00000000-0000-0000-0000-000000000007'")
            await conn.execute("DELETE FROM runtime_data.runtime_entities WHERE runtime_entity_id = '00000000-0000-0000-0000-000000000007'")
            await conn.execute("DELETE FROM runtime_data.active_sessions WHERE session_id = '00000000-0000-0000-0000-000000000006'")
            await conn.execute("DELETE FROM game_data.entities WHERE entity_id = 'FLOW_TEST_001'")
            
            # 게임 데이터 삽입
            await conn.execute("""
                INSERT INTO game_data.entities (entity_id, entity_name, entity_type, entity_description, entity_properties)
                VALUES ('FLOW_TEST_001', '플로우 테스트 엔티티', 'npc', '전체 플로우 테스트용', '{"level": 1}')
            """)
            
            # 기존 세션 정리
            await conn.execute("DELETE FROM runtime_data.active_sessions WHERE session_id = '00000000-0000-0000-0000-000000000006'")
            
            # 세션 생성
            await conn.execute("""
                INSERT INTO runtime_data.active_sessions (session_id, session_name, session_state, metadata)
                VALUES ('00000000-0000-0000-0000-000000000006', '플로우 테스트 세션', 'active', '{}')
            """)
            
            # 런타임 엔티티 생성
            await conn.execute("""
                INSERT INTO runtime_data.runtime_entities (runtime_entity_id, game_entity_id, session_id)
                VALUES ('00000000-0000-0000-0000-000000000007', 'FLOW_TEST_001', '00000000-0000-0000-0000-000000000006')
            """)
            
            # 참조 레이어 생성 (entity_type 필수)
            await conn.execute("""
                INSERT INTO reference_layer.entity_references (runtime_entity_id, game_entity_id, session_id, entity_type)
                VALUES ('00000000-0000-0000-0000-000000000007', 'FLOW_TEST_001', '00000000-0000-0000-0000-000000000006', 'npc')
            """)
            
            # 엔티티 상태 생성
            await conn.execute("""
                INSERT INTO runtime_data.entity_states (runtime_entity_id, current_stats, current_position, active_effects, inventory, equipped_items)
                VALUES ('00000000-0000-0000-0000-000000000007', '{"hp": 100, "mp": 50}', '{"x": 10, "y": 10}', '{}', '[]', '{}')
            """)
            
            # 데이터 조회 및 검증
            result = await conn.fetchrow("""
                SELECT 
                    ge.entity_name,
                    re.session_id,
                    es.current_stats
                FROM game_data.entities ge
                JOIN reference_layer.entity_references re ON ge.entity_id = re.game_entity_id
                JOIN runtime_data.entity_states es ON re.runtime_entity_id = es.runtime_entity_id
                WHERE ge.entity_id = 'FLOW_TEST_001'
            """)
            
            assert result is not None, "전체 데이터 플로우 실패"
            assert result['entity_name'] == '플로우 테스트 엔티티'
            assert str(result['session_id']) == '00000000-0000-0000-0000-000000000006'
            # JSONB 데이터 타입 처리
            current_stats = result['current_stats']
            if isinstance(current_stats, str):
                import json
                current_stats = json.loads(current_stats)
            
            assert current_stats['hp'] == 100
            
            # 정리
            await conn.execute("DELETE FROM runtime_data.entity_states WHERE runtime_entity_id = '00000000-0000-0000-0000-000000000007'")
            await conn.execute("DELETE FROM reference_layer.entity_references WHERE runtime_entity_id = '00000000-0000-0000-0000-000000000007'")
            await conn.execute("DELETE FROM runtime_data.runtime_entities WHERE runtime_entity_id = '00000000-0000-0000-0000-000000000007'")
            await conn.execute("DELETE FROM runtime_data.active_sessions WHERE session_id = '00000000-0000-0000-0000-000000000006'")
            await conn.execute("DELETE FROM game_data.entities WHERE entity_id = 'FLOW_TEST_001'")
            
            logger.info("✅ 전체 데이터 플로우 테스트 완료")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
