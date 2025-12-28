"""
오브젝트 상호작용 핸들러 모듈
"""
from app.handlers.object_interactions.information import InformationInteractionHandler
from app.handlers.object_interactions.state_change import StateChangeInteractionHandler
from app.handlers.object_interactions.position import PositionInteractionHandler
from app.handlers.object_interactions.recovery import RecoveryInteractionHandler
from app.handlers.object_interactions.consumption import ConsumptionInteractionHandler
from app.handlers.object_interactions.learning import LearningInteractionHandler
from app.handlers.object_interactions.item_manipulation import ItemManipulationInteractionHandler
from app.handlers.object_interactions.crafting import CraftingInteractionHandler
from app.handlers.object_interactions.destruction import DestructionInteractionHandler

__all__ = [
    'InformationInteractionHandler',
    'StateChangeInteractionHandler',
    'PositionInteractionHandler',
    'RecoveryInteractionHandler',
    'ConsumptionInteractionHandler',
    'LearningInteractionHandler',
    'ItemManipulationInteractionHandler',
    'CraftingInteractionHandler',
    'DestructionInteractionHandler',
]

