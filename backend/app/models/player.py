"""
SuperScout Backend — Player Model
"""
from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Date, DateTime, Boolean, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import PlayerRole


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    short_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    role: Mapped[PlayerRole] = mapped_column(
        SQLEnum(PlayerRole, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=PlayerRole.BATTER,
        index=True,
    )
    batting_style: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    bowling_style: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    nationality: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Player(id={self.id}, name='{self.name}', role='{self.role}')>"
