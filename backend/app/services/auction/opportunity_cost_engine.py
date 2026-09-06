"""
SuperScout Backend — Opportunity Cost Engine

Evaluates franchise trade-offs and opportunity costs for proposed auction bids.
"""
from typing import List
from app.models.player import Player
from app.services.auction.schemas import OpportunityCostResponse
from app.services.squad.schemas import RoleGapRecommendation


class OpportunityCostEngine:
    """Engine for analyzing financial trade-offs and sacrificed role coverage for auction bids."""

    @classmethod
    def evaluate_opportunity_cost(
        cls,
        player: Player,
        proposed_bid: float,
        remaining_purse: float,
        remaining_squad_slots: int,
        squad_gaps: List[RoleGapRecommendation],
    ) -> OpportunityCostResponse:

        bid = max(0.0, proposed_bid)
        purse_after = remaining_purse - bid
        slots_after = max(1, remaining_squad_slots - 1)

        avg_purse_per_slot = purse_after / float(slots_after)

        sacrificed_roles: List[str] = []
        cost_level = "LOW"

        # Evaluate if bid restricts remaining gap fulfillment
        if avg_purse_per_slot < 30.0 and len(squad_gaps) >= 2:
            cost_level = "HIGH"
            for g in squad_gaps:
                sacrificed_roles.append(g.gap_title)
        elif avg_purse_per_slot < 50.0 and len(squad_gaps) >= 1:
            cost_level = "MEDIUM"
            if squad_gaps:
                sacrificed_roles.append(squad_gaps[0].gap_title)

        if cost_level == "HIGH":
            exp = (
                f"HIGH Opportunity Cost: Bidding ₹{bid:.1f}L for {player.name} leaves only "
                f"₹{purse_after:.1f}L (₹{avg_purse_per_slot:.1f}L/slot) for {slots_after} remaining slots, "
                f"severely risking capacity to address {len(sacrificed_roles)} remaining gap(s): {', '.join(sacrificed_roles)}."
            )
        elif cost_level == "MEDIUM":
            exp = (
                f"MEDIUM Opportunity Cost: Bidding ₹{bid:.1f}L for {player.name} leaves "
                f"₹{purse_after:.1f}L. Moderately constrains budget for {', '.join(sacrificed_roles)}."
            )
        else:
            exp = (
                f"LOW Opportunity Cost: Proposed bid of ₹{bid:.1f}L is well within purse limits. "
                f"Sufficient budget (₹{purse_after:.1f}L) remains for {slots_after} slots."
            )

        return OpportunityCostResponse(
            player_id=player.id,
            player_name=player.name,
            proposed_bid=bid,
            cost_level=cost_level,
            sacrificed_roles=sacrificed_roles,
            explanation=exp,
        )
