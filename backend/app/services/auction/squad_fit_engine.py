"""
SuperScout Backend — Franchise Squad Fit Engine

Evaluates candidate player suitability and urgency for a specific franchise squad.
"""
from typing import Dict, List, Optional
from app.models.enums import PlayerRole
from app.models.player import Player
from app.services.analytics.schemas import PlayerAnalyticsOverviewResponse
from app.services.auction.schemas import SquadFitScore
from app.services.squad.balance_analyzer import SquadBalanceAnalyzer
from app.services.squad.role_classifier import RoleClassifier


class SquadFitEngine:
    """Engine for evaluating how strongly a candidate player fills a franchise's tactical needs."""

    @classmethod
    def evaluate_fit(
        cls,
        player: Player,
        squad_players: List[Player],
        analytics: Optional[PlayerAnalyticsOverviewResponse] = None,
        squad_analytics_map: Optional[Dict[int, PlayerAnalyticsOverviewResponse]] = None,
    ) -> SquadFitScore:

        quality_score = analytics.intelligence_score.overall_score if analytics else 50.0

        # Run balance audit on current franchise squad
        balance_report = SquadBalanceAnalyzer.analyze_squad(
            0, "Temp", squad_players, squad_analytics_map or {}
        )
        dist = balance_report.role_distribution
        phase = balance_report.phase_coverage

        is_keeper = RoleClassifier.is_wicketkeeper(player)
        is_pacer = RoleClassifier.is_pace_bowler(player)
        is_spinner = RoleClassifier.is_spin_bowler(player)
        is_ar = RoleClassifier.is_all_rounder(player)
        is_death = RoleClassifier.is_death_bowler(analytics)

        fit_score = 50.0
        gap_sev = "MEDIUM"
        priority = "TIER_2"
        contrib = "ROTATION"

        # Rule 1: Wicketkeeper priority
        if is_keeper:
            if dist.wicketkeepers_count == 0:
                fit_score = 95.0
                gap_sev = "CRITICAL"
                priority = "TIER_1"
                contrib = "STARTER"
            elif dist.wicketkeepers_count == 1:
                fit_score = 80.0
                gap_sev = "HIGH"
                priority = "TIER_1"
            else:
                fit_score = 40.0
                gap_sev = "OVERSTOCKED"
                priority = "TIER_3"

        # Rule 2: Death Bowler priority
        elif is_death:
            if phase.death_bowlers_count == 0:
                fit_score = 92.0
                gap_sev = "CRITICAL"
                priority = "TIER_1"
                contrib = "STARTER"
            elif phase.death_bowlers_count == 1:
                fit_score = 82.0
                gap_sev = "HIGH"
                priority = "TIER_1"

        # Rule 3: All-Rounder flexibility
        elif is_ar:
            if dist.all_rounders_count < 2:
                fit_score = 85.0
                gap_sev = "HIGH"
                priority = "TIER_1"
            else:
                fit_score = 70.0
                gap_sev = "MEDIUM"

        # Rule 4: Bowling variety shortages
        elif is_pacer and dist.pace_bowlers_count == 0:
            fit_score = 90.0
            gap_sev = "CRITICAL"
            priority = "TIER_1"
        elif is_spinner and dist.spin_bowlers_count == 0:
            fit_score = 90.0
            gap_sev = "CRITICAL"
            priority = "TIER_1"

        # Rule 5: Overstocked roles
        elif player.role in ("batter", "wicketkeeper_batter") and dist.batters_count >= 5:
            fit_score = 35.0
            gap_sev = "OVERSTOCKED"
            priority = "AVOID" if quality_score < 70.0 else "TIER_3"
        elif player.role in ("bowler", "fast_bowler", "spinner", "medium_fast_bowler") and dist.bowlers_count >= 6:
            fit_score = 40.0
            gap_sev = "OVERSTOCKED"
            priority = "TIER_3"

        scarcity = "HIGH" if gap_sev in ("CRITICAL", "HIGH") else ("LOW" if gap_sev == "OVERSTOCKED" else "MEDIUM")

        return SquadFitScore(
            player_quality_score=quality_score,
            squad_fit_score=fit_score,
            gap_severity=gap_sev,
            role_scarcity_level=scarcity,
            expected_contribution_rating=contrib,
            overall_priority=priority,
        )
