"""
위치 API 라우터
"""
from fastapi import APIRouter, HTTPException
from typing import List

from app.api.schemas import (
    LocationCreate, LocationUpdate, LocationResponse, LocationResolvedResponse
)
from app.services.world_editor.location_service import LocationService
from app.services.world_editor.id_generator import IDGenerator

router = APIRouter()
location_service = LocationService()


@router.get("/", response_model=List[LocationResponse])
async def get_locations():
    """모든 위치 조회"""
    try:
        return await location_service.get_all_locations()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get locations: {str(e)}")


@router.get("/region/{region_id}", response_model=List[LocationResponse])
async def get_locations_by_region(region_id: str):
    """특정 지역의 모든 위치 조회"""
    try:
        return await location_service.get_locations_by_region(region_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get locations by region: {str(e)}")


@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(location_id: str):
    """특정 위치 조회"""
    location = await location_service.get_location(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


@router.post("/", response_model=LocationResponse)
async def create_location(location_data: LocationCreate):
    """새 위치 생성"""
    # ID가 제공된 경우 규칙 검증
    if location_data.location_id:
        is_valid, error_msg = IDGenerator.validate_id('location', location_data.location_id)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid location_id format: {error_msg}"
            )
    else:
        # ID가 없으면 자동 생성
        id_generator = IDGenerator()
        location_data.location_id = await id_generator.generate_location_id(
            location_data.region_id,
            location_data.location_name
        )
    
    return await location_service.create_location(location_data)


@router.put("/{location_id}", response_model=LocationResponse)
async def update_location(location_id: str, location_data: LocationUpdate):
    """위치 정보 업데이트"""
    # 위치 ID 규칙 검증
    is_valid, error_msg = IDGenerator.validate_id('location', location_id)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid location_id format: {error_msg}"
        )
    
    return await location_service.update_location(location_id, location_data)


@router.get("/{location_id}/resolved", response_model=LocationResolvedResponse)
async def get_location_resolved(location_id: str):
    """모든 참조를 해결한 위치 조회 (Phase 4)"""
    location = await location_service.get_location_resolved(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


@router.delete("/{location_id}")
async def delete_location(location_id: str):
    """위치 삭제"""
    success = await location_service.delete_location(location_id)
    if not success:
        raise HTTPException(status_code=404, detail="Location not found")
    return {"message": "Location deleted successfully"}

