"""
SuperScout Backend — Auction Target Ranker Module

Ranks candidate auction targets for a franchise based on quality, squad fit, scarcity, and value for money.
"""
from typing import Dict, List, Optional
from app.models.player import Player
from app.services.analytics.schemas import PlayerAnalyticsOverviewResponse
from app.services.auction.schemas import (
    AuctionTargetItem,
    AuctionTargetRankingResponse,
)
from app.services.auction.scarcity_engine import RoleScarcityEngine
from app.services.auction.squad_fit_engine import SquadFitEngine
from app.services.auction.valuation_engine import ValuationEngine


class TargetRanker:
    """Engine for building ranked target lists for franchise auction strategy."""

    @classmethod
    def rank_targets(
        cls,
        auction_id: int,
        team_id: int,
        team_name: str,
        squad_players: List[Player],
        candidates: List[Player],
        analytics_map: Dict[int, PlayerAnalyticsOverviewResponse],
        remaining_purse: float = 1000.0,
        remaining_squad_slots: int = 5,
    ) -> AuctionTargetRankingResponse:

        target_items: List[AuctionTargetItem] = []

        for p in candidates:
            # Skip if already in squad
            if any(sp.id == p.id for sp in squad_players):
                continue

            a = analytics_map.get(p.id)
            fit = SquadFitEngine.evaluate_fit(p, squad_players, a, analytics_map)
            val = ValuationEngine.calculate_valuation(
                p,
                base_price=20.0,
                analytics=a,
                fit_score=fit,
                remaining_purse=remaining_purse,
                remaining_squad_slots=remaining_squad_slots,
            )

            # Target score calculation
            scarcity_pts = 90.0 if fit.role_scarcity_level == "HIGH" else (70.0 if fit.role_scarcity_level == "MEDIUM" else 50.0)
            target_score = (fit.player_quality_score * 0.35) + (fit.squad_fit_score * 0.45) + (scarcity_pts * 0.20)

            # Assign Priority
            if target_score >= 75.0 and fit.overall_priority != "AVOID":
                priority = "TIER_1"
            elif target_score >= 60.0 and fit.overall_priority != "AVOID":
                priority = "TIER_2"
            elif fit.overall_priority == "AVOID":
                priority = "AVOID"
            else:
                priority = "TIER_3"

            fit_explanation = (
                f"Quality: {fit.player_quality_score:.1f}/100, Squad Fit: {fit.squad_fit_score:.1f}/100 "
                f"({fit.gap_severity} gap). Max Recommended Bid: ₹{val.recommended_max_bid:.1f}L."
            )

            target_items.append(
                AuctionTargetItem(
                    rank=0,  # Assigned after sorting
                    player_id=p.id,
                    player_name=p.name,
                    role=p.role,
                    intelligence_score=fit.player_quality_score,
                    squad_fit_score=fit.squad_fit_score,
                    role_scarcity=fit.role_scarcity_level,
                    base_price=val.base_price,
                    estimated_fair_value=val.estimated_fair_value,
                    recommended_max_bid=val.recommended_max_bid,
                    priority=priority,
                    confidence=val.confidence,
                    fit_explanation=fit_explanation,
                )
            )

        # Sort by target score / squad fit descending
        target_items.sort(key=lambda t: (t.priority == "TIER_1", t.priority == "TIER_2", t.squad_fit_score, t.intelligence_score), reverse=True)

        # Assign ranks
        for rank_idx, item in enumerate(target_items, start=1):
            item.rank = rank_idx

        tier_1_cnt = sum(1 for t in target_items if t.priority == "TIER_1")

        tactical = (
            f"Ranked {len(target_items)} candidate auction targets for {team_name}. "
            f"Identified {tier_1_cnt} TIER_1 primary target(s) matching high-priority squad gaps."
        )

        return AuctionTargetRankingResponse(
            auction_id=auction_id,
            team_id=team_id,
            team_name=team_name,
            remaining_purse=remaining_purse,
            total_targets_ranked=len(target_items),
            targets=target_items,
            tactical_summary=tactical,
        )
