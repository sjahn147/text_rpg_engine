"""
에러 처리 및 엣지 케이스 QA 테스트

P1 (High): 에러 처리 검증
"""
import pytest
import pytest_asyncio
import uuid
from typing import Dict, Any
from common.utils.logger import logger


@pytest.mark.asyncio
class TestErrorHandling:
    """에러 처리 테스트"""
    
    async def test_nonexistent_session_id(
        self,
        db_connection,
        game_service
    ):
        """
        P1-7: 존재하지 않는 세션 ID 처리
        
        검증 항목:
        - 적절한 에러 메시지 반환
        - 적절한 상태 코드
        """
        logger.info("[P1-7] 존재하지 않는 세션 ID 처리 테스트 시작")
        
        # 존재하지 않는 세션 ID로 상태 조회
        with pytest.raises(ValueError, match="세션을 찾을 수 없습니다"):
            await game_service.get_game_state("00000000-0000-0000-0000-000000000000")
        
        logger.info("[P1-7] 존재하지 않는 세션 ID 처리 테스트 통과")
    
    async def test_nonexistent_entity_id(
        self,
        db_connection,
        game_service,
        test_game_data
    ):
        """
        P1-8: 존재하지 않는 엔티티 ID 처리
        
        검증 항목:
        - 적절한 에러 메시지 반환
        """
        logger.info("[P1-8] 존재하지 않는 엔티티 ID 처리 테스트 시작")
        
        # 게임 시작
        result = await game_service.start_game(
            player_template_id=test_game_data["player_template_id"],
            start_cell_id=test_game_data["cell_id"]
        )
        
        session_id = result["game_state"]["session_id"]
        
        # 존재하지 않는 엔티티 ID로 상호작용 시도
        from app.services.gameplay import InteractionService
        interaction_service = InteractionService(db_connection)
        
        with pytest.raises(ValueError, match="엔티티를 찾을 수 없습니다|현재 셀에서 엔티티를 찾을 수 없습니다"):
            await interaction_service.interact_with_entity(
                session_id=session_id,
                entity_id="00000000-0000-0000-0000-000000000000"
            )
        
        logger.info("[P1-8] 존재하지 않는 엔티티 ID 처리 테스트 통과")
    
    async def test_invalid_data_format_missing_fields(
        self,
        db_connection
    ):
        """
        P1-9: 필수 필드 누락 처리
        
        검증 항목:
        - 적절한 검증 에러 메시지
        """
        logger.info("[P1-9] 필수 필드 누락 처리 테스트 시작")
        
        # 필수 필드 없이 게임 시작 시도 (API 레벨에서 검증)
        from fastapi.testclient import TestClient
        from app.ui.backend.main import app
        
        client = TestClient(app)
        
        # player_template_id 누락
        response = client.post(
            "/api/gameplay/start",
            json={
                "start_cell_id": "CELL_QA_TEST_ROOM_001"
            }
        )
        
        # Pydantic 검증 에러 (422 Unprocessable Entity)
        assert response.status_code == 422, \
            f"필수 필드 누락 시 422가 반환되어야 함: {response.status_code}"
        
        data = response.json()
        assert "detail" in data, "에러 메시지가 포함되어야 함"
        
        logger.info("[P1-9] 필수 필드 누락 처리 테스트 통과")
    
    async def test_invalid_data_format_wrong_type(
        self,
        db_connection
    ):
        """
        P1-10: 잘못된 데이터 타입 처리
        
        검증 항목:
        - 적절한 검증 에러 메시지
        """
        logger.info("[P1-10] 잘못된 데이터 타입 처리 테스트 시작")
        
        from fastapi.testclient import TestClient
        from app.ui.backend.main import app
        
        client = TestClient(app)
        
        # 잘못된 타입 (session_id를 숫자로 전달)
        response = client.post(
            "/api/gameplay/move",
            json={
                "session_id": 12345,  # 문자열이어야 함
                "target_cell_id": "CELL_QA_TEST_ROOM_002"
            }
        )
        
        # Pydantic 검증 에러 (422 Unprocessable Entity)
        assert response.status_code == 422, \
            f"잘못된 데이터 타입 시 422가 반환되어야 함: {response.status_code}"
        
        data = response.json()
        assert "detail" in data, "에러 메시지가 포함되어야 함"
        
        logger.info("[P1-10] 잘못된 데이터 타입 처리 테스트 통과")

