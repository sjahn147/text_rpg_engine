"""
게임 시작에 필요한 데이터 확인 스크립트
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from database.connection import DatabaseConnection


async def check_game_data():
    """게임 시작에 필요한 데이터 확인"""
    db = DatabaseConnection()
    await db.initialize()
    
    try:
        pool = await db.pool
        async with pool.acquire() as conn:
            # 셀 확인
            cell = await conn.fetchval(
                "SELECT cell_id FROM game_data.world_cells WHERE cell_id = 'CELL_INN_ROOM_001'"
            )
            print(f"✅ CELL_INN_ROOM_001: {cell}")
            
            if not cell:
                # 다른 셀 확인
                all_cells = await conn.fetch(
                    "SELECT cell_id, cell_name FROM game_data.world_cells LIMIT 5"
                )
                print(f"\n📋 사용 가능한 셀 목록:")
                for row in all_cells:
                    print(f"  - {row['cell_id']}: {row['cell_name']}")
            
            # 플레이어 엔티티 확인
            player_entity = await conn.fetchval(
                "SELECT entity_id FROM game_data.entities WHERE entity_type = 'player' LIMIT 1"
            )
            print(f"\n✅ Player entity: {player_entity}")
            
            if not player_entity:
                # 모든 엔티티 확인
                all_entities = await conn.fetch(
                    "SELECT entity_id, entity_name, entity_type FROM game_data.entities LIMIT 5"
                )
                print(f"\n📋 사용 가능한 엔티티 목록:")
                for row in all_entities:
                    print(f"  - {row['entity_id']}: {row['entity_name']} ({row['entity_type']})")
            
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(check_game_data())

