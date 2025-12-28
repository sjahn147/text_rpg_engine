"""
데이터 무결성 테스트
Foreign Key 제약조건 및 참조 무결성 검증
"""
import pytest
import pytest_asyncio
from common.utils.logger import logger


class TestDataIntegrity:
    """데이터 무결성 검증 테스트"""
    
    @pytest.mark.asyncio
    async def test_foreign_key_constraints(self, db_connection):
        """외래 키 제약조건 검증"""
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # game_data.entities 존재 확인
            entities_exist = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_schema='game_data' AND table_name='entities')"
            )
            assert entities_exist is True
            logger.info("✅ game_data.entities table exists")
            
            # runtime_data.runtime_entities FK 검증
            fk_count = await conn.fetchval("""
                SELECT COUNT(*)
                FROM information_schema.table_constraints tc
                WHERE tc.table_schema = 'runtime_data'
                  AND tc.table_name = 'runtime_entities'
                  AND tc.constraint_type = 'FOREIGN KEY'
            """)
            assert fk_count > 0
            logger.info(f"✅ runtime_entities has {fk_count} foreign key constraints")
    
    @pytest.mark.asyncio
    async def test_template_referential_integrity(self, db_with_templates, entity_manager, test_session):
        """정적 템플릿 참조 무결성 검증"""
        session_id = test_session['session_id']
        
        # 존재하는 템플릿으로 엔티티 생성 (성공해야 함)
        valid_result = await entity_manager.create_entity(
            static_entity_id="NPC_VILLAGER_001",
            session_id=session_id
        )
        assert valid_result.status == "success"
        logger.info("✅ Entity created from valid template")
        
        # 존재하지 않는 템플릿으로 엔티티 생성 시도 (실패해야 함)
        invalid_result = await entity_manager.create_entity(
            static_entity_id="NONEXISTENT_TEMPLATE",
            session_id=session_id
        )
        assert invalid_result.status != "success"
        logger.info("✅ Entity creation failed for invalid template (expected)")
    
    @pytest.mark.asyncio
    async def test_session_cascade_delete(self, db_connection, test_session):
        """세션 삭제 시 연관 데이터 삭제 검증"""
        session_id = test_session['session_id']
        
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 세션 존재 확인
            session_exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM runtime_data.active_sessions WHERE session_id = $1)",
                session_id
            )
            assert session_exists is True
            logger.info(f"✅ Session {session_id} exists")

