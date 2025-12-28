"""
게임플레이 API 라우트 (리팩토링 버전)
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from app.services.gameplay import (
    GameService,
    CellService,
    DialogueService,
    InteractionService,
    ActionService
)
from common.utils.logger import logger

router = APIRouter(prefix="/api/gameplay", tags=["gameplay"])

# 서비스 인스턴스 (싱글톤)
_game_service: Optional[GameService] = None
_cell_service: Optional[CellService] = None
_dialogue_service: Optional[DialogueService] = None
_interaction_service: Optional[InteractionService] = None
_action_service: Optional[ActionService] = None

def get_game_service() -> GameService:
    """GameService 인스턴스 생성 (싱글톤)"""
    global _game_service
    if _game_service is None:
        _game_service = GameService()
    return _game_service

def get_cell_service() -> CellService:
    """CellService 인스턴스 생성 (싱글톤)"""
    global _cell_service
    if _cell_service is None:
        _cell_service = CellService()
    return _cell_service

def get_dialogue_service() -> DialogueService:
    """DialogueService 인스턴스 생성 (싱글톤)"""
    global _dialogue_service
    if _dialogue_service is None:
        _dialogue_service = DialogueService()
    return _dialogue_service

def get_interaction_service() -> InteractionService:
    """InteractionService 인스턴스 생성 (싱글톤)"""
    global _interaction_service
    if _interaction_service is None:
        _interaction_service = InteractionService()
    return _interaction_service

def get_action_service() -> ActionService:
    """ActionService 인스턴스 생성 (싱글톤)"""
    global _action_service
    if _action_service is None:
        _action_service = ActionService()
    return _action_service


# 요청/응답 스키마
class StartGameRequest(BaseModel):
    player_template_id: str
    start_cell_id: Optional[str] = None

class StartGameResponse(BaseModel):
    success: bool
    game_state: dict
    message: str = "게임이 시작되었습니다."

class MovePlayerRequest(BaseModel):
    session_id: str
    target_cell_id: str

class MovePlayerResponse(BaseModel):
    success: bool
    game_state: dict
    message: str = "이동했습니다."

class StartDialogueRequest(BaseModel):
    session_id: str
    npc_id: str

class StartDialogueResponse(BaseModel):
    success: bool
    dialogue: dict
    message: str = "대화를 시작했습니다."

class ProcessDialogueChoiceRequest(BaseModel):
    session_id: str
    dialogue_id: str
    choice_id: str

class InteractRequest(BaseModel):
    session_id: str
    entity_id: str
    action_type: Optional[str] = None

class InteractObjectRequest(BaseModel):
    session_id: str
    object_id: str
    action_type: Optional[str] = None

class PickupFromObjectRequest(BaseModel):
    session_id: str
    object_id: str
    item_id: str

class CombineItemsRequest(BaseModel):
    session_id: str
    items: List[str]

class InteractResponse(BaseModel):
    success: bool
    message: str
    result: Optional[dict] = None


# API 엔드포인트
@router.post("/start", response_model=StartGameResponse, status_code=status.HTTP_201_CREATED)
async def start_new_game(request: StartGameRequest):
    """새 게임 시작"""
    try:
        service = get_game_service()
        result = await service.start_game(
            player_template_id=request.player_template_id,
            start_cell_id=request.start_cell_id
        )
        return StartGameResponse(**result)
    except Exception as e:
        logger.error(f"게임 시작 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게임 시작 실패: {str(e)}"
        )

@router.get("/state/{session_id}")
async def get_current_state(session_id: str):
    """현재 게임 상태 조회"""
    try:
        service = get_game_service()
        return await service.get_game_state(session_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"상태 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"상태 조회 실패: {str(e)}"
        )

@router.get("/inventory/{session_id}")
async def get_player_inventory(session_id: str):
    """플레이어 인벤토리 조회"""
    try:
        service = get_game_service()
        result = await service.get_player_inventory(session_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"인벤토리 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"인벤토리 조회 실패: {str(e)}"
        )

@router.get("/cell/{session_id}")
async def get_current_cell(session_id: str):
    """현재 셀 정보 조회"""
    try:
        service = get_cell_service()
        return await service.get_current_cell(session_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"셀 정보 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"셀 정보 조회 실패: {str(e)}"
        )

@router.post("/move", response_model=MovePlayerResponse)
async def move_player(request: MovePlayerRequest):
    """플레이어 이동"""
    try:
        service = get_cell_service()
        result = await service.move_player(
            session_id=request.session_id,
            target_cell_id=request.target_cell_id
        )
        return MovePlayerResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"이동 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이동 실패: {str(e)}"
        )

@router.post("/dialogue/start", response_model=StartDialogueResponse)
async def start_dialogue(request: StartDialogueRequest):
    """대화 시작"""
    try:
        service = get_dialogue_service()
        result = await service.start_dialogue(
            session_id=request.session_id,
            npc_id=request.npc_id
        )
        return StartDialogueResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"대화 시작 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"대화 시작 실패: {str(e)}"
        )

@router.post("/dialogue/choice")
async def process_dialogue_choice(request: ProcessDialogueChoiceRequest):
    """대화 선택지 처리"""
    try:
        service = get_dialogue_service()
        return await service.process_dialogue_choice(
            session_id=request.session_id,
            dialogue_id=request.dialogue_id,
            choice_id=request.choice_id
        )
    except Exception as e:
        logger.error(f"대화 선택지 처리 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"대화 선택지 처리 실패: {str(e)}"
        )

@router.post("/interact", response_model=InteractResponse)
async def interact_with_entity(request: InteractRequest):
    """엔티티와 상호작용"""
    try:
        service = get_interaction_service()
        result = await service.interact_with_entity(
            session_id=request.session_id,
            entity_id=request.entity_id,
            action_type=request.action_type
        )
        return InteractResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"상호작용 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"상호작용 실패: {str(e)}"
        )

@router.post("/interact/object", response_model=InteractResponse)
async def interact_with_object(request: InteractObjectRequest):
    """오브젝트와 상호작용"""
    try:
        service = get_interaction_service()
        result = await service.interact_with_object(
            session_id=request.session_id,
            object_id=request.object_id,
            action_type=request.action_type
        )
        return InteractResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"오브젝트 상호작용 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"오브젝트 상호작용 실패: {str(e)}"
        )

@router.post("/interact/object/pickup", response_model=InteractResponse)
async def pickup_from_object(request: PickupFromObjectRequest):
    """오브젝트에서 아이템 획득"""
    try:
        service = get_interaction_service()
        result = await service.pickup_from_object(
            session_id=request.session_id,
            object_id=request.object_id,
            item_id=request.item_id
        )
        return InteractResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"아이템 획득 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"아이템 획득 실패: {str(e)}"
        )

@router.post("/combine", response_model=InteractResponse)
async def combine_items(request: CombineItemsRequest):
    """아이템 조합"""
    try:
        service = get_interaction_service()
        result = await service.combine_items(
            session_id=request.session_id,
            item_ids=request.items
        )
        return InteractResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"아이템 조합 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"아이템 조합 실패: {str(e)}"
        )

@router.get("/actions/{session_id}")
async def get_available_actions(session_id: str):
    """사용 가능한 액션 조회"""
    try:
        service = get_action_service()
        return await service.get_available_actions(session_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"액션 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"액션 조회 실패: {str(e)}"
        )

