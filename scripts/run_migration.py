"""
DB 마이그레이션 실행 스크립트
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from database.connection import DatabaseConnection


async def run_migration(migration_file: str):
    """마이그레이션 파일 실행"""
    db = DatabaseConnection()
    await db.initialize()
    
    try:
        migration_path = project_root / migration_file
        if not migration_path.exists():
            print(f"❌ 마이그레이션 파일을 찾을 수 없습니다: {migration_path}")
            return False
        
        print(f"📄 마이그레이션 파일 읽기: {migration_path}")
        sql_content = migration_path.read_text(encoding='utf-8')
        
        print("🔄 마이그레이션 실행 중...")
        pool = await db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(sql_content)
        
        print("✅ 마이그레이션 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 마이그레이션 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await db.close()


if __name__ == "__main__":
    migration_file = "database/migrations/add_effect_carrier_to_items_equipment.sql"
    success = asyncio.run(run_migration(migration_file))
    sys.exit(0 if success else 1)

