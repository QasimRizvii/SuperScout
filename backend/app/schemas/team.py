"""
SuperScout Backend — Team Pydantic Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TeamBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    short_name: Optional[str] = Field(None, max_length=100)
    abbreviation: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    team_type: str = Field("franchise", max_length=50)
    logo_url: Optional[str] = Field(None, max_length=255)
    is_active: bool = True


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    short_name: Optional[str] = Field(None, max_length=100)
    abbreviation: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    team_type: Optional[str] = Field(None, max_length=50)
    logo_url: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class TeamResponse(TeamBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
