"""
Entity Behavior Schedule 서비스
"""
from typing import List, Optional, Dict, Any
import uuid
from database.connection import DatabaseConnection
from app.api.schemas import (
    EntityBehaviorScheduleCreate,
    EntityBehaviorScheduleUpdate,
    EntityBehaviorScheduleResponse
)
from common.utils.logger import logger
from common.utils.jsonb_handler import serialize_jsonb_data, parse_jsonb_data


class BehaviorScheduleService:
    """Entity Behavior Schedule 서비스"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db = db_connection or DatabaseConnection()
    
    async def get_schedules_by_entity(self, entity_id: str) -> List[EntityBehaviorScheduleResponse]:
        """특정 엔티티의 모든 행동 스케줄 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        schedule_id, entity_id, time_period, action_type,
                        action_priority, conditions, action_data,
                        created_at, updated_at
                    FROM game_data.entity_behavior_schedules
                    WHERE entity_id = $1
                    ORDER BY time_period, action_priority
                """, entity_id)
                
                schedules = []
                for row in rows:
                    conditions = parse_jsonb_data(row['conditions'])
                    action_data = parse_jsonb_data(row['action_data'])
                    
                    schedule_dict = {
                        "schedule_id": str(row['schedule_id']),
                        "entity_id": row['entity_id'],
                        "time_period": row['time_period'],
                        "action_type": row['action_type'],
                        "action_priority": row['action_priority'],
                        "conditions": conditions or {},
                        "action_data": action_data or {},
                        "created_at": row['created_at'],
                        "updated_at": row['updated_at']
                    }
                    schedules.append(EntityBehaviorScheduleResponse(**schedule_dict))
                
                return schedules
        except Exception as e:
            logger.error(f"Error getting schedules by entity: {str(e)}")
            raise
    
    async def get_schedule(self, schedule_id: str) -> Optional[EntityBehaviorScheduleResponse]:
        """특정 행동 스케줄 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT 
                        schedule_id, entity_id, time_period, action_type,
                        action_priority, conditions, action_data,
                        created_at, updated_at
                    FROM game_data.entity_behavior_schedules
                    WHERE schedule_id = $1
                """, schedule_id)
                
                if not row:
                    return None
                
                conditions = parse_jsonb_data(row['conditions'])
                action_data = parse_jsonb_data(row['action_data'])
                
                schedule_dict = {
                    "schedule_id": str(row['schedule_id']),
                    "entity_id": row['entity_id'],
                    "time_period": row['time_period'],
                    "action_type": row['action_type'],
                    "action_priority": row['action_priority'],
                    "conditions": conditions or {},
                    "action_data": action_data or {},
                    "created_at": row['created_at'],
                    "updated_at": row['updated_at']
                }
                return EntityBehaviorScheduleResponse(**schedule_dict)
        except Exception as e:
            logger.error(f"Error getting schedule: {str(e)}")
            raise
    
    async def create_schedule(self, schedule_data: EntityBehaviorScheduleCreate) -> EntityBehaviorScheduleResponse:
        """새 행동 스케줄 생성"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # schedule_id가 없으면 UUID 생성
                schedule_id = schedule_data.schedule_id or str(uuid.uuid4())
                
                conditions_json = serialize_jsonb_data(schedule_data.conditions or {})
                action_data_json = serialize_jsonb_data(schedule_data.action_data or {})
                
                await conn.execute("""
                    INSERT INTO game_data.entity_behavior_schedules
                    (schedule_id, entity_id, time_period, action_type, action_priority, conditions, action_data)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, schedule_id, schedule_data.entity_id, schedule_data.time_period,
                    schedule_data.action_type, schedule_data.action_priority,
                    conditions_json, action_data_json)
                
                # 생성된 스케줄 조회
                return await self.get_schedule(schedule_id)
        except Exception as e:
            logger.error(f"Error creating schedule: {str(e)}")
            raise
    
    async def update_schedule(self, schedule_id: str, schedule_data: EntityBehaviorScheduleUpdate) -> Optional[EntityBehaviorScheduleResponse]:
        """행동 스케줄 업데이트"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # 기존 스케줄 조회
                existing = await self.get_schedule(schedule_id)
                if not existing:
                    return None
                
                # 업데이트할 필드만 구성
                update_fields = []
                update_values = []
                param_index = 1
                
                if schedule_data.time_period is not None:
                    update_fields.append(f"time_period = ${param_index}")
                    update_values.append(schedule_data.time_period)
                    param_index += 1
                
                if schedule_data.action_type is not None:
                    update_fields.append(f"action_type = ${param_index}")
                    update_values.append(schedule_data.action_type)
                    param_index += 1
                
                if schedule_data.action_priority is not None:
                    update_fields.append(f"action_priority = ${param_index}")
                    update_values.append(schedule_data.action_priority)
                    param_index += 1
                
                if schedule_data.conditions is not None:
                    update_fields.append(f"conditions = ${param_index}")
                    update_values.append(serialize_jsonb_data(schedule_data.conditions))
                    param_index += 1
                
                if schedule_data.action_data is not None:
                    update_fields.append(f"action_data = ${param_index}")
                    update_values.append(serialize_jsonb_data(schedule_data.action_data))
                    param_index += 1
                
                if not update_fields:
                    return existing
                
                # updated_at 추가
                update_fields.append(f"updated_at = CURRENT_TIMESTAMP")
                update_values.append(schedule_id)
                
                query = f"""
                    UPDATE game_data.entity_behavior_schedules
                    SET {', '.join(update_fields)}
                    WHERE schedule_id = ${param_index}
                """
                
                await conn.execute(query, *update_values)
                
                return await self.get_schedule(schedule_id)
        except Exception as e:
            logger.error(f"Error updating schedule: {str(e)}")
            raise
    
    async def delete_schedule(self, schedule_id: str) -> bool:
        """행동 스케줄 삭제"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM game_data.entity_behavior_schedules
                    WHERE schedule_id = $1
                """, schedule_id)
                
                return result == "DELETE 1"
        except Exception as e:
            logger.error(f"Error deleting schedule: {str(e)}")
            raise

