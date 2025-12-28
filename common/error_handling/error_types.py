"""
에러 처리 시스템 - 계층별 에러 타입 정의
RPG Engine의 모든 에러를 체계적으로 분류하고 처리
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import traceback

class ErrorSeverity(str, Enum):
    """에러 심각도"""
    LOW = "low"           # 경고 수준
    MEDIUM = "medium"     # 주의 수준  
    HIGH = "high"         # 오류 수준
    CRITICAL = "critical" # 치명적 수준

class ErrorCategory(str, Enum):
    """에러 카테고리"""
    DATABASE = "database"
    VALIDATION = "validation"
    BUSINESS_LOGIC = "business_logic"
    NETWORK = "network"
    SYSTEM = "system"
    USER_INPUT = "user_input"

@dataclass
class ErrorContext:
    """에러 컨텍스트 정보"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    entity_id: Optional[str] = None
    cell_id: Optional[str] = None
    action: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class RPGEngineError(Exception):
    """RPG Engine 기본 에러 클래스"""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        context: Optional[ErrorContext] = None,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.category = category
        self.context = context or ErrorContext()
        self.original_error = original_error
        self.details = details or {}
        self.timestamp = datetime.now()
        self.traceback = traceback.format_exc()
    
    def to_dict(self) -> Dict[str, Any]:
        """에러 정보를 딕셔너리로 변환"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "severity": self.severity.value,
            "category": self.category.value,
            "context": {
                "user_id": self.context.user_id,
                "session_id": self.context.session_id,
                "entity_id": self.context.entity_id,
                "cell_id": self.context.cell_id,
                "action": self.context.action,
                "timestamp": self.context.timestamp.isoformat()
            },
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "traceback": self.traceback
        }

class DatabaseError(RPGEngineError):
    """데이터베이스 관련 에러"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "DATABASE_ERROR",
        severity: ErrorSeverity = ErrorSeverity.HIGH,
        context: Optional[ErrorContext] = None,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            severity=severity,
            category=ErrorCategory.DATABASE,
            context=context,
            original_error=original_error,
            details=details
        )

class ConnectionError(DatabaseError):
    """데이터베이스 연결 에러"""
    
    def __init__(
        self,
        message: str = "데이터베이스 연결 실패",
        error_code: str = "CONNECTION_ERROR",
        context: Optional[ErrorContext] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            severity=ErrorSeverity.CRITICAL,
            context=context,
            original_error=original_error
        )

class QueryError(DatabaseError):
    """SQL 쿼리 에러"""
    
    def __init__(
        self,
        message: str,
        query: Optional[str] = None,
        error_code: str = "QUERY_ERROR",
        context: Optional[ErrorContext] = None,
        original_error: Optional[Exception] = None
    ):
        details = {"query": query} if query else {}
        super().__init__(
            message=message,
            error_code=error_code,
            severity=ErrorSeverity.HIGH,
            context=context,
            original_error=original_error,
            details=details
        )

class ValidationError(RPGEngineError):
    """데이터 검증 에러"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        error_code: str = "VALIDATION_ERROR",
        context: Optional[ErrorContext] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        validation_details = {"field": field, "value": value}
        if details:
            validation_details.update(details)
        
        super().__init__(
            message=message,
            error_code=error_code,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.VALIDATION,
            context=context,
            details=validation_details
        )

class BusinessLogicError(RPGEngineError):
    """비즈니스 로직 에러"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "BUSINESS_LOGIC_ERROR",
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[ErrorContext] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            severity=severity,
            category=ErrorCategory.BUSINESS_LOGIC,
            context=context,
            details=details
        )

class EntityNotFoundError(BusinessLogicError):
    """엔티티를 찾을 수 없음"""
    
    def __init__(
        self,
        entity_id: str,
        entity_type: Optional[str] = None,
        context: Optional[ErrorContext] = None
    ):
        message = f"엔티티를 찾을 수 없습니다: {entity_id}"
        if entity_type:
            message += f" (타입: {entity_type})"
        
        super().__init__(
            message=message,
            error_code="ENTITY_NOT_FOUND",
            context=context,
            details={"entity_id": entity_id, "entity_type": entity_type}
        )

class CellNotFoundError(BusinessLogicError):
    """셀을 찾을 수 없음"""
    
    def __init__(
        self,
        cell_id: str,
        context: Optional[ErrorContext] = None
    ):
        super().__init__(
            message=f"셀을 찾을 수 없습니다: {cell_id}",
            error_code="CELL_NOT_FOUND",
            context=context,
            details={"cell_id": cell_id}
        )

class SessionNotFoundError(BusinessLogicError):
    """세션을 찾을 수 없음"""
    
    def __init__(
        self,
        session_id: str,
        context: Optional[ErrorContext] = None
    ):
        super().__init__(
            message=f"세션을 찾을 수 없습니다: {session_id}",
            error_code="SESSION_NOT_FOUND",
            context=context,
            details={"session_id": session_id}
        )

class UserInputError(RPGEngineError):
    """사용자 입력 에러"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        error_code: str = "USER_INPUT_ERROR",
        context: Optional[ErrorContext] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        input_details = {"field": field} if field else {}
        if details:
            input_details.update(details)
        
        super().__init__(
            message=message,
            error_code=error_code,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.USER_INPUT,
            context=context,
            details=input_details
        )

class SystemError(RPGEngineError):
    """시스템 에러"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "SYSTEM_ERROR",
        severity: ErrorSeverity = ErrorSeverity.CRITICAL,
        context: Optional[ErrorContext] = None,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            severity=severity,
            category=ErrorCategory.SYSTEM,
            context=context,
            original_error=original_error,
            details=details
        )

class NetworkError(RPGEngineError):
    """네트워크 에러"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "NETWORK_ERROR",
        context: Optional[ErrorContext] = None,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.NETWORK,
            context=context,
            original_error=original_error,
            details=details
        )

# 에러 팩토리 함수들
def create_database_error(
    message: str,
    error_code: str = "DATABASE_ERROR",
    context: Optional[ErrorContext] = None,
    original_error: Optional[Exception] = None
) -> DatabaseError:
    """데이터베이스 에러 생성"""
    return DatabaseError(
        message=message,
        error_code=error_code,
        context=context,
        original_error=original_error
    )

def create_validation_error(
    message: str,
    field: Optional[str] = None,
    value: Optional[Any] = None,
    context: Optional[ErrorContext] = None
) -> ValidationError:
    """검증 에러 생성"""
    return ValidationError(
        message=message,
        field=field,
        value=value,
        context=context
    )

def create_business_logic_error(
    message: str,
    error_code: str = "BUSINESS_LOGIC_ERROR",
    context: Optional[ErrorContext] = None,
    details: Optional[Dict[str, Any]] = None
) -> BusinessLogicError:
    """비즈니스 로직 에러 생성"""
    return BusinessLogicError(
        message=message,
        error_code=error_code,
        context=context,
        details=details
    )

def create_entity_not_found_error(
    entity_id: str,
    entity_type: Optional[str] = None,
    context: Optional[ErrorContext] = None
) -> EntityNotFoundError:
    """엔티티 없음 에러 생성"""
    return EntityNotFoundError(
        entity_id=entity_id,
        entity_type=entity_type,
        context=context
    )

def create_cell_not_found_error(
    cell_id: str,
    context: Optional[ErrorContext] = None
) -> CellNotFoundError:
    """셀 없음 에러 생성"""
    return CellNotFoundError(
        cell_id=cell_id,
        context=context
    )

def create_session_not_found_error(
    session_id: str,
    context: Optional[ErrorContext] = None
) -> SessionNotFoundError:
    """세션 없음 에러 생성"""
    return SessionNotFoundError(
        session_id=session_id,
        context=context
    )
