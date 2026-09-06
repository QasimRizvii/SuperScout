"""
SuperScout Backend — Auctions & Auction Intelligence API Endpoints

Provides RESTful endpoints for auction listing, player valuations, franchise target rankings,
purse budget allocation, fallback targets, opportunity cost, comparable analysis, and scenarios.
"""
import math
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.enums import AuctionType
from app.schemas.auction import AuctionResponse
from app.schemas.common import PaginatedResponse
from app.services.auction_service import AuctionService
from app.services.auction import (
    AuctionIntelligenceService,
    AuctionNotFoundError,
    InvalidPurseError,
)
from app.services.analytics.exceptions import PlayerNotFoundError
from app.services.squad.exceptions import SquadNotFoundError
from app.services.auction.schemas import (
    AlternativeTargetResponse,
    AuctionScenarioRequest,
    AuctionScenarioResponse,
    AuctionTargetRankingResponse,
    ComparablePlayerResponse,
    OpportunityCostResponse,
    PlayerValuationResponse,
    PurseBudgetAllocationResponse,
)

router = APIRouter()


@router.get("", response_model=PaginatedResponse[AuctionResponse])
def list_auctions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    season: Optional[str] = Query(None, description="Filter by season"),
    auction_type: Optional[AuctionType] = Query(None, description="Filter by auction type"),
    db: Session = Depends(get_db),
):
    """List auctions with pagination and filtering."""
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


@router.get("/{auction_id}/targets", response_model=AuctionTargetRankingResponse, summary="Get ranked auction targets for franchise")
def get_auction_targets(
    auction_id: int,
    team_id: int = Query(..., description="Franchise Team ID"),
    remaining_purse: float = Query(1000.0, ge=0.0, description="Remaining purse in INR Lakhs"),
    remaining_squad_slots: int = Query(5, ge=1, le=25, description="Remaining squad slots"),
    db: Session = Depends(get_db),
):
    """Retrieve ranked candidate auction targets for a franchise."""
    service = AuctionIntelligenceService(db)
    try:
        return service.rank_targets(
            auction_id=auction_id,
            team_id=team_id,
            remaining_purse=remaining_purse,
            remaining_squad_slots=remaining_squad_slots,
        )
    except SquadNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{auction_id}/valuation/{player_id}", response_model=PlayerValuationResponse, summary="Get player auction valuation")
def get_player_valuation(
    auction_id: int,
    player_id: int,
    team_id: Optional[int] = Query(None, description="Franchise Team ID for squad-fit calculation"),
    base_price: float = Query(20.0, ge=0.0, description="Player base price in INR Lakhs"),
    remaining_purse: float = Query(1000.0, ge=0.0, description="Remaining purse in INR Lakhs"),
    remaining_squad_slots: int = Query(5, ge=1, le=25, description="Remaining squad slots"),
    db: Session = Depends(get_db),
):
    """Retrieve estimated Fair Value and Recommended Maximum Bid Ceiling for a player."""
    service = AuctionIntelligenceService(db)
    try:
        return service.compute_player_valuation(
            auction_id=auction_id,
            player_id=player_id,
            team_id=team_id,
            base_price=base_price,
            remaining_purse=remaining_purse,
            remaining_squad_slots=remaining_squad_slots,
        )
    except PlayerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{auction_id}/budget", response_model=PurseBudgetAllocationResponse, summary="Get purse budget allocation strategy")
def get_budget_allocation(
    auction_id: int,
    team_id: int = Query(..., description="Franchise Team ID"),
    total_purse: float = Query(1000.0, ge=0.0, description="Total purse in INR Lakhs"),
    remaining_purse: float = Query(1000.0, ge=0.0, description="Remaining purse in INR Lakhs"),
    remaining_squad_slots: int = Query(5, ge=1, le=25, description="Remaining squad slots"),
    db: Session = Depends(get_db),
):
    """Retrieve dynamic purse budget allocation strategy across squad categories."""
    service = AuctionIntelligenceService(db)
    try:
        return service.allocate_purse(
            auction_id=auction_id,
            team_id=team_id,
            total_purse=total_purse,
            remaining_purse=remaining_purse,
            remaining_squad_slots=remaining_squad_slots,
        )
    except SquadNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidPurseError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{auction_id}/alternatives/{player_id}", response_model=AlternativeTargetResponse, summary="Get alternative fallback targets")
def get_alternative_targets(
    auction_id: int,
    player_id: int,
    team_id: int = Query(..., description="Franchise Team ID"),
    remaining_purse: float = Query(1000.0, ge=0.0, description="Remaining purse in INR Lakhs"),
    remaining_squad_slots: int = Query(5, ge=1, le=25, description="Remaining squad slots"),
    db: Session = Depends(get_db),
):
    """Retrieve recommended fallback targets if primary player exceeds max bid ceiling."""
    service = AuctionIntelligenceService(db)
    try:
        return service.get_alternative_targets(
            auction_id=auction_id,
            player_id=player_id,
            team_id=team_id,
            remaining_purse=remaining_purse,
            remaining_squad_slots=remaining_squad_slots,
        )
    except (PlayerNotFoundError, SquadNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{auction_id}/opportunity-cost/{player_id}", response_model=OpportunityCostResponse, summary="Get opportunity cost analysis")
def get_opportunity_cost(
    auction_id: int,
    player_id: int,
    proposed_bid: float = Query(..., ge=0.0, description="Proposed bid amount in INR Lakhs"),
    team_id: int = Query(..., description="Franchise Team ID"),
    remaining_purse: float = Query(1000.0, ge=0.0, description="Remaining purse in INR Lakhs"),
    remaining_squad_slots: int = Query(5, ge=1, le=25, description="Remaining squad slots"),
    db: Session = Depends(get_db),
):
    """Analyze financial trade-offs and sacrificed role coverage for a proposed bid."""
    service = AuctionIntelligenceService(db)
    try:
        return service.evaluate_opportunity_cost(
            auction_id=auction_id,
            player_id=player_id,
            team_id=team_id,
            proposed_bid=proposed_bid,
            remaining_purse=remaining_purse,
            remaining_squad_slots=remaining_squad_slots,
        )
    except (PlayerNotFoundError, SquadNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{auction_id}/comparables/{player_id}", response_model=ComparablePlayerResponse, summary="Get comparable player analysis")
def get_comparable_players(
    auction_id: int,
    player_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve statistically & strategically similar players and price benchmarks."""
    service = AuctionIntelligenceService(db)
    try:
        return service.get_comparables(auction_id=auction_id, player_id=player_id)
    except PlayerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{auction_id}/scenarios", response_model=AuctionScenarioResponse, summary="Simulate auction scenario")
def simulate_auction_scenario(
    auction_id: int,
    body: AuctionScenarioRequest,
    db: Session = Depends(get_db),
):
    """Simulate What-If auction transaction (acquisition, outbid, or price surge)."""
    service = AuctionIntelligenceService(db)
    try:
        return service.simulate_scenario(
            auction_id=auction_id,
            team_id=body.team_id,
            target_player_id=body.target_player_id,
            bid_price=body.bid_price,
            outcome=body.outcome,
        )
    except (PlayerNotFoundError, SquadNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{auction_id}", response_model=AuctionResponse)
def get_auction(auction_id: int, db: Session = Depends(get_db)):
    """Fetch single auction by ID."""
    auction = AuctionService.get_auction_by_id(db, auction_id)
    if not auction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Auction with ID {auction_id} not found",
        )
    return AuctionResponse.model_validate(auction)
