"""
지역 서비스
"""
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import json
import uuid

from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from app.api.schemas import (
    RegionCreate, RegionUpdate, RegionResponse
)
from common.utils.logger import logger
from common.utils.jsonb_handler import serialize_jsonb_data, parse_jsonb_data


class RegionService:
    """지역 서비스"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db = db_connection or DatabaseConnection()
        self.game_data_repo = GameDataRepository(self.db)
    
    async def get_all_regions(self) -> List[RegionResponse]:
        """모든 지역 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        region_id, region_name, region_description, region_type,
                        region_properties, created_at, updated_at
                    FROM game_data.world_regions
                    ORDER BY region_name
                """)
                
                regions = []
                for row in rows:
                    region_properties = parse_jsonb_data(row['region_properties'])
                    regions.append(RegionResponse(
                        region_id=row['region_id'],
                        region_name=row['region_name'],
                        region_description=row['region_description'],
                        region_type=row['region_type'],
                        region_properties=region_properties or {},
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))
                
                return regions
        except Exception as e:
            logger.error(f"지역 조회 실패: {e}")
            raise
    
    async def get_region(self, region_id: str) -> Optional[RegionResponse]:
        """특정 지역 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT 
                        region_id, region_name, region_description, region_type,
                        region_properties, created_at, updated_at
                    FROM game_data.world_regions
                    WHERE region_id = $1
                """, region_id)
                
                if not row:
                    return None
                
                region_properties = parse_jsonb_data(row['region_properties'])
                return RegionResponse(
                    region_id=row['region_id'],
                    region_name=row['region_name'],
                    region_description=row['region_description'],
                    region_type=row['region_type'],
                    region_properties=region_properties or {},
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
        except Exception as e:
            logger.error(f"지역 조회 실패: {e}")
            raise
    
    async def create_region(self, region_data: RegionCreate) -> RegionResponse:
        """새 지역 생성"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                region_properties_json = serialize_jsonb_data(region_data.region_properties)
                
                await conn.execute("""
                    INSERT INTO game_data.world_regions
                    (region_id, region_name, region_description, region_type, region_properties)
                    VALUES ($1, $2, $3, $4, $5)
                """,
                region_data.region_id,
                region_data.region_name,
                region_data.region_description,
                region_data.region_type,
                region_properties_json
                )
                
                # 생성된 지역 조회
                return await self.get_region(region_data.region_id)
        except Exception as e:
            logger.error(f"지역 생성 실패: {e}")
            raise
    
    async def update_region(
        self, 
        region_id: str, 
        region_data: Union[RegionUpdate, Dict[str, Any]]
    ) -> RegionResponse:
        """지역 정보 업데이트"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # 기존 데이터 조회
                existing = await self.get_region(region_id)
                if not existing:
                    raise ValueError(f"지역을 찾을 수 없습니다: {region_id}")
                
                # Dict인 경우 RegionUpdate로 변환
                if isinstance(region_data, dict):
                    region_data = RegionUpdate(**region_data)
                
                # 업데이트할 필드만 변경
                update_fields = []
                values = []
                param_index = 1
                
                if region_data.region_name is not None:
                    update_fields.append(f"region_name = ${param_index}")
                    values.append(region_data.region_name)
                    param_index += 1
                
                if region_data.region_description is not None:
                    update_fields.append(f"region_description = ${param_index}")
                    values.append(region_data.region_description)
                    param_index += 1
                
                if region_data.region_type is not None:
                    update_fields.append(f"region_type = ${param_index}")
                    values.append(region_data.region_type)
                    param_index += 1
                
                if region_data.region_properties is not None:
                    update_fields.append(f"region_properties = ${param_index}")
                    values.append(serialize_jsonb_data(region_data.region_properties))
                    param_index += 1
                
                if update_fields:
                    update_fields.append(f"updated_at = CURRENT_TIMESTAMP")
                    values.append(region_id)
                    
                    query = f"""
                        UPDATE game_data.world_regions
                        SET {', '.join(update_fields)}
                        WHERE region_id = ${param_index}
                    """
                    
                    await conn.execute(query, *values)
                
                return await self.get_region(region_id)
        except Exception as e:
            logger.error(f"지역 업데이트 실패: {e}")
            raise
    
    async def delete_region(self, region_id: str) -> bool:
        """지역 삭제"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM game_data.world_regions
                    WHERE region_id = $1
                """, region_id)
                
                return result == "DELETE 1"
        except Exception as e:
            logger.error(f"지역 삭제 실패: {e}")
            raise

