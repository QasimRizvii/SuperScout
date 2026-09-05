"""
SuperScout Backend — Matches API Endpoint
"""
import math
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.match import MatchResponse
from app.schemas.common import PaginatedResponse
from app.services.match_service import MatchService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[MatchResponse])
def list_matches(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    season: Optional[str] = Query(None, description="Filter by season"),
    team_id: Optional[int] = Query(None, description="Filter by team (team 1 or team 2)"),
    venue_id: Optional[int] = Query(None, description="Filter by venue ID"),
    match_date: Optional[date] = Query(None, description="Filter by match date"),
    db: Session = Depends(get_db),
):
    """
    List matches with pagination and filtering.
    """
    items, total = MatchService.get_matches(
        db, page=page, page_size=page_size, season=season, team_id=team_id, venue_id=venue_id, match_date=match_date
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse[MatchResponse](
        items=[MatchResponse.model_validate(m) for m in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{match_id}", response_model=MatchResponse)
def get_match(match_id: int, db: Session = Depends(get_db)):
    """
    Fetch single match by ID.
    """
    match = MatchService.get_match_by_id(db, match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID {match_id} not found",
        )
    return MatchResponse.model_validate(match)
