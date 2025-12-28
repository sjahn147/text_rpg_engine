"""
기존 데이터베이스 삭제 및 MVP 스키마 생성 스크립트
"""
import asyncio
import asyncpg

async def reset_database():
    """기존 데이터베이스 삭제 및 MVP 스키마 생성"""
    try:
        # 데이터베이스 연결
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='2696Sjbj!',
            database='rpg_engine'
        )
        
        print("🗑️ 기존 데이터베이스 삭제 중...")
        
        # 기존 스키마 삭제 (CASCADE로 모든 테이블과 데이터 삭제)
        await conn.execute("DROP SCHEMA IF EXISTS game_data CASCADE;")
        await conn.execute("DROP SCHEMA IF EXISTS reference_layer CASCADE;")
        await conn.execute("DROP SCHEMA IF EXISTS runtime_data CASCADE;")
        
        print("✅ 기존 스키마 삭제 완료")
        
        await conn.close()
        print("✅ 데이터베이스 리셋 완료")
        
    except Exception as e:
        print(f"❌ 데이터베이스 리셋 실패: {str(e)}")

if __name__ == "__main__":
    asyncio.run(reset_database())
