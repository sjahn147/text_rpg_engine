"""
에러 처리 강화 테스트

목적:
- 핸들러의 에러 처리 강화 검증
- 사용자 친화적인 에러 메시지 검증
- 상세한 로깅 검증
"""
import pytest
import pytest_asyncio
from typing import Dict, Any
from common.utils.logger import logger

from database.connection import DatabaseConnection
from app.handlers.object_interactions.recovery import RecoveryInteractionHandler
from app.handlers.object_interactions.consumption import ConsumptionInteractionHandler
from app.handlers.object_interactions.learning import LearningInteractionHandler
from app.managers.entity_manager import EntityManager
from app.managers.object_state_manager import ObjectStateManager


@pytest.mark.asyncio
class TestErrorHandlingEnhancement:
    """에러 처리 강화 테스트"""
    
    async def test_validate_required_managers(self):
        """필수 매니저 검증 테스트"""
        db = DatabaseConnection()
        
        # EntityManager가 None인 경우
        handler = RecoveryInteractionHandler(
            db_connection=db,
            entity_manager=None
        )
        
        result = handler._validate_required_managers(
            {"entity_manager": handler.entity_manager},
            "테스트 작업"
        )
        
        assert result is not None, "매니저가 None이면 실패 결과를 반환해야 함"
        assert result.success is False, "실패 결과여야 함"
        assert "EntityManager" in result.message or "entity_manager" in result.message.lower()
    
    async def test_validate_parameters_missing(self):
        """파라미터 누락 검증 테스트"""
        db = DatabaseConnection()
        handler = RecoveryInteractionHandler(db_connection=db)
        
        # 파라미터가 None인 경우
        result = handler._validate_parameters(None, ["session_id"], "테스트 작업")
        assert result is not None, "파라미터가 None이면 실패 결과를 반환해야 함"
        assert result.success is False, "실패 결과여야 함"
        
        # 필수 키가 없는 경우
        result = handler._validate_parameters({}, ["session_id"], "테스트 작업")
        assert result is not None, "필수 키가 없으면 실패 결과를 반환해야 함"
        assert result.success is False, "실패 결과여야 함"
        assert "session_id" in result.message
    
    async def test_handle_error_user_friendly_message(self):
        """사용자 친화적인 에러 메시지 테스트"""
        db = DatabaseConnection()
        handler = RecoveryInteractionHandler(db_connection=db)
        
        context = {
            "entity_id": "test-entity",
            "target_id": "test-target",
            "operation": "test_operation"
        }
        
        # ValueError 테스트
        error = ValueError("Invalid input")
        result = handler._handle_error(error, context)
        assert result.success is False, "실패 결과여야 함"
        assert "입력값 오류" in result.message or "Invalid input" in result.message
        
        # KeyError 테스트
        error = KeyError("missing_key")
        result = handler._handle_error(error, context)
        assert result.success is False, "실패 결과여야 함"
        assert "필수 정보" in result.message or "누락" in result.message
    
    @pytest.mark.integration
    async def test_recovery_handler_error_handling(
        self,
        db_connection
    ):
        """RecoveryHandler 에러 처리 통합 테스트"""
        logger.info("[통합 테스트] RecoveryHandler 에러 처리 테스트 시작")
        
        # EntityManager가 None인 핸들러 생성
        handler = RecoveryInteractionHandler(
            db_connection=db_connection,
            entity_manager=None
        )
        
        # handle_rest 호출 (에러 발생 예상)
        result = await handler.handle_rest(
            entity_id="test-entity",
            target_id="test-target",
            parameters={"session_id": "test-session"}
        )
        
        assert result.success is False, "EntityManager가 None이면 실패해야 함"
        assert "EntityManager" in result.message or "entity_manager" in result.message.lower()
        
        logger.info("[OK] RecoveryHandler 에러 처리 테스트 통과")
    
    @pytest.mark.integration
    async def test_consumption_handler_error_handling(
        self,
        db_connection
    ):
        """ConsumptionHandler 에러 처리 통합 테스트"""
        logger.info("[통합 테스트] ConsumptionHandler 에러 처리 테스트 시작")
        
        handler = ConsumptionInteractionHandler(
            db_connection=db_connection,
            entity_manager=None
        )
        
        # handle_eat 호출 (에러 발생 예상)
        result = await handler.handle_eat(
            entity_id="test-entity",
            target_id="test-target",
            parameters={"session_id": "test-session"}
        )
        
        assert result.success is False, "EntityManager가 None이면 실패해야 함"
        assert "EntityManager" in result.message or "entity_manager" in result.message.lower()
        
        logger.info("[OK] ConsumptionHandler 에러 처리 테스트 통과")
    
    @pytest.mark.integration
    async def test_learning_handler_error_handling(
        self,
        db_connection
    ):
        """LearningHandler 에러 처리 통합 테스트"""
        logger.info("[통합 테스트] LearningHandler 에러 처리 테스트 시작")
        
        handler = LearningInteractionHandler(
            db_connection=db_connection
        )
        
        # handle_read 호출 (session_id 누락)
        result = await handler.handle_read(
            entity_id="test-entity",
            target_id="test-target",
            parameters={}  # session_id 누락
        )
        
        assert result.success is False, "session_id가 없으면 실패해야 함"
        assert "session_id" in result.message or "파라미터" in result.message
        
        # handle_write 호출 (content 누락)
        result = await handler.handle_write(
            entity_id="test-entity",
            target_id="test-target",
            parameters={"session_id": "test-session"}  # content 누락
        )
        
        assert result.success is False, "content가 없으면 실패해야 함"
        assert "content" in result.message or "파라미터" in result.message
        
        logger.info("[OK] LearningHandler 에러 처리 테스트 통과")

