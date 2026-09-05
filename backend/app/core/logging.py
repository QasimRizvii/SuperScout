"""
SuperScout Backend — Logging Configuration

Provides a consistent logging setup across the application.
"""
import logging
import sys
from typing import Optional

from app.core.config import get_settings


def configure_logging() -> None:
    """
    Configure the root logger for the application.

    - Development: human-readable format with color-friendly output
    - Production: structured format suitable for log aggregators

    Call this once during application startup (in main.py lifespan).
    """
    settings = get_settings()

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    if settings.DEBUG:
        fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        datefmt = "%H:%M:%S"
    else:
        # Production: structured format that log aggregators can parse
        fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
        datefmt = "%Y-%m-%dT%H:%M:%S"

    logging.basicConfig(
        level=log_level,
        format=fmt,
        datefmt=datefmt,
        stream=sys.stdout,
        force=True,
    )

    # Quiet down noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Return a named logger for a module.

    Usage:
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        logger.info("Server started")
    """
    return logging.getLogger(name or "superscout")
