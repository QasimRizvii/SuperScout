"""
SuperScout Backend — Database Health Check

Provides a lightweight database connectivity check using a simple
SELECT 1 query. Never exposes credentials or connection details.
"""
from typing import Any, Dict

from sqlalchemy import text

from app.core.logging import get_logger
from app.db.session import SessionLocal

logger = get_logger(__name__)


def check_database_health() -> Dict[str, Any]:
    """
    Check whether the database is reachable.

    Returns a dict suitable for inclusion in the health endpoint response.
    Never raises an exception — failures are captured and reported gracefully.

    Returns:
        {
            "status": "healthy" | "unavailable",
            "detail": "Optional error description"
        }
    """
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as exc:
        logger.warning("Database health check failed: %s", str(exc))
        return {
            "status": "unavailable",
            "detail": "Database is not reachable. Check DATABASE_URL and ensure PostgreSQL is running.",
        }
