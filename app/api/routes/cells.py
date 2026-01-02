"""
셀 API 라우터
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel

from app.api.schemas import (
    CellCreate, CellUpdate, CellResponse, CellResolvedResponse
)
from app.services.world_editor.cell_service import CellService
from app.services.world_editor.id_generator import IDGenerator

router = APIRouter()
cell_service = CellService()


@router.get("/", response_model=List[CellResponse])
async def get_cells():
    """모든 셀 조회"""
    try:
        return await cell_service.get_all_cells()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cells: {str(e)}")


@router.get("/location/{location_id}", response_model=List[CellResponse])
async def get_cells_by_location(location_id: str):
    """특정 위치의 모든 셀 조회"""
    try:
        return await cell_service.get_cells_by_location(location_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cells by location: {str(e)}")


@router.get("/{cell_id}", response_model=CellResponse)
async def get_cell(cell_id: str):
    """특정 셀 조회"""
    cell = await cell_service.get_cell(cell_id)
    if not cell:
        raise HTTPException(status_code=404, detail="Cell not found")
    return cell


@router.post("/", response_model=CellResponse)
async def create_cell(cell_data: CellCreate):
    """새 셀 생성"""
    # ID가 제공된 경우 규칙 검증
    if cell_data.cell_id:
        is_valid, error_msg = IDGenerator.validate_id('cell', cell_data.cell_id)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid cell_id format: {error_msg}"
            )
    else:
        # ID가 없으면 자동 생성
        id_generator = IDGenerator()
        cell_data.cell_id = await id_generator.generate_cell_id(
            cell_data.location_id,
            cell_data.cell_name or "UNNAMED"
        )
    
    return await cell_service.create_cell(cell_data)


@router.put("/{cell_id}", response_model=CellResponse)
async def update_cell(cell_id: str, cell_data: CellUpdate):
    """셀 정보 업데이트"""
    # 셀 ID 규칙 검증
    is_valid, error_msg = IDGenerator.validate_id('cell', cell_id)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid cell_id format: {error_msg}"
        )
    
    return await cell_service.update_cell(cell_id, cell_data)


@router.get("/{cell_id}/resolved", response_model=CellResolvedResponse)
async def get_cell_resolved(cell_id: str):
    """모든 참조를 해결한 셀 조회 (Phase 4)"""
    cell = await cell_service.get_cell_resolved(cell_id)
    if not cell:
        raise HTTPException(status_code=404, detail="Cell not found")
    return cell


@router.delete("/{cell_id}")
async def delete_cell(cell_id: str):
    """셀 삭제 (참조 무결성 검증 포함)"""
    try:
        success = await cell_service.delete_cell(cell_id)
        if not success:
            raise HTTPException(status_code=404, detail="Cell not found")
        return {"message": "Cell deleted successfully"}
    except ValueError as e:
        # 참조 무결성 에러는 400 Bad Request로 반환
        raise HTTPException(status_code=400, detail=str(e))


# Cell Properties API
class CellPropertiesUpdate(BaseModel):
    """셀 Properties 업데이트 스키마"""
    properties: Dict[str, Any]


@router.get("/{cell_id}/properties")
async def get_cell_properties(cell_id: str):
    """셀의 Properties 조회"""
    cell = await cell_service.get_cell(cell_id)
    if not cell:
        raise HTTPException(status_code=404, detail="Cell not found")
    return {
        "cell_id": cell.cell_id,
        "properties": cell.cell_properties or {}
    }


@router.put("/{cell_id}/properties")
async def update_cell_properties(cell_id: str, properties_data: CellPropertiesUpdate):
    """셀의 Properties 업데이트"""
    try:
        # 기존 셀 정보 가져오기
        existing = await cell_service.get_cell(cell_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Cell not found")
        
        # Properties만 업데이트
        updated_cell = await cell_service.update_cell(cell_id, {
            "cell_properties": properties_data.properties
        })
        
        return {
            "cell_id": updated_cell.cell_id,
            "properties": updated_cell.cell_properties or {},
            "updated_at": updated_cell.updated_at
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Properties 업데이트 실패: {str(e)}")

