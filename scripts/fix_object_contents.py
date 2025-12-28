"""
오브젝트의 contents에서 이름을 제거하고 빈 배열로 변경
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from database.connection import DatabaseConnection

async def fix_contents():
    db = DatabaseConnection()
    pool = await db.pool
    async with pool.acquire() as conn:
        # contents를 빈 배열로 변경
        await conn.execute("""
            UPDATE game_data.world_objects 
            SET properties = jsonb_set(properties, '{contents}', '[]'::jsonb)
            WHERE properties->>'contents' IS NOT NULL
        """)
        print("✅ 오브젝트 contents를 빈 배열로 업데이트했습니다.")

if __name__ == "__main__":
    asyncio.run(fix_contents())

