"""
게임플레이 API 라우트 (리팩토링 버전)
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field, validator
from app.services.gameplay import (
    GameService,
    CellService,
    DialogueService,
    InteractionService,
    ActionService,
    CharacterService,
    ObjectService,
    JournalService,
    MapService,
    ExplorationService
)
from common.utils.logger import logger

router = APIRouter(prefix="/api/gameplay", tags=["gameplay"])

# 서비스 인스턴스 (싱글톤)
_game_service: Optional[GameService] = None
_cell_service: Optional[CellService] = None
_dialogue_service: Optional[DialogueService] = None
_interaction_service: Optional[InteractionService] = None
_action_service: Optional[ActionService] = None
_character_service: Optional[CharacterService] = None
_object_service: Optional[ObjectService] = None
_journal_service: Optional[JournalService] = None
_map_service: Optional[MapService] = None
_exploration_service: Optional[ExplorationService] = None

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

def get_character_service() -> CharacterService:
    """CharacterService 인스턴스 생성 (싱글톤)"""
    global _character_service
    if _character_service is None:
        _character_service = CharacterService()
    return _character_service

def get_object_service() -> ObjectService:
    """ObjectService 인스턴스 생성 (싱글톤)"""
    global _object_service
    if _object_service is None:
        _object_service = ObjectService()
    return _object_service

def get_journal_service() -> JournalService:
    """JournalService 인스턴스 생성 (싱글톤)"""
    global _journal_service
    if _journal_service is None:
        _journal_service = JournalService()
    return _journal_service

def get_map_service() -> MapService:
    """MapService 인스턴스 생성 (싱글톤)"""
    global _map_service
    if _map_service is None:
        _map_service = MapService()
    return _map_service

def get_exploration_service() -> ExplorationService:
    """ExplorationService 인스턴스 생성 (싱글톤)"""
    global _exploration_service
    if _exploration_service is None:
        _exploration_service = ExplorationService()
    return _exploration_service


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
    session_id: str = Field(..., description="게임 세션 ID")
    npc_id: str = Field(..., description="NPC ID (runtime_entity_id 또는 game_entity_id)")
    
    @validator('session_id')
    def validate_session_id(cls, v):
        if not v or not isinstance(v, str) or len(v.strip()) == 0:
            raise ValueError('session_id는 비어있을 수 없습니다.')
        return v.strip()
    
    @validator('npc_id')
    def validate_npc_id(cls, v):
        if not v or not isinstance(v, str) or len(v.strip()) == 0:
            raise ValueError('npc_id는 비어있을 수 없습니다.')
        return v.strip()

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
    # #region agent log
    import json as json_module
    import traceback
    try:
        with open('c:\\hobby\\rpg_engine\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
            f.write(json_module.dumps({"location":"gameplay.py:271","message":"move_player API 진입","data":{"session_id":request.session_id,"target_cell_id":request.target_cell_id},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"B"}) + "\n")
    except: pass
    # #endregion
    try:
        service = get_cell_service()
        # #region agent log
        try:
            with open('c:\\hobby\\rpg_engine\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({"location":"gameplay.py:277","message":"CellService.move_player 호출 전","data":{"session_id":request.session_id,"target_cell_id":request.target_cell_id},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"B"}) + "\n")
        except: pass
        # #endregion
        result = await service.move_player(
            session_id=request.session_id,
            target_cell_id=request.target_cell_id
        )
        # #region agent log
        try:
            with open('c:\\hobby\\rpg_engine\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({"location":"gameplay.py:285","message":"CellService.move_player 성공","data":{"session_id":request.session_id,"has_result":bool(result)},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"B"}) + "\n")
        except: pass
        # #endregion
        return MovePlayerResponse(**result)
    except ValueError as e:
        # #region agent log
        try:
            with open('c:\\hobby\\rpg_engine\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({"location":"gameplay.py:291","message":"move_player ValueError","data":{"session_id":request.session_id,"error":str(e)},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"B"}) + "\n")
        except: pass
        # #endregion
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # #region agent log
        try:
            with open('c:\\hobby\\rpg_engine\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({"location":"gameplay.py:299","message":"move_player 예외 발생","data":{"session_id":request.session_id,"error":str(e),"error_type":type(e).__name__,"traceback":traceback.format_exc()},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"B"}) + "\n")
        except: pass
        # #endregion
        logger.error(f"이동 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이동 실패: {str(e)}"
        )

@router.post("/dialogue/start", response_model=StartDialogueResponse)
async def start_dialogue(request: StartDialogueRequest):
    """대화 시작"""
    import traceback
    
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
        error_trace = traceback.format_exc()
        logger.error(f"대화 시작 실패: {str(e)}")
        logger.error(f"Traceback: {error_trace}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"대화 시작 실패: {str(e)}"
        )

@router.post("/dialogue/choice")
async def process_dialogue_choice(request: ProcessDialogueChoiceRequest):
    """대화 선택지 처리"""
    # #region agent log
    import json as json_module
    import traceback
    try:
        with open('c:\\hobby\\rpg_engine\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
            f.write(json_module.dumps({"location":"gameplay.py:354","message":"process_dialogue_choice API 진입","data":{"session_id":request.session_id,"dialogue_id":request.dialogue_id,"choice_id":request.choice_id},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"C"}) + "\n")
    except: pass
    # #endregion
    try:
        service = get_dialogue_service()
        # #region agent log
        try:
            with open('c:\\hobby\\rpg_engine\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({"location":"gameplay.py:361","message":"DialogueService.process_dialogue_choice 호출 전","data":{"session_id":request.session_id,"dialogue_id":request.dialogue_id,"choice_id":request.choice_id},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"C"}) + "\n")
        except: pass
        # #endregion
        result = await service.process_dialogue_choice(
            session_id=request.session_id,
            dialogue_id=request.dialogue_id,
            choice_id=request.choice_id
        )
        # #region agent log
        try:
            with open('c:\\hobby\\rpg_engine\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({"location":"gameplay.py:368","message":"DialogueService.process_dialogue_choice 성공","data":{"session_id":request.session_id,"has_result":bool(result),"result_keys":list(result.keys()) if isinstance(result,dict) else None},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"C"}) + "\n")
        except: pass
        # #endregion
        return result
    except Exception as e:
        # #region agent log
        try:
            with open('c:\\hobby\\rpg_engine\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({"location":"gameplay.py:373","message":"process_dialogue_choice 예외 발생","data":{"session_id":request.session_id,"dialogue_id":request.dialogue_id,"choice_id":request.choice_id,"error":str(e),"error_type":type(e).__name__,"traceback":traceback.format_exc()},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"C"}) + "\n")
        except: pass
        # #endregion
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
    # #region agent log
    import json as json_module
    import traceback
    try:
        with open('c:\\hobby\\rpg_engine\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
            f.write(json_module.dumps({"location":"gameplay.py:421","message":"interact_with_object API 진입","data":{"session_id":request.session_id,"object_id":request.object_id,"action_type":request.action_type},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"F"}) + "\n")
    except: pass
    # #endregion
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
        # #region agent log
        try:
            with open('c:\\hobby\\rpg_engine\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({"location":"gameplay.py:442","message":"InteractionService.interact_with_object 호출 전","data":{"session_id":request.session_id,"object_id":request.object_id},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"F"}) + "\n")
        except: pass
        # #endregion
        result = await service.interact_with_object(
            session_id=request.session_id,
            object_id=request.object_id,
            action_type=request.action_type
        )
        # #region agent log
        try:
            with open('c:\\hobby\\rpg_engine\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({"location":"gameplay.py:450","message":"InteractionService.interact_with_object 성공","data":{"success":result.get('success'),"message":result.get('message')},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"F"}) + "\n")
        except: pass
        # #endregion
        logger.info(f"오브젝트 상호작용 성공: {result.get('message', '')}")
        return InteractResponse(**result)
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"오브젝트 상호작용 실패 (ValueError): {str(e)}")
        # #region agent log
        try:
            with open('c:\\hobby\\rpg_engine\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({"location":"gameplay.py:461","message":"interact_with_object ValueError","data":{"error":str(e)},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"F"}) + "\n")
        except: pass
        # #endregion
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"오브젝트 상호작용 실패: {str(e)}", exc_info=True)
        # #region agent log
        try:
            with open('c:\\hobby\\rpg_engine\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({"location":"gameplay.py:470","message":"interact_with_object 예외 발생","data":{"error":str(e),"error_type":type(e).__name__,"traceback":traceback.format_exc()},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"F"}) + "\n")
        except: pass
        # #endregion
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
    # #region agent log
    import json as json_module
    import traceback
    try:
        with open('c:\\hobby\\rpg_engine\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
            f.write(json_module.dumps({"location":"gameplay.py:638","message":"get_available_actions API 진입","data":{"session_id":session_id,"session_id_length":len(session_id) if session_id else 0},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"G"}) + "\n")
    except: pass
    # #endregion
    # UUID 형식 검증
    try:
        import uuid
        uuid.UUID(session_id)
    except ValueError as e:
        # #region agent log
        try:
            with open('c:\\hobby\\rpg_engine\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({"location":"gameplay.py:645","message":"get_available_actions UUID 검증 실패","data":{"session_id":session_id,"error":str(e)},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"G"}) + "\n")
        except: pass
        # #endregion
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"잘못된 세션 ID 형식: {session_id}"
        )
    
    try:
        service = get_action_service()
        # #region agent log
        try:
            with open('c:\\hobby\\rpg_engine\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({"location":"gameplay.py:653","message":"ActionService.get_available_actions 호출 전","data":{"session_id":session_id},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"G"}) + "\n")
        except: pass
        # #endregion
        result = await service.get_available_actions(session_id)
        # #region agent log
        try:
            with open('c:\\hobby\\rpg_engine\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({"location":"gameplay.py:656","message":"ActionService.get_available_actions 성공","data":{"actions_count":len(result) if isinstance(result, list) else 0},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"G"}) + "\n")
        except: pass
        # #endregion
        return result
    except ValueError as e:
        logger.error(f"액션 조회 실패 (ValueError): {str(e)}")
        # #region agent log
        try:
            with open('c:\\hobby\\rpg_engine\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({"location":"gameplay.py:662","message":"get_available_actions ValueError","data":{"error":str(e)},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"G"}) + "\n")
        except: pass
        # #endregion
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"액션 조회 실패: {str(e)}", exc_info=True)
        # #region agent log
        try:
            with open('c:\\hobby\\rpg_engine\\.cursor\\debug.log', 'a', encoding='utf-8') as f:
                f.write(json_module.dumps({"location":"gameplay.py:670","message":"get_available_actions 예외 발생","data":{"error":str(e),"error_type":type(e).__name__,"traceback":traceback.format_exc()},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"G"}) + "\n")
        except: pass
        # #endregion
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


# =====================================================
# 캐릭터 관련 API
# =====================================================

@router.get("/character/stats/{session_id}", response_model=Dict[str, Any])
async def get_character_stats(
    session_id: str,
    service: CharacterService = Depends(get_character_service)
):
    """
    캐릭터 능력치 조회
    
    Args:
        session_id: 게임 세션 ID
        
    Returns:
        캐릭터 능력치 정보
    """
    try:
        result = await service.get_character_stats(session_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"캐릭터 능력치 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"캐릭터 능력치 조회 실패: {str(e)}"
        )


@router.get("/character/inventory/{session_id}", response_model=Dict[str, Any])
async def get_character_inventory(
    session_id: str,
    service: CharacterService = Depends(get_character_service)
):
    """
    인벤토리 및 장착 아이템 조회 (Effect Carrier 포함)
    
    Args:
        session_id: 게임 세션 ID
        
    Returns:
        인벤토리 및 장착 아이템 정보
    """
    try:
        result = await service.get_character_inventory(session_id)
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


@router.get("/character/equipped/{session_id}", response_model=Dict[str, Any])
async def get_character_equipped(
    session_id: str,
    service: CharacterService = Depends(get_character_service)
):
    """
    장착 아이템 조회 (Effect Carrier 포함)
    
    Args:
        session_id: 게임 세션 ID
        
    Returns:
        장착 아이템 정보
    """
    try:
        result = await service.get_character_equipped(session_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"장착 아이템 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"장착 아이템 조회 실패: {str(e)}"
        )


@router.get("/character/applied-effects/{session_id}", response_model=Dict[str, Any])
async def get_character_applied_effects(
    session_id: str,
    service: CharacterService = Depends(get_character_service)
):
    """
    적용 중인 Effect Carrier 조회
    
    Args:
        session_id: 게임 세션 ID
        
    Returns:
        적용 중인 Effect Carrier 목록
    """
    try:
        result = await service.get_character_applied_effects(session_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"적용 중인 Effect Carrier 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"적용 중인 Effect Carrier 조회 실패: {str(e)}"
        )


@router.get("/character/abilities/{session_id}", response_model=Dict[str, Any])
async def get_character_abilities(
    session_id: str,
    service: CharacterService = Depends(get_character_service)
):
    """
    엔티티의 스킬/주문 목록 조회
    
    Args:
        session_id: 게임 세션 ID
        
    Returns:
        스킬 및 주문 목록
    """
    try:
        result = await service.get_character_abilities(session_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"스킬/주문 목록 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"스킬/주문 목록 조회 실패: {str(e)}"
        )


@router.get("/character/spells/{session_id}", response_model=Dict[str, Any])
async def get_character_spells(
    session_id: str,
    service: CharacterService = Depends(get_character_service)
):
    """
    주문 목록 조회 (abilities_magic 테이블 기반)
    
    Args:
        session_id: 게임 세션 ID
        
    Returns:
        주문 목록
    """
    try:
        result = await service.get_character_spells(session_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"주문 목록 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"주문 목록 조회 실패: {str(e)}"
        )


# =====================================================
# 오브젝트 관련 API
# =====================================================

@router.get("/object/{object_id}/state", response_model=Dict[str, Any])
async def get_object_state(
    object_id: str,
    session_id: str = Query(..., description="게임 세션 ID"),
    service: ObjectService = Depends(get_object_service)
):
    """
    오브젝트 상태 조회
    
    Args:
        object_id: 오브젝트 ID (game_object_id 또는 runtime_object_id)
        session_id: 게임 세션 ID
        
    Returns:
        오브젝트 상태 정보
    """
    try:
        result = await service.get_object_state(object_id, session_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"오브젝트 상태 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"오브젝트 상태 조회 실패: {str(e)}"
        )


@router.get("/object/{object_id}/actions", response_model=Dict[str, Any])
async def get_object_actions(
    object_id: str,
    session_id: str = Query(..., description="게임 세션 ID"),
    service: ObjectService = Depends(get_object_service)
):
    """
    가능한 액션 조회 (상태 기반)
    
    Args:
        object_id: 오브젝트 ID (game_object_id 또는 runtime_object_id)
        session_id: 게임 세션 ID
        
    Returns:
        가능한 액션 목록
    """
    try:
        result = await service.get_object_actions(object_id, session_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"오브젝트 액션 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"오브젝트 액션 조회 실패: {str(e)}"
        )


@router.get("/actions/categorized/{session_id}", response_model=Dict[str, Any])
async def get_categorized_actions(
    session_id: str,
    service: ObjectService = Depends(get_object_service)
):
    """
    카테고리별 액션 조회
    
    Args:
        session_id: 게임 세션 ID
        
    Returns:
        카테고리별 액션 목록
    """
    try:
        result = await service.get_categorized_actions(session_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"카테고리별 액션 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"카테고리별 액션 조회 실패: {str(e)}"
        )


# =====================================================
# 저널 관련 API
# =====================================================

@router.get("/journal/{session_id}", response_model=Dict[str, Any])
async def get_journal(
    session_id: str,
    service: JournalService = Depends(get_journal_service)
):
    """
    저널 데이터 통합 조회
    
    Args:
        session_id: 게임 세션 ID
        
    Returns:
        저널 데이터 (퀘스트/이야기/발견/인물/장소)
    """
    try:
        result = await service.get_journal(session_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"저널 데이터 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"저널 데이터 조회 실패: {str(e)}"
        )


@router.get("/journal/story/{session_id}", response_model=Dict[str, Any])
async def get_story_history(
    session_id: str,
    service: JournalService = Depends(get_journal_service)
):
    """
    이야기 히스토리 조회
    
    Args:
        session_id: 게임 세션 ID
        
    Returns:
        이야기 히스토리 (주요 이벤트, 선택한 분기)
    """
    try:
        result = await service.get_story_history(session_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"이야기 히스토리 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이야기 히스토리 조회 실패: {str(e)}"
        )


@router.get("/journal/discoveries/{session_id}", response_model=Dict[str, Any])
async def get_discoveries(
    session_id: str,
    service: JournalService = Depends(get_journal_service)
):
    """
    발견한 정보 조회
    
    Args:
        session_id: 게임 세션 ID
        
    Returns:
        발견한 오브젝트, 셀, 엔티티
    """
    try:
        result = await service.get_discoveries(session_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"발견한 정보 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"발견한 정보 조회 실패: {str(e)}"
        )


@router.get("/journal/characters/{session_id}", response_model=Dict[str, Any])
async def get_characters(
    session_id: str,
    service: JournalService = Depends(get_journal_service)
):
    """
    만난 NPC 목록 및 대화 히스토리 조회
    
    Args:
        session_id: 게임 세션 ID
        
    Returns:
        만난 NPC 목록 및 대화 히스토리
    """
    try:
        result = await service.get_characters(session_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"만난 NPC 목록 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"만난 NPC 목록 조회 실패: {str(e)}"
        )


@router.get("/journal/locations/{session_id}", response_model=Dict[str, Any])
async def get_locations(
    session_id: str,
    service: JournalService = Depends(get_journal_service)
):
    """
    방문한 셀/위치 목록 조회
    
    Args:
        session_id: 게임 세션 ID
        
    Returns:
        방문한 셀/위치 목록
    """
    try:
        result = await service.get_locations(session_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"방문한 위치 목록 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"방문한 위치 목록 조회 실패: {str(e)}"
        )


# =====================================================
# 맵 관련 API
# =====================================================

@router.get("/map/{session_id}", response_model=Dict[str, Any])
async def get_map_data(
    session_id: str,
    service: MapService = Depends(get_map_service)
):
    """
    맵 데이터 조회 (계층적 구조: 지역 → 위치 → 셀)
    
    Args:
        session_id: 게임 세션 ID
        
    Returns:
        맵 데이터 (계층적 구조)
    """
    try:
        result = await service.get_map_data(session_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"맵 데이터 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"맵 데이터 조회 실패: {str(e)}"
        )


@router.get("/map/discovered/{session_id}", response_model=Dict[str, Any])
async def get_discovered_cells(
    session_id: str,
    service: MapService = Depends(get_map_service)
):
    """
    발견한 셀 목록 조회
    
    Args:
        session_id: 게임 세션 ID
        
    Returns:
        발견한 셀 목록
    """
    try:
        result = await service.get_discovered_cells(session_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"발견한 셀 목록 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"발견한 셀 목록 조회 실패: {str(e)}"
        )


# =====================================================
# 탐험 관련 API
# =====================================================

@router.get("/exploration/{session_id}", response_model=Dict[str, Any])
async def get_exploration_progress(
    session_id: str,
    service: ExplorationService = Depends(get_exploration_service)
):
    """
    탐험 진행도 조회
    
    Args:
        session_id: 게임 세션 ID
        
    Returns:
        탐험 진행도 (발견한 셀 수 / 전체 셀 수)
    """
    try:
        result = await service.get_exploration_progress(session_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"탐험 진행도 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"탐험 진행도 조회 실패: {str(e)}"
        )

