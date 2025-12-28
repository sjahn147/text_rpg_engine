"""
도로 서비스
"""
from typing import List, Optional, Dict, Any, Union
import json
import uuid

from database.connection import DatabaseConnection
from app.api.schemas import (
    RoadCreate, RoadUpdate, RoadResponse, PathPoint
)
from common.utils.logger import logger
from common.utils.jsonb_handler import serialize_jsonb_data, parse_jsonb_data


class RoadService:
    """도로 서비스"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db = db_connection or DatabaseConnection()
    
    async def get_all_roads(self) -> List[RoadResponse]:
        """모든 도로 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        road_id, from_region_id, from_location_id,
                        to_region_id, to_location_id, from_pin_id, to_pin_id,
                        road_type, distance, travel_time, danger_level,
                        color, width, dashed,
                        road_properties, path_coordinates,
                        created_at, updated_at
                    FROM game_data.world_roads
                    ORDER BY road_id
                """)
                
                roads = []
                for row in rows:
                    road_properties = parse_jsonb_data(row['road_properties'])
                    path_coords = parse_jsonb_data(row['path_coordinates']) or []
                    path_points = [PathPoint(x=p['x'], y=p['y']) for p in path_coords]
                    
                    roads.append(RoadResponse(
                        road_id=row['road_id'],
                        from_region_id=row['from_region_id'],
                        from_location_id=row['from_location_id'],
                        to_region_id=row['to_region_id'],
                        to_location_id=row['to_location_id'],
                        from_pin_id=row.get('from_pin_id'),
                        to_pin_id=row.get('to_pin_id'),
                        road_type=row['road_type'],
                        distance=float(row['distance']) if row['distance'] else None,
                        travel_time=row['travel_time'],
                        danger_level=row['danger_level'],
                        color=row.get('color', '#8B4513'),
                        width=row.get('width', 2),
                        dashed=row.get('dashed', False),
                        road_properties=road_properties or {},
                        path_coordinates=path_points,
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))
                
                return roads
        except Exception as e:
            logger.error(f"도로 조회 실패: {e}")
            raise
    
    async def get_road(self, road_id: str) -> Optional[RoadResponse]:
        """특정 도로 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT 
                        road_id, from_region_id, from_location_id,
                        to_region_id, to_location_id, from_pin_id, to_pin_id,
                        road_type, distance, travel_time, danger_level,
                        color, width, dashed,
                        road_properties, path_coordinates,
                        created_at, updated_at
                    FROM game_data.world_roads
                    WHERE road_id = $1
                """, road_id)
                
                if not row:
                    return None
                
                road_properties = parse_jsonb_data(row['road_properties'])
                path_coords = parse_jsonb_data(row['path_coordinates']) or []
                path_points = [PathPoint(x=p['x'], y=p['y']) for p in path_coords]
                
                return RoadResponse(
                    road_id=row['road_id'],
                    from_region_id=row['from_region_id'],
                    from_location_id=row['from_location_id'],
                    to_region_id=row['to_region_id'],
                    to_location_id=row['to_location_id'],
                    from_pin_id=row.get('from_pin_id'),
                    to_pin_id=row.get('to_pin_id'),
                    road_type=row['road_type'],
                    distance=float(row['distance']) if row['distance'] else None,
                    travel_time=row['travel_time'],
                    danger_level=row['danger_level'],
                    color=row.get('color', '#8B4513'),
                    width=row.get('width', 2),
                    dashed=row.get('dashed', False),
                    road_properties=road_properties or {},
                    path_coordinates=path_points,
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
        except Exception as e:
            logger.error(f"도로 조회 실패: {e}")
            raise
    
    async def create_road(self, road_data: RoadCreate) -> RoadResponse:
        """새 도로 생성"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # 핀 ID가 제공된 경우 우선 사용, 없으면 region_id/location_id 사용
                from_region_id = road_data.from_region_id
                from_location_id = road_data.from_location_id
                to_region_id = road_data.to_region_id
                to_location_id = road_data.to_location_id
                
                # 핀 ID로부터 region_id 또는 location_id 조회 (레거시 호환)
                if road_data.from_pin_id and not (from_region_id or from_location_id):
                    pin_info = await self._get_pin_info(conn, road_data.from_pin_id)
                    if pin_info:
                        if pin_info['pin_type'] == 'region':
                            from_region_id = pin_info['game_data_id']
                        elif pin_info['pin_type'] == 'location':
                            from_location_id = pin_info['game_data_id']
                
                if road_data.to_pin_id and not (to_region_id or to_location_id):
                    pin_info = await self._get_pin_info(conn, road_data.to_pin_id)
                    if pin_info:
                        if pin_info['pin_type'] == 'region':
                            to_region_id = pin_info['game_data_id']
                        elif pin_info['pin_type'] == 'location':
                            to_location_id = pin_info['game_data_id']
                
                road_id = road_data.road_id or f"ROAD_{uuid.uuid4().hex[:8].upper()}"
                road_properties_json = serialize_jsonb_data(road_data.road_properties or {})
                
                # path_coordinates 처리: PathPoint 객체 또는 dict 모두 처리
                if road_data.path_coordinates:
                    path_coords_list = []
                    for p in road_data.path_coordinates:
                        if isinstance(p, dict):
                            path_coords_list.append({"x": p.get("x", 0), "y": p.get("y", 0)})
                        else:
                            path_coords_list.append({"x": p.x, "y": p.y})
                    path_coords_json = json.dumps(path_coords_list)
                else:
                    path_coords_json = json.dumps([])
                
                await conn.execute("""
                    INSERT INTO game_data.world_roads
                    (road_id, from_region_id, from_location_id,
                     to_region_id, to_location_id, from_pin_id, to_pin_id,
                     road_type, distance, travel_time, danger_level,
                     color, width, dashed,
                     road_properties, path_coordinates)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                """,
                road_id,
                from_region_id,
                from_location_id,
                to_region_id,
                to_location_id,
                road_data.from_pin_id,
                road_data.to_pin_id,
                road_data.road_type,
                road_data.distance,
                road_data.travel_time,
                road_data.danger_level,
                road_data.color,
                road_data.width,
                road_data.dashed,
                road_properties_json,
                path_coords_json
                )
                
                return await self.get_road(road_id)
        except Exception as e:
            logger.error(f"도로 생성 실패: {e}")
            raise
    
    async def update_road(
        self, 
        road_id: str, 
        road_data: RoadUpdate
    ) -> RoadResponse:
        """도로 정보 업데이트"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                existing = await self.get_road(road_id)
                if not existing:
                    raise ValueError(f"도로를 찾을 수 없습니다: {road_id}")
                
                # Dict인 경우 RoadUpdate로 변환
                if isinstance(road_data, dict):
                    road_data = RoadUpdate(**road_data)
                
                update_fields = []
                values = []
                param_index = 1
                
                if road_data.from_pin_id is not None:
                    update_fields.append(f"from_pin_id = ${param_index}")
                    values.append(road_data.from_pin_id)
                    param_index += 1
                
                if road_data.to_pin_id is not None:
                    update_fields.append(f"to_pin_id = ${param_index}")
                    values.append(road_data.to_pin_id)
                    param_index += 1
                
                if road_data.road_type is not None:
                    update_fields.append(f"road_type = ${param_index}")
                    values.append(road_data.road_type)
                    param_index += 1
                
                if road_data.distance is not None:
                    update_fields.append(f"distance = ${param_index}")
                    values.append(road_data.distance)
                    param_index += 1
                
                if road_data.travel_time is not None:
                    update_fields.append(f"travel_time = ${param_index}")
                    values.append(road_data.travel_time)
                    param_index += 1
                
                if road_data.danger_level is not None:
                    update_fields.append(f"danger_level = ${param_index}")
                    values.append(road_data.danger_level)
                    param_index += 1
                
                if road_data.color is not None:
                    update_fields.append(f"color = ${param_index}")
                    values.append(road_data.color)
                    param_index += 1
                
                if road_data.width is not None:
                    update_fields.append(f"width = ${param_index}")
                    values.append(road_data.width)
                    param_index += 1
                
                if road_data.dashed is not None:
                    update_fields.append(f"dashed = ${param_index}")
                    values.append(road_data.dashed)
                    param_index += 1
                
                if road_data.road_properties is not None:
                    update_fields.append(f"road_properties = ${param_index}")
                    values.append(serialize_jsonb_data(road_data.road_properties))
                    param_index += 1
                
                if road_data.path_coordinates is not None:
                    update_fields.append(f"path_coordinates = ${param_index}")
                    path_coords_json = json.dumps([{"x": p.x, "y": p.y} for p in road_data.path_coordinates])
                    values.append(path_coords_json)
                    param_index += 1
                
                if update_fields:
                    update_fields.append(f"updated_at = CURRENT_TIMESTAMP")
                    values.append(road_id)
                    
                    query = f"""
                        UPDATE game_data.world_roads
                        SET {', '.join(update_fields)}
                        WHERE road_id = ${param_index}
                    """
                    
                    await conn.execute(query, *values)
                
                return await self.get_road(road_id)
        except Exception as e:
            logger.error(f"도로 업데이트 실패: {e}")
            raise
    
    async def delete_road(self, road_id: str) -> bool:
        """도로 삭제"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM game_data.world_roads
                    WHERE road_id = $1
                """, road_id)
                
                return result == "DELETE 1"
        except Exception as e:
            logger.error(f"도로 삭제 실패: {e}")
            raise
    
    async def _get_pin_info(self, conn, pin_id: str):
        """핀 정보 조회 (내부 헬퍼)"""
        row = await conn.fetchrow("""
            SELECT game_data_id, pin_type
            FROM game_data.pin_positions
            WHERE pin_id = $1
        """, pin_id)
        return dict(row) if row else None

