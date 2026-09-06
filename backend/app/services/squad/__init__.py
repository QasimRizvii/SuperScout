"""
SuperScout Backend — Squad Intelligence Package Initializer
"""
from app.services.squad.exceptions import (
    SquadError,
    SquadNotFoundError,
    InsufficientSquadSizeError,
    OptimizationError,
)
from app.services.squad.squad_service import SquadIntelligenceService

__all__ = [
    "SquadError",
    "SquadNotFoundError",
    "InsufficientSquadSizeError",
    "OptimizationError",
    "SquadIntelligenceService",
]
