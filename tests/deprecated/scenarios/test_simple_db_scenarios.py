"""
간단한 실제 DB 연결을 통한 시나리오 테스트
복잡한 Manager 클래스 대신 직접 DB 쿼리 사용
"""
import pytest
import pytest_asyncio
import asyncio
import uuid
from datetime import datetime
from database.connection import DatabaseConnection
from common.utils.logger import logger


class TestSimpleDBScenarios:
    """간단한 실제 DB 연결을 통한 시나리오 테스트"""
    
    @pytest_asyncio.fixture(scope="class")
    async def db_connection(self):
        """실제 DB 연결"""
        db = DatabaseConnection()
        await db.initialize()
        yield db
        await db.close()
    
    @pytest_asyncio.fixture(scope="class")
    async def test_session(self, db_connection):
        """테스트용 세션 생성"""
        session_id = str(uuid.uuid4())
        
        # 테스트 세션을 DB에 생성
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO runtime_data.active_sessions (session_id, session_name, session_state, created_at)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (session_id) DO NOTHING
            """, session_id, "test-session", "active", datetime.now())
        
        return session_id
    
    @pytest.mark.asyncio
    async def test_db_connection_scenario(self, db_connection):
        """DB 연결 시나리오 - 기본 연결 테스트"""
        logger.info("=== DB 연결 시나리오 시작 ===")
        
        # 1. DB 연결 확인
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            assert result == 1, "DB 연결 실패"
        
        logger.info("[SUCCESS] DB 연결 확인 완료")
        
        # 2. 스키마 확인
        async with pool.acquire() as conn:
            # game_data 스키마 확인
            game_data_tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'game_data'
                ORDER BY table_name
            """)
            
            assert len(game_data_tables) > 0, "game_data 스키마가 없습니다"
            logger.info(f"[SUCCESS] game_data 스키마 확인: {len(game_data_tables)}개 테이블")
            
            # runtime_data 스키마 확인
            runtime_data_tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'runtime_data'
                ORDER BY table_name
            """)
            
            assert len(runtime_data_tables) > 0, "runtime_data 스키마가 없습니다"
            logger.info(f"[SUCCESS] runtime_data 스키마 확인: {len(runtime_data_tables)}개 테이블")
            
            # reference_layer 스키마 확인
            reference_layer_tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'reference_layer'
                ORDER BY table_name
            """)
            
            assert len(reference_layer_tables) > 0, "reference_layer 스키마가 없습니다"
            logger.info(f"[SUCCESS] reference_layer 스키마 확인: {len(reference_layer_tables)}개 테이블")
        
        logger.info("=== DB 연결 시나리오 완료 ===")
    
    @pytest.mark.asyncio
    async def test_entity_data_scenario(self, db_connection, test_session):
        """엔티티 데이터 시나리오 - 정적 데이터 조회"""
        logger.info("=== 엔티티 데이터 시나리오 시작 ===")
        
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 1. 정적 엔티티 템플릿 조회
            entities = await conn.fetch("""
                SELECT entity_id, entity_type, entity_name, entity_description
                FROM game_data.entities
                ORDER BY entity_id
                LIMIT 10
            """)
            
            assert len(entities) > 0, "정적 엔티티 템플릿이 없습니다"
            logger.info(f"[SUCCESS] 정적 엔티티 템플릿 조회: {len(entities)}개")
            
            # 2. 특정 엔티티 상세 정보 조회
            if entities:
                entity_id = entities[0]['entity_id']
                entity_detail = await conn.fetchrow("""
                    SELECT * FROM game_data.entities WHERE entity_id = $1
                """, entity_id)
                
                assert entity_detail is not None, f"엔티티 {entity_id} 상세 정보 조회 실패"
                logger.info(f"[SUCCESS] 엔티티 상세 정보 조회: {entity_detail['entity_name']}")
        
        logger.info("=== 엔티티 데이터 시나리오 완료 ===")
    
    @pytest.mark.asyncio
    async def test_cell_data_scenario(self, db_connection, test_session):
        """셀 데이터 시나리오 - 정적 셀 데이터 조회"""
        logger.info("=== 셀 데이터 시나리오 시작 ===")
        
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 1. 정적 셀 템플릿 조회
            cells = await conn.fetch("""
                SELECT cell_id, cell_name, cell_type, cell_description
                FROM game_data.world_cells
                ORDER BY cell_id
                LIMIT 10
            """)
            
            assert len(cells) > 0, "정적 셀 템플릿이 없습니다"
            logger.info(f"[SUCCESS] 정적 셀 템플릿 조회: {len(cells)}개")
            
            # 2. 특정 셀 상세 정보 조회
            if cells:
                cell_id = cells[0]['cell_id']
                cell_detail = await conn.fetchrow("""
                    SELECT * FROM game_data.world_cells WHERE cell_id = $1
                """, cell_id)
                
                assert cell_detail is not None, f"셀 {cell_id} 상세 정보 조회 실패"
                logger.info(f"[SUCCESS] 셀 상세 정보 조회: {cell_detail['cell_name']}")
        
        logger.info("=== 셀 데이터 시나리오 완료 ===")
    
    @pytest.mark.asyncio
    async def test_dialogue_data_scenario(self, db_connection, test_session):
        """대화 데이터 시나리오 - 대화 컨텍스트 조회"""
        logger.info("=== 대화 데이터 시나리오 시작 ===")
        
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 1. 대화 컨텍스트 조회
            dialogue_contexts = await conn.fetch("""
                SELECT dialogue_id, title, content, available_topics
                FROM game_data.dialogue_contexts
                ORDER BY priority DESC
                LIMIT 10
            """)
            
            assert len(dialogue_contexts) > 0, "대화 컨텍스트가 없습니다"
            logger.info(f"[SUCCESS] 대화 컨텍스트 조회: {len(dialogue_contexts)}개")
            
            # 2. 대화 주제 조회
            dialogue_topics = await conn.fetch("""
                SELECT topic_type, topic_name, description
                FROM game_data.dialogue_topics
                ORDER BY priority DESC
                LIMIT 10
            """)
            
            assert len(dialogue_topics) > 0, "대화 주제가 없습니다"
            logger.info(f"[SUCCESS] 대화 주제 조회: {len(dialogue_topics)}개")
        
        logger.info("=== 대화 데이터 시나리오 완료 ===")
    
    @pytest.mark.asyncio
    async def test_session_data_scenario(self, db_connection, test_session):
        """세션 데이터 시나리오 - 런타임 데이터 조회"""
        logger.info("=== 세션 데이터 시나리오 시작 ===")
        
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 1. 활성 세션 조회
            sessions = await conn.fetch("""
                SELECT session_id, session_name, session_state, created_at
                FROM runtime_data.active_sessions
                WHERE session_state = 'active'
                ORDER BY created_at DESC
            """)
            
            assert len(sessions) > 0, "활성 세션이 없습니다"
            logger.info(f"[SUCCESS] 활성 세션 조회: {len(sessions)}개")
            
            # 2. 테스트 세션 확인
            test_session_found = False
            for session in sessions:
                if session['session_id'] == test_session:
                    test_session_found = True
                    break
            
            assert test_session_found, f"테스트 세션 {test_session}을 찾을 수 없습니다"
            logger.info(f"[SUCCESS] 테스트 세션 확인: {test_session}")
        
        logger.info("=== 세션 데이터 시나리오 완료 ===")
    
    @pytest.mark.asyncio
    async def test_full_data_flow_scenario(self, db_connection, test_session):
        """전체 데이터 플로우 시나리오 - 3계층 설계 검증"""
        logger.info("=== 전체 데이터 플로우 시나리오 시작 ===")
        
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 1. game_data → reference_layer → runtime_data 플로우 확인
            
            # game_data에서 정적 엔티티 조회
            static_entities = await conn.fetch("""
                SELECT entity_id, entity_name, entity_type
                FROM game_data.entities
                WHERE entity_type = 'npc'
                LIMIT 5
            """)
            
            assert len(static_entities) > 0, "정적 NPC 엔티티가 없습니다"
            logger.info(f"[SUCCESS] 정적 NPC 엔티티 조회: {len(static_entities)}개")
            
            # 2. reference_layer 테이블 확인
            entity_references = await conn.fetch("""
                SELECT COUNT(*) as count
                FROM reference_layer.entity_references
            """)
            
            logger.info(f"[SUCCESS] 엔티티 참조 레이어: {entity_references[0]['count']}개")
            
            # 3. runtime_data 테이블 확인
            runtime_entities = await conn.fetch("""
                SELECT COUNT(*) as count
                FROM runtime_data.runtime_entities
            """)
            
            logger.info(f"[SUCCESS] 런타임 엔티티: {runtime_entities[0]['count']}개")
            
            # 4. 세션별 데이터 확인
            session_data = await conn.fetch("""
                SELECT 
                    s.session_id,
                    s.session_name,
                    s.session_state,
                    COUNT(re.runtime_entity_id) as entity_count,
                    COUNT(rc.runtime_cell_id) as cell_count
                FROM runtime_data.active_sessions s
                LEFT JOIN runtime_data.runtime_entities re ON s.session_id = re.session_id
                LEFT JOIN runtime_data.runtime_cells rc ON s.session_id = rc.session_id
                WHERE s.session_id = $1
                GROUP BY s.session_id, s.session_name, s.session_state
            """, test_session)
            
            assert len(session_data) > 0, f"세션 {test_session} 데이터가 없습니다"
            session_info = session_data[0]
            logger.info(f"[SUCCESS] 세션 데이터 확인: {session_info['entity_count']}개 엔티티, {session_info['cell_count']}개 셀")
        
        logger.info("=== 전체 데이터 플로우 시나리오 완료 ===")
