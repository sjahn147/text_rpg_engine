"""
Location/Cell 관리 API - ID 생성 및 편집용
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel

from app.services.world_editor.location_service import LocationService
from app.services.world_editor.cell_service import CellService
from app.services.world_editor.entity_service import EntityService
from app.services.world_editor.id_generator import IDGenerator
from app.api.schemas import (
    LocationCreate, LocationUpdate, LocationResponse,
    CellCreate, CellUpdate, CellResponse,
    EntityCreate, EntityResponse
)

router = APIRouter()
location_service = LocationService()
cell_service = CellService()
entity_service = EntityService()
id_generator = IDGenerator()


class LocationCreateRequest(BaseModel):
    """Location 생성 요청"""
    region_id: str
    location_name: str
    location_type: Optional[str] = None
    location_description: Optional[str] = None


class CellCreateRequest(BaseModel):
    """Cell 생성 요청"""
    location_id: str
    cell_name: str
    matrix_width: int = 10
    matrix_height: int = 10
    cell_description: Optional[str] = None


class EntityCreateRequest(BaseModel):
    """Entity 생성 요청"""
    cell_id: str
    entity_name: str
    entity_type: str = "npc"
    entity_description: Optional[str] = None


@router.post("/locations/create", response_model=LocationResponse)
async def create_location_with_auto_id(request: LocationCreateRequest):
    """Location 생성 (ID 자동 생성)"""
    try:
        # ID 생성
        location_id = await id_generator.generate_location_id(
            request.region_id,
            request.location_name
        )
        
        # Location 생성
        location_data = LocationCreate(
            location_id=location_id,
            region_id=request.region_id,
            location_name=request.location_name,
            location_type=request.location_type,
            location_description=request.location_description,
            location_properties={}
        )
        
        return await location_service.create_location(location_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/locations/{location_id}/with-cells", response_model=dict)
async def get_location_with_cells(location_id: str):
    """Location과 하위 Cells를 함께 조회"""
    location = await location_service.get_location(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    cells = await cell_service.get_cells_by_location(location_id)
    
    return {
        "location": location,
        "cells": cells
    }


@router.post("/cells/create", response_model=CellResponse)
async def create_cell_with_auto_id(request: CellCreateRequest):
    """Cell 생성 (ID 자동 생성)"""
    try:
        # ID 생성
        cell_id = await id_generator.generate_cell_id(
            request.location_id,
            request.cell_name
        )
        
        # Cell 생성
        cell_data = CellCreate(
            cell_id=cell_id,
            location_id=request.location_id,
            cell_name=request.cell_name,
            matrix_width=request.matrix_width,
            matrix_height=request.matrix_height,
            cell_description=request.cell_description,
            cell_properties={}
        )
        
        return await cell_service.create_cell(cell_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/cells/{cell_id}/full", response_model=dict)
async def get_cell_with_location(cell_id: str):
    """Cell과 상위 Location을 함께 조회"""
    cell = await cell_service.get_cell(cell_id)
    if not cell:
        raise HTTPException(status_code=404, detail="Cell not found")
    
    location = await location_service.get_location(cell.location_id)
    
    return {
        "cell": cell,
        "location": location
    }


@router.post("/entities/create", response_model=EntityResponse)
async def create_entity_with_auto_id(request: EntityCreateRequest):
    """Entity 생성 (ID 자동 생성)"""
    try:
        # Cell 존재 확인
        cell = await cell_service.get_cell(request.cell_id)
        if not cell:
            raise HTTPException(status_code=404, detail="Cell not found")
        
        # ID 생성
        entity_id = await id_generator.generate_entity_id(
            request.entity_type,
            request.entity_name
        )
        
        # Entity 생성
        entity_data = EntityCreate(
            entity_id=entity_id,
            entity_type=request.entity_type,
            entity_name=request.entity_name,
            entity_description=request.entity_description,
            base_stats={},
            default_equipment={},
            default_abilities={},
            default_inventory={},
            entity_properties={
                "cell_id": request.cell_id,
                "location_id": cell.location_id
            }
        )
        
        return await entity_service.create_entity(entity_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

