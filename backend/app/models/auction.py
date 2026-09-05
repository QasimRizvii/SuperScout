"""
SuperScout Backend — Auction and AuctionTransaction Models
"""
from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import String, Date, Float, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AuctionType, AuctionStatus


class Auction(Base):
    __tablename__ = "auctions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    season: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    auction_name: Mapped[str] = mapped_column(String(150), nullable=False)
    auction_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    auction_type: Mapped[AuctionType] = mapped_column(
        SQLEnum(AuctionType, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=AuctionType.MEGA,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    transactions = relationship(
        "AuctionTransaction", back_populates="auction", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Auction(id={self.id}, name='{self.auction_name}', season='{self.season}')>"


class AuctionTransaction(Base):
    __tablename__ = "auction_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    auction_id: Mapped[int] = mapped_column(
        ForeignKey("auctions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False, index=True)
    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"), nullable=True)
    base_price: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    final_price: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[AuctionStatus] = mapped_column(
        SQLEnum(AuctionStatus, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=AuctionStatus.SOLD,
        index=True,
    )
    purse_before: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    purse_after: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    auction = relationship("Auction", back_populates="transactions")
    player = relationship("Player")
    team = relationship("Team")

    def __repr__(self) -> str:
        return f"<AuctionTransaction(id={self.id}, player_id={self.player_id}, status='{self.status}', price={self.final_price})>"
