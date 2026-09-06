"""
SuperScout Backend — Alternative Target Fallback Engine

Identifies fallback candidates for auction targets when bidding exceeds max ceiling.
"""
from typing import Dict, List, Optional
from app.models.player import Player
from app.services.analytics.schemas import PlayerAnalyticsOverviewResponse
from app.services.auction.schemas import (
    AlternativeTarget,
    AlternativeTargetResponse,
)
from app.services.auction.squad_fit_engine import SquadFitEngine
from app.services.auction.valuation_engine import ValuationEngine


class AlternativeEngine:
    """Engine for building fallback decision trees when bidding exceeds ceilings."""

    @classmethod
    def find_alternatives(
        cls,
        primary_player: Player,
        squad_players: List[Player],
        candidates: List[Player],
        analytics_map: Dict[int, PlayerAnalyticsOverviewResponse],
        remaining_purse: float = 1000.0,
        remaining_squad_slots: int = 5,
        limit: int = 3,
    ) -> AlternativeTargetResponse:

        p_analytics = analytics_map.get(primary_player.id)
        p_fit = SquadFitEngine.evaluate_fit(primary_player, squad_players, p_analytics, analytics_map)
        p_val = ValuationEngine.calculate_valuation(
            primary_player, 20.0, p_analytics, p_fit, remaining_purse, remaining_squad_slots
        )

        alternatives: List[AlternativeTarget] = []

        for cand in candidates:
            if cand.id == primary_player.id or any(sp.id == cand.id for sp in squad_players):
                continue

            # Match role or similar capabilities
            if cand.role == primary_player.role or (
                primary_player.is_wicketkeeper and cand.is_wicketkeeper
            ):
                c_analytics = analytics_map.get(cand.id)
                c_fit = SquadFitEngine.evaluate_fit(cand, squad_players, c_analytics, analytics_map)
                c_val = ValuationEngine.calculate_valuation(
                    cand, 20.0, c_analytics, c_fit, remaining_purse, remaining_squad_slots
                )

                score = c_analytics.intelligence_score.overall_score if c_analytics else 50.0

                rationale = (
                    f"Fallback option for {primary_player.name}: {cand.name} ({cand.role.value.upper()}) "
                    f"has Intelligence Score {score:.1f}/100. Recommended Max Bid: ₹{c_val.recommended_max_bid:.1f}L "
                    f"(saves ₹{max(0.0, p_val.recommended_max_bid - c_val.recommended_max_bid):.1f}L)."
                )

                alternatives.append(
                    AlternativeTarget(
                        player_id=cand.id,
                        player_name=cand.name,
                        role=cand.role,
                        intelligence_score=score,
                        base_price=c_val.base_price,
                        estimated_fair_value=c_val.estimated_fair_value,
                        recommended_max_bid=c_val.recommended_max_bid,
                        transition_rationale=rationale,
                    )
                )

        # Sort alternatives by intelligence score descending
        alternatives.sort(key=lambda a: a.intelligence_score, reverse=True)

        rec_str = (
            f"If bidding on {primary_player.name} exceeds recommended ceiling ₹{p_val.recommended_max_bid:.1f}L, "
            f"pivot immediately to fallback target {alternatives[0].player_name} (Max Bid: ₹{alternatives[0].recommended_max_bid:.1f}L)."
            if alternatives else f"No comparable alternatives found for {primary_player.name} in current pool."
        )

        return AlternativeTargetResponse(
            primary_player_id=primary_player.id,
            primary_player_name=primary_player.name,
            primary_max_bid=p_val.recommended_max_bid,
            alternatives=alternatives[:limit],
            recommendation=rec_str,
        )
