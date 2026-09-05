"""
SuperScout Backend — Bowling Performance Model
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BowlingPerformance(Base):
    __tablename__ = "bowling_performances"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    innings_id: Mapped[int] = mapped_column(
        ForeignKey("innings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    overs: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    balls_bowled: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    maidens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    runs_conceded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    wickets: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    wides: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    no_balls: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    economy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    match = relationship("Match")
    innings = relationship("Innings", back_populates="bowling_performances")
    player = relationship("Player", foreign_keys=[player_id])
    team = relationship("Team")

    @staticmethod
    def calculate_economy(runs_conceded: int, balls_bowled: int, overs: float = 0.0) -> float:
        """
        Safely derive economy rate.

        If balls_bowled is present and > 0, calculate economy as runs per 6 balls.
        Otherwise if overs > 0, convert cricket overs notation (e.g., 3.4 overs = 22 balls)
        and compute safely.
        """
        total_balls = balls_bowled
        if total_balls <= 0 and overs > 0:
            full_overs = int(overs)
            part_balls = int(round((overs - full_overs) * 10))
            total_balls = (full_overs * 6) + part_balls

        if total_balls <= 0:
            return 0.0

        overs_decimal = total_balls / 6.0
        return round(runs_conceded / overs_decimal, 2)

    def update_economy(self) -> None:
        """Update self.economy using current runs_conceded and balls_bowled/overs."""
        self.economy = self.calculate_economy(self.runs_conceded, self.balls_bowled, self.overs)

    def __repr__(self) -> str:
        return f"<BowlingPerformance(id={self.id}, player_id={self.player_id}, wickets={self.wickets}, runs={self.runs_conceded})>"
