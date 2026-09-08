"""
SuperScout Backend — Candidate Ranking Engine

Executes explainable multi-factor scouting candidate rankings using explicit, configurable weights.
"""
from typing import Dict, List, Optional, Any
from app.models.player import Player
from app.services.analytics.schemas import PlayerAnalyticsOverviewResponse
from app.services.auction.squad_fit_engine import SquadFitEngine
from app.services.auction.valuation_engine import ValuationEngine
from app.services.scouting.schemas import (
    CandidateRankingResponse,
    RankedCandidateItem,
    RankingWeightsSchema,
)


class CandidateRankerEngine:
    """Multi-factor explainable scouting candidate ranker."""

    @staticmethod
    def rank_candidates(
        candidates: List[Player],
        analytics_map: Dict[int, PlayerAnalyticsOverviewResponse],
        weights: RankingWeightsSchema,
        squad_players: Optional[List[Player]] = None,
        squad_analytics_map: Optional[Dict[int, PlayerAnalyticsOverviewResponse]] = None,
        team_id: Optional[int] = None,
        requested_role: Optional[str] = None,
    ) -> CandidateRankingResponse:
        
        ranked_list: List[RankedCandidateItem] = []

        # Normalize weights to ensure sum = 1.0
        total_w = (
            weights.performance_weight
            + weights.recent_form_weight
            + weights.consistency_weight
            + weights.role_fit_weight
            + weights.squad_fit_weight
            + weights.scarcity_weight
            + weights.tactical_value_weight
        )
        if total_w <= 0:
            total_w = 1.0

        p_w = weights.performance_weight / total_w
        rf_w = weights.recent_form_weight / total_w
        c_w = weights.consistency_weight / total_w
        rf_fit_w = weights.role_fit_weight / total_w
        sq_w = weights.squad_fit_weight / total_w
        sc_w = weights.scarcity_weight / total_w
        tv_w = weights.tactical_value_weight / total_w

        for player in candidates:
            analytics = analytics_map.get(player.id)
            if not analytics:
                continue

            score_obj = analytics.intelligence_score
            batting = analytics.batting
            bowling = analytics.bowling
            consistency = analytics.consistency
            sample_confidence = score_obj.confidence_factor if score_obj else 0.5

            # 1. Performance score (0-100)
            perf_score = score_obj.overall_score if score_obj else 50.0

            # 2. Recent form score (0-100)
            rf_score = score_obj.recent_form_score.score if score_obj else 50.0

            # 3. Consistency score (0-100)
            const_score = score_obj.consistency_score.score if score_obj else 50.0

            # 4. Role Fit score (0-100)
            player_role_str = str(player.role.value if hasattr(player.role, "value") else player.role).lower()
            if requested_role:
                req_lower = requested_role.lower()
                if req_lower in player_role_str:
                    role_fit_score = 95.0
                elif ("all_rounder" in player_role_str or "all-rounder" in player_role_str):
                    role_fit_score = 80.0
                else:
                    role_fit_score = 50.0
            else:
                role_fit_score = score_obj.phase_impact_score.score if score_obj else 70.0

            # 5. Squad Fit score (0-100)
            squad_fit_score = 70.0
            fit_eval = None
            if squad_players and squad_analytics_map:
                fit_eval = SquadFitEngine.evaluate_fit(player, squad_players, analytics, squad_analytics_map)
                squad_fit_score = fit_eval.squad_fit_score

            # 6. Scarcity score (0-100)
            val_eval = ValuationEngine.calculate_valuation(player, base_price=20.0, analytics=analytics, fit_score=fit_eval)
            scarcity_score = 75.0 if (fit_eval and fit_eval.role_scarcity_level == "HIGH") else 50.0

            # 7. Tactical Value score (0-100)
            tactical_score = min(100.0, (perf_score * 0.4 + rf_score * 0.3 + scarcity_score * 0.3))

            # Raw Scouting Score
            raw_score = (
                perf_score * p_w
                + rf_score * rf_w
                + const_score * c_w
                + role_fit_score * rf_fit_w
                + squad_fit_score * sq_w
                + scarcity_score * sc_w
                + tactical_score * tv_w
            )

            # Apply Sample Confidence damping factor (if confidence < 1.0, adjust score towards benchmark 50)
            final_scouting_score = round(50.0 + (raw_score - 50.0) * (0.5 + 0.5 * sample_confidence), 1)

            # Component Scores breakdown
            components = {
                "performance_score": round(perf_score, 1),
                "recent_form_score": round(rf_score, 1),
                "consistency_score": round(const_score, 1),
                "role_fit_score": round(role_fit_score, 1),
                "squad_fit_score": round(squad_fit_score, 1),
                "scarcity_score": round(scarcity_score, 1),
                "tactical_value_score": round(tactical_score, 1),
            }

            # Reasons & Risks Generation
            reasons: List[str] = []
            risks: List[str] = []

            if perf_score >= 75.0:
                reasons.append(f"High overall performance quality score ({perf_score:.1f}/100).")
            if rf_score >= 75.0:
                reasons.append(f"Exceptional recent form momentum ({rf_score:.1f}/100).")
            if squad_fit_score >= 75.0:
                reasons.append(f"Strong fit for squad composition and team needs ({squad_fit_score:.1f}/100).")
            if scarcity_score >= 70.0:
                reasons.append(f"High role scarcity increases strategic auction value ({scarcity_score:.1f}/100).")
            if const_score >= 75.0:
                reasons.append(f"Proven consistency across match sample ({const_score:.1f}/100).")

            if not reasons:
                reasons.append("Solid secondary squad target with balanced multi-factor evaluation.")

            if sample_confidence < 0.6:
                risks.append(f"Limited match sample size (confidence {sample_confidence:.2f}).")
            if rf_score < 50.0:
                risks.append("Dip in recent match form increases performance risk.")
            if const_score < 50.0:
                risks.append("High performance variance and volatility.")

            if not risks:
                risks.append("Low overall recruitment risk based on statistical indicators.")

            ranked_list.append(
                RankedCandidateItem(
                    rank=0,  # assigned after sorting
                    player_id=player.id,
                    player_name=player.name,
                    role=player_role_str,
                    scouting_score=final_scouting_score,
                    confidence=round(sample_confidence, 2),
                    component_scores=components,
                    reasons=reasons,
                    risks=risks,
                )
            )

        # Sort candidates descending by scouting_score
        ranked_list.sort(key=lambda x: x.scouting_score, reverse=True)
        for idx, item in enumerate(ranked_list, 1):
            item.rank = idx

        return CandidateRankingResponse(
            team_id=team_id,
            weights_used=weights,
            total_ranked=len(ranked_list),
            candidates=ranked_list,
        )
