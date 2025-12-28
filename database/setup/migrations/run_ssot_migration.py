"""
SSOT Phase 3: 데이터 마이그레이션 실행 스크립트

owner_name 제거 및 고아 참조 정리
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from database.connection import DatabaseConnection


async def run_migration_file(conn, file_path: Path) -> tuple[str, bool, str]:
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


async def verify_owner_name_removed(conn) -> bool:
    """owner_name이 제거되었는지 확인"""
    location_count = await conn.fetchval("""
        SELECT COUNT(*) 
        FROM game_data.world_locations
        WHERE location_properties->'ownership'->>'owner_name' IS NOT NULL
    """)
    
    cell_count = await conn.fetchval("""
        SELECT COUNT(*) 
        FROM game_data.world_cells
        WHERE cell_properties->'ownership'->>'owner_name' IS NOT NULL
    """)
    
    return location_count == 0 and cell_count == 0


async def verify_orphan_references_cleaned(conn) -> bool:
    """고아 참조가 정리되었는지 확인"""
    # Location의 고아 owner_entity_id 확인
    orphan_location_owners = await conn.fetchval("""
        SELECT COUNT(*) 
        FROM game_data.world_locations
        WHERE location_properties->'ownership'->>'owner_entity_id' IS NOT NULL
          AND NOT EXISTS (
              SELECT 1 FROM game_data.entities 
              WHERE entity_id = location_properties->'ownership'->>'owner_entity_id'
          )
    """)
    
    # Cell의 고아 owner_entity_id 확인
    orphan_cell_owners = await conn.fetchval("""
        SELECT COUNT(*) 
        FROM game_data.world_cells
        WHERE cell_properties->'ownership'->>'owner_entity_id' IS NOT NULL
          AND NOT EXISTS (
              SELECT 1 FROM game_data.entities 
              WHERE entity_id = cell_properties->'ownership'->>'owner_entity_id'
          )
    """)
    
    return orphan_location_owners == 0 and orphan_cell_owners == 0


async def run_migration():
    """마이그레이션 실행"""
    db = DatabaseConnection()
    pool = await db.pool
    
    migrations_dir = Path(__file__).parent
    migration_files = [
        migrations_dir / "remove_owner_name_ssot.sql",
        migrations_dir / "cleanup_orphan_references_ssot.sql",
    ]
    
    print("=" * 60)
    print("SSOT Phase 3: 데이터 마이그레이션 시작")
    print("=" * 60)
    print("⚠️  주의: 이 마이그레이션은 데이터를 수정합니다.")
    print("    백업을 권장합니다.")
    print()
    
    async with pool.acquire() as conn:
        results = []
        
        for migration_file in migration_files:
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
                if "owner_name" in file_name:
                    if await verify_owner_name_removed(conn):
                        print(f"  ✓ 검증 성공: owner_name이 모두 제거되었습니다")
                    else:
                        print(f"  ⚠️ 검증 실패: owner_name이 일부 남아있습니다")
                        results.append((file_name, False, "검증 실패"))
                        continue
                elif "orphan" in file_name:
                    if await verify_orphan_references_cleaned(conn):
                        print(f"  ✓ 검증 성공: 고아 참조가 모두 정리되었습니다")
                    else:
                        print(f"  ⚠️ 검증 실패: 고아 참조가 일부 남아있습니다")
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
        if not success and error:
            print(f"   오류: {error}")
    
    print(f"\n총 {total_count}개 중 {success_count}개 성공")
    
    if success_count == total_count:
        print("\n✅ 모든 마이그레이션이 성공적으로 완료되었습니다!")
    else:
        print("\n⚠️ 일부 마이그레이션이 실패했습니다. 위의 오류를 확인하세요.")
        sys.exit(1)
    
    await db.close()


if __name__ == "__main__":
    asyncio.run(run_migration())

