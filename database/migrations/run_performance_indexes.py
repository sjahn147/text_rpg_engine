"""
성능 최적화 인덱스 마이그레이션 실행 스크립트
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from database.connection import DatabaseConnection


async def run():
    """성능 최적화 인덱스 마이그레이션 실행"""
    db = DatabaseConnection()
    pool = await db.pool
    
    try:
        migration_file = Path(__file__).parent / "add_performance_indexes.sql"
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        async with pool.acquire() as conn:
            print("성능 최적화 인덱스 추가 중...")
            await conn.execute(migration_sql)
            print("✅ 성능 최적화 인덱스 추가 완료!")
    
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        raise
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(run())

