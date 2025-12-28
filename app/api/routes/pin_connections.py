"""
핀 연결 API 라우터
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.world_editor.pin_connection_service import PinConnectionService

router = APIRouter()
connection_service = PinConnectionService()


class ConnectPinToRegionRequest(BaseModel):
    """핀-Region 연결 요청"""
    pin_id: str
    region_id: str
    create_if_not_exists: bool = False
    region_name: Optional[str] = None


class ConnectPinToLocationRequest(BaseModel):
    """핀-Location 연결 요청"""
    pin_id: str
    location_id: str
    create_if_not_exists: bool = False
    location_name: Optional[str] = None
    region_id: Optional[str] = None


class ConnectPinToCellRequest(BaseModel):
    """핀-Cell 연결 요청"""
    pin_id: str
    cell_id: str
    create_if_not_exists: bool = False
    cell_name: Optional[str] = None
    location_id: Optional[str] = None


@router.post("/connect/region")
async def connect_pin_to_region(request: ConnectPinToRegionRequest):
    """핀을 Region에 연결"""
    try:
        result = await connection_service.connect_pin_to_region(
            pin_id=request.pin_id,
            region_id=request.region_id,
            create_if_not_exists=request.create_if_not_exists,
            region_name=request.region_name
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"연결 실패: {str(e)}")


@router.post("/connect/location")
async def connect_pin_to_location(request: ConnectPinToLocationRequest):
    """핀을 Location에 연결"""
    try:
        result = await connection_service.connect_pin_to_location(
            pin_id=request.pin_id,
            location_id=request.location_id,
            create_if_not_exists=request.create_if_not_exists,
            location_name=request.location_name,
            region_id=request.region_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"연결 실패: {str(e)}")


@router.post("/connect/cell")
async def connect_pin_to_cell(request: ConnectPinToCellRequest):
    """핀을 Cell에 연결"""
    try:
        result = await connection_service.connect_pin_to_cell(
            pin_id=request.pin_id,
            cell_id=request.cell_id,
            create_if_not_exists=request.create_if_not_exists,
            cell_name=request.cell_name,
            location_id=request.location_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"연결 실패: {str(e)}")

