"""
핀 API 라우터
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional

from app.api.schemas import (
    PinPositionCreate, PinPositionUpdate, PinPositionResponse
)
from app.services.world_editor.pin_service import PinService

router = APIRouter()
pin_service = PinService()


@router.get("/", response_model=List[PinPositionResponse])
async def get_pins():
    """모든 핀 조회"""
    try:
        return await pin_service.get_all_pins()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pins: {str(e)}")


@router.get("/{pin_id}", response_model=PinPositionResponse)
async def get_pin(pin_id: str):
    """특정 핀 조회"""
    pin = await pin_service.get_pin(pin_id)
    if not pin:
        raise HTTPException(status_code=404, detail="Pin not found")
    return pin


@router.get("/game-data/{game_data_id}/{pin_type}", response_model=PinPositionResponse)
async def get_pin_by_game_data(game_data_id: str, pin_type: str):
    """게임 데이터 ID로 핀 조회"""
    pin = await pin_service.get_pin_by_game_data(game_data_id, pin_type)
    if not pin:
        raise HTTPException(status_code=404, detail="Pin not found")
    return pin


@router.post("/", response_model=PinPositionResponse)
async def create_pin(pin_data: PinPositionCreate):
    """새 핀 생성"""
    try:
        return await pin_service.create_pin(pin_data)
    except Exception as e:
        # Pydantic validation 에러를 더 자세히 표시
        if hasattr(e, 'errors'):
            raise HTTPException(status_code=422, detail=f"Validation error: {e.errors()}")
        raise HTTPException(status_code=500, detail=f"Failed to create pin: {str(e)}")


@router.put("/{pin_id}", response_model=PinPositionResponse)
async def update_pin(pin_id: str, pin_data: PinPositionUpdate):
    """핀 정보 업데이트"""
    return await pin_service.update_pin(pin_id, pin_data)


@router.delete("/{pin_id}")
async def delete_pin(pin_id: str):
    """핀 삭제"""
    success = await pin_service.delete_pin(pin_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pin not found")
    return {"message": "Pin deleted successfully"}

