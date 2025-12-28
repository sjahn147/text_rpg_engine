"""
통합 검색 서비스
"""
from typing import List, Dict, Any
from database.connection import DatabaseConnection
from app.api.schemas import SearchResultItem, SearchResponse
from common.utils.logger import logger
from common.utils.jsonb_handler import parse_jsonb_data


class SearchService:
    """통합 검색 서비스"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection or DatabaseConnection()
    
    async def search(self, query: str, entity_types: List[str] = None) -> SearchResponse:
        """모든 엔티티 타입에서 검색"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                results: List[SearchResultItem] = []
                entity_type_counts: Dict[str, int] = {}
                
                search_pattern = f"%{query}%"
                
                # Regions 검색
                if not entity_types or 'region' in entity_types:
                    rows = await conn.fetch("""
                        SELECT region_id, region_name, region_description
                        FROM game_data.world_regions
                        WHERE region_name ILIKE $1 OR region_description ILIKE $1
                        LIMIT 100
                    """, search_pattern)
                    for row in rows:
                        results.append(SearchResultItem(
                            entity_type='region',
                            entity_id=row['region_id'],
                            name=row['region_name'],
                            description=row['region_description'],
                            metadata={'type': 'region'}
                        ))
                    entity_type_counts['region'] = len(rows)
                
                # Locations 검색
                if not entity_types or 'location' in entity_types:
                    rows = await conn.fetch("""
                        SELECT location_id, location_name, location_description
                        FROM game_data.world_locations
                        WHERE location_name ILIKE $1 OR location_description ILIKE $1
                        LIMIT 100
                    """, search_pattern)
                    for row in rows:
                        results.append(SearchResultItem(
                            entity_type='location',
                            entity_id=row['location_id'],
                            name=row['location_name'],
                            description=row['location_description'],
                            metadata={'type': 'location'}
                        ))
                    entity_type_counts['location'] = len(rows)
                
                # Cells 검색
                if not entity_types or 'cell' in entity_types:
                    rows = await conn.fetch("""
                        SELECT cell_id, cell_name, cell_description
                        FROM game_data.world_cells
                        WHERE cell_name ILIKE $1 OR cell_description ILIKE $1
                        LIMIT 100
                    """, search_pattern)
                    for row in rows:
                        results.append(SearchResultItem(
                            entity_type='cell',
                            entity_id=row['cell_id'],
                            name=row['cell_name'] or row['cell_id'],
                            description=row['cell_description'],
                            metadata={'type': 'cell'}
                        ))
                    entity_type_counts['cell'] = len(rows)
                
                # Entities 검색
                if not entity_types or 'entity' in entity_types:
                    rows = await conn.fetch("""
                        SELECT entity_id, entity_name, entity_description
                        FROM game_data.entities
                        WHERE entity_name ILIKE $1 OR entity_description ILIKE $1
                        LIMIT 100
                    """, search_pattern)
                    for row in rows:
                        results.append(SearchResultItem(
                            entity_type='entity',
                            entity_id=row['entity_id'],
                            name=row['entity_name'],
                            description=row['entity_description'],
                            metadata={'type': 'entity'}
                        ))
                    entity_type_counts['entity'] = len(rows)
                
                # World Objects 검색
                if not entity_types or 'world_object' in entity_types:
                    rows = await conn.fetch("""
                        SELECT object_id, object_name, object_description
                        FROM game_data.world_objects
                        WHERE object_name ILIKE $1 OR object_description ILIKE $1
                        LIMIT 100
                    """, search_pattern)
                    for row in rows:
                        results.append(SearchResultItem(
                            entity_type='world_object',
                            entity_id=row['object_id'],
                            name=row['object_name'],
                            description=row['object_description'],
                            metadata={'type': 'world_object'}
                        ))
                    entity_type_counts['world_object'] = len(rows)
                
                # Effect Carriers 검색
                if not entity_types or 'effect_carrier' in entity_types:
                    rows = await conn.fetch("""
                        SELECT effect_id, name, carrier_type
                        FROM game_data.effect_carriers
                        WHERE name ILIKE $1
                        LIMIT 100
                    """, search_pattern)
                    for row in rows:
                        results.append(SearchResultItem(
                            entity_type='effect_carrier',
                            entity_id=str(row['effect_id']),
                            name=row['name'],
                            description=None,
                            metadata={'type': 'effect_carrier', 'carrier_type': row['carrier_type']}
                        ))
                    entity_type_counts['effect_carrier'] = len(rows)
                
                # Items 검색
                if not entity_types or 'item' in entity_types:
                    rows = await conn.fetch("""
                        SELECT i.item_id, bp.name, bp.description, i.item_type
                        FROM game_data.items i
                        LEFT JOIN game_data.base_properties bp ON i.base_property_id = bp.property_id
                        WHERE bp.name ILIKE $1 OR bp.description ILIKE $1
                        LIMIT 100
                    """, search_pattern)
                    for row in rows:
                        results.append(SearchResultItem(
                            entity_type='item',
                            entity_id=row['item_id'],
                            name=row['name'] or row['item_id'],
                            description=row['description'],
                            metadata={'type': 'item', 'item_type': row['item_type']}
                        ))
                    entity_type_counts['item'] = len(rows)
                
                return SearchResponse(
                    query=query,
                    results=results,
                    total=len(results),
                    entity_type_counts=entity_type_counts
                )
        except Exception as e:
            logger.error(f"검색 실패: {e}")
            raise

