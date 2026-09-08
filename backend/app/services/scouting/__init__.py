"""
SuperScout Backend — Scouting Package
"""
from app.services.scouting.exceptions import (
    ScoutingError,
    PlayerNotFoundError,
    WatchlistNotFoundError,
    ScoutingNoteNotFoundError,
    InvalidScoutingFilterError,
)
from app.services.scouting.schemas import (
    ScoutingProfileResponse,
    PlayerDiscoveryResponse,
    CandidateRankingResponse,
    UndervaluedPlayerResponse,
    RoleTargetResponse,
    ScoutingRecommendationResponse,
    ScoutingReportResponse,
    TacticalRoleFitResponse,
    WatchlistCreateRequest,
    WatchlistUpdateRequest,
    WatchlistResponse,
    ScoutingNoteCreateRequest,
    ScoutingNoteResponse,
)
from app.services.scouting.scouting_service import ScoutingService

__all__ = [
    "ScoutingError",
    "PlayerNotFoundError",
    "WatchlistNotFoundError",
    "ScoutingNoteNotFoundError",
    "InvalidScoutingFilterError",
    "ScoutingService",
]
