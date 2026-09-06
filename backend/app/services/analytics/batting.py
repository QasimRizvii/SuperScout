"""
SuperScout Backend — Batting Analytics Module

Calculates deterministic, statistically sound batting performance metrics.
"""
from typing import List, Optional
from app.models.batting import BattingPerformance
from app.services.analytics.schemas import (
    BattingAnalyticsResponse,
    BattingPhaseAnalytics,
    MetricValue,
    PhaseBattingStats,
)


class BattingAnalyticsEngine:
    """Deterministic calculator for player batting performance metrics."""

    @staticmethod
    def compute_batting_analytics(
        player_id: int,
        player_name: str,
        performances: List[BattingPerformance],
    ) -> BattingAnalyticsResponse:
        sample_size = len(performances)

        if sample_size == 0:
            return BattingAnalyticsResponse(
                player_id=player_id,
                player_name=player_name,
                sample_size=0,
                innings=0,
                runs=0,
                balls_faced=0,
                dismissals=0,
                not_outs=0,
                highest_score=0,
                batting_average=MetricValue(value=None, sample_size=0, metric_available=False, reason="No batting innings found"),
                strike_rate=MetricValue(value=None, sample_size=0, metric_available=False, reason="No batting innings found"),
                fours=0,
                sixes=0,
                boundary_runs=0,
                boundary_percentage=MetricValue(value=None, sample_size=0, metric_available=False, reason="No batting innings found"),
                balls_per_boundary=MetricValue(value=None, sample_size=0, metric_available=False, reason="No batting innings found"),
                dot_balls=0,
                dot_ball_percentage=MetricValue(value=None, sample_size=0, metric_available=False, reason="No batting innings found"),
                runs_per_innings=MetricValue(value=None, sample_size=0, metric_available=False, reason="No batting innings found"),
                runs_per_100_balls=MetricValue(value=None, sample_size=0, metric_available=False, reason="No batting innings found"),
                dismissal_rate=MetricValue(value=None, sample_size=0, metric_available=False, reason="No batting innings found"),
                phases=BattingPhaseAnalytics(),
            )

        runs = sum(p.runs for p in performances)
        balls_faced = sum(p.balls_faced for p in performances)
        fours = sum(p.fours for p in performances)
        sixes = sum(p.sixes for p in performances)
        dot_balls = sum(p.dot_balls for p in performances)
        highest_score = max(p.runs for p in performances)

        dismissals = 0
        not_outs = 0
        for p in performances:
            if p.dismissal_type is None or str(p.dismissal_type).lower() in ("not_out", "none", ""):
                not_outs += 1
            else:
                dismissals += 1

        # Batting Average
        if dismissals > 0:
            avg_val = round(runs / dismissals, 2)
            avg_metric = MetricValue(value=avg_val, sample_size=sample_size, metric_available=True)
        else:
            avg_metric = MetricValue(value=float(runs), sample_size=sample_size, metric_available=True, reason="Undefeated across all innings")

        # Strike Rate
        if balls_faced > 0:
            sr_val = round((runs / balls_faced) * 100.0, 2)
            sr_metric = MetricValue(value=sr_val, sample_size=balls_faced, metric_available=True)
        else:
            sr_metric = MetricValue(value=None, sample_size=0, metric_available=False, reason="Zero balls faced")

        # Boundaries
        boundary_runs = (fours * 4) + (sixes * 6)
        if runs > 0:
            bound_pct_val = round((boundary_runs / runs) * 100.0, 2)
            bound_pct_metric = MetricValue(value=bound_pct_val, sample_size=runs, metric_available=True)
        else:
            bound_pct_metric = MetricValue(value=0.0, sample_size=0, metric_available=True)

        total_boundaries = fours + sixes
        if total_boundaries > 0:
            bpb_val = round(balls_faced / total_boundaries, 2)
            bpb_metric = MetricValue(value=bpb_val, sample_size=total_boundaries, metric_available=True)
        else:
            bpb_metric = MetricValue(value=None, sample_size=0, metric_available=False, reason="Zero boundaries hit")

        # Dot balls
        if balls_faced > 0:
            dot_pct_val = round((dot_balls / balls_faced) * 100.0, 2)
            dot_pct_metric = MetricValue(value=dot_pct_val, sample_size=balls_faced, metric_available=True)
        else:
            dot_pct_metric = MetricValue(value=None, sample_size=0, metric_available=False, reason="Zero balls faced")

        # Runs per innings & per 100 balls & dismissal rate
        rpi_metric = MetricValue(value=round(runs / sample_size, 2), sample_size=sample_size, metric_available=True)
        r100_metric = MetricValue(value=sr_metric.value, sample_size=balls_faced, metric_available=sr_metric.metric_available, reason=sr_metric.reason)
        dism_rate_metric = MetricValue(value=round(dismissals / sample_size, 2), sample_size=sample_size, metric_available=True)

        # Phase analytics calculation
        pp_runs = sum(p.runs_powerplay for p in performances if p.runs_powerplay is not None)
        mid_runs = sum(p.runs_middle for p in performances if p.runs_middle is not None)
        dth_runs = sum(p.runs_death for p in performances if p.runs_death is not None)

        phases = BattingPhaseAnalytics(
            powerplay=PhaseBattingStats(
                runs=pp_runs,
                phase_contribution_pct=round((pp_runs / runs) * 100.0, 2) if runs > 0 else 0.0,
            ),
            middle=PhaseBattingStats(
                runs=mid_runs,
                phase_contribution_pct=round((mid_runs / runs) * 100.0, 2) if runs > 0 else 0.0,
            ),
            death=PhaseBattingStats(
                runs=dth_runs,
                phase_contribution_pct=round((dth_runs / runs) * 100.0, 2) if runs > 0 else 0.0,
            ),
        )

        return BattingAnalyticsResponse(
            player_id=player_id,
            player_name=player_name,
            sample_size=sample_size,
            innings=sample_size,
            runs=runs,
            balls_faced=balls_faced,
            dismissals=dismissals,
            not_outs=not_outs,
            highest_score=highest_score,
            batting_average=avg_metric,
            strike_rate=sr_metric,
            fours=fours,
            sixes=sixes,
            boundary_runs=boundary_runs,
            boundary_percentage=bound_pct_metric,
            balls_per_boundary=bpb_metric,
            dot_balls=dot_balls,
            dot_ball_percentage=dot_pct_metric,
            runs_per_innings=rpi_metric,
            runs_per_100_balls=r100_metric,
            dismissal_rate=dism_rate_metric,
            phases=phases,
        )
