"""
위치 기반 쿼리 서비스

Cell 내 Entity들의 위치 기반 조회 및 최적화된 쿼리 제공
"""
from typing import Dict, Any, List, Optional, Tuple
import math

from database.connection import DatabaseConnection


class PositionService:
    """위치 기반 쿼리 서비스"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    async def get_entities_by_cell(
        self,
        cell_id: str,
        sort_by_position: bool = True,
        area_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Cell 내 Entity 목록 조회 (위치 기반 정렬 및 필터링)
        
        Args:
            cell_id: 셀 ID
            sort_by_position: 위치로 정렬할지 여부 (기본값: True)
            area_filter: 영역 필터 (예: {"x_min": 0, "x_max": 10, "y_min": 0, "y_max": 10})
        
        Returns:
            Entity 목록 (위치 정보 포함)
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            query = """
                SELECT 
                    entity_id,
                    entity_name,
                    entity_type,
                    entity_size,
                    default_position_3d,
                    entity_properties
                FROM game_data.entities
                WHERE default_position_3d IS NOT NULL
                AND default_position_3d->>'cell_id' = $1
            """
            
            params = [cell_id]
            
            # 영역 필터 적용
            if area_filter:
                conditions = []
                if 'x_min' in area_filter:
                    conditions.append("(default_position_3d->>'x')::float >= $%d" % (len(params) + 1))
                    params.append(area_filter['x_min'])
                if 'x_max' in area_filter:
                    conditions.append("(default_position_3d->>'x')::float <= $%d" % (len(params) + 1))
                    params.append(area_filter['x_max'])
                if 'y_min' in area_filter:
                    conditions.append("(default_position_3d->>'y')::float >= $%d" % (len(params) + 1))
                    params.append(area_filter['y_min'])
                if 'y_max' in area_filter:
                    conditions.append("(default_position_3d->>'y')::float <= $%d" % (len(params) + 1))
                    params.append(area_filter['y_max'])
                if 'z_min' in area_filter:
                    conditions.append("(default_position_3d->>'z')::float >= $%d" % (len(params) + 1))
                    params.append(area_filter['z_min'])
                if 'z_max' in area_filter:
                    conditions.append("(default_position_3d->>'z')::float <= $%d" % (len(params) + 1))
                    params.append(area_filter['z_max'])
                
                if conditions:
                    query += " AND " + " AND ".join(conditions)
            
            # 위치로 정렬
            if sort_by_position:
                query += """
                    ORDER BY 
                        (default_position_3d->>'y')::float DESC,
                        (default_position_3d->>'x')::float ASC,
                        (default_position_3d->>'z')::float ASC
                """
            
            rows = await conn.fetch(query, *params)
            
            entities = []
            for row in rows:
                position = row['default_position_3d']
                # JSONB가 문자열로 반환될 수 있으므로 파싱
                if isinstance(position, str):
                    import json
                    position = json.loads(position)
                
                entities.append({
                    "entity_id": row['entity_id'],
                    "entity_name": row['entity_name'],
                    "entity_type": row['entity_type'],
                    "entity_size": row['entity_size'] or 'medium',
                    "position": position if isinstance(position, dict) else {},
                    "properties": row['entity_properties'] if isinstance(row['entity_properties'], dict) else {}
                })
            
            return entities
    
    async def get_entities_in_radius(
        self,
        cell_id: str,
        center_position: Dict[str, float],
        radius: float
    ) -> List[Dict[str, Any]]:
        """
        특정 위치 주변 반경 내 Entity 조회
        
        Args:
            cell_id: 셀 ID
            center_position: 중심 위치 {"x": 5.0, "y": 4.0, "z": 0.0}
            radius: 반경 (미터)
        
        Returns:
            반경 내 Entity 목록 (거리 정보 포함)
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 먼저 대략적인 영역 내 Entity 조회 (성능 최적화)
            area_filter = {
                'x_min': center_position.get('x', 0) - radius,
                'x_max': center_position.get('x', 0) + radius,
                'y_min': center_position.get('y', 0) - radius,
                'y_max': center_position.get('y', 0) + radius,
                'z_min': center_position.get('z', 0) - radius,
                'z_max': center_position.get('z', 0) + radius
            }
            
            entities = await self.get_entities_by_cell(
                cell_id,
                sort_by_position=False,
                area_filter=area_filter
            )
            
            # 정확한 거리 계산 및 필터링
            result = []
            for entity in entities:
                if not entity['position'] or 'x' not in entity['position']:
                    continue
                
                # 거리 계산
                dx = entity['position'].get('x', 0) - center_position.get('x', 0)
                dy = entity['position'].get('y', 0) - center_position.get('y', 0)
                dz = entity['position'].get('z', 0) - center_position.get('z', 0)
                distance = math.sqrt(dx*dx + dy*dy + dz*dz)
                
                if distance <= radius:
                    entity['distance'] = distance
                    result.append(entity)
            
            # 거리순 정렬
            result.sort(key=lambda x: x.get('distance', 0))
            
            return result
    
    async def get_world_objects_by_cell(
        self,
        cell_id: str,
        sort_by_position: bool = True,
        area_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Cell 내 World Object 목록 조회 (위치 기반 정렬 및 필터링)
        
        Args:
            cell_id: 셀 ID
            sort_by_position: 위치로 정렬할지 여부
            area_filter: 영역 필터
        
        Returns:
            World Object 목록 (위치 정보 포함)
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            query = """
                SELECT 
                    object_id,
                    object_name,
                    object_type,
                    default_position,
                    object_width,
                    object_depth,
                    object_height,
                    object_weight,
                    wall_mounted,
                    passable,
                    movable,
                    properties
                FROM game_data.world_objects
                WHERE default_cell_id = $1
                AND default_position IS NOT NULL
            """
            
            params = [cell_id]
            
            # 영역 필터 적용
            if area_filter:
                conditions = []
                if 'x_min' in area_filter:
                    conditions.append("(default_position->>'x')::float >= $%d" % (len(params) + 1))
                    params.append(area_filter['x_min'])
                if 'x_max' in area_filter:
                    conditions.append("(default_position->>'x')::float <= $%d" % (len(params) + 1))
                    params.append(area_filter['x_max'])
                if 'y_min' in area_filter:
                    conditions.append("(default_position->>'y')::float >= $%d" % (len(params) + 1))
                    params.append(area_filter['y_min'])
                if 'y_max' in area_filter:
                    conditions.append("(default_position->>'y')::float <= $%d" % (len(params) + 1))
                    params.append(area_filter['y_max'])
                
                if conditions:
                    query += " AND " + " AND ".join(conditions)
            
            # 위치로 정렬
            if sort_by_position:
                query += """
                    ORDER BY 
                        (default_position->>'y')::float DESC,
                        (default_position->>'x')::float ASC
                """
            
            rows = await conn.fetch(query, *params)
            
            objects = []
            for row in rows:
                position = row['default_position']
                # JSONB가 문자열로 반환될 수 있으므로 파싱
                if isinstance(position, str):
                    import json
                    position = json.loads(position)
                
                objects.append({
                    "object_id": row['object_id'],
                    "object_name": row['object_name'],
                    "object_type": row['object_type'],
                    "position": position if isinstance(position, dict) else {},
                    "object_width": row['object_width'] or 1.0,
                    "object_depth": row['object_depth'] or 1.0,
                    "object_height": row['object_height'] or 1.0,
                    "object_weight": row['object_weight'] or 0.0,
                    "wall_mounted": row['wall_mounted'] or False,
                    "passable": row['passable'] or False,
                    "movable": row['movable'] or False,
                    "properties": row['properties'] if isinstance(row['properties'], dict) else {}
                })
            
            return objects

