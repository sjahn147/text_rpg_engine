"""
World Objects API 라우터
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.api.schemas import (
    WorldObjectCreate, WorldObjectUpdate, WorldObjectResponse
)
from app.services.world_editor.world_object_service import WorldObjectService

router = APIRouter()
world_object_service = WorldObjectService()


@router.get("/", response_model=List[WorldObjectResponse])
async def get_world_objects():
    """모든 World Object 조회"""
    return await world_object_service.get_all_world_objects()


@router.get("/cell/{cell_id}", response_model=List[WorldObjectResponse])
async def get_world_objects_by_cell(cell_id: str):
    """특정 Cell의 모든 World Object 조회"""
    return await world_object_service.get_world_objects_by_cell(cell_id)


@router.get("/{object_id}", response_model=WorldObjectResponse)
async def get_world_object(object_id: str):
    """특정 World Object 조회"""
    world_object = await world_object_service.get_world_object(object_id)
    if not world_object:
        raise HTTPException(status_code=404, detail="World Object not found")
    return world_object


@router.post("/", response_model=WorldObjectResponse)
async def create_world_object(world_object_data: WorldObjectCreate):
    """새 World Object 생성"""
    try:
        return await world_object_service.create_world_object(world_object_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create world object: {str(e)}")


@router.put("/{object_id}", response_model=WorldObjectResponse)
async def update_world_object(object_id: str, world_object_data: WorldObjectUpdate):
    """World Object 정보 업데이트"""
    try:
        world_object = await world_object_service.update_world_object(object_id, world_object_data)
        if not world_object:
            raise HTTPException(status_code=404, detail="World Object not found")
        return world_object
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update world object: {str(e)}")


@router.delete("/{object_id}")
async def delete_world_object(object_id: str):
    """World Object 삭제"""
    success = await world_object_service.delete_world_object(object_id)
    if not success:
        raise HTTPException(status_code=404, detail="World Object not found")
    return {"message": "World Object deleted successfully"}

