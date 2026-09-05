"""
SuperScout Backend — Player Matchup Model
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, Float, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PlayerMatchup(Base):
    __tablename__ = "player_matchups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    batter_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False, index=True)
    bowler_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False, index=True)
    matches: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    balls: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    runs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dismissals: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    fours: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sixes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    strike_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    average: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("batter_id", "bowler_id", name="uq_batter_bowler_matchup"),
    )

    # Relationships
    batter = relationship("Player", foreign_keys=[batter_id])
    bowler = relationship("Player", foreign_keys=[bowler_id])

    @staticmethod
    def calculate_strike_rate(runs: int, balls: int) -> float:
        """Safely derive strike rate avoiding division by zero."""
        if balls <= 0:
            return 0.0
        return round((runs / balls) * 100.0, 2)

    @staticmethod
    def calculate_average(runs: int, dismissals: int) -> Optional[float]:
        """Safely derive batting average against bowler (None if 0 dismissals)."""
        if dismissals <= 0:
            return None
        return round(runs / dismissals, 2)

    def update_derived_stats(self) -> None:
        """Update self.strike_rate and self.average."""
        self.strike_rate = self.calculate_strike_rate(self.runs, self.balls)
        self.average = self.calculate_average(self.runs, self.dismissals)

    def __repr__(self) -> str:
        return f"<PlayerMatchup(id={self.id}, batter_id={self.batter_id}, bowler_id={self.bowler_id}, runs={self.runs}, balls={self.balls})>"
