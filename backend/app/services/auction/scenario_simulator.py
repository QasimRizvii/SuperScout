"""
SuperScout Backend — Auction Scenario Simulator Module

Simulates What-If auction scenarios (acquisition, outbid by rival, price surge).
"""
from typing import Dict, List
from app.models.player import Player
from app.services.analytics.schemas import PlayerAnalyticsOverviewResponse
from app.services.auction.schemas import AuctionScenarioResponse
from app.services.squad.balance_analyzer import SquadBalanceAnalyzer


class ScenarioSimulator:
    """Engine for simulating What-If auction transactions and updating franchise strategies."""

    @classmethod
    def simulate_scenario(
        cls,
        auction_id: int,
        team_id: int,
        team_name: str,
        target_player: Player,
        bid_price: float,
        outcome: str,
        current_squad: List[Player],
        analytics_map: Dict[int, PlayerAnalyticsOverviewResponse],
        remaining_purse: float = 1000.0,
    ) -> AuctionScenarioResponse:

        base_bal = SquadBalanceAnalyzer.analyze_squad(
            team_id, team_name, current_squad, analytics_map
        )
        score_before = base_bal.overall_balance_score

        if outcome == "purchased":
            new_squad = current_squad + [target_player]
            new_bal = SquadBalanceAnalyzer.analyze_squad(
                team_id, team_name, new_squad, analytics_map
            )
            score_after = new_bal.overall_balance_score
            score_delta = round(score_after - score_before, 1)
            updated_purse = round(max(0.0, remaining_purse - bid_price), 1)

            rem_gaps = [w for w in new_bal.weaknesses]
            next_targets = ["Target secondary bowler", "Target backup keeper"]

            summary = (
                f"Simulated acquisition of {target_player.name} for ₹{bid_price:.1f}L. "
                f"Squad balance score improved from {score_before} to {score_after} (delta: {score_delta:+.1f}). "
                f"Remaining purse: ₹{updated_purse:.1f}L."
            )
        elif outcome == "outbid":
            score_after = score_before
            score_delta = 0.0
            updated_purse = remaining_purse
            rem_gaps = [w for w in base_bal.weaknesses]
            next_targets = [f"Pivot to alternative targets for role {target_player.role.value.upper()}"]

            summary = (
                f"Simulated outbid scenario for {target_player.name} at ₹{bid_price:.1f}L. "
                f"Purse remains intact at ₹{updated_purse:.1f}L. Pivot to alternative targets."
            )
        else:  # surged
            score_after = score_before
            score_delta = 0.0
            updated_purse = remaining_purse
            rem_gaps = [w for w in base_bal.weaknesses]
            next_targets = ["Evaluate opportunity cost before continuing bid"]

            summary = (
                f"Simulated price surge scenario for {target_player.name} up to ₹{bid_price:.1f}L. "
                f"Price exceeds fair value. Recommend evaluating opportunity cost ceiling."
            )

        return AuctionScenarioResponse(
            auction_id=auction_id,
            team_id=team_id,
            team_name=team_name,
            target_player_id=target_player.id,
            target_player_name=target_player.name,
            bid_price=bid_price,
            outcome=outcome,
            updated_remaining_purse=updated_purse,
            squad_balance_before=score_before,
            squad_balance_after=score_after,
            score_delta=score_delta,
            remaining_gaps=rem_gaps,
            next_recommended_targets=next_targets,
            scenario_summary=summary,
        )
