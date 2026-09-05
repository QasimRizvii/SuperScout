"""
SuperScout Backend — Player Pydantic Schemas
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import PlayerRole


class PlayerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    short_name: Optional[str] = Field(None, max_length=100)
    role: PlayerRole = PlayerRole.BATTER
    batting_style: Optional[str] = Field(None, max_length=100)
    bowling_style: Optional[str] = Field(None, max_length=100)
    nationality: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[date] = None
    is_active: bool = True


class PlayerCreate(PlayerBase):
    pass


class PlayerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    short_name: Optional[str] = Field(None, max_length=100)
    role: Optional[PlayerRole] = None
    batting_style: Optional[str] = Field(None, max_length=100)
    bowling_style: Optional[str] = Field(None, max_length=100)
    nationality: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[date] = None
    is_active: Optional[bool] = None


class PlayerResponse(PlayerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
