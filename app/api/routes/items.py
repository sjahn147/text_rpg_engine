"""
Items API 라우터
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.api.schemas import (
    ItemCreate, ItemUpdate, ItemResponse
)
from app.services.world_editor.item_service import ItemService

router = APIRouter()
item_service = ItemService()


@router.get("/", response_model=List[ItemResponse])
async def get_items(
    item_type: Optional[str] = Query(None, description="아이템 타입 필터")
):
    """모든 Item 조회 (필터링 가능)"""
    if item_type:
        return await item_service.get_items_by_type(item_type)
    return await item_service.get_all_items()


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str):
    """특정 Item 조회"""
    item = await item_service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/", response_model=ItemResponse)
async def create_item(item_data: ItemCreate):
    """새 Item 생성"""
    try:
        return await item_service.create_item(item_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create item: {str(e)}")


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: str, item_data: ItemUpdate):
    """Item 정보 업데이트"""
    try:
        item = await item_service.update_item(item_id, item_data)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update item: {str(e)}")


@router.delete("/{item_id}")
async def delete_item(item_id: str):
    """Item 삭제"""
    success = await item_service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}

