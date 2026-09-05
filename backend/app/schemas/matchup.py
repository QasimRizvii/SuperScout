"""
SuperScout Backend — Player Matchup Pydantic Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.player import PlayerResponse


class PlayerMatchupBase(BaseModel):
    batter_id: int
    bowler_id: int
    matches: int = Field(0, ge=0)
    balls: int = Field(0, ge=0)
    runs: int = Field(0, ge=0)
    dismissals: int = Field(0, ge=0)
    fours: int = Field(0, ge=0)
    sixes: int = Field(0, ge=0)
    strike_rate: Optional[float] = Field(None, ge=0.0)
    average: Optional[float] = Field(None, ge=0.0)


class PlayerMatchupCreate(PlayerMatchupBase):
    pass


class PlayerMatchupResponse(PlayerMatchupBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    batter: Optional[PlayerResponse] = None
    bowler: Optional[PlayerResponse] = None
