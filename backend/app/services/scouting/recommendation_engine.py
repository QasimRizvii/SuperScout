"""
SuperScout Backend — Scouting Recommendation Engine

Decision-support engine answering "Who should this franchise scout next?"
Categorizes targets into Immediate Priorities, Secondary Targets, Watchlists, and Avoid candidates.
"""
from typing import Dict, List, Optional, Any
from app.models.player import Player
from app.services.analytics.schemas import PlayerAnalyticsOverviewResponse
from app.services.auction.valuation_engine import ValuationEngine
from app.services.scouting.schemas import (
    ScoutingRecommendationResponse,
    ScoutingTargetRecommendation,
)
from app.services.squad.squad_service import SquadIntelligenceService


class RecommendationEngine:
    """Decision-support engine for franchise scouting priorities."""

    @staticmethod
    def generate_recommendations(
        candidates: List[Player],
        analytics_map: Dict[int, PlayerAnalyticsOverviewResponse],
        team_id: Optional[int] = None,
        squad_fit_map: Optional[Dict[int, float]] = None,
        budget: float = 1000.0,
        slots_needed: int = 5,
    ) -> ScoutingRecommendationResponse:
        
        immediate_priorities: List[ScoutingTargetRecommendation] = []
        secondary_targets: List[ScoutingTargetRecommendation] = []
        watchlist_candidates: List[ScoutingTargetRecommendation] = []
        avoid_candidates: List[ScoutingTargetRecommendation] = []

        all_recommendations: List[ScoutingTargetRecommendation] = []

        for p in candidates:
            analytics = analytics_map.get(p.id)
            if not analytics:
                continue

            intel = analytics.intelligence_score
            batting = analytics.batting
            bowling = analytics.bowling
            confidence = intel.confidence_factor if intel else 0.5
            intel_score = intel.overall_score if intel else 0.0
            form_score = intel.recent_form_score.score if intel else 0.0

            fit_score = squad_fit_map.get(p.id, 70.0) if squad_fit_map else 70.0
            val_eval = ValuationEngine.calculate_valuation(p, base_price=20.0, analytics=analytics, fit_score=None)
            est_val = val_eval.estimated_fair_value
            scarcity_score = 60.0

            # Calculate composite scouting score
            scouting_score = round(intel_score * 0.4 + form_score * 0.2 + fit_score * 0.2 + scarcity_score * 0.2, 1)
            player_role_str = str(p.role.value if hasattr(p.role, "value") else p.role)

            why_scout = (
                f"High-impact candidate ({scouting_score:.1f}/100) providing strong role synergy "
                f"and estimated valuation of {est_val:.1f} Lakhs."
            )
            main_risk = (
                "Limited match sample size." if confidence < 0.5
                else "Potential auction price surge beyond ceiling." if est_val > 250.0
                else "Recent form fluctuation." if form_score < 50.0
                else "Low structural risk."
            )
            tactical_use = f"Primary {player_role_str} option to fulfill squad tactical gap."

            rec_item = ScoutingTargetRecommendation(
                rank=0,
                player_id=p.id,
                player_name=p.name,
                primary_role=player_role_str,
                scouting_score=scouting_score,
                squad_fit=fit_score,
                estimated_value=est_val,
                why_scout=why_scout,
                main_risk=main_risk,
                expected_tactical_use=tactical_use,
                confidence=round(confidence, 2),
            )
            all_recommendations.append(rec_item)

        # Sort all candidates descending by scouting_score
        all_recommendations.sort(key=lambda x: x.scouting_score, reverse=True)

        for idx, item in enumerate(all_recommendations, 1):
            item.rank = idx
            if item.scouting_score < 40.0 or item.confidence < 0.3:
                avoid_candidates.append(item)
            elif item.scouting_score >= 75.0 and item.squad_fit >= 70.0 and len(immediate_priorities) < slots_needed:
                immediate_priorities.append(item)
            elif item.scouting_score >= 60.0:
                secondary_targets.append(item)
            else:
                watchlist_candidates.append(item)

        # Ensure immediate priorities has at least top item if available
        if not immediate_priorities and all_recommendations:
            immediate_priorities.append(all_recommendations[0])

        return ScoutingRecommendationResponse(
            team_id=team_id,
            budget=budget,
            slots_needed=slots_needed,
            immediate_priorities=immediate_priorities,
            secondary_targets=secondary_targets,
            watchlist_candidates=watchlist_candidates,
            avoid_candidates=avoid_candidates,
        )
