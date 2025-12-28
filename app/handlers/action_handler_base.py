"""
ActionHandler 베이스 클래스
모든 액션 핸들러의 공통 베이스 클래스
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from app.handlers.action_result import ActionResult
from app.managers.entity_manager import EntityManager
from app.managers.cell_manager import CellManager
from app.managers.inventory_manager import InventoryManager
from app.managers.object_state_manager import ObjectStateManager
from app.managers.effect_carrier_manager import EffectCarrierManager
from database.connection import DatabaseConnection
from common.utils.logger import logger


class ActionHandlerBase(ABC):
    """액션 핸들러 베이스 클래스"""
    
    def __init__(
        self,
        db_connection: DatabaseConnection,
        entity_manager: Optional[EntityManager] = None,
        cell_manager: Optional[CellManager] = None,
        inventory_manager: Optional[InventoryManager] = None,
        object_state_manager: Optional[ObjectStateManager] = None,
        effect_carrier_manager: Optional[EffectCarrierManager] = None,
        time_system: Optional[Any] = None,  # TimeSystem 타입은 나중에 정의
    ):
        """
        액션 핸들러 초기화
        
        Args:
            db_connection: 데이터베이스 연결
            entity_manager: 엔티티 관리자
            cell_manager: 셀 관리자
            inventory_manager: 인벤토리 관리자
            object_state_manager: 오브젝트 상태 관리자
            effect_carrier_manager: Effect Carrier 관리자
            time_system: 시간 시스템
        """
        self.db = db_connection
        self.entity_manager = entity_manager
        self.cell_manager = cell_manager
        self.inventory_manager = inventory_manager
        self.object_state_manager = object_state_manager
        self.effect_carrier_manager = effect_carrier_manager
        self.time_system = time_system
        self.logger = logger
    
    @abstractmethod
    async def handle(
        self,
        entity_id: str,
        target_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """
        액션 처리
        
        Args:
            entity_id: 엔티티 ID
            target_id: 대상 ID (선택사항)
            parameters: 추가 파라미터 (선택사항)
        
        Returns:
            ActionResult: 액션 결과
        """
        pass
    
    async def _apply_time_cost(self, time_cost: int) -> None:
        """
        시간 소모 적용
        
        Args:
            time_cost: 소모할 시간 (분)
        """
        if self.time_system and time_cost > 0:
            try:
                await self.time_system.advance_time(minutes=time_cost)
                self.logger.info(f"시간 {time_cost}분 소모됨")
            except Exception as e:
                self.logger.error(f"시간 소모 실패: {str(e)}")
    
    async def _apply_effect_carrier(
        self,
        entity_id: str,
        effect_carrier_id: str
    ) -> bool:
        """
        Effect Carrier 적용
        
        Args:
            entity_id: 엔티티 ID
            effect_carrier_id: Effect Carrier ID
        
        Returns:
            bool: 적용 성공 여부
        """
        if not self.effect_carrier_manager:
            self.logger.warning("EffectCarrierManager가 초기화되지 않았습니다.")
            return False
        
        try:
            await self.effect_carrier_manager.grant_effect_to_entity(
                entity_id=entity_id,
                effect_carrier_id=effect_carrier_id
            )
            self.logger.info(f"Effect Carrier '{effect_carrier_id}' 적용 완료")
            return True
        except Exception as e:
            self.logger.error(f"Effect Carrier 적용 실패: {str(e)}")
            return False

