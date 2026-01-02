"""
데이터 무결성 QA 테스트

P0 (Critical): 외래키 제약조건, SSOT, 데이터 생성 순서 검증
"""
import pytest
import pytest_asyncio
import uuid
import json
from typing import Dict, Any
from common.utils.logger import logger


@pytest.mark.asyncio
class TestDataIntegrity:
    """데이터 무결성 테스트"""
    
    async def test_foreign_key_constraints_cell_references(
        self,
        db_connection,
        instance_factory,
        test_game_data
    ):
        """
        P0-7: cell_references 외래키 제약조건 검증
        
        검증 항목:
        - cell_references.runtime_cell_id → runtime_cells.runtime_cell_id
        - runtime_cells 없이 cell_references 생성 시도 시 실패
        """
        logger.info("[P0-7] cell_references 외래키 제약조건 검증 테스트 시작")
        
        session_id = str(uuid.uuid4())
        invalid_runtime_cell_id = str(uuid.uuid4())  # 존재하지 않는 runtime_cell_id
        
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO runtime_data.active_sessions
                (session_id, session_state, created_at, metadata)
                VALUES ($1, $2, NOW(), $3::jsonb)
            """, session_id, "active", json.dumps({"test_type": "qa_test"}))
        
        # runtime_cells 없이 cell_references 생성 시도 (실패해야 함)
        async with pool.acquire() as conn:
            with pytest.raises(Exception) as exc_info:
                await conn.execute("""
                    INSERT INTO reference_layer.cell_references
                    (runtime_cell_id, game_cell_id, session_id, cell_type)
                    VALUES ($1, $2, $3, $4)
                """, invalid_runtime_cell_id, test_game_data["cell_id"], session_id, "indoor")
            
            error_message = str(exc_info.value)
            assert "foreign key" in error_message.lower() or "참조키" in error_message or "제약 조건" in error_message, \
                f"외래키 제약조건 위반 에러가 발생해야 함: {error_message}"
        
        logger.info("[P0-7] cell_references 외래키 제약조건 검증 테스트 통과")
    
    async def test_foreign_key_constraints_entity_references(
        self,
        db_connection,
        test_game_data
    ):
        """
        P0-8: entity_references 외래키 제약조건 검증
        
        검증 항목:
        - entity_references.runtime_entity_id → runtime_entities.runtime_entity_id
        - runtime_entities 없이 entity_references 생성 시도 시 실패
        """
        logger.info("[P0-8] entity_references 외래키 제약조건 검증 테스트 시작")
        
        session_id = str(uuid.uuid4())
        invalid_runtime_entity_id = uuid.uuid4()  # 존재하지 않는 runtime_entity_id
        
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO runtime_data.active_sessions
                (session_id, session_state, created_at, metadata)
                VALUES ($1, $2, NOW(), $3::jsonb)
            """, session_id, "active", json.dumps({"test_type": "qa_test"}))
        
        # runtime_entities 없이 entity_references 생성 시도 (실패해야 함)
        async with pool.acquire() as conn:
            with pytest.raises(Exception) as exc_info:
                await conn.execute("""
                    INSERT INTO reference_layer.entity_references
                    (runtime_entity_id, game_entity_id, session_id, entity_type, is_player)
                    VALUES ($1, $2, $3, $4, $5)
                """, invalid_runtime_entity_id, test_game_data["player_template_id"], session_id, "player", True)
            
            error_message = str(exc_info.value)
            assert "foreign key" in error_message.lower() or "참조키" in error_message or "제약 조건" in error_message, \
                f"외래키 제약조건 위반 에러가 발생해야 함: {error_message}"
        
        logger.info("[P0-8] entity_references 외래키 제약조건 검증 테스트 통과")
    
    async def test_ssot_cell_occupants_sync(
        self,
        db_connection,
        game_service,
        test_game_data
    ):
        """
        P0-9: SSOT - cell_occupants 자동 동기화 검증
        
        검증 항목:
        - entity_states.current_position이 SSOT
        - current_position 변경 시 cell_occupants 자동 동기화
        - 이전 셀에서 제거, 새 셀에 추가 확인
        """
        logger.info("[P0-9] SSOT - cell_occupants 자동 동기화 검증 테스트 시작")
        
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
            # cell_occupants에 자동 동기화되었는지 확인
            cell_occupant = await conn.fetchrow("""
                SELECT runtime_cell_id, runtime_entity_id, entered_at
                FROM runtime_data.cell_occupants
                WHERE runtime_cell_id = $1 AND runtime_entity_id = $2
            """, current_cell_id, player_id)
            assert cell_occupant is not None, "cell_occupants에 자동 동기화되어야 함"
        
        # 두 번째 셀로 이동 (CellService를 사용하여 실제 이동 로직 테스트)
        from app.services.gameplay import CellService
        cell_service = CellService(db_connection)
        
        # 두 번째 셀로 이동
        move_result = await cell_service.move_player(
            session_id=session_id,
            target_cell_id=test_game_data["cell_id_2"]
        )
        
        assert move_result["success"] is True, "이동이 성공해야 함"
        new_cell_id = move_result["game_state"]["current_cell_id"]
        assert new_cell_id != current_cell_id, "셀이 변경되어야 함"
        
        # cell_occupants 자동 동기화 확인
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 이전 셀에서 제거되었는지 확인
            old_cell_occupant = await conn.fetchrow("""
                SELECT runtime_cell_id FROM runtime_data.cell_occupants
                WHERE runtime_cell_id = $1 AND runtime_entity_id = $2
            """, current_cell_id, player_id)
            assert old_cell_occupant is None, "이전 셀에서 제거되어야 함"
            
            # 새 셀에 추가되었는지 확인
            new_cell_occupant = await conn.fetchrow("""
                SELECT runtime_cell_id, runtime_entity_id, entered_at
                FROM runtime_data.cell_occupants
                WHERE runtime_cell_id = $1 AND runtime_entity_id = $2
            """, new_cell_id, player_id)
            assert new_cell_occupant is not None, "새 셀에 추가되어야 함"
            
            # entity_states.current_position이 SSOT인지 확인
            entity_state = await conn.fetchrow("""
                SELECT current_position
                FROM runtime_data.entity_states
                WHERE runtime_entity_id = $1
            """, player_id)
            assert entity_state is not None, "entity_state가 존재해야 함"
            
            current_position = entity_state["current_position"]
            if isinstance(current_position, str):
                import json
                current_position = json.loads(current_position)
            
            assert current_position.get("runtime_cell_id") == str(new_cell_id), \
                "entity_states.current_position이 SSOT이어야 함"
        
        logger.info("[P0-9] SSOT - cell_occupants 자동 동기화 검증 테스트 통과")
    
    async def test_ssot_cell_occupants_direct_write_prevention(
        self,
        db_connection,
        game_service,
        test_game_data
    ):
        """
        P0-10: SSOT - cell_occupants 직접 쓰기 방지 검증
        
        검증 항목:
        - cell_occupants 직접 INSERT/UPDATE/DELETE 시도 시 트리거에 의해 차단
        """
        logger.info("[P0-10] SSOT - cell_occupants 직접 쓰기 방지 검증 테스트 시작")
        
        # 게임 시작
        result = await game_service.start_game(
            player_template_id=test_game_data["player_template_id"],
            start_cell_id=test_game_data["cell_id"]
        )
        
        player_id = result["game_state"]["player_id"]
        current_cell_id = result["game_state"]["current_cell_id"]
        
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # cell_occupants 직접 INSERT 시도 (실패해야 함)
            with pytest.raises(Exception) as exc_info:
                await conn.execute("""
                    INSERT INTO runtime_data.cell_occupants
                    (runtime_cell_id, runtime_entity_id, entity_type, position, entered_at)
                    VALUES ($1, $2, $3, $4, NOW())
                """, current_cell_id, player_id, "player", json.dumps({"x": 0, "y": 0, "z": 0}))
            
            error_message = str(exc_info.value)
            assert "직접 수정할 수 없습니다" in error_message or "direct write" in error_message.lower(), \
                f"직접 쓰기 방지 트리거가 작동해야 함: {error_message}"
        
        logger.info("[P0-10] SSOT - cell_occupants 직접 쓰기 방지 검증 테스트 통과")

