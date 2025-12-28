"""
에러 처리 유틸리티
"""
import traceback
from typing import Any, Dict, Optional, Tuple
from enum import Enum


class ErrorType(str, Enum):
    """에러 타입 열거형"""
    SCHEMA_MISMATCH = "schema_mismatch"
    DATABASE_ERROR = "database_error"
    VALIDATION_ERROR = "validation_error"
    CONNECTION_ERROR = "connection_error"
    PERMISSION_ERROR = "permission_error"
    UNKNOWN_ERROR = "unknown_error"


class ManagerError(Exception):
    """매니저 클래스 전용 에러"""
    
    def __init__(self, message: str, error_type: ErrorType, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_type = error_type
        self.details = details or {}
        super().__init__(self.message)


def handle_database_error(error: Exception, operation: str, table: str = None) -> ManagerError:
    """
    데이터베이스 에러를 매니저 에러로 변환
    
    Args:
        error: 원본 에러
        operation: 수행 중이던 작업
        table: 관련 테이블 (선택사항)
        
    Returns:
        ManagerError: 변환된 에러
    """
    error_message = str(error)
    
    # 스키마 불일치 에러 감지
    if "does not exist" in error_message or "column" in error_message and "does not exist" in error_message:
        return ManagerError(
            f"스키마 불일치: {operation} 중 테이블/컬럼을 찾을 수 없습니다. "
            f"테이블: {table}, 에러: {error_message}",
            ErrorType.SCHEMA_MISMATCH,
            {"original_error": error_message, "table": table, "operation": operation}
        )
    
    # 연결 에러 감지
    if "connection" in error_message.lower() or "timeout" in error_message.lower():
        return ManagerError(
            f"데이터베이스 연결 오류: {operation} 중 연결이 실패했습니다. 에러: {error_message}",
            ErrorType.CONNECTION_ERROR,
            {"original_error": error_message, "operation": operation}
        )
    
    # 권한 에러 감지
    if "permission" in error_message.lower() or "access" in error_message.lower():
        return ManagerError(
            f"권한 오류: {operation} 중 접근이 거부되었습니다. 에러: {error_message}",
            ErrorType.PERMISSION_ERROR,
            {"original_error": error_message, "operation": operation}
        )
    
    # 일반 데이터베이스 에러
    return ManagerError(
        f"데이터베이스 오류: {operation} 중 오류가 발생했습니다. 에러: {error_message}",
        ErrorType.DATABASE_ERROR,
        {"original_error": error_message, "operation": operation}
    )


def handle_validation_error(error: Exception, field: str = None) -> ManagerError:
    """
    검증 에러를 매니저 에러로 변환
    
    Args:
        error: 원본 에러
        field: 검증 실패한 필드 (선택사항)
        
    Returns:
        ManagerError: 변환된 에러
    """
    error_message = str(error)
    
    return ManagerError(
        f"검증 오류: {field or '데이터'} 검증에 실패했습니다. 에러: {error_message}",
        ErrorType.VALIDATION_ERROR,
        {"original_error": error_message, "field": field}
    )


def create_error_response(error: ManagerError, operation: str) -> Dict[str, Any]:
    """
    에러 응답 생성
    
    Args:
        error: ManagerError 인스턴스
        operation: 수행 중이던 작업
        
    Returns:
        에러 응답 딕셔너리
    """
    return {
        "success": False,
        "error_type": error.error_type,
        "message": error.message,
        "operation": operation,
        "details": error.details,
        "timestamp": None  # 호출자가 설정
    }


def log_error_with_context(logger, error: Exception, operation: str, context: Dict[str, Any] = None):
    """
    컨텍스트와 함께 에러 로깅
    
    Args:
        logger: 로거 인스턴스
        error: 에러
        operation: 수행 중이던 작업
        context: 추가 컨텍스트
    """
    context = context or {}
    
    logger.error(f"Operation failed: {operation}")
    logger.error(f"Error: {str(error)}")
    logger.error(f"Context: {context}")
    logger.error(f"Traceback: {traceback.format_exc()}")


def validate_session_id(session_id: str) -> bool:
    """
    세션 ID 유효성 검증
    
    Args:
        session_id: 검증할 세션 ID
        
    Returns:
        유효성 여부
    """
    if not session_id:
        return False
    
    # UUID 형식 검증 (간단한 검증)
    if len(session_id) != 36:
        return False
    
    if session_id.count('-') != 4:
        return False
    
    return True


def validate_entity_id(entity_id: str) -> bool:
    """
    엔티티 ID 유효성 검증
    
    Args:
        entity_id: 검증할 엔티티 ID
        
    Returns:
        유효성 여부
    """
    if not entity_id:
        return False
    
    # UUID 형식 또는 정적 ID 형식 검증
    if len(entity_id) == 36 and entity_id.count('-') == 4:
        return True  # UUID 형식
    
    if entity_id.startswith(('NPC_', 'PLAYER_', 'MONSTER_', 'OBJECT_')):
        return True  # 정적 ID 형식
    
    return False
