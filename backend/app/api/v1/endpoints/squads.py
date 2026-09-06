"""
SuperScout Backend — Squad Intelligence API Endpoints

Provides RESTful endpoints for squad intelligence, balance audits, Playing XI recommendations,
role coverage analysis, gap recruitment, scenario simulations, and side-by-side squad comparison.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.squad import (
    SquadIntelligenceService,
    SquadNotFoundError,
    InsufficientSquadSizeError,
    OptimizationError,
)
from app.services.squad.schemas import (
    PlayingXIOptimizationResponse,
    RoleGapRecommendation,
    ScenarioAnalysisRequest,
    ScenarioAnalysisResponse,
    SquadBalanceResponse,
    SquadComparisonResponse,
    SquadIntelligenceOverviewResponse,
    SquadRoleAnalysisResponse,
)

router = APIRouter()


@router.get(
    "/compare",
    response_model=SquadComparisonResponse,
    summary="Compare two team squads side-by-side",
)
def compare_squads(
    team_1_id: int = Query(..., description="First team ID to compare"),
    team_2_id: int = Query(..., description="Second team ID to compare"),
    db: Session = Depends(get_db),
):
    """Compare two team squads head-to-head across 12 statistical dimensions."""
    service = SquadIntelligenceService(db)
    try:
        return service.compare_squads(team_1_id, team_2_id)
    except SquadNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/{team_id}/intelligence",
    response_model=SquadIntelligenceOverviewResponse,
    summary="Get complete squad intelligence overview",
)
def get_squad_intelligence(
    team_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve full unified squad dashboard profile."""
    service = SquadIntelligenceService(db)
    try:
        return service.get_overview(team_id)
    except SquadNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/{team_id}/balance",
    response_model=SquadBalanceResponse,
    summary="Get squad balance score and audit",
)
def get_squad_balance(
    team_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve 17-dimension squad balance score, strengths, and weaknesses."""
    service = SquadIntelligenceService(db)
    try:
        return service.compute_squad_balance(team_id)
    except SquadNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/{team_id}/playing-xi",
    response_model=PlayingXIOptimizationResponse,
    summary="Get recommended Playing XI",
)
def get_recommended_playing_xi(
    team_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve constraint-satisfied recommended Playing XI lineup with selection justifications."""
    service = SquadIntelligenceService(db)
    try:
        return service.optimize_playing_xi(team_id)
    except SquadNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InsufficientSquadSizeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except OptimizationError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/{team_id}/role-analysis",
    response_model=SquadRoleAnalysisResponse,
    summary="Get squad role and phase coverage analysis",
)
def get_squad_role_analysis(
    team_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve detailed role distribution, pace/spin split, and phase coverage."""
    service = SquadIntelligenceService(db)
    try:
        return service.analyze_role_coverage(team_id)
    except SquadNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/{team_id}/gaps",
    response_model=List[RoleGapRecommendation],
    summary="Get squad role gaps and recruitment recommendations",
)
def get_squad_role_gaps(
    team_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve identified squad role deficiencies and recruitment candidate recommendations."""
    service = SquadIntelligenceService(db)
    try:
        return service.identify_gaps(team_id)
    except SquadNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/{team_id}/scenarios",
    response_model=ScenarioAnalysisResponse,
    summary="Simulate unavailable players scenario",
)
def simulate_squad_scenario(
    team_id: int,
    body: ScenarioAnalysisRequest,
    db: Session = Depends(get_db),
):
    """Simulate squad balance impact and bench replacement options when key players are unavailable."""
    service = SquadIntelligenceService(db)
    try:
        return service.simulate_scenario(team_id, body.unavailable_player_ids)
    except SquadNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
