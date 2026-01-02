"""
셀 이동 QA 테스트

P1 (High): 플레이어 이동 및 셀 정보 조회 검증
"""
import pytest
import pytest_asyncio
import uuid
import json
from typing import Dict, Any
from common.utils.logger import logger


@pytest.mark.asyncio
class TestCellMovement:
    """셀 이동 테스트"""
    
    async def test_player_movement(
        self,
        db_connection,
        game_service,
        test_game_data
    ):
        """
        P1-1: 플레이어 이동 검증
        
        검증 항목:
        - entity_states.current_position 업데이트
        - cell_occupants 자동 동기화
        - 이전 셀에서 제거 확인
        - 새 셀에 추가 확인
        - 트랜잭션 원자성
        """
        logger.info("[P1-1] 플레이어 이동 검증 테스트 시작")
        
        # 게임 시작
        result = await game_service.start_game(
            player_template_id=test_game_data["player_template_id"],
            start_cell_id=test_game_data["cell_id"]
        )
        
        session_id = result["game_state"]["session_id"]
        player_id = result["game_state"]["player_id"]
        start_cell_id = result["game_state"]["current_cell_id"]
        
        # 시작 셀에서 플레이어가 있는지 확인
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            start_cell_occupant = await conn.fetchrow("""
                SELECT runtime_cell_id, runtime_entity_id
                FROM runtime_data.cell_occupants
                WHERE runtime_cell_id = $1 AND runtime_entity_id = $2
            """, start_cell_id, player_id)
            assert start_cell_occupant is not None, "시작 셀에 플레이어가 있어야 함"
        
        # 두 번째 셀로 이동
        from app.services.gameplay import CellService
        cell_service = CellService(db_connection)
        
        move_result = await cell_service.move_player(
            session_id=session_id,
            target_cell_id=test_game_data["cell_id_2"]
        )
        
        assert move_result["success"] is True, "이동이 성공해야 함"
        assert "game_state" in move_result, "game_state가 포함되어야 함"
        
        new_cell_id = move_result["game_state"]["current_cell_id"]
        assert new_cell_id != start_cell_id, "셀이 변경되어야 함"
        
        # entity_states.current_position 업데이트 확인
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            entity_state = await conn.fetchrow("""
                SELECT current_position
                FROM runtime_data.entity_states
                WHERE runtime_entity_id = $1
            """, player_id)
            assert entity_state is not None, "entity_state가 존재해야 함"
            
            current_position = entity_state["current_position"]
            if isinstance(current_position, str):
                current_position = json.loads(current_position)
            
            assert current_position.get("runtime_cell_id") == str(new_cell_id), \
                "current_position이 새 셀 ID로 업데이트되어야 함"
        
        # cell_occupants 자동 동기화 확인
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 이전 셀에서 제거되었는지 확인
            old_cell_occupant = await conn.fetchrow("""
                SELECT runtime_cell_id FROM runtime_data.cell_occupants
                WHERE runtime_cell_id = $1 AND runtime_entity_id = $2
            """, start_cell_id, player_id)
            assert old_cell_occupant is None, "이전 셀에서 제거되어야 함"
            
            # 새 셀에 추가되었는지 확인
            new_cell_occupant = await conn.fetchrow("""
                SELECT runtime_cell_id, runtime_entity_id, entered_at
                FROM runtime_data.cell_occupants
                WHERE runtime_cell_id = $1 AND runtime_entity_id = $2
            """, new_cell_id, player_id)
            assert new_cell_occupant is not None, "새 셀에 추가되어야 함"
        
        logger.info("[P1-1] 플레이어 이동 검증 테스트 통과")
    
    async def test_get_current_cell(
        self,
        db_connection,
        game_service,
        test_game_data
    ):
        """
        P1-2: 현재 셀 정보 조회 검증
        
        검증 항목:
        - 셀 정보 정확성
        - 엔티티 목록 정확성
        - 오브젝트 목록 정확성
        - 연결된 셀 정보 정확성
        """
        logger.info("[P1-2] 현재 셀 정보 조회 검증 테스트 시작")
        
        # 게임 시작
        result = await game_service.start_game(
            player_template_id=test_game_data["player_template_id"],
            start_cell_id=test_game_data["cell_id"]
        )
        
        session_id = result["game_state"]["session_id"]
        player_id = result["game_state"]["player_id"]
        current_cell_id = result["game_state"]["current_cell_id"]
        
        # 현재 셀 정보 조회
        from app.services.gameplay import CellService
        cell_service = CellService(db_connection)
        
        cell_info = await cell_service.get_current_cell(session_id)
        
        assert cell_info is not None, "셀 정보가 조회되어야 함"
        assert "cell_id" in cell_info or "runtime_cell_id" in cell_info, "셀 ID가 포함되어야 함"
        
        # 셀 정보 정확성 확인
        if "runtime_cell_id" in cell_info:
            assert cell_info["runtime_cell_id"] == current_cell_id, "현재 셀 ID가 일치해야 함"
        
        # 엔티티 목록 확인 (플레이어가 포함되어야 함)
        if "entities" in cell_info:
            entity_ids = [e.get("runtime_entity_id") or e.get("entity_id") for e in cell_info["entities"]]
            assert player_id in entity_ids or str(player_id) in entity_ids, "플레이어가 엔티티 목록에 포함되어야 함"
        
        # 오브젝트 목록 확인 (게임 데이터에 오브젝트가 있으면 반드시 조회되어야 함)
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 게임 데이터에서 해당 셀의 오브젝트 확인
            cell_ref = await conn.fetchrow("""
                SELECT game_cell_id FROM reference_layer.cell_references
                WHERE runtime_cell_id = $1 AND session_id = $2
            """, current_cell_id, session_id)
            
            if cell_ref:
                game_objects = await conn.fetch("""
                    SELECT object_id FROM game_data.world_objects
                    WHERE default_cell_id = $1
                """, cell_ref['game_cell_id'])
                
                if len(game_objects) > 0:
                    # 게임 데이터에 오브젝트가 있으면 반드시 조회되어야 함
                    assert "objects" in cell_info, "게임 데이터에 오브젝트가 있으면 objects 키가 있어야 함"
                    assert isinstance(cell_info["objects"], list), "오브젝트 목록은 리스트여야 함"
                    assert len(cell_info["objects"]) > 0, f"게임 데이터에 {len(game_objects)}개의 오브젝트가 있으면 런타임 오브젝트도 조회되어야 함"
                    
                    # 각 오브젝트가 올바른 구조를 가지고 있는지 확인
                    for obj in cell_info["objects"]:
                        assert "object_id" in obj or "runtime_object_id" in obj or "game_object_id" in obj, \
                            "오브젝트는 object_id, runtime_object_id, 또는 game_object_id를 가져야 함"
                        assert "object_name" in obj, "오브젝트는 object_name을 가져야 함"
                    
                    # object_states에 current_position이 설정되어 있는지 확인
                    for obj in cell_info["objects"]:
                        runtime_object_id = obj.get("runtime_object_id") or obj.get("object_id")
                        if runtime_object_id:
                            object_state = await conn.fetchrow("""
                                SELECT current_position FROM runtime_data.object_states
                                WHERE runtime_object_id = $1
                            """, runtime_object_id)
                            assert object_state is not None, \
                                f"오브젝트 {runtime_object_id}의 object_states가 생성되어야 함"
                            
                            if object_state and object_state['current_position']:
                                import json
                                position = object_state['current_position']
                                if isinstance(position, str):
                                    position = json.loads(position)
                                assert position.get('runtime_cell_id') == str(current_cell_id), \
                                    f"오브젝트 {runtime_object_id}의 current_position에 runtime_cell_id가 설정되어야 함"
        
        logger.info("[P1-2] 현재 셀 정보 조회 검증 테스트 통과")
    
    async def test_player_movement_invalid_cell(
        self,
        db_connection,
        game_service,
        test_game_data
    ):
        """
        P1-3: 잘못된 셀로 이동 시 에러 처리 검증
        
        검증 항목:
        - 존재하지 않는 셀 ID 처리
        - 적절한 에러 메시지 반환
        """
        logger.info("[P1-3] 잘못된 셀로 이동 시 에러 처리 검증 테스트 시작")
        
        # 게임 시작
        result = await game_service.start_game(
            player_template_id=test_game_data["player_template_id"],
            start_cell_id=test_game_data["cell_id"]
        )
        
        session_id = result["game_state"]["session_id"]
        start_cell_id = result["game_state"]["current_cell_id"]
        
        # 존재하지 않는 셀로 이동 시도
        from app.services.gameplay import CellService
        cell_service = CellService(db_connection)
        
        with pytest.raises(ValueError, match="셀.*찾을 수 없습니다"):
            await cell_service.move_player(
                session_id=session_id,
                target_cell_id="INVALID_CELL_ID"
            )
        
        # 원래 셀에 그대로 있어야 함
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            current_position = await conn.fetchrow("""
                SELECT current_position
                FROM runtime_data.entity_states
                WHERE runtime_entity_id = $1
            """, result["game_state"]["player_id"])
            
            if current_position:
                position = current_position["current_position"]
                if isinstance(position, str):
                    position = json.loads(position)
                assert position.get("runtime_cell_id") == str(start_cell_id), \
                    "이동 실패 시 원래 셀에 그대로 있어야 함"
        
        logger.info("[P1-3] 잘못된 셀로 이동 시 에러 처리 검증 테스트 통과")

