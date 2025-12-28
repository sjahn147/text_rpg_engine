"""
Entity Interactions Handlers
엔티티 상호작용 핸들러 모듈
"""
from app.handlers.entity_interactions.dialogue_handler import DialogueHandler
from app.handlers.entity_interactions.trade_handler import TradeHandler
from app.handlers.entity_interactions.combat_handler import CombatHandler

__all__ = [
    "DialogueHandler",
    "TradeHandler",
    "CombatHandler",
]
