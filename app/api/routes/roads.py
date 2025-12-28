"""
도로 API 라우터
"""
from fastapi import APIRouter, HTTPException
from typing import List

from app.api.schemas import (
    RoadCreate, RoadUpdate, RoadResponse
)
from app.services.world_editor.road_service import RoadService

router = APIRouter()
road_service = RoadService()


@router.get("/", response_model=List[RoadResponse])
async def get_roads():
    """모든 도로 조회"""
    try:
        return await road_service.get_all_roads()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get roads: {str(e)}")


@router.get("/{road_id}", response_model=RoadResponse)
async def get_road(road_id: str):
    """특정 도로 조회"""
    road = await road_service.get_road(road_id)
    if not road:
        raise HTTPException(status_code=404, detail="Road not found")
    return road


@router.post("/", response_model=RoadResponse)
async def create_road(road_data: RoadCreate):
    """새 도로 생성"""
    return await road_service.create_road(road_data)


@router.put("/{road_id}", response_model=RoadResponse)
async def update_road(road_id: str, road_data: RoadUpdate):
    """도로 정보 업데이트"""
    return await road_service.update_road(road_id, road_data)


@router.delete("/{road_id}")
async def delete_road(road_id: str):
    """도로 삭제"""
    success = await road_service.delete_road(road_id)
    if not success:
        raise HTTPException(status_code=404, detail="Road not found")
    return {"message": "Road deleted successfully"}

