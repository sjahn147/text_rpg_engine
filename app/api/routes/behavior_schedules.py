"""
Entity Behavior Schedule API 라우터
"""
from fastapi import APIRouter, HTTPException
from typing import List

from app.api.schemas import (
    EntityBehaviorScheduleCreate,
    EntityBehaviorScheduleUpdate,
    EntityBehaviorScheduleResponse
)
from app.services.world_editor.behavior_schedule_service import BehaviorScheduleService

router = APIRouter()
behavior_schedule_service = BehaviorScheduleService()


@router.get("/entity/{entity_id}", response_model=List[EntityBehaviorScheduleResponse])
async def get_schedules_by_entity(entity_id: str):
    """특정 엔티티의 모든 행동 스케줄 조회"""
    try:
        return await behavior_schedule_service.get_schedules_by_entity(entity_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting schedules: {str(e)}")


@router.get("/{schedule_id}", response_model=EntityBehaviorScheduleResponse)
async def get_schedule(schedule_id: str):
    """특정 행동 스케줄 조회"""
    try:
        schedule = await behavior_schedule_service.get_schedule(schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return schedule
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting schedule: {str(e)}")


@router.post("/", response_model=EntityBehaviorScheduleResponse)
async def create_schedule(schedule_data: EntityBehaviorScheduleCreate):
    """새 행동 스케줄 생성"""
    try:
        return await behavior_schedule_service.create_schedule(schedule_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating schedule: {str(e)}")


@router.put("/{schedule_id}", response_model=EntityBehaviorScheduleResponse)
async def update_schedule(schedule_id: str, schedule_data: EntityBehaviorScheduleUpdate):
    """행동 스케줄 업데이트"""
    try:
        schedule = await behavior_schedule_service.update_schedule(schedule_id, schedule_data)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return schedule
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating schedule: {str(e)}")


@router.delete("/{schedule_id}")
async def delete_schedule(schedule_id: str):
    """행동 스케줄 삭제"""
    try:
        success = await behavior_schedule_service.delete_schedule(schedule_id)
        if not success:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return {"message": "Schedule deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting schedule: {str(e)}")

