"""
기본값 테이블 생성 스크립트
"""
import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from database.connection import DatabaseConnection


async def create_default_values_table():
    """기본값 테이블 생성"""
    db = DatabaseConnection()
    
    try:
        # 테이블 생성
        await db.execute_query("""
            CREATE TABLE IF NOT EXISTS game_data.default_values (
                setting_id VARCHAR(50) PRIMARY KEY,
                category VARCHAR(50) NOT NULL,
                setting_name VARCHAR(100) NOT NULL,
                setting_value JSONB NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 인덱스 생성
        await db.execute_query("""
            CREATE INDEX IF NOT EXISTS idx_default_values_category 
            ON game_data.default_values(category);
        """)
        
        await db.execute_query("""
            CREATE INDEX IF NOT EXISTS idx_default_values_active 
            ON game_data.default_values(is_active);
        """)
        
        # 기본값 데이터 삽입
        default_values = [
            ('CELL_DEFAULT_SIZE', 'cell', 'default_size', 
             json.dumps({"width": 20, "height": 20}), '셀 기본 크기'),
            ('CELL_DEFAULT_STATUS', 'cell', 'default_status', 
             json.dumps("active"), '셀 기본 상태'),
            ('CELL_DEFAULT_TYPE', 'cell', 'default_type', 
             json.dumps("indoor"), '셀 기본 타입'),
            ('ENTITY_DEFAULT_POSITION', 'entity', 'default_position', 
             json.dumps({"x": 0.0, "y": 0.0}), '엔티티 기본 위치'),
            ('ENTITY_DEFAULT_STATUS', 'entity', 'default_status', 
             json.dumps("active"), '엔티티 기본 상태'),
            ('ENTITY_DEFAULT_TYPE', 'entity', 'default_type', 
             json.dumps("npc"), '엔티티 기본 타입'),
        ]
        
        for setting_id, category, setting_name, setting_value, description in default_values:
            await db.execute_query("""
                INSERT INTO game_data.default_values 
                (setting_id, category, setting_name, setting_value, description)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (setting_id) DO UPDATE SET
                setting_value = EXCLUDED.setting_value,
                updated_at = CURRENT_TIMESTAMP;
            """, setting_id, category, setting_name, setting_value, description)
        
        print("✅ 기본값 테이블이 성공적으로 생성되었습니다.")
        
    except Exception as e:
        print(f"❌ 기본값 테이블 생성 실패: {str(e)}")
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(create_default_values_table())
