"""
엔티티(NPC) API 라우터
"""
from fastapi import APIRouter, HTTPException
from typing import List

from app.api.schemas import (
    EntityCreate, EntityUpdate, EntityResponse
)
from app.services.world_editor.entity_service import EntityService

router = APIRouter()
entity_service = EntityService()


@router.get("/cell/{cell_id}", response_model=List[EntityResponse])
async def get_entities_by_cell(cell_id: str):
    """특정 셀의 모든 엔티티 조회"""
    return await entity_service.get_entities_by_cell(cell_id)


@router.get("/location/{location_id}", response_model=List[EntityResponse])
async def get_entities_by_location(location_id: str):
    """특정 위치의 모든 엔티티 조회"""
    return await entity_service.get_entities_by_location(location_id)


@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(entity_id: str):
    """특정 엔티티 조회"""
    entity = await entity_service.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@router.post("/", response_model=EntityResponse)
async def create_entity(entity_data: EntityCreate):
    """새 엔티티 생성"""
    return await entity_service.create_entity(entity_data)


@router.put("/{entity_id}", response_model=EntityResponse)
async def update_entity(entity_id: str, entity_data: EntityUpdate):
    """엔티티 정보 업데이트"""
    return await entity_service.update_entity(entity_id, entity_data)


@router.delete("/{entity_id}")
async def delete_entity(entity_id: str):
    """엔티티 삭제 (참조 무결성 검증 포함)"""
    try:
        success = await entity_service.delete_entity(entity_id)
        if not success:
            raise HTTPException(status_code=404, detail="Entity not found")
        return {"message": "Entity deleted successfully"}
    except ValueError as e:
        # 참조 무결성 에러는 400 Bad Request로 반환
        raise HTTPException(status_code=400, detail=str(e))

