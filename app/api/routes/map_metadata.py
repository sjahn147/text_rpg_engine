"""
지도 메타데이터 API 라우터
"""
from fastapi import APIRouter, HTTPException

from app.api.schemas import (
    MapMetadataCreate, MapMetadataUpdate, MapMetadataResponse
)
from app.services.world_editor.map_service import MapService

router = APIRouter()
map_service = MapService()


@router.get("/{map_id}", response_model=MapMetadataResponse)
async def get_map(map_id: str = "default_map"):
    """지도 메타데이터 조회"""
    try:
        map_data = await map_service.get_map(map_id)
        if not map_data:
            raise HTTPException(status_code=404, detail="Map not found")
        return map_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get map: {str(e)}")


@router.post("/", response_model=MapMetadataResponse)
async def create_map(map_data: MapMetadataCreate):
    """새 지도 메타데이터 생성"""
    return await map_service.create_map(map_data)


@router.put("/{map_id}", response_model=MapMetadataResponse)
async def update_map(map_id: str, map_data: MapMetadataUpdate):
    """지도 메타데이터 업데이트"""
    return await map_service.update_map(map_id, map_data)

