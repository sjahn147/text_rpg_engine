"""
핀 이름 필드 추가 마이그레이션 실행 스크립트
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from database.connection import DatabaseConnection


async def run_migration():
    """마이그레이션 실행"""
    db = DatabaseConnection()
    pool = await db.pool
    
    async with pool.acquire() as conn:
        try:
            # pin_name 컬럼 추가
            await conn.execute("""
                ALTER TABLE game_data.pin_positions
                ADD COLUMN IF NOT EXISTS pin_name VARCHAR(100) DEFAULT '새 핀 01';
            """)
            print("✓ pin_name 컬럼 추가 완료")
            
            # 기존 데이터에 기본 이름 설정 (CTE 사용)
            await conn.execute("""
                WITH numbered_pins AS (
                    SELECT 
                        pin_id,
                        '새 핀 ' || LPAD(ROW_NUMBER() OVER (ORDER BY created_at)::text, 2, '0') AS new_name
                    FROM game_data.pin_positions
                    WHERE pin_name IS NULL OR pin_name = '새 핀 01'
                )
                UPDATE game_data.pin_positions
                SET pin_name = numbered_pins.new_name
                FROM numbered_pins
                WHERE pin_positions.pin_id = numbered_pins.pin_id;
            """)
            print("✓ 기존 데이터에 기본 이름 설정 완료")
            
            # NOT NULL 제약조건 추가
            await conn.execute("""
                ALTER TABLE game_data.pin_positions
                ALTER COLUMN pin_name SET NOT NULL;
            """)
            print("✓ NOT NULL 제약조건 추가 완료")
            
            # 코멘트 추가
            await conn.execute("""
                COMMENT ON COLUMN game_data.pin_positions.pin_name IS '핀 표시 이름 (사용자 친화적 이름)';
            """)
            print("✓ 코멘트 추가 완료")
            
            print("\n✅ 마이그레이션 완료!")
            
        except Exception as e:
            print(f"\n❌ 마이그레이션 실패: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(run_migration())

