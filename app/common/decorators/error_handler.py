"""
공통 예외 처리 데코레이터
"""
from functools import wraps
from fastapi import HTTPException
from asyncpg.exceptions import ForeignKeyViolationError, UniqueViolationError
from common.utils.logger import logger


def handle_service_errors(func):
    """
    서비스 레이어 메서드의 예외를 HTTPException으로 변환하는 데코레이터
    
    사용 예시:
        @handle_service_errors
        async def delete_entity(self, entity_id: str) -> bool:
            ...
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValueError as e:
            # 비즈니스 로직 오류 (예: 참조 무결성 검증 실패)
            raise HTTPException(status_code=400, detail=str(e))
        except ForeignKeyViolationError as e:
            # 외래키 제약조건 위반
            logger.error(f"ForeignKey violation in {func.__name__}: {e}")
            raise HTTPException(
                status_code=409,
                detail=f"참조 무결성 오류: {str(e)}"
            )
        except UniqueViolationError as e:
            # 고유 제약조건 위반
            logger.error(f"Unique violation in {func.__name__}: {e}")
            raise HTTPException(
                status_code=409,
                detail=f"중복 데이터 오류: {str(e)}"
            )
        except HTTPException:
            # 이미 HTTPException인 경우 그대로 전파
            raise
        except Exception as e:
            # 예상치 못한 오류
            logger.error(
                f"Unexpected error in {func.__name__}: {e}",
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail="내부 서버 오류"
            )
    return wrapper

