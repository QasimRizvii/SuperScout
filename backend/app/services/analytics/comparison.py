"""
SuperScout Backend — Player Comparison Analytics Module

Performs multi-player statistical head-to-head comparison (2 to 5 players).
"""
from typing import List
from app.services.analytics.exceptions import InvalidComparisonError
from app.services.analytics.schemas import (
    PlayerAnalyticsOverviewResponse,
    PlayerComparisonMatrixItem,
    PlayerComparisonResponse,
)


class PlayerComparisonEngine:
    """Service engine for comparing 2-5 players across statistical metrics."""

    @staticmethod
    def compare_players(
        overviews: List[PlayerAnalyticsOverviewResponse],
    ) -> PlayerComparisonResponse:
        num_players = len(overviews)
        if num_players < 2 or num_players > 5:
            raise InvalidComparisonError(
                f"Player comparison requires between 2 and 5 players, got {num_players}."
            )

        items: List[PlayerComparisonMatrixItem] = []

        top_batter_id = None
        best_bat_avg = -1.0

        top_bowler_id = None
        best_bowl_econ = 999.0

        top_overall_id = None
        best_overall_score = -1.0

        for ov in overviews:
            bat_avg = ov.batting.batting_average.value
            sr = ov.batting.strike_rate.value
            b_pct = ov.batting.boundary_percentage.value
            econ = ov.bowling.economy_rate.value
            bowl_avg = ov.bowling.bowling_average.value
            cv = ov.consistency.coefficient_of_variation.value
            score = ov.intelligence_score.overall_score

            items.append(
                PlayerComparisonMatrixItem(
                    player_id=ov.player_id,
                    player_name=ov.player_name,
                    role=ov.role,
                    sample_size=ov.intelligence_score.sample_size,
                    overall_score=score,
                    batting_average=bat_avg,
                    strike_rate=sr,
                    boundary_pct=b_pct,
                    bowling_economy=econ,
                    bowling_average=bowl_avg,
                    wickets=ov.bowling.wickets,
                    consistency_cv=cv,
                    recent_form_runs=ov.recent_form.recent_batting.runs,
                    recent_form_sr=ov.recent_form.recent_batting.strike_rate.value,
                )
            )

            # Track top batter
            if bat_avg is not None and bat_avg > best_bat_avg:
                best_bat_avg = bat_avg
                top_batter_id = ov.player_id

            # Track top bowler
            if econ is not None and ov.bowling.wickets > 0 and econ < best_bowl_econ:
                best_bowl_econ = econ
                top_bowler_id = ov.player_id

            # Track top overall
            if score > best_overall_score:
                best_overall_score = score
                top_overall_id = ov.player_id

        summary = (
            f"Compared {num_players} players. Highest Intelligence Score: "
            f"Player ID {top_overall_id} ({best_overall_score}/100)."
        )

        return PlayerComparisonResponse(
            players_compared=num_players,
            players=items,
            top_batter_player_id=top_batter_id,
            top_bowler_player_id=top_bowler_id,
            top_overall_player_id=top_overall_id,
            summary=summary,
        )
