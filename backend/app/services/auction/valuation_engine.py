"""
SuperScout Backend — Auction Valuation Engine

Calculates statistical Fair Value and Recommended Maximum Bid Ceiling (in INR Lakhs).
"""
import math
from typing import Optional
from app.models.player import Player
from app.services.analytics.schemas import PlayerAnalyticsOverviewResponse
from app.services.auction.schemas import PlayerValuationResponse, SquadFitScore
from app.services.auction.scarcity_engine import RoleScarcityEngine


class ValuationEngine:
    """Engine for computing statistical player valuation and recommended maximum bid ceiling."""

    @classmethod
    def calculate_valuation(
        cls,
        player: Player,
        base_price: float = 20.0,
        analytics: Optional[PlayerAnalyticsOverviewResponse] = None,
        fit_score: Optional[SquadFitScore] = None,
        remaining_purse: float = 1000.0,
        remaining_squad_slots: int = 5,
    ) -> PlayerValuationResponse:

        base_p = max(20.0, base_price)
        intel_score = analytics.intelligence_score.overall_score if analytics else 50.0
        sample_size = analytics.intelligence_score.sample_size if analytics else 0

        # Scarcity multiplier
        scarcity_level = fit_score.role_scarcity_level if fit_score else "MEDIUM"
        scarcity_mult = RoleScarcityEngine.get_scarcity_multiplier(scarcity_level)

        # 1. Estimated Fair Value (Statistical valuation)
        # Scale: Base Price + (Base Price * 1.5 * (intel_score / 100)^1.2) * scarcity_mult
        performance_boost = (intel_score / 100.0) ** 1.2
        fair_value = base_p + (base_p * 2.5 * performance_boost * scarcity_mult)
        fair_value = round(max(base_p, fair_value), 1)

        # 2. Recommended Maximum Bid Ceiling (Franchise strategic valuation)
        squad_fit = fit_score.squad_fit_score if fit_score else 65.0
        fit_multiplier = squad_fit / 65.0
        raw_max_bid = fair_value * fit_multiplier

        # Purse Cap constraint (Reserve budget for remaining slots)
        if remaining_purse > 0 and remaining_squad_slots > 1:
            reserve_needed = (remaining_squad_slots - 1) * 20.0  # ₹20 Lakhs per remaining slot
            purse_cap = max(base_p, remaining_purse - reserve_needed)
            recommended_max_bid = min(raw_max_bid, purse_cap)
        else:
            recommended_max_bid = min(raw_max_bid, max(base_p, remaining_purse))

        recommended_max_bid = round(max(base_p, recommended_max_bid), 1)

        # 3. Confidence Assessment
        if sample_size >= 5:
            confidence = "HIGH"
        elif sample_size >= 1:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        explanation = (
            f"Valuation for {player.name} ({player.role.value.upper()}): "
            f"Base Price ₹{base_p:.1f}L, Intelligence Score {intel_score:.1f}/100, "
            f"Squad Fit {squad_fit:.1f}/100 ({scarcity_level} scarcity). "
            f"Estimated Fair Value: ₹{fair_value:.1f}L. Recommended Max Bid Ceiling: ₹{recommended_max_bid:.1f}L "
            f"(reserving budget for remaining {remaining_squad_slots - 1} slots)."
        )

        return PlayerValuationResponse(
            player_id=player.id,
            player_name=player.name,
            role=player.role,
            intelligence_score=intel_score,
            base_price=base_p,
            estimated_fair_value=fair_value,
            recommended_max_bid=recommended_max_bid,
            confidence=confidence,
            sample_size=sample_size,
            explanation=explanation,
        )
