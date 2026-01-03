"""
데이터베이스 연결 관리 모듈
- 연결의 생명주기 관리
- 테스트 환경별 연결 분리
- 비동기 이벤트 루프 관리
"""
import asyncio
import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
from database.connection import DatabaseConnection
from app.config.app_config import get_db_settings

logger = logging.getLogger(__name__)


class DatabaseConnectionManager:
    """데이터베이스 연결 관리자"""
    
    def __init__(self):
        self._connections: Dict[str, DatabaseConnection] = {}
        self._pools: Dict[str, Any] = {}
        self._event_loops: Dict[str, asyncio.AbstractEventLoop] = {}
        self._is_initialized = False
    
    async def initialize(self, connection_id: str = "default") -> DatabaseConnection:
        """연결 초기화"""
        try:
            if connection_id in self._connections:
                return self._connections[connection_id]
            
            # 독립적인 이벤트 루프 생성 (테스트 환경)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._event_loops[connection_id] = loop
            
            # DB 연결 생성
            db_connection = DatabaseConnection()
            await db_connection.initialize()
            
            self._connections[connection_id] = db_connection
            self._pools[connection_id] = db_connection.pool
            self._is_initialized = True
            
            logger.info(f"Database connection '{connection_id}' initialized successfully")
            return db_connection
            
        except Exception as e:
            logger.error(f"Failed to initialize database connection '{connection_id}': {str(e)}")
            raise
    
    async def get_connection(self, connection_id: str = "default") -> DatabaseConnection:
        """연결 조회"""
        if connection_id not in self._connections:
            return await self.initialize(connection_id)
        return self._connections[connection_id]
    
    async def close_connection(self, connection_id: str = "default") -> None:
        """연결 종료"""
        try:
            if connection_id in self._connections:
                connection = self._connections[connection_id]
                await connection.close()
                del self._connections[connection_id]
                
            if connection_id in self._pools:
                pool = self._pools[connection_id]
                await pool.close()
                del self._pools[connection_id]
                
            if connection_id in self._event_loops:
                loop = self._event_loops[connection_id]
                if not loop.is_closed():
                    loop.close()
                del self._event_loops[connection_id]
                
            logger.info(f"Database connection '{connection_id}' closed successfully")
            
        except Exception as e:
            logger.error(f"Failed to close database connection '{connection_id}': {str(e)}")
            raise
    
    async def close_all_connections(self) -> None:
        """모든 연결 종료"""
        connection_ids = list(self._connections.keys())
        for connection_id in connection_ids:
            await self.close_connection(connection_id)
    
    @asynccontextmanager
    async def get_managed_connection(self, connection_id: str = "default"):
        """관리되는 연결 컨텍스트 매니저"""
        connection = None
        try:
            connection = await self.get_connection(connection_id)
            yield connection
        finally:
            if connection:
                # 연결은 풀에서 자동으로 관리
                pass
    
    def is_initialized(self) -> bool:
        """초기화 여부 확인"""
        return self._is_initialized
    
    def get_connection_count(self) -> int:
        """활성 연결 수"""
        return len(self._connections)


# 전역 연결 관리자 인스턴스
connection_manager = DatabaseConnectionManager()


class TestDatabaseManager:
    """테스트용 데이터베이스 관리자"""
    
    def __init__(self):
        self.test_connections: Dict[str, DatabaseConnection] = {}
        self.test_pools: Dict[str, Any] = {}
    
    async def create_test_connection(self, test_id: str) -> DatabaseConnection:
        """테스트 연결 생성"""
        try:
            # 테스트용 독립 이벤트 루프
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 테스트용 DB 연결
            db_connection = DatabaseConnection()
            await db_connection.initialize()
            
            self.test_connections[test_id] = db_connection
            self.test_pools[test_id] = db_connection.pool
            
            logger.info(f"Test database connection '{test_id}' created")
            return db_connection
            
        except Exception as e:
            logger.error(f"Failed to create test connection '{test_id}': {str(e)}")
            raise
    
    async def cleanup_test_connection(self, test_id: str) -> None:
        """테스트 연결 정리"""
        try:
            if test_id in self.test_connections:
                connection = self.test_connections[test_id]
                await connection.close()
                del self.test_connections[test_id]
                
            if test_id in self.test_pools:
                pool = self.test_pools[test_id]
                # pool이 None이 아니고 이미 닫히지 않았을 때만 닫기
                if pool is not None:
                    try:
                        await pool.close()
                    except Exception as pool_error:
                        # pool이 이미 닫혔거나 None인 경우 무시
                        logger.debug(f"Pool cleanup warning for '{test_id}': {str(pool_error)}")
                del self.test_pools[test_id]
                
            logger.info(f"Test database connection '{test_id}' cleaned up")
            
        except Exception as e:
            logger.error(f"Failed to cleanup test connection '{test_id}': {str(e)}")
            # teardown 오류는 테스트 결과에 영향을 주지 않도록 예외를 다시 발생시키지 않음
            # raise
    
    async def cleanup_all_test_connections(self) -> None:
        """모든 테스트 연결 정리"""
        test_ids = list(self.test_connections.keys())
        for test_id in test_ids:
            await self.cleanup_test_connection(test_id)


# 전역 테스트 관리자 인스턴스
test_db_manager = TestDatabaseManager()
