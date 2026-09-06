"""
SuperScout Backend — Comparable Player Analysis Engine

Finds statistically & strategically similar players and benchmarks transaction prices.
"""
from typing import Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.auction import AuctionTransaction
from app.models.player import Player
from app.services.analytics.schemas import PlayerAnalyticsOverviewResponse
from app.services.auction.schemas import (
    ComparablePlayerItem,
    ComparablePlayerResponse,
)


class ComparableEngine:
    """Engine for identifying comparable players and historical price benchmarks."""

    @classmethod
    def find_comparables(
        cls,
        db: Session,
        target_player: Player,
        candidate_pool: List[Player],
        analytics_map: Dict[int, PlayerAnalyticsOverviewResponse],
        limit: int = 4,
    ) -> ComparablePlayerResponse:

        t_analytics = analytics_map.get(target_player.id)
        t_score = t_analytics.intelligence_score.overall_score if t_analytics else 50.0

        comparable_items: List[ComparablePlayerItem] = []
        historical_prices: List[float] = []

        # Query past auction transaction prices for historical benchmarking
        tx_stmt = select(AuctionTransaction).where(AuctionTransaction.status == "sold")
        past_transactions = list(db.scalars(tx_stmt).all())
        tx_price_map: Dict[int, float] = {tx.player_id: tx.final_price for tx in past_transactions}

        for cand in candidate_pool:
            if cand.id == target_player.id:
                continue

            # Check role match
            if cand.role == target_player.role or (
                target_player.is_wicketkeeper and cand.is_wicketkeeper
            ):
                c_analytics = analytics_map.get(cand.id)
                c_score = c_analytics.intelligence_score.overall_score if c_analytics else 50.0

                # Compute statistical similarity (100 - score_diff*2)
                score_diff = abs(t_score - c_score)
                similarity = max(50.0, round(100.0 - (score_diff * 2.5), 1))

                hist_price = tx_price_map.get(cand.id)
                if hist_price is not None and hist_price > 0:
                    historical_prices.append(hist_price)

                reason = (
                    f"Matches role {cand.role.value.upper()} with Intelligence Score "
                    f"{c_score:.1f}/100 (Similarity: {similarity:.0f}%)."
                )

                comparable_items.append(
                    ComparablePlayerItem(
                        player_id=cand.id,
                        player_name=cand.name,
                        role=cand.role,
                        intelligence_score=c_score,
                        historical_final_price=hist_price,
                        similarity_score=similarity,
                        key_matching_reason=reason,
                    )
                )

        # Sort by similarity score descending
        comparable_items.sort(key=lambda c: c.similarity_score, reverse=True)
        top_comparables = comparable_items[:limit]

        avg_price = round(sum(historical_prices) / len(historical_prices), 1) if historical_prices else 150.0

        guidance = (
            f"Statistically comparable player analysis for {target_player.name} ({target_player.role.value.upper()}). "
            f"Identified {len(top_comparables)} similar profile(s) with average historical benchmark ₹{avg_price:.1f}L."
        )

        return ComparablePlayerResponse(
            target_player_id=target_player.id,
            target_player_name=target_player.name,
            role=target_player.role,
            intelligence_score=t_score,
            comparables=top_comparables,
            average_price_benchmark=avg_price,
            valuation_guidance=guidance,
        )
