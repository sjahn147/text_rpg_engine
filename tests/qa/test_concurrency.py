"""
동시성 QA 테스트

P2 (Medium): 동시성 및 격리 수준 검증
"""
import pytest
import pytest_asyncio
import asyncio
from typing import Dict, Any, List
from common.utils.logger import logger


@pytest.mark.asyncio
class TestConcurrency:
    """동시성 테스트"""
    
    async def test_concurrent_game_starts(
        self,
        db_connection,
        game_service,
        test_game_data
    ):
        """
        P2-6: 동시 게임 시작 처리
        
        검증 항목:
        - 동일 세션에 대한 동시 요청 처리
        - 트랜잭션 격리 수준
        - 데드락 방지
        """
        logger.info("[P2-6] 동시 게임 시작 처리 테스트 시작")
        
        # 5개의 동시 게임 시작 요청
        async def start_game_task():
            try:
                result = await game_service.start_game(
                    player_template_id=test_game_data["player_template_id"],
                    start_cell_id=test_game_data["cell_id"]
                )
                return result
            except Exception as e:
                logger.error(f"게임 시작 실패: {str(e)}")
                return None
        
        tasks = [start_game_task() for _ in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 모든 요청이 성공하거나 적절히 처리되었는지 확인
        success_count = sum(1 for r in results if r is not None and not isinstance(r, Exception))
        
        assert success_count > 0, "최소한 하나의 게임 시작이 성공해야 함"
        
        # 세션 ID가 모두 다른지 확인 (고유성)
        session_ids = []
        for r in results:
            if r and not isinstance(r, Exception) and "game_state" in r:
                session_ids.append(r["game_state"]["session_id"])
        
        assert len(session_ids) == len(set(session_ids)), \
            "모든 세션 ID가 고유해야 함"
        
        logger.info(f"[P2-6] 동시 게임 시작 처리 테스트 통과: {success_count}/5 성공")
    
    async def test_concurrent_cell_queries(
        self,
        db_connection,
        game_service,
        test_game_data
    ):
        """
        P2-7: 동시 셀 조회 처리
        
        검증 항목:
        - 동시 셀 조회 (10개 요청)
        - 트랜잭션 격리 수준
        """
        logger.info("[P2-7] 동시 셀 조회 처리 테스트 시작")
        
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
                logger.error(f"셀 조회 실패: {str(e)}")
                return None
        
        tasks = [query_cell() for _ in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 모든 요청이 성공했는지 확인
        success_count = sum(1 for r in results if r is not None and not isinstance(r, Exception))
        
        assert success_count == 10, f"모든 셀 조회가 성공해야 함: {success_count}/10"
        
        logger.info("[P2-7] 동시 셀 조회 처리 테스트 통과")

