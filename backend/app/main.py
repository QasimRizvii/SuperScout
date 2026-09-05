"""
SuperScout Backend — FastAPI Application Entry Point

This module creates and configures the FastAPI application instance.
It wires together:
  - CORS middleware
  - API versioned routers
  - Error handlers
  - Startup / shutdown lifecycle hooks
  - Logging
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger

settings = get_settings()


# ── Lifespan ───────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.

    Code before `yield` runs at startup; code after `yield` runs at shutdown.
    This is the recommended FastAPI pattern for resource management.
    """
    # ── Startup ────────────────────────────────────────────────────────────────
    configure_logging()
    logger = get_logger(__name__)
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    logger.info("Debug mode: %s", settings.DEBUG)
    logger.info("Allowed CORS origins: %s", settings.allowed_origins_list)

    yield  # Application is running

    # ── Shutdown ───────────────────────────────────────────────────────────────
    logger.info("Shutting down %s", settings.APP_NAME)


# ── Application Factory ────────────────────────────────────────────────────────
def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns a fully configured app instance. Using a factory function
    makes the app easier to test (each test can get a fresh instance).
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "SuperScout — AI-Powered Cricket Auction & Match Intelligence Platform. "
            "Backend API for player analytics, squad intelligence, auction strategy, "
            "match intelligence, and simulation."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ───────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ────────────────────────────────────────────────────────────────
    app.include_router(v1_router)

    # ── Error Handlers ─────────────────────────────────────────────────────────
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"Resource not found: {request.url.path}"},
        )

    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger = get_logger(__name__)
        logger.error("Unhandled exception: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An internal server error occurred."},
        )

    return app


# ── Application Instance ───────────────────────────────────────────────────────
# This is the object uvicorn imports: `uvicorn app.main:app`
app = create_app()
