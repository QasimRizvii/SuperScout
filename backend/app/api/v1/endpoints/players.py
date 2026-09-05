"""
SuperScout Backend — Players API Endpoint
"""
import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.enums import PlayerRole
from app.schemas.player import PlayerResponse
from app.schemas.common import PaginatedResponse
from app.services.player_service import PlayerService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[PlayerResponse])
def list_players(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    name: Optional[str] = Query(None, description="Filter by player name (partial match)"),
    role: Optional[PlayerRole] = Query(None, description="Filter by player role"),
    nationality: Optional[str] = Query(None, description="Filter by nationality"),
    is_active: Optional[bool] = Query(None, description="Filter active status"),
    db: Session = Depends(get_db),
):
    """
    List players with pagination and filtering.
    """
    items, total = PlayerService.get_players(
        db, page=page, page_size=page_size, name=name, role=role, nationality=nationality, is_active=is_active
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse[PlayerResponse](
        items=[PlayerResponse.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(player_id: int, db: Session = Depends(get_db)):
    """
    Fetch single player by ID.
    """
    player = PlayerService.get_player_by_id(db, player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {player_id} not found",
        )
    return PlayerResponse.model_validate(player)
