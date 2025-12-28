"""
누락된 테이블 생성 스크립트
"""
import asyncio
import asyncpg
from database.connection import DatabaseConnection

async def create_missing_tables():
    """누락된 테이블 생성"""
    db_connection = DatabaseConnection()
    await db_connection.initialize()
    
    try:
        pool = await db_connection.pool
        async with pool.acquire() as conn:
            # cell_occupants 테이블 생성
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS runtime_data.cell_occupants (
                    cell_id VARCHAR(255) NOT NULL,
                    entity_id VARCHAR(255) NOT NULL,
                    entity_type VARCHAR(50) NOT NULL,
                    position JSONB,
                    entered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (cell_id, entity_id),
                    FOREIGN KEY (cell_id) REFERENCES runtime_data.runtime_cells(cell_id) ON DELETE CASCADE,
                    FOREIGN KEY (entity_id) REFERENCES runtime_data.runtime_entities(entity_id) ON DELETE CASCADE
                )
            """)
            
            # 인덱스 생성
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cell_occupants_cell_id 
                ON runtime_data.cell_occupants(cell_id)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cell_occupants_entity_id 
                ON runtime_data.cell_occupants(entity_id)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cell_occupants_entered_at 
                ON runtime_data.cell_occupants(entered_at)
            """)
            
            print("✅ runtime_data.cell_occupants 테이블 생성 완료")
            
            # 테이블 존재 확인
            result = await conn.fetchval("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'runtime_data' 
                AND table_name = 'cell_occupants'
            """)
            
            if result > 0:
                print("✅ 테이블 생성 확인됨")
            else:
                print("❌ 테이블 생성 실패")
                
    except Exception as e:
        print(f"❌ 테이블 생성 실패: {str(e)}")
        raise
    finally:
        await db_connection.close()

if __name__ == "__main__":
    asyncio.run(create_missing_tables())
