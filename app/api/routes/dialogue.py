"""
Dialogue (대화) API 라우터
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.services.world_editor.dialogue_service import DialogueService

router = APIRouter()
dialogue_service = DialogueService()


class DialogueContextCreate(BaseModel):
    """Dialogue Context 생성 스키마"""
    dialogue_id: str = Field(..., description="Dialogue Context ID")
    title: str = Field(..., description="제목")
    content: str = Field(..., description="내용")
    entity_id: Optional[str] = Field(None, description="Entity ID")
    cell_id: Optional[str] = Field(None, description="Cell ID")
    time_category: Optional[str] = Field(None, description="시간 카테고리")
    event_id: Optional[str] = Field(None, description="이벤트 ID")
    priority: int = Field(0, description="우선순위")
    available_topics: Optional[Dict[str, Any]] = Field(None, description="사용 가능한 주제들")
    entity_personality: Optional[str] = Field(None, description="Entity 성격")
    constraints: Optional[Dict[str, Any]] = Field(None, description="제약 조건")


class DialogueContextUpdate(BaseModel):
    """Dialogue Context 업데이트 스키마"""
    title: Optional[str] = None
    content: Optional[str] = None
    entity_id: Optional[str] = None
    cell_id: Optional[str] = None
    time_category: Optional[str] = None
    event_id: Optional[str] = None
    priority: Optional[int] = None
    available_topics: Optional[Dict[str, Any]] = None
    entity_personality: Optional[str] = None
    constraints: Optional[Dict[str, Any]] = None


class DialogueTopicCreate(BaseModel):
    """Dialogue Topic 생성 스키마"""
    topic_id: str = Field(..., description="Topic ID")
    dialogue_id: str = Field(..., description="Dialogue Context ID")
    topic_type: str = Field(..., description="주제 타입 (greeting, trade, lore, quest, farewell)")
    content: str = Field(..., description="주제 내용")
    conditions: Optional[Dict[str, Any]] = Field(None, description="조건")


class DialogueTopicUpdate(BaseModel):
    """Dialogue Topic 업데이트 스키마"""
    topic_type: Optional[str] = None
    content: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None


@router.get("/contexts/entity/{entity_id}")
async def get_dialogue_contexts_by_entity(entity_id: str):
    """특정 Entity의 모든 Dialogue Context 조회"""
    try:
        contexts = await dialogue_service.get_dialogue_contexts_by_entity(entity_id)
        return contexts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dialogue Context 조회 실패: {str(e)}")


@router.get("/contexts/{dialogue_id}")
async def get_dialogue_context(dialogue_id: str):
    """특정 Dialogue Context 조회"""
    try:
        context = await dialogue_service.get_dialogue_context(dialogue_id)
        if not context:
            raise HTTPException(status_code=404, detail="Dialogue Context not found")
        return context
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dialogue Context 조회 실패: {str(e)}")


@router.post("/contexts", status_code=201)
async def create_dialogue_context(context_data: DialogueContextCreate):
    """Dialogue Context 생성"""
    try:
        dialogue_id = await dialogue_service.create_dialogue_context(
            dialogue_id=context_data.dialogue_id,
            title=context_data.title,
            content=context_data.content,
            entity_id=context_data.entity_id,
            cell_id=context_data.cell_id,
            time_category=context_data.time_category,
            event_id=context_data.event_id,
            priority=context_data.priority,
            available_topics=context_data.available_topics,
            entity_personality=context_data.entity_personality,
            constraints=context_data.constraints
        )
        return await dialogue_service.get_dialogue_context(dialogue_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dialogue Context 생성 실패: {str(e)}")


@router.put("/contexts/{dialogue_id}")
async def update_dialogue_context(dialogue_id: str, context_data: DialogueContextUpdate):
    """Dialogue Context 업데이트"""
    try:
        context = await dialogue_service.update_dialogue_context(
            dialogue_id=dialogue_id,
            title=context_data.title,
            content=context_data.content,
            entity_id=context_data.entity_id,
            cell_id=context_data.cell_id,
            time_category=context_data.time_category,
            event_id=context_data.event_id,
            priority=context_data.priority,
            available_topics=context_data.available_topics,
            entity_personality=context_data.entity_personality,
            constraints=context_data.constraints
        )
        if not context:
            raise HTTPException(status_code=404, detail="Dialogue Context not found")
        return context
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dialogue Context 업데이트 실패: {str(e)}")


@router.get("/topics/{dialogue_id}")
async def get_dialogue_topics(dialogue_id: str):
    """특정 Dialogue Context의 모든 Topics 조회"""
    try:
        topics = await dialogue_service.get_dialogue_topics(dialogue_id)
        return topics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dialogue Topics 조회 실패: {str(e)}")


@router.post("/topics", status_code=201)
async def create_dialogue_topic(topic_data: DialogueTopicCreate):
    """Dialogue Topic 생성"""
    try:
        topic_id = await dialogue_service.create_dialogue_topic(
            topic_id=topic_data.topic_id,
            dialogue_id=topic_data.dialogue_id,
            topic_type=topic_data.topic_type,
            content=topic_data.content,
            conditions=topic_data.conditions
        )
        topics = await dialogue_service.get_dialogue_topics(topic_data.dialogue_id)
        return next((t for t in topics if t['topic_id'] == topic_id), None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dialogue Topic 생성 실패: {str(e)}")


@router.put("/topics/{topic_id}")
async def update_dialogue_topic(topic_id: str, topic_data: DialogueTopicUpdate):
    """Dialogue Topic 업데이트"""
    try:
        topic = await dialogue_service.update_dialogue_topic(
            topic_id=topic_id,
            topic_type=topic_data.topic_type,
            content=topic_data.content,
            conditions=topic_data.conditions
        )
        if not topic:
            raise HTTPException(status_code=404, detail="Dialogue Topic not found")
        return topic
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dialogue Topic 업데이트 실패: {str(e)}")


@router.delete("/topics/{topic_id}")
async def delete_dialogue_topic(topic_id: str):
    """Dialogue Topic 삭제"""
    try:
        success = await dialogue_service.delete_dialogue_topic(topic_id)
        if not success:
            raise HTTPException(status_code=404, detail="Dialogue Topic not found")
        return {"message": "Dialogue Topic deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dialogue Topic 삭제 실패: {str(e)}")

