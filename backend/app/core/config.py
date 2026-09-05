"""
SuperScout Backend — Application Configuration

All settings are loaded from environment variables.
Never hardcode secrets here.
"""
from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    In development, values are read from a .env file in the project root.
    In production, set environment variables directly.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ────────────────────────────────────────────────────────────
    APP_NAME: str = "SuperScout API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── Server ─────────────────────────────────────────────────────────────────
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # ── Logging ────────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"

    # ── CORS ───────────────────────────────────────────────────────────────────
    # Comma-separated list of allowed origins, e.g. "http://localhost:3000"
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse the comma-separated ALLOWED_ORIGINS string into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    # ── Database ───────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://superscout:password@localhost:5432/superscout_db"

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith(("postgresql://", "postgresql+psycopg2://")):
            raise ValueError("DATABASE_URL must be a PostgreSQL connection string")
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the cached application settings singleton.

    Using lru_cache ensures settings are only parsed once per process,
    which is important for performance and testability.
    """
    return Settings()
