"""
World Objects와 Entity 상호작용 서비스

Entity가 World Object와 상호작용할 수 있는지 검사하는 서비스
"""
from typing import Dict, Any, Optional

from database.connection import DatabaseConnection
from .collision_service import CollisionService


class InteractionService:
    """World Objects와 Entity 상호작용 서비스"""
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.collision_service = CollisionService()
    
    async def can_entity_pass_through(
        self,
        entity_id: str,
        object_id: str
    ) -> Dict[str, Any]:
        """
        Entity가 World Object를 통과할 수 있는지 확인
        
        Args:
            entity_id: 엔티티 ID
            object_id: 객체 ID
        
        Returns:
            {
                "can_pass": bool,
                "reason": str,
                "object_info": {...}
            }
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # Entity 정보 조회
            entity_row = await conn.fetchrow("""
                SELECT entity_id, entity_name, entity_size, default_position_3d
                FROM game_data.entities
                WHERE entity_id = $1
            """, entity_id)
            
            if not entity_row:
                return {
                    "can_pass": False,
                    "reason": "Entity not found",
                    "object_info": None
                }
            
            # World Object 정보 조회
            object_row = await conn.fetchrow("""
                SELECT 
                    object_id,
                    object_name,
                    object_type,
                    passable,
                    object_width,
                    object_depth,
                    object_height,
                    properties
                FROM game_data.world_objects
                WHERE object_id = $1
            """, object_id)
            
            if not object_row:
                return {
                    "can_pass": False,
                    "reason": "Object not found",
                    "object_info": None
                }
            
            # 통과 가능 여부 확인
            can_pass = object_row['passable'] or False
            
            object_info = {
                "object_id": object_row['object_id'],
                "object_name": object_row['object_name'],
                "object_type": object_row['object_type'],
                "passable": can_pass,
                "dimensions": {
                    "width": object_row['object_width'] or 1.0,
                    "depth": object_row['object_depth'] or 1.0,
                    "height": object_row['object_height'] or 1.0
                },
                "properties": object_row['properties'] if isinstance(object_row['properties'], dict) else {}
            }
            
            return {
                "can_pass": can_pass,
                "reason": "Object is passable" if can_pass else "Object is not passable",
                "object_info": object_info
            }
    
    async def can_entity_move_object(
        self,
        entity_id: str,
        object_id: str
    ) -> Dict[str, Any]:
        """
        Entity가 World Object를 이동시킬 수 있는지 확인
        
        Args:
            entity_id: 엔티티 ID
            object_id: 객체 ID
        
        Returns:
            {
                "can_move": bool,
                "reason": str,
                "entity_strength": float,
                "object_weight": float,
                "object_info": {...}
            }
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # Entity 정보 조회
            entity_row = await conn.fetchrow("""
                SELECT 
                    entity_id,
                    entity_name,
                    base_stats,
                    entity_size
                FROM game_data.entities
                WHERE entity_id = $1
            """, entity_id)
            
            if not entity_row:
                return {
                    "can_move": False,
                    "reason": "Entity not found",
                    "entity_strength": 0.0,
                    "object_weight": 0.0,
                    "object_info": None
                }
            
            # World Object 정보 조회
            object_row = await conn.fetchrow("""
                SELECT 
                    object_id,
                    object_name,
                    object_type,
                    movable,
                    object_weight,
                    properties
                FROM game_data.world_objects
                WHERE object_id = $1
            """, object_id)
            
            if not object_row:
                return {
                    "can_move": False,
                    "reason": "Object not found",
                    "entity_strength": 0.0,
                    "object_weight": 0.0,
                    "object_info": None
                }
            
            # 이동 가능 여부 확인
            is_movable = object_row['movable'] or False
            object_weight = object_row['object_weight'] or 0.0
            
            # Entity의 힘(strength) 추출
            base_stats = entity_row['base_stats']
            if isinstance(base_stats, str):
                import json
                base_stats = json.loads(base_stats)
            
            entity_strength = 0.0
            if isinstance(base_stats, dict):
                entity_strength = base_stats.get('strength', 0.0) or 0.0
            
            # 크기별 기본 힘 보정
            entity_size = entity_row['entity_size'] or 'medium'
            size_multiplier = {
                'tiny': 0.5,
                'small': 0.75,
                'medium': 1.0,
                'large': 1.5,
                'huge': 2.0,
                'gargantuan': 3.0
            }.get(entity_size, 1.0)
            
            effective_strength = entity_strength * size_multiplier
            
            # 이동 가능 여부 판단
            can_move = is_movable and effective_strength >= object_weight
            
            object_info = {
                "object_id": object_row['object_id'],
                "object_name": object_row['object_name'],
                "object_type": object_row['object_type'],
                "movable": is_movable,
                "object_weight": object_weight,
                "properties": object_row['properties'] if isinstance(object_row['properties'], dict) else {}
            }
            
            reason = "Object is not movable"
            if is_movable:
                if effective_strength >= object_weight:
                    reason = "Entity has enough strength to move the object"
                else:
                    reason = f"Entity strength ({effective_strength}) is less than object weight ({object_weight})"
            
            return {
                "can_move": can_move,
                "reason": reason,
                "entity_strength": effective_strength,
                "object_weight": object_weight,
                "object_info": object_info
            }
    
    async def validate_wall_mounted_placement(
        self,
        object_id: str,
        position: Dict[str, float],
        cell_id: str
    ) -> Dict[str, Any]:
        """
        벽에 부착된 객체의 배치 유효성 검사
        
        Args:
            object_id: 객체 ID
            position: 배치할 위치 {"x": 5.0, "y": 4.0, "z": 0.0}
            cell_id: 셀 ID
        
        Returns:
            {
                "valid": bool,
                "reason": str,
                "suggestions": List[Dict[str, float]]
            }
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # World Object 정보 조회
            object_row = await conn.fetchrow("""
                SELECT 
                    object_id,
                    object_name,
                    wall_mounted,
                    object_width,
                    object_depth,
                    object_height
                FROM game_data.world_objects
                WHERE object_id = $1
            """, object_id)
            
            if not object_row:
                return {
                    "valid": False,
                    "reason": "Object not found",
                    "suggestions": []
                }
            
            is_wall_mounted = object_row['wall_mounted'] or False
            
            if not is_wall_mounted:
                return {
                    "valid": True,
                    "reason": "Object is not wall-mounted, placement validation not required",
                    "suggestions": []
                }
            
            # Cell 정보 조회 (벽 위치 확인)
            cell_row = await conn.fetchrow("""
                SELECT 
                    cell_id,
                    cell_name,
                    matrix_width,
                    matrix_height,
                    cell_properties
                FROM game_data.world_cells
                WHERE cell_id = $1
            """, cell_id)
            
            if not cell_row:
                return {
                    "valid": False,
                    "reason": "Cell not found",
                    "suggestions": []
                }
            
            matrix_width = cell_row['matrix_width'] or 20
            matrix_height = cell_row['matrix_height'] or 20
            
            # 벽 위치 확인 (셀 경계)
            x = position.get('x', 0)
            y = position.get('y', 0)
            
            # 벽에 부착된 객체는 셀 경계 근처에 배치되어야 함
            wall_threshold = 0.5  # 벽으로 간주할 거리 (미터)
            
            is_near_wall = (
                x <= wall_threshold or  # 왼쪽 벽
                x >= (matrix_width - wall_threshold) or  # 오른쪽 벽
                y <= wall_threshold or  # 아래 벽
                y >= (matrix_height - wall_threshold)  # 위 벽
            )
            
            if not is_near_wall:
                # 벽 근처 위치 제안
                suggestions = []
                if x > wall_threshold:
                    suggestions.append({"x": wall_threshold, "y": y, "z": position.get('z', 0)})
                if x < (matrix_width - wall_threshold):
                    suggestions.append({"x": matrix_width - wall_threshold, "y": y, "z": position.get('z', 0)})
                if y > wall_threshold:
                    suggestions.append({"x": x, "y": wall_threshold, "z": position.get('z', 0)})
                if y < (matrix_height - wall_threshold):
                    suggestions.append({"x": x, "y": matrix_height - wall_threshold, "z": position.get('z', 0)})
                
                return {
                    "valid": False,
                    "reason": "Wall-mounted object must be placed near cell walls",
                    "suggestions": suggestions
                }
            
            return {
                "valid": True,
                "reason": "Object is placed near a wall",
                "suggestions": []
            }

