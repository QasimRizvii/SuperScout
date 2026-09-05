"""
SuperScout Backend — Auction and AuctionTransaction Pydantic Schemas
"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AuctionType, AuctionStatus
from app.schemas.player import PlayerResponse
from app.schemas.team import TeamResponse


class AuctionTransactionBase(BaseModel):
    auction_id: int
    player_id: int
    team_id: Optional[int] = None
    base_price: float = Field(0.0, ge=0.0)
    final_price: float = Field(0.0, ge=0.0)
    status: AuctionStatus = AuctionStatus.SOLD
    purse_before: Optional[float] = Field(None, ge=0.0)
    purse_after: Optional[float] = Field(None, ge=0.0)


class AuctionTransactionCreate(AuctionTransactionBase):
    pass


class AuctionTransactionResponse(AuctionTransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    player: Optional[PlayerResponse] = None
    team: Optional[TeamResponse] = None


class AuctionBase(BaseModel):
    season: str = Field(..., max_length=50)
    auction_name: str = Field(..., max_length=150)
    auction_date: Optional[date] = None
    auction_type: AuctionType = AuctionType.MEGA


class AuctionCreate(AuctionBase):
    pass


class AuctionUpdate(BaseModel):
    season: Optional[str] = None
    auction_name: Optional[str] = None
    auction_date: Optional[date] = None
    auction_type: Optional[AuctionType] = None


class AuctionResponse(AuctionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    transactions: List[AuctionTransactionResponse] = []
