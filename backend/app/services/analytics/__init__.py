"""
SuperScout Backend — Analytics Package Initializer
"""
from app.services.analytics.exceptions import (
    AnalyticsError,
    PlayerNotFoundError,
    InsufficientDataError,
    InvalidComparisonError,
)
from app.services.analytics.player import PlayerAnalyticsService

__all__ = [
    "AnalyticsError",
    "PlayerNotFoundError",
    "InsufficientDataError",
    "InvalidComparisonError",
    "PlayerAnalyticsService",
]
