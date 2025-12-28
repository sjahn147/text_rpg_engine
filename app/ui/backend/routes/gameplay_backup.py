"""
게임플레이 API 라우트
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from app.core.game_manager import GameManager
from app.core.game_session import GameSession
from app.managers.cell_manager import CellManager
from app.managers.inventory_manager import InventoryManager
from app.managers.effect_carrier_manager import EffectCarrierManager
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from database.factories.game_data_factory import GameDataFactory
from database.factories.instance_factory import InstanceFactory
from common.utils.logger import logger

router = APIRouter(prefix="/api/gameplay", tags=["gameplay"])

# 의존성 주입을 위한 헬퍼 함수
_game_manager_instance: Optional[GameManager] = None

def get_game_manager() -> GameManager:
    """GameManager 인스턴스 생성 (싱글톤)"""
    global _game_manager_instance
    if _game_manager_instance is None:
        db = DatabaseConnection()
        game_data_repo = GameDataRepository(db)
        runtime_data_repo = RuntimeDataRepository(db)
        reference_layer_repo = ReferenceLayerRepository(db)
        game_data_factory = GameDataFactory(db)  # db 파라미터 추가
        instance_factory = InstanceFactory(db)  # db 파라미터 추가
        
        _game_manager_instance = GameManager(
            db_connection=db,
            game_data_repo=game_data_repo,
            runtime_data_repo=runtime_data_repo,
            reference_layer_repo=reference_layer_repo,
            game_data_factory=game_data_factory,
            instance_factory=instance_factory,
        )
    return _game_manager_instance


# 요청/응답 스키마
class StartGameRequest(BaseModel):
    player_template_id: str
    start_cell_id: Optional[str] = None


class StartGameResponse(BaseModel):
    success: bool
    game_state: Dict[str, Any]
    message: str = "게임이 시작되었습니다."


class MovePlayerRequest(BaseModel):
    session_id: str
    target_cell_id: str


class MovePlayerResponse(BaseModel):
    success: bool
    game_state: Dict[str, Any]
    message: str = "이동했습니다."


class StartDialogueRequest(BaseModel):
    session_id: str
    npc_id: str


class StartDialogueResponse(BaseModel):
    success: bool
    dialogue: Dict[str, Any]
    message: str = "대화를 시작했습니다."


class ProcessDialogueChoiceRequest(BaseModel):
    session_id: str
    dialogue_id: str
    choice_id: str


class InteractRequest(BaseModel):
    session_id: str
    entity_id: str
    action_type: Optional[str] = None  # 'examine', 'dialogue', 'interact', 'pickup' 등


class InteractObjectRequest(BaseModel):
    session_id: str
    object_id: str
    action_type: Optional[str] = None  # 'examine', 'open', 'close', 'pickup' 등


class PickupFromObjectRequest(BaseModel):
    session_id: str
    object_id: str
    item_id: str  # 획득할 아이템/장비/Effect Carrier ID


class CombineItemsRequest(BaseModel):
    session_id: str
    items: List[str]  # 조합할 아이템 ID 목록 (2~5개)


class InteractResponse(BaseModel):
    success: bool
    message: str
    result: Optional[Dict[str, Any]] = None


# API 엔드포인트
@router.post("/start", response_model=StartGameResponse, status_code=status.HTTP_201_CREATED)
async def start_new_game(
    request: StartGameRequest,
    game_manager: GameManager = Depends(get_game_manager)
):
    """새 게임 시작"""
    try:
        session_id = await game_manager.start_new_game(
            player_template_id=request.player_template_id,
            start_cell_id=request.start_cell_id
        )
        
        # 게임 상태 조회
        session = GameSession(session_id)
        await session.initialize_session()
        
        # 플레이어 엔티티 정보 조회
        player_entities = await session.get_player_entities()
        if not player_entities:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="플레이어 엔티티를 찾을 수 없습니다."
            )
        
        player_id = player_entities[0]['runtime_entity_id']
        current_cell_id = player_entities[0].get('runtime_cell_id')
        
        # 게임 상태 구성
        game_state = {
            "session_id": session_id,
            "player_id": player_id,
            "current_cell_id": current_cell_id,
            "current_location": "",
            "play_time": 0,
            "flags": {},
            "variables": {},
            "save_date": "",
            "version": "1.0.0"
        }
        
        return StartGameResponse(
            success=True,
            game_state=game_state,
            message="게임이 시작되었습니다."
        )
    except Exception as e:
        import traceback
        error_detail = f"게임 시작 실패: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_detail)
        # 클라이언트에게는 간단한 메시지만 전달, 상세 내용은 로그에 기록
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게임 시작 실패: {str(e)}\n\n상세 에러는 서버 로그를 확인하세요."
        )


@router.get("/state/{session_id}")
async def get_current_state(session_id: str):
    """현재 게임 상태 조회"""
    try:
        session = GameSession(session_id)
        player_entities = await session.get_player_entities()
        
        if not player_entities:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션을 찾을 수 없습니다."
            )
        
        player_id = player_entities[0]['runtime_entity_id']
        # current_position JSONB에서 runtime_cell_id 추출
        current_position = player_entities[0].get('current_position', {})
        if isinstance(current_position, str):
            import json
            current_position = json.loads(current_position)
        current_cell_id = current_position.get('runtime_cell_id')
        
        game_state = {
            "session_id": session_id,
            "player_id": player_id,
            "current_cell_id": current_cell_id,
            "current_location": "",
            "play_time": 0,
            "flags": {},
            "variables": {},
            "save_date": "",
            "version": "1.0.0"
        }
        
        return game_state
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"상태 조회 실패: {str(e)}"
        )


@router.get("/inventory/{session_id}")
async def get_player_inventory(session_id: str):
    """플레이어 인벤토리 조회"""
    try:
        session = GameSession(session_id)
        player_entities = await session.get_player_entities()
        
        if not player_entities:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션을 찾을 수 없습니다."
            )
        
        player_id = player_entities[0]['runtime_entity_id']
        
        # 인벤토리 조회
        from database.connection import DatabaseConnection
        from database.repositories.runtime_data import RuntimeDataRepository
        
        db = DatabaseConnection()
        runtime_data_repo = RuntimeDataRepository(db)
        entity_state = await runtime_data_repo.get_entity_state(player_id)
        
        if not entity_state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="엔티티 상태를 찾을 수 없습니다."
            )
        
        # 인벤토리 파싱
        import json
        inventory = entity_state.get('inventory', {})
        if isinstance(inventory, str):
            inventory = json.loads(inventory)
        
        quantities = inventory.get('quantities', {})
        
        # 아이템 정보 조회
        from database.repositories.game_data import GameDataRepository
        game_data_repo = GameDataRepository(db)
        
        inventory_items = []
        for item_id, quantity in quantities.items():
            if quantity > 0:
                item_template = await game_data_repo.get_item(item_id)
                item_name = item_id
                if item_template:
                    # base_properties에서 이름 가져오기
                    base_property_id = item_template.get('base_property_id')
                    if base_property_id:
                        pool = await db.pool
                        async with pool.acquire() as conn:
                            bp_row = await conn.fetchrow(
                                """
                                SELECT name FROM game_data.base_properties WHERE property_id = $1
                                """,
                                base_property_id
                            )
                            if bp_row:
                                item_name = bp_row['name']
                
                inventory_items.append({
                    "item_id": item_id,
                    "quantity": quantity,
                    "name": item_name
                })
        
        return {
            "success": True,
            "inventory": inventory_items
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"인벤토리 조회 실패: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_detail)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"인벤토리 조회 실패: {str(e)}"
        )


@router.get("/cell/{session_id}")
async def get_current_cell(session_id: str):
    """현재 셀 정보 조회"""
    try:
        session = GameSession(session_id)
        player_entities = await session.get_player_entities()
        
        if not player_entities:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션을 찾을 수 없습니다."
            )
        
        # current_position JSONB에서 runtime_cell_id 추출
        current_position = player_entities[0].get('current_position', {})
        if isinstance(current_position, str):
            import json
            current_position = json.loads(current_position)
        current_cell_id = current_position.get('runtime_cell_id')
        if not current_cell_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="현재 셀을 찾을 수 없습니다."
            )
        
        # 셀 정보 조회
        from database.repositories.game_data import GameDataRepository
        from database.repositories.runtime_data import RuntimeDataRepository
        from database.repositories.reference_layer import ReferenceLayerRepository
        from app.managers.entity_manager import EntityManager
        
        db = DatabaseConnection()
        game_data_repo = GameDataRepository(db)
        runtime_data_repo = RuntimeDataRepository(db)
        reference_layer_repo = ReferenceLayerRepository(db)
        entity_manager = EntityManager(db, game_data_repo, runtime_data_repo, reference_layer_repo)
        
        cell_manager = CellManager(
            db_connection=db,
            game_data_repo=game_data_repo,
            runtime_data_repo=runtime_data_repo,
            reference_layer_repo=reference_layer_repo,
            entity_manager=entity_manager
        )
        cell_contents = await cell_manager.get_cell_contents(current_cell_id)
        
        # 셀 기본 정보 조회 (game_data에서)
        pool = await db.pool
        async with pool.acquire() as conn:
            cell_data = await conn.fetchrow(
                """
                SELECT 
                    c.cell_id,
                    c.cell_name,
                    c.cell_description as description,
                    l.location_name,
                    r.region_name
                FROM game_data.world_cells c
                JOIN game_data.world_locations l ON c.location_id = l.location_id
                JOIN game_data.world_regions r ON l.region_id = r.region_id
                WHERE c.cell_id = (
                    SELECT game_cell_id FROM reference_layer.cell_references
                    WHERE runtime_cell_id = $1
                )
                """,
                current_cell_id
            )
            
            if not cell_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="셀 데이터를 찾을 수 없습니다."
                )
        
        # 연결된 셀 조회
        connected_cells = []
        # TODO: 연결된 셀 정보 조회 로직 구현
        
        # 응답 구성
        cell_info = {
            "cell_id": current_cell_id,
            "cell_name": cell_data['cell_name'],
            "description": cell_data['description'] or "",
            "location_name": cell_data['location_name'],
            "region_name": cell_data['region_name'],
            "entities": [
                {
                    "entity_id": e.get('runtime_entity_id', ''),
                    "entity_name": e.get('entity_name', 'Unknown'),
                    "entity_type": e.get('entity_type', 'npc'),
                    "description": e.get('description', ''),
                    "position": e.get('current_position', {}),
                    "can_interact": True,
                    "dialogue_id": e.get('dialogue_id'),
                }
                for e in cell_contents.get('entities', [])
            ],
            "objects": [
                {
                    "object_id": o.get('runtime_object_id', ''),  # 레퍼런스 레이어를 통해 확보된 runtime_object_id만 사용
                    "object_name": o.get('object_name', 'Unknown'),
                    "object_type": o.get('object_type', 'interactive'),
                    "description": o.get('description'),
                    "position": o.get('position', {'x': 0.0, 'y': 0.0, 'z': 0.0}),
                    "can_interact": True,
                    "interaction_type": o.get('interaction_type'),
                    "properties": o.get('properties', {}),  # properties 추가 (contents 포함)
                }
                for o in cell_contents.get('objects', [])
            ],
            "connected_cells": connected_cells,
        }
        
        return cell_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"셀 정보 조회 실패: {str(e)}"
        )


@router.post("/move", response_model=MovePlayerResponse)
async def move_player(
    request: MovePlayerRequest,
    game_manager: GameManager = Depends(get_game_manager)
):
    """플레이어 이동"""
    try:
        session = GameSession(request.session_id)
        player_entities = await session.get_player_entities()
        
        if not player_entities:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션을 찾을 수 없습니다."
            )
        
        player_id = player_entities[0]['runtime_entity_id']
        
        # 이동 처리 (임시로 간단하게)
        # TODO: 실제 이동 로직 구현
        success = await session.move_player(
            player_id=player_id,
            target_cell_id=request.target_cell_id,
            new_position={"x": 0, "y": 0, "z": 0}
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="이동에 실패했습니다."
            )
        
        # 새로운 게임 상태 조회
        player_entities = await session.get_player_entities()
        current_cell_id = player_entities[0].get('runtime_cell_id')
        
        game_state = {
            "session_id": request.session_id,
            "player_id": player_id,
            "current_cell_id": current_cell_id,
            "current_location": "",
            "play_time": 0,
            "flags": {},
            "variables": {},
            "save_date": "",
            "version": "1.0.0"
        }
        
        return MovePlayerResponse(
            success=True,
            game_state=game_state,
            message="이동했습니다."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이동 실패: {str(e)}"
        )


@router.post("/dialogue/start", response_model=StartDialogueResponse)
async def start_dialogue(request: StartDialogueRequest):
    """대화 시작"""
    try:
        session = GameSession(request.session_id)
        player_entities = await session.get_player_entities()
        
        if not player_entities:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션을 찾을 수 없습니다."
            )
        
        player_id = player_entities[0]['runtime_entity_id']
        
        # 대화 시작
        dialogue_id = await session.start_npc_dialogue(player_id, request.npc_id)
        
        if not dialogue_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="대화를 시작할 수 없습니다."
            )
        
        # 대화 정보 조회 (임시)
        dialogue = {
            "dialogue_id": dialogue_id,
            "npc_name": "NPC",
            "messages": [
                {
                    "text": "안녕하세요!",
                    "character_name": "NPC",
                    "message_id": "msg_1"
                }
            ],
            "choices": []
        }
        
        return StartDialogueResponse(
            success=True,
            dialogue=dialogue,
            message="대화를 시작했습니다."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"대화 시작 실패: {str(e)}"
        )


@router.post("/dialogue/choice")
async def process_dialogue_choice(request: ProcessDialogueChoiceRequest):
    """대화 선택지 처리"""
    # TODO: 대화 선택지 처리 로직 구현
    return {"success": True, "message": "선택지가 처리되었습니다."}


@router.post("/interact", response_model=InteractResponse)
async def interact_with_entity(request: InteractRequest):
    """엔티티와 상호작용"""
    try:
        session = GameSession(request.session_id)
        player_entities = await session.get_player_entities()
        
        if not player_entities:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션을 찾을 수 없습니다."
            )
        
        player_id = player_entities[0]['runtime_entity_id']
        
        # 엔티티 정보 조회
        from database.connection import DatabaseConnection
        db = DatabaseConnection()
        pool = await db.pool
        async with pool.acquire() as conn:
            # 엔티티 참조 조회
            entity_ref = await conn.fetchrow(
                """
                SELECT er.runtime_entity_id, er.game_entity_id, er.entity_type
                FROM reference_layer.entity_references er
                WHERE er.runtime_entity_id = $1
                """,
                request.entity_id
            )
            
            if not entity_ref:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="엔티티를 찾을 수 없습니다."
                )
        
            # 게임 엔티티 정보 조회
            game_entity = await conn.fetchrow(
                """
                SELECT entity_id, entity_name, entity_description, entity_type, entity_properties
                FROM game_data.entities
                WHERE entity_id = $1
                """,
                entity_ref['game_entity_id']
            )
            
            if not game_entity:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="게임 엔티티를 찾을 수 없습니다."
                )
            
            # 액션 타입에 따른 처리
            action_type = request.action_type or 'interact'
            
            if action_type == 'examine':
                # 관찰 시 상세 정보 제공
                import json
                entity_properties = json.loads(game_entity['entity_properties']) if isinstance(game_entity['entity_properties'], str) else game_entity['entity_properties']
                
                # 플레이어 본인을 관찰하는 경우 특별한 메시지
                is_self = (entity_ref['entity_type'] == 'player' and 
                          str(entity_ref['runtime_entity_id']) == str(player_id))
                
                if is_self:
                    description = "거울을 보는 것처럼 자신의 모습을 관찰합니다. "
                    if game_entity['entity_description']:
                        description += game_entity['entity_description']
                    else:
                        description += f"{game_entity['entity_name']}의 모습이 보입니다."
                else:
                    description = game_entity['entity_description'] or f"{game_entity['entity_name']}을(를) 관찰합니다."
                
                details = []
                
                details.append(f"타입: {game_entity['entity_type']}")
                
                if entity_properties:
                    occupation = entity_properties.get('occupation')
                    if occupation:
                        details.append(f"직업: {occupation}")
                    
                    mood = entity_properties.get('mood')
                    if mood:
                        details.append(f"기분: {mood}")
                    
                    level = entity_properties.get('level')
                    if level:
                        details.append(f"레벨: {level}")
                    
                    # 플레이어 본인인 경우 추가 정보
                    if is_self:
                        # 런타임 상태에서 현재 HP/MP 정보 가져오기
                        entity_state = await conn.fetchrow(
                            """
                            SELECT current_stats FROM runtime_data.entity_states
                            WHERE runtime_entity_id = $1
                            """,
                            player_id
                        )
                        if entity_state and entity_state.get('current_stats'):
                            stats = json.loads(entity_state['current_stats']) if isinstance(entity_state['current_stats'], str) else entity_state['current_stats']
                            hp = stats.get('hp', entity_properties.get('hp', 100))
                            mp = stats.get('mp', entity_properties.get('mp', 50))
                            details.append(f"체력: {hp} / {entity_properties.get('hp', 100)}")
                            details.append(f"마나: {mp} / {entity_properties.get('mp', 50)}")
                
                if details:
                    description += f"\n\n{chr(10).join(details)}"
                
                return InteractResponse(
                    success=True,
                    message=description,
                    result={
                        "action": "examine",
                        "entity_id": request.entity_id,
                        "description": description,
                        "entity_type": game_entity['entity_type'],
                        "properties": entity_properties,
                        "is_self": is_self
                    }
                )
            elif action_type == 'dialogue':
                # 대화 시작은 별도 엔드포인트로 처리
                return InteractResponse(
                    success=True,
                    message=f"{game_entity['entity_name']}와 대화를 시작합니다.",
                    result={"action": "dialogue", "entity_id": request.entity_id}
                )
            else:
                return InteractResponse(
                    success=True,
                    message=f"{game_entity['entity_name']}와 상호작용했습니다.",
                    result={"action": action_type, "entity_id": request.entity_id}
                )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"상호작용 실패: {str(e)}"
        )


@router.post("/interact/object", response_model=InteractResponse)
async def interact_with_object(request: InteractObjectRequest):
    """오브젝트와 상호작용"""
    try:
        session = GameSession(request.session_id)
        player_entities = await session.get_player_entities()
        
        if not player_entities:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션을 찾을 수 없습니다."
            )
        
        player_id = player_entities[0]['runtime_entity_id']
        action_type = request.action_type or 'examine'
        
        # current_position JSONB에서 runtime_cell_id 추출
        current_position = player_entities[0].get('current_position', {})
        if isinstance(current_position, str):
            import json
            current_position = json.loads(current_position)
        current_cell_id = current_position.get('runtime_cell_id')
        
        if not current_cell_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="현재 셀을 찾을 수 없습니다."
            )
        
        # 현재 셀의 오브젝트 목록 조회 (관찰하기와 동일한 방식)
        from database.connection import DatabaseConnection
        from database.repositories.game_data import GameDataRepository
        from database.repositories.runtime_data import RuntimeDataRepository
        from database.repositories.reference_layer import ReferenceLayerRepository
        from app.managers.entity_manager import EntityManager
        
        db = DatabaseConnection()
        game_data_repo = GameDataRepository(db)
        runtime_data_repo = RuntimeDataRepository(db)
        reference_layer_repo = ReferenceLayerRepository(db)
        entity_manager = EntityManager(db, game_data_repo, runtime_data_repo, reference_layer_repo)
        
        cell_manager = CellManager(
            db_connection=db,
            game_data_repo=game_data_repo,
            runtime_data_repo=runtime_data_repo,
            reference_layer_repo=reference_layer_repo,
            entity_manager=entity_manager
        )
        cell_contents = await cell_manager.get_cell_contents(current_cell_id)
        
        # 현재 셀의 오브젝트 목록에서 요청한 오브젝트 찾기
        target_object = None
        for obj in cell_contents.get('objects', []):
            # object_id가 runtime_object_id 또는 game_object_id와 일치하는지 확인
            if (obj.get('runtime_object_id') == request.object_id or 
                obj.get('game_object_id') == request.object_id):
                target_object = obj
                break
        
        if not target_object:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="현재 셀에서 오브젝트를 찾을 수 없습니다."
            )
        
        # 오브젝트 정보 조회
        pool = await db.pool
        async with pool.acquire() as conn:
            # 게임 오브젝트 정보 조회 (target_object에서 game_object_id 사용)
            game_object = await conn.fetchrow(
                """
                SELECT object_id, object_name, object_description, interaction_type, properties
                FROM game_data.world_objects
                WHERE object_id = $1
                """,
                target_object['game_object_id']
            )
            
            if not game_object:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="게임 오브젝트를 찾을 수 없습니다."
                )
            
            # 액션 타입에 따른 처리
            import json
            import uuid
            properties = json.loads(game_object['properties']) if isinstance(game_object['properties'], str) else game_object['properties']
            
            # 레퍼런스 레이어를 통해 game_object_id → runtime_object_id 변환
            # 1. object_references에서 조회
            object_ref = await conn.fetchrow(
                """
                SELECT runtime_object_id FROM reference_layer.object_references
                WHERE game_object_id = $1 AND session_id = $2
                """,
                target_object['game_object_id'],
                request.session_id
            )
            
            if object_ref:
                # 레퍼런스 레이어에 있으면 사용
                runtime_object_id = str(object_ref['runtime_object_id'])
            else:
                # 레퍼런스 레이어에 없으면 새로 생성하고 등록
                runtime_object_id = str(uuid.uuid4())
                
                # object_references에 등록
                await conn.execute(
                    """
                    INSERT INTO reference_layer.object_references 
                    (runtime_object_id, game_object_id, session_id, object_type)
                    VALUES ($1, $2, $3, $4)
                    """,
                    runtime_object_id,
                    target_object['game_object_id'],
                    request.session_id,
                    target_object.get('object_type', 'interactive')
                )
                
                # runtime_objects에도 생성
                await conn.execute(
                    """
                    INSERT INTO runtime_data.runtime_objects 
                    (runtime_object_id, game_object_id, session_id)
                    VALUES ($1, $2, $3)
                    """,
                    runtime_object_id,
                    target_object['game_object_id'],
                    request.session_id
                )
            
            if action_type == 'open':
                # 오브젝트 열기 - contents 확인
                contents = properties.get('contents', [])
                current_state = properties.get('current_state', 'closed')
                
                # 상태 변경
                if current_state == 'closed':
                    # 런타임 오브젝트 상태 업데이트
                    # object_states 테이블에 상태 저장 (기존 상태 확인 후 업데이트)
                    existing_state = await conn.fetchrow(
                        """
                        SELECT current_state FROM runtime_data.object_states
                        WHERE runtime_object_id = $1
                        """,
                        runtime_object_id
                    )
                    
                    new_state = {"state": "open", "contents": contents}
                    if existing_state:
                        # 기존 상태 업데이트
                        existing_state_dict = json.loads(existing_state['current_state']) if isinstance(existing_state['current_state'], str) else existing_state['current_state']
                        existing_state_dict.update(new_state)
                        await conn.execute(
                            """
                            UPDATE runtime_data.object_states
                            SET current_state = $1::jsonb, updated_at = NOW()
                            WHERE runtime_object_id = $2
                            """,
                            json.dumps(existing_state_dict),
                            runtime_object_id
                        )
                    else:
                        # 새 상태 생성 (runtime_object_id는 이미 위에서 레퍼런스 레이어를 통해 확보됨)
                        await conn.execute(
                            """
                            INSERT INTO runtime_data.object_states (runtime_object_id, current_state)
                            VALUES ($1, $2::jsonb)
                            """,
                            runtime_object_id,
                            json.dumps(new_state)
                        )
                
                message = f"{game_object['object_name']}을(를) 열었습니다."
                if contents and len(contents) > 0:
                    message += f"\n\n내부에 {len(contents)}개의 항목이 보입니다: {', '.join(contents)}"
                
                return InteractResponse(
                    success=True,
                    message=message,
                    result={
                        "action": "open",
                        "object_id": runtime_object_id,
                        "contents": contents,
                        "new_state": "open"
                    }
                )
            elif action_type == 'light':
                # 불 켜기
                current_state = properties.get('current_state', 'unlit')
                if current_state == 'unlit':
                    # 런타임 오브젝트 상태 업데이트
                    existing_state = await conn.fetchrow(
                        """
                        SELECT current_state FROM runtime_data.object_states
                        WHERE runtime_object_id = $1
                        """,
                        runtime_object_id
                    )
                    
                    new_state = {"state": "lit"}
                    if existing_state:
                        existing_state_dict = json.loads(existing_state['current_state']) if isinstance(existing_state['current_state'], str) else existing_state['current_state']
                        existing_state_dict.update(new_state)
                        await conn.execute(
                            """
                            UPDATE runtime_data.object_states
                            SET current_state = $1::jsonb, updated_at = NOW()
                            WHERE runtime_object_id = $2
                            """,
                            json.dumps(existing_state_dict),
                            runtime_object_id
                        )
                    else:
                        # 새 상태 생성 (runtime_object_id는 이미 위에서 레퍼런스 레이어를 통해 확보됨)
                        await conn.execute(
                            """
                            INSERT INTO runtime_data.object_states (runtime_object_id, current_state)
                            VALUES ($1, $2::jsonb)
                            """,
                            runtime_object_id,
                            json.dumps(new_state)
                        )
                    message = f"{game_object['object_name']}에 불을 켰습니다. 따뜻한 빛이 방을 비춥니다."
                else:
                    message = f"{game_object['object_name']}의 불이 이미 켜져 있습니다."
                
                return InteractResponse(
                    success=True,
                    message=message,
                    result={"action": "light", "object_id": runtime_object_id, "new_state": "lit"}
                )
            elif action_type == 'sit':
                # 앉기
                return InteractResponse(
                    success=True,
                    message=f"{game_object['object_name']}에 앉았습니다. 편안합니다.",
                    result={"action": "sit", "object_id": runtime_object_id}
                )
            elif action_type == 'rest':
                # 쉬기
                rest_effect = properties.get('rest_effect', {})
                hp_regen = rest_effect.get('hp_regen', 0)
                mp_regen = rest_effect.get('mp_regen', 0)
                
                message = f"{game_object['object_name']}에서 휴식을 취했습니다."
                if hp_regen > 0 or mp_regen > 0:
                    effects = []
                    if hp_regen > 0:
                        effects.append(f"HP +{hp_regen}")
                    if mp_regen > 0:
                        effects.append(f"MP +{mp_regen}")
                    message += f"\n\n효과: {', '.join(effects)}"
                
                return InteractResponse(
                    success=True,
                    message=message,
                    result={"action": "rest", "object_id": runtime_object_id, "effect": rest_effect}
                )
            elif action_type == 'examine':
                # 관찰 시 상세 정보 제공
                interaction_type = properties.get('interaction_type', 'none')
                possible_states = properties.get('possible_states', [])
                current_state = properties.get('current_state', 'default')
                
                # 상세 설명 구성
                base_description = game_object.get('object_description') or game_object.get('object_name', '오브젝트')
                description = base_description  # 기본 설명을 먼저 설정
                if not description or description.strip() == '':
                    description = f"{game_object.get('object_name', '오브젝트')}을(를) 살펴봅니다."
                else:
                    description = f"{description}"
                
                details = []
                
                if interaction_type and interaction_type != 'none':
                    interaction_names = {
                        'openable': '열 수 있는',
                        'lightable': '불을 켤 수 있는',
                        'sitable': '앉을 수 있는',
                        'restable': '쉴 수 있는',
                        'examine': '조사 가능한',
                    }
                    details.append(f"타입: {interaction_names.get(interaction_type, interaction_type)}")
                
                if possible_states and len(possible_states) > 0:
                    details.append(f"상태: {current_state} (가능한 상태: {', '.join(possible_states)})")
                
                # 런타임 상태 확인 (열림/닫힘 등)
                # runtime_object_id가 UUID인 경우에만 조회 (문자열 ID는 runtime_objects에 없을 수 있음)
                try:
                    import uuid
                    # UUID 형식인지 확인
                    if len(runtime_object_id) == 36 and '-' in runtime_object_id:
                        uuid.UUID(runtime_object_id)  # UUID 형식 검증
                        runtime_state = await conn.fetchrow(
                            """
                            SELECT current_state FROM runtime_data.object_states
                            WHERE runtime_object_id = $1
                            """,
                            runtime_object_id
                        )
                        if runtime_state and runtime_state.get('current_state'):
                            state_dict = json.loads(runtime_state['current_state']) if isinstance(runtime_state['current_state'], str) else runtime_state['current_state']
                            if state_dict.get('state'):
                                details.append(f"현재 상태: {state_dict['state']}")
                    else:
                        # 문자열 ID인 경우, runtime_objects에서 UUID 찾기
                        runtime_obj = await conn.fetchrow(
                            """
                            SELECT runtime_object_id FROM runtime_data.runtime_objects
                            WHERE game_object_id = $1 AND session_id = $2
                            """,
                            target_object['game_object_id'],
                            request.session_id
                        )
                        if runtime_obj:
                            runtime_state = await conn.fetchrow(
                                """
                                SELECT current_state FROM runtime_data.object_states
                                WHERE runtime_object_id = $1
                                """,
                                runtime_obj['runtime_object_id']
                            )
                            if runtime_state and runtime_state.get('current_state'):
                                state_dict = json.loads(runtime_state['current_state']) if isinstance(runtime_state['current_state'], str) else runtime_state['current_state']
                                if state_dict.get('state'):
                                    details.append(f"현재 상태: {state_dict['state']}")
                except (ValueError, Exception) as e:
                    # UUID 변환 실패 또는 조회 실패 시 무시 (상태가 없을 수 있음)
                    logger.debug(f"Runtime state 조회 실패 (정상일 수 있음): {e}")
                    pass
                
                if details:
                    description += f"\n\n{chr(10).join(details)}"
                
                logger.info(f"Examine action: object_id={runtime_object_id}, description={description}")
                
                return InteractResponse(
                    success=True,
                    message=description,
                    result={
                        "action": "examine",
                        "object_id": runtime_object_id,
                        "description": description,
                        "interaction_type": interaction_type,
                        "current_state": current_state,
                        "properties": properties
                    }
                )
            else:
                return InteractResponse(
                    success=True,
                    message=f"{game_object['object_name']}과(와) 상호작용했습니다.",
                    result={"action": action_type, "object_id": runtime_object_id}
                )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"오브젝트 상호작용 실패: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_detail)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"오브젝트 상호작용 실패: {str(e)}"
        )


@router.get("/actions/{session_id}")
async def get_available_actions(session_id: str):
    """사용 가능한 액션 조회"""
    try:
        session = GameSession(session_id)
        player_entities = await session.get_player_entities()
        
        if not player_entities:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션을 찾을 수 없습니다."
            )
        
        # current_position JSONB에서 runtime_cell_id 추출
        current_position = player_entities[0].get('current_position', {})
        if isinstance(current_position, str):
            import json
            current_position = json.loads(current_position)
        current_cell_id = current_position.get('runtime_cell_id')
        
        if not current_cell_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="현재 셀을 찾을 수 없습니다."
            )
        
        # 현재 셀 정보 조회
        from database.repositories.game_data import GameDataRepository
        from database.repositories.runtime_data import RuntimeDataRepository
        from database.repositories.reference_layer import ReferenceLayerRepository
        from app.managers.entity_manager import EntityManager
        
        db = DatabaseConnection()
        game_data_repo = GameDataRepository(db)
        runtime_data_repo = RuntimeDataRepository(db)
        reference_layer_repo = ReferenceLayerRepository(db)
        entity_manager = EntityManager(db, game_data_repo, runtime_data_repo, reference_layer_repo)
        
        cell_manager = CellManager(
            db_connection=db,
            game_data_repo=game_data_repo,
            runtime_data_repo=runtime_data_repo,
            reference_layer_repo=reference_layer_repo,
            entity_manager=entity_manager
        )
        cell_contents = await cell_manager.get_cell_contents(current_cell_id)
        
        actions = []
        
        # 연결된 셀로 이동 액션
        # TODO: 연결된 셀 정보 조회하여 이동 액션 생성
        
        # 엔티티와 대화 액션
        for entity in cell_contents.get('entities', []):
            if entity.get('entity_type') == 'npc' and entity.get('dialogue_id'):
                actions.append({
                    "action_id": f"dialogue_{entity['runtime_entity_id']}",
                    "action_type": "dialogue",
                    "text": f"{entity.get('entity_name', 'NPC')}와 대화하기",
                    "target_id": entity['runtime_entity_id'],
                    "target_name": entity.get('entity_name', 'NPC'),
                })
        
        # 엔티티 관찰 및 상호작용 액션
        for entity in cell_contents.get('entities', []):
            entity_name = entity.get('entity_name', 'Entity')
            entity_id = entity['runtime_entity_id']
            
            # 관찰하기 액션 (항상 가능)
            actions.append({
                "action_id": f"examine_entity_{entity_id}",
                "action_type": "examine",
                "text": f"{entity_name} 관찰하기",
                "target_id": entity_id,
                "target_name": entity_name,
                "target_type": "entity",
                "description": entity.get('description', ''),
            })
            
            # 대화하기 액션
            if entity.get('dialogue_id'):
                actions.append({
                    "action_id": f"dialogue_{entity_id}",
                    "action_type": "dialogue",
                    "text": f"{entity_name}와 대화하기",
                    "target_id": entity_id,
                    "target_name": entity_name,
                    "target_type": "entity",
                })
            
            # 상호작용하기 액션
            if entity.get('can_interact'):
                actions.append({
                    "action_id": f"interact_entity_{entity_id}",
                    "action_type": "interact",
                    "text": f"{entity_name}와 상호작용하기",
                    "target_id": entity_id,
                    "target_name": entity_name,
                    "target_type": "entity",
                })
        
        # 일반적인 액션 추가 (TRPG 스타일)
        objects = cell_contents.get('objects', [])
        if len(objects) > 0:
            # 관찰하기 - 모든 오브젝트 발견
            object_names = [obj.get('object_name', 'Object') for obj in objects]
            actions.append({
                "action_id": "observe_room",
                "action_type": "observe",
                "text": "주변 관찰하기",
                "target_id": None,
                "target_name": None,
                "target_type": None,
                "description": f"주변을 관찰하여 {', '.join(object_names)} 등을 발견합니다.",
            })
        
        # 오브젝트별 구체적인 액션은 제거 (컨텍스트 메뉴에서 처리)
        
        return actions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"액션 조회 실패: {str(e)}"
        )


@router.post("/combine", response_model=InteractResponse)
async def combine_items(request: CombineItemsRequest):
    """아이템 조합"""
    try:
        session = GameSession(request.session_id)
        player_entities = await session.get_player_entities()
        
        if not player_entities:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션을 찾을 수 없습니다."
            )
        
        player_id = player_entities[0]['runtime_entity_id']
        
        # 입력 검증
        if len(request.items) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="조합하려면 최소 2개의 아이템이 필요합니다."
            )
        if len(request.items) > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="조합은 최대 5개의 아이템까지만 가능합니다."
            )
        
        # Managers 및 Handlers 생성
        from database.connection import DatabaseConnection
        from database.repositories.game_data import GameDataRepository
        from database.repositories.runtime_data import RuntimeDataRepository
        from database.repositories.reference_layer import ReferenceLayerRepository
        from app.managers.entity_manager import EntityManager
        from app.managers.inventory_manager import InventoryManager
        from app.managers.effect_carrier_manager import EffectCarrierManager
        from app.managers.object_state_manager import ObjectStateManager
        from app.handlers.object_interactions.crafting import CraftingInteractionHandler
        
        db = DatabaseConnection()
        game_data_repo = GameDataRepository(db)
        runtime_data_repo = RuntimeDataRepository(db)
        reference_layer_repo = ReferenceLayerRepository(db)
        effect_carrier_manager = EffectCarrierManager(
            db, game_data_repo, runtime_data_repo, reference_layer_repo
        )
        entity_manager = EntityManager(
            db, game_data_repo, runtime_data_repo, reference_layer_repo, effect_carrier_manager
        )
        inventory_manager = InventoryManager(
            db, game_data_repo, runtime_data_repo, reference_layer_repo
        )
        object_state_manager = ObjectStateManager(
            db, game_data_repo, runtime_data_repo, reference_layer_repo
        )
        
        crafting_handler = CraftingInteractionHandler(
            db,
            object_state_manager,
            entity_manager=entity_manager,
            inventory_manager=inventory_manager,
            effect_carrier_manager=effect_carrier_manager
        )
        
        # 조합 실행
        result = await crafting_handler.handle_combine(
            entity_id=player_id,
            target_id=None,
            parameters={
                "session_id": request.session_id,
                "items": request.items
            }
        )
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )
        
        return InteractResponse(
            success=True,
            message=result.message,
            result=result.data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"아이템 조합 실패: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_detail)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"아이템 조합 실패: {str(e)}"
        )


@router.post("/interact/object/pickup", response_model=InteractResponse)
async def pickup_from_object(request: PickupFromObjectRequest):
    """오브젝트에서 아이템/장비/Effect Carrier 획득 (하이브리드 접근법)"""
    try:
        session = GameSession(request.session_id)
        player_entities = await session.get_player_entities()
        
        if not player_entities:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션을 찾을 수 없습니다."
            )
        
        player_id = player_entities[0]['runtime_entity_id']
        
        # current_position JSONB에서 runtime_cell_id 추출
        current_position = player_entities[0].get('current_position', {})
        if isinstance(current_position, str):
            import json
            current_position = json.loads(current_position)
        current_cell_id = current_position.get('runtime_cell_id')
        
        if not current_cell_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="현재 셀을 찾을 수 없습니다."
            )
        
        # 현재 셀의 오브젝트 목록 조회 (레퍼런스 레이어를 통해)
        from database.connection import DatabaseConnection
        from database.repositories.game_data import GameDataRepository
        from database.repositories.runtime_data import RuntimeDataRepository
        from database.repositories.reference_layer import ReferenceLayerRepository
        from app.managers.entity_manager import EntityManager
        
        db = DatabaseConnection()
        game_data_repo = GameDataRepository(db)
        runtime_data_repo = RuntimeDataRepository(db)
        reference_layer_repo = ReferenceLayerRepository(db)
        entity_manager = EntityManager(db, game_data_repo, runtime_data_repo, reference_layer_repo)
        
        cell_manager = CellManager(
            db_connection=db,
            game_data_repo=game_data_repo,
            runtime_data_repo=runtime_data_repo,
            reference_layer_repo=reference_layer_repo,
            entity_manager=entity_manager
        )
        cell_contents = await cell_manager.get_cell_contents(current_cell_id)
        
        # 현재 셀의 오브젝트 목록에서 요청한 오브젝트 찾기
        target_object = None
        for obj in cell_contents.get('objects', []):
            # object_id가 runtime_object_id 또는 game_object_id와 일치하는지 확인
            if (obj.get('runtime_object_id') == request.object_id or 
                obj.get('game_object_id') == request.object_id):
                target_object = obj
                break
        
        if not target_object:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="현재 셀에서 오브젝트를 찾을 수 없습니다."
            )
        
        # 오브젝트 정보 조회
        import json
        pool = await db.pool
        async with pool.acquire() as conn:
            async with conn.transaction():
                # 게임 오브젝트 정보 조회 (target_object에서 game_object_id 사용)
                game_object = await conn.fetchrow(
                    """
                    SELECT object_id, object_name, object_description, properties
                    FROM game_data.world_objects
                    WHERE object_id = $1
                    """,
                    target_object['game_object_id']
                )
                
                if not game_object:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="게임 오브젝트를 찾을 수 없습니다."
                    )
                
                # 레퍼런스 레이어를 통해 runtime_object_id 확보
                import uuid
                object_ref = await conn.fetchrow(
                    """
                    SELECT runtime_object_id FROM reference_layer.object_references
                    WHERE game_object_id = $1 AND session_id = $2
                    """,
                    target_object['game_object_id'],
                    request.session_id
                )
                
                if not object_ref:
                    # 레퍼런스 레이어에 없으면 새로 생성
                    runtime_object_id = str(uuid.uuid4())
                    await conn.execute(
                        """
                        INSERT INTO reference_layer.object_references 
                        (runtime_object_id, game_object_id, session_id, object_type)
                        VALUES ($1, $2, $3, $4)
                        """,
                        runtime_object_id,
                        target_object['game_object_id'],
                        request.session_id,
                        target_object.get('object_type', 'interactive')
                    )
                    await conn.execute(
                        """
                        INSERT INTO runtime_data.runtime_objects 
                        (runtime_object_id, game_object_id, session_id)
                        VALUES ($1, $2, $3)
                        """,
                        runtime_object_id,
                        target_object['game_object_id'],
                        request.session_id
                    )
                else:
                    runtime_object_id = str(object_ref['runtime_object_id'])
                
                # 런타임 상태에서 contents 확인 (없으면 game_data의 기본값 사용)
                runtime_state = await conn.fetchrow(
                    """
                    SELECT current_state FROM runtime_data.object_states
                    WHERE runtime_object_id = $1
                    """,
                    runtime_object_id
                )
                
                # game_data의 기본 properties
                properties = json.loads(game_object['properties']) if isinstance(game_object['properties'], str) else game_object['properties']
                default_contents = properties.get('contents', [])
                
                # 런타임 상태가 있으면 런타임 contents 사용, 없으면 기본값 사용
                # 중요: 런타임 상태에서 이미 제거된 아이템은 더 이상 획득할 수 없음
                if runtime_state and runtime_state.get('current_state'):
                    state_dict = json.loads(runtime_state['current_state']) if isinstance(runtime_state['current_state'], str) else runtime_state['current_state']
                    # 런타임 상태에 'contents' 키가 명시적으로 있으면 사용 (빈 배열이어도)
                    if 'contents' in state_dict:
                        contents = state_dict['contents'].copy()  # 런타임 상태 우선
                    else:
                        contents = default_contents.copy()  # 런타임 상태에 contents 키가 없으면 기본값
                else:
                    contents = default_contents.copy()  # 런타임 상태가 없으면 기본값
                
                # 요청한 ID가 contents에 있는지 확인
                if request.item_id not in contents:
                    # 게임 로직상 아이템이 없는 것은 정상적인 상태이므로 200 OK로 반환
                    return InteractResponse(
                        success=False,
                        message="이 오브젝트에는 해당 아이템이 없습니다.",
                        result={
                            "action": "pickup",
                            "item_id": request.item_id,
                            "reason": "item_not_found"
                        }
                    )
                
                # ID 타입 확인 및 획득 처리
                item_name = request.item_id
                
                if request.item_id.startswith('ITEM_'):
                    # 아이템 획득
                    item_template = await conn.fetchrow(
                        """
                        SELECT 
                            i.item_id, i.item_type, i.consumable, i.stack_size, 
                            i.item_properties, i.base_property_id,
                            bp.name as item_name
                        FROM game_data.items i
                        LEFT JOIN game_data.base_properties bp ON i.base_property_id = bp.property_id
                        WHERE i.item_id = $1
                        """,
                        request.item_id
                    )
                    
                    if not item_template:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="아이템 템플릿을 찾을 수 없습니다."
                        )
                    
                    item_name = item_template['item_name'] or request.item_id
                    
                    # 인벤토리에 추가
                    inventory_manager = InventoryManager(db)
                    await inventory_manager.add_item_to_inventory(
                        runtime_entity_id=player_id,
                        item_id=request.item_id,
                        quantity=1
                    )
                    
                    # Effect Carrier가 있으면 소유권 추가
                    if item_template.get('effect_carrier_id'):
                        effect_carrier_manager = EffectCarrierManager(
                            db_connection=db,
                            game_data_repo=GameDataRepository(db),
                            runtime_data_repo=RuntimeDataRepository(db),
                            reference_layer_repo=ReferenceLayerRepository(db)
                        )
                        await effect_carrier_manager.grant_effect_to_entity(
                            session_id=request.session_id,
                            entity_id=player_id,
                            effect_id=str(item_template['effect_carrier_id']),
                            source="item_pickup"
                        )
                    
                elif request.item_id.startswith('WEAPON_'):
                    # 무기 획득
                    weapon_template = await conn.fetchrow(
                        """
                        SELECT 
                            w.weapon_id, w.base_property_id, w.damage, w.weapon_type,
                            w.weapon_properties,
                            bp.name as weapon_name
                        FROM game_data.equipment_weapons w
                        LEFT JOIN game_data.base_properties bp ON w.base_property_id = bp.property_id
                        WHERE w.weapon_id = $1
                        """,
                        request.item_id
                    )
                    
                    if not weapon_template:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="무기 템플릿을 찾을 수 없습니다."
                        )
                    
                    item_name = weapon_template['weapon_name'] or request.item_id
                    
                    # 무기도 인벤토리에 추가 (장착은 별도)
                    inventory_manager = InventoryManager(db)
                    await inventory_manager.add_item_to_inventory(
                        runtime_entity_id=player_id,
                        item_id=request.item_id,
                        quantity=1
                    )
                    
                    # Effect Carrier가 있으면 소유권 추가
                    if weapon_template.get('effect_carrier_id'):
                        effect_carrier_manager = EffectCarrierManager(
                            db_connection=db,
                            game_data_repo=GameDataRepository(db),
                            runtime_data_repo=RuntimeDataRepository(db),
                            reference_layer_repo=ReferenceLayerRepository(db)
                        )
                        await effect_carrier_manager.grant_effect_to_entity(
                            session_id=request.session_id,
                            entity_id=player_id,
                            effect_id=str(weapon_template['effect_carrier_id']),
                            source="weapon_pickup"
                        )
                    
                elif request.item_id.startswith('ARMOR_'):
                    # 방어구 획득
                    armor_template = await conn.fetchrow(
                        """
                        SELECT 
                            a.armor_id, a.base_property_id, a.defense, a.armor_type,
                            a.armor_properties,
                            bp.name as armor_name
                        FROM game_data.equipment_armors a
                        LEFT JOIN game_data.base_properties bp ON a.base_property_id = bp.property_id
                        WHERE a.armor_id = $1
                        """,
                        request.item_id
                    )
                    
                    if not armor_template:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="방어구 템플릿을 찾을 수 없습니다."
                        )
                    
                    item_name = armor_template['armor_name'] or request.item_id
                    
                    # 방어구도 인벤토리에 추가
                    inventory_manager = InventoryManager(db)
                    await inventory_manager.add_item_to_inventory(
                        runtime_entity_id=player_id,
                        item_id=request.item_id,
                        quantity=1
                    )
                    
                    # Effect Carrier가 있으면 소유권 추가
                    if armor_template.get('effect_carrier_id'):
                        effect_carrier_manager = EffectCarrierManager(
                            db_connection=db,
                            game_data_repo=GameDataRepository(db),
                            runtime_data_repo=RuntimeDataRepository(db),
                            reference_layer_repo=ReferenceLayerRepository(db)
                        )
                        await effect_carrier_manager.grant_effect_to_entity(
                            session_id=request.session_id,
                            entity_id=player_id,
                            effect_id=str(armor_template['effect_carrier_id']),
                            source="armor_pickup"
                        )
                    
                else:
                    # UUID인 경우 Effect Carrier (아이템/장비와 분리된 효과)
                    effect_carrier_manager = EffectCarrierManager(
                        db_connection=db,
                        game_data_repo=GameDataRepository(db),
                        runtime_data_repo=RuntimeDataRepository(db),
                        reference_layer_repo=ReferenceLayerRepository(db)
                    )
                    result = await effect_carrier_manager.grant_effect_to_entity(
                        session_id=request.session_id,
                        entity_id=player_id,
                        effect_id=request.item_id,
                        source="object_pickup"
                    )
                    
                    if not result.success:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=result.message
                        )
                    
                    # Effect Carrier 이름 조회
                    effect_carrier = await conn.fetchrow(
                        """
                        SELECT name
                        FROM game_data.effect_carriers
                        WHERE effect_id = $1
                        """,
                        request.item_id
                    )
                    if effect_carrier:
                        item_name = effect_carrier['name']
                
                # 오브젝트의 contents에서 제거 (런타임 상태에 저장)
                contents.remove(request.item_id)
                
                # 런타임 상태 업데이트 또는 생성
                if runtime_state and runtime_state.get('current_state'):
                    # 기존 상태 업데이트
                    existing_state = json.loads(runtime_state['current_state']) if isinstance(runtime_state['current_state'], str) else runtime_state['current_state']
                    existing_state['contents'] = contents
                    # state는 기존 값 유지, 없으면 'default'
                    if 'state' not in existing_state:
                        existing_state['state'] = 'default'
                    
                    await conn.execute(
                        """
                        UPDATE runtime_data.object_states
                        SET current_state = $1::jsonb, updated_at = NOW()
                        WHERE runtime_object_id = $2
                        """,
                        json.dumps(existing_state),
                        runtime_object_id
                    )
                else:
                    # 새 상태 생성
                    new_state = {
                        "contents": contents,
                        "state": "default"
                    }
                    await conn.execute(
                        """
                        INSERT INTO runtime_data.object_states (runtime_object_id, current_state)
                        VALUES ($1, $2::jsonb)
                        """,
                        runtime_object_id,
                        json.dumps(new_state)
                    )
                
                return InteractResponse(
                    success=True,
                    message=f"{item_name}을(를) 획득했습니다.",
                    result={
                        "action": "pickup",
                        "item_id": request.item_id,
                        "item_name": item_name
                    }
                )
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"아이템 획득 실패: {str(e)}"
        )

