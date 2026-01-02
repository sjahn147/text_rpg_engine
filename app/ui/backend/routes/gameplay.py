"""
게임플레이 API 라우트 (리팩토링 버전)
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, Query
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
    item_id: Optional[str] = None  # None이면 첫 번째 아이템

class CombineItemsRequest(BaseModel):
    session_id: str
    items: List[str]

class ItemActionRequest(BaseModel):
    session_id: str
    item_id: str

class InteractResponse(BaseModel):
    success: bool
    message: str
    result: Optional[dict] = None

class SaveGameRequest(BaseModel):
    session_id: str
    slot_id: int
    save_name: Optional[str] = None

class SaveGameResponse(BaseModel):
    success: bool
    message: str
    slot_id: int

class LoadGameRequest(BaseModel):
    slot_id: int

class LoadGameResponse(BaseModel):
    success: bool
    message: str
    session_id: str
    game_state: Dict[str, Any]

class DeleteSaveResponse(BaseModel):
    success: bool
    message: str

class SaveSlot(BaseModel):
    slot_id: int
    session_id: Optional[str] = None
    player_name: Optional[str] = None
    location: Optional[str] = None
    play_time: Optional[int] = None
    save_date: Optional[str] = None
    is_empty: bool

class SaveSlotsResponse(BaseModel):
    success: bool
    slots: List[SaveSlot]


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
    # UUID 형식 검증
    try:
        import uuid
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="잘못된 세션 ID 형식입니다.")
    
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

@router.get("/character/{session_id}")
async def get_player_character(session_id: str):
    """플레이어 캐릭터 정보 조회"""
    try:
        service = get_game_service()
        result = await service.get_player_character_info(session_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"캐릭터 정보 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"캐릭터 정보 조회 실패: {str(e)}"
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
        # 입력 검증
        if not request.session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="session_id가 필요합니다."
            )
        if not request.object_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="object_id가 필요합니다."
            )
        
        logger.info(f"오브젝트 상호작용 요청: session_id={request.session_id}, object_id={request.object_id} (type={type(request.object_id).__name__}), action_type={request.action_type}")
        service = get_interaction_service()
        result = await service.interact_with_object(
            session_id=request.session_id,
            object_id=request.object_id,
            action_type=request.action_type
        )
        logger.info(f"오브젝트 상호작용 성공: {result.get('message', '')}")
        return InteractResponse(**result)
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"오브젝트 상호작용 실패 (ValueError): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"오브젝트 상호작용 실패: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"오브젝트 상호작용 실패: {str(e)}"
        )

@router.get("/object/{object_id}/contents")
async def get_object_contents(object_id: str, session_id: str = Query(..., description="세션 ID")):
    """오브젝트의 contents 조회"""
    try:
        service = get_interaction_service()
        result = await service.get_object_contents(
            session_id=session_id,
            object_id=object_id
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"오브젝트 contents 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"오브젝트 contents 조회 실패: {str(e)}"
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
            status_code=status.HTTP_400_BAD_REQUEST,
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

@router.post("/item/use", response_model=InteractResponse)
async def use_item(request: ItemActionRequest):
    """아이템 사용"""
    try:
        service = get_interaction_service()
        result = await service.use_item(
            session_id=request.session_id,
            item_id=request.item_id
        )
        return InteractResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"아이템 사용 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"아이템 사용 실패: {str(e)}"
        )

@router.post("/item/eat", response_model=InteractResponse)
async def eat_item(request: ItemActionRequest):
    """아이템 먹기"""
    try:
        service = get_interaction_service()
        result = await service.eat_item(
            session_id=request.session_id,
            item_id=request.item_id
        )
        return InteractResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"아이템 먹기 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"아이템 먹기 실패: {str(e)}"
        )

@router.post("/item/equip", response_model=InteractResponse)
async def equip_item(request: ItemActionRequest):
    """아이템 장착"""
    try:
        service = get_interaction_service()
        result = await service.equip_item(
            session_id=request.session_id,
            item_id=request.item_id
        )
        return InteractResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"아이템 장착 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"아이템 장착 실패: {str(e)}"
        )

@router.post("/item/unequip", response_model=InteractResponse)
async def unequip_item(request: ItemActionRequest):
    """아이템 해제"""
    try:
        service = get_interaction_service()
        result = await service.unequip_item(
            session_id=request.session_id,
            item_id=request.item_id
        )
        return InteractResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"아이템 해제 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"아이템 해제 실패: {str(e)}"
        )

@router.post("/item/drop", response_model=InteractResponse)
async def drop_item(request: ItemActionRequest):
    """아이템 버리기"""
    try:
        service = get_interaction_service()
        result = await service.drop_item(
            session_id=request.session_id,
            item_id=request.item_id
        )
        return InteractResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"아이템 버리기 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"아이템 버리기 실패: {str(e)}"
        )

@router.get("/actions/{session_id}")
async def get_available_actions(session_id: str):
    """사용 가능한 액션 조회"""
    # UUID 형식 검증
    try:
        import uuid
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"잘못된 세션 ID 형식: {session_id}"
        )
    
    try:
        service = get_action_service()
        return await service.get_available_actions(session_id)
    except ValueError as e:
        logger.error(f"액션 조회 실패 (ValueError): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"액션 조회 실패: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"액션 조회 실패: {str(e)}"
        )

@router.post("/save", response_model=SaveGameResponse)
async def save_game(request: SaveGameRequest):
    """게임 저장"""
    try:
        service = get_game_service()
        result = await service.save_game(
            session_id=request.session_id,
            slot_id=request.slot_id,
            save_name=request.save_name
        )
        return SaveGameResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"게임 저장 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게임 저장 실패: {str(e)}"
        )

@router.get("/save-slots", response_model=SaveSlotsResponse)
async def get_save_slots():
    """저장 슬롯 목록 조회"""
    try:
        service = get_game_service()
        slots = await service.get_save_slots()
        return SaveSlotsResponse(success=True, slots=slots)
    except Exception as e:
        logger.error(f"저장 슬롯 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"저장 슬롯 조회 실패: {str(e)}"
        )

@router.post("/load", response_model=LoadGameResponse)
async def load_game(request: LoadGameRequest):
    """게임 불러오기"""
    try:
        service = get_game_service()
        result = await service.load_game(request.slot_id)
        return LoadGameResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"게임 불러오기 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게임 불러오기 실패: {str(e)}"
        )

@router.delete("/save/{slot_id}", response_model=DeleteSaveResponse)
async def delete_save(slot_id: int):
    """저장 슬롯 삭제"""
    try:
        service = get_game_service()
        result = await service.delete_save(slot_id)
        return DeleteSaveResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"저장 슬롯 삭제 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"저장 슬롯 삭제 실패: {str(e)}"
        )

