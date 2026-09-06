"""
SuperScout Backend — Analytics API Endpoints

Provides RESTful endpoints for player analytics, batting/bowling stats, recent form,
Player Intelligence Score, and multi-player comparison.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.analytics import (
    PlayerAnalyticsService,
    PlayerNotFoundError,
    InvalidComparisonError,
)
from app.services.analytics.schemas import (
    BattingAnalyticsResponse,
    BowlingAnalyticsResponse,
    IntelligenceScoreResponse,
    PlayerAnalyticsOverviewResponse,
    PlayerComparisonResponse,
    RecentFormResponse,
)

router = APIRouter()


@router.get(
    "/compare",
    response_model=PlayerComparisonResponse,
    summary="Compare 2 to 5 players head-to-head",
)
def compare_players(
    player_ids: List[int] = Query(..., description="List of 2 to 5 player IDs to compare"),
    db: Session = Depends(get_db),
):
    """Compare multiple players side-by-side across key statistical metrics."""
    service = PlayerAnalyticsService(db)
    try:
        return service.compare_players(player_ids)
    except PlayerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidComparisonError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{player_id}/analytics",
    response_model=PlayerAnalyticsOverviewResponse,
    summary="Get complete player analytics overview",
)
def get_player_analytics_overview(
    player_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve full unified analytics dashboard profile for a player."""
    service = PlayerAnalyticsService(db)
    try:
        return service.compute_overview(player_id)
    except PlayerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/{player_id}/batting-analytics",
    response_model=BattingAnalyticsResponse,
    summary="Get player batting analytics",
)
def get_player_batting_analytics(
    player_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve detailed batting statistics and phase breakdown for a player."""
    service = PlayerAnalyticsService(db)
    try:
        return service.compute_batting_analytics(player_id)
    except PlayerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/{player_id}/bowling-analytics",
    response_model=BowlingAnalyticsResponse,
    summary="Get player bowling analytics",
)
def get_player_bowling_analytics(
    player_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve detailed bowling statistics and phase breakdown for a player."""
    service = PlayerAnalyticsService(db)
    try:
        return service.compute_bowling_analytics(player_id)
    except PlayerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/{player_id}/recent-form",
    response_model=RecentFormResponse,
    summary="Get player recent form window",
)
def get_player_recent_form(
    player_id: int,
    limit: int = Query(5, ge=1, le=50, description="Number of recent matches to include"),
    db: Session = Depends(get_db),
):
    """Retrieve recent match form analysis for a player."""
    service = PlayerAnalyticsService(db)
    try:
        return service.compute_recent_form(player_id, window=limit)
    except PlayerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/{player_id}/intelligence-score",
    response_model=IntelligenceScoreResponse,
    summary="Get player intelligence score",
)
def get_player_intelligence_score(
    player_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve explainable statistical Player Intelligence Score for a player."""
    service = PlayerAnalyticsService(db)
    try:
        return service.compute_intelligence_score(player_id)
    except PlayerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
