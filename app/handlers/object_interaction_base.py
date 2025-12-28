"""
오브젝트 상호작용 핸들러 베이스 클래스
"""
from typing import Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
from app.managers.object_state_manager import ObjectStateManager
from app.managers.entity_manager import EntityManager
from app.managers.inventory_manager import InventoryManager
from app.managers.effect_carrier_manager import EffectCarrierManager
from database.connection import DatabaseConnection
from common.utils.logger import logger
from app.handlers.action_result import ActionResult


class ObjectInteractionHandlerBase(ABC):
    """오브젝트 상호작용 핸들러 베이스 클래스"""
    
    def __init__(
        self,
        db_connection: DatabaseConnection,
        object_state_manager: ObjectStateManager,
        entity_manager: Optional[EntityManager] = None,
        inventory_manager: Optional[InventoryManager] = None,
        effect_carrier_manager: Optional[EffectCarrierManager] = None
    ):
        """
        초기화
        
        Args:
            db_connection: 데이터베이스 연결
            object_state_manager: 오브젝트 상태 관리자
            entity_manager: 엔티티 관리자 (선택사항)
            inventory_manager: 인벤토리 관리자 (선택사항)
            effect_carrier_manager: Effect Carrier 관리자 (선택사항)
        """
        self.db = db_connection
        self.object_state_manager = object_state_manager
        self.entity_manager = entity_manager
        self.inventory_manager = inventory_manager
        self.effect_carrier_manager = effect_carrier_manager
        self.logger = logger
    
    async def _parse_object_id(
        self,
        target_id: str,
        session_id: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        오브젝트 ID 파싱 (runtime_object_id, game_object_id 반환)
        
        Args:
            target_id: 대상 오브젝트 ID (UUID 또는 game_object_id)
            session_id: 세션 ID
        
        Returns:
            (runtime_object_id, game_object_id) 튜플
        """
        import re
        is_uuid = bool(re.match(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            target_id,
            re.I
        ))
        
        runtime_object_id = target_id if is_uuid else None
        game_object_id = target_id if not is_uuid else None
        
        # game_object_id가 없으면 reference_layer에서 조회
        if runtime_object_id and not game_object_id:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                ref = await conn.fetchrow(
                    """
                    SELECT game_object_id FROM reference_layer.object_references
                    WHERE runtime_object_id = $1 AND session_id = $2
                    """,
                    runtime_object_id,
                    session_id
                )
                if ref:
                    game_object_id = ref['game_object_id']
        
        return runtime_object_id, game_object_id
    
    async def _get_object_state(
        self,
        runtime_object_id: Optional[str],
        game_object_id: str,
        session_id: str
    ):
        """오브젝트 상태 조회 헬퍼"""
        if not game_object_id:
            return None
        
        state_result = await self.object_state_manager.get_object_state(
            runtime_object_id,
            game_object_id,
            session_id
        )
        
        if not state_result.success:
            return None
        
        return state_result.object_state
    
    async def _update_object_state(
        self,
        runtime_object_id: Optional[str],
        game_object_id: str,
        session_id: str,
        state: Optional[str] = None,
        contents: Optional[list] = None,
        properties: Optional[Dict[str, Any]] = None
    ):
        """오브젝트 상태 업데이트 헬퍼"""
        if not game_object_id:
            return None
        
        update_result = await self.object_state_manager.update_object_state(
            runtime_object_id,
            game_object_id,
            session_id,
            state=state,
            contents=contents,
            properties=properties
        )
        
        if not update_result.success:
            return None
        
        return update_result.object_state
    
    @abstractmethod
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """
        상호작용 처리
        
        Args:
            entity_id: 엔티티 ID
            target_id: 대상 오브젝트 ID
            parameters: 추가 파라미터 (session_id 포함)
        
        Returns:
            ActionResult: 처리 결과
        """
        pass

