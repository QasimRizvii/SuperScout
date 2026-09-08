"""
SuperScout Backend — Undervalued Player Intelligence Engine

Identifies candidates who deliver measurable performance contribution relative to acquisition cost or market valuation.
"""
from typing import Dict, List, Optional, Any
from app.models.player import Player
from app.services.analytics.schemas import PlayerAnalyticsOverviewResponse
from app.services.auction.valuation_engine import ValuationEngine
from app.services.scouting.schemas import (
    UndervaluedPlayerItem,
    UndervaluedPlayerResponse,
)


class UnderratedPlayerEngine:
    """Engine to detect statistically and strategically undervalued players."""

    @staticmethod
    def identify_undervalued_players(
        candidates: List[Player],
        analytics_map: Dict[int, PlayerAnalyticsOverviewResponse],
        squad_fit_map: Optional[Dict[int, float]] = None,
        min_undervaluation_score: float = 60.0,
    ) -> UndervaluedPlayerResponse:
        
        results: List[UndervaluedPlayerItem] = []

        for p in candidates:
            analytics = analytics_map.get(p.id)
            if not analytics:
                continue

            intel = analytics.intelligence_score
            sample_size = intel.sample_size if intel else 0
            sample_confidence = intel.confidence_factor if (intel and sample_size > 0) else 0.5

            intel_score = intel.overall_score if (intel and sample_size > 0) else 50.0
            recent_form_score = intel.recent_form_score.score if (intel and sample_size > 0) else 50.0
            consistency_score = intel.consistency_score.score if (intel and sample_size > 0) else 50.0

            # Squad fit & Valuation
            fit_score = squad_fit_map.get(p.id, 70.0) if squad_fit_map else 70.0
            val_eval = ValuationEngine.calculate_valuation(p, base_price=20.0, analytics=analytics, fit_score=None)
            est_value = val_eval.estimated_fair_value
            scarcity_score = 60.0

            # Undervaluation Signal Calculation
            # 1. Performance Efficiency Ratio = Intelligence Score / max(Est Value, 15.0)
            perf_efficiency = (intel_score / max(est_value, 15.0)) * 50.0

            # 2. Scarcity Arbitrage = High scarcity + Moderate price
            scarcity_arbitrage = (scarcity_score * 0.5) if est_value <= 150.0 else 20.0

            # 3. Consistency/Form Boost
            reliability_boost = (recent_form_score * 0.25 + consistency_score * 0.25)

            raw_underval_score = min(100.0, (perf_efficiency * 0.4 + scarcity_arbitrage * 0.3 + reliability_boost * 0.3))
            final_underval_score = round(raw_underval_score * (0.6 + 0.4 * sample_confidence), 1)

            if final_underval_score < min_undervaluation_score:
                continue

            # Classify Undervaluation Type
            if scarcity_score >= 75.0 and est_value <= 200.0:
                uv_type = "role_scarcity"
                price_rel = "Scarcity arbitrage: High role scarcity with accessible market valuation."
            elif perf_efficiency >= 80.0:
                uv_type = "statistical"
                price_rel = f"Statistical value: Delivers high intelligence score ({intel_score:.1f}) at an estimated valuation of {est_value:.1f} Lakhs."
            else:
                uv_type = "auction"
                price_rel = f"Auction target: Favorable contribution-to-cost ratio relative to market tier."

            reasons: List[str] = []
            risk_factors: List[str] = []

            if intel_score >= 70.0:
                reasons.append(f"High Player Intelligence Score ({intel_score:.1f}/100) indicates elite contribution capability.")
            if recent_form_score >= 70.0:
                reasons.append(f"Strong recent form momentum ({recent_form_score:.1f}/100).")
            if consistency_score >= 70.0:
                reasons.append(f"Proven statistical consistency ({consistency_score:.1f}/100).")
            if scarcity_score >= 70.0:
                reasons.append(f"High role scarcity score ({scarcity_score:.1f}/100) provides competitive advantage.")

            if not reasons:
                reasons.append("Potential value target because estimated contribution is high relative to estimated acquisition cost.")

            if sample_confidence < 0.6:
                risk_factors.append(f"Low match sample size (confidence {sample_confidence:.2f}) increases volatility.")
            if est_value > 300.0:
                risk_factors.append("Higher valuation threshold requires substantial purse allocation.")

            if not risk_factors:
                risk_factors.append("Low statistical and market valuation risk.")

            player_role_str = str(p.role.value if hasattr(p.role, "value") else p.role)

            results.append(
                UndervaluedPlayerItem(
                    player_id=p.id,
                    player_name=p.name,
                    role=player_role_str,
                    undervaluation_score=final_underval_score,
                    estimated_value=est_value,
                    expected_contribution=f"Expected to deliver solid performance in {player_role_str} role with strong ROI.",
                    price_value_relationship=price_rel,
                    undervaluation_type=uv_type,
                    reasons=reasons,
                    confidence=round(sample_confidence, 2),
                    risk_factors=risk_factors,
                )
            )

        results.sort(key=lambda x: x.undervaluation_score, reverse=True)

        return UndervaluedPlayerResponse(
            total_found=len(results),
            players=results,
        )
