"""
연결된 셀 동적 생성 QA 테스트

P1 (High): 연결된 셀 동적 생성 시 FK 제약조건 준수 검증
"""
import pytest
import pytest_asyncio
import uuid
import json
from typing import Dict, Any
from common.utils.logger import logger


@pytest.mark.asyncio
class TestConnectedCellsDynamicCreation:
    """연결된 셀 동적 생성 테스트"""
    
    @pytest_asyncio.fixture(scope="function")
    async def test_cell_with_connected_cells(self, db_connection):
        """
        연결된 셀이 있는 테스트 셀 생성 (함수 스코프)
        
        cell_properties에 connected_cells를 포함하여
        ActionService가 동적으로 연결된 셀 인스턴스를 생성하는 시나리오 테스트
        """
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # 테스트용 게임 데이터 생성
            region_id = "REG_QA_CONNECTED_CELLS_001"
            location_id = "LOC_QA_CONNECTED_CELLS_001"
            main_cell_id = "CELL_QA_CONNECTED_MAIN_001"
            connected_cell_id_1 = "CELL_QA_CONNECTED_1_001"
            connected_cell_id_2 = "CELL_QA_CONNECTED_2_001"
            
            # 1. Region 생성
            await conn.execute("""
                INSERT INTO game_data.world_regions 
                (region_id, region_name, region_description, region_properties)
                VALUES ($1, $2, $3, $4::jsonb)
                ON CONFLICT (region_id) DO NOTHING
            """,
            region_id, "QA Connected Cells Region", "QA 테스트용 지역",
            json.dumps({"climate": "temperate", "terrain": "plains"}))
            
            # 2. Location 생성
            await conn.execute("""
                INSERT INTO game_data.world_locations 
                (location_id, region_id, location_name, location_description, location_properties)
                VALUES ($1, $2, $3, $4, $5::jsonb)
                ON CONFLICT (location_id) DO NOTHING
            """,
            location_id, region_id, "QA Connected Cells Location", "QA 테스트용 위치",
            json.dumps({"type": "village", "population": 100}))
            
            # 3. 연결된 셀들 생성 (메인 셀에서 참조될 셀들)
            await conn.execute("""
                INSERT INTO game_data.world_cells 
                (cell_id, location_id, cell_name, matrix_width, matrix_height, cell_description, cell_properties)
                VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb)
                ON CONFLICT (cell_id) DO NOTHING
            """,
            connected_cell_id_1, location_id, "QA Connected Room 1", 10, 10, "QA 테스트용 연결된 방 1",
            json.dumps({"cell_type": "indoor", "size": "medium"}))
            
            await conn.execute("""
                INSERT INTO game_data.world_cells 
                (cell_id, location_id, cell_name, matrix_width, matrix_height, cell_description, cell_properties)
                VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb)
                ON CONFLICT (cell_id) DO NOTHING
            """,
            connected_cell_id_2, location_id, "QA Connected Room 2", 10, 10, "QA 테스트용 연결된 방 2",
            json.dumps({"cell_type": "indoor", "size": "medium"}))
            
            # 4. 메인 셀 생성 (connected_cells 포함)
            connected_cells_properties = {
                "cell_type": "indoor",
                "size": "large",
                "connected_cells": [
                    {
                        "cell_id": connected_cell_id_1,
                        "direction": "북쪽",
                        "description": "북쪽 방향으로 이동",
                        "cell_name": "QA Connected Room 1"
                    },
                    {
                        "cell_id": connected_cell_id_2,
                        "direction": "남쪽",
                        "description": "남쪽 방향으로 이동",
                        "cell_name": "QA Connected Room 2"
                    }
                ]
            }
            
            await conn.execute("""
                INSERT INTO game_data.world_cells 
                (cell_id, location_id, cell_name, matrix_width, matrix_height, cell_description, cell_properties)
                VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb)
                ON CONFLICT (cell_id) DO NOTHING
            """,
            main_cell_id, location_id, "QA Main Room", 10, 10, "QA 테스트용 메인 방",
            json.dumps(connected_cells_properties))
            
            yield {
                "region_id": region_id,
                "location_id": location_id,
                "main_cell_id": main_cell_id,
                "connected_cell_id_1": connected_cell_id_1,
                "connected_cell_id_2": connected_cell_id_2
            }
    
    @pytest_asyncio.fixture(scope="function")
    async def test_player_template_for_connected_cells(self, db_connection):
        """연결된 셀 테스트용 플레이어 템플릿 (함수 스코프)"""
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            player_template_id = "ENT_QA_CONNECTED_PLAYER_001"
            
            await conn.execute("""
                INSERT INTO game_data.entities 
                (entity_id, entity_name, entity_type, entity_description, entity_properties, base_stats)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (entity_id) DO NOTHING
            """,
            player_template_id, "QA Connected Cells Player", "player", "QA 테스트용 플레이어",
            json.dumps({"level": 1, "occupation": "adventurer"}),
            json.dumps({"hp": 100, "mp": 50, "strength": 10, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10}))
            
            return player_template_id
    
    async def test_connected_cells_dynamic_creation(
        self,
        db_connection,
        game_service,
        test_cell_with_connected_cells,
        test_player_template_for_connected_cells
    ):
        """
        P1-1: 연결된 셀 동적 생성 검증
        
        검증 항목:
        - 연결된 셀의 런타임 인스턴스가 올바른 순서로 생성됨
        - FK 제약조건 준수 (cell_references 생성 전 runtime_cells 생성)
        - 액션 조회 시 FK 제약조건 위반이 발생하지 않음
        """
        logger.info("[P1-1] 연결된 셀 동적 생성 검증 테스트 시작")
        
        # 게임 시작 (연결된 셀이 있는 메인 셀에서)
        result = await game_service.start_game(
            player_template_id=test_player_template_for_connected_cells,
            start_cell_id=test_cell_with_connected_cells["main_cell_id"]
        )
        
        session_id = result["game_state"]["session_id"]
        current_cell_id = result["game_state"]["current_cell_id"]
        
        logger.info(f"[P1-1] 게임 시작 성공: session_id={session_id}, cell_id={current_cell_id}")
        
        # 액션 조회 (연결된 셀의 런타임 인스턴스가 동적으로 생성되어야 함)
        from app.services.gameplay import ActionService
        action_service = ActionService(db_connection)
        
        # FK 제약조건 위반이 발생하지 않아야 함
        actions = await action_service.get_available_actions(session_id)
        
        assert isinstance(actions, list), "액션 목록은 리스트여야 함"
        logger.info(f"[P1-1] 액션 조회 성공: {len(actions)}개 액션")
        
        # 연결된 셀의 런타임 인스턴스가 올바르게 생성되었는지 확인
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # cell_references에 있는 모든 runtime_cell_id가 runtime_cells에 존재하는지 확인
            cell_refs = await conn.fetch("""
                SELECT cr.runtime_cell_id, cr.game_cell_id
                FROM reference_layer.cell_references cr
                WHERE cr.session_id = $1
            """, session_id)
            
            assert len(cell_refs) > 0, "셀 참조가 생성되어야 함"
            
            for cell_ref in cell_refs:
                runtime_cell = await conn.fetchrow("""
                    SELECT runtime_cell_id, game_cell_id
                    FROM runtime_data.runtime_cells
                    WHERE runtime_cell_id = $1
                """, cell_ref['runtime_cell_id'])
                
                assert runtime_cell is not None, \
                    f"runtime_cell_id {cell_ref['runtime_cell_id']}가 runtime_cells에 존재해야 함 (FK 제약조건)"
                assert runtime_cell['game_cell_id'] == cell_ref['game_cell_id'], \
                    f"game_cell_id가 일치해야 함: {runtime_cell['game_cell_id']} != {cell_ref['game_cell_id']}"
            
            # 연결된 셀들이 실제로 생성되었는지 확인
            connected_cell_refs = await conn.fetch("""
                SELECT cr.runtime_cell_id, cr.game_cell_id
                FROM reference_layer.cell_references cr
                WHERE cr.session_id = $1
                AND cr.game_cell_id IN ($2, $3)
            """, 
            session_id,
            test_cell_with_connected_cells["connected_cell_id_1"],
            test_cell_with_connected_cells["connected_cell_id_2"])
            
            # 연결된 셀들이 생성되었는지 확인 (최소 1개 이상)
            assert len(connected_cell_refs) >= 1, \
                "연결된 셀의 런타임 인스턴스가 최소 1개 이상 생성되어야 함"
            
            logger.info(f"[P1-1] 연결된 셀 {len(connected_cell_refs)}개 생성 확인")
        
        # 이동 액션이 포함되어 있는지 확인
        move_actions = [action for action in actions if action.get("action_type") == "move"]
        assert len(move_actions) > 0, "연결된 셀로의 이동 액션이 포함되어야 함"
        
        logger.info(f"[P1-1] 이동 액션 {len(move_actions)}개 확인")
        logger.info("[P1-1] 연결된 셀 동적 생성 검증 테스트 통과")
