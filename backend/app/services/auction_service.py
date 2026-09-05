"""
SuperScout Backend — Auction Service Layer
"""
from typing import Optional, Tuple, List
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.auction import Auction
from app.models.enums import AuctionType
from app.schemas.auction import AuctionCreate


class AuctionService:
    @staticmethod
    def get_auctions(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        season: Optional[str] = None,
        auction_type: Optional[AuctionType] = None,
    ) -> Tuple[List[Auction], int]:
        """Fetch paginated list of auctions with optional filtering."""
        stmt = select(Auction)

        if season:
            stmt = stmt.where(Auction.season == season)
        if auction_type:
            stmt = stmt.where(Auction.auction_type == auction_type)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0

        offset = (page - 1) * page_size
        stmt = stmt.order_by(Auction.season.desc()).offset(offset).limit(page_size)

        items = list(db.scalars(stmt).all())
        return items, total

    @staticmethod
    def get_auction_by_id(db: Session, auction_id: int) -> Optional[Auction]:
        """Fetch single auction by ID."""
        return db.scalar(select(Auction).where(Auction.id == auction_id))

    @staticmethod
    def create_auction(db: Session, auction_in: AuctionCreate) -> Auction:
        """Create a new auction record."""
        auction = Auction(**auction_in.model_dump())
        db.add(auction)
        db.commit()
        db.refresh(auction)
        return auction
