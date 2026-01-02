import asyncpg
from typing import Optional
import logging
import os
import sys
from dotenv import load_dotenv
from app.config.app_config import get_db_settings

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        # 설정 통합: app/config/app_config.py 사용
        db_settings = get_db_settings()
        self.host = db_settings.host
        self.port = db_settings.port
        self.user = db_settings.user
        self.password = db_settings.password
        self.database = db_settings.database
        
        # 로깅 설정
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # 연결 상태 관리
        self._pool = None
        self._is_initialized = False
        self._is_closed = False
        
    async def initialize(self) -> None:
        """연결 초기화"""
        if self._is_initialized or self._is_closed:
            return
            
        try:
            # 테스트 환경 고려: 연결 풀 크기 증가
            # 테스트 실행 시 여러 테스트가 동시에 실행될 수 있으므로
            # max_size를 증가시켜 연결 풀 고갈 방지
            is_test = (
                "pytest" in sys.modules or 
                any("pytest" in arg for arg in sys.argv) or
                "PYTEST_CURRENT_TEST" in os.environ
            )
            
            # 연결 풀 크기: 성능과 안정성의 균형
            # 테스트 환경: session 스코프로 연결 풀 공유하므로 적절한 크기 유지
            # 프로덕션: 실제 부하에 맞게 조정
            min_size = 2
            max_size = 15 if is_test else 10  # 테스트: 15 (session 공유로 효율적), 프로덕션: 10
            
            self._pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                min_size=min_size,
                max_size=max_size,
                command_timeout=60  # 테스트 환경에서 타임아웃 증가
            )
            self._is_initialized = True
            self.logger.info(f"Database connection pool initialized successfully (min={min_size}, max={max_size}, test={is_test})")
        except Exception as e:
            self.logger.error(f"Failed to initialize database connection pool: {str(e)}")
            raise
    
    @property
    async def pool(self) -> asyncpg.Pool:
        """데이터베이스 커넥션 풀을 반환합니다"""
        if not self._is_initialized:
            await self.initialize()
        return self._pool
    
    async def close(self):
        """데이터베이스 연결을 종료합니다"""
        if self._pool and not self._is_closed:
            try:
                await self._pool.close()
                self._is_closed = True
                self._is_initialized = False
                self.logger.info("Database connection pool closed successfully")
            except Exception as e:
                self.logger.error(f"Failed to close database connection pool: {str(e)}")
                raise
    
    async def execute_query(self, query: str, *args) -> Optional[list]:
        """
        SQL 쿼리를 실행합니다
        
        Args:
            query: SQL 쿼리 문자열
            *args: 쿼리 파라미터
            
        Returns:
            쿼리 결과 또는 None
        """
        try:
            pool = await self.pool
            async with pool.acquire() as conn:
                result = await conn.fetch(query, *args)
                return result
        except Exception as e:
            self.logger.error(f"Query execution failed: {str(e)}")
            self.logger.error(f"Query: {query}")
            self.logger.error(f"Args: {args}")
            raise
    
    async def execute_transaction(self, queries: list) -> bool:
        """
        여러 쿼리를 트랜잭션으로 실행합니다
        
        Args:
            queries: (query, args) 튜플 리스트
            
        Returns:
            성공 여부
        """
        try:
            pool = await self.pool
            async with pool.acquire() as conn:
                async with conn.transaction():
                    for query, args in queries:
                        await conn.execute(query, *args)
                    return True
        except Exception as e:
            self.logger.error(f"Transaction failed: {str(e)}")
            return False
            
    async def test_connection(self) -> bool:
        """데이터베이스 연결을 테스트합니다."""
        try:
            pool = await self.pool
            async with pool.acquire() as conn:
                await conn.fetchval('SELECT 1')
                self.logger.info("Database connection test successful")
                return True
        except Exception as e:
            self.logger.error(f"Database connection test failed: {str(e)}")
            return False

    async def get_connection(self):
        """데이터베이스 연결을 가져옵니다."""
        pool = await self.pool
        return await pool.acquire()

    async def release_connection(self, connection):
        """데이터베이스 연결을 해제합니다"""
        await connection.release()

    async def execute_single_query(self, query: str, *args) -> Optional[asyncpg.Record]:
        """
        단일 결과를 반환하는 쿼리를 실행합니다
        
        Args:
            query: SQL 쿼리 문자열
            *args: 쿼리 파라미터
            
        Returns:
            단일 결과 레코드 또는 None
        """
        try:
            pool = await self.pool
            async with pool.acquire() as conn:
                result = await conn.fetchrow(query, *args)
                return result
        except Exception as e:
            self.logger.error(f"Single query execution failed: {str(e)}")
            self.logger.error(f"Query: {query}")
            self.logger.error(f"Args: {args}")
            raise

    async def execute_scalar_query(self, query: str, *args) -> Optional[any]:
        """
        스칼라 값을 반환하는 쿼리를 실행합니다
        
        Args:
            query: SQL 쿼리 문자열
            *args: 쿼리 파라미터
            
        Returns:
            스칼라 값 또는 None
        """
        try:
            pool = await self.pool
            async with pool.acquire() as conn:
                result = await conn.fetchval(query, *args)
                return result
        except Exception as e:
            self.logger.error(f"Scalar query execution failed: {str(e)}")
            self.logger.error(f"Query: {query}")
            self.logger.error(f"Args: {args}")
            raise

    async def check_table_exists(self, schema: str, table: str) -> bool:
        """
        테이블이 존재하는지 확인합니다
        
        Args:
            schema: 스키마 이름
            table: 테이블 이름
            
        Returns:
            테이블 존재 여부
        """
        try:
            pool = await self.pool
            async with pool.acquire() as conn:
                result = await conn.fetchval(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = $1 
                        AND table_name = $2
                    );
                    """,
                    schema, table
                )
                return result
        except Exception as e:
            self.logger.error(f"Table existence check failed: {str(e)}")
            return False

    async def get_table_columns(self, schema: str, table: str) -> list:
        """
        테이블의 컬럼 정보를 조회합니다
        
        Args:
            schema: 스키마 이름
            table: 테이블 이름
            
        Returns:
            컬럼 정보 리스트
        """
        try:
            pool = await self.pool
            async with pool.acquire() as conn:
                columns = await conn.fetch(
                    """
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = $1 AND table_name = $2
                    ORDER BY ordinal_position
                    """,
                    schema, table
                )
                return [dict(col) for col in columns]
        except Exception as e:
            self.logger.error(f"Column information retrieval failed: {str(e)}")
            return []
