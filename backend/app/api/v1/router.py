"""
SuperScout Backend — API v1 Router

Aggregates all v1 endpoint routers under the /api/v1 prefix.
Add new feature routers here as Phase 2+ modules are implemented.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import health

router = APIRouter(prefix="/api/v1")

# ── System ─────────────────────────────────────────────────────────────────────
router.include_router(health.router)

# ── Future Cricket Intelligence Routers (Phase 2+) ────────────────────────────
# router.include_router(players.router,    prefix="/players",    tags=["players"])
# router.include_router(squads.router,     prefix="/squads",     tags=["squads"])
# router.include_router(auction.router,    prefix="/auction",    tags=["auction"])
# router.include_router(matches.router,    prefix="/matches",    tags=["matches"])
# router.include_router(matchups.router,   prefix="/matchups",   tags=["matchups"])
# router.include_router(playing_xi.router, prefix="/playing-xi", tags=["playing-xi"])
# router.include_router(super_over.router, prefix="/super-over", tags=["super-over"])
