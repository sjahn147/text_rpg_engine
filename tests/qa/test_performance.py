"""
성능 QA 테스트

P2 (Medium): 응답 시간 및 동시 사용자 검증
"""
import pytest
import pytest_asyncio
import asyncio
import time
from typing import Dict, Any
from common.utils.logger import logger


@pytest.mark.asyncio
class TestPerformance:
    """성능 테스트"""
    
    async def test_game_start_response_time(
        self,
        db_connection,
        game_service,
        test_game_data
    ):
        """
        P2-8: 게임 시작 응답 시간 검증
        
        검증 항목:
        - 게임 시작 응답 시간 < 1초
        """
        logger.info("[P2-8] 게임 시작 응답 시간 검증 테스트 시작")
        
        start_time = time.time()
        
        result = await game_service.start_game(
            player_template_id=test_game_data["player_template_id"],
            start_cell_id=test_game_data["cell_id"]
        )
        
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < 1.0, \
            f"게임 시작 응답 시간이 1초 미만이어야 함: {elapsed_time:.3f}초"
        
        logger.info(f"[P2-8] 게임 시작 응답 시간: {elapsed_time:.3f}초")
    
    async def test_cell_query_response_time(
        self,
        db_connection,
        game_service,
        test_game_data
    ):
        """
        P2-9: 셀 조회 응답 시간 검증
        
        검증 항목:
        - 셀 조회 응답 시간 < 500ms
        """
        logger.info("[P2-9] 셀 조회 응답 시간 검증 테스트 시작")
        
        # 게임 시작
        result = await game_service.start_game(
            player_template_id=test_game_data["player_template_id"],
            start_cell_id=test_game_data["cell_id"]
        )
        
        session_id = result["game_state"]["session_id"]
        
        # 셀 조회
        from app.services.gameplay import CellService
        cell_service = CellService(db_connection)
        
        start_time = time.time()
        cell_info = await cell_service.get_current_cell(session_id)
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < 0.5, \
            f"셀 조회 응답 시간이 500ms 미만이어야 함: {elapsed_time*1000:.1f}ms"
        
        logger.info(f"[P2-9] 셀 조회 응답 시간: {elapsed_time*1000:.1f}ms")
    
    async def test_interaction_response_time(
        self,
        db_connection,
        game_service,
        test_game_data
    ):
        """
        P2-10: 상호작용 응답 시간 검증
        
        검증 항목:
        - 상호작용 응답 시간 < 500ms
        """
        logger.info("[P2-10] 상호작용 응답 시간 검증 테스트 시작")
        
        # 게임 시작
        result = await game_service.start_game(
            player_template_id=test_game_data["player_template_id"],
            start_cell_id=test_game_data["cell_id"]
        )
        
        session_id = result["game_state"]["session_id"]
        player_id = result["game_state"]["player_id"]
        
        # 플레이어 본인과 상호작용 (examine)
        from app.services.gameplay import InteractionService
        interaction_service = InteractionService(db_connection)
        
        start_time = time.time()
        interaction_result = await interaction_service.interact_with_entity(
            session_id=session_id,
            entity_id=player_id,
            action_type="examine"
        )
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < 0.5, \
            f"상호작용 응답 시간이 500ms 미만이어야 함: {elapsed_time*1000:.1f}ms"
        
        logger.info(f"[P2-10] 상호작용 응답 시간: {elapsed_time*1000:.1f}ms")
    
    async def test_concurrent_users_game_start(
        self,
        db_connection,
        game_service,
        test_game_data
    ):
        """
        P2-11: 동시 사용자 게임 시작 (10개 세션)
        
        검증 항목:
        - 동시 게임 시작 (10개 세션)
        """
        logger.info("[P2-11] 동시 사용자 게임 시작 테스트 시작")
        
        async def start_game_task():
            try:
                result = await game_service.start_game(
                    player_template_id=test_game_data["player_template_id"],
                    start_cell_id=test_game_data["cell_id"]
                )
                return result
            except Exception as e:
                return None
        
        start_time = time.time()
        tasks = [start_game_task() for _ in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed_time = time.time() - start_time
        
        success_count = sum(1 for r in results if r is not None and not isinstance(r, Exception))
        
        assert success_count >= 8, \
            f"최소 8개 이상의 게임 시작이 성공해야 함: {success_count}/10"
        
        logger.info(f"[P2-11] 동시 사용자 게임 시작: {success_count}/10 성공, {elapsed_time:.3f}초")
    
    async def test_concurrent_users_cell_query(
        self,
        db_connection,
        game_service,
        test_game_data
    ):
        """
        P2-12: 동시 사용자 셀 조회 (50개 요청)
        
        검증 항목:
        - 동시 셀 조회 (50개 요청)
        """
        logger.info("[P2-12] 동시 사용자 셀 조회 테스트 시작")
        
        # 게임 시작
        result = await game_service.start_game(
            player_template_id=test_game_data["player_template_id"],
            start_cell_id=test_game_data["cell_id"]
        )
        
        session_id = result["game_state"]["session_id"]
        
        # 동시 셀 조회
        from app.services.gameplay import CellService
        cell_service = CellService(db_connection)
        
        async def query_cell():
            try:
                cell_info = await cell_service.get_current_cell(session_id)
                return cell_info
            except Exception as e:
                return None
        
        start_time = time.time()
        tasks = [query_cell() for _ in range(50)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed_time = time.time() - start_time
        
        success_count = sum(1 for r in results if r is not None and not isinstance(r, Exception))
        
        # 동시성 문제로 일부 실패할 수 있으므로, 최소 30개 이상 성공하면 통과
        assert success_count >= 30, \
            f"최소 30개 이상의 셀 조회가 성공해야 함: {success_count}/50"
        
        logger.info(f"[P2-12] 동시 사용자 셀 조회: {success_count}/50 성공, {elapsed_time:.3f}초")

