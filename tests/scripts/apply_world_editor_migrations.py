"""
월드 에디터 마이그레이션 적용 스크립트
"""
import asyncio
import asyncpg
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


async def apply_migrations():
    """마이그레이션 적용"""
    # 데이터베이스 연결 정보
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", 5432))
    db_name = os.getenv("DB_NAME", "rpg_engine")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "")
    
    # 마이그레이션 파일 경로
    migration_file = Path(__file__).parent.parent / "database" / "setup" / "world_editor_migrations.sql"
    
    if not migration_file.exists():
        print(f"❌ 마이그레이션 파일을 찾을 수 없습니다: {migration_file}")
        return False
    
    try:
        # 데이터베이스 연결
        conn = await asyncpg.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        
        print(f"✓ 데이터베이스 연결 성공: {db_name}")
        
        # 마이그레이션 파일 읽기
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # 마이그레이션 실행
        print("마이그레이션 적용 중...")
        await conn.execute(migration_sql)
        
        print("✓ 마이그레이션 적용 완료")
        
        # 테이블 확인
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'game_data' 
            AND table_name IN ('map_metadata', 'pin_positions', 'world_roads')
            ORDER BY table_name
        """)
        
        print("\n생성된 테이블:")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 마이그레이션 적용 실패: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(apply_migrations())
    exit(0 if success else 1)
