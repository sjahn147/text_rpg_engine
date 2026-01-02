"""
셀 서비스
"""
from typing import List, Optional, Dict, Any, Union
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from app.api.schemas import (
    CellCreate, CellUpdate, CellResponse, CellResolvedResponse
)
from common.utils.logger import logger
from common.utils.jsonb_handler import serialize_jsonb_data, parse_jsonb_data
from app.common.decorators.error_handler import handle_service_errors
from app.services.integrity_service import IntegrityService


class CellService:
    """셀 서비스"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db = db_connection or DatabaseConnection()
        self.game_data_repo = GameDataRepository(self.db)
        self.integrity_service = IntegrityService(self.db)
    
    async def get_all_cells(self) -> List[CellResponse]:
        """모든 셀 조회 (SSOT 준수: owner_name은 JOIN으로 해결)"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        c.cell_id, c.location_id, c.cell_name, c.matrix_width, c.matrix_height,
                        c.cell_description, c.cell_properties, 
                        COALESCE(c.cell_status, 'active') as cell_status,
                        COALESCE(c.cell_type, 'indoor') as cell_type,
                        c.created_at, c.updated_at,
                        e.entity_name as owner_name
                    FROM game_data.world_cells c
                    LEFT JOIN game_data.entities e ON (
                        e.entity_id = c.cell_properties->'ownership'->>'owner_entity_id'
                    )
                    ORDER BY c.cell_name
                """)
                
                cells = []
                for row in rows:
                    cell_properties = parse_jsonb_data(row['cell_properties'])
                    # SSOT 준수: cell_properties에서 owner_name 제거 (있다면)
                    if cell_properties and 'ownership' in cell_properties:
                        ownership = cell_properties.get('ownership', {})
                        if isinstance(ownership, dict) and 'owner_name' in ownership:
                            ownership = ownership.copy()
                            ownership.pop('owner_name', None)
                            cell_properties = cell_properties.copy()
                            cell_properties['ownership'] = ownership
                    
                    cells.append(CellResponse(
                        cell_id=row['cell_id'],
                        location_id=row['location_id'],
                        cell_name=row['cell_name'],
                        matrix_width=row['matrix_width'],
                        matrix_height=row['matrix_height'],
                        cell_description=row['cell_description'],
                        cell_properties=cell_properties or {},
                        cell_status=row.get('cell_status', 'active'),
                        cell_type=row.get('cell_type', 'indoor'),
                        created_at=row['created_at'],
                        updated_at=row['updated_at'],
                        owner_name=row['owner_name']  # JOIN으로 해결
                    ))
                
                return cells
        except Exception as e:
            logger.error(f"셀 조회 실패: {e}")
            raise
    
    async def get_cell(self, cell_id: str) -> Optional[CellResponse]:
        """특정 셀 조회 (SSOT 준수: owner_name은 JOIN으로 해결)"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT 
                        c.cell_id, c.location_id, c.cell_name, c.matrix_width, c.matrix_height,
                        c.cell_description, c.cell_properties,
                        COALESCE(c.cell_status, 'active') as cell_status,
                        COALESCE(c.cell_type, 'indoor') as cell_type,
                        c.created_at, c.updated_at,
                        e.entity_name as owner_name
                    FROM game_data.world_cells c
                    LEFT JOIN game_data.entities e ON (
                        e.entity_id = c.cell_properties->'ownership'->>'owner_entity_id'
                    )
                    WHERE c.cell_id = $1
                """, cell_id)
                
                if not row:
                    return None
                
                cell_properties = parse_jsonb_data(row['cell_properties'])
                # SSOT 준수: cell_properties에서 owner_name 제거 (있다면)
                if cell_properties and 'ownership' in cell_properties:
                    ownership = cell_properties.get('ownership', {})
                    if isinstance(ownership, dict) and 'owner_name' in ownership:
                        ownership = ownership.copy()
                        ownership.pop('owner_name', None)
                        cell_properties = cell_properties.copy()
                        cell_properties['ownership'] = ownership
                
                return CellResponse(
                    cell_id=row['cell_id'],
                    location_id=row['location_id'],
                    cell_name=row['cell_name'],
                    matrix_width=row['matrix_width'],
                    matrix_height=row['matrix_height'],
                    cell_description=row['cell_description'],
                    cell_properties=cell_properties or {},
                    cell_status=row.get('cell_status', 'active'),
                    cell_type=row.get('cell_type', 'indoor'),
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    owner_name=row['owner_name']  # JOIN으로 해결
                )
        except Exception as e:
            logger.error(f"셀 조회 실패: {e}")
            raise
    
    async def get_cells_by_location(self, location_id: str) -> List[CellResponse]:
        """특정 위치의 모든 셀 조회 (SSOT 준수: owner_name은 JOIN으로 해결)"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        c.cell_id, c.location_id, c.cell_name, c.matrix_width, c.matrix_height,
                        c.cell_description, c.cell_properties,
                        COALESCE(c.cell_status, 'active') as cell_status,
                        COALESCE(c.cell_type, 'indoor') as cell_type,
                        c.created_at, c.updated_at,
                        e.entity_name as owner_name
                    FROM game_data.world_cells c
                    LEFT JOIN game_data.entities e ON (
                        e.entity_id = c.cell_properties->'ownership'->>'owner_entity_id'
                    )
                    WHERE c.location_id = $1
                    ORDER BY c.cell_name
                """, location_id)
                
                cells = []
                for row in rows:
                    cell_properties = parse_jsonb_data(row['cell_properties'])
                    # SSOT 준수: cell_properties에서 owner_name 제거 (있다면)
                    if cell_properties and 'ownership' in cell_properties:
                        ownership = cell_properties.get('ownership', {})
                        if isinstance(ownership, dict) and 'owner_name' in ownership:
                            ownership = ownership.copy()
                            ownership.pop('owner_name', None)
                            cell_properties = cell_properties.copy()
                            cell_properties['ownership'] = ownership
                    
                    cells.append(CellResponse(
                        cell_id=row['cell_id'],
                        location_id=row['location_id'],
                        cell_name=row['cell_name'],
                        matrix_width=row['matrix_width'],
                        matrix_height=row['matrix_height'],
                        cell_description=row['cell_description'],
                        cell_properties=cell_properties or {},
                        cell_status=row.get('cell_status', 'active'),
                        cell_type=row.get('cell_type', 'indoor'),
                        created_at=row['created_at'],
                        updated_at=row['updated_at'],
                        owner_name=row['owner_name']  # JOIN으로 해결
                    ))
                
                return cells
        except Exception as e:
            logger.error(f"위치별 셀 조회 실패: {e}")
            raise
    
    @handle_service_errors
    async def create_cell(self, cell_data: CellCreate) -> CellResponse:
        """새 셀 생성"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                cell_properties_json = serialize_jsonb_data(cell_data.cell_properties)
                
                await conn.execute("""
                    INSERT INTO game_data.world_cells
                    (cell_id, location_id, cell_name, matrix_width, matrix_height,
                     cell_description, cell_properties, cell_status, cell_type)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                cell_data.cell_id,
                cell_data.location_id,
                cell_data.cell_name,
                cell_data.matrix_width,
                cell_data.matrix_height,
                cell_data.cell_description,
                cell_properties_json,
                cell_data.cell_status or 'active',
                cell_data.cell_type or 'indoor'
                )
                
                return await self.get_cell(cell_data.cell_id)
        except Exception as e:
            logger.error(f"셀 생성 실패: {e}")
            raise
    
    @handle_service_errors
    async def update_cell(
        self, 
        cell_id: str, 
        cell_data: Union[CellUpdate, Dict[str, Any]]
    ) -> CellResponse:
        """셀 정보 업데이트"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                existing = await self.get_cell(cell_id)
                if not existing:
                    raise ValueError(f"셀을 찾을 수 없습니다: {cell_id}")
                
                # Dict인 경우 CellUpdate로 변환
                if isinstance(cell_data, dict):
                    cell_data = CellUpdate(**cell_data)
                
                update_fields = []
                values = []
                param_index = 1
                
                if cell_data.location_id is not None:
                    update_fields.append(f"location_id = ${param_index}")
                    values.append(cell_data.location_id)
                    param_index += 1
                
                if cell_data.cell_name is not None:
                    update_fields.append(f"cell_name = ${param_index}")
                    values.append(cell_data.cell_name)
                    param_index += 1
                
                if cell_data.matrix_width is not None:
                    update_fields.append(f"matrix_width = ${param_index}")
                    values.append(cell_data.matrix_width)
                    param_index += 1
                
                if cell_data.matrix_height is not None:
                    update_fields.append(f"matrix_height = ${param_index}")
                    values.append(cell_data.matrix_height)
                    param_index += 1
                
                if cell_data.cell_description is not None:
                    update_fields.append(f"cell_description = ${param_index}")
                    values.append(cell_data.cell_description)
                    param_index += 1
                
                if cell_data.cell_properties is not None:
                    update_fields.append(f"cell_properties = ${param_index}")
                    values.append(serialize_jsonb_data(cell_data.cell_properties))
                    param_index += 1
                
                if cell_data.cell_status is not None:
                    update_fields.append(f"cell_status = ${param_index}")
                    values.append(cell_data.cell_status)
                    param_index += 1
                
                if cell_data.cell_type is not None:
                    update_fields.append(f"cell_type = ${param_index}")
                    values.append(cell_data.cell_type)
                    param_index += 1
                
                if update_fields:
                    update_fields.append(f"updated_at = CURRENT_TIMESTAMP")
                    values.append(cell_id)
                    
                    query = f"""
                        UPDATE game_data.world_cells
                        SET {', '.join(update_fields)}
                        WHERE cell_id = ${param_index}
                    """
                    
                    await conn.execute(query, *values)
                
                return await self.get_cell(cell_id)
        except Exception as e:
            logger.error(f"셀 업데이트 실패: {e}")
            raise
    
    async def validate_cell_references(self, cell_id: str) -> Dict[str, List[str]]:
        """
        Cell이 참조되는 Location/Cell 목록 반환 (SSOT 참조 무결성 검증)
        
        Returns:
            {
                "locations_in_entry_points": ["LOC_001", ...],
                "cells_in_exits": ["CELL_002", ...],
                "cells_in_entrances": ["CELL_003", ...],
                "cells_in_connections": ["CELL_004", ...]
            }
        """
        # IntegrityService로 위임
        return await self.integrity_service.validate_cell_references(cell_id)
    
    async def get_cell_resolved(self, cell_id: str) -> Optional[CellResolvedResponse]:
        """모든 참조를 해결한 셀 조회 (Phase 4)"""
        try:
            cell = await self.get_cell(cell_id)
            if not cell:
                return None
            
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # owner_entity 정보 조회
                owner_entity = None
                if cell.cell_properties and cell.cell_properties.get('ownership', {}).get('owner_entity_id'):
                    owner_entity_id = cell.cell_properties['ownership']['owner_entity_id']
                    owner_row = await conn.fetchrow("""
                        SELECT entity_id, entity_type, entity_name, entity_description,
                               entity_status, base_stats, default_equipment, default_abilities,
                               default_inventory, entity_properties, default_position_3d, entity_size
                        FROM game_data.entities
                        WHERE entity_id = $1
                    """, owner_entity_id)
                    
                    if owner_row:
                        owner_entity = {
                            "entity_id": owner_row['entity_id'],
                            "entity_type": owner_row['entity_type'],
                            "entity_name": owner_row['entity_name'],
                            "entity_description": owner_row['entity_description'],
                            "entity_status": owner_row.get('entity_status', 'active'),
                            "base_stats": parse_jsonb_data(owner_row['base_stats']),
                            "default_equipment": parse_jsonb_data(owner_row['default_equipment']),
                            "default_abilities": parse_jsonb_data(owner_row['default_abilities']),
                            "default_inventory": parse_jsonb_data(owner_row['default_inventory']),
                            "entity_properties": parse_jsonb_data(owner_row['entity_properties']),
                            "default_position_3d": parse_jsonb_data(owner_row.get('default_position_3d')),
                            "entity_size": owner_row.get('entity_size')
                        }
                
                # exit_cells 조회
                exit_cells = []
                if cell.cell_properties and cell.cell_properties.get('structure', {}).get('exits'):
                    exits = cell.cell_properties['structure']['exits']
                    if isinstance(exits, list):
                        for exit_data in exits:
                            if isinstance(exit_data, dict) and exit_data.get('cell_id'):
                                exit_cell_id = exit_data['cell_id']
                                exit_cell_row = await conn.fetchrow("""
                                    SELECT cell_id, location_id, cell_name, matrix_width, matrix_height,
                                           cell_description, cell_properties, cell_status, cell_type
                                    FROM game_data.world_cells
                                    WHERE cell_id = $1
                                """, exit_cell_id)
                                
                                if exit_cell_row:
                                    exit_cells.append({
                                        "cell_id": exit_cell_row['cell_id'],
                                        "location_id": exit_cell_row['location_id'],
                                        "cell_name": exit_cell_row['cell_name'],
                                        "matrix_width": exit_cell_row['matrix_width'],
                                        "matrix_height": exit_cell_row['matrix_height'],
                                        "cell_description": exit_cell_row['cell_description'],
                                        "cell_properties": parse_jsonb_data(exit_cell_row['cell_properties']),
                                        "cell_status": exit_cell_row.get('cell_status', 'active'),
                                        "cell_type": exit_cell_row.get('cell_type', 'indoor'),
                                        "direction": exit_data.get('direction'),
                                        "exit_data": exit_data
                                    })
                
                # entrance_cells 조회
                entrance_cells = []
                if cell.cell_properties and cell.cell_properties.get('structure', {}).get('entrances'):
                    entrances = cell.cell_properties['structure']['entrances']
                    if isinstance(entrances, list):
                        for entrance_data in entrances:
                            if isinstance(entrance_data, dict) and entrance_data.get('cell_id'):
                                entrance_cell_id = entrance_data['cell_id']
                                entrance_cell_row = await conn.fetchrow("""
                                    SELECT cell_id, location_id, cell_name, matrix_width, matrix_height,
                                           cell_description, cell_properties, cell_status, cell_type
                                    FROM game_data.world_cells
                                    WHERE cell_id = $1
                                """, entrance_cell_id)
                                
                                if entrance_cell_row:
                                    entrance_cells.append({
                                        "cell_id": entrance_cell_row['cell_id'],
                                        "location_id": entrance_cell_row['location_id'],
                                        "cell_name": entrance_cell_row['cell_name'],
                                        "matrix_width": entrance_cell_row['matrix_width'],
                                        "matrix_height": entrance_cell_row['matrix_height'],
                                        "cell_description": entrance_cell_row['cell_description'],
                                        "cell_properties": parse_jsonb_data(entrance_cell_row['cell_properties']),
                                        "cell_status": entrance_cell_row.get('cell_status', 'active'),
                                        "cell_type": entrance_cell_row.get('cell_type', 'indoor'),
                                        "direction": entrance_data.get('direction'),
                                        "entrance_data": entrance_data
                                    })
                
                # connection_cells 조회
                connection_cells = []
                if cell.cell_properties and cell.cell_properties.get('structure', {}).get('connections'):
                    connections = cell.cell_properties['structure']['connections']
                    if isinstance(connections, list):
                        for connection_data in connections:
                            if isinstance(connection_data, dict) and connection_data.get('cell_id'):
                                connection_cell_id = connection_data['cell_id']
                                connection_cell_row = await conn.fetchrow("""
                                    SELECT cell_id, location_id, cell_name, matrix_width, matrix_height,
                                           cell_description, cell_properties, cell_status, cell_type
                                    FROM game_data.world_cells
                                    WHERE cell_id = $1
                                """, connection_cell_id)
                                
                                if connection_cell_row:
                                    connection_cells.append({
                                        "cell_id": connection_cell_row['cell_id'],
                                        "location_id": connection_cell_row['location_id'],
                                        "cell_name": connection_cell_row['cell_name'],
                                        "matrix_width": connection_cell_row['matrix_width'],
                                        "matrix_height": connection_cell_row['matrix_height'],
                                        "cell_description": connection_cell_row['cell_description'],
                                        "cell_properties": parse_jsonb_data(connection_cell_row['cell_properties']),
                                        "cell_status": connection_cell_row.get('cell_status', 'active'),
                                        "cell_type": connection_cell_row.get('cell_type', 'indoor'),
                                        "connection_type": connection_data.get('connection_type'),
                                        "connection_data": connection_data
                                    })
                
                return CellResolvedResponse(
                    **cell.model_dump(),
                    owner_entity=owner_entity,
                    exit_cells=exit_cells if exit_cells else None,
                    entrance_cells=entrance_cells if entrance_cells else None,
                    connection_cells=connection_cells if connection_cells else None
                )
        except Exception as e:
            logger.error(f"해결된 셀 조회 실패: {e}")
            raise
    
    @handle_service_errors
    async def delete_cell(self, cell_id: str) -> bool:
        """셀 삭제 (SSOT 참조 무결성 검증 포함)"""
        # IntegrityService로 삭제 가능 여부 검사
        check_result = await self.integrity_service.can_delete_cell(cell_id)
        
        if not check_result.can_delete:
            raise ValueError(
                f"셀 '{cell_id}'는 다음 위치에서 참조되고 있어 삭제할 수 없습니다:\n" +
                check_result.error_message +
                "\n\n참조를 먼저 제거한 후 삭제해주세요."
            )
        
        pool = await self.db.pool
        async with pool.acquire() as conn:
            result = await conn.execute("""
                DELETE FROM game_data.world_cells
                WHERE cell_id = $1
            """, cell_id)
            
            return result == "DELETE 1"

