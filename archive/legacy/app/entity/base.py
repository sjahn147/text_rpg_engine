from typing import Dict, Any, Optional
from datetime import datetime

class BaseEntity:
    def __init__(
        self,
        entity_id: str,
        entity_type: str,
        properties: Dict[str, Any],
        runtime_id: Optional[str] = None
    ):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.properties = properties
        self.runtime_id = runtime_id
        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at
        
    def update_property(self, key: str, value: Any):
        """엔티티 속성을 업데이트합니다."""
        self.properties[key] = value
        self.updated_at = datetime.utcnow()
        
    def get_property(self, key: str, default: Any = None) -> Any:
        """엔티티 속성을 조회합니다."""
        return self.properties.get(key, default)
        
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환합니다."""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "properties": self.properties,
            "runtime_id": self.runtime_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseEntity':
        """딕셔너리에서 엔티티를 생성합니다."""
        entity = cls(
            entity_id=data["entity_id"],
            entity_type=data["entity_type"],
            properties=data["properties"],
            runtime_id=data.get("runtime_id")
        )
        if "created_at" in data:
            entity.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            entity.updated_at = datetime.fromisoformat(data["updated_at"])
        return entity 