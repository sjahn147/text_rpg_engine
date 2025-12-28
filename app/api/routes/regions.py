"""
지역 API 라우터
"""
from fastapi import APIRouter, HTTPException
from typing import List

from app.api.schemas import (
    RegionCreate, RegionUpdate, RegionResponse
)
from app.services.world_editor.region_service import RegionService

router = APIRouter()
region_service = RegionService()


@router.get("/", response_model=List[RegionResponse])
async def get_regions():
    """모든 지역 조회"""
    try:
        return await region_service.get_all_regions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get regions: {str(e)}")


@router.get("/{region_id}", response_model=RegionResponse)
async def get_region(region_id: str):
    """특정 지역 조회"""
    region = await region_service.get_region(region_id)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    return region


@router.post("/", response_model=RegionResponse)
async def create_region(region_data: RegionCreate):
    """새 지역 생성"""
    return await region_service.create_region(region_data)


@router.put("/{region_id}", response_model=RegionResponse)
async def update_region(region_id: str, region_data: RegionUpdate):
    """지역 정보 업데이트"""
    return await region_service.update_region(region_id, region_data)


@router.delete("/{region_id}")
async def delete_region(region_id: str):
    """지역 삭제"""
    success = await region_service.delete_region(region_id)
    if not success:
        raise HTTPException(status_code=404, detail="Region not found")
    return {"message": "Region deleted successfully"}

