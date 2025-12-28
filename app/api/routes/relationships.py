"""
관계 조회 API 라우터
"""
from fastapi import APIRouter, HTTPException

from app.api.schemas import RelationshipsResponse
from app.services.world_editor.relationship_service import RelationshipService

router = APIRouter()
relationship_service = RelationshipService()


@router.get("/{entity_type}/{entity_id}", response_model=RelationshipsResponse)
async def get_relationships(entity_type: str, entity_id: str):
    """엔티티의 모든 관계 조회"""
    valid_types = ['region', 'location', 'cell', 'entity', 'world_object', 'effect_carrier']
    if entity_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid entity type. Must be one of: {valid_types}")
    
    try:
        relationships = await relationship_service.get_relationships(entity_type, entity_id)
        if not relationships:
            raise HTTPException(status_code=404, detail="Entity not found")
        return relationships
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"관계 조회 실패: {str(e)}")

