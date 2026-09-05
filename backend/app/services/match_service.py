"""
SuperScout Backend — Match Service Layer
"""
from datetime import date
from typing import Optional, Tuple, List
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from app.models.match import Match
from app.schemas.match import MatchCreate


class MatchService:
    @staticmethod
    def get_matches(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        season: Optional[str] = None,
        team_id: Optional[int] = None,
        venue_id: Optional[int] = None,
        match_date: Optional[date] = None,
    ) -> Tuple[List[Match], int]:
        """Fetch paginated list of matches with optional filtering."""
        stmt = select(Match)

        if season:
            stmt = stmt.where(Match.season == season)
        if team_id:
            stmt = stmt.where(
                or_(Match.team_1_id == team_id, Match.team_2_id == team_id)
            )
        if venue_id:
            stmt = stmt.where(Match.venue_id == venue_id)
        if match_date:
            stmt = stmt.where(Match.match_date == match_date)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0

        offset = (page - 1) * page_size
        stmt = stmt.order_by(Match.match_date.desc()).offset(offset).limit(page_size)

        items = list(db.scalars(stmt).all())
        return items, total

    @staticmethod
    def get_match_by_id(db: Session, match_id: int) -> Optional[Match]:
        """Fetch single match by ID."""
        return db.scalar(select(Match).where(Match.id == match_id))

    @staticmethod
    def create_match(db: Session, match_in: MatchCreate) -> Match:
        """Create a new match record."""
        match = Match(**match_in.model_dump())
        db.add(match)
        db.commit()
        db.refresh(match)
        return match
