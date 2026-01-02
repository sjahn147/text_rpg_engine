"""
JSONB 필드 구조를 위한 Pydantic 모델
"""
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator
from uuid import UUID


class Position(BaseModel):
    """위치 정보 (current_position)"""
    x: float = Field(default=0.0, description="X 좌표")
    y: float = Field(default=0.0, description="Y 좌표")
    z: Optional[float] = Field(default=0.0, description="Z 좌표")
    runtime_cell_id: Optional[str] = Field(default=None, description="런타임 셀 ID (UUID)")
    
    @field_validator('runtime_cell_id')
    @classmethod
    def validate_runtime_cell_id(cls, v: Optional[str]) -> Optional[str]:
        """runtime_cell_id가 UUID 형식인지 검증"""
        if v is None:
            return v
        
        # UUID 형식 검증
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, v, re.IGNORECASE):
            raise ValueError(f"runtime_cell_id는 UUID 형식이어야 합니다: {v}")
        
        return v
    
    def to_jsonb(self) -> Dict[str, Any]:
        """JSONB 형식으로 변환"""
        result = {
            "x": self.x,
            "y": self.y,
            "z": self.z
        }
        if self.runtime_cell_id:
            result["runtime_cell_id"] = self.runtime_cell_id
        return result


class InventoryItem(BaseModel):
    """인벤토리 아이템"""
    item_id: str = Field(description="아이템 ID")
    quantity: int = Field(default=1, ge=0, description="수량")
    properties: Optional[Dict[str, Any]] = Field(default=None, description="아이템 속성")


class Inventory(BaseModel):
    """인벤토리 정보"""
    items: List[Union[str, InventoryItem, Dict[str, Any]]] = Field(default_factory=list, description="아이템 목록")
    quantities: Optional[Dict[str, int]] = Field(default=None, description="아이템별 수량")
    
    @field_validator('items')
    @classmethod
    def validate_items(cls, v: List[Any]) -> List[Any]:
        """items가 리스트인지 검증"""
        if not isinstance(v, list):
            raise ValueError("items는 리스트여야 합니다")
        return v
    
    def to_jsonb(self) -> Dict[str, Any]:
        """JSONB 형식으로 변환"""
        result = {"items": self.items}
        if self.quantities:
            result["quantities"] = self.quantities
        return result


class EntityStats(BaseModel):
    """엔티티 능력치 (current_stats)"""
    hp: Optional[float] = Field(default=None, ge=0, description="체력")
    mp: Optional[float] = Field(default=None, ge=0, description="마나")
    max_hp: Optional[float] = Field(default=None, ge=0, description="최대 체력")
    max_mp: Optional[float] = Field(default=None, ge=0, description="최대 마나")
    level: Optional[int] = Field(default=None, ge=1, description="레벨")
    experience: Optional[int] = Field(default=None, ge=0, description="경험치")
    
    def to_jsonb(self) -> Dict[str, Any]:
        """JSONB 형식으로 변환"""
        result = {}
        if self.hp is not None:
            result["hp"] = self.hp
        if self.mp is not None:
            result["mp"] = self.mp
        if self.max_hp is not None:
            result["max_hp"] = self.max_hp
        if self.max_mp is not None:
            result["max_mp"] = self.max_mp
        if self.level is not None:
            result["level"] = self.level
        if self.experience is not None:
            result["experience"] = self.experience
        return result


class ObjectState(BaseModel):
    """오브젝트 상태 (current_state)"""
    state: str = Field(description="현재 상태 (예: 'open', 'closed', 'locked')")
    durability: Optional[float] = Field(default=None, ge=0, le=100, description="내구도 (0-100)")
    contents: Optional[List[Union[str, Dict[str, Any]]]] = Field(default=None, description="내용물")
    properties: Optional[Dict[str, Any]] = Field(default=None, description="추가 속성")
    
    def to_jsonb(self) -> Dict[str, Any]:
        """JSONB 형식으로 변환"""
        result = {"state": self.state}
        if self.durability is not None:
            result["durability"] = self.durability
        if self.contents:
            result["contents"] = self.contents
        if self.properties:
            result["properties"] = self.properties
        return result


def validate_position(data: Optional[Dict[str, Any]]) -> Optional[Position]:
    """current_position JSONB 데이터 검증"""
    if data is None:
        return None
    
    try:
        return Position(**data)
    except Exception as e:
        raise ValueError(f"Invalid position data: {e}")


def validate_inventory(data: Optional[Dict[str, Any]]) -> Optional[Inventory]:
    """inventory JSONB 데이터 검증"""
    if data is None:
        return None
    
    try:
        return Inventory(**data)
    except Exception as e:
        raise ValueError(f"Invalid inventory data: {e}")


def validate_stats(data: Optional[Dict[str, Any]]) -> Optional[EntityStats]:
    """current_stats JSONB 데이터 검증"""
    if data is None:
        return None
    
    try:
        return EntityStats(**data)
    except Exception as e:
        raise ValueError(f"Invalid stats data: {e}")


def validate_object_state(data: Optional[Dict[str, Any]]) -> Optional[ObjectState]:
    """current_state JSONB 데이터 검증"""
    if data is None:
        return None
    
    try:
        return ObjectState(**data)
    except Exception as e:
        raise ValueError(f"Invalid object state data: {e}")

