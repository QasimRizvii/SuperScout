"""
SuperScout Backend — Player Discovery Engine

Executes efficient, multi-criteria candidate discovery, sorting, and pagination.
"""
import math
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session

from app.models.player import Player
from app.services.analytics.player import PlayerAnalyticsService
from app.services.analytics.schemas import PlayerAnalyticsOverviewResponse
from app.services.auction.squad_fit_engine import SquadFitEngine
from app.services.auction.valuation_engine import ValuationEngine
from app.services.scouting.schemas import (
    DiscoveredPlayerItem,
    PlayerDiscoveryResponse,
)
from app.services.squad.squad_service import SquadIntelligenceService


class PlayerDiscoveryEngine:
    """Multi-factor player search and filter discovery engine."""

    def __init__(self, db: Session):
        self.db = db
        self.analytics_svc = PlayerAnalyticsService(db)
        self.squad_svc = SquadIntelligenceService(db)

    def discover_players(
        self,
        role: Optional[str] = None,
        batting_style: Optional[str] = None,
        bowling_style: Optional[str] = None,
        nationality: Optional[str] = None,
        is_wicketkeeper: Optional[bool] = None,
        is_active: Optional[bool] = True,
        min_intelligence_score: Optional[float] = None,
        min_batting_strike_rate: Optional[float] = None,
        min_batting_average: Optional[float] = None,
        min_bowling_wickets: Optional[int] = None,
        max_economy: Optional[float] = None,
        min_recent_form_score: Optional[float] = None,
        min_consistency: Optional[float] = None,
        min_squad_fit: Optional[float] = None,
        team_id: Optional[int] = None,
        scarcity_tier: Optional[str] = None,
        sort_by: str = "intelligence_score",
        sort_order: str = "desc",
        page: int = 1,
        size: int = 20,
    ) -> PlayerDiscoveryResponse:
        
        # 1. Build Base Database Query for Player Attributes
        stmt = select(Player)
        conditions = []

        if is_active is not None:
            conditions.append(Player.is_active == is_active)
        if role:
            conditions.append(func.lower(Player.role).contains(role.lower()))
        if batting_style:
            conditions.append(func.lower(Player.batting_style).contains(batting_style.lower()))
        if bowling_style:
            conditions.append(func.lower(Player.bowling_style).contains(bowling_style.lower()))
        if nationality:
            conditions.append(func.lower(Player.nationality) == nationality.lower())
        if is_wicketkeeper is not None:
            conditions.append(Player.is_wicketkeeper == is_wicketkeeper)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        players = list(self.db.scalars(stmt).all())

        # Pre-fetch squad context if team_id specified
        squad_players = []
        squad_map = {}
        if team_id:
            try:
                squad_players = self.squad_svc.get_squad_players(team_id)
                for sp in squad_players:
                    squad_map[sp.id] = self.analytics_svc.compute_overview(sp.id)
            except Exception:
                squad_players = []

        # 2. Compute Analytics & Filter in Python for Complex Derived Metrics
        discovered_items: List[DiscoveredPlayerItem] = []

        for p in players:
            analytics = self.analytics_svc.compute_overview(p.id)
            intel = analytics.intelligence_score
            batting = analytics.batting
            bowling = analytics.bowling
            consistency = analytics.consistency
            recent = analytics.recent_form

            # Metric extractions
            intel_val = intel.overall_score if intel else 0.0
            form_val = intel.recent_form_score.score if intel else 0.0
            consistency_val = intel.consistency_score.score if intel else 0.0
            impact_val = intel.phase_impact_score.score if intel else 0.0

            runs = batting.runs if batting else 0
            bat_avg = batting.batting_average.value if (batting and batting.batting_average) else None
            sr = batting.strike_rate.value if (batting and batting.strike_rate) else None
            wickets = bowling.wickets if bowling else 0
            econ = bowling.economy_rate.value if (bowling and bowling.economy_rate) else None

            # Calculate Squad Fit if team specified
            fit_val = None
            fit_eval = None
            if squad_players:
                fit_eval = SquadFitEngine.evaluate_fit(p, squad_players, analytics, squad_map)
                fit_val = fit_eval.squad_fit_score

            # Calculate Valuation & Scarcity
            val_eval = ValuationEngine.calculate_valuation(p, base_price=20.0, analytics=analytics, fit_score=fit_eval)
            est_val = val_eval.estimated_fair_value
            scarcity_val = 75.0 if (fit_eval and fit_eval.role_scarcity_level == "HIGH") else 50.0

            # Value for Money Score: (Intelligence Score / Estimated Value) scaled
            vfm_val = round((intel_val / max(est_val, 10.0)) * 100.0, 2)

            # Apply Filter Thresholds
            if min_intelligence_score is not None and intel_val < min_intelligence_score:
                continue
            if min_batting_strike_rate is not None and (sr is None or sr < min_batting_strike_rate):
                continue
            if min_batting_average is not None and (bat_avg is None or bat_avg < min_batting_average):
                continue
            if min_bowling_wickets is not None and wickets < min_bowling_wickets:
                continue
            if max_economy is not None and (econ is None or econ > max_economy):
                continue
            if min_recent_form_score is not None and form_val < min_recent_form_score:
                continue
            if min_consistency is not None and consistency_val < min_consistency:
                continue
            if min_squad_fit is not None and (fit_val is None or fit_val < min_squad_fit):
                continue

            discovered_items.append(
                DiscoveredPlayerItem(
                    player_id=p.id,
                    name=p.name,
                    role=str(p.role.value if hasattr(p.role, "value") else p.role),
                    nationality=p.nationality,
                    batting_style=p.batting_style,
                    bowling_style=p.bowling_style,
                    is_wicketkeeper=p.is_wicketkeeper,
                    is_active=p.is_active,
                    intelligence_score=intel_val,
                    recent_form_score=form_val,
                    consistency_score=consistency_val,
                    impact_score=impact_val,
                    squad_fit_score=fit_val,
                    scarcity_score=scarcity_val,
                    estimated_value=est_val,
                    value_for_money_score=vfm_val,
                    runs=runs,
                    batting_average=bat_avg,
                    strike_rate=sr,
                    wickets=wickets,
                    economy=econ,
                )
            )

        # 3. Sorting Logic
        reverse = (sort_order.lower() == "desc")
        
        sort_key_map = {
            "intelligence_score": lambda x: x.intelligence_score,
            "recent_form": lambda x: x.recent_form_score,
            "consistency": lambda x: x.consistency_score,
            "squad_fit": lambda x: (x.squad_fit_score or 0.0),
            "scarcity": lambda x: x.scarcity_score,
            "estimated_value": lambda x: x.estimated_value,
            "value_for_money": lambda x: x.value_for_money_score,
            "impact_score": lambda x: x.impact_score,
            "runs": lambda x: x.runs,
            "wickets": lambda x: x.wickets,
            "strike_rate": lambda x: (x.strike_rate or 0.0),
            "economy": lambda x: (x.economy or 999.0 if reverse else x.economy or 0.0),
        }

        key_fn = sort_key_map.get(sort_by.lower(), lambda x: x.intelligence_score)
        discovered_items.sort(key=key_fn, reverse=reverse)

        # 4. Pagination
        total_items = len(discovered_items)
        page = max(1, page)
        size = max(1, min(size, 100))
        total_pages = max(1, math.ceil(total_items / size)) if total_items > 0 else 1

        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paged_items = discovered_items[start_idx:end_idx]

        return PlayerDiscoveryResponse(
            total_candidates=total_items,
            page=page,
            size=size,
            total_pages=total_pages,
            items=paged_items,
        )
