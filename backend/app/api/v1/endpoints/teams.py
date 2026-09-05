"""
SuperScout Backend — Teams API Endpoint
"""
import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.team import TeamResponse
from app.schemas.common import PaginatedResponse
from app.services.team_service import TeamService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[TeamResponse])
def list_teams(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    name: Optional[str] = Query(None, description="Filter by team name"),
    is_active: Optional[bool] = Query(None, description="Filter active status"),
    db: Session = Depends(get_db),
):
    """
    List teams with pagination and filtering.
    """
    items, total = TeamService.get_teams(
        db, page=page, page_size=page_size, name=name, is_active=is_active
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse[TeamResponse](
        items=[TeamResponse.model_validate(t) for t in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(team_id: int, db: Session = Depends(get_db)):
    """
    Fetch single team by ID.
    """
    team = TeamService.get_team_by_id(db, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found",
        )
    return TeamResponse.model_validate(team)
