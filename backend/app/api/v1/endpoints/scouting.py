"""
SuperScout Backend — Scouting & Decision-Support REST API Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.enums import (
    WatchlistPriority,
    WatchlistStatus,
    ScoutingNoteCategory,
)
from app.services.scouting import (
    PlayerNotFoundError,
    WatchlistNotFoundError,
    ScoutingNoteNotFoundError,
    ScoutingService,
)
from app.services.scouting.schemas import (
    CandidateRankingResponse,
    PlayerDiscoveryResponse,
    RankingWeightsSchema,
    RoleTargetResponse,
    ScoutingNoteCreateRequest,
    ScoutingNoteResponse,
    ScoutingProfileResponse,
    ScoutingRecommendationResponse,
    ScoutingReportResponse,
    TacticalRoleFitResponse,
    UndervaluedPlayerResponse,
    WatchlistCreateRequest,
    WatchlistResponse,
    WatchlistUpdateRequest,
)

router = APIRouter()


# ── 1. Scouting Profile ────────────────────────────────────────────────────────

@router.get("/player/{player_id}", response_model=ScoutingProfileResponse)
def get_scouting_profile(
    player_id: int,
    team_id: Optional[int] = Query(None, description="Optional team context for squad fit evaluation"),
    db: Session = Depends(get_db),
):
    """Fetch unified evidence-based scouting profile for player."""
    svc = ScoutingService(db)
    try:
        return svc.get_scouting_profile(player_id, team_id=team_id)
    except PlayerNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {player_id} not found",
        )


# ── 2. Player Discovery Engine ─────────────────────────────────────────────────

@router.get("/discover", response_model=PlayerDiscoveryResponse)
def discover_players(
    role: Optional[str] = Query(None, description="Filter by role"),
    batting_style: Optional[str] = Query(None, description="Filter by batting style"),
    bowling_style: Optional[str] = Query(None, description="Filter by bowling style"),
    nationality: Optional[str] = Query(None, description="Filter by nationality"),
    is_wicketkeeper: Optional[bool] = Query(None, description="Filter wicketkeeper status"),
    is_active: Optional[bool] = Query(True, description="Filter active status"),
    min_intelligence_score: Optional[float] = Query(None, ge=0.0, le=100.0),
    min_batting_strike_rate: Optional[float] = Query(None, ge=0.0),
    min_batting_average: Optional[float] = Query(None, ge=0.0),
    min_bowling_wickets: Optional[int] = Query(None, ge=0),
    max_economy: Optional[float] = Query(None, ge=0.0),
    min_recent_form_score: Optional[float] = Query(None, ge=0.0, le=100.0),
    min_consistency: Optional[float] = Query(None, ge=0.0, le=100.0),
    min_squad_fit: Optional[float] = Query(None, ge=0.0, le=100.0),
    team_id: Optional[int] = Query(None),
    sort_by: str = Query("intelligence_score", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Multi-criteria candidate discovery with sorting and pagination."""
    svc = ScoutingService(db)
    return svc.discover_players(
        role=role,
        batting_style=batting_style,
        bowling_style=bowling_style,
        nationality=nationality,
        is_wicketkeeper=is_wicketkeeper,
        is_active=is_active,
        min_intelligence_score=min_intelligence_score,
        min_batting_strike_rate=min_batting_strike_rate,
        min_batting_average=min_batting_average,
        min_bowling_wickets=min_bowling_wickets,
        max_economy=max_economy,
        min_recent_form_score=min_recent_form_score,
        min_consistency=min_consistency,
        min_squad_fit=min_squad_fit,
        team_id=team_id,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        size=size,
    )


# ── 3. Candidate Ranking Engine ────────────────────────────────────────────────

@router.post("/rank", response_model=CandidateRankingResponse)
def rank_candidates(
    weights: Optional[RankingWeightsSchema] = None,
    team_id: Optional[int] = Query(None),
    requested_role: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Rank candidate players using explicit, configurable multi-factor weights."""
    svc = ScoutingService(db)
    return svc.rank_candidates(weights=weights, team_id=team_id, requested_role=requested_role)


# ── 4. Undervalued Player Intelligence ─────────────────────────────────────────

@router.get("/undervalued", response_model=UndervaluedPlayerResponse)
def get_undervalued_players(
    team_id: Optional[int] = Query(None),
    min_undervaluation_score: float = Query(60.0, ge=0.0, le=100.0),
    db: Session = Depends(get_db),
):
    """Identify players who are statistically or strategically undervalued."""
    svc = ScoutingService(db)
    return svc.get_undervalued_players(team_id=team_id, min_undervaluation_score=min_undervaluation_score)


# ── 5. Role-Specific Target Engine ─────────────────────────────────────────────

@router.get("/role-targets", response_model=RoleTargetResponse)
def get_role_targets(
    role: str = Query(..., description="Requested role (e.g. opener, death_bowler, finisher, wicketkeeper)"),
    team_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """Find and rank candidate targets for a specific tactical cricket role."""
    svc = ScoutingService(db)
    return svc.get_role_targets(requested_role=role, team_id=team_id)


# ── 6. Scouting Recommendations ───────────────────────────────────────────────

@router.get("/recommendations", response_model=ScoutingRecommendationResponse)
def get_scouting_recommendations_get(
    team_id: Optional[int] = Query(None),
    budget: float = Query(1000.0, ge=0.0),
    slots_needed: int = Query(5, ge=1),
    db: Session = Depends(get_db),
):
    """Generate prioritized scouting targets for a franchise."""
    svc = ScoutingService(db)
    return svc.get_recommendations(team_id=team_id, budget=budget, slots_needed=slots_needed)


@router.post("/recommendations", response_model=ScoutingRecommendationResponse)
def get_scouting_recommendations_post(
    team_id: Optional[int] = Query(None),
    budget: float = Query(1000.0, ge=0.0),
    slots_needed: int = Query(5, ge=1),
    db: Session = Depends(get_db),
):
    """POST endpoint variant for scouting recommendations."""
    svc = ScoutingService(db)
    return svc.get_recommendations(team_id=team_id, budget=budget, slots_needed=slots_needed)


# ── 7. Scouting Report Generator ──────────────────────────────────────────────

@router.get("/report/{player_id}", response_model=ScoutingReportResponse)
def get_scouting_report(
    player_id: int,
    team_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """Generate structured machine-readable scouting report with explainable verdict."""
    svc = ScoutingService(db)
    try:
        return svc.get_scouting_report(player_id, team_id=team_id)
    except PlayerNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {player_id} not found",
        )


# ── 8. Tactical Role Simulation ───────────────────────────────────────────────

@router.get("/role-fit/{player_id}", response_model=TacticalRoleFitResponse)
def get_tactical_role_fit(
    player_id: int,
    role: str = Query(..., description="Role to evaluate (e.g. opener, finisher, powerplay, death)"),
    db: Session = Depends(get_db),
):
    """Evaluate candidate suitability and supporting metrics for a specific tactical scenario."""
    svc = ScoutingService(db)
    try:
        return svc.get_tactical_role_fit(player_id, evaluated_role=role)
    except PlayerNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {player_id} not found",
        )


# ── 9. Scouting Watchlist Endpoints ───────────────────────────────────────────

@router.get("/watchlist", response_model=List[WatchlistResponse])
def get_watchlist(
    priority: Optional[WatchlistPriority] = Query(None),
    status: Optional[WatchlistStatus] = Query(None),
    player_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """List persistent scouting watchlist entries."""
    svc = ScoutingService(db)
    return svc.get_watchlist(priority=priority, status=status, player_id=player_id)


@router.post("/watchlist", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
def add_to_watchlist(
    req: WatchlistCreateRequest,
    db: Session = Depends(get_db),
):
    """Add a player to persistent scouting watchlist."""
    svc = ScoutingService(db)
    try:
        return svc.add_to_watchlist(req)
    except PlayerNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {req.player_id} not found",
        )


@router.patch("/watchlist/{id}", response_model=WatchlistResponse)
def update_watchlist(
    id: int,
    req: WatchlistUpdateRequest,
    db: Session = Depends(get_db),
):
    """Update priority, status, notes, or tags for a watchlist entry."""
    svc = ScoutingService(db)
    try:
        return svc.update_watchlist(id, req)
    except WatchlistNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Watchlist entry with ID {id} not found",
        )


@router.delete("/watchlist/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_watchlist(
    id: int,
    db: Session = Depends(get_db),
):
    """Delete a player from persistent scouting watchlist."""
    svc = ScoutingService(db)
    try:
        svc.delete_watchlist(id)
        return None
    except WatchlistNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Watchlist entry with ID {id} not found",
        )


# ── 10. Scouting Notes Endpoints ──────────────────────────────────────────────

@router.get("/notes", response_model=List[ScoutingNoteResponse])
def get_scouting_notes_list(
    player_id: Optional[int] = Query(None),
    category: Optional[ScoutingNoteCategory] = Query(None),
    db: Session = Depends(get_db),
):
    """List structured scouting notes."""
    svc = ScoutingService(db)
    return svc.get_notes(player_id=player_id, category=category)


@router.get("/notes/{player_id}", response_model=List[ScoutingNoteResponse])
def get_scouting_notes_by_player(
    player_id: int,
    category: Optional[ScoutingNoteCategory] = Query(None),
    db: Session = Depends(get_db),
):
    """List structured scouting notes for a specific player."""
    svc = ScoutingService(db)
    try:
        svc.get_player_or_raise(player_id)
    except PlayerNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {player_id} not found",
        )
    return svc.get_notes(player_id=player_id, category=category)


@router.post("/notes", response_model=ScoutingNoteResponse, status_code=status.HTTP_201_CREATED)
def add_scouting_note(
    req: ScoutingNoteCreateRequest,
    db: Session = Depends(get_db),
):
    """Add a structured observation/note for a player."""
    svc = ScoutingService(db)
    try:
        return svc.add_note(req)
    except PlayerNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {req.player_id} not found",
        )
