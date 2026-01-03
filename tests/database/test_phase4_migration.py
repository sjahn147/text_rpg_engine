"""
Phase 4 마이그레이션 테스트

목적:
- runtime_data.quests 테이블 생성 검증
- items, equipment_weapons, equipment_armors 테이블의 effect_carrier_id FK 검증
"""
import pytest
import pytest_asyncio
from common.utils.logger import logger

from database.connection import DatabaseConnection


@pytest.mark.asyncio
class TestPhase4Migration:
    """Phase 4 마이그레이션 테스트"""
    
    @pytest.mark.integration
    async def test_quests_table_exists(self, db_connection):
        """runtime_data.quests 테이블 존재 확인"""
        logger.info("[마이그레이션 테스트] runtime_data.quests 테이블 존재 확인")
        
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 테이블 존재 확인
            result = await conn.fetchrow(
                """
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.tables 
                    WHERE table_schema = 'runtime_data' 
                    AND table_name = 'quests'
                ) as exists
                """
            )
            
            assert result['exists'] is True, "runtime_data.quests 테이블이 존재하지 않습니다"
            
            # 컬럼 확인
            columns = await conn.fetch(
                """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'runtime_data'
                AND table_name = 'quests'
                ORDER BY ordinal_position
                """
            )
            
            column_names = [col['column_name'] for col in columns]
            
            # 필수 컬럼 확인
            assert 'quest_id' in column_names, "quest_id 컬럼이 없습니다"
            assert 'session_id' in column_names, "session_id 컬럼이 없습니다"
            assert 'quest_status' in column_names, "quest_status 컬럼이 없습니다"
            assert 'quest_title' in column_names, "quest_title 컬럼이 없습니다"
            assert 'quest_data' in column_names, "quest_data 컬럼이 없습니다"
            
            logger.info(f"[OK] runtime_data.quests 테이블 검증 성공: {len(column_names)}개 컬럼")
    
    @pytest.mark.integration
    async def test_quests_table_constraints(self, db_connection):
        """runtime_data.quests 테이블 제약조건 확인"""
        logger.info("[마이그레이션 테스트] runtime_data.quests 테이블 제약조건 확인")
        
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # CHECK 제약조건 확인
            constraints = await conn.fetch(
                """
                SELECT constraint_name, constraint_type
                FROM information_schema.table_constraints
                WHERE table_schema = 'runtime_data'
                AND table_name = 'quests'
                """
            )
            
            constraint_names = [c['constraint_name'] for c in constraints]
            
            # PRIMARY KEY 확인
            assert any('quest_id' in name or 'pkey' in name.lower() for name in constraint_names), "PRIMARY KEY 제약조건이 없습니다"
            
            # CHECK 제약조건 확인
            check_constraints = await conn.fetch(
                """
                SELECT constraint_name
                FROM information_schema.constraint_column_usage
                WHERE table_schema = 'runtime_data'
                AND table_name = 'quests'
                AND constraint_name LIKE 'chk_%'
                """
            )
            
            assert len(check_constraints) > 0, "CHECK 제약조건이 없습니다"
            
            logger.info(f"[OK] runtime_data.quests 테이블 제약조건 검증 성공")
    
    @pytest.mark.integration
    async def test_quests_table_indexes(self, db_connection):
        """runtime_data.quests 테이블 인덱스 확인"""
        logger.info("[마이그레이션 테스트] runtime_data.quests 테이블 인덱스 확인")
        
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 인덱스 확인
            indexes = await conn.fetch(
                """
                SELECT indexname
                FROM pg_indexes
                WHERE schemaname = 'runtime_data'
                AND tablename = 'quests'
                """
            )
            
            index_names = [idx['indexname'] for idx in indexes]
            
            # 필수 인덱스 확인
            assert any('session' in name.lower() for name in index_names), "session_id 인덱스가 없습니다"
            assert any('status' in name.lower() for name in index_names), "quest_status 인덱스가 없습니다"
            
            logger.info(f"[OK] runtime_data.quests 테이블 인덱스 검증 성공: {len(index_names)}개 인덱스")
    
    @pytest.mark.integration
    async def test_items_effect_carrier_fk(self, db_connection):
        """game_data.items 테이블의 effect_carrier_id FK 확인"""
        logger.info("[마이그레이션 테스트] game_data.items.effect_carrier_id FK 확인")
        
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 컬럼 존재 확인
            column = await conn.fetchrow(
                """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'game_data'
                AND table_name = 'items'
                AND column_name = 'effect_carrier_id'
                """
            )
            
            assert column is not None, "game_data.items.effect_carrier_id 컬럼이 없습니다"
            assert column['data_type'] == 'uuid', f"effect_carrier_id 타입이 UUID가 아닙니다: {column['data_type']}"
            
            # FK 제약조건 확인
            fk = await conn.fetchrow(
                """
                SELECT constraint_name
                FROM information_schema.table_constraints
                WHERE table_schema = 'game_data'
                AND table_name = 'items'
                AND constraint_name = 'fk_items_effect_carrier'
                """
            )
            
            assert fk is not None, "fk_items_effect_carrier 제약조건이 없습니다"
            
            # 인덱스 확인
            index = await conn.fetchrow(
                """
                SELECT indexname
                FROM pg_indexes
                WHERE schemaname = 'game_data'
                AND tablename = 'items'
                AND indexname = 'idx_items_effect_carrier'
                """
            )
            
            assert index is not None, "idx_items_effect_carrier 인덱스가 없습니다"
            
            logger.info(f"[OK] game_data.items.effect_carrier_id FK 검증 성공")
    
    @pytest.mark.integration
    async def test_equipment_weapons_effect_carrier_fk(self, db_connection):
        """game_data.equipment_weapons 테이블의 effect_carrier_id FK 확인"""
        logger.info("[마이그레이션 테스트] game_data.equipment_weapons.effect_carrier_id FK 확인")
        
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 컬럼 존재 확인
            column = await conn.fetchrow(
                """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'game_data'
                AND table_name = 'equipment_weapons'
                AND column_name = 'effect_carrier_id'
                """
            )
            
            assert column is not None, "game_data.equipment_weapons.effect_carrier_id 컬럼이 없습니다"
            assert column['data_type'] == 'uuid', f"effect_carrier_id 타입이 UUID가 아닙니다: {column['data_type']}"
            
            # FK 제약조건 확인
            fk = await conn.fetchrow(
                """
                SELECT constraint_name
                FROM information_schema.table_constraints
                WHERE table_schema = 'game_data'
                AND table_name = 'equipment_weapons'
                AND constraint_name = 'fk_weapons_effect_carrier'
                """
            )
            
            assert fk is not None, "fk_weapons_effect_carrier 제약조건이 없습니다"
            
            logger.info(f"[OK] game_data.equipment_weapons.effect_carrier_id FK 검증 성공")
    
    @pytest.mark.integration
    async def test_equipment_armors_effect_carrier_fk(self, db_connection):
        """game_data.equipment_armors 테이블의 effect_carrier_id FK 확인"""
        logger.info("[마이그레이션 테스트] game_data.equipment_armors.effect_carrier_id FK 확인")
        
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 컬럼 존재 확인
            column = await conn.fetchrow(
                """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'game_data'
                AND table_name = 'equipment_armors'
                AND column_name = 'effect_carrier_id'
                """
            )
            
            assert column is not None, "game_data.equipment_armors.effect_carrier_id 컬럼이 없습니다"
            assert column['data_type'] == 'uuid', f"effect_carrier_id 타입이 UUID가 아닙니다: {column['data_type']}"
            
            # FK 제약조건 확인
            fk = await conn.fetchrow(
                """
                SELECT constraint_name
                FROM information_schema.table_constraints
                WHERE table_schema = 'game_data'
                AND table_name = 'equipment_armors'
                AND constraint_name = 'fk_armors_effect_carrier'
                """
            )
            
            assert fk is not None, "fk_armors_effect_carrier 제약조건이 없습니다"
            
            logger.info(f"[OK] game_data.equipment_armors.effect_carrier_id FK 검증 성공")
    
    @pytest.mark.integration
    async def test_quests_table_insert(self, db_connection):
        """runtime_data.quests 테이블에 데이터 삽입 테스트"""
        logger.info("[마이그레이션 테스트] runtime_data.quests 테이블 데이터 삽입 테스트")
        
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 테스트 세션 생성
            session_id = await conn.fetchval(
                """
                INSERT INTO runtime_data.active_sessions (session_name, session_state)
                VALUES ('Test Session', 'active')
                RETURNING session_id
                """
            )
            
            try:
                # 퀘스트 삽입
                quest_id = await conn.fetchval(
                    """
                    INSERT INTO runtime_data.quests (
                        session_id,
                        quest_title,
                        quest_description,
                        quest_status,
                        quest_data
                    )
                    VALUES (
                        $1,
                        'Test Quest',
                        'This is a test quest',
                        'active',
                        '{"objectives": [{"id": 1, "description": "Kill 10 goblins", "completed": false}], "progress": {"goblins_killed": 0}}'::jsonb
                    )
                    RETURNING quest_id
                    """,
                    session_id
                )
                
                assert quest_id is not None, "퀘스트 삽입 실패"
                
                # 퀘스트 조회
                quest = await conn.fetchrow(
                    """
                    SELECT quest_id, quest_title, quest_status, quest_data
                    FROM runtime_data.quests
                    WHERE quest_id = $1
                    """,
                    quest_id
                )
                
                assert quest is not None, "퀘스트 조회 실패"
                assert quest['quest_title'] == 'Test Quest', "퀘스트 제목 불일치"
                assert quest['quest_status'] == 'active', "퀘스트 상태 불일치"
                
                logger.info(f"[OK] runtime_data.quests 테이블 데이터 삽입 테스트 성공")
            finally:
                # 정리
                await conn.execute(
                    "DELETE FROM runtime_data.quests WHERE session_id = $1",
                    session_id
                )
                await conn.execute(
                    "DELETE FROM runtime_data.active_sessions WHERE session_id = $1",
                    session_id
                )

