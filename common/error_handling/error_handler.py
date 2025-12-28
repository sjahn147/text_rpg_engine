"""
에러 처리 중앙 관리 시스템
구조화된 로깅, 에러 추적, 복구 메커니즘
"""
import asyncio
import json
import sys
import os
from typing import Optional, Dict, Any, List, Callable, Union
from datetime import datetime
from dataclasses import dataclass
import structlog
from structlog import get_logger

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from common.error_handling.error_types import (
    RPGEngineError, DatabaseError, ValidationError, BusinessLogicError,
    ErrorSeverity, ErrorCategory, ErrorContext
)

@dataclass
class ErrorRecoveryAction:
    """에러 복구 액션"""
    action_type: str
    description: str
    handler: Callable
    retry_count: int = 0
    max_retries: int = 3

class ErrorHandler:
    """에러 처리 중앙 관리 클래스"""
    
    def __init__(self):
        self.logger = get_logger("error_handler")
        self.error_history: List[Dict[str, Any]] = []
        self.recovery_actions: Dict[str, ErrorRecoveryAction] = {}
        self.error_counts: Dict[str, int] = {}
        self.setup_logging()
    
    def setup_logging(self):
        """구조화된 로깅 설정"""
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    async def handle_error(
        self,
        error: Union[Exception, RPGEngineError],
        context: Optional[ErrorContext] = None,
        auto_recovery: bool = True
    ) -> Dict[str, Any]:
        """에러 처리 메인 메서드"""
        try:
            # 에러 타입 확인 및 변환
            if not isinstance(error, RPGEngineError):
                error = self._convert_to_rpg_error(error, context)
            
            # 에러 로깅
            await self._log_error(error)
            
            # 에러 카운팅
            self._increment_error_count(error)
            
            # 에러 히스토리 저장
            self._add_to_history(error)
            
            # 자동 복구 시도
            recovery_result = None
            if auto_recovery:
                recovery_result = await self._attempt_recovery(error)
            
            # 에러 정보 반환
            return {
                "error_id": error.error_code,
                "message": error.message,
                "severity": error.severity.value,
                "category": error.category.value,
                "recovery_attempted": auto_recovery,
                "recovery_result": recovery_result,
                "timestamp": error.timestamp.isoformat()
            }
            
        except Exception as e:
            # 에러 처리 중 에러 발생
            self.logger.error(
                "Error handling failed",
                error=str(e),
                original_error=str(error),
                exc_info=True
            )
            return {
                "error_id": "ERROR_HANDLING_FAILED",
                "message": f"에러 처리 실패: {str(e)}",
                "severity": "critical",
                "category": "system",
                "recovery_attempted": False,
                "recovery_result": None,
                "timestamp": datetime.now().isoformat()
            }
    
    def _convert_to_rpg_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None
    ) -> RPGEngineError:
        """일반 Exception을 RPGEngineError로 변환"""
        if isinstance(error, ConnectionError):
            return DatabaseError(
                message=f"데이터베이스 연결 실패: {str(error)}",
                error_code="CONNECTION_ERROR",
                severity=ErrorSeverity.CRITICAL,
                context=context,
                original_error=error
            )
        elif isinstance(error, ValueError):
            return ValidationError(
                message=f"값 검증 실패: {str(error)}",
                error_code="VALUE_ERROR",
                context=context,
                original_error=error
            )
        elif isinstance(error, KeyError):
            return ValidationError(
                message=f"키 오류: {str(error)}",
                error_code="KEY_ERROR",
                context=context,
                original_error=error
            )
        else:
            return RPGEngineError(
                message=f"예상치 못한 에러: {str(error)}",
                error_code="UNEXPECTED_ERROR",
                severity=ErrorSeverity.HIGH,
                context=context,
                original_error=error
            )
    
    async def _log_error(self, error: RPGEngineError):
        """에러 로깅"""
        log_data = {
            "error_type": error.__class__.__name__,
            "error_code": error.error_code,
            "message": error.message,
            "severity": error.severity.value,
            "category": error.category.value,
            "context": {
                "user_id": error.context.user_id,
                "session_id": error.context.session_id,
                "entity_id": error.context.entity_id,
                "cell_id": error.context.cell_id,
                "action": error.context.action
            },
            "details": error.details,
            "timestamp": error.timestamp.isoformat()
        }
        
        # 심각도별 로깅 레벨
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical("Critical error occurred", **log_data)
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error("High severity error occurred", **log_data)
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning("Medium severity error occurred", **log_data)
        else:
            self.logger.info("Low severity error occurred", **log_data)
    
    def _increment_error_count(self, error: RPGEngineError):
        """에러 카운팅"""
        key = f"{error.category.value}_{error.error_code}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
    
    def _add_to_history(self, error: RPGEngineError):
        """에러 히스토리에 추가"""
        error_record = error.to_dict()
        self.error_history.append(error_record)
        
        # 히스토리 크기 제한 (최근 1000개만 유지)
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-1000:]
    
    async def _attempt_recovery(self, error: RPGEngineError) -> Optional[Dict[str, Any]]:
        """에러 복구 시도"""
        recovery_key = f"{error.category.value}_{error.error_code}"
        
        if recovery_key not in self.recovery_actions:
            return None
        
        recovery_action = self.recovery_actions[recovery_key]
        
        if recovery_action.retry_count >= recovery_action.max_retries:
            return {
                "success": False,
                "message": f"최대 재시도 횟수 초과: {recovery_action.max_retries}",
                "retry_count": recovery_action.retry_count
        }
        
        try:
            result = await recovery_action.handler(error)
            recovery_action.retry_count = 0  # 성공 시 카운터 리셋
            
            return {
                "success": True,
                "message": "복구 성공",
                "result": result,
                "retry_count": recovery_action.retry_count
            }
            
        except Exception as e:
            recovery_action.retry_count += 1
            
            return {
                "success": False,
                "message": f"복구 실패: {str(e)}",
                "retry_count": recovery_action.retry_count,
                "max_retries": recovery_action.max_retries
            }
    
    def register_recovery_action(
        self,
        error_category: ErrorCategory,
        error_code: str,
        action_type: str,
        description: str,
        handler: Callable,
        max_retries: int = 3
    ):
        """복구 액션 등록"""
        key = f"{error_category.value}_{error_code}"
        self.recovery_actions[key] = ErrorRecoveryAction(
            action_type=action_type,
            description=description,
            handler=handler,
            max_retries=max_retries
        )
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """에러 통계 조회"""
        total_errors = sum(self.error_counts.values())
        
        # 카테고리별 통계
        category_stats = {}
        for key, count in self.error_counts.items():
            category = key.split('_')[0]
            if category not in category_stats:
                category_stats[category] = 0
            category_stats[category] += count
        
        # 심각도별 통계
        severity_stats = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for error_record in self.error_history:
            severity = error_record.get("severity", "medium")
            if severity in severity_stats:
                severity_stats[severity] += 1
        
        return {
            "total_errors": total_errors,
            "category_stats": category_stats,
            "severity_stats": severity_stats,
            "error_counts": self.error_counts,
            "recovery_actions": len(self.recovery_actions)
        }
    
    def get_recent_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """최근 에러 조회"""
        return self.error_history[-limit:] if self.error_history else []
    
    def clear_error_history(self):
        """에러 히스토리 초기화"""
        self.error_history.clear()
        self.error_counts.clear()
    
    async def export_error_report(self, file_path: str):
        """에러 보고서 내보내기"""
        report = {
            "export_timestamp": datetime.now().isoformat(),
            "statistics": self.get_error_statistics(),
            "recent_errors": self.get_recent_errors(100),
            "recovery_actions": {
                key: {
                    "action_type": action.action_type,
                    "description": action.description,
                    "max_retries": action.max_retries
                }
                for key, action in self.recovery_actions.items()
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Error report exported to {file_path}")

# 전역 에러 핸들러 인스턴스
error_handler = ErrorHandler()

# 편의 함수들
async def handle_error(
    error: Union[Exception, RPGEngineError],
    context: Optional[ErrorContext] = None,
    auto_recovery: bool = True
) -> Dict[str, Any]:
    """에러 처리 편의 함수"""
    return await error_handler.handle_error(error, context, auto_recovery)

def register_recovery_action(
    error_category: ErrorCategory,
    error_code: str,
    action_type: str,
    description: str,
    handler: Callable,
    max_retries: int = 3
):
    """복구 액션 등록 편의 함수"""
    error_handler.register_recovery_action(
        error_category, error_code, action_type, description, handler, max_retries
    )

def get_error_statistics() -> Dict[str, Any]:
    """에러 통계 조회 편의 함수"""
    return error_handler.get_error_statistics()

def get_recent_errors(limit: int = 50) -> List[Dict[str, Any]]:
    """최근 에러 조회 편의 함수"""
    return error_handler.get_recent_errors(limit)
