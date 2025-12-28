"""
Manager 인터페이스 정의
모든 Manager 클래스가 구현해야 하는 인터페이스를 정의합니다.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pydantic import BaseModel


# Result 타입들 (인터페이스에서 사용)
class EntityCreationResult(BaseModel):
    """엔티티 생성 결과"""
    status: str
    entity_id: Optional[str] = None
    entity_data: Optional[Dict[str, Any]] = None
    message: str
    error_code: Optional[str] = None


class EntityResult(BaseModel):
    """엔티티 작업 결과"""
    success: bool
    entity: Optional[Dict[str, Any]] = None
    message: str = ""
    error: Optional[str] = None


class CellResult(BaseModel):
    """셀 작업 결과"""
    success: bool
    cell: Optional[Dict[str, Any]] = None
    message: str = ""
    error: Optional[str] = None


class DialogueResult(BaseModel):
    """대화 결과"""
    success: bool
    message: str
    npc_response: str
    available_topics: List[str] = []
    dialogue_data: Optional[Dict[str, Any]] = None


class IEntityManager(ABC):
    """엔티티 관리자 인터페이스"""
    
    @abstractmethod
    async def create_entity(
        self,
        static_entity_id: str,
        session_id: str,
        custom_properties: Optional[Dict[str, Any]] = None,
        custom_position: Optional[Dict[str, float]] = None
    ) -> EntityCreationResult:
        """엔티티 생성"""
        pass
    
    @abstractmethod
    async def get_entity(self, entity_id: str) -> EntityResult:
        """엔티티 조회"""
        pass
    
    @abstractmethod
    async def update_entity(
        self,
        entity_id: str,
        updates: Dict[str, Any]
    ) -> EntityResult:
        """엔티티 업데이트"""
        pass
    
    @abstractmethod
    async def delete_entity(self, entity_id: str) -> EntityResult:
        """엔티티 삭제"""
        pass


class ICellManager(ABC):
    """셀 관리자 인터페이스"""
    
    @abstractmethod
    async def create_cell(
        self,
        static_cell_id: str,
        session_id: str
    ) -> CellResult:
        """셀 생성"""
        pass
    
    @abstractmethod
    async def get_cell(self, cell_id: str) -> CellResult:
        """셀 조회"""
        pass
    
    @abstractmethod
    async def get_cell_contents(self, cell_id: str) -> Dict[str, Any]:
        """셀 컨텐츠 조회"""
        pass
    
    @abstractmethod
    async def enter_cell(
        self,
        cell_id: str,
        player_id: str
    ) -> CellResult:
        """셀 진입"""
        pass
    
    @abstractmethod
    async def update_cell(
        self,
        cell_id: str,
        updates: Dict[str, Any]
    ) -> CellResult:
        """셀 업데이트"""
        pass
    
    @abstractmethod
    async def delete_cell(self, cell_id: str) -> CellResult:
        """셀 삭제"""
        pass


class IDialogueManager(ABC):
    """대화 관리자 인터페이스"""
    
    @abstractmethod
    async def start_dialogue(
        self,
        player_id: str,
        npc_id: str,
        topic: Optional[str] = None
    ) -> DialogueResult:
        """대화 시작"""
        pass
    
    @abstractmethod
    async def continue_dialogue(
        self,
        player_id: str,
        npc_id: str,
        player_message: str,
        topic: Optional[str] = None
    ) -> DialogueResult:
        """대화 계속"""
        pass
    
    @abstractmethod
    async def end_dialogue(
        self,
        player_id: str,
        npc_id: str
    ) -> DialogueResult:
        """대화 종료"""
        pass
    
    @abstractmethod
    async def get_dialogue_history(
        self,
        session_id: str,
        player_id: str,
        npc_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """대화 기록 조회"""
        pass


class IEffectCarrierManager(ABC):
    """Effect Carrier 관리자 인터페이스"""
    
    @abstractmethod
    async def apply_effect(
        self,
        carrier_id: str,
        target_id: str,
        session_id: str
    ) -> Dict[str, Any]:
        """효과 적용"""
        pass
    
    @abstractmethod
    async def remove_effect(
        self,
        carrier_id: str,
        target_id: str,
        session_id: str
    ) -> Dict[str, Any]:
        """효과 제거"""
        pass


class IInstanceManager(ABC):
    """인스턴스 관리자 인터페이스"""
    
    @abstractmethod
    async def create_cell_instance(
        self,
        game_cell_id: str,
        session_id: str
    ) -> str:
        """셀 인스턴스 생성"""
        pass
    
    @abstractmethod
    async def create_entity_instance(
        self,
        game_entity_id: str,
        session_id: str,
        runtime_cell_id: str,
        position: Dict[str, float],
        entity_type: str = "npc"
    ) -> str:
        """엔티티 인스턴스 생성"""
        pass
    
    @abstractmethod
    async def get_cell_instance(
        self,
        runtime_cell_id: str
    ) -> Optional[Dict[str, Any]]:
        """셀 인스턴스 조회"""
        pass
    
    @abstractmethod
    async def get_entity_instance(
        self,
        runtime_entity_id: str
    ) -> Optional[Dict[str, Any]]:
        """엔티티 인스턴스 조회"""
        pass

