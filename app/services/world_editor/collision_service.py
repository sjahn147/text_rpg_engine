"""
Entity 위치 충돌 검사 서비스

Cell 내 Entity들의 위치 충돌을 검사하는 서비스
"""
from typing import Dict, Any, List, Optional
import math
from enum import Enum

from database.connection import DatabaseConnection


class EntitySize(str, Enum):
    """Entity 크기 (D&D 5e 스타일)"""
    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HUGE = "huge"
    GARGANTUAN = "gargantuan"


# 크기별 충돌 반경 정의 (미터 단위)
SIZE_COLLISION_RADIUS = {
    EntitySize.TINY: 0.25,      # 0.5x0.5 공간
    EntitySize.SMALL: 0.5,      # 1x1 공간
    EntitySize.MEDIUM: 0.5,     # 1x1 공간 (기본)
    EntitySize.LARGE: 1.0,      # 2x2 공간
    EntitySize.HUGE: 1.5,       # 3x3 공간
    EntitySize.GARGANTUAN: 2.0  # 4x4 이상 공간
}


def get_collision_radius(entity_size: str) -> float:
    """
    Entity 크기에 따른 충돌 반경 반환
    
    Args:
        entity_size: Entity 크기 ('tiny', 'small', 'medium', 'large', 'huge', 'gargantuan')
    
    Returns:
        충돌 반경 (미터)
    """
    try:
        size_enum = EntitySize(entity_size)
        return SIZE_COLLISION_RADIUS.get(size_enum, 0.5)
    except ValueError:
        # 유효하지 않은 크기인 경우 기본값 반환
        return 0.5


def calculate_distance(pos1: Dict[str, float], pos2: Dict[str, float]) -> float:
    """
    두 위치 간의 3D 거리 계산
    
    Args:
        pos1: 첫 번째 위치 {"x": 5.0, "y": 4.0, "z": 0.0}
        pos2: 두 번째 위치 {"x": 5.5, "y": 4.0, "z": 0.0}
    
    Returns:
        거리 (미터)
    """
    dx = pos1.get('x', 0.0) - pos2.get('x', 0.0)
    dy = pos1.get('y', 0.0) - pos2.get('y', 0.0)
    dz = pos1.get('z', 0.0) - pos2.get('z', 0.0)
    return math.sqrt(dx*dx + dy*dy + dz*dz)


def check_collision(
    position1: Dict[str, float],
    size1: str,
    position2: Dict[str, float],
    size2: str
) -> bool:
    """
    두 위치가 충돌하는지 확인 (크기 고려)
    
    Args:
        position1: 첫 번째 위치 {"x": 5.0, "y": 4.0, "z": 0.0}
        size1: 첫 번째 Entity 크기
        position2: 두 번째 위치 {"x": 5.5, "y": 4.0, "z": 0.0}
        size2: 두 번째 Entity 크기
    
    Returns:
        True: 충돌, False: 충돌 없음
    """
    # 거리 계산
    distance = calculate_distance(position1, position2)
    
    # 각 Entity의 충돌 반경
    radius1 = get_collision_radius(size1)
    radius2 = get_collision_radius(size2)
    
    # 두 충돌 반경의 합이 거리보다 크면 충돌
    return distance < (radius1 + radius2)


class CollisionService:
    """Entity 위치 충돌 검사 서비스"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    async def check_position_collision(
        self,
        cell_id: str,
        position: Dict[str, float],
        entity_size: str = 'medium',
        exclude_entity_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cell 내 특정 위치에 다른 Entity가 있는지 확인 (크기 고려)
        
        Args:
            cell_id: 셀 ID
            position: 확인할 위치 {"x": 5.0, "y": 4.0, "z": 0.0}
            entity_size: 엔티티 크기 ('tiny', 'small', 'medium', 'large', 'huge', 'gargantuan')
            exclude_entity_id: 제외할 엔티티 ID (수정 시 자신 제외)
        
        Returns:
            {
                "collision": bool,
                "colliding_entities": [
                    {
                        "entity_id": str,
                        "entity_name": str,
                        "entity_size": str,
                        "position": Dict[str, float],
                        "distance": float,
                        "collision_radius_self": float,
                        "collision_radius_other": float,
                        "combined_radius": float
                    }
                ]
            }
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 같은 cell_id를 가진 다른 Entity들의 위치와 크기 확인
            query = """
                SELECT 
                    entity_id,
                    entity_name,
                    entity_size,
                    default_position_3d
                FROM game_data.entities
                WHERE default_position_3d IS NOT NULL
                AND default_position_3d->>'cell_id' = $1
            """
            
            params = [cell_id]
            if exclude_entity_id:
                query += " AND entity_id != $2"
                params.append(exclude_entity_id)
            
            rows = await conn.fetch(query, *params)
            
            colliding_entities = []
            self_radius = get_collision_radius(entity_size)
            
            for row in rows:
                other_position = row['default_position_3d']
                other_size = row['entity_size'] or 'medium'
                
                # JSONB가 문자열로 반환될 수 있으므로 파싱
                if isinstance(other_position, str):
                    import json
                    other_position = json.loads(other_position)
                
                # 위치 정보가 없으면 스킵
                if not other_position or not isinstance(other_position, dict) or 'x' not in other_position:
                    continue
                
                # 충돌 검사
                if check_collision(position, entity_size, other_position, other_size):
                    other_radius = get_collision_radius(other_size)
                    distance = calculate_distance(position, other_position)
                    
                    colliding_entities.append({
                        "entity_id": row['entity_id'],
                        "entity_name": row['entity_name'],
                        "entity_size": other_size,
                        "position": other_position,
                        "distance": distance,
                        "collision_radius_self": self_radius,
                        "collision_radius_other": other_radius,
                        "combined_radius": self_radius + other_radius
                    })
            
            return {
                "collision": len(colliding_entities) > 0,
                "colliding_entities": colliding_entities
            }
    
    async def check_world_object_collision(
        self,
        cell_id: str,
        position: Dict[str, float],
        entity_size: str = 'medium',
        exclude_object_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cell 내 특정 위치에 World Object가 있는지 확인
        
        Args:
            cell_id: 셀 ID
            position: 확인할 위치 {"x": 5.0, "y": 4.0, "z": 0.0}
            entity_size: 엔티티 크기
            exclude_object_id: 제외할 객체 ID
        
        Returns:
            {
                "collision": bool,
                "colliding_objects": [
                    {
                        "object_id": str,
                        "object_name": str,
                        "position": Dict[str, float],
                        "object_width": float,
                        "object_depth": float,
                        "object_height": float,
                        "passable": bool
                    }
                ]
            }
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # 같은 cell_id를 가진 World Objects 확인
            query = """
                SELECT 
                    object_id,
                    object_name,
                    default_position,
                    object_width,
                    object_depth,
                    object_height,
                    passable
                FROM game_data.world_objects
                WHERE default_cell_id = $1
                AND default_position IS NOT NULL
            """
            
            params = [cell_id]
            if exclude_object_id:
                query += " AND object_id != $2"
                params.append(exclude_object_id)
            
            rows = await conn.fetch(query, *params)
            
            colliding_objects = []
            entity_radius = get_collision_radius(entity_size)
            
            for row in rows:
                obj_position = row['default_position']
                
                # JSONB가 문자열로 반환될 수 있으므로 파싱
                if isinstance(obj_position, str):
                    import json
                    obj_position = json.loads(obj_position)
                
                # 위치 정보가 없으면 스킵
                if not obj_position or not isinstance(obj_position, dict) or 'x' not in obj_position:
                    continue
                
                # 통과 가능한 객체는 충돌로 간주하지 않음
                if row['passable']:
                    continue
                
                # 객체의 크기를 고려한 충돌 검사
                obj_width = row['object_width'] or 1.0
                obj_depth = row['object_depth'] or 1.0
                obj_radius = max(obj_width, obj_depth) / 2.0
                
                # 거리 계산
                distance = calculate_distance(position, obj_position)
                
                # 충돌 검사 (Entity 반경 + Object 반경)
                if distance < (entity_radius + obj_radius):
                    colliding_objects.append({
                        "object_id": row['object_id'],
                        "object_name": row['object_name'],
                        "position": obj_position,
                        "object_width": obj_width,
                        "object_depth": obj_depth,
                        "object_height": row['object_height'] or 1.0,
                        "passable": row['passable'] or False
                    })
            
            return {
                "collision": len(colliding_objects) > 0,
                "colliding_objects": colliding_objects
            }
    
    async def check_all_collisions(
        self,
        cell_id: str,
        position: Dict[str, float],
        entity_size: str = 'medium',
        exclude_entity_id: Optional[str] = None,
        exclude_object_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Entity와 World Object 모두에 대한 충돌 검사
        
        Args:
            cell_id: 셀 ID
            position: 확인할 위치
            entity_size: 엔티티 크기
            exclude_entity_id: 제외할 엔티티 ID
            exclude_object_id: 제외할 객체 ID
        
        Returns:
            {
                "collision": bool,
                "entity_collisions": {...},
                "object_collisions": {...}
            }
        """
        entity_result = await self.check_position_collision(
            cell_id, position, entity_size, exclude_entity_id
        )
        object_result = await self.check_world_object_collision(
            cell_id, position, entity_size, exclude_object_id
        )
        
        return {
            "collision": entity_result["collision"] or object_result["collision"],
            "entity_collisions": entity_result,
            "object_collisions": object_result
        }

