"""
runtime_objects 테이블에 잘못된 값이 들어갔는지 확인
"""
import asyncio
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

os.chdir(project_root)

from database.connection import DatabaseConnection
import uuid

async def check():
    db = DatabaseConnection()
    pool = await db.pool
    
    async with pool.acquire() as conn:
        # runtime_objects 테이블 확인
        rows = await conn.fetch("""
            SELECT runtime_object_id, game_object_id, session_id
            FROM runtime_data.runtime_objects
            ORDER BY created_at DESC
            LIMIT 20
        """)
        
        print("=== runtime_objects 테이블 확인 ===\n")
        print(f"총 {len(rows)}개 레코드\n")
        
        invalid_count = 0
        for r in rows:
            runtime_object_id = r['runtime_object_id']
            game_object_id = r['game_object_id']
            
            # UUID 형식인지 확인
            is_uuid = False
            try:
                if isinstance(runtime_object_id, str) and len(runtime_object_id) == 36 and '-' in runtime_object_id:
                    uuid.UUID(runtime_object_id)
                    is_uuid = True
            except (ValueError, AttributeError):
                pass
            
            if not is_uuid:
                invalid_count += 1
                print(f"❌ 잘못된 값 발견:")
                print(f"   runtime_object_id: {runtime_object_id} (타입: {type(runtime_object_id).__name__})")
                print(f"   game_object_id: {game_object_id}")
                print(f"   session_id: {r['session_id']}")
                print()
        
        if invalid_count == 0:
            print("✅ 모든 runtime_object_id가 올바른 UUID 형식입니다.")
        else:
            print(f"⚠️ {invalid_count}개의 잘못된 값이 발견되었습니다.")
            print("\n문제 원인:")
            print("1. CellManager에서 game_object_id를 runtime_object_id로 사용")
            print("2. interact_with_object에서 문자열 ID를 runtime_objects에 INSERT")

if __name__ == "__main__":
    asyncio.run(check())

