"""
SuperScout Backend — Venue Model
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, DateTime, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Venue(Base):
    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pitch_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    timezone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint("capacity IS NULL OR capacity >= 0", name="chk_venue_capacity_non_negative"),
    )

    def __repr__(self) -> str:
        return f"<Venue(id={self.id}, name='{self.name}', city='{self.city}')>"
