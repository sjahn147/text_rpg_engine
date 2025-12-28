"""
인터페이스 정의 모듈
Manager, Repository, Handler, Service의 인터페이스를 정의합니다.
"""

from app.interfaces.managers import (
    IEntityManager,
    ICellManager,
    IDialogueManager,
    IEffectCarrierManager,
    IInstanceManager
)

from app.interfaces.handlers import (
    IActionHandler
)

from app.interfaces.repositories import (
    IGameDataRepository,
    IRuntimeDataRepository,
    IReferenceLayerRepository
)

__all__ = [
    # Managers
    "IEntityManager",
    "ICellManager",
    "IDialogueManager",
    "IEffectCarrierManager",
    "IInstanceManager",
    # Handlers
    "IActionHandler",
    # Repositories
    "IGameDataRepository",
    "IRuntimeDataRepository",
    "IReferenceLayerRepository",
]

