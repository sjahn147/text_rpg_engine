"""
위치 서비스
"""
from typing import List, Optional, Dict, Any, Union
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from app.api.schemas import (
    LocationCreate, LocationUpdate, LocationResponse, LocationResolvedResponse
)
from common.utils.logger import logger
from common.utils.jsonb_handler import serialize_jsonb_data, parse_jsonb_data


class LocationService:
    """위치 서비스"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db = db_connection or DatabaseConnection()
        self.game_data_repo = GameDataRepository(self.db)
    
    async def get_all_locations(self) -> List[LocationResponse]:
        """모든 위치 조회 (SSOT 준수: owner_name은 JOIN으로 해결)"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        l.location_id, l.region_id, l.location_name, l.location_description,
                        l.location_type, l.location_properties, l.created_at, l.updated_at,
                        e.entity_name as owner_name
                    FROM game_data.world_locations l
                    LEFT JOIN game_data.entities e ON (
                        e.entity_id = l.location_properties->'ownership'->>'owner_entity_id'
                    )
                    ORDER BY l.location_name
                """)
                
                locations = []
                for row in rows:
                    location_properties = parse_jsonb_data(row['location_properties'])
                    # SSOT 준수: location_properties에서 owner_name 제거 (있다면)
                    if location_properties and 'ownership' in location_properties:
                        ownership = location_properties.get('ownership', {})
                        if isinstance(ownership, dict) and 'owner_name' in ownership:
                            ownership = ownership.copy()
                            ownership.pop('owner_name', None)
                            location_properties = location_properties.copy()
                            location_properties['ownership'] = ownership
                    
                    locations.append(LocationResponse(
                        location_id=row['location_id'],
                        region_id=row['region_id'],
                        location_name=row['location_name'],
                        location_description=row['location_description'],
                        location_type=row['location_type'],
                        location_properties=location_properties or {},
                        created_at=row['created_at'],
                        updated_at=row['updated_at'],
                        owner_name=row['owner_name']  # JOIN으로 해결
                    ))
                
                return locations
        except Exception as e:
            logger.error(f"위치 조회 실패: {e}")
            raise
    
    async def get_location(self, location_id: str) -> Optional[LocationResponse]:
        """특정 위치 조회 (SSOT 준수: owner_name은 JOIN으로 해결)"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT 
                        l.location_id, l.region_id, l.location_name, l.location_description,
                        l.location_type, l.location_properties, l.created_at, l.updated_at,
                        e.entity_name as owner_name
                    FROM game_data.world_locations l
                    LEFT JOIN game_data.entities e ON (
                        e.entity_id = l.location_properties->'ownership'->>'owner_entity_id'
                    )
                    WHERE l.location_id = $1
                """, location_id)
                
                if not row:
                    return None
                
                location_properties = parse_jsonb_data(row['location_properties'])
                # SSOT 준수: location_properties에서 owner_name 제거 (있다면)
                if location_properties and 'ownership' in location_properties:
                    ownership = location_properties.get('ownership', {})
                    if isinstance(ownership, dict) and 'owner_name' in ownership:
                        ownership = ownership.copy()
                        ownership.pop('owner_name', None)
                        location_properties = location_properties.copy()
                        location_properties['ownership'] = ownership
                
                return LocationResponse(
                    location_id=row['location_id'],
                    region_id=row['region_id'],
                    location_name=row['location_name'],
                    location_description=row['location_description'],
                    location_type=row['location_type'],
                    location_properties=location_properties or {},
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    owner_name=row['owner_name']  # JOIN으로 해결
                )
        except Exception as e:
            logger.error(f"위치 조회 실패: {e}")
            raise
    
    async def get_locations_by_region(self, region_id: str) -> List[LocationResponse]:
        """특정 지역의 모든 위치 조회 (SSOT 준수: owner_name은 JOIN으로 해결)"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        l.location_id, l.region_id, l.location_name, l.location_description,
                        l.location_type, l.location_properties, l.created_at, l.updated_at,
                        e.entity_name as owner_name
                    FROM game_data.world_locations l
                    LEFT JOIN game_data.entities e ON (
                        e.entity_id = l.location_properties->'ownership'->>'owner_entity_id'
                    )
                    WHERE l.region_id = $1
                    ORDER BY l.location_name
                """, region_id)
                
                locations = []
                for row in rows:
                    location_properties = parse_jsonb_data(row['location_properties'])
                    # SSOT 준수: location_properties에서 owner_name 제거 (있다면)
                    if location_properties and 'ownership' in location_properties:
                        ownership = location_properties.get('ownership', {})
                        if isinstance(ownership, dict) and 'owner_name' in ownership:
                            ownership = ownership.copy()
                            ownership.pop('owner_name', None)
                            location_properties = location_properties.copy()
                            location_properties['ownership'] = ownership
                    
                    locations.append(LocationResponse(
                        location_id=row['location_id'],
                        region_id=row['region_id'],
                        location_name=row['location_name'],
                        location_description=row['location_description'],
                        location_type=row['location_type'],
                        location_properties=location_properties or {},
                        created_at=row['created_at'],
                        updated_at=row['updated_at'],
                        owner_name=row['owner_name']  # JOIN으로 해결
                    ))
                
                return locations
        except Exception as e:
            logger.error(f"지역별 위치 조회 실패: {e}")
            raise
    
    async def create_location(self, location_data: LocationCreate) -> LocationResponse:
        """새 위치 생성"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                location_properties_json = serialize_jsonb_data(location_data.location_properties)
                
                await conn.execute("""
                    INSERT INTO game_data.world_locations
                    (location_id, region_id, location_name, location_description, 
                     location_type, location_properties)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """,
                location_data.location_id,
                location_data.region_id,
                location_data.location_name,
                location_data.location_description,
                location_data.location_type,
                location_properties_json
                )
                
                return await self.get_location(location_data.location_id)
        except Exception as e:
            logger.error(f"위치 생성 실패: {e}")
            raise
    
    async def update_location(
        self, 
        location_id: str, 
        location_data: Union[LocationUpdate, Dict[str, Any]]
    ) -> LocationResponse:
        """위치 정보 업데이트"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                existing = await self.get_location(location_id)
                if not existing:
                    raise ValueError(f"위치를 찾을 수 없습니다: {location_id}")
                
                # Dict인 경우 LocationUpdate로 변환
                if isinstance(location_data, dict):
                    location_data = LocationUpdate(**location_data)
                
                update_fields = []
                values = []
                param_index = 1
                
                if location_data.region_id is not None:
                    update_fields.append(f"region_id = ${param_index}")
                    values.append(location_data.region_id)
                    param_index += 1
                
                if location_data.location_name is not None:
                    update_fields.append(f"location_name = ${param_index}")
                    values.append(location_data.location_name)
                    param_index += 1
                
                if location_data.location_description is not None:
                    update_fields.append(f"location_description = ${param_index}")
                    values.append(location_data.location_description)
                    param_index += 1
                
                if location_data.location_type is not None:
                    update_fields.append(f"location_type = ${param_index}")
                    values.append(location_data.location_type)
                    param_index += 1
                
                if location_data.location_properties is not None:
                    update_fields.append(f"location_properties = ${param_index}")
                    values.append(serialize_jsonb_data(location_data.location_properties))
                    param_index += 1
                
                if update_fields:
                    update_fields.append(f"updated_at = CURRENT_TIMESTAMP")
                    values.append(location_id)
                    
                    query = f"""
                        UPDATE game_data.world_locations
                        SET {', '.join(update_fields)}
                        WHERE location_id = ${param_index}
                    """
                    
                    await conn.execute(query, *values)
                
                return await self.get_location(location_id)
        except Exception as e:
            logger.error(f"위치 업데이트 실패: {e}")
            raise
    
    async def get_location_resolved(self, location_id: str) -> Optional[LocationResolvedResponse]:
        """모든 참조를 해결한 위치 조회 (Phase 4)"""
        try:
            location = await self.get_location(location_id)
            if not location:
                return None
            
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # owner_entity 정보 조회
                owner_entity = None
                if location.location_properties and location.location_properties.get('ownership', {}).get('owner_entity_id'):
                    owner_entity_id = location.location_properties['ownership']['owner_entity_id']
                    owner_row = await conn.fetchrow("""
                        SELECT entity_id, entity_type, entity_name, entity_description,
                               entity_status, base_stats, default_equipment, default_abilities,
                               default_inventory, entity_properties, default_position_3d, entity_size
                        FROM game_data.entities
                        WHERE entity_id = $1
                    """, owner_entity_id)
                    
                    if owner_row:
                        owner_entity = {
                            "entity_id": owner_row['entity_id'],
                            "entity_type": owner_row['entity_type'],
                            "entity_name": owner_row['entity_name'],
                            "entity_description": owner_row['entity_description'],
                            "entity_status": owner_row.get('entity_status', 'active'),
                            "base_stats": parse_jsonb_data(owner_row['base_stats']),
                            "default_equipment": parse_jsonb_data(owner_row['default_equipment']),
                            "default_abilities": parse_jsonb_data(owner_row['default_abilities']),
                            "default_inventory": parse_jsonb_data(owner_row['default_inventory']),
                            "entity_properties": parse_jsonb_data(owner_row['entity_properties']),
                            "default_position_3d": parse_jsonb_data(owner_row.get('default_position_3d')),
                            "entity_size": owner_row.get('entity_size')
                        }
                
                # quest_giver_entities 조회
                quest_giver_entities = []
                if location.location_properties and location.location_properties.get('quests', {}).get('quest_givers'):
                    quest_giver_ids = location.location_properties['quests']['quest_givers']
                    if isinstance(quest_giver_ids, list):
                        for quest_giver_id in quest_giver_ids:
                            quest_giver_row = await conn.fetchrow("""
                                SELECT entity_id, entity_type, entity_name, entity_description,
                                       entity_status, base_stats, default_equipment, default_abilities,
                                       default_inventory, entity_properties, default_position_3d, entity_size
                                FROM game_data.entities
                                WHERE entity_id = $1
                            """, quest_giver_id)
                            
                            if quest_giver_row:
                                quest_giver_entities.append({
                                    "entity_id": quest_giver_row['entity_id'],
                                    "entity_type": quest_giver_row['entity_type'],
                                    "entity_name": quest_giver_row['entity_name'],
                                    "entity_description": quest_giver_row['entity_description'],
                                    "entity_status": quest_giver_row.get('entity_status', 'active'),
                                    "base_stats": parse_jsonb_data(quest_giver_row['base_stats']),
                                    "default_equipment": parse_jsonb_data(quest_giver_row['default_equipment']),
                                    "default_abilities": parse_jsonb_data(quest_giver_row['default_abilities']),
                                    "default_inventory": parse_jsonb_data(quest_giver_row['default_inventory']),
                                    "entity_properties": parse_jsonb_data(quest_giver_row['entity_properties']),
                                    "default_position_3d": parse_jsonb_data(quest_giver_row.get('default_position_3d')),
                                    "entity_size": quest_giver_row.get('entity_size')
                                })
                
                # entry_point_cells 조회
                entry_point_cells = []
                if location.location_properties and location.location_properties.get('accessibility', {}).get('entry_points'):
                    entry_points = location.location_properties['accessibility']['entry_points']
                    if isinstance(entry_points, list):
                        for entry_point in entry_points:
                            if isinstance(entry_point, dict) and entry_point.get('cell_id'):
                                cell_id = entry_point['cell_id']
                                cell_row = await conn.fetchrow("""
                                    SELECT cell_id, location_id, cell_name, matrix_width, matrix_height,
                                           cell_description, cell_properties, cell_status, cell_type
                                    FROM game_data.world_cells
                                    WHERE cell_id = $1
                                """, cell_id)
                                
                                if cell_row:
                                    entry_point_cells.append({
                                        "cell_id": cell_row['cell_id'],
                                        "location_id": cell_row['location_id'],
                                        "cell_name": cell_row['cell_name'],
                                        "matrix_width": cell_row['matrix_width'],
                                        "matrix_height": cell_row['matrix_height'],
                                        "cell_description": cell_row['cell_description'],
                                        "cell_properties": parse_jsonb_data(cell_row['cell_properties']),
                                        "cell_status": cell_row.get('cell_status', 'active'),
                                        "cell_type": cell_row.get('cell_type', 'indoor'),
                                        "direction": entry_point.get('direction'),
                                        "entry_point_data": entry_point
                                    })
                
                return LocationResolvedResponse(
                    **location.model_dump(),
                    owner_entity=owner_entity,
                    quest_giver_entities=quest_giver_entities if quest_giver_entities else None,
                    entry_point_cells=entry_point_cells if entry_point_cells else None
                )
        except Exception as e:
            logger.error(f"해결된 위치 조회 실패: {e}")
            raise
    
    async def delete_location(self, location_id: str) -> bool:
        """위치 삭제"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM game_data.world_locations
                    WHERE location_id = $1
                """, location_id)
                
                return result == "DELETE 1"
        except Exception as e:
            logger.error(f"위치 삭제 실패: {e}")
            raise

