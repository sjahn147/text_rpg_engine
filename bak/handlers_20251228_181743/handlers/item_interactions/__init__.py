"""
Item Interactions 핸들러 모듈
인벤토리 아이템과의 상호작용 처리
"""
from app.handlers.item_interactions.use_handler import UseItemHandler
from app.handlers.item_interactions.consumption_handler import ConsumptionItemHandler
from app.handlers.item_interactions.equipment_handler import EquipmentItemHandler
from app.handlers.item_interactions.inventory_handler import InventoryItemHandler

__all__ = [
    "UseItemHandler",
    "ConsumptionItemHandler",
    "EquipmentItemHandler",
    "InventoryItemHandler",
]

