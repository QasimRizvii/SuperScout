"""
SuperScout Backend — Innings Model
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, Float, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Innings(Base):
    __tablename__ = "innings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    innings_number: Mapped[int] = mapped_column(Integer, nullable=False)
    batting_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    bowling_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    total_runs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    wickets: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    overs: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    run_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    extras: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    powerplay_runs: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("match_id", "innings_number", name="uq_match_innings_number"),
        CheckConstraint("total_runs >= 0", name="chk_innings_total_runs_non_negative"),
        CheckConstraint("wickets >= 0 AND wickets <= 10", name="chk_innings_wickets_valid"),
        CheckConstraint("overs >= 0.0", name="chk_innings_overs_non_negative"),
        CheckConstraint("extras >= 0", name="chk_innings_extras_non_negative"),
    )

    # Relationships
    match = relationship("Match", back_populates="innings")
    batting_team = relationship("Team", foreign_keys=[batting_team_id])
    bowling_team = relationship("Team", foreign_keys=[bowling_team_id])
    batting_performances = relationship("BattingPerformance", back_populates="innings", cascade="all, delete-orphan")
    bowling_performances = relationship("BowlingPerformance", back_populates="innings", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Innings(id={self.id}, match_id={self.match_id}, innings_number={self.innings_number})>"
