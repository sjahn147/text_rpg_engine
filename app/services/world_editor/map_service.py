"""
지도 메타데이터 서비스
"""
from typing import Optional, Dict, Any, Union
from database.connection import DatabaseConnection
from app.api.schemas import (
    MapMetadataCreate, MapMetadataUpdate, MapMetadataResponse
)
from common.utils.logger import logger


class MapService:
    """지도 메타데이터 서비스"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db = db_connection or DatabaseConnection()
    
    async def get_map(self, map_id: str = "default_map") -> Optional[MapMetadataResponse]:
        """지도 메타데이터 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT 
                        map_id, map_name, background_image, background_color,
                        width, height, grid_enabled, grid_size,
                        zoom_level, viewport_x, viewport_y,
                        created_at, updated_at
                    FROM game_data.map_metadata
                    WHERE map_id = $1
                """, map_id)
                
                if not row:
                    return None
                
                return MapMetadataResponse(
                    map_id=row['map_id'],
                    map_name=row['map_name'],
                    background_image=row['background_image'],
                    background_color=row['background_color'],
                    width=row['width'],
                    height=row['height'],
                    grid_enabled=row['grid_enabled'],
                    grid_size=row['grid_size'],
                    zoom_level=float(row['zoom_level']),
                    viewport_x=row['viewport_x'],
                    viewport_y=row['viewport_y'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
        except Exception as e:
            logger.error(f"지도 메타데이터 조회 실패: {e}")
            raise
    
    async def create_map(self, map_data: MapMetadataCreate) -> MapMetadataResponse:
        """새 지도 메타데이터 생성"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                map_id = map_data.map_id or "default_map"
                
                await conn.execute("""
                    INSERT INTO game_data.map_metadata
                    (map_id, map_name, background_image, background_color,
                     width, height, grid_enabled, grid_size,
                     zoom_level, viewport_x, viewport_y)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    ON CONFLICT (map_id) DO UPDATE SET
                        map_name = EXCLUDED.map_name,
                        background_image = EXCLUDED.background_image,
                        background_color = EXCLUDED.background_color,
                        width = EXCLUDED.width,
                        height = EXCLUDED.height,
                        grid_enabled = EXCLUDED.grid_enabled,
                        grid_size = EXCLUDED.grid_size,
                        zoom_level = EXCLUDED.zoom_level,
                        viewport_x = EXCLUDED.viewport_x,
                        viewport_y = EXCLUDED.viewport_y,
                        updated_at = CURRENT_TIMESTAMP
                """,
                map_id,
                map_data.map_name,
                map_data.background_image,
                map_data.background_color,
                map_data.width,
                map_data.height,
                map_data.grid_enabled,
                map_data.grid_size,
                map_data.zoom_level,
                map_data.viewport_x,
                map_data.viewport_y
                )
                
                return await self.get_map(map_id)
        except Exception as e:
            logger.error(f"지도 메타데이터 생성 실패: {e}")
            raise
    
    async def update_map(
        self, 
        map_id: str, 
        map_data: Union[MapMetadataUpdate, Dict[str, Any]]
    ) -> MapMetadataResponse:
        """지도 메타데이터 업데이트"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                existing = await self.get_map(map_id)
                if not existing:
                    raise ValueError(f"지도를 찾을 수 없습니다: {map_id}")
                
                # Dict인 경우 MapMetadataUpdate로 변환
                if isinstance(map_data, dict):
                    map_data = MapMetadataUpdate(**map_data)
                
                update_fields = []
                values = []
                param_index = 1
                
                if map_data.map_name is not None:
                    update_fields.append(f"map_name = ${param_index}")
                    values.append(map_data.map_name)
                    param_index += 1
                
                if map_data.background_image is not None:
                    update_fields.append(f"background_image = ${param_index}")
                    values.append(map_data.background_image)
                    param_index += 1
                
                if map_data.background_color is not None:
                    update_fields.append(f"background_color = ${param_index}")
                    values.append(map_data.background_color)
                    param_index += 1
                
                if map_data.width is not None:
                    update_fields.append(f"width = ${param_index}")
                    values.append(map_data.width)
                    param_index += 1
                
                if map_data.height is not None:
                    update_fields.append(f"height = ${param_index}")
                    values.append(map_data.height)
                    param_index += 1
                
                if map_data.grid_enabled is not None:
                    update_fields.append(f"grid_enabled = ${param_index}")
                    values.append(map_data.grid_enabled)
                    param_index += 1
                
                if map_data.grid_size is not None:
                    update_fields.append(f"grid_size = ${param_index}")
                    values.append(map_data.grid_size)
                    param_index += 1
                
                if map_data.zoom_level is not None:
                    update_fields.append(f"zoom_level = ${param_index}")
                    values.append(map_data.zoom_level)
                    param_index += 1
                
                if map_data.viewport_x is not None:
                    update_fields.append(f"viewport_x = ${param_index}")
                    values.append(map_data.viewport_x)
                    param_index += 1
                
                if map_data.viewport_y is not None:
                    update_fields.append(f"viewport_y = ${param_index}")
                    values.append(map_data.viewport_y)
                    param_index += 1
                
                if update_fields:
                    update_fields.append(f"updated_at = CURRENT_TIMESTAMP")
                    values.append(map_id)
                    
                    query = f"""
                        UPDATE game_data.map_metadata
                        SET {', '.join(update_fields)}
                        WHERE map_id = ${param_index}
                    """
                    
                    await conn.execute(query, *values)
                
                return await self.get_map(map_id)
        except Exception as e:
            logger.error(f"지도 메타데이터 업데이트 실패: {e}")
            raise

