"""
SuperScout Backend — Health Response Schemas
"""
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel


class DatabaseStatus(BaseModel):
    """Database connectivity status."""

    status: Literal["healthy", "unavailable"]
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    """Response schema for GET /api/v1/health."""

    status: Literal["healthy"]
    service: str
    version: str
    database: DatabaseStatus
