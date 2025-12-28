"""
Effect Carrier 서비스
"""
from typing import List, Optional
from uuid import UUID
from database.connection import DatabaseConnection
from app.api.schemas import (
    EffectCarrierCreate, EffectCarrierUpdate, EffectCarrierResponse
)
from common.utils.logger import logger
from common.utils.jsonb_handler import serialize_jsonb_data, parse_jsonb_data


class EffectCarrierService:
    """Effect Carrier 서비스"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db = db_connection or DatabaseConnection()
    
    async def get_all_effect_carriers(self) -> List[EffectCarrierResponse]:
        """모든 Effect Carrier 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        effect_id, name, carrier_type, effect_json,
                        constraints_json, source_entity_id, tags,
                        created_at, updated_at
                    FROM game_data.effect_carriers
                    ORDER BY name
                """)
                
                carriers = []
                for row in rows:
                    effect_json = parse_jsonb_data(row['effect_json'])
                    constraints_json = parse_jsonb_data(row['constraints_json'])
                    tags = row['tags'] or []
                    
                    carriers.append(EffectCarrierResponse(
                        effect_id=row['effect_id'],
                        name=row['name'],
                        carrier_type=row['carrier_type'],
                        effect_json=effect_json or {},
                        constraints_json=constraints_json or {},
                        source_entity_id=row['source_entity_id'],
                        tags=tags,
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))
                
                return carriers
        except Exception as e:
            logger.error(f"Effect Carrier 전체 조회 실패: {e}")
            raise
    
    async def get_effect_carrier(self, effect_id: UUID) -> Optional[EffectCarrierResponse]:
        """특정 Effect Carrier 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT 
                        effect_id, name, carrier_type, effect_json,
                        constraints_json, source_entity_id, tags,
                        created_at, updated_at
                    FROM game_data.effect_carriers
                    WHERE effect_id = $1
                """, str(effect_id))
                
                if not row:
                    return None
                
                effect_json = parse_jsonb_data(row['effect_json'])
                constraints_json = parse_jsonb_data(row['constraints_json'])
                tags = row['tags'] or []
                
                return EffectCarrierResponse(
                    effect_id=row['effect_id'],
                    name=row['name'],
                    carrier_type=row['carrier_type'],
                    effect_json=effect_json or {},
                    constraints_json=constraints_json or {},
                    source_entity_id=row['source_entity_id'],
                    tags=tags,
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
        except Exception as e:
            logger.error(f"Effect Carrier 조회 실패: {e}")
            raise
    
    async def get_effect_carriers_by_entity(self, entity_id: str) -> List[EffectCarrierResponse]:
        """특정 Entity가 소유한 모든 Effect Carrier 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        effect_id, name, carrier_type, effect_json,
                        constraints_json, source_entity_id, tags,
                        created_at, updated_at
                    FROM game_data.effect_carriers
                    WHERE source_entity_id = $1
                    ORDER BY name
                """, entity_id)
                
                carriers = []
                for row in rows:
                    effect_json = parse_jsonb_data(row['effect_json'])
                    constraints_json = parse_jsonb_data(row['constraints_json'])
                    tags = row['tags'] or []
                    
                    carriers.append(EffectCarrierResponse(
                        effect_id=row['effect_id'],
                        name=row['name'],
                        carrier_type=row['carrier_type'],
                        effect_json=effect_json or {},
                        constraints_json=constraints_json or {},
                        source_entity_id=row['source_entity_id'],
                        tags=tags,
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))
                
                return carriers
        except Exception as e:
            logger.error(f"Entity별 Effect Carrier 조회 실패: {e}")
            raise
    
    async def get_effect_carriers_by_type(self, carrier_type: str) -> List[EffectCarrierResponse]:
        """특정 타입의 모든 Effect Carrier 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        effect_id, name, carrier_type, effect_json,
                        constraints_json, source_entity_id, tags,
                        created_at, updated_at
                    FROM game_data.effect_carriers
                    WHERE carrier_type = $1
                    ORDER BY name
                """, carrier_type)
                
                carriers = []
                for row in rows:
                    effect_json = parse_jsonb_data(row['effect_json'])
                    constraints_json = parse_jsonb_data(row['constraints_json'])
                    tags = row['tags'] or []
                    
                    carriers.append(EffectCarrierResponse(
                        effect_id=row['effect_id'],
                        name=row['name'],
                        carrier_type=row['carrier_type'],
                        effect_json=effect_json or {},
                        constraints_json=constraints_json or {},
                        source_entity_id=row['source_entity_id'],
                        tags=tags,
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))
                
                return carriers
        except Exception as e:
            logger.error(f"타입별 Effect Carrier 조회 실패: {e}")
            raise
    
    async def create_effect_carrier(self, carrier_data: EffectCarrierCreate) -> EffectCarrierResponse:
        """새 Effect Carrier 생성"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # Entity 존재 확인 (source_entity_id가 제공된 경우)
                if carrier_data.source_entity_id:
                    entity_row = await conn.fetchrow("""
                        SELECT entity_id FROM game_data.entities WHERE entity_id = $1
                    """, carrier_data.source_entity_id)
                    if not entity_row:
                        raise ValueError(f"Entity not found: {carrier_data.source_entity_id}")
                
                # carrier_type 검증
                valid_types = ['skill', 'buff', 'item', 'blessing', 'curse', 'ritual']
                if carrier_data.carrier_type not in valid_types:
                    raise ValueError(f"Invalid carrier_type. Must be one of: {valid_types}")
                
                # effect_json 검증 (비어있으면 안됨)
                if not carrier_data.effect_json:
                    raise ValueError("effect_json cannot be empty")
                
                import uuid
                effect_id = carrier_data.effect_id or uuid.uuid4()
                effect_json = serialize_jsonb_data(carrier_data.effect_json)
                constraints_json = serialize_jsonb_data(carrier_data.constraints_json)
                
                row = await conn.fetchrow("""
                    INSERT INTO game_data.effect_carriers (
                        effect_id, name, carrier_type, effect_json,
                        constraints_json, source_entity_id, tags
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    RETURNING 
                        effect_id, name, carrier_type, effect_json,
                        constraints_json, source_entity_id, tags,
                        created_at, updated_at
                """,
                    str(effect_id),
                    carrier_data.name,
                    carrier_data.carrier_type,
                    effect_json,
                    constraints_json,
                    carrier_data.source_entity_id,
                    carrier_data.tags
                )
                
                effect_json_parsed = parse_jsonb_data(row['effect_json'])
                constraints_json_parsed = parse_jsonb_data(row['constraints_json'])
                tags = row['tags'] or []
                
                return EffectCarrierResponse(
                    effect_id=row['effect_id'],
                    name=row['name'],
                    carrier_type=row['carrier_type'],
                    effect_json=effect_json_parsed or {},
                    constraints_json=constraints_json_parsed or {},
                    source_entity_id=row['source_entity_id'],
                    tags=tags,
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
        except Exception as e:
            logger.error(f"Effect Carrier 생성 실패: {e}")
            raise
    
    async def update_effect_carrier(self, effect_id: UUID, carrier_data: EffectCarrierUpdate) -> Optional[EffectCarrierResponse]:
        """Effect Carrier 정보 업데이트"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # 기존 Carrier 조회
                existing = await self.get_effect_carrier(effect_id)
                if not existing:
                    return None
                
                # Entity 존재 확인 (source_entity_id가 변경되는 경우)
                if carrier_data.source_entity_id and carrier_data.source_entity_id != existing.source_entity_id:
                    entity_row = await conn.fetchrow("""
                        SELECT entity_id FROM game_data.entities WHERE entity_id = $1
                    """, carrier_data.source_entity_id)
                    if not entity_row:
                        raise ValueError(f"Entity not found: {carrier_data.source_entity_id}")
                
                # carrier_type 검증 (변경되는 경우)
                if carrier_data.carrier_type:
                    valid_types = ['skill', 'buff', 'item', 'blessing', 'curse', 'ritual']
                    if carrier_data.carrier_type not in valid_types:
                        raise ValueError(f"Invalid carrier_type. Must be one of: {valid_types}")
                
                # effect_json 검증 (변경되는 경우)
                if carrier_data.effect_json is not None and not carrier_data.effect_json:
                    raise ValueError("effect_json cannot be empty")
                
                # 업데이트할 필드 구성
                update_fields = []
                update_values = []
                param_index = 1
                
                if carrier_data.name is not None:
                    update_fields.append(f"name = ${param_index}")
                    update_values.append(carrier_data.name)
                    param_index += 1
                
                if carrier_data.carrier_type is not None:
                    update_fields.append(f"carrier_type = ${param_index}")
                    update_values.append(carrier_data.carrier_type)
                    param_index += 1
                
                if carrier_data.effect_json is not None:
                    update_fields.append(f"effect_json = ${param_index}")
                    update_values.append(serialize_jsonb_data(carrier_data.effect_json))
                    param_index += 1
                
                if carrier_data.constraints_json is not None:
                    update_fields.append(f"constraints_json = ${param_index}")
                    update_values.append(serialize_jsonb_data(carrier_data.constraints_json))
                    param_index += 1
                
                if carrier_data.source_entity_id is not None:
                    update_fields.append(f"source_entity_id = ${param_index}")
                    update_values.append(carrier_data.source_entity_id)
                    param_index += 1
                
                if carrier_data.tags is not None:
                    update_fields.append(f"tags = ${param_index}")
                    update_values.append(carrier_data.tags)
                    param_index += 1
                
                if not update_fields:
                    return existing
                
                update_fields.append(f"updated_at = CURRENT_TIMESTAMP")
                update_values.append(str(effect_id))
                
                query = f"""
                    UPDATE game_data.effect_carriers
                    SET {', '.join(update_fields)}
                    WHERE effect_id = ${param_index}::uuid
                    RETURNING 
                        effect_id, name, carrier_type, effect_json,
                        constraints_json, source_entity_id, tags,
                        created_at, updated_at
                """
                
                row = await conn.fetchrow(query, *update_values)
                
                effect_json_parsed = parse_jsonb_data(row['effect_json'])
                constraints_json_parsed = parse_jsonb_data(row['constraints_json'])
                tags = row['tags'] or []
                
                return EffectCarrierResponse(
                    effect_id=row['effect_id'],
                    name=row['name'],
                    carrier_type=row['carrier_type'],
                    effect_json=effect_json_parsed or {},
                    constraints_json=constraints_json_parsed or {},
                    source_entity_id=row['source_entity_id'],
                    tags=tags,
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
        except Exception as e:
            logger.error(f"Effect Carrier 업데이트 실패: {e}")
            raise
    
    async def delete_effect_carrier(self, effect_id: UUID) -> bool:
        """Effect Carrier 삭제"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM game_data.effect_carriers
                    WHERE effect_id = $1
                """, str(effect_id))
                
                return result == "DELETE 1"
        except Exception as e:
            logger.error(f"Effect Carrier 삭제 실패: {e}")
            raise

