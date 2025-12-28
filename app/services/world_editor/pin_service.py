"""
핀 서비스
"""
from typing import List, Optional, Dict, Any, Union
import uuid

from database.connection import DatabaseConnection
from app.api.schemas import (
    PinPositionCreate, PinPositionUpdate, PinPositionResponse
)
from common.utils.logger import logger


class PinService:
    """핀 서비스"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db = db_connection or DatabaseConnection()
    
    async def get_all_pins(self) -> List[PinPositionResponse]:
        """모든 핀 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        pin_id, pin_name, game_data_id, pin_type, x, y,
                        icon_type, color, size, created_at, updated_at
                    FROM game_data.pin_positions
                    ORDER BY pin_type, game_data_id
                """)
                
                pins = []
                for row in rows:
                    pins.append(PinPositionResponse(
                        pin_id=row['pin_id'],
                        pin_name=row.get('pin_name', f"새 핀 {row['pin_id'][-4:]}"),
                        game_data_id=row['game_data_id'],
                        pin_type=row['pin_type'],
                        x=row['x'],
                        y=row['y'],
                        icon_type=row['icon_type'],
                        color=row['color'],
                        size=row['size'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))
                
                return pins
        except Exception as e:
            logger.error(f"핀 조회 실패: {e}")
            raise
    
    async def get_pin(self, pin_id: str) -> Optional[PinPositionResponse]:
        """특정 핀 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT 
                        pin_id, pin_name, game_data_id, pin_type, x, y,
                        icon_type, color, size, created_at, updated_at
                    FROM game_data.pin_positions
                    WHERE pin_id = $1
                """, pin_id)
                
                if not row:
                    return None
                
                return PinPositionResponse(
                    pin_id=row['pin_id'],
                    pin_name=row.get('pin_name', f"새 핀 {row['pin_id'][-4:]}"),
                    game_data_id=row['game_data_id'],
                    pin_type=row['pin_type'],
                    x=row['x'],
                    y=row['y'],
                    icon_type=row['icon_type'],
                    color=row['color'],
                    size=row['size'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
        except Exception as e:
            logger.error(f"핀 조회 실패: {e}")
            raise
    
    async def get_pin_by_game_data(
        self, 
        game_data_id: str, 
        pin_type: str
    ) -> Optional[PinPositionResponse]:
        """게임 데이터 ID로 핀 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT 
                        pin_id, pin_name, game_data_id, pin_type, x, y,
                        icon_type, color, size, created_at, updated_at
                    FROM game_data.pin_positions
                    WHERE game_data_id = $1 AND pin_type = $2
                """, game_data_id, pin_type)
                
                if not row:
                    return None
                
                return PinPositionResponse(
                    pin_id=row['pin_id'],
                    pin_name=row.get('pin_name', f"새 핀 {row['pin_id'][-4:]}"),
                    game_data_id=row['game_data_id'],
                    pin_type=row['pin_type'],
                    x=row['x'],
                    y=row['y'],
                    icon_type=row['icon_type'],
                    color=row['color'],
                    size=row['size'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
        except Exception as e:
            logger.error(f"핀 조회 실패: {e}")
            raise
    
    async def create_pin(self, pin_data: PinPositionCreate) -> PinPositionResponse:
        """새 핀 생성"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                pin_id = pin_data.pin_id or f"PIN_{uuid.uuid4().hex[:8].upper()}"
                
                pin_name = getattr(pin_data, 'pin_name', None) or f"새 핀 {pin_id[-4:]}"
                
                await conn.execute("""
                    INSERT INTO game_data.pin_positions
                    (pin_id, pin_name, game_data_id, pin_type, x, y, icon_type, color, size)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT (game_data_id, pin_type) 
                    DO UPDATE SET
                        pin_name = COALESCE(EXCLUDED.pin_name, pin_positions.pin_name),
                        x = EXCLUDED.x,
                        y = EXCLUDED.y,
                        icon_type = EXCLUDED.icon_type,
                        color = EXCLUDED.color,
                        size = EXCLUDED.size,
                        updated_at = CURRENT_TIMESTAMP
                """,
                pin_id,
                pin_name,
                pin_data.game_data_id,
                pin_data.pin_type,
                pin_data.x,
                pin_data.y,
                pin_data.icon_type,
                pin_data.color,
                pin_data.size
                )
                
                # 생성된 핀 조회 (ON CONFLICT로 인해 기존 핀일 수 있음)
                result = await self.get_pin_by_game_data(
                    pin_data.game_data_id, 
                    pin_data.pin_type
                )
                if not result:
                    result = await self.get_pin(pin_id)
                
                return result
        except Exception as e:
            logger.error(f"핀 생성 실패: {e}")
            raise
    
    async def update_pin(
        self, 
        pin_id: str, 
        pin_data: PinPositionUpdate
    ) -> PinPositionResponse:
        """핀 정보 업데이트"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                existing = await self.get_pin(pin_id)
                if not existing:
                    raise ValueError(f"핀을 찾을 수 없습니다: {pin_id}")
                
                # Dict인 경우 PinPositionUpdate로 변환
                if isinstance(pin_data, dict):
                    pin_data = PinPositionUpdate(**pin_data)
                
                update_fields = []
                values = []
                param_index = 1
                
                if pin_data.x is not None:
                    update_fields.append(f"x = ${param_index}")
                    values.append(pin_data.x)
                    param_index += 1
                
                if pin_data.y is not None:
                    update_fields.append(f"y = ${param_index}")
                    values.append(pin_data.y)
                    param_index += 1
                
                if pin_data.icon_type is not None:
                    update_fields.append(f"icon_type = ${param_index}")
                    values.append(pin_data.icon_type)
                    param_index += 1
                
                if pin_data.color is not None:
                    update_fields.append(f"color = ${param_index}")
                    values.append(pin_data.color)
                    param_index += 1
                
                if pin_data.size is not None:
                    update_fields.append(f"size = ${param_index}")
                    values.append(pin_data.size)
                    param_index += 1
                
                if pin_data.pin_name is not None:
                    update_fields.append(f"pin_name = ${param_index}")
                    values.append(pin_data.pin_name)
                    param_index += 1
                
                if update_fields:
                    update_fields.append(f"updated_at = CURRENT_TIMESTAMP")
                    values.append(pin_id)
                    
                    query = f"""
                        UPDATE game_data.pin_positions
                        SET {', '.join(update_fields)}
                        WHERE pin_id = ${param_index}
                    """
                    
                    await conn.execute(query, *values)
                
                return await self.get_pin(pin_id)
        except Exception as e:
            logger.error(f"핀 업데이트 실패: {e}")
            raise
    
    async def delete_pin(self, pin_id: str) -> bool:
        """핀 삭제"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM game_data.pin_positions
                    WHERE pin_id = $1
                """, pin_id)
                
                return result == "DELETE 1"
        except Exception as e:
            logger.error(f"핀 삭제 실패: {e}")
            raise

