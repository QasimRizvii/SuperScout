"""
SuperScout Backend — Player Service Layer
"""
from typing import Optional, Tuple, List
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.player import Player
from app.models.enums import PlayerRole
from app.schemas.player import PlayerCreate, PlayerUpdate


class PlayerService:
    @staticmethod
    def get_players(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        name: Optional[str] = None,
        role: Optional[PlayerRole] = None,
        nationality: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[Player], int]:
        """
        Fetch paginated list of players with optional filtering.

        Returns (items, total_count).
        """
        stmt = select(Player)

        if name:
            stmt = stmt.where(Player.name.ilike(f"%{name}%"))
        if role:
            stmt = stmt.where(Player.role == role)
        if nationality:
            stmt = stmt.where(Player.nationality.ilike(f"%{nationality}%"))
        if is_active is not None:
            stmt = stmt.where(Player.is_active == is_active)

        # Count total matching records
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0

        # Apply pagination & sorting
        offset = (page - 1) * page_size
        stmt = stmt.order_by(Player.name.asc()).offset(offset).limit(page_size)

        items = list(db.scalars(stmt).all())
        return items, total

    @staticmethod
    def get_player_by_id(db: Session, player_id: int) -> Optional[Player]:
        """Fetch single player by ID."""
        return db.scalar(select(Player).where(Player.id == player_id))

    @staticmethod
    def create_player(db: Session, player_in: PlayerCreate) -> Player:
        """Create a new player record."""
        player = Player(**player_in.model_dump())
        db.add(player)
        db.commit()
        db.refresh(player)
        return player
