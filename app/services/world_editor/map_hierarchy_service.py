"""
계층적 맵 구조 서비스

Region Map, Location Map 등 계층적 맵 구조를 관리하는 서비스
"""
from typing import List, Optional, Dict, Any
import uuid
from database.connection import DatabaseConnection
from common.utils.logger import logger
from common.utils.jsonb_handler import parse_jsonb_data


class MapHierarchyService:
    """계층적 맵 구조 서비스"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    async def get_region_map(
        self,
        region_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Region Map 메타데이터 조회
        
        Args:
            region_id: Region ID
        
        Returns:
            Region Map 메타데이터 (없으면 기본값 반환)
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # Region 정보 조회
            region = await conn.fetchrow("""
                SELECT region_id, region_name, region_type
                FROM game_data.world_regions
                WHERE region_id = $1
            """, region_id)
            
            if not region:
                return None
            
            # Region Map 메타데이터 조회
            map_metadata = await conn.fetchrow("""
                SELECT 
                    map_id, map_name, background_image, background_color,
                    width, height, grid_enabled, grid_size,
                    zoom_level, viewport_x, viewport_y,
                    map_level, parent_entity_id, parent_entity_type
                FROM game_data.map_metadata
                WHERE map_level = 'region'
                AND parent_entity_id = $1
                AND parent_entity_type = 'region'
            """, region_id)
            
            # 기본 맵 메타데이터 (없으면 생성)
            if not map_metadata:
                return {
                    "map_id": f"region_map_{region_id}",
                    "map_name": f"{region['region_name']} Map",
                    "map_level": "region",
                    "parent_entity_id": region_id,
                    "parent_entity_type": "region",
                    "background_image": None,
                    "background_color": "#f0f0f0",
                    "width": 1000,
                    "height": 1000,
                    "grid_enabled": True,
                    "grid_size": 50,
                    "zoom_level": 1.0,
                    "viewport_x": 0,
                    "viewport_y": 0
                }
            
            return {
                "map_id": map_metadata['map_id'],
                "map_name": map_metadata['map_name'],
                "map_level": map_metadata['map_level'],
                "parent_entity_id": map_metadata['parent_entity_id'],
                "parent_entity_type": map_metadata['parent_entity_type'],
                "background_image": map_metadata['background_image'],
                "background_color": map_metadata['background_color'],
                "width": map_metadata['width'],
                "height": map_metadata['height'],
                "grid_enabled": map_metadata['grid_enabled'],
                "grid_size": map_metadata['grid_size'],
                "zoom_level": float(map_metadata['zoom_level']),
                "viewport_x": map_metadata['viewport_x'],
                "viewport_y": map_metadata['viewport_y']
            }
    
    async def get_region_locations(
        self,
        region_id: str
    ) -> List[Dict[str, Any]]:
        """
        Region 내 Location 목록 조회 (위치 정보 포함)
        
        Args:
            region_id: Region ID
        
        Returns:
            Location 목록 (위치 정보 포함)
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # Location 목록 조회
            locations = await conn.fetch("""
                SELECT 
                    l.location_id,
                    l.location_name,
                    l.location_type,
                    l.location_description,
                    l.location_properties,
                    p.x,
                    p.y,
                    p.pin_type
                FROM game_data.world_locations l
                LEFT JOIN game_data.pin_positions p ON (
                    p.game_data_id = l.location_id
                    AND p.pin_type = 'location'
                )
                WHERE l.region_id = $1
                ORDER BY l.location_name
            """, region_id)
            
            result = []
            for row in locations:
                properties = parse_jsonb_data(row.get('location_properties'))
                result.append({
                    "location_id": row['location_id'],
                    "location_name": row['location_name'],
                    "location_type": row['location_type'],
                    "location_description": row['location_description'],
                    "properties": properties or {},
                    "position": {
                        "x": float(row['x']) if row['x'] is not None else None,
                        "y": float(row['y']) if row['y'] is not None else None
                    }
                })
            
            return result
    
    async def place_location_in_region(
        self,
        region_id: str,
        location_id: str,
        position: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Region Map에 Location 배치
        
        Args:
            region_id: Region ID
            location_id: Location ID
            position: 위치 {"x": 100.0, "y": 200.0}
        
        Returns:
            배치 결과
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                # Location이 해당 Region에 속하는지 확인
                location = await conn.fetchrow("""
                    SELECT location_id, location_name, region_id
                    FROM game_data.world_locations
                    WHERE location_id = $1 AND region_id = $2
                """, location_id, region_id)
                
                if not location:
                    raise ValueError(f"Location {location_id} not found in region {region_id}")
                
                # 기존 핀 확인
                existing_pin = await conn.fetchrow("""
                    SELECT pin_id, pin_name
                    FROM game_data.pin_positions
                    WHERE game_data_id = $1 AND pin_type = 'location'
                """, location_id)
                
                if existing_pin:
                    # 기존 핀 업데이트
                    await conn.execute("""
                        UPDATE game_data.pin_positions
                        SET x = $1, y = $2, updated_at = CURRENT_TIMESTAMP
                        WHERE pin_id = $3
                    """, position['x'], position['y'], existing_pin['pin_id'])
                else:
                    # 새 핀 생성
                    pin_id = f"PIN_{uuid.uuid4().hex[:8].upper()}"
                    pin_name = location['location_name'] or f"새 핀 {pin_id[-4:]}"
                    await conn.execute("""
                        INSERT INTO game_data.pin_positions
                        (pin_id, pin_name, game_data_id, pin_type, x, y, icon_type, color, size)
                        VALUES ($1, $2, $3, 'location', $4, $5, 'default', '#FF6B9D', 10)
                    """, pin_id, pin_name, location_id, position['x'], position['y'])
                
                return {
                    "location_id": location_id,
                    "position": position,
                    "status": "placed"
                }
    
    async def get_location_map(
        self,
        location_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Location Map 메타데이터 조회
        
        Args:
            location_id: Location ID
        
        Returns:
            Location Map 메타데이터 (없으면 기본값 반환)
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # Location 정보 조회
            location = await conn.fetchrow("""
                SELECT location_id, location_name, location_type
                FROM game_data.world_locations
                WHERE location_id = $1
            """, location_id)
            
            if not location:
                return None
            
            # Location Map 메타데이터 조회
            map_metadata = await conn.fetchrow("""
                SELECT 
                    map_id, map_name, background_image, background_color,
                    width, height, grid_enabled, grid_size,
                    zoom_level, viewport_x, viewport_y,
                    map_level, parent_entity_id, parent_entity_type
                FROM game_data.map_metadata
                WHERE map_level = 'location'
                AND parent_entity_id = $1
                AND parent_entity_type = 'location'
            """, location_id)
            
            # 기본 맵 메타데이터 (없으면 생성)
            if not map_metadata:
                return {
                    "map_id": f"location_map_{location_id}",
                    "map_name": f"{location['location_name']} Map",
                    "map_level": "location",
                    "parent_entity_id": location_id,
                    "parent_entity_type": "location",
                    "background_image": None,
                    "background_color": "#e0e0e0",
                    "width": 800,
                    "height": 800,
                    "grid_enabled": True,
                    "grid_size": 40,
                    "zoom_level": 1.0,
                    "viewport_x": 0,
                    "viewport_y": 0
                }
            
            return {
                "map_id": map_metadata['map_id'],
                "map_name": map_metadata['map_name'],
                "map_level": map_metadata['map_level'],
                "parent_entity_id": map_metadata['parent_entity_id'],
                "parent_entity_type": map_metadata['parent_entity_type'],
                "background_image": map_metadata['background_image'],
                "background_color": map_metadata['background_color'],
                "width": map_metadata['width'],
                "height": map_metadata['height'],
                "grid_enabled": map_metadata['grid_enabled'],
                "grid_size": map_metadata['grid_size'],
                "zoom_level": float(map_metadata['zoom_level']),
                "viewport_x": map_metadata['viewport_x'],
                "viewport_y": map_metadata['viewport_y']
            }
    
    async def get_location_cells(
        self,
        location_id: str
    ) -> List[Dict[str, Any]]:
        """
        Location 내 Cell 목록 조회 (위치 정보 포함)
        
        Args:
            location_id: Location ID
        
        Returns:
            Cell 목록 (위치 정보 포함)
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            # Cell 목록 조회
            cells = await conn.fetch("""
                SELECT 
                    c.cell_id,
                    c.cell_name,
                    c.matrix_width,
                    c.matrix_height,
                    c.cell_description,
                    c.cell_properties,
                    p.x,
                    p.y,
                    p.pin_type
                FROM game_data.world_cells c
                LEFT JOIN game_data.pin_positions p ON (
                    p.game_data_id = c.cell_id
                    AND p.pin_type = 'cell'
                )
                WHERE c.location_id = $1
                ORDER BY c.cell_name
            """, location_id)
            
            result = []
            for row in cells:
                cell_properties = parse_jsonb_data(row['cell_properties'])
                result.append({
                    "cell_id": row['cell_id'],
                    "cell_name": row['cell_name'],
                    "matrix_width": row['matrix_width'],
                    "matrix_height": row['matrix_height'],
                    "cell_description": row['cell_description'],
                    "cell_properties": cell_properties or {},
                    "position": {
                        "x": float(row['x']) if row['x'] is not None else None,
                        "y": float(row['y']) if row['y'] is not None else None
                    }
                })
            
            return result
    
    async def place_cell_in_location(
        self,
        location_id: str,
        cell_id: str,
        position: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Location Map에 Cell 배치
        
        Args:
            location_id: Location ID
            cell_id: Cell ID
            position: 위치 {"x": 100.0, "y": 200.0}
        
        Returns:
            배치 결과
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                # Cell이 해당 Location에 속하는지 확인
                cell = await conn.fetchrow("""
                    SELECT cell_id, cell_name, location_id
                    FROM game_data.world_cells
                    WHERE cell_id = $1 AND location_id = $2
                """, cell_id, location_id)
                
                if not cell:
                    raise ValueError(f"Cell {cell_id} not found in location {location_id}")
                
                # 기존 핀 확인
                existing_pin = await conn.fetchrow("""
                    SELECT pin_id, pin_name
                    FROM game_data.pin_positions
                    WHERE game_data_id = $1 AND pin_type = 'cell'
                """, cell_id)
                
                if existing_pin:
                    # 기존 핀 업데이트
                    await conn.execute("""
                        UPDATE game_data.pin_positions
                        SET x = $1, y = $2, updated_at = CURRENT_TIMESTAMP
                        WHERE pin_id = $3
                    """, position['x'], position['y'], existing_pin['pin_id'])
                else:
                    # 새 핀 생성
                    pin_id = f"PIN_{uuid.uuid4().hex[:8].upper()}"
                    pin_name = cell['cell_name'] or f"새 핀 {pin_id[-4:]}"
                    await conn.execute("""
                        INSERT INTO game_data.pin_positions
                        (pin_id, pin_name, game_data_id, pin_type, x, y, icon_type, color, size)
                        VALUES ($1, $2, $3, 'cell', $4, $5, 'default', '#FF6B9D', 10)
                    """, pin_id, pin_name, cell_id, position['x'], position['y'])
                
                return {
                    "cell_id": cell_id,
                    "position": position,
                    "status": "placed"
                }
    
    async def update_map_metadata(
        self,
        map_level: str,
        parent_entity_id: str,
        parent_entity_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        맵 메타데이터 업데이트 또는 생성
        
        Args:
            map_level: 맵 레벨 ('world', 'region', 'location', 'cell')
            parent_entity_id: 부모 엔티티 ID
            parent_entity_type: 부모 엔티티 타입
            metadata: 맵 메타데이터
        
        Returns:
            업데이트된 맵 메타데이터
        """
        pool = await self.db.pool
        async with pool.acquire() as conn:
            map_id = metadata.get('map_id') or f"{map_level}_map_{parent_entity_id}"
            
            await conn.execute("""
                INSERT INTO game_data.map_metadata
                (
                    map_id, map_name, background_image, background_color,
                    width, height, grid_enabled, grid_size,
                    zoom_level, viewport_x, viewport_y,
                    map_level, parent_entity_id, parent_entity_type
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
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
                    map_level = EXCLUDED.map_level,
                    parent_entity_id = EXCLUDED.parent_entity_id,
                    parent_entity_type = EXCLUDED.parent_entity_type,
                    updated_at = CURRENT_TIMESTAMP
            """,
                map_id,
                metadata.get('map_name', f'{map_level} Map'),
                metadata.get('background_image'),
                metadata.get('background_color', '#f0f0f0'),
                metadata.get('width', 1000),
                metadata.get('height', 1000),
                metadata.get('grid_enabled', True),
                metadata.get('grid_size', 50),
                metadata.get('zoom_level', 1.0),
                metadata.get('viewport_x', 0),
                metadata.get('viewport_y', 0),
                map_level,
                parent_entity_id,
                parent_entity_type
            )
            
            # 업데이트된 메타데이터 반환
            if map_level == 'region':
                return await self.get_region_map(parent_entity_id)
            elif map_level == 'location':
                return await self.get_location_map(parent_entity_id)
            else:
                return {
                    "map_id": map_id,
                    "map_level": map_level,
                    "parent_entity_id": parent_entity_id,
                    "parent_entity_type": parent_entity_type
                }

