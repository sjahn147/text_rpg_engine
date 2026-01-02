"""
엔티티(NPC) API 라우터
"""
from fastapi import APIRouter, HTTPException
from typing import List

from app.api.schemas import (
    EntityCreate, EntityUpdate, EntityResponse
)
from app.services.world_editor.entity_service import EntityService
from app.services.world_editor.id_generator import IDGenerator

router = APIRouter()
entity_service = EntityService()


@router.get("/", response_model=List[EntityResponse])
async def get_entities():
    """모든 엔티티 조회"""
    try:
        return await entity_service.get_all_entities()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get entities: {str(e)}")


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
    # ID가 제공된 경우 규칙 검증
    if entity_data.entity_id:
        is_valid, error_msg = IDGenerator.validate_id('entity', entity_data.entity_id)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid entity_id format: {error_msg}"
            )
    else:
        # ID가 없으면 자동 생성
        id_generator = IDGenerator()
        entity_data.entity_id = await id_generator.generate_entity_id(
            entity_data.entity_type,
            entity_data.entity_name
        )
    
    return await entity_service.create_entity(entity_data)


@router.put("/{entity_id}", response_model=EntityResponse)
async def update_entity(entity_id: str, entity_data: EntityUpdate):
    """엔티티 정보 업데이트"""
    # 엔티티 ID 규칙 검증
    is_valid, error_msg = IDGenerator.validate_id('entity', entity_id)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid entity_id format: {error_msg}"
        )
    
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

