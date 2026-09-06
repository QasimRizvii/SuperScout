"""
SuperScout Backend — Player Intelligence Score Engine

Computes a deterministic, explainable statistical Player Intelligence Score (0–100 scale).

IMPORTANT: This is a transparent statistical scoring model, NOT an AI/ML prediction model.
"""
import math
from typing import Dict, List, Tuple
from app.models.enums import PlayerRole
from app.services.analytics.schemas import (
    BattingAnalyticsResponse,
    BowlingAnalyticsResponse,
    ConsistencyMetrics,
    IntelligenceScoreResponse,
    RecentFormResponse,
    ScoreComponent,
)

# Configurable score weights per player role category
WEIGHTS_BY_ROLE: Dict[str, Dict[str, float]] = {
    "batting_heavy": {
        "batting": 0.50,
        "bowling": 0.00,
        "consistency": 0.20,
        "recent_form": 0.15,
        "phase_impact": 0.15,
    },
    "bowling_heavy": {
        "batting": 0.00,
        "bowling": 0.50,
        "consistency": 0.20,
        "recent_form": 0.15,
        "phase_impact": 0.15,
    },
    "all_rounder": {
        "batting": 0.35,
        "bowling": 0.35,
        "consistency": 0.10,
        "recent_form": 0.10,
        "phase_impact": 0.10,
    },
    "balanced": {
        "batting": 0.25,
        "bowling": 0.25,
        "consistency": 0.20,
        "recent_form": 0.15,
        "phase_impact": 0.15,
    },
}


def get_role_category(role: PlayerRole) -> str:
    """Map PlayerRole enum to weight category."""
    if role in (PlayerRole.BATTER, PlayerRole.WICKETKEEPER_BATTER, PlayerRole.WICKETKEEPER):
        return "batting_heavy"
    elif role in (PlayerRole.FAST_BOWLER, PlayerRole.SPINNER, PlayerRole.BOWLER, PlayerRole.MEDIUM_FAST_BOWLER):
        return "bowling_heavy"
    elif role in (PlayerRole.ALL_ROUNDER, PlayerRole.BOWLING_ALL_ROUNDER):
        return "all_rounder"
    return "balanced"


class PlayerIntelligenceScorer:
    """Engine for computing explainable statistical player score (0-100)."""

    @staticmethod
    def calculate_batting_score(batting: BattingAnalyticsResponse) -> float:
        if not batting.batting_average.metric_available and not batting.strike_rate.metric_available:
            return 0.0

        avg = batting.batting_average.value or 0.0
        sr = batting.strike_rate.value or 0.0
        bound_pct = batting.boundary_percentage.value or 0.0

        # Benchmark score components: Avg (35+ -> 100), SR (150+ -> 100), Boundary % (20%+ -> 100)
        avg_score = min(100.0, (avg / 35.0) * 100.0)
        sr_score = min(100.0, (sr / 150.0) * 100.0)
        b_score = min(100.0, (bound_pct / 20.0) * 100.0)

        return round(0.40 * avg_score + 0.40 * sr_score + 0.20 * b_score, 2)

    @staticmethod
    def calculate_bowling_score(bowling: BowlingAnalyticsResponse) -> float:
        if not bowling.economy_rate.metric_available and not bowling.bowling_average.metric_available:
            return 0.0

        econ = bowling.economy_rate.value or 10.0
        avg = bowling.bowling_average.value or 40.0
        dot_pct = bowling.dot_ball_percentage.value or 0.0

        # Benchmark score components: Econ (<=6.5 -> 100, >=11.5 -> 0), Avg (<=20 -> 100, >=45 -> 0), Dot % (45%+ -> 100)
        econ_score = max(0.0, min(100.0, (11.5 - econ) / (11.5 - 6.5) * 100.0))
        avg_score = max(0.0, min(100.0, (45.0 - avg) / (45.0 - 20.0) * 100.0))
        dot_score = min(100.0, (dot_pct / 45.0) * 100.0)

        return round(0.45 * econ_score + 0.35 * avg_score + 0.20 * dot_score, 2)

    @staticmethod
    def calculate_consistency_score(consistency: ConsistencyMetrics) -> float:
        if consistency.sample_size < 2 or not consistency.coefficient_of_variation.metric_available:
            return 50.0  # Default neutral score for tiny sample size

        cv = consistency.coefficient_of_variation.value or 1.0
        impact_pct = consistency.meaningful_contributions_pct.value or 0.0

        # CV score: lower CV is better (CV <= 0.3 -> 100, CV >= 1.2 -> 0)
        cv_score = max(0.0, min(100.0, (1.2 - cv) / (1.2 - 0.3) * 100.0))
        impact_score = min(100.0, (impact_pct / 50.0) * 100.0)

        return round(0.60 * cv_score + 0.40 * impact_score, 2)

    @staticmethod
    def calculate_recent_form_score(form: RecentFormResponse, role: PlayerRole) -> float:
        if form.actual_sample_size == 0:
            return 50.0

        batting_form = PlayerIntelligenceScorer.calculate_batting_score(form.recent_batting)
        bowling_form = PlayerIntelligenceScorer.calculate_bowling_score(form.recent_bowling)

        category = get_role_category(role)
        if category == "batting_heavy":
            return batting_form
        elif category == "bowling_heavy":
            return bowling_form
        else:
            return round((batting_form + bowling_form) / 2.0, 2)

    @staticmethod
    def calculate_phase_impact_score(batting: BattingAnalyticsResponse, bowling: BowlingAnalyticsResponse) -> float:
        # Phase impact rewards death/powerplay contributions
        bat_death = batting.phases.death.runs
        bowl_death_wkts = bowling.phases.death.wickets if hasattr(bowling.phases.death, "wickets") else 0

        score = min(100.0, (bat_death * 3.0) + (bowl_death_wkts * 20.0) + 50.0)
        return round(score, 2)

    @classmethod
    def compute_score(
        cls,
        player_id: int,
        player_name: str,
        role: PlayerRole,
        batting: BattingAnalyticsResponse,
        bowling: BowlingAnalyticsResponse,
        consistency: ConsistencyMetrics,
        recent_form: RecentFormResponse,
    ) -> IntelligenceScoreResponse:

        total_sample_size = max(batting.sample_size, bowling.sample_size)
        confidence_factor = round(min(1.0, math.sqrt(total_sample_size / 10.0)), 2)

        category = get_role_category(role)
        weights = WEIGHTS_BY_ROLE[category]

        sub_batting = cls.calculate_batting_score(batting)
        sub_bowling = cls.calculate_bowling_score(bowling)
        sub_consistency = cls.calculate_consistency_score(consistency)
        sub_form = cls.calculate_recent_form_score(recent_form, role)
        sub_phase = cls.calculate_phase_impact_score(batting, bowling)

        w_bat = weights["batting"]
        w_bowl = weights["bowling"]
        w_con = weights["consistency"]
        w_form = weights["recent_form"]
        w_phase = weights["phase_impact"]

        raw_score = (
            (sub_batting * w_bat)
            + (sub_bowling * w_bowl)
            + (sub_consistency * w_con)
            + (sub_form * w_form)
            + (sub_phase * w_phase)
        )

        overall_score = round(raw_score * confidence_factor, 1)

        explanation = (
            f"Player Intelligence Score of {overall_score}/100 computed for {role.value.upper()} role "
            f"using {total_sample_size} innings (sample confidence: {confidence_factor * 100:.0f}%). "
            f"Sub-scores: Batting={sub_batting:.1f}, Bowling={sub_bowling:.1f}, Consistency={sub_consistency:.1f}, "
            f"Recent Form={sub_form:.1f}, Phase Impact={sub_phase:.1f}."
        )

        return IntelligenceScoreResponse(
            player_id=player_id,
            player_name=player_name,
            role=role,
            overall_score=overall_score,
            confidence_factor=confidence_factor,
            sample_size=total_sample_size,
            batting_score=ScoreComponent(score=sub_batting, weight=w_bat, weighted_score=round(sub_batting * w_bat, 2), description="Batting Average, Strike Rate & Boundary %"),
            bowling_score=ScoreComponent(score=sub_bowling, weight=w_bowl, weighted_score=round(sub_bowling * w_bowl, 2), description="Economy Rate, Average & Dot Ball %"),
            consistency_score=ScoreComponent(score=sub_consistency, weight=w_con, weighted_score=round(sub_consistency * w_con, 2), description="Coefficient of Variation & High Impact %"),
            recent_form_score=ScoreComponent(score=sub_form, weight=w_form, weighted_score=round(sub_form * w_form, 2), description="Recent N matches performance window"),
            phase_impact_score=ScoreComponent(score=sub_phase, weight=w_phase, weighted_score=round(sub_phase * w_phase, 2), description="Powerplay and Death overs impact"),
            explanation=explanation,
        )
