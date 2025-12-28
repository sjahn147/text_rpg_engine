"""
World Object 서비스
"""
from typing import List, Optional
from database.connection import DatabaseConnection
from app.api.schemas import (
    WorldObjectCreate, WorldObjectUpdate, WorldObjectResponse
)
from common.utils.logger import logger
from common.utils.jsonb_handler import serialize_jsonb_data, parse_jsonb_data


class WorldObjectService:
    """World Object 서비스"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db = db_connection or DatabaseConnection()
    
    async def get_all_world_objects(self) -> List[WorldObjectResponse]:
        """모든 World Object 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        object_id, object_type, object_name, object_description,
                        default_cell_id, default_position, interaction_type,
                        possible_states, properties, created_at, updated_at
                    FROM game_data.world_objects
                    ORDER BY object_name
                """)
                
                objects = []
                for row in rows:
                    default_position = parse_jsonb_data(row['default_position'])
                    possible_states = parse_jsonb_data(row['possible_states'])
                    properties = parse_jsonb_data(row['properties'])
                    
                    # possible_states가 dict가 아닌 경우 빈 dict로 변환
                    if not isinstance(possible_states, dict):
                        possible_states = {}
                    
                    objects.append(WorldObjectResponse(
                        object_id=row['object_id'],
                        object_type=row['object_type'],
                        object_name=row['object_name'],
                        object_description=row['object_description'],
                        default_cell_id=row['default_cell_id'],
                        default_position=default_position or {},
                        interaction_type=row['interaction_type'],
                        possible_states=possible_states or {},
                        properties=properties or {},
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))
                
                return objects
        except Exception as e:
            logger.error(f"World Object 전체 조회 실패: {e}")
            raise
    
    async def get_world_object(self, object_id: str) -> Optional[WorldObjectResponse]:
        """특정 World Object 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT 
                        object_id, object_type, object_name, object_description,
                        default_cell_id, default_position, interaction_type,
                        possible_states, properties, created_at, updated_at
                    FROM game_data.world_objects
                    WHERE object_id = $1
                """, object_id)
                
                if not row:
                    return None
                
                default_position = parse_jsonb_data(row['default_position'])
                possible_states = parse_jsonb_data(row['possible_states'])
                properties = parse_jsonb_data(row['properties'])
                
                # possible_states가 dict가 아닌 경우 빈 dict로 변환
                if not isinstance(possible_states, dict):
                    possible_states = {}
                
                return WorldObjectResponse(
                    object_id=row['object_id'],
                    object_type=row['object_type'],
                    object_name=row['object_name'],
                    object_description=row['object_description'],
                    default_cell_id=row['default_cell_id'],
                    default_position=default_position or {},
                    interaction_type=row['interaction_type'],
                    possible_states=possible_states or {},
                    properties=properties or {},
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
        except Exception as e:
            logger.error(f"World Object 조회 실패: {e}")
            raise
    
    async def get_world_objects_by_cell(self, cell_id: str) -> List[WorldObjectResponse]:
        """특정 Cell의 모든 World Object 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        object_id, object_type, object_name, object_description,
                        default_cell_id, default_position, interaction_type,
                        possible_states, properties, created_at, updated_at
                    FROM game_data.world_objects
                    WHERE default_cell_id = $1
                    ORDER BY object_name
                """, cell_id)
                
                objects = []
                for row in rows:
                    default_position = parse_jsonb_data(row['default_position'])
                    possible_states = parse_jsonb_data(row['possible_states'])
                    properties = parse_jsonb_data(row['properties'])
                    
                    # possible_states가 dict가 아닌 경우 빈 dict로 변환
                    if not isinstance(possible_states, dict):
                        possible_states = {}
                    
                    objects.append(WorldObjectResponse(
                        object_id=row['object_id'],
                        object_type=row['object_type'],
                        object_name=row['object_name'],
                        object_description=row['object_description'],
                        default_cell_id=row['default_cell_id'],
                        default_position=default_position or {},
                        interaction_type=row['interaction_type'],
                        possible_states=possible_states or {},
                        properties=properties or {},
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))
                
                return objects
        except Exception as e:
            logger.error(f"Cell별 World Object 조회 실패: {e}")
            raise
    
    async def create_world_object(self, world_object_data: WorldObjectCreate) -> WorldObjectResponse:
        """새 World Object 생성"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # Cell 존재 확인 (default_cell_id가 제공된 경우)
                if world_object_data.default_cell_id:
                    cell_row = await conn.fetchrow("""
                        SELECT cell_id FROM game_data.world_cells WHERE cell_id = $1
                    """, world_object_data.default_cell_id)
                    if not cell_row:
                        raise ValueError(f"Cell not found: {world_object_data.default_cell_id}")
                
                # object_type 검증
                valid_types = ['static', 'interactive', 'trigger']
                if world_object_data.object_type not in valid_types:
                    raise ValueError(f"Invalid object_type. Must be one of: {valid_types}")
                
                default_position_json = serialize_jsonb_data(world_object_data.default_position)
                possible_states_json = serialize_jsonb_data(world_object_data.possible_states)
                properties_json = serialize_jsonb_data(world_object_data.properties)
                
                row = await conn.fetchrow("""
                    INSERT INTO game_data.world_objects (
                        object_id, object_type, object_name, object_description,
                        default_cell_id, default_position, interaction_type,
                        possible_states, properties
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    RETURNING 
                        object_id, object_type, object_name, object_description,
                        default_cell_id, default_position, interaction_type,
                        possible_states, properties, created_at, updated_at
                """,
                    world_object_data.object_id,
                    world_object_data.object_type,
                    world_object_data.object_name,
                    world_object_data.object_description,
                    world_object_data.default_cell_id,
                    default_position_json,
                    world_object_data.interaction_type,
                    possible_states_json,
                    properties_json
                )
                
                default_position = parse_jsonb_data(row['default_position'])
                possible_states = parse_jsonb_data(row['possible_states'])
                properties = parse_jsonb_data(row['properties'])
                
                # possible_states가 dict가 아닌 경우 빈 dict로 변환
                if not isinstance(possible_states, dict):
                    possible_states = {}
                
                return WorldObjectResponse(
                    object_id=row['object_id'],
                    object_type=row['object_type'],
                    object_name=row['object_name'],
                    object_description=row['object_description'],
                    default_cell_id=row['default_cell_id'],
                    default_position=default_position or {},
                    interaction_type=row['interaction_type'],
                    possible_states=possible_states or {},
                    properties=properties or {},
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
        except Exception as e:
            logger.error(f"World Object 생성 실패: {e}")
            raise
    
    async def update_world_object(self, object_id: str, world_object_data: WorldObjectUpdate) -> Optional[WorldObjectResponse]:
        """World Object 정보 업데이트"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # 기존 오브젝트 조회
                existing = await self.get_world_object(object_id)
                if not existing:
                    return None
                
                # Cell 존재 확인 (default_cell_id가 변경되는 경우)
                if world_object_data.default_cell_id and world_object_data.default_cell_id != existing.default_cell_id:
                    cell_row = await conn.fetchrow("""
                        SELECT cell_id FROM game_data.world_cells WHERE cell_id = $1
                    """, world_object_data.default_cell_id)
                    if not cell_row:
                        raise ValueError(f"Cell not found: {world_object_data.default_cell_id}")
                
                # object_type 검증 (변경되는 경우)
                if world_object_data.object_type:
                    valid_types = ['static', 'interactive', 'trigger']
                    if world_object_data.object_type not in valid_types:
                        raise ValueError(f"Invalid object_type. Must be one of: {valid_types}")
                
                # 업데이트할 필드 구성
                update_fields = []
                update_values = []
                param_index = 1
                
                if world_object_data.object_type is not None:
                    update_fields.append(f"object_type = ${param_index}")
                    update_values.append(world_object_data.object_type)
                    param_index += 1
                
                if world_object_data.object_name is not None:
                    update_fields.append(f"object_name = ${param_index}")
                    update_values.append(world_object_data.object_name)
                    param_index += 1
                
                if world_object_data.object_description is not None:
                    update_fields.append(f"object_description = ${param_index}")
                    update_values.append(world_object_data.object_description)
                    param_index += 1
                
                if world_object_data.default_cell_id is not None:
                    update_fields.append(f"default_cell_id = ${param_index}")
                    update_values.append(world_object_data.default_cell_id)
                    param_index += 1
                
                if world_object_data.default_position is not None:
                    update_fields.append(f"default_position = ${param_index}")
                    update_values.append(serialize_jsonb_data(world_object_data.default_position))
                    param_index += 1
                
                if world_object_data.interaction_type is not None:
                    update_fields.append(f"interaction_type = ${param_index}")
                    update_values.append(world_object_data.interaction_type)
                    param_index += 1
                
                if world_object_data.possible_states is not None:
                    update_fields.append(f"possible_states = ${param_index}")
                    update_values.append(serialize_jsonb_data(world_object_data.possible_states))
                    param_index += 1
                
                if world_object_data.properties is not None:
                    update_fields.append(f"properties = ${param_index}")
                    update_values.append(serialize_jsonb_data(world_object_data.properties))
                    param_index += 1
                
                if not update_fields:
                    return existing
                
                update_fields.append(f"updated_at = CURRENT_TIMESTAMP")
                update_values.append(object_id)
                
                query = f"""
                    UPDATE game_data.world_objects
                    SET {', '.join(update_fields)}
                    WHERE object_id = ${param_index}
                    RETURNING 
                        object_id, object_type, object_name, object_description,
                        default_cell_id, default_position, interaction_type,
                        possible_states, properties, created_at, updated_at
                """
                
                row = await conn.fetchrow(query, *update_values)
                
                default_position = parse_jsonb_data(row['default_position'])
                possible_states = parse_jsonb_data(row['possible_states'])
                properties = parse_jsonb_data(row['properties'])
                
                # possible_states가 dict가 아닌 경우 빈 dict로 변환
                if not isinstance(possible_states, dict):
                    possible_states = {}
                
                return WorldObjectResponse(
                    object_id=row['object_id'],
                    object_type=row['object_type'],
                    object_name=row['object_name'],
                    object_description=row['object_description'],
                    default_cell_id=row['default_cell_id'],
                    default_position=default_position or {},
                    interaction_type=row['interaction_type'],
                    possible_states=possible_states or {},
                    properties=properties or {},
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
        except Exception as e:
            logger.error(f"World Object 업데이트 실패: {e}")
            raise
    
    async def delete_world_object(self, object_id: str) -> bool:
        """World Object 삭제"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM game_data.world_objects
                    WHERE object_id = $1
                """, object_id)
                
                return result == "DELETE 1"
        except Exception as e:
            logger.error(f"World Object 삭제 실패: {e}")
            raise

