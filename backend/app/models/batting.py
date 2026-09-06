"""
SuperScout Backend — Batting Performance Model
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, Float, String, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BattingPerformance(Base):
    __tablename__ = "batting_performances"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    innings_id: Mapped[int] = mapped_column(
        ForeignKey("innings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    batting_position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    runs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    balls_faced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    fours: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sixes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dot_balls: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    runs_powerplay: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    runs_middle: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    runs_death: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    strike_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    dismissal_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    dismissed_by_player_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("players.id"), nullable=True
    )
    fielder_player_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("players.id"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint("runs >= 0", name="chk_batting_runs_non_negative"),
        CheckConstraint("balls_faced >= 0", name="chk_batting_balls_non_negative"),
        CheckConstraint("fours >= 0", name="chk_batting_fours_non_negative"),
        CheckConstraint("sixes >= 0", name="chk_batting_sixes_non_negative"),
        CheckConstraint("dot_balls >= 0", name="chk_batting_dot_balls_non_negative"),
    )

    # Relationships
    match = relationship("Match")
    innings = relationship("Innings", back_populates="batting_performances")
    player = relationship("Player", foreign_keys=[player_id])
    team = relationship("Team")
    dismissed_by = relationship("Player", foreign_keys=[dismissed_by_player_id])
    fielder = relationship("Player", foreign_keys=[fielder_player_id])

    @property
    def boundary_percentage(self) -> Optional[float]:
        """Calculates boundary percentage safely avoiding division by zero."""
        if self.runs <= 0:
            return 0.0
        boundary_runs = (self.fours * 4) + (self.sixes * 6)
        return round((boundary_runs / self.runs) * 100.0, 2)

    @property
    def balls_per_boundary(self) -> Optional[float]:
        """Calculates balls per boundary safely avoiding division by zero."""
        total_boundaries = self.fours + self.sixes
        if total_boundaries <= 0:
            return None
        return round(self.balls_faced / total_boundaries, 2)

    @staticmethod
    def calculate_strike_rate(runs: int, balls_faced: int) -> float:
        """Safely derive strike rate avoiding division by zero."""
        if balls_faced <= 0:
            return 0.0
        return round((runs / balls_faced) * 100.0, 2)

    def update_strike_rate(self) -> None:
        """Update self.strike_rate from current runs and balls_faced."""
        self.strike_rate = self.calculate_strike_rate(self.runs, self.balls_faced)

    def __repr__(self) -> str:
        return f"<BattingPerformance(id={self.id}, player_id={self.player_id}, runs={self.runs}, balls={self.balls_faced})>"
