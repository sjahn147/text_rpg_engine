import asyncio
from database.connection import DatabaseConnection

async def check_cells():
    db = DatabaseConnection()
    pool = await db.pool
    async with pool.acquire() as conn:
        rows = await conn.fetch('SELECT cell_id FROM game_data.world_cells')
        print('Available cells:')
        for row in rows:
            print(f'  {row[0]}')

if __name__ == "__main__":
    asyncio.run(check_cells()) 