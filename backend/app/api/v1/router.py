"""
SuperScout Backend — API v1 Router

Aggregates all v1 endpoint routers under the /api/v1 prefix.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    players,
    teams,
    venues,
    matches,
    auctions,
    analytics,
)

router = APIRouter(prefix="/api/v1")

# ── System ─────────────────────────────────────────────────────────────────────
router.include_router(health.router)

# ── Phase 2 & Step 4 Routers ───────────────────────────────────────────────────
router.include_router(analytics.router, prefix="/players", tags=["Player Analytics"])
router.include_router(players.router, prefix="/players", tags=["Players"])
router.include_router(teams.router, prefix="/teams", tags=["Teams"])
router.include_router(venues.router, prefix="/venues", tags=["Venues"])
router.include_router(matches.router, prefix="/matches", tags=["Matches"])
router.include_router(auctions.router, prefix="/auctions", tags=["Auctions"])

