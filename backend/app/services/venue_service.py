"""
SuperScout Backend — Venue Service Layer
"""
from typing import Optional, Tuple, List
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.venue import Venue
from app.schemas.venue import VenueCreate


class VenueService:
    @staticmethod
    def get_venues(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        city: Optional[str] = None,
        country: Optional[str] = None,
    ) -> Tuple[List[Venue], int]:
        """Fetch paginated list of venues with optional filtering."""
        stmt = select(Venue)

        if city:
            stmt = stmt.where(Venue.city.ilike(f"%{city}%"))
        if country:
            stmt = stmt.where(Venue.country.ilike(f"%{country}%"))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0

        offset = (page - 1) * page_size
        stmt = stmt.order_by(Venue.name.asc()).offset(offset).limit(page_size)

        items = list(db.scalars(stmt).all())
        return items, total

    @staticmethod
    def get_venue_by_id(db: Session, venue_id: int) -> Optional[Venue]:
        """Fetch single venue by ID."""
        return db.scalar(select(Venue).where(Venue.id == venue_id))

    @staticmethod
    def create_venue(db: Session, venue_in: VenueCreate) -> Venue:
        """Create a new venue record."""
        venue = Venue(**venue_in.model_dump())
        db.add(venue)
        db.commit()
        db.refresh(venue)
        return venue
