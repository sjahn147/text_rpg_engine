"""
Item 서비스
"""
from typing import List, Optional
from database.connection import DatabaseConnection
from app.api.schemas import (
    ItemCreate, ItemUpdate, ItemResponse
)
from common.utils.logger import logger
from common.utils.jsonb_handler import serialize_jsonb_data, parse_jsonb_data


class ItemService:
    """Item 서비스"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db = db_connection or DatabaseConnection()
    
    async def get_all_items(self) -> List[ItemResponse]:
        """모든 Item 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        i.item_id, i.base_property_id, i.item_type, i.stack_size,
                        i.consumable, i.item_properties, i.created_at, i.updated_at,
                        bp.name as base_property_name, bp.description as base_property_description
                    FROM game_data.items i
                    LEFT JOIN game_data.base_properties bp ON i.base_property_id = bp.property_id
                    ORDER BY i.item_id
                """)
                
                items = []
                for row in rows:
                    item_properties = parse_jsonb_data(row['item_properties'])
                    
                    items.append(ItemResponse(
                        item_id=row['item_id'],
                        base_property_id=row['base_property_id'],
                        item_type=row['item_type'],
                        stack_size=row['stack_size'],
                        consumable=row['consumable'],
                        item_properties=item_properties or {},
                        base_property_name=row['base_property_name'],
                        base_property_description=row['base_property_description'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))
                
                return items
        except Exception as e:
            logger.error(f"Item 전체 조회 실패: {e}")
            raise
    
    async def get_item(self, item_id: str) -> Optional[ItemResponse]:
        """특정 Item 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT 
                        i.item_id, i.base_property_id, i.item_type, i.stack_size,
                        i.consumable, i.item_properties, i.created_at, i.updated_at,
                        bp.name as base_property_name, bp.description as base_property_description
                    FROM game_data.items i
                    LEFT JOIN game_data.base_properties bp ON i.base_property_id = bp.property_id
                    WHERE i.item_id = $1
                """, item_id)
                
                if not row:
                    return None
                
                item_properties = parse_jsonb_data(row['item_properties'])
                
                return ItemResponse(
                    item_id=row['item_id'],
                    base_property_id=row['base_property_id'],
                    item_type=row['item_type'],
                    stack_size=row['stack_size'],
                    consumable=row['consumable'],
                    item_properties=item_properties or {},
                    base_property_name=row['base_property_name'],
                    base_property_description=row['base_property_description'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
        except Exception as e:
            logger.error(f"Item 조회 실패: {e}")
            raise
    
    async def get_items_by_type(self, item_type: str) -> List[ItemResponse]:
        """특정 타입의 모든 Item 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        i.item_id, i.base_property_id, i.item_type, i.stack_size,
                        i.consumable, i.item_properties, i.created_at, i.updated_at,
                        bp.name as base_property_name, bp.description as base_property_description
                    FROM game_data.items i
                    LEFT JOIN game_data.base_properties bp ON i.base_property_id = bp.property_id
                    WHERE i.item_type = $1
                    ORDER BY i.item_id
                """, item_type)
                
                items = []
                for row in rows:
                    item_properties = parse_jsonb_data(row['item_properties'])
                    
                    items.append(ItemResponse(
                        item_id=row['item_id'],
                        base_property_id=row['base_property_id'],
                        item_type=row['item_type'],
                        stack_size=row['stack_size'],
                        consumable=row['consumable'],
                        item_properties=item_properties or {},
                        base_property_name=row['base_property_name'],
                        base_property_description=row['base_property_description'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))
                
                return items
        except Exception as e:
            logger.error(f"타입별 Item 조회 실패: {e}")
            raise
    
    async def create_item(self, item_data: ItemCreate) -> ItemResponse:
        """새 Item 생성"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # base_property_id 존재 확인
                prop_row = await conn.fetchrow("""
                    SELECT property_id FROM game_data.base_properties WHERE property_id = $1
                """, item_data.base_property_id)
                if not prop_row:
                    raise ValueError(f"Base property not found: {item_data.base_property_id}")
                
                item_properties_json = serialize_jsonb_data(item_data.item_properties)
                
                row = await conn.fetchrow("""
                    INSERT INTO game_data.items (
                        item_id, base_property_id, item_type, stack_size,
                        consumable, item_properties
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING 
                        item_id, base_property_id, item_type, stack_size,
                        consumable, item_properties, created_at, updated_at
                """,
                    item_data.item_id,
                    item_data.base_property_id,
                    item_data.item_type,
                    item_data.stack_size,
                    item_data.consumable,
                    item_properties_json
                )
                
                # base_property 정보 조회
                bp_row = await conn.fetchrow("""
                    SELECT name, description FROM game_data.base_properties WHERE property_id = $1
                """, item_data.base_property_id)
                
                item_properties = parse_jsonb_data(row['item_properties'])
                
                return ItemResponse(
                    item_id=row['item_id'],
                    base_property_id=row['base_property_id'],
                    item_type=row['item_type'],
                    stack_size=row['stack_size'],
                    consumable=row['consumable'],
                    item_properties=item_properties or {},
                    base_property_name=bp_row['name'] if bp_row else None,
                    base_property_description=bp_row['description'] if bp_row else None,
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
        except Exception as e:
            logger.error(f"Item 생성 실패: {e}")
            raise
    
    async def update_item(self, item_id: str, item_data: ItemUpdate) -> Optional[ItemResponse]:
        """Item 정보 업데이트"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # 기존 Item 조회
                existing = await self.get_item(item_id)
                if not existing:
                    return None
                
                # base_property_id 존재 확인 (변경되는 경우)
                if item_data.base_property_id and item_data.base_property_id != existing.base_property_id:
                    prop_row = await conn.fetchrow("""
                        SELECT property_id FROM game_data.base_properties WHERE property_id = $1
                    """, item_data.base_property_id)
                    if not prop_row:
                        raise ValueError(f"Base property not found: {item_data.base_property_id}")
                
                # 업데이트할 필드 구성
                update_fields = []
                update_values = []
                param_index = 1
                
                if item_data.base_property_id is not None:
                    update_fields.append(f"base_property_id = ${param_index}")
                    update_values.append(item_data.base_property_id)
                    param_index += 1
                
                if item_data.item_type is not None:
                    update_fields.append(f"item_type = ${param_index}")
                    update_values.append(item_data.item_type)
                    param_index += 1
                
                if item_data.stack_size is not None:
                    update_fields.append(f"stack_size = ${param_index}")
                    update_values.append(item_data.stack_size)
                    param_index += 1
                
                if item_data.consumable is not None:
                    update_fields.append(f"consumable = ${param_index}")
                    update_values.append(item_data.consumable)
                    param_index += 1
                
                if item_data.item_properties is not None:
                    update_fields.append(f"item_properties = ${param_index}")
                    update_values.append(serialize_jsonb_data(item_data.item_properties))
                    param_index += 1
                
                if not update_fields:
                    return existing
                
                update_fields.append(f"updated_at = CURRENT_TIMESTAMP")
                update_values.append(item_id)
                
                query = f"""
                    UPDATE game_data.items
                    SET {', '.join(update_fields)}
                    WHERE item_id = ${param_index}
                    RETURNING 
                        item_id, base_property_id, item_type, stack_size,
                        consumable, item_properties, created_at, updated_at
                """
                
                row = await conn.fetchrow(query, *update_values)
                
                # base_property 정보 조회
                bp_row = await conn.fetchrow("""
                    SELECT name, description FROM game_data.base_properties WHERE property_id = $1
                """, row['base_property_id'])
                
                item_properties = parse_jsonb_data(row['item_properties'])
                
                return ItemResponse(
                    item_id=row['item_id'],
                    base_property_id=row['base_property_id'],
                    item_type=row['item_type'],
                    stack_size=row['stack_size'],
                    consumable=row['consumable'],
                    item_properties=item_properties or {},
                    base_property_name=bp_row['name'] if bp_row else None,
                    base_property_description=bp_row['description'] if bp_row else None,
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
        except Exception as e:
            logger.error(f"Item 업데이트 실패: {e}")
            raise
    
    async def delete_item(self, item_id: str) -> bool:
        """Item 삭제"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM game_data.items
                    WHERE item_id = $1
                """, item_id)
                
                return result == "DELETE 1"
        except Exception as e:
            logger.error(f"Item 삭제 실패: {e}")
            raise

