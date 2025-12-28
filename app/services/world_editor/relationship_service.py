"""
관계 조회 서비스
"""
from typing import List, Optional
from database.connection import DatabaseConnection
from app.api.schemas import RelationshipItem, RelationshipsResponse
from common.utils.logger import logger


class RelationshipService:
    """관계 조회 서비스"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection or DatabaseConnection()
    
    async def get_relationships(self, entity_type: str, entity_id: str) -> Optional[RelationshipsResponse]:
        """엔티티의 모든 관계 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                relationships: List[RelationshipItem] = []
                entity_name = None
                
                if entity_type == 'region':
                    # Region의 자식 Locations
                    region_row = await conn.fetchrow("""
                        SELECT region_id, region_name FROM game_data.world_regions WHERE region_id = $1
                    """, entity_id)
                    if not region_row:
                        return None
                    entity_name = region_row['region_name']
                    
                    location_rows = await conn.fetch("""
                        SELECT location_id, location_name
                        FROM game_data.world_locations
                        WHERE region_id = $1
                    """, entity_id)
                    for row in location_rows:
                        relationships.append(RelationshipItem(
                            entity_type='location',
                            entity_id=row['location_id'],
                            entity_name=row['location_name'],
                            relationship_type='child',
                            metadata={}
                        ))
                
                elif entity_type == 'location':
                    # Location의 부모 Region과 자식 Cells
                    location_row = await conn.fetchrow("""
                        SELECT location_id, location_name, region_id
                        FROM game_data.world_locations WHERE location_id = $1
                    """, entity_id)
                    if not location_row:
                        return None
                    entity_name = location_row['location_name']
                    
                    # 부모 Region
                    if location_row['region_id']:
                        region_row = await conn.fetchrow("""
                            SELECT region_id, region_name FROM game_data.world_regions WHERE region_id = $1
                        """, location_row['region_id'])
                        if region_row:
                            relationships.append(RelationshipItem(
                                entity_type='region',
                                entity_id=region_row['region_id'],
                                entity_name=region_row['region_name'],
                                relationship_type='parent',
                                metadata={}
                            ))
                    
                    # 자식 Cells
                    cell_rows = await conn.fetch("""
                        SELECT cell_id, cell_name
                        FROM game_data.world_cells
                        WHERE location_id = $1
                    """, entity_id)
                    for row in cell_rows:
                        relationships.append(RelationshipItem(
                            entity_type='cell',
                            entity_id=row['cell_id'],
                            entity_name=row['cell_name'] or row['cell_id'],
                            relationship_type='child',
                            metadata={}
                        ))
                
                elif entity_type == 'cell':
                    # Cell의 부모 Location, 자식 Entities와 World Objects
                    cell_row = await conn.fetchrow("""
                        SELECT cell_id, cell_name, location_id
                        FROM game_data.world_cells WHERE cell_id = $1
                    """, entity_id)
                    if not cell_row:
                        return None
                    entity_name = cell_row['cell_name'] or cell_row['cell_id']
                    
                    # 부모 Location
                    if cell_row['location_id']:
                        location_row = await conn.fetchrow("""
                            SELECT location_id, location_name FROM game_data.world_locations WHERE location_id = $1
                        """, cell_row['location_id'])
                        if location_row:
                            relationships.append(RelationshipItem(
                                entity_type='location',
                                entity_id=location_row['location_id'],
                                entity_name=location_row['location_name'],
                                relationship_type='parent',
                                metadata={}
                            ))
                    
                    # 자식 Entities
                    entity_rows = await conn.fetch("""
                        SELECT entity_id, entity_name
                        FROM game_data.entities
                        WHERE entity_properties->>'cell_id' = $1
                    """, entity_id)
                    for row in entity_rows:
                        relationships.append(RelationshipItem(
                            entity_type='entity',
                            entity_id=row['entity_id'],
                            entity_name=row['entity_name'],
                            relationship_type='child',
                            metadata={'relationship': 'located_in'}
                        ))
                    
                    # 자식 World Objects
                    object_rows = await conn.fetch("""
                        SELECT object_id, object_name
                        FROM game_data.world_objects
                        WHERE default_cell_id = $1
                    """, entity_id)
                    for row in object_rows:
                        relationships.append(RelationshipItem(
                            entity_type='world_object',
                            entity_id=row['object_id'],
                            entity_name=row['object_name'],
                            relationship_type='child',
                            metadata={'relationship': 'located_in'}
                        ))
                
                elif entity_type == 'entity':
                    # Entity의 소유 Cell, 소유 Effect Carriers
                    entity_row = await conn.fetchrow("""
                        SELECT entity_id, entity_name, entity_properties
                        FROM game_data.entities WHERE entity_id = $1
                    """, entity_id)
                    if not entity_row:
                        return None
                    entity_name = entity_row['entity_name']
                    
                    # 소유 Cell
                    cell_id = entity_row['entity_properties'].get('cell_id') if entity_row['entity_properties'] else None
                    if cell_id:
                        cell_row = await conn.fetchrow("""
                            SELECT cell_id, cell_name FROM game_data.world_cells WHERE cell_id = $1
                        """, cell_id)
                        if cell_row:
                            relationships.append(RelationshipItem(
                                entity_type='cell',
                                entity_id=cell_row['cell_id'],
                                entity_name=cell_row['cell_name'] or cell_row['cell_id'],
                                relationship_type='parent',
                                metadata={'relationship': 'located_in'}
                            ))
                    
                    # 소유 Effect Carriers
                    effect_rows = await conn.fetch("""
                        SELECT effect_id, name, carrier_type
                        FROM game_data.effect_carriers
                        WHERE source_entity_id = $1
                    """, entity_id)
                    for row in effect_rows:
                        relationships.append(RelationshipItem(
                            entity_type='effect_carrier',
                            entity_id=str(row['effect_id']),
                            entity_name=row['name'],
                            relationship_type='child',
                            metadata={'relationship': 'owns', 'carrier_type': row['carrier_type']}
                        ))
                
                elif entity_type == 'world_object':
                    # World Object의 소유 Cell
                    object_row = await conn.fetchrow("""
                        SELECT object_id, object_name, default_cell_id
                        FROM game_data.world_objects WHERE object_id = $1
                    """, entity_id)
                    if not object_row:
                        return None
                    entity_name = object_row['object_name']
                    
                    if object_row['default_cell_id']:
                        cell_row = await conn.fetchrow("""
                            SELECT cell_id, cell_name FROM game_data.world_cells WHERE cell_id = $1
                        """, object_row['default_cell_id'])
                        if cell_row:
                            relationships.append(RelationshipItem(
                                entity_type='cell',
                                entity_id=cell_row['cell_id'],
                                entity_name=cell_row['cell_name'] or cell_row['cell_id'],
                                relationship_type='parent',
                                metadata={'relationship': 'located_in'}
                            ))
                
                elif entity_type == 'effect_carrier':
                    # Effect Carrier의 소유 Entity
                    effect_row = await conn.fetchrow("""
                        SELECT effect_id, name, source_entity_id
                        FROM game_data.effect_carriers WHERE effect_id = $1::uuid
                    """, entity_id)
                    if not effect_row:
                        return None
                    entity_name = effect_row['name']
                    
                    if effect_row['source_entity_id']:
                        entity_row = await conn.fetchrow("""
                            SELECT entity_id, entity_name FROM game_data.entities WHERE entity_id = $1
                        """, effect_row['source_entity_id'])
                        if entity_row:
                            relationships.append(RelationshipItem(
                                entity_type='entity',
                                entity_id=entity_row['entity_id'],
                                entity_name=entity_row['entity_name'],
                                relationship_type='parent',
                                metadata={'relationship': 'owned_by'}
                            ))
                
                else:
                    return None
                
                return RelationshipsResponse(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    entity_name=entity_name or entity_id,
                    relationships=relationships
                )
        except Exception as e:
            logger.error(f"관계 조회 실패: {e}")
            raise

