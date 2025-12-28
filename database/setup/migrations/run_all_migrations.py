"""
Phase 1: DB 스키마 마이그레이션 실행 스크립트

모든 마이그레이션을 순차적으로 실행하고 검증합니다.
"""
import asyncio
import sys
from pathlib import Path
from typing import List, Tuple

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from database.connection import DatabaseConnection


async def run_migration_file(conn, file_path: Path) -> Tuple[str, bool, str]:
    """
    마이그레이션 파일 실행
    
    Returns:
        (파일명, 성공 여부, 에러 메시지)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # 트랜잭션으로 실행
        async with conn.transaction():
            await conn.execute(migration_sql)
        
        return (file_path.name, True, "")
    except Exception as e:
        return (file_path.name, False, str(e))


async def verify_migration(conn, migration_name: str) -> bool:
    """
    마이그레이션 검증
    
    Args:
        conn: 데이터베이스 연결
        migration_name: 마이그레이션 이름 ('entity', 'world_object', 'map_metadata')
    
    Returns:
        검증 성공 여부
    """
    try:
        if migration_name == 'entity':
            # Entity 필드 검증
            result = await conn.fetchval("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_schema = 'game_data' 
                AND table_name = 'entities' 
                AND column_name IN ('default_position_3d', 'entity_size')
            """)
            return result == 2
        
        elif migration_name == 'world_object':
            # World Objects 필드 검증
            result = await conn.fetchval("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_schema = 'game_data' 
                AND table_name = 'world_objects' 
                AND column_name IN ('wall_mounted', 'passable', 'movable', 
                                     'object_height', 'object_width', 'object_depth', 'object_weight')
            """)
            return result == 7
        
        elif migration_name == 'map_metadata':
            # Map Metadata 필드 검증
            result = await conn.fetchval("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_schema = 'game_data' 
                AND table_name = 'map_metadata' 
                AND column_name IN ('map_level', 'parent_entity_id', 'parent_entity_type')
            """)
            return result == 3
        
        return False
    except Exception as e:
        print(f"❌ 검증 중 오류 발생: {e}")
        return False


async def run_all_migrations():
    """모든 마이그레이션 실행"""
    db = DatabaseConnection()
    pool = await db.pool
    
    migrations_dir = Path(__file__).parent
    migration_files = [
        (migrations_dir / "add_entity_position_size.sql", "entity"),
        (migrations_dir / "add_world_object_properties.sql", "world_object"),
        (migrations_dir / "add_map_metadata_hierarchy.sql", "map_metadata"),
    ]
    
    print("=" * 60)
    print("Phase 1: DB 스키마 마이그레이션 시작")
    print("=" * 60)
    
    async with pool.acquire() as conn:
        results = []
        
        for migration_file, migration_name in migration_files:
            if not migration_file.exists():
                print(f"❌ 마이그레이션 파일 없음: {migration_file.name}")
                results.append((migration_file.name, False, "파일 없음"))
                continue
            
            print(f"\n📄 실행 중: {migration_file.name}")
            file_name, success, error = await run_migration_file(conn, migration_file)
            
            if success:
                print(f"✓ 마이그레이션 실행 완료: {file_name}")
                
                # 검증
                print(f"  검증 중...")
                if await verify_migration(conn, migration_name):
                    print(f"  ✓ 검증 성공: {migration_name}")
                else:
                    print(f"  ⚠️ 검증 실패: {migration_name}")
                    results.append((file_name, False, "검증 실패"))
                    continue
            else:
                print(f"❌ 마이그레이션 실패: {file_name}")
                print(f"   오류: {error}")
            
            results.append((file_name, success, error))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("마이그레이션 결과 요약")
    print("=" * 60)
    
    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)
    
    for file_name, success, error in results:
        status = "✓ 성공" if success else "❌ 실패"
        print(f"{status}: {file_name}")
        if error and not success:
            print(f"   오류: {error}")
    
    print(f"\n총 {total_count}개 중 {success_count}개 성공")
    
    if success_count == total_count:
        print("\n✅ 모든 마이그레이션이 성공적으로 완료되었습니다!")
    else:
        print(f"\n⚠️ {total_count - success_count}개의 마이그레이션이 실패했습니다.")
        sys.exit(1)
    
    await db.close()


if __name__ == "__main__":
    asyncio.run(run_all_migrations())

