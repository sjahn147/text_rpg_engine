"""
Effect Carriers API 라우터
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID

from app.api.schemas import (
    EffectCarrierCreate, EffectCarrierUpdate, EffectCarrierResponse
)
from app.services.world_editor.effect_carrier_service import EffectCarrierService

router = APIRouter()
effect_carrier_service = EffectCarrierService()


@router.get("/", response_model=List[EffectCarrierResponse])
async def get_effect_carriers(
    carrier_type: Optional[str] = Query(None, description="Effect Carrier 타입 필터"),
    source_entity_id: Optional[str] = Query(None, description="출처 Entity ID 필터"),
    tags: Optional[str] = Query(None, description="태그 필터 (쉼표로 구분)")
):
    """모든 Effect Carrier 조회 (필터링 가능)"""
    all_carriers = await effect_carrier_service.get_all_effect_carriers()
    
    # 필터링
    filtered = all_carriers
    if carrier_type:
        filtered = [c for c in filtered if c.carrier_type == carrier_type]
    if source_entity_id:
        filtered = [c for c in filtered if c.source_entity_id == source_entity_id]
    if tags:
        tag_list = [tag.strip() for tag in tags.split(',')]
        filtered = [c for c in filtered if any(tag in c.tags for tag in tag_list)]
    
    return filtered


@router.get("/entity/{entity_id}", response_model=List[EffectCarrierResponse])
async def get_effect_carriers_by_entity(entity_id: str):
    """특정 Entity가 소유한 모든 Effect Carrier 조회"""
    return await effect_carrier_service.get_effect_carriers_by_entity(entity_id)


@router.get("/type/{carrier_type}", response_model=List[EffectCarrierResponse])
async def get_effect_carriers_by_type(carrier_type: str):
    """특정 타입의 모든 Effect Carrier 조회"""
    return await effect_carrier_service.get_effect_carriers_by_type(carrier_type)


@router.get("/{effect_id}", response_model=EffectCarrierResponse)
async def get_effect_carrier(effect_id: UUID):
    """특정 Effect Carrier 조회"""
    carrier = await effect_carrier_service.get_effect_carrier(effect_id)
    if not carrier:
        raise HTTPException(status_code=404, detail="Effect Carrier not found")
    return carrier


@router.post("/", response_model=EffectCarrierResponse)
async def create_effect_carrier(carrier_data: EffectCarrierCreate):
    """새 Effect Carrier 생성"""
    try:
        return await effect_carrier_service.create_effect_carrier(carrier_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create effect carrier: {str(e)}")


@router.put("/{effect_id}", response_model=EffectCarrierResponse)
async def update_effect_carrier(effect_id: UUID, carrier_data: EffectCarrierUpdate):
    """Effect Carrier 정보 업데이트"""
    try:
        carrier = await effect_carrier_service.update_effect_carrier(effect_id, carrier_data)
        if not carrier:
            raise HTTPException(status_code=404, detail="Effect Carrier not found")
        return carrier
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update effect carrier: {str(e)}")


@router.delete("/{effect_id}")
async def delete_effect_carrier(effect_id: UUID):
    """Effect Carrier 삭제"""
    success = await effect_carrier_service.delete_effect_carrier(effect_id)
    if not success:
        raise HTTPException(status_code=404, detail="Effect Carrier not found")
    return {"message": "Effect Carrier deleted successfully"}

