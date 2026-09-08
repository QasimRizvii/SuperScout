"""
SuperScout Backend — Scouting ORM Models

Models for persistent Scouting Watchlists and structured Scouting Notes.
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import WatchlistStatus, WatchlistPriority, ScoutingNoteCategory


class ScoutingWatchlist(Base):
    __tablename__ = "scouting_watchlists"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True
    )
    priority: Mapped[WatchlistPriority] = mapped_column(
        SQLEnum(WatchlistPriority, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=WatchlistPriority.MEDIUM,
        index=True,
    )
    status: Mapped[WatchlistStatus] = mapped_column(
        SQLEnum(WatchlistStatus, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=WatchlistStatus.NEW,
        index=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    player = relationship("Player", backref="watchlist_entries", lazy="joined")

    def __repr__(self) -> str:
        return f"<ScoutingWatchlist(id={self.id}, player_id={self.player_id}, status='{self.status}', priority='{self.priority}')>"


class ScoutingNote(Base):
    __tablename__ = "scouting_notes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category: Mapped[ScoutingNoteCategory] = mapped_column(
        SQLEnum(ScoutingNoteCategory, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ScoutingNoteCategory.GENERAL,
        index=True,
    )
    observation: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    author: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default="Scout Analyst")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    player = relationship("Player", backref="scouting_notes", lazy="joined")

    def __repr__(self) -> str:
        return f"<ScoutingNote(id={self.id}, player_id={self.player_id}, category='{self.category}')>"
