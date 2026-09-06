"""
SuperScout Backend — Venues API Endpoint
"""
import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.venue import VenueResponse
from app.schemas.common import PaginatedResponse
from app.services.venue_service import VenueService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[VenueResponse])
def list_venues(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    name: Optional[str] = Query(None, description="Filter by venue name"),
    city: Optional[str] = Query(None, description="Filter by city"),
    country: Optional[str] = Query(None, description="Filter by country"),
    db: Session = Depends(get_db),
):
    """
    List venues with pagination and filtering.
    """
    items, total = VenueService.get_venues(
        db, page=page, page_size=page_size, name=name, city=city, country=country
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse[VenueResponse](
        items=[VenueResponse.model_validate(v) for v in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{venue_id}", response_model=VenueResponse)
def get_venue(venue_id: int, db: Session = Depends(get_db)):
    """
    Fetch single venue by ID.
    """
    venue = VenueService.get_venue_by_id(db, venue_id)
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Venue with ID {venue_id} not found",
        )
    return VenueResponse.model_validate(venue)
