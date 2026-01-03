#!/usr/bin/env python3
"""
데이터베이스 마이그레이션 실행 스크립트

사용법:
    python scripts/run_migration.py <migration_file>
    
예시:
    python scripts/run_migration.py database/migrations/add_quests_table.sql
"""
import sys
import os
import asyncio
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.connection import DatabaseConnection
from common.utils.logger import logger


async def run_migration(migration_file: str):
    """
    마이그레이션 파일 실행
    
    Args:
        migration_file: 마이그레이션 SQL 파일 경로
    """
    migration_path = Path(migration_file)
    
    if not migration_path.exists():
        logger.error(f"마이그레이션 파일을 찾을 수 없습니다: {migration_file}")
        sys.exit(1)
    
    logger.info(f"마이그레이션 실행 시작: {migration_file}")
    
    # SQL 파일 읽기
    with open(migration_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 데이터베이스 연결
    db = DatabaseConnection()
    
    try:
        pool = await db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                # 마이그레이션 실행
                await conn.execute(sql_content)
                logger.info(f"마이그레이션 성공: {migration_file}")
    except Exception as e:
        logger.error(f"마이그레이션 실패: {migration_file}")
        logger.error(f"오류: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        await db.close()


async def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        logger.error("사용법: python scripts/run_migration.py <migration_file>")
        sys.exit(1)
    
    migration_file = sys.argv[1]
    await run_migration(migration_file)


if __name__ == "__main__":
    asyncio.run(main())

