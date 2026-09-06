"""
SuperScout Backend — Match Model
"""
from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import String, Date, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import MatchType


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True, index=True)
    season: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    match_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    match_type: Mapped[MatchType] = mapped_column(
        SQLEnum(MatchType, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=MatchType.T20,
        index=True,
    )
    competition: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(50), default="completed", nullable=False, index=True)
    venue_id: Mapped[int] = mapped_column(ForeignKey("venues.id"), nullable=False, index=True)
    team_1_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False, index=True)
    team_2_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False, index=True)
    winner_team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"), nullable=True)
    toss_winner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"), nullable=True)
    toss_decision: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    result_description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    venue = relationship("Venue", foreign_keys=[venue_id])
    team_1 = relationship("Team", foreign_keys=[team_1_id])
    team_2 = relationship("Team", foreign_keys=[team_2_id])
    winner_team = relationship("Team", foreign_keys=[winner_team_id])
    toss_winner = relationship("Team", foreign_keys=[toss_winner_id])
    innings = relationship("Innings", back_populates="match", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Match(id={self.id}, season='{self.season}', date={self.match_date})>"
