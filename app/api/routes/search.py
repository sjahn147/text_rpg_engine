"""
통합 검색 API 라우터
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.api.schemas import SearchResponse
from app.services.world_editor.search_service import SearchService

router = APIRouter()
search_service = SearchService()


@router.get("/", response_model=SearchResponse)
async def search(
    q: str = Query(..., description="검색어"),
    type: Optional[List[str]] = Query(None, description="엔티티 타입 필터 (region, location, cell, entity, world_object, effect_carrier, item)")
):
    """통합 검색"""
    if not q or len(q.strip()) < 1:
        raise HTTPException(status_code=400, detail="검색어는 최소 1자 이상이어야 합니다.")
    
    try:
        return await search_service.search(q.strip(), entity_types=type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 실패: {str(e)}")

