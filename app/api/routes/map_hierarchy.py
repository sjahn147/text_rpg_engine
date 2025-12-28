"""
계층적 맵 구조 API 라우터

Region Map, Location Map 등 계층적 맵 구조를 관리하는 API
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel

from app.services.world_editor.map_hierarchy_service import MapHierarchyService

router = APIRouter()
map_hierarchy_service = MapHierarchyService()


class PositionUpdate(BaseModel):
    """위치 업데이트 요청"""
    x: float
    y: float


class MapMetadataUpdate(BaseModel):
    """맵 메타데이터 업데이트 요청"""
    map_name: str = None
    background_image: str = None
    background_color: str = None
    width: int = None
    height: int = None
    grid_enabled: bool = None
    grid_size: int = None
    zoom_level: float = None
    viewport_x: int = None
    viewport_y: int = None


# =====================================================
# Region Map API
# =====================================================

@router.get("/region/{region_id}")
async def get_region_map(region_id: str) -> Dict[str, Any]:
    """Region Map 메타데이터 조회"""
    try:
        map_data = await map_hierarchy_service.get_region_map(region_id)
        if not map_data:
            raise HTTPException(status_code=404, detail=f"Region {region_id} not found")
        return map_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/region/{region_id}/locations")
async def get_region_locations(region_id: str) -> List[Dict[str, Any]]:
    """Region 내 Location 목록 조회 (위치 정보 포함)"""
    try:
        locations = await map_hierarchy_service.get_region_locations(region_id)
        return locations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/region/{region_id}/locations/{location_id}/position")
async def place_location_in_region(
    region_id: str,
    location_id: str,
    position: PositionUpdate
) -> Dict[str, Any]:
    """Region Map에 Location 배치"""
    try:
        result = await map_hierarchy_service.place_location_in_region(
            region_id,
            location_id,
            {"x": position.x, "y": position.y}
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/region/{region_id}/locations/{location_id}/position")
async def update_location_position(
    region_id: str,
    location_id: str,
    position: PositionUpdate
) -> Dict[str, Any]:
    """Location 위치 업데이트"""
    try:
        result = await map_hierarchy_service.place_location_in_region(
            region_id,
            location_id,
            {"x": position.x, "y": position.y}
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/region/{region_id}/metadata")
async def update_region_map_metadata(
    region_id: str,
    metadata: MapMetadataUpdate
) -> Dict[str, Any]:
    """Region Map 메타데이터 업데이트"""
    try:
        metadata_dict = metadata.dict(exclude_unset=True)
        result = await map_hierarchy_service.update_map_metadata(
            'region',
            region_id,
            'region',
            metadata_dict
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# Location Map API
# =====================================================

@router.get("/location/{location_id}")
async def get_location_map(location_id: str) -> Dict[str, Any]:
    """Location Map 메타데이터 조회"""
    try:
        map_data = await map_hierarchy_service.get_location_map(location_id)
        if not map_data:
            raise HTTPException(status_code=404, detail=f"Location {location_id} not found")
        return map_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/location/{location_id}/cells")
async def get_location_cells(location_id: str) -> List[Dict[str, Any]]:
    """Location 내 Cell 목록 조회 (위치 정보 포함)"""
    try:
        cells = await map_hierarchy_service.get_location_cells(location_id)
        return cells
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/location/{location_id}/cells/{cell_id}/position")
async def place_cell_in_location(
    location_id: str,
    cell_id: str,
    position: PositionUpdate
) -> Dict[str, Any]:
    """Location Map에 Cell 배치"""
    try:
        result = await map_hierarchy_service.place_cell_in_location(
            location_id,
            cell_id,
            {"x": position.x, "y": position.y}
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/location/{location_id}/cells/{cell_id}/position")
async def update_cell_position(
    location_id: str,
    cell_id: str,
    position: PositionUpdate
) -> Dict[str, Any]:
    """Cell 위치 업데이트"""
    try:
        result = await map_hierarchy_service.place_cell_in_location(
            location_id,
            cell_id,
            {"x": position.x, "y": position.y}
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/location/{location_id}/metadata")
async def update_location_map_metadata(
    location_id: str,
    metadata: MapMetadataUpdate
) -> Dict[str, Any]:
    """Location Map 메타데이터 업데이트"""
    try:
        metadata_dict = metadata.dict(exclude_unset=True)
        result = await map_hierarchy_service.update_map_metadata(
            'location',
            location_id,
            'location',
            metadata_dict
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

