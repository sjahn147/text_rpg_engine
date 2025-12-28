"""
간단한 데이터베이스 연결 테스트
Pydantic 없이 직접 환경 변수를 읽어서 연결을 시도합니다.
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def test_simple_connection():
    """간단한 데이터베이스 연결 테스트"""
    print("=== 간단한 데이터베이스 연결 테스트 ===")
    
    # .env 파일 로드
    load_dotenv()
    
    # 환경 변수 직접 읽기
    host = os.getenv('DB_HOST', 'localhost')
    port = int(os.getenv('DB_PORT', '5432'))
    user = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', '')
    database = os.getenv('DB_NAME', 'rpg_engine')
    
    print(f"연결 설정:")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  User: {user}")
    print(f"  Password: '{password}'")
    print(f"  Database: {database}")
    
    try:
        # 직접 연결 시도
        print("\n직접 연결 시도...")
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        print("✅ 데이터베이스 연결 성공!")
        
        # 간단한 쿼리 테스트
        result = await conn.fetchval('SELECT 1')
        print(f"✅ 쿼리 테스트 성공: {result}")
        
        # 연결 종료
        await conn.close()
        print("✅ 연결 종료")
        
        return True
        
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {str(e)}")
        print(f"오류 타입: {type(e).__name__}")
        return False

if __name__ == "__main__":
    asyncio.run(test_simple_connection())
