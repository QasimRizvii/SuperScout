"""
SuperScout Backend — Venue Pydantic Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class VenueBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    capacity: Optional[int] = Field(None, ge=0)
    pitch_type: Optional[str] = Field(None, max_length=100)


class VenueCreate(VenueBase):
    pass


class VenueUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    capacity: Optional[int] = Field(None, ge=0)
    pitch_type: Optional[str] = Field(None, max_length=100)


class VenueResponse(VenueBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
