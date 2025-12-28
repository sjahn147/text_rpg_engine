"""
Effect Carrier 시스템 통합 테스트
MVP의 핵심 기능인 Effect Carrier 시스템 검증
"""

import pytest
import pytest_asyncio
import asyncio
import json
from typing import Dict, List, Any
from database.connection import DatabaseConnection
from common.utils.logger import logger

class TestEffectCarrierSystem:
    """Effect Carrier 시스템 테스트"""
    
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
    async def test_effect_carrier_table_exists(self, conn):
        """Effect Carrier 테이블 존재 확인"""
        # 테이블 존재 확인
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'game_data' 
            AND table_name = 'effect_carriers'
        """)
        
        assert len(tables) == 1, "effect_carriers 테이블이 존재하지 않습니다"
        
        # 컬럼 구조 확인
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'game_data' 
            AND table_name = 'effect_carriers'
            ORDER BY ordinal_position
        """)
        
        expected_columns = [
            'effect_id', 'name', 'carrier_type', 'effect_json', 
            'constraints_json', 'source_entity_id', 'tags', 
            'created_at', 'updated_at'
        ]
        
        actual_columns = [col['column_name'] for col in columns]
        for expected_col in expected_columns:
            assert expected_col in actual_columns, f"누락된 컬럼: {expected_col}"
        
        logger.info("✅ Effect Carrier 테이블 구조 확인 완료")
    
    @pytest.mark.asyncio
    async def test_entity_effect_ownership_table_exists(self, conn):
        """Entity Effect Ownership 테이블 존재 확인"""
        # 테이블 존재 확인
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'reference_layer' 
            AND table_name = 'entity_effect_ownership'
        """)
        
        assert len(tables) == 1, "entity_effect_ownership 테이블이 존재하지 않습니다"
        
        # 외래키 제약조건 확인
        fk_constraints = await conn.fetch("""
            SELECT 
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.table_schema = 'reference_layer'
            AND tc.table_name = 'entity_effect_ownership'
            AND tc.constraint_type = 'FOREIGN KEY'
        """)
        
        assert len(fk_constraints) >= 3, "필수 외래키 제약조건이 누락되었습니다"
        
        logger.info("✅ Entity Effect Ownership 테이블 구조 확인 완료")
    
    @pytest.mark.asyncio
    async def test_effect_carrier_sample_data(self, conn):
        """Effect Carrier 샘플 데이터 확인"""
        # 샘플 데이터 조회
        effects = await conn.fetch("""
            SELECT effect_id, name, carrier_type, effect_json, constraints_json, tags
            FROM game_data.effect_carriers
            ORDER BY carrier_type, name
        """)
        
        assert len(effects) >= 6, f"샘플 데이터 부족: {len(effects)}개 (최소 6개 필요)"
        
        # 타입별 데이터 확인
        carrier_types = [effect['carrier_type'] for effect in effects]
        expected_types = ['skill', 'buff', 'item', 'blessing', 'curse', 'ritual']
        
        for expected_type in expected_types:
            assert expected_type in carrier_types, f"누락된 Effect Carrier 타입: {expected_type}"
        
        # JSON 데이터 검증
        for effect in effects:
            effect_json = effect['effect_json']
            constraints_json = effect['constraints_json']
            tags = effect['tags']
            
            # JSONB 데이터 타입 처리
            if isinstance(effect_json, str):
                import json
                effect_json = json.loads(effect_json)
            if isinstance(constraints_json, str):
                import json
                constraints_json = json.loads(constraints_json)
            
            assert isinstance(effect_json, dict), f"effect_json이 딕셔너리가 아님: {effect['name']}"
            assert isinstance(constraints_json, dict), f"constraints_json이 딕셔너리가 아님: {effect['name']}"
            assert isinstance(tags, list), f"tags가 리스트가 아님: {effect['name']}"
        
        logger.info(f"✅ Effect Carrier 샘플 데이터 확인 완료: {len(effects)}개")
    
    @pytest.mark.asyncio
    async def test_effect_carrier_creation(self, conn):
        """Effect Carrier 생성 테스트"""
        # 새로운 Effect Carrier 생성
        await conn.execute("""
            INSERT INTO game_data.effect_carriers (name, carrier_type, effect_json, constraints_json, tags)
            VALUES ($1, $2, $3, $4, $5)
        """, 
        "Test Skill", "skill",
        '{"damage": 25, "range": 2, "cooldown": 3, "mana_cost": 5}',
        '{"level_required": 3, "class_required": ["warrior"]}',
        ['test', 'combat']
        )
        
        # 생성된 Effect Carrier 조회
        result = await conn.fetchrow("""
            SELECT * FROM game_data.effect_carriers 
            WHERE name = 'Test Skill'
        """)
        
        assert result is not None, "Effect Carrier 생성 실패"
        assert result['carrier_type'] == 'skill'
        
        # JSONB 데이터 타입 처리
        effect_json = result['effect_json']
        if isinstance(effect_json, str):
            import json
            effect_json = json.loads(effect_json)
        
        assert effect_json['damage'] == 25
        
        # 정리
        await conn.execute("DELETE FROM game_data.effect_carriers WHERE name = 'Test Skill'")
        
        logger.info("✅ Effect Carrier 생성 테스트 완료")
    
    @pytest.mark.asyncio
    async def test_effect_ownership_creation(self, conn):
        """Effect Ownership 생성 테스트"""
        # 테스트용 세션 생성
        await conn.execute("""
            INSERT INTO runtime_data.active_sessions (session_id, session_name, session_state, metadata)
            VALUES ($1, $2, $3, $4)
        """, 
        '00000000-0000-0000-0000-000000000009', 'Test Session', 'active', '{}'
        )
        
        # 테스트용 게임 엔티티 먼저 생성
        await conn.execute("""
            INSERT INTO game_data.entities (entity_id, entity_name, entity_type, entity_description, entity_properties)
            VALUES ($1, $2, $3, $4, $5)
        """,
        'TEST_ENTITY_001', 'Test Entity', 'npc', 'Test entity for ownership', '{"level": 1}'
        )
        
        # 테스트용 런타임 엔티티 생성
        await conn.execute("""
            INSERT INTO runtime_data.runtime_entities (runtime_entity_id, game_entity_id, session_id)
            VALUES ($1, $2, $3)
        """,
        '00000000-0000-0000-0000-000000000010', 'TEST_ENTITY_001', '00000000-0000-0000-0000-000000000009'
        )
        
        # Effect Carrier 조회 (첫 번째 스킬)
        effect = await conn.fetchrow("""
            SELECT effect_id FROM game_data.effect_carriers 
            WHERE carrier_type = 'skill' 
            LIMIT 1
        """)
        
        if effect:
            # Effect Ownership 생성
            await conn.execute("""
                INSERT INTO reference_layer.entity_effect_ownership 
                (session_id, runtime_entity_id, effect_id, source)
                VALUES ($1, $2, $3, $4)
            """,
            '00000000-0000-0000-0000-000000000009',
            '00000000-0000-0000-0000-000000000010',
            effect['effect_id'],
            'test_acquisition'
            )
            
            # 소유 관계 확인
            ownership = await conn.fetchrow("""
                SELECT * FROM reference_layer.entity_effect_ownership
                WHERE session_id = $1 AND runtime_entity_id = $2 AND effect_id = $3
            """,
            '00000000-0000-0000-0000-000000000009',
            '00000000-0000-0000-0000-000000000010',
            effect['effect_id']
            )
            
            assert ownership is not None, "Effect Ownership 생성 실패"
            assert ownership['source'] == 'test_acquisition'
            
            # 정리
            await conn.execute("""
                DELETE FROM reference_layer.entity_effect_ownership 
                WHERE session_id = $1 AND runtime_entity_id = $2
            """,
            '00000000-0000-0000-0000-000000000009',
            '00000000-0000-0000-0000-000000000010'
            )
            
            await conn.execute("DELETE FROM runtime_data.runtime_entities WHERE runtime_entity_id = '00000000-0000-0000-0000-000000000010'")
            await conn.execute("DELETE FROM game_data.entities WHERE entity_id = 'TEST_ENTITY_001'")
        
        # 정리
        await conn.execute("DELETE FROM runtime_data.active_sessions WHERE session_id = '00000000-0000-0000-0000-000000000009'")
        
        logger.info("✅ Effect Ownership 생성 테스트 완료")
    
    @pytest.mark.asyncio
    async def test_effect_carrier_json_validation(self, conn):
        """Effect Carrier JSON 데이터 검증"""
        # 스킬 Effect Carrier 조회
        skill_effect = await conn.fetchrow("""
            SELECT name, effect_json, constraints_json 
            FROM game_data.effect_carriers 
            WHERE carrier_type = 'skill' 
            LIMIT 1
        """)
        
        if skill_effect:
            effect_json = skill_effect['effect_json']
            constraints_json = skill_effect['constraints_json']
            
            # JSONB 데이터 타입 처리
            if isinstance(effect_json, str):
                import json
                effect_json = json.loads(effect_json)
            if isinstance(constraints_json, str):
                import json
                constraints_json = json.loads(constraints_json)
            
            # 스킬 필수 필드 확인
            required_fields = ['damage', 'range', 'cooldown']
            for field in required_fields:
                assert field in effect_json, f"스킬 필수 필드 누락: {field}"
                assert isinstance(effect_json[field], int), f"스킬 필드 타입 오류: {field}"
            
            # 제약 조건 확인
            if 'level_required' in constraints_json:
                assert isinstance(constraints_json['level_required'], int), "level_required 타입 오류"
            
            logger.info(f"✅ 스킬 Effect Carrier JSON 검증 완료: {skill_effect['name']}")
        
        # 버프 Effect Carrier 조회
        buff_effect = await conn.fetchrow("""
            SELECT name, effect_json, constraints_json 
            FROM game_data.effect_carriers 
            WHERE carrier_type = 'buff' 
            LIMIT 1
        """)
        
        if buff_effect:
            effect_json = buff_effect['effect_json']
            
            # JSONB 데이터 타입 처리
            if isinstance(effect_json, str):
                import json
                effect_json = json.loads(effect_json)
            
            # 버프 필수 필드 확인
            assert 'stat_modifier' in effect_json, "버프 stat_modifier 누락"
            assert 'duration' in effect_json, "버프 duration 누락"
            assert isinstance(effect_json['stat_modifier'], dict), "stat_modifier 타입 오류"
            assert isinstance(effect_json['duration'], int), "duration 타입 오류"
            
            logger.info(f"✅ 버프 Effect Carrier JSON 검증 완료: {buff_effect['name']}")
    
    @pytest.mark.asyncio
    async def test_effect_carrier_indexes(self, conn):
        """Effect Carrier 인덱스 확인"""
        # 인덱스 조회
        indexes = await conn.fetch("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE schemaname = 'game_data' 
            AND tablename = 'effect_carriers'
        """)
        
        index_names = [idx['indexname'] for idx in indexes]
        
        # 필수 인덱스 확인
        required_indexes = [
            'idx_effect_carriers_type',
            'idx_effect_carriers_effect_json',
            'idx_effect_carriers_constraints_json',
            'idx_effect_carriers_tags'
        ]
        
        for required_idx in required_indexes:
            assert required_idx in index_names, f"누락된 인덱스: {required_idx}"
        
        # GIN 인덱스 확인
        gin_indexes = [idx for idx in indexes if 'gin' in idx['indexdef'].lower()]
        assert len(gin_indexes) >= 3, f"GIN 인덱스 부족: {len(gin_indexes)}개"
        
        logger.info(f"✅ Effect Carrier 인덱스 확인 완료: {len(indexes)}개")
    
    @pytest.mark.asyncio
    async def test_effect_carrier_performance(self, conn):
        """Effect Carrier 성능 테스트"""
        # 대량 데이터 조회 성능 테스트
        start_time = asyncio.get_event_loop().time()
        
        # 타입별 조회
        for carrier_type in ['skill', 'buff', 'item', 'blessing', 'curse', 'ritual']:
            effects = await conn.fetch("""
                SELECT * FROM game_data.effect_carriers 
                WHERE carrier_type = $1
            """, carrier_type)
            assert len(effects) > 0, f"{carrier_type} 타입 데이터 없음"
        
        # JSONB 쿼리 성능 테스트
        json_effects = await conn.fetch("""
            SELECT * FROM game_data.effect_carriers 
            WHERE effect_json @> '{"damage": 50}'
        """)
        
        # 태그 검색 성능 테스트
        tagged_effects = await conn.fetch("""
            SELECT * FROM game_data.effect_carriers 
            WHERE tags @> ARRAY['combat']
        """)
        
        end_time = asyncio.get_event_loop().time()
        execution_time = end_time - start_time
        
        assert execution_time < 1.0, f"성능 테스트 실패: {execution_time:.3f}초"
        
        logger.info(f"✅ Effect Carrier 성능 테스트 완료: {execution_time:.3f}초")
    
    @pytest.mark.asyncio
    async def test_effect_carrier_constraints(self, conn):
        """Effect Carrier 제약조건 테스트"""
        # 잘못된 carrier_type 시도
        with pytest.raises(Exception):
            await conn.execute("""
                INSERT INTO game_data.effect_carriers (name, carrier_type, effect_json)
                VALUES ($1, $2, $3)
            """, "Invalid Effect", "invalid_type", '{}')
        
        # 필수 필드 누락 시도
        with pytest.raises(Exception):
            await conn.execute("""
                INSERT INTO game_data.effect_carriers (carrier_type, effect_json)
                VALUES ($1, $2)
            """, "skill", '{}')
        
        logger.info("✅ Effect Carrier 제약조건 테스트 완료")

class TestEffectCarrierIntegration:
    """Effect Carrier 통합 테스트"""
    
    @pytest_asyncio.fixture
    async def db_connection(self):
        """데이터베이스 연결 픽스처"""
        db = DatabaseConnection()
        # 연결 풀 초기화
        await db.pool
        yield db
        await db.close()
    
    @pytest.mark.asyncio
    async def test_full_effect_carrier_workflow(self, db_connection):
        """전체 Effect Carrier 워크플로우 테스트"""
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 1. 세션 생성
            await conn.execute("""
                INSERT INTO runtime_data.active_sessions (session_id, session_name, session_state, metadata)
                VALUES ($1, $2, $3, $4)
            """, 
            '00000000-0000-0000-0000-000000000011', 'Effect Test Session', 'active', '{}'
            )
            
            # 2. 게임 엔티티 생성
            await conn.execute("""
                INSERT INTO game_data.entities (entity_id, entity_name, entity_type, entity_description, entity_properties)
                VALUES ($1, $2, $3, $4, $5)
            """,
            'TEST_PLAYER_001', 'Test Player', 'player', 'Effect Carrier 테스트용 플레이어', '{"level": 5}'
            )
            
            # 3. 런타임 엔티티 생성
            await conn.execute("""
                INSERT INTO runtime_data.runtime_entities (runtime_entity_id, game_entity_id, session_id)
                VALUES ($1, $2, $3)
            """,
            '00000000-0000-0000-0000-000000000012', 'TEST_PLAYER_001', '00000000-0000-0000-0000-000000000011'
            )
            
            # 4. Effect Carrier 조회
            skill_effect = await conn.fetchrow("""
                SELECT effect_id, name, effect_json FROM game_data.effect_carriers 
                WHERE carrier_type = 'skill' 
                LIMIT 1
            """)
            
            if skill_effect:
                # 5. Effect Ownership 생성
                await conn.execute("""
                    INSERT INTO reference_layer.entity_effect_ownership 
                    (session_id, runtime_entity_id, effect_id, source)
                    VALUES ($1, $2, $3, $4)
                """,
                '00000000-0000-0000-0000-000000000011',
                '00000000-0000-0000-0000-000000000012',
                skill_effect['effect_id'],
                'quest_reward'
                )
                
                # 6. 통합 조회 테스트
                result = await conn.fetchrow("""
                    SELECT 
                        e.entity_name,
                        ec.name as effect_name,
                        ec.carrier_type,
                        ec.effect_json,
                        eo.acquired_at,
                        eo.source
                    FROM game_data.entities e
                    JOIN runtime_data.runtime_entities re ON e.entity_id = re.game_entity_id
                    JOIN reference_layer.entity_effect_ownership eo ON re.runtime_entity_id = eo.runtime_entity_id
                    JOIN game_data.effect_carriers ec ON eo.effect_id = ec.effect_id
                    WHERE e.entity_id = $1
                """, 'TEST_PLAYER_001')
                
                assert result is not None, "통합 조회 실패"
                assert result['entity_name'] == 'Test Player'
                assert result['effect_name'] == skill_effect['name']
                assert result['carrier_type'] == 'skill'
                assert result['source'] == 'quest_reward'
                
                logger.info(f"✅ 전체 Effect Carrier 워크플로우 완료: {result['entity_name']} -> {result['effect_name']}")
            
            # 정리
            await conn.execute("DELETE FROM reference_layer.entity_effect_ownership WHERE session_id = '00000000-0000-0000-0000-000000000011'")
            await conn.execute("DELETE FROM runtime_data.runtime_entities WHERE runtime_entity_id = '00000000-0000-0000-0000-000000000012'")
            await conn.execute("DELETE FROM runtime_data.active_sessions WHERE session_id = '00000000-0000-0000-0000-000000000011'")
            await conn.execute("DELETE FROM game_data.entities WHERE entity_id = 'TEST_PLAYER_001'")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
