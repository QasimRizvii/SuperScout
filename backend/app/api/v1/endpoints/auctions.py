"""
SuperScout Backend — Auctions API Endpoint
"""
import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.enums import AuctionType
from app.schemas.auction import AuctionResponse
from app.schemas.common import PaginatedResponse
from app.services.auction_service import AuctionService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[AuctionResponse])
def list_auctions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    season: Optional[str] = Query(None, description="Filter by season"),
    auction_type: Optional[AuctionType] = Query(None, description="Filter by auction type"),
    db: Session = Depends(get_db),
):
    """
    List auctions with pagination and filtering.
    """
    items, total = AuctionService.get_auctions(
        db, page=page, page_size=page_size, season=season, auction_type=auction_type
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse[AuctionResponse](
        items=[AuctionResponse.model_validate(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{auction_id}", response_model=AuctionResponse)
def get_auction(auction_id: int, db: Session = Depends(get_db)):
    """
    Fetch single auction by ID.
    """
    auction = AuctionService.get_auction_by_id(db, auction_id)
    if not auction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Auction with ID {auction_id} not found",
        )
    return AuctionResponse.model_validate(auction)
