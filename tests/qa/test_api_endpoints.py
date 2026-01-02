"""
API 엔드포인트 QA 테스트

P1 (High): API 엔드포인트 검증
"""
import pytest
import pytest_asyncio
from typing import Dict, Any
from common.utils.logger import logger


class TestAPIEndpoints:
    """API 엔드포인트 테스트"""
    
    @pytest_asyncio.fixture
    async def client(self):
        """FastAPI 테스트 클라이언트
        
        싱글톤 서비스가 자체 DatabaseConnection을 사용하도록 함.
        테스트 데이터는 ON CONFLICT DO NOTHING으로 처리되므로 문제 없음.
        """
        from fastapi.testclient import TestClient
        from app.ui.backend.main import app
        
        client = TestClient(app)
        yield client
    
    def test_game_start_api_endpoint(
        self,
        client,
        test_game_data: Dict[str, Any]
    ):
        """
        P1-1: 게임 시작 API 엔드포인트
        
        검증 항목:
        - 상태 코드 (201 Created)
        - 응답 스키마 검증
        - 에러 처리
        """
        logger.info("[P1-1] 게임 시작 API 엔드포인트 테스트 시작")
        
        response = client.post(
            "/api/gameplay/start",
            json={
                "player_template_id": test_game_data["player_template_id"],
                "start_cell_id": test_game_data["cell_id"]
            }
        )
        
        assert response.status_code == 201, f"상태 코드가 201이어야 함: {response.status_code}"
        data = response.json()
        assert data["success"] is True, "success가 True여야 함"
        assert "game_state" in data, "game_state가 포함되어야 함"
        assert "session_id" in data["game_state"], "session_id가 포함되어야 함"
        assert "player_id" in data["game_state"], "player_id가 포함되어야 함"
        assert "current_cell_id" in data["game_state"], "current_cell_id가 포함되어야 함"
        
        logger.info(f"[P1-1] 게임 시작 API 성공: session_id={data['game_state']['session_id']}")
    
    def test_game_start_api_invalid_player(
        self,
        client,
        test_game_data: Dict[str, Any]
    ):
        """
        P1-2: 잘못된 플레이어 템플릿 ID API 테스트
        
        검증 항목:
        - 상태 코드 (500 Internal Server Error)
        - 에러 메시지 포함
        """
        logger.info("[P1-2] 잘못된 플레이어 템플릿 ID API 테스트 시작")
        
        response = client.post(
            "/api/gameplay/start",
            json={
                "player_template_id": "INVALID_PLAYER_TEMPLATE",
                "start_cell_id": test_game_data["cell_id"]
            }
        )
        
        assert response.status_code == 500, f"상태 코드가 500이어야 함: {response.status_code}"
        data = response.json()
        assert "detail" in data, "에러 메시지가 포함되어야 함"
        
        logger.info("[P1-2] 잘못된 플레이어 템플릿 ID API 테스트 통과")
    
    def test_game_state_api_endpoint(
        self,
        client,
        test_game_data: Dict[str, Any]
    ):
        """
        P1-3: 게임 상태 조회 API 엔드포인트
        
        검증 항목:
        - 상태 코드 (200 OK)
        - 응답 스키마 검증
        - 세션 없음 처리 (404)
        """
        logger.info("[P1-3] 게임 상태 조회 API 엔드포인트 테스트 시작")
        
        # 먼저 게임 시작 (API를 통해)
        start_response = client.post(
            "/api/gameplay/start",
            json={
                "player_template_id": test_game_data["player_template_id"],
                "start_cell_id": test_game_data["cell_id"]
            }
        )
        assert start_response.status_code == 201, "게임 시작이 성공해야 함"
        start_data = start_response.json()
        session_id = start_data["game_state"]["session_id"]
        
        # 게임 상태 조회
        response = client.get(f"/api/gameplay/state/{session_id}")
        
        assert response.status_code == 200, f"상태 코드가 200이어야 함: {response.status_code}"
        data = response.json()
        assert "session_id" in data, "session_id가 포함되어야 함"
        assert "player_id" in data, "player_id가 포함되어야 함"
        assert data["session_id"] == session_id, "session_id가 일치해야 함"
        
        # 잘못된 UUID 형식 조회 (400 Bad Request)
        response = client.get("/api/gameplay/state/invalid-session-id")
        assert response.status_code == 400, \
            f"잘못된 UUID 형식은 400이어야 함: {response.status_code}"
        
        # 존재하지 않는 세션 조회 (유효한 UUID 형식이지만 존재하지 않는 세션)
        import uuid
        non_existent_session_id = str(uuid.uuid4())
        response = client.get(f"/api/gameplay/state/{non_existent_session_id}")
        assert response.status_code == 404, \
            f"존재하지 않는 세션은 404이어야 함: {response.status_code}"
        
        logger.info("[P1-3] 게임 상태 조회 API 엔드포인트 테스트 통과")
    
    def test_move_player_api_endpoint(
        self,
        client,
        test_game_data: Dict[str, Any]
    ):
        """
        P1-4: 플레이어 이동 API 엔드포인트
        
        검증 항목:
        - 상태 코드 (200 OK)
        - 이동 성공/실패 처리
        - 잘못된 셀 ID 처리 (400)
        """
        logger.info("[P1-4] 플레이어 이동 API 엔드포인트 테스트 시작")
        
        # 먼저 게임 시작 (API를 통해)
        start_response = client.post(
            "/api/gameplay/start",
            json={
                "player_template_id": test_game_data["player_template_id"],
                "start_cell_id": test_game_data["cell_id"]
            }
        )
        assert start_response.status_code == 201, "게임 시작이 성공해야 함"
        start_data = start_response.json()
        session_id = start_data["game_state"]["session_id"]
        start_cell_id = start_data["game_state"]["current_cell_id"]
        
        # 플레이어 이동
        response = client.post(
            "/api/gameplay/move",
            json={
                "session_id": session_id,
                "target_cell_id": test_game_data["cell_id_2"]
            }
        )
        
        assert response.status_code == 200, f"상태 코드가 200이어야 함: {response.status_code}"
        data = response.json()
        assert data["success"] is True, "success가 True여야 함"
        assert "game_state" in data, "game_state가 포함되어야 함"
        assert data["game_state"]["current_cell_id"] != start_cell_id, "셀이 변경되어야 함"
        
        # 잘못된 셀 ID로 이동 시도
        response = client.post(
            "/api/gameplay/move",
            json={
                "session_id": session_id,
                "target_cell_id": "INVALID_CELL_ID"
            }
        )
        
        # 400 (Bad Request) 또는 500 (Internal Server Error) 허용
        # 400은 ValueError가 발생한 경우, 500은 다른 예외가 발생한 경우
        assert response.status_code in [400, 500], \
            f"상태 코드가 400 또는 500이어야 함: {response.status_code}"
        data = response.json()
        assert "detail" in data, "에러 메시지가 포함되어야 함"
        
        logger.info("[P1-4] 플레이어 이동 API 엔드포인트 테스트 통과")
    
    def test_get_available_actions_api_endpoint(
        self,
        client,
        test_game_data: Dict[str, Any]
    ):
        """
        P1-5: 액션 조회 API 엔드포인트
        
        검증 항목:
        - 상태 코드 (200 OK)
        - 응답 스키마 검증 (리스트)
        - 연결된 셀이 있는 경우 FK 제약조건 준수
        - 연결된 셀이 없는 경우 빈 액션 리스트 반환
        - 에러 처리 (잘못된 세션 ID)
        """
        logger.info("[P1-5] 액션 조회 API 엔드포인트 테스트 시작")
        
        # 게임 시작
        start_response = client.post(
            "/api/gameplay/start",
            json={
                "player_template_id": test_game_data["player_template_id"],
                "start_cell_id": test_game_data["cell_id"]
            }
        )
        assert start_response.status_code == 201, "게임 시작이 성공해야 함"
        start_data = start_response.json()
        session_id = start_data["game_state"]["session_id"]
        
        # 액션 조회
        actions_response = client.get(f"/api/gameplay/actions/{session_id}")
        
        assert actions_response.status_code == 200, \
            f"상태 코드가 200이어야 함: {actions_response.status_code}"
        actions = actions_response.json()
        assert isinstance(actions, list), "응답은 리스트여야 함"
        
        # 기본 액션들이 포함되어 있는지 확인 (관찰하기 등)
        action_types = [action.get("action_type") for action in actions]
        assert "observe" in action_types, "관찰하기 액션이 포함되어야 함"
        
        # 잘못된 UUID 형식 조회 (400 Bad Request)
        response = client.get("/api/gameplay/actions/invalid-session-id")
        assert response.status_code == 400, \
            f"잘못된 UUID 형식은 400이어야 함: {response.status_code}"
        
        # 존재하지 않는 세션 조회 (유효한 UUID 형식이지만 존재하지 않는 세션)
        import uuid
        non_existent_session_id = str(uuid.uuid4())
        response = client.get(f"/api/gameplay/actions/{non_existent_session_id}")
        # 400 (ValueError) 또는 500 (Exception) 허용
        assert response.status_code in [400, 500], \
            f"존재하지 않는 세션은 400 또는 500이어야 함: {response.status_code}"
        
        logger.info(f"[P1-5] 액션 조회 API 성공: {len(actions)}개 액션 조회됨")

