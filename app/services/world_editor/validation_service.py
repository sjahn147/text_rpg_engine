"""
데이터 검증 서비스
"""
from typing import Dict, Any, List
from database.connection import DatabaseConnection
from common.utils.logger import logger


class ValidationService:
    """데이터 검증 서비스"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection or DatabaseConnection()
    
    async def validate_all(self) -> Dict[str, List[str]]:
        """전체 데이터 검증"""
        issues = {
            'regions': [],
            'locations': [],
            'cells': [],
            'entities': [],
        }
        
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # Regions 검증
                rows = await conn.fetch("""
                    SELECT region_id, region_name, region_description
                    FROM game_data.world_regions
                """)
                for row in rows:
                    if not row['region_name'] or row['region_name'].strip() == '':
                        issues['regions'].append(f"지역 {row['region_id']}: 이름이 없습니다.")
                
                # Locations 검증
                rows = await conn.fetch("""
                    SELECT location_id, location_name, location_description, region_id
                    FROM game_data.world_locations
                """)
                for row in rows:
                    if not row['location_name'] or row['location_name'].strip() == '':
                        issues['locations'].append(f"위치 {row['location_id']}: 이름이 없습니다.")
                    if not row['region_id']:
                        issues['locations'].append(f"위치 {row['location_id']}: 지역 ID가 없습니다.")
                
                # Cells 검증
                rows = await conn.fetch("""
                    SELECT cell_id, cell_name, location_id
                    FROM game_data.world_cells
                """)
                for row in rows:
                    if not row['location_id']:
                        issues['cells'].append(f"셀 {row['cell_id']}: 위치 ID가 없습니다.")
                
                # Entities 검증
                rows = await conn.fetch("""
                    SELECT entity_id, entity_name, entity_description
                    FROM game_data.entities
                    WHERE entity_type = 'npc'
                """)
                for row in rows:
                    if not row['entity_name'] or row['entity_name'].strip() == '':
                        issues['entities'].append(f"인물 {row['entity_id']}: 이름이 없습니다.")
        
        except Exception as e:
            logger.error(f"검증 실패: {e}")
            raise
        
        return issues
    
    async def find_orphans(self) -> List[str]:
        """고아 엔티티 찾기"""
        orphans = []
        
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # 부모가 없는 Locations
                rows = await conn.fetch("""
                    SELECT l.location_id, l.region_id
                    FROM game_data.world_locations l
                    LEFT JOIN game_data.world_regions r ON l.region_id = r.region_id
                    WHERE l.region_id IS NOT NULL AND r.region_id IS NULL
                """)
                for row in rows:
                    orphans.append(f"위치 {row['location_id']}: 부모 지역 {row['region_id']}가 존재하지 않습니다.")
                
                # 부모가 없는 Cells
                rows = await conn.fetch("""
                    SELECT c.cell_id, c.location_id
                    FROM game_data.world_cells c
                    LEFT JOIN game_data.world_locations l ON c.location_id = l.location_id
                    WHERE c.location_id IS NOT NULL AND l.location_id IS NULL
                """)
                for row in rows:
                    orphans.append(f"셀 {row['cell_id']}: 부모 위치 {row['location_id']}가 존재하지 않습니다.")
        
        except Exception as e:
            logger.error(f"고아 엔티티 검색 실패: {e}")
            raise
        
        return orphans
    
    async def find_duplicates(self) -> List[str]:
        """중복 이름 찾기"""
        duplicates = []
        
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # 중복된 지역 이름
                rows = await conn.fetch("""
                    SELECT region_name, array_agg(region_id) as ids, count(*) as cnt
                    FROM game_data.world_regions
                    WHERE region_name IS NOT NULL AND region_name != ''
                    GROUP BY region_name
                    HAVING count(*) > 1
                """)
                for row in rows:
                    duplicates.append(f"지역 이름 \"{row['region_name']}\": {row['cnt']}개 중복 ({', '.join(row['ids'])})")
                
                # 중복된 위치 이름
                rows = await conn.fetch("""
                    SELECT location_name, array_agg(location_id) as ids, count(*) as cnt
                    FROM game_data.world_locations
                    WHERE location_name IS NOT NULL AND location_name != ''
                    GROUP BY location_name
                    HAVING count(*) > 1
                """)
                for row in rows:
                    duplicates.append(f"위치 이름 \"{row['location_name']}\": {row['cnt']}개 중복 ({', '.join(row['ids'])})")
        
        except Exception as e:
            logger.error(f"중복 검색 실패: {e}")
            raise
        
        return duplicates

