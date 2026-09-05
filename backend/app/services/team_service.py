"""
SuperScout Backend — Team Service Layer
"""
from typing import Optional, Tuple, List
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.team import Team
from app.schemas.team import TeamCreate


class TeamService:
    @staticmethod
    def get_teams(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        name: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[Team], int]:
        """Fetch paginated list of teams with optional filtering."""
        stmt = select(Team)

        if name:
            stmt = stmt.where(Team.name.ilike(f"%{name}%"))
        if is_active is not None:
            stmt = stmt.where(Team.is_active == is_active)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0

        offset = (page - 1) * page_size
        stmt = stmt.order_by(Team.name.asc()).offset(offset).limit(page_size)

        items = list(db.scalars(stmt).all())
        return items, total

    @staticmethod
    def get_team_by_id(db: Session, team_id: int) -> Optional[Team]:
        """Fetch single team by ID."""
        return db.scalar(select(Team).where(Team.id == team_id))

    @staticmethod
    def create_team(db: Session, team_in: TeamCreate) -> Team:
        """Create a new team record."""
        team = Team(**team_in.model_dump())
        db.add(team)
        db.commit()
        db.refresh(team)
        return team
