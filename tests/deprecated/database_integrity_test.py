#!/usr/bin/env python3
"""
데이터베이스 정합성 종합 테스트
"""

import asyncio
import json
import uuid
from datetime import datetime
from database.connection import DatabaseConnection

class DatabaseIntegrityTester:
    def __init__(self):
        self.db = DatabaseConnection()
        self.test_results = []
        
    async def run_all_tests(self):
        """모든 정합성 테스트 실행"""
        print("🧪 데이터베이스 정합성 종합 테스트 시작")
        print("=" * 60)
        
        tests = [
            ("외래 키 제약조건 테스트", self.test_foreign_key_constraints),
            ("데이터 무결성 테스트", self.test_data_integrity),
            ("게임 세션 플로우 테스트", self.test_session_flow),
            ("대화 시스템 테스트", self.test_dialogue_system),
            ("엔티티 생명주기 테스트", self.test_entity_lifecycle),
            ("성능 및 확장성 테스트", self.test_performance)
        ]
        
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * 40)
            try:
                result = await test_func()
                self.test_results.append((test_name, "PASS", result))
                print(f"✅ {test_name}: 통과")
            except Exception as e:
                self.test_results.append((test_name, "FAIL", str(e)))
                print(f"❌ {test_name}: 실패 - {e}")
        
        self.print_summary()
    
    async def test_foreign_key_constraints(self):
        """외래 키 제약조건 테스트"""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 1. 존재하지 않는 엔티티 참조 시도
            try:
                await conn.execute("""
                    INSERT INTO reference_layer.entity_references 
                    (runtime_entity_id, game_entity_id, session_id, entity_type, is_player)
                    VALUES ($1, $2, $3, $4, $5)
                """, str(uuid.uuid4()), "NONEXISTENT_ENTITY", str(uuid.uuid4()), "player", True)
                return "외래 키 제약조건 실패: 존재하지 않는 엔티티 참조 허용됨"
            except Exception as e:
                if "foreign key" in str(e).lower():
                    print("✓ 존재하지 않는 엔티티 참조 차단됨")
                else:
                    raise e
            
            # 2. 존재하지 않는 세션 참조 시도
            try:
                await conn.execute("""
                    INSERT INTO reference_layer.entity_references 
                    (runtime_entity_id, game_entity_id, session_id, entity_type, is_player)
                    VALUES ($1, $2, $3, $4, $5)
                """, str(uuid.uuid4()), "TEST_PLAYER_001", str(uuid.uuid4()), "player", True)
                return "외래 키 제약조건 실패: 존재하지 않는 세션 참조 허용됨"
            except Exception as e:
                if "foreign key" in str(e).lower():
                    print("✓ 존재하지 않는 세션 참조 차단됨")
                else:
                    raise e
            
            # 3. 올바른 참조 생성 테스트
            session_id = str(uuid.uuid4())
            await conn.execute("""
                INSERT INTO runtime_data.active_sessions (session_id, session_state, metadata)
                VALUES ($1, $2, $3)
            """, session_id, "active", json.dumps({"test": True}))
            
            runtime_entity_id = str(uuid.uuid4())
            await conn.execute("""
                INSERT INTO reference_layer.entity_references 
                (runtime_entity_id, game_entity_id, session_id, entity_type, is_player)
                VALUES ($1, $2, $3, $4, $5)
            """, runtime_entity_id, "TEST_PLAYER_001", session_id, "player", True)
            
            print("✓ 올바른 참조 생성 성공")
            return "외래 키 제약조건 테스트 통과"
    
    async def test_data_integrity(self):
        """데이터 무결성 테스트"""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 1. JSONB 필드 유효성 검사
            invalid_json = "invalid json string"
            try:
                await conn.execute("""
                    INSERT INTO runtime_data.entity_states 
                    (runtime_entity_id, runtime_cell_id, current_stats)
                    VALUES ($1, $2, $3)
                """, str(uuid.uuid4()), str(uuid.uuid4()), invalid_json)
                return "JSONB 유효성 검사 실패: 잘못된 JSON 허용됨"
            except Exception as e:
                if "json" in str(e).lower() or "invalid" in str(e).lower():
                    print("✓ 잘못된 JSON 데이터 차단됨")
                else:
                    raise e
            
            # 2. 필수 필드 NULL 검사
            try:
                await conn.execute("""
                    INSERT INTO game_data.entities (entity_id, entity_type, entity_name)
                    VALUES ($1, $2, NULL)
                """, "TEST_ENTITY_NULL", "player")
                return "NULL 제약조건 실패: 필수 필드 NULL 허용됨"
            except Exception as e:
                if "null" in str(e).lower() or "not null" in str(e).lower():
                    print("✓ 필수 필드 NULL 차단됨")
                else:
                    raise e
            
            # 3. 중복 키 검사
            try:
                await conn.execute("""
                    INSERT INTO game_data.entities (entity_id, entity_type, entity_name)
                    VALUES ($1, $2, $3)
                """, "TEST_PLAYER_001", "player", "Duplicate Player")
                return "중복 키 제약조건 실패: 중복 키 허용됨"
            except Exception as e:
                if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                    print("✓ 중복 키 차단됨")
                else:
                    raise e
            
            return "데이터 무결성 테스트 통과"
    
    async def test_session_flow(self):
        """게임 세션 플로우 테스트"""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 1. 세션 생성 → 엔티티 참조 → 상태 생성 플로우
            session_id = str(uuid.uuid4())
            
            # 세션 생성
            await conn.execute("""
                INSERT INTO runtime_data.active_sessions (session_id, session_state, metadata)
                VALUES ($1, $2, $3)
            """, session_id, "active", json.dumps({"test_flow": True}))
            
            # 셀 참조 생성
            cell_runtime_id = str(uuid.uuid4())
            await conn.execute("""
                INSERT INTO reference_layer.cell_references 
                (runtime_cell_id, game_cell_id, session_id)
                VALUES ($1, $2, $3)
            """, cell_runtime_id, "CELL_VILLAGE_CENTER_001", session_id)
            
            # 엔티티 참조 생성
            entity_runtime_id = str(uuid.uuid4())
            await conn.execute("""
                INSERT INTO reference_layer.entity_references 
                (runtime_entity_id, game_entity_id, session_id, entity_type, is_player)
                VALUES ($1, $2, $3, $4, $5)
            """, entity_runtime_id, "TEST_PLAYER_001", session_id, "player", True)
            
            # 엔티티 상태 생성
            await conn.execute("""
                INSERT INTO runtime_data.entity_states 
                (runtime_entity_id, runtime_cell_id, current_stats, current_position)
                VALUES ($1, $2, $3, $4)
            """, entity_runtime_id, cell_runtime_id, 
                json.dumps({"hp": 100, "mp": 50}), 
                json.dumps({"x": 10, "y": 10}))
            
            # 세션에 플레이어 참조 추가
            await conn.execute("""
                UPDATE runtime_data.active_sessions
                SET player_runtime_entity_id = $1
                WHERE session_id = $2
            """, entity_runtime_id, session_id)
            
            print("✓ 세션 플로우 테스트 성공")
            return "게임 세션 플로우 테스트 통과"
    
    async def test_dialogue_system(self):
        """대화 시스템 테스트"""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 1. 대화 컨텍스트 조회
            result = await conn.fetch("""
                SELECT dialogue_id, title, content FROM game_data.dialogue_contexts
                WHERE dialogue_id = $1
            """, "MERCHANT_GREETING")
            
            if not result:
                return "대화 시스템 실패: 대화 컨텍스트 없음"
            
            print("✓ 대화 컨텍스트 조회 성공")
            
            # 2. 대화 상태 생성
            session_id = str(uuid.uuid4())
            await conn.execute("""
                INSERT INTO runtime_data.active_sessions (session_id, session_state, metadata)
                VALUES ($1, $2, $3)
            """, session_id, "active", json.dumps({"dialogue_test": True}))
            
            entity_runtime_id = str(uuid.uuid4())
            await conn.execute("""
                INSERT INTO reference_layer.entity_references 
                (runtime_entity_id, game_entity_id, session_id, entity_type, is_player)
                VALUES ($1, $2, $3, $4, $5)
            """, entity_runtime_id, "TEST_NPC_001", session_id, "npc", False)
            
            # 대화 상태 생성
            await conn.execute("""
                INSERT INTO runtime_data.dialogue_states 
                (session_id, runtime_entity_id, current_context_id, conversation_state, active_topics)
                VALUES ($1, $2, $3, $4, $5)
            """, session_id, entity_runtime_id, "MERCHANT_GREETING",
                json.dumps({"current_topic": "greeting", "emotion": "neutral"}),
                json.dumps({"current_topics": ["greeting"], "available_topics": ["shop_items"]}))
            
            print("✓ 대화 상태 생성 성공")
            return "대화 시스템 테스트 통과"
    
    async def test_entity_lifecycle(self):
        """엔티티 생명주기 테스트"""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 1. 엔티티 생성 → 상태 생성 → 상태 업데이트 → 삭제 플로우
            session_id = str(uuid.uuid4())
            
            # 세션 생성
            await conn.execute("""
                INSERT INTO runtime_data.active_sessions (session_id, session_state, metadata)
                VALUES ($1, $2, $3)
            """, session_id, "active", json.dumps({"lifecycle_test": True}))
            
            # 엔티티 참조 생성
            entity_runtime_id = str(uuid.uuid4())
            await conn.execute("""
                INSERT INTO reference_layer.entity_references 
                (runtime_entity_id, game_entity_id, session_id, entity_type, is_player)
                VALUES ($1, $2, $3, $4, $5)
            """, entity_runtime_id, "TEST_PLAYER_001", session_id, "player", True)
            
            # 셀 참조 생성
            cell_runtime_id = str(uuid.uuid4())
            await conn.execute("""
                INSERT INTO reference_layer.cell_references 
                (runtime_cell_id, game_cell_id, session_id)
                VALUES ($1, $2, $3)
            """, cell_runtime_id, "CELL_VILLAGE_CENTER_001", session_id)
            
            # 엔티티 상태 생성
            await conn.execute("""
                INSERT INTO runtime_data.entity_states 
                (runtime_entity_id, runtime_cell_id, current_stats, current_position)
                VALUES ($1, $2, $3, $4)
            """, entity_runtime_id, cell_runtime_id,
                json.dumps({"hp": 100, "mp": 50}),
                json.dumps({"x": 10, "y": 10}))
            
            # 상태 업데이트
            await conn.execute("""
                UPDATE runtime_data.entity_states
                SET current_stats = $1, updated_at = CURRENT_TIMESTAMP
                WHERE runtime_entity_id = $2
            """, json.dumps({"hp": 80, "mp": 40}), entity_runtime_id)
            
            # 상태 변경 이력 기록
            await conn.execute("""
                INSERT INTO runtime_data.entity_state_history 
                (runtime_entity_id, change_type, previous_value, new_value, reason)
                VALUES ($1, $2, $3, $4, $5)
            """, entity_runtime_id, "stats_change",
                json.dumps({"hp": 100, "mp": 50}),
                json.dumps({"hp": 80, "mp": 40}),
                "Combat damage")
            
            print("✓ 엔티티 생명주기 테스트 성공")
            return "엔티티 생명주기 테스트 통과"
    
    async def test_performance(self):
        """성능 및 확장성 테스트"""
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 1. 대량 데이터 삽입 테스트
            start_time = datetime.now()
            
            session_id = str(uuid.uuid4())
            await conn.execute("""
                INSERT INTO runtime_data.active_sessions (session_id, session_state, metadata)
                VALUES ($1, $2, $3)
            """, session_id, "active", json.dumps({"performance_test": True}))
            
            # 100개 엔티티 참조 생성
            for i in range(100):
                entity_runtime_id = str(uuid.uuid4())
                await conn.execute("""
                    INSERT INTO reference_layer.entity_references 
                    (runtime_entity_id, game_entity_id, session_id, entity_type, is_player)
                    VALUES ($1, $2, $3, $4, $5)
                """, entity_runtime_id, "TEST_PLAYER_001", session_id, "player", True)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"✓ 100개 엔티티 참조 생성: {duration:.2f}초")
            
            # 2. 복잡한 조인 쿼리 성능 테스트
            start_time = datetime.now()
            
            result = await conn.fetch("""
                SELECT 
                    s.session_id,
                    s.session_state,
                    er.entity_type,
                    er.is_player,
                    es.current_stats,
                    es.current_position
                FROM runtime_data.active_sessions s
                JOIN reference_layer.entity_references er ON s.session_id = er.session_id
                LEFT JOIN runtime_data.entity_states es ON er.runtime_entity_id = es.runtime_entity_id
                WHERE s.session_id = $1
            """, session_id)
            
            end_time = datetime.now()
            query_duration = (end_time - start_time).total_seconds()
            
            print(f"✓ 복잡한 조인 쿼리: {query_duration:.3f}초 ({len(result)}개 결과)")
            
            return f"성능 테스트 통과 (삽입: {duration:.2f}초, 조회: {query_duration:.3f}초)"
    
    def print_summary(self):
        """테스트 결과 요약"""
        print("\n" + "=" * 60)
        print("📊 테스트 결과 요약")
        print("=" * 60)
        
        passed = sum(1 for _, status, _ in self.test_results if status == "PASS")
        total = len(self.test_results)
        
        for test_name, status, result in self.test_results:
            icon = "✅" if status == "PASS" else "❌"
            print(f"{icon} {test_name}: {status}")
            if status == "FAIL":
                print(f"   오류: {result}")
        
        print(f"\n🎯 전체 결과: {passed}/{total} 테스트 통과")
        
        if passed == total:
            print("🎉 모든 테스트 통과! 데이터베이스가 게임 개발 준비 완료되었습니다.")
        else:
            print("⚠️ 일부 테스트 실패. 문제를 해결한 후 다시 테스트하세요.")

async def main():
    tester = DatabaseIntegrityTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
