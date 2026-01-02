"""
트랜잭션 데코레이터
"""
from functools import wraps
from typing import Callable, Any
from common.utils.logger import logger


def with_transaction(func: Callable) -> Callable:
    """
    메서드를 트랜잭션으로 래핑하는 데코레이터
    
    사용 예시:
        class MyService:
            def __init__(self, db_connection):
                self.db = db_connection
            
            @with_transaction
            async def update_data(self, data_id: str, conn=None):
                # conn은 자동으로 트랜잭션 내부
                await conn.execute("UPDATE ...")
                return result
    """
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        # conn이 이미 제공된 경우 (중첩 트랜잭션 방지)
        if 'conn' in kwargs and kwargs['conn'] is not None:
            # 이미 트랜잭션 내부이므로 그대로 실행
            return await func(self, *args, **kwargs)
        
        # 데이터베이스 연결 풀 가져오기
        if not hasattr(self, 'db'):
            raise AttributeError(
                f"{self.__class__.__name__}에 'db' 속성이 없습니다. "
                "DatabaseConnection 인스턴스를 'db' 속성에 할당하세요."
            )
        
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                # conn을 kwargs에 추가하여 함수에 전달
                return await func(self, *args, **kwargs, conn=conn)
    
    return wrapper

