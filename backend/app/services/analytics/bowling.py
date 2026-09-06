"""
SuperScout Backend — Bowling Analytics Module

Calculates deterministic, statistically sound bowling performance metrics.
"""
from typing import List, Optional
from app.models.bowling import BowlingPerformance
from app.services.analytics.schemas import (
    BowlingAnalyticsResponse,
    BowlingPhaseAnalytics,
    MetricValue,
    PhaseBowlingStats,
)


def overs_to_balls(overs: float) -> int:
    """Convert cricket overs notation (e.g., 3.4 overs = 22 balls) to total balls."""
    if overs <= 0.0:
        return 0
    full_overs = int(overs)
    part_balls = int(round((overs - full_overs) * 10))
    return (full_overs * 6) + min(part_balls, 5)


def balls_to_overs(balls: int) -> float:
    """Convert total balls to standard cricket overs notation (e.g., 22 balls = 3.4 overs)."""
    if balls <= 0:
        return 0.0
    full_overs = balls // 6
    part_balls = balls % 6
    return round(full_overs + (part_balls / 10.0), 1)


class BowlingAnalyticsEngine:
    """Deterministic calculator for player bowling performance metrics."""

    @staticmethod
    def compute_bowling_analytics(
        player_id: int,
        player_name: str,
        performances: List[BowlingPerformance],
    ) -> BowlingAnalyticsResponse:
        sample_size = len(performances)

        if sample_size == 0:
            return BowlingAnalyticsResponse(
                player_id=player_id,
                player_name=player_name,
                sample_size=0,
                innings_bowled=0,
                balls_bowled=0,
                overs=0.0,
                runs_conceded=0,
                wickets=0,
                economy_rate=MetricValue(value=None, sample_size=0, metric_available=False, reason="No bowling innings found"),
                bowling_average=MetricValue(value=None, sample_size=0, metric_available=False, reason="No bowling innings found"),
                bowling_strike_rate=MetricValue(value=None, sample_size=0, metric_available=False, reason="No bowling innings found"),
                dot_balls=0,
                dot_ball_percentage=MetricValue(value=None, sample_size=0, metric_available=False, reason="No bowling innings found"),
                maidens=0,
                wides=0,
                no_balls=0,
                extras_conceded=0,
                wickets_per_innings=MetricValue(value=None, sample_size=0, metric_available=False, reason="No bowling innings found"),
                phases=BowlingPhaseAnalytics(),
            )

        balls_bowled = 0
        for p in performances:
            if (p.balls_bowled or 0) > 0:
                balls_bowled += p.balls_bowled
            elif (p.overs or 0.0) > 0:
                balls_bowled += overs_to_balls(p.overs)

        overs_formatted = balls_to_overs(balls_bowled)
        runs_conceded = sum(p.runs_conceded or 0 for p in performances)
        wickets = sum(p.wickets or 0 for p in performances)
        dot_balls = sum(p.dot_balls or 0 for p in performances)
        maidens = sum(p.maidens or 0 for p in performances)
        wides = sum(p.wides or 0 for p in performances)
        no_balls = sum(p.no_balls or 0 for p in performances)
        extras_conceded = wides + no_balls

        # Economy Rate
        if balls_bowled > 0:
            econ_val = round(runs_conceded / (balls_bowled / 6.0), 2)
            econ_metric = MetricValue(value=econ_val, sample_size=balls_bowled, metric_available=True)
        else:
            econ_metric = MetricValue(value=None, sample_size=0, metric_available=False, reason="Zero balls bowled")

        # Bowling Average
        if wickets > 0:
            avg_val = round(runs_conceded / wickets, 2)
            avg_metric = MetricValue(value=avg_val, sample_size=wickets, metric_available=True)
        else:
            avg_metric = MetricValue(value=None, sample_size=0, metric_available=False, reason="Zero wickets taken")

        # Bowling Strike Rate
        if wickets > 0:
            sr_val = round(balls_bowled / wickets, 2)
            sr_metric = MetricValue(value=sr_val, sample_size=wickets, metric_available=True)
        else:
            sr_metric = MetricValue(value=None, sample_size=0, metric_available=False, reason="Zero wickets taken")

        # Dot ball %
        if balls_bowled > 0:
            dot_pct_val = round((dot_balls / balls_bowled) * 100.0, 2)
            dot_pct_metric = MetricValue(value=dot_pct_val, sample_size=balls_bowled, metric_available=True)
        else:
            dot_pct_metric = MetricValue(value=None, sample_size=0, metric_available=False, reason="Zero balls bowled")

        # Wickets per innings
        wpi_metric = MetricValue(value=round(wickets / sample_size, 2), sample_size=sample_size, metric_available=True)

        # Phase bowling stats
        pp_overs = sum(p.overs_powerplay for p in performances if p.overs_powerplay is not None)
        mid_overs = sum(p.overs_middle for p in performances if p.overs_middle is not None)
        dth_overs = sum(p.overs_death for p in performances if p.overs_death is not None)

        phases = BowlingPhaseAnalytics(
            powerplay=PhaseBowlingStats(
                overs=round(pp_overs, 1),
                balls=overs_to_balls(pp_overs),
                phase_overs_pct=round((pp_overs / overs_formatted) * 100.0, 2) if overs_formatted > 0 else 0.0,
            ),
            middle=PhaseBowlingStats(
                overs=round(mid_overs, 1),
                balls=overs_to_balls(mid_overs),
                phase_overs_pct=round((mid_overs / overs_formatted) * 100.0, 2) if overs_formatted > 0 else 0.0,
            ),
            death=PhaseBowlingStats(
                overs=round(dth_overs, 1),
                balls=overs_to_balls(dth_overs),
                phase_overs_pct=round((dth_overs / overs_formatted) * 100.0, 2) if overs_formatted > 0 else 0.0,
            ),
        )

        return BowlingAnalyticsResponse(
            player_id=player_id,
            player_name=player_name,
            sample_size=sample_size,
            innings_bowled=sample_size,
            balls_bowled=balls_bowled,
            overs=overs_formatted,
            runs_conceded=runs_conceded,
            wickets=wickets,
            economy_rate=econ_metric,
            bowling_average=avg_metric,
            bowling_strike_rate=sr_metric,
            dot_balls=dot_balls,
            dot_ball_percentage=dot_pct_metric,
            maidens=maidens,
            wides=wides,
            no_balls=no_balls,
            extras_conceded=extras_conceded,
            wickets_per_innings=wpi_metric,
            phases=phases,
        )
