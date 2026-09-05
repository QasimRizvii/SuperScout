"""
SuperScout Backend — Database Session Management

Provides the SQLAlchemy engine, session factory, and a FastAPI
dependency for injecting database sessions into route handlers.
"""
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

settings = get_settings()

# ── Engine ─────────────────────────────────────────────────────────────────────
# pool_pre_ping=True ensures stale connections are detected and recycled
# automatically, which prevents "server closed the connection" errors.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,  # Log SQL statements only in debug mode
)

# ── Session Factory ────────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# ── FastAPI Dependency ─────────────────────────────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session.

    Each request gets its own session. The session is automatically
    closed (and rolled back on error) when the request completes.

    Usage:
        @router.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
