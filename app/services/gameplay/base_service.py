"""
게임플레이 서비스 베이스 클래스
"""
from typing import Optional
from database.connection import DatabaseConnection
from database.repositories.game_data import GameDataRepository
from database.repositories.runtime_data import RuntimeDataRepository
from database.repositories.reference_layer import ReferenceLayerRepository
from app.managers.entity_manager import EntityManager
from app.managers.cell_manager import CellManager
from app.managers.inventory_manager import InventoryManager
from app.managers.effect_carrier_manager import EffectCarrierManager
from app.managers.object_state_manager import ObjectStateManager
from app.handlers.action_handler import ActionHandler
from common.utils.logger import logger


class BaseGameplayService:
    """게임플레이 서비스 베이스 클래스"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db = db_connection or DatabaseConnection()
        self.game_data_repo = GameDataRepository(self.db)
        self.runtime_data_repo = RuntimeDataRepository(self.db)
        self.reference_layer_repo = ReferenceLayerRepository(self.db)
        self.logger = logger
        
        # Managers 초기화 (필요시에만)
        self._entity_manager = None
        self._cell_manager = None
        self._inventory_manager = None
        self._effect_carrier_manager = None
        self._object_state_manager = None
        self._action_handler = None
    
    @property
    def entity_manager(self) -> EntityManager:
        """EntityManager 지연 초기화"""
        if self._entity_manager is None:
            self._effect_carrier_manager = EffectCarrierManager(
                self.db,
                self.game_data_repo,
                self.runtime_data_repo,
                self.reference_layer_repo
            )
            self._entity_manager = EntityManager(
                self.db,
                self.game_data_repo,
                self.runtime_data_repo,
                self.reference_layer_repo,
                self._effect_carrier_manager
            )
        return self._entity_manager
    
    @property
    def cell_manager(self) -> CellManager:
        """CellManager 지연 초기화"""
        if self._cell_manager is None:
            self._cell_manager = CellManager(
                self.db,
                self.game_data_repo,
                self.runtime_data_repo,
                self.reference_layer_repo,
                self.entity_manager
            )
        return self._cell_manager
    
    @property
    def inventory_manager(self) -> InventoryManager:
        """InventoryManager 지연 초기화"""
        if self._inventory_manager is None:
            self._inventory_manager = InventoryManager(self.db)
        return self._inventory_manager
    
    @property
    def effect_carrier_manager(self) -> EffectCarrierManager:
        """EffectCarrierManager 지연 초기화"""
        if self._effect_carrier_manager is None:
            self._effect_carrier_manager = EffectCarrierManager(
                self.db,
                self.game_data_repo,
                self.runtime_data_repo,
                self.reference_layer_repo
            )
        return self._effect_carrier_manager
    
    @property
    def object_state_manager(self) -> ObjectStateManager:
        """ObjectStateManager 지연 초기화"""
        if self._object_state_manager is None:
            self._object_state_manager = ObjectStateManager(
                self.db,
                self.game_data_repo,
                self.runtime_data_repo,
                self.reference_layer_repo
            )
        return self._object_state_manager
    
    @property
    def action_handler(self) -> ActionHandler:
        """ActionHandler 지연 초기화"""
        if self._action_handler is None:
            self._action_handler = ActionHandler(
                db_connection=self.db,
                game_data_repo=self.game_data_repo,
                runtime_data_repo=self.runtime_data_repo,
                reference_layer_repo=self.reference_layer_repo,
                entity_manager=self.entity_manager,
                cell_manager=self.cell_manager,
                effect_carrier_manager=self.effect_carrier_manager,
                object_state_manager=self.object_state_manager,
                inventory_manager=self.inventory_manager
            )
        return self._action_handler

