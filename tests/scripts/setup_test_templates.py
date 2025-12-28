#!/usr/bin/env python3
"""
테스트 템플릿 데이터 삽입 스크립트
database/setup/test_templates.sql의 내용을 Python으로 실행
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent))

from database.connection import DatabaseConnection
from common.utils.logger import logger


async def insert_test_templates():
    """테스트 템플릿 데이터 삽입"""
    db = DatabaseConnection()
    
    try:
        await db.initialize()
        logger.info("[OK] DB connection successful")
        
        pool = await db.pool
        async with pool.acquire() as conn:
            # SQL 파일 읽기
            sql_file = Path("database/setup/test_templates.sql")
            if not sql_file.exists():
                logger.error(f"[ERROR] SQL file not found: {sql_file}")
                return False
            
            sql_content = sql_file.read_text(encoding='utf-8')
            logger.info(f"[INFO] SQL file loaded: {len(sql_content)} characters")
            
            # SQL 실행 (전체를 하나의 트랜잭션으로)
            try:
                await conn.execute(sql_content)
                logger.info("[OK] Test templates inserted successfully")
                
                # 삽입된 데이터 확인
                entity_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM game_data.entities WHERE entity_id LIKE 'TEST_%' OR entity_id LIKE 'NPC_%'"
                )
                cell_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM game_data.world_cells WHERE cell_id LIKE 'CELL_%'"
                )
                
                logger.info(f"[STATS] Inserted data:")
                logger.info(f"   - Entities: {entity_count}")
                logger.info(f"   - Cells: {cell_count}")
                
                return True
                
            except Exception as e:
                logger.error(f"[ERROR] SQL execution failed: {e}")
                return False
        
    except Exception as e:
        logger.error(f"[ERROR] DB connection failed: {e}")
        return False
    
    finally:
        await db.close()
        logger.info("[OK] DB connection closed")


async def main():
    """메인 함수"""
    logger.info("=" * 60)
    logger.info("Test template data insertion started")
    logger.info("=" * 60)
    
    success = await insert_test_templates()
    
    logger.info("=" * 60)
    if success:
        logger.info("[SUCCESS] Test template data insertion completed!")
    else:
        logger.error("[FAILED] Test template data insertion failed")
    logger.info("=" * 60)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

