"""
Dialogue Knowledge (대화 지식) API 라우터
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.services.world_editor.dialogue_knowledge_service import DialogueKnowledgeService

router = APIRouter()
knowledge_service = DialogueKnowledgeService()


class DialogueKnowledgeCreate(BaseModel):
    """Dialogue Knowledge 생성 스키마"""
    knowledge_id: str = Field(..., description="Knowledge ID")
    title: str = Field(..., description="제목")
    content: str = Field(..., description="내용")
    knowledge_type: str = Field(..., description="지식 타입 (lore, quest, location, character, etc.)")
    related_entities: Optional[Dict[str, Any]] = Field(None, description="관련 엔티티")
    related_topics: Optional[Dict[str, Any]] = Field(None, description="관련 주제")
    knowledge_properties: Optional[Dict[str, Any]] = Field(None, description="지식 속성")


class DialogueKnowledgeUpdate(BaseModel):
    """Dialogue Knowledge 업데이트 스키마"""
    title: Optional[str] = None
    content: Optional[str] = None
    knowledge_type: Optional[str] = None
    related_entities: Optional[Dict[str, Any]] = None
    related_topics: Optional[Dict[str, Any]] = None
    knowledge_properties: Optional[Dict[str, Any]] = None


@router.get("/knowledge")
async def get_all_knowledge():
    """모든 Dialogue Knowledge 조회"""
    try:
        knowledge_list = await knowledge_service.get_all_knowledge()
        return knowledge_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dialogue Knowledge 조회 실패: {str(e)}")


@router.get("/knowledge/{knowledge_id}")
async def get_knowledge(knowledge_id: str):
    """특정 Dialogue Knowledge 조회"""
    try:
        knowledge = await knowledge_service.get_knowledge(knowledge_id)
        if not knowledge:
            raise HTTPException(status_code=404, detail="Dialogue Knowledge not found")
        return knowledge
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dialogue Knowledge 조회 실패: {str(e)}")


@router.get("/knowledge/type/{knowledge_type}")
async def get_knowledge_by_type(knowledge_type: str):
    """특정 타입의 Dialogue Knowledge 조회"""
    try:
        knowledge_list = await knowledge_service.get_knowledge_by_type(knowledge_type)
        return knowledge_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"타입별 Dialogue Knowledge 조회 실패: {str(e)}")


@router.post("/knowledge", status_code=201)
async def create_knowledge(knowledge_data: DialogueKnowledgeCreate):
    """Dialogue Knowledge 생성"""
    try:
        knowledge_id = await knowledge_service.create_knowledge(
            knowledge_id=knowledge_data.knowledge_id,
            title=knowledge_data.title,
            content=knowledge_data.content,
            knowledge_type=knowledge_data.knowledge_type,
            related_entities=knowledge_data.related_entities,
            related_topics=knowledge_data.related_topics,
            knowledge_properties=knowledge_data.knowledge_properties
        )
        return await knowledge_service.get_knowledge(knowledge_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dialogue Knowledge 생성 실패: {str(e)}")


@router.put("/knowledge/{knowledge_id}")
async def update_knowledge(knowledge_id: str, knowledge_data: DialogueKnowledgeUpdate):
    """Dialogue Knowledge 업데이트"""
    try:
        knowledge = await knowledge_service.update_knowledge(
            knowledge_id=knowledge_id,
            title=knowledge_data.title,
            content=knowledge_data.content,
            knowledge_type=knowledge_data.knowledge_type,
            related_entities=knowledge_data.related_entities,
            related_topics=knowledge_data.related_topics,
            knowledge_properties=knowledge_data.knowledge_properties
        )
        if not knowledge:
            raise HTTPException(status_code=404, detail="Dialogue Knowledge not found")
        return knowledge
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dialogue Knowledge 업데이트 실패: {str(e)}")


@router.delete("/knowledge/{knowledge_id}")
async def delete_knowledge(knowledge_id: str):
    """Dialogue Knowledge 삭제"""
    try:
        success = await knowledge_service.delete_knowledge(knowledge_id)
        if not success:
            raise HTTPException(status_code=404, detail="Dialogue Knowledge not found")
        return {"message": "Dialogue Knowledge deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dialogue Knowledge 삭제 실패: {str(e)}")

