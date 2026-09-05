"""
SuperScout Backend — Health Endpoint

GET /api/v1/health

Returns the API health status and database connectivity status.
This is the primary liveness/readiness check for the application.
"""
from fastapi import APIRouter

from app.core.config import get_settings
from app.db.health import check_database_health
from app.schemas.health import DatabaseStatus, HealthResponse

router = APIRouter()
settings = get_settings()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check API liveness and database connectivity.",
    tags=["system"],
)
def health_check() -> HealthResponse:
    """
    Return the current health status of the SuperScout API.

    - **status**: Always 'healthy' if this endpoint responds (API is running).
    - **service**: Service name.
    - **version**: Current API version.
    - **database**: Database connectivity status (healthy | unavailable).
    """
    db_health = check_database_health()

    return HealthResponse(
        status="healthy",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        database=DatabaseStatus(**db_health),
    )
