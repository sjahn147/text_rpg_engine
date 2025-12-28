import asyncio
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import DatabaseConnection

async def fix_triggers():
    """트리거 함수의 무한 재귀 문제를 수정합니다."""
    db = DatabaseConnection()
    
    try:
        # SQL 스크립트 읽기
        with open('docs/architecture/db_schema/02_fix_triggers.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 데이터베이스에 실행
        pool = await db.pool
        async with pool.acquire() as conn:
            await conn.execute(sql_script)
        
        print("트리거 수정이 완료되었습니다.")
        
    except Exception as e:
        print(f"트리거 수정 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_triggers()) 