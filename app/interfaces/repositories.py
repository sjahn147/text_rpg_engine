"""
Repository 인터페이스 정의
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class IGameDataRepository(ABC):
    """게임 데이터 저장소 인터페이스"""
    
    @abstractmethod
    async def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """엔티티 조회"""
        pass
    
    @abstractmethod
    async def get_cell(self, cell_id: str) -> Optional[Dict[str, Any]]:
        """셀 조회"""
        pass
    
    @abstractmethod
    async def get_location(self, location_id: str) -> Optional[Dict[str, Any]]:
        """위치 조회"""
        pass


class IRuntimeDataRepository(ABC):
    """런타임 데이터 저장소 인터페이스"""
    
    @abstractmethod
    async def create_session(self, session_data: Dict[str, Any]) -> str:
        """세션 생성"""
        pass
    
    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """세션 조회"""
        pass
    
    @abstractmethod
    async def create_entity_state(
        self,
        entity_state_data: Dict[str, Any]
    ) -> str:
        """엔티티 상태 생성"""
        pass
    
    @abstractmethod
    async def get_entity_state(
        self,
        runtime_entity_id: str
    ) -> Optional[Dict[str, Any]]:
        """엔티티 상태 조회"""
        pass


class IReferenceLayerRepository(ABC):
    """참조 레이어 저장소 인터페이스"""
    
    @abstractmethod
    async def create_cell_reference(
        self,
        game_cell_id: str,
        session_id: str
    ) -> str:
        """셀 참조 생성"""
        pass
    
    @abstractmethod
    async def create_entity_reference(
        self,
        game_entity_id: str,
        session_id: str,
        entity_type: str,
        is_player: bool = False
    ) -> str:
        """엔티티 참조 생성"""
        pass
    
    @abstractmethod
    async def get_cell_reference(
        self,
        runtime_cell_id: str
    ) -> Optional[Dict[str, Any]]:
        """셀 참조 조회"""
        pass
    
    @abstractmethod
    async def get_entity_reference(
        self,
        runtime_entity_id: str
    ) -> Optional[Dict[str, Any]]:
        """엔티티 참조 조회"""
        pass

