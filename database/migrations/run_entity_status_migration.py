"""
Entity Status 마이그레이션 실행 스크립트
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from database.connection import DatabaseConnection


async def run_migration():
    """마이그레이션 실행"""
    db = DatabaseConnection()
    pool = await db.pool
    
    migration_file = Path(__file__).parent / "add_entity_status.sql"
    
    print("=" * 60)
    print("Entity Status 마이그레이션 시작")
    print("=" * 60)
    
    async with pool.acquire() as conn:
        try:
            with open(migration_file, 'r', encoding='utf-8') as f:
                migration_sql = f.read()
            
            # 트랜잭션으로 실행
            async with conn.transaction():
                await conn.execute(migration_sql)
            
            print(f"✓ 마이그레이션 실행 완료: {migration_file.name}")
            
            # 검증
            print("  검증 중...")
            result = await conn.fetchval("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_schema = 'game_data' 
                AND table_name = 'entities' 
                AND column_name = 'entity_status'
            """)
            
            if result == 1:
                print("  ✓ 검증 성공: entity_status 필드가 추가되었습니다")
            else:
                print(f"  ⚠️ 검증 실패: {result}개 필드만 발견됨 (예상: 1개)")
                sys.exit(1)
            
        except Exception as e:
            print(f"❌ 마이그레이션 실패: {e}")
            sys.exit(1)
    
    print("\n✅ 마이그레이션이 성공적으로 완료되었습니다!")
    await db.close()


if __name__ == "__main__":
    asyncio.run(run_migration())

