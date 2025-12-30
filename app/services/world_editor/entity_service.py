"""
엔티티(NPC) 서비스
"""
from typing import List, Optional, Dict, Any, Union
from database.connection import DatabaseConnection
from app.api.schemas import EntityCreate, EntityUpdate, EntityResponse
from common.utils.logger import logger
from common.utils.jsonb_handler import serialize_jsonb_data, parse_jsonb_data


class EntityService:
    """엔티티(NPC) 서비스"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db = db_connection or DatabaseConnection()
    
    async def get_all_entities(self) -> List[EntityResponse]:
        """모든 엔티티 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        entity_id, entity_type, entity_name, entity_description,
                        entity_status, base_stats, default_equipment, default_abilities,
                        default_inventory, entity_properties, 
                        default_position_3d, entity_size,
                        dialogue_context_id,
                        created_at, updated_at
                    FROM game_data.entities
                    ORDER BY entity_name
                """)
                
                entities = []
                for row in rows:
                    base_stats = parse_jsonb_data(row['base_stats'])
                    default_equipment = parse_jsonb_data(row['default_equipment'])
                    default_abilities = parse_jsonb_data(row['default_abilities'])
                    default_inventory = parse_jsonb_data(row['default_inventory'])
                    entity_properties = parse_jsonb_data(row['entity_properties'])
                    default_position_3d = parse_jsonb_data(row.get('default_position_3d'))
                    
                    entities.append(EntityResponse(
                        entity_id=row['entity_id'],
                        entity_type=row['entity_type'],
                        entity_name=row['entity_name'],
                        entity_description=row['entity_description'],
                        entity_status=row.get('entity_status', 'active'),
                        base_stats=base_stats or {},
                        default_equipment=default_equipment or {},
                        default_abilities=default_abilities or {},
                        default_inventory=default_inventory or {},
                        entity_properties=entity_properties or {},
                        default_position_3d=default_position_3d,
                        entity_size=row.get('entity_size'),
                        dialogue_context_id=row.get('dialogue_context_id'),
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))
                
                return entities
        except Exception as e:
            logger.error(f"모든 엔티티 조회 실패: {e}")
            raise
    
    async def get_entities_by_cell(self, cell_id: str) -> List[EntityResponse]:
        """특정 셀의 모든 엔티티 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        entity_id, entity_type, entity_name, entity_description,
                        entity_status, base_stats, default_equipment, default_abilities,
                        default_inventory, entity_properties, 
                        default_position_3d, entity_size,
                        dialogue_context_id,
                        created_at, updated_at
                    FROM game_data.entities
                    WHERE entity_properties->>'cell_id' = $1
                       AND entity_type = 'npc'
                    ORDER BY entity_name
                """, cell_id)
                
                entities = []
                for row in rows:
                    base_stats = parse_jsonb_data(row['base_stats'])
                    default_equipment = parse_jsonb_data(row['default_equipment'])
                    default_abilities = parse_jsonb_data(row['default_abilities'])
                    default_inventory = parse_jsonb_data(row['default_inventory'])
                    entity_properties = parse_jsonb_data(row['entity_properties'])
                    default_position_3d = parse_jsonb_data(row.get('default_position_3d'))
                    
                    entities.append(EntityResponse(
                        entity_id=row['entity_id'],
                        entity_type=row['entity_type'],
                        entity_name=row['entity_name'],
                        entity_description=row['entity_description'],
                        entity_status=row.get('entity_status', 'active'),
                        base_stats=base_stats or {},
                        default_equipment=default_equipment or {},
                        default_abilities=default_abilities or {},
                        default_inventory=default_inventory or {},
                        entity_properties=entity_properties or {},
                        default_position_3d=default_position_3d,
                        entity_size=row.get('entity_size'),
                        dialogue_context_id=row.get('dialogue_context_id'),
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))
                
                return entities
        except Exception as e:
            logger.error(f"셀별 엔티티 조회 실패: {e}")
            raise
    
    async def get_entities_by_location(self, location_id: str) -> List[EntityResponse]:
        """특정 위치의 모든 엔티티 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        entity_id, entity_type, entity_name, entity_description,
                        entity_status, base_stats, default_equipment, default_abilities,
                        default_inventory, entity_properties, created_at, updated_at
                    FROM game_data.entities
                    WHERE (entity_properties->>'location_id' = $1
                       OR entity_properties->>'current_location_id' = $1)
                       AND entity_type LIKE 'npc%'
                    ORDER BY entity_name
                """, location_id)
                
                entities = []
                for row in rows:
                    base_stats = parse_jsonb_data(row['base_stats'])
                    default_equipment = parse_jsonb_data(row['default_equipment'])
                    default_abilities = parse_jsonb_data(row['default_abilities'])
                    default_inventory = parse_jsonb_data(row['default_inventory'])
                    entity_properties = parse_jsonb_data(row['entity_properties'])
                    
                    entities.append(EntityResponse(
                        entity_id=row['entity_id'],
                        entity_type=row['entity_type'],
                        entity_name=row['entity_name'],
                        entity_description=row['entity_description'],
                        entity_status=row.get('entity_status', 'active'),
                        base_stats=base_stats or {},
                        default_equipment=default_equipment or {},
                        default_abilities=default_abilities or {},
                        default_inventory=default_inventory or {},
                        entity_properties=entity_properties or {},
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))
                
                return entities
        except Exception as e:
            logger.error(f"위치별 엔티티 조회 실패: {e}")
            raise
    
    async def get_entity(self, entity_id: str) -> Optional[EntityResponse]:
        """특정 엔티티 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT 
                        entity_id, entity_type, entity_name, entity_description,
                        entity_status, base_stats, default_equipment, default_abilities,
                        default_inventory, entity_properties, 
                        default_position_3d, entity_size,
                        dialogue_context_id,
                        created_at, updated_at
                    FROM game_data.entities
                    WHERE entity_id = $1
                """, entity_id)
                
                if not row:
                    return None
                
                base_stats = parse_jsonb_data(row['base_stats'])
                default_equipment = parse_jsonb_data(row['default_equipment'])
                default_abilities = parse_jsonb_data(row['default_abilities'])
                default_inventory = parse_jsonb_data(row['default_inventory'])
                entity_properties = parse_jsonb_data(row['entity_properties'])
                default_position_3d = parse_jsonb_data(row.get('default_position_3d'))
                
                return EntityResponse(
                    entity_id=row['entity_id'],
                    entity_type=row['entity_type'],
                    entity_name=row['entity_name'],
                    entity_description=row['entity_description'],
                    entity_status=row.get('entity_status', 'active'),
                    base_stats=base_stats or {},
                    default_equipment=default_equipment or {},
                    default_abilities=default_abilities or {},
                    default_inventory=default_inventory or {},
                    entity_properties=entity_properties or {},
                    default_position_3d=default_position_3d,
                    entity_size=row.get('entity_size'),
                    dialogue_context_id=row.get('dialogue_context_id'),
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
        except Exception as e:
            logger.error(f"엔티티 조회 실패: {e}")
            raise
    
    async def create_entity(self, entity_data: EntityCreate) -> EntityResponse:
        """새 엔티티 생성"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                base_stats_json = serialize_jsonb_data(entity_data.base_stats)
                default_equipment_json = serialize_jsonb_data(entity_data.default_equipment)
                default_abilities_json = serialize_jsonb_data(entity_data.default_abilities)
                default_inventory_json = serialize_jsonb_data(entity_data.default_inventory)
                entity_properties_json = serialize_jsonb_data(entity_data.entity_properties)
                
                await conn.execute("""
                    INSERT INTO game_data.entities
                    (entity_id, entity_type, entity_name, entity_description,
                     entity_status, base_stats, default_equipment, default_abilities,
                     default_inventory, entity_properties)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                entity_data.entity_id,
                entity_data.entity_type,
                entity_data.entity_name,
                entity_data.entity_description,
                entity_data.entity_status or 'active',
                base_stats_json,
                default_equipment_json,
                default_abilities_json,
                default_inventory_json,
                entity_properties_json
                )
                
                return await self.get_entity(entity_data.entity_id)
        except Exception as e:
            logger.error(f"엔티티 생성 실패: {e}")
            raise
    
    async def update_entity(
        self, 
        entity_id: str, 
        entity_data: Union[EntityUpdate, Dict[str, Any]]
    ) -> EntityResponse:
        """엔티티 정보 업데이트"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                existing = await self.get_entity(entity_id)
                if not existing:
                    raise ValueError(f"엔티티를 찾을 수 없습니다: {entity_id}")
                
                if isinstance(entity_data, dict):
                    entity_data = EntityUpdate(**entity_data)
                
                update_fields = []
                values = []
                param_index = 1
                
                if entity_data.entity_type is not None:
                    update_fields.append(f"entity_type = ${param_index}")
                    values.append(entity_data.entity_type)
                    param_index += 1
                
                if entity_data.entity_name is not None:
                    update_fields.append(f"entity_name = ${param_index}")
                    values.append(entity_data.entity_name)
                    param_index += 1
                
                if entity_data.entity_description is not None:
                    update_fields.append(f"entity_description = ${param_index}")
                    values.append(entity_data.entity_description)
                    param_index += 1
                
                if entity_data.entity_status is not None:
                    update_fields.append(f"entity_status = ${param_index}")
                    values.append(entity_data.entity_status)
                    param_index += 1
                
                if entity_data.base_stats is not None:
                    update_fields.append(f"base_stats = ${param_index}")
                    values.append(serialize_jsonb_data(entity_data.base_stats))
                    param_index += 1
                
                if entity_data.default_equipment is not None:
                    update_fields.append(f"default_equipment = ${param_index}")
                    values.append(serialize_jsonb_data(entity_data.default_equipment))
                    param_index += 1
                
                if entity_data.default_abilities is not None:
                    update_fields.append(f"default_abilities = ${param_index}")
                    values.append(serialize_jsonb_data(entity_data.default_abilities))
                    param_index += 1
                
                if entity_data.default_inventory is not None:
                    update_fields.append(f"default_inventory = ${param_index}")
                    values.append(serialize_jsonb_data(entity_data.default_inventory))
                    param_index += 1
                
                if entity_data.entity_properties is not None:
                    update_fields.append(f"entity_properties = ${param_index}")
                    values.append(serialize_jsonb_data(entity_data.entity_properties))
                    param_index += 1
                
                if entity_data.dialogue_context_id is not None:
                    update_fields.append(f"dialogue_context_id = ${param_index}")
                    values.append(entity_data.dialogue_context_id)
                    param_index += 1
                
                if update_fields:
                    update_fields.append(f"updated_at = CURRENT_TIMESTAMP")
                    values.append(entity_id)
                    
                    query = f"""
                        UPDATE game_data.entities
                        SET {', '.join(update_fields)}
                        WHERE entity_id = ${param_index}
                    """
                    
                    await conn.execute(query, *values)
                
                return await self.get_entity(entity_id)
        except Exception as e:
            logger.error(f"엔티티 업데이트 실패: {e}")
            raise
    
    async def validate_entity_references(self, entity_id: str) -> Dict[str, List[str]]:
        """
        엔티티가 참조되는 Location/Cell 목록 반환 (SSOT 참조 무결성 검증)
        
        Returns:
            {
                "locations_as_owner": ["LOC_001", ...],
                "cells_as_owner": ["CELL_001", ...],
                "locations_in_quest_givers": ["LOC_002", ...]
            }
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 1. Location의 owner로 참조되는 경우
            locations_as_owner = await conn.fetch("""
                SELECT location_id, location_name
                FROM game_data.world_locations
                WHERE location_properties->'ownership'->>'owner_entity_id' = $1
            """, entity_id)
            
            # 2. Cell의 owner로 참조되는 경우
            cells_as_owner = await conn.fetch("""
                SELECT cell_id, cell_name
                FROM game_data.world_cells
                WHERE cell_properties->'ownership'->>'owner_entity_id' = $1
            """, entity_id)
            
            # 3. Location의 quest_givers에 포함된 경우
            locations_in_quest_givers = await conn.fetch("""
                SELECT location_id, location_name
                FROM game_data.world_locations
                WHERE location_properties->'quests'->'quest_givers' @> $1::jsonb
            """, serialize_jsonb_data([entity_id]))
            
            return {
                "locations_as_owner": [row['location_id'] for row in locations_as_owner],
                "cells_as_owner": [row['cell_id'] for row in cells_as_owner],
                "locations_in_quest_givers": [row['location_id'] for row in locations_in_quest_givers]
            }
    
    async def delete_entity(self, entity_id: str) -> bool:
        """엔티티 삭제 (SSOT 참조 무결성 검증 포함)"""
        try:
            # 참조 검증
            references = await self.validate_entity_references(entity_id)
            
            conflicting_items = []
            if references["locations_as_owner"]:
                conflicting_items.append(f"Location owner: {', '.join(references['locations_as_owner'])}")
            if references["cells_as_owner"]:
                conflicting_items.append(f"Cell owner: {', '.join(references['cells_as_owner'])}")
            if references["locations_in_quest_givers"]:
                conflicting_items.append(f"Quest giver: {', '.join(references['locations_in_quest_givers'])}")
            
            if conflicting_items:
                raise ValueError(
                    f"엔티티 '{entity_id}'는 다음 위치에서 참조되고 있어 삭제할 수 없습니다:\n" +
                    "\n".join(conflicting_items) +
                    "\n\n참조를 먼저 제거한 후 삭제해주세요."
                )
            
            pool = await self.db.pool
            async with pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM game_data.entities
                    WHERE entity_id = $1
                """, entity_id)
                
                return result == "DELETE 1"
        except ValueError:
            # 참조 무결성 에러는 그대로 전파
            raise
        except Exception as e:
            logger.error(f"엔티티 삭제 실패: {e}")
            raise

