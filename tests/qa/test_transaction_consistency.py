"""
트랜잭션 일관성 QA 테스트

P1 (High): 트랜잭션 전후 데이터 일관성 검증
"""
import pytest
import pytest_asyncio
import uuid
import json
from typing import Dict, Any
from common.utils.logger import logger


@pytest.mark.asyncio
class TestTransactionConsistency:
    """트랜잭션 일관성 테스트"""
    
    async def test_transaction_consistency_game_start(
        self,
        db_connection,
        game_service,
        test_game_data
    ):
        """
        P1-5: 게임 시작 트랜잭션 일관성 검증
        
        검증 항목:
        - 트랜잭션 전후 데이터 일관성
        - 외래키 제약조건 일관성
        - SSOT 일관성
        """
        logger.info("[P1-5] 게임 시작 트랜잭션 일관성 검증 테스트 시작")
        
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 트랜잭션 전 상태 확인
            before_sessions = await conn.fetch("""
                SELECT COUNT(*) as count FROM runtime_data.active_sessions
            """)
            before_cells = await conn.fetch("""
                SELECT COUNT(*) as count FROM runtime_data.runtime_cells
            """)
            before_entities = await conn.fetch("""
                SELECT COUNT(*) as count FROM runtime_data.runtime_entities
            """)
            before_cell_refs = await conn.fetch("""
                SELECT COUNT(*) as count FROM reference_layer.cell_references
            """)
            before_entity_refs = await conn.fetch("""
                SELECT COUNT(*) as count FROM reference_layer.entity_references
            """)
        
        # 게임 시작
        result = await game_service.start_game(
            player_template_id=test_game_data["player_template_id"],
            start_cell_id=test_game_data["cell_id"]
        )
        
        session_id = result["game_state"]["session_id"]
        player_id = result["game_state"]["player_id"]
        current_cell_id = result["game_state"]["current_cell_id"]
        
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 트랜잭션 후 상태 확인
            after_sessions = await conn.fetch("""
                SELECT COUNT(*) as count FROM runtime_data.active_sessions
            """)
            after_cells = await conn.fetch("""
                SELECT COUNT(*) as count FROM runtime_data.runtime_cells
            """)
            after_entities = await conn.fetch("""
                SELECT COUNT(*) as count FROM runtime_data.runtime_entities
            """)
            after_cell_refs = await conn.fetch("""
                SELECT COUNT(*) as count FROM reference_layer.cell_references
            """)
            after_entity_refs = await conn.fetch("""
                SELECT COUNT(*) as count FROM reference_layer.entity_references
            """)
            
            # 세션 증가 확인
            assert after_sessions[0]["count"] == before_sessions[0]["count"] + 1, \
                "세션이 1개 증가해야 함"
            
            # 셀 인스턴스 증가 확인
            assert after_cells[0]["count"] == before_cells[0]["count"] + 1, \
                "셀 인스턴스가 1개 증가해야 함"
            
            # 엔티티 인스턴스 증가 확인
            assert after_entities[0]["count"] == before_entities[0]["count"] + 1, \
                "엔티티 인스턴스가 1개 증가해야 함"
            
            # 셀 참조 증가 확인
            assert after_cell_refs[0]["count"] == before_cell_refs[0]["count"] + 1, \
                "셀 참조가 1개 증가해야 함"
            
            # 엔티티 참조 증가 확인
            assert after_entity_refs[0]["count"] == before_entity_refs[0]["count"] + 1, \
                "엔티티 참조가 1개 증가해야 함"
            
            # 외래키 제약조건 일관성 확인
            # cell_references의 모든 runtime_cell_id가 runtime_cells에 존재하는지 확인
            cell_refs_check = await conn.fetchrow("""
                SELECT COUNT(*) as count
                FROM reference_layer.cell_references cr
                WHERE NOT EXISTS (
                    SELECT 1 FROM runtime_data.runtime_cells rc
                    WHERE rc.runtime_cell_id = cr.runtime_cell_id
                )
            """)
            assert cell_refs_check["count"] == 0, \
                "cell_references의 모든 runtime_cell_id가 runtime_cells에 존재해야 함"
            
            # entity_references의 모든 runtime_entity_id가 runtime_entities에 존재하는지 확인
            entity_refs_check = await conn.fetchrow("""
                SELECT COUNT(*) as count
                FROM reference_layer.entity_references er
                WHERE NOT EXISTS (
                    SELECT 1 FROM runtime_data.runtime_entities re
                    WHERE re.runtime_entity_id = er.runtime_entity_id
                )
            """)
            assert entity_refs_check["count"] == 0, \
                "entity_references의 모든 runtime_entity_id가 runtime_entities에 존재해야 함"
            
            # SSOT 일관성 확인 (현재 세션의 플레이어만 확인)
            # entity_states.current_position과 cell_occupants 일치 확인
            ssot_check = await conn.fetchrow("""
                SELECT COUNT(*) as count
                FROM runtime_data.entity_states es
                WHERE es.runtime_entity_id = $1
                  AND es.current_position->>'runtime_cell_id' IS NOT NULL
                  AND NOT EXISTS (
                      SELECT 1 FROM runtime_data.cell_occupants co
                      WHERE co.runtime_entity_id = es.runtime_entity_id
                        AND co.runtime_cell_id::text = es.current_position->>'runtime_cell_id'
                  )
            """, player_id)
            assert ssot_check["count"] == 0, \
                "entity_states.current_position과 cell_occupants가 일치해야 함 (SSOT)"
        
        logger.info("[P1-5] 게임 시작 트랜잭션 일관성 검증 테스트 통과")
    
    async def test_transaction_consistency_cell_movement(
        self,
        db_connection,
        game_service,
        test_game_data
    ):
        """
        P1-6: 셀 이동 트랜잭션 일관성 검증
        
        검증 항목:
        - 이동 전후 데이터 일관성
        - SSOT 일관성 유지
        - cell_occupants 자동 동기화 확인
        """
        logger.info("[P1-6] 셀 이동 트랜잭션 일관성 검증 테스트 시작")
        
        # 게임 시작
        result = await game_service.start_game(
            player_template_id=test_game_data["player_template_id"],
            start_cell_id=test_game_data["cell_id"]
        )
        
        session_id = result["game_state"]["session_id"]
        player_id = result["game_state"]["player_id"]
        start_cell_id = result["game_state"]["current_cell_id"]
        
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 이동 전 상태 확인
            before_position = await conn.fetchrow("""
                SELECT current_position
                FROM runtime_data.entity_states
                WHERE runtime_entity_id = $1
            """, player_id)
            
            before_occupants_start = await conn.fetchrow("""
                SELECT COUNT(*) as count
                FROM runtime_data.cell_occupants
                WHERE runtime_cell_id = $1 AND runtime_entity_id = $2
            """, start_cell_id, player_id)
            
            assert before_occupants_start["count"] == 1, \
                "시작 셀에 플레이어가 있어야 함"
        
        # 셀 이동
        from app.services.gameplay import CellService
        cell_service = CellService(db_connection)
        
        move_result = await cell_service.move_player(
            session_id=session_id,
            target_cell_id=test_game_data["cell_id_2"]
        )
        
        new_cell_id = move_result["game_state"]["current_cell_id"]
        
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 이동 후 상태 확인
            after_position = await conn.fetchrow("""
                SELECT current_position
                FROM runtime_data.entity_states
                WHERE runtime_entity_id = $1
            """, player_id)
            
            after_occupants_start = await conn.fetchrow("""
                SELECT COUNT(*) as count
                FROM runtime_data.cell_occupants
                WHERE runtime_cell_id = $1 AND runtime_entity_id = $2
            """, start_cell_id, player_id)
            
            after_occupants_new = await conn.fetchrow("""
                SELECT COUNT(*) as count
                FROM runtime_data.cell_occupants
                WHERE runtime_cell_id = $1 AND runtime_entity_id = $2
            """, new_cell_id, player_id)
            
            # 이전 셀에서 제거 확인
            assert after_occupants_start["count"] == 0, \
                "이전 셀에서 플레이어가 제거되어야 함"
            
            # 새 셀에 추가 확인
            assert after_occupants_new["count"] == 1, \
                "새 셀에 플레이어가 추가되어야 함"
            
            # SSOT 일관성 확인
            position_data = after_position["current_position"]
            if isinstance(position_data, str):
                position_data = json.loads(position_data)
            
            assert position_data.get("runtime_cell_id") == str(new_cell_id), \
                "entity_states.current_position이 새 셀 ID로 업데이트되어야 함"
            
            # cell_occupants와 current_position 일치 확인
            ssot_check = await conn.fetchrow("""
                SELECT COUNT(*) as count
                FROM runtime_data.entity_states es
                JOIN runtime_data.cell_occupants co
                  ON es.runtime_entity_id = co.runtime_entity_id
                WHERE es.runtime_entity_id = $1
                  AND co.runtime_cell_id::text != es.current_position->>'runtime_cell_id'
            """, player_id)
            assert ssot_check["count"] == 0, \
                "entity_states.current_position과 cell_occupants가 일치해야 함 (SSOT)"
        
        logger.info("[P1-6] 셀 이동 트랜잭션 일관성 검증 테스트 통과")

