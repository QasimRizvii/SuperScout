"""
SuperScout Backend — Squad Role Classifier Module

Classifies player roles, capabilities, pace vs spin, wicketkeeping, and phase capabilities.
"""
from typing import Dict, List, Optional, Set
from app.models.enums import PlayerRole
from app.models.player import Player
from app.services.analytics.schemas import PlayerAnalyticsOverviewResponse


class RoleClassifier:
    """Helper for classifying player capabilities and squad role distributions."""

    @staticmethod
    def is_wicketkeeper(player: Player) -> bool:
        """Check if player is a wicketkeeper."""
        if player.is_wicketkeeper:
            return True
        return player.role in (PlayerRole.WICKETKEEPER, PlayerRole.WICKETKEEPER_BATTER)

    @staticmethod
    def is_pace_bowler(player: Player) -> bool:
        """Check if player is a pace/fast bowler."""
        if player.role in (PlayerRole.FAST_BOWLER, PlayerRole.MEDIUM_FAST_BOWLER):
            return True
        style = (player.bowling_style or "").lower()
        return any(term in style for term in ["fast", "medium", "pace", "seam"])

    @staticmethod
    def is_spin_bowler(player: Player) -> bool:
        """Check if player is a spin bowler."""
        if player.role == PlayerRole.SPINNER:
            return True
        style = (player.bowling_style or "").lower()
        return any(term in style for term in ["spin", "legbreak", "offbreak", "slow", "orthodox", "googly"])

    @staticmethod
    def is_all_rounder(player: Player) -> bool:
        """Check if player is an all-rounder."""
        return player.role in (PlayerRole.ALL_ROUNDER, PlayerRole.BOWLING_ALL_ROUNDER)

    @staticmethod
    def is_capable_batter(player: Player, analytics: Optional[PlayerAnalyticsOverviewResponse] = None) -> bool:
        """Check if player can contribute meaningfully with the bat."""
        if player.role in (PlayerRole.BATTER, PlayerRole.WICKETKEEPER_BATTER, PlayerRole.ALL_ROUNDER, PlayerRole.WICKETKEEPER):
            return True
        if analytics and analytics.batting.sample_size > 0:
            avg = analytics.batting.batting_average.value or 0.0
            return avg >= 15.0 or analytics.batting.highest_score >= 30
        return False

    @staticmethod
    def is_capable_bowler(player: Player, analytics: Optional[PlayerAnalyticsOverviewResponse] = None) -> bool:
        """Check if player can bowl at least 1-2 overs in T20."""
        if player.role in (PlayerRole.BOWLER, PlayerRole.FAST_BOWLER, PlayerRole.SPINNER, PlayerRole.MEDIUM_FAST_BOWLER, PlayerRole.BOWLING_ALL_ROUNDER, PlayerRole.ALL_ROUNDER):
            return True
        if analytics and analytics.bowling.sample_size > 0:
            return analytics.bowling.balls_bowled >= 12
        return False

    @staticmethod
    def is_powerplay_bowler(analytics: Optional[PlayerAnalyticsOverviewResponse]) -> bool:
        """Check if player is effective in Powerplay overs."""
        if not analytics:
            return False
        return (analytics.bowling.phases.powerplay.overs or 0.0) >= 1.0

    @staticmethod
    def is_death_bowler(analytics: Optional[PlayerAnalyticsOverviewResponse]) -> bool:
        """Check if player is effective in Death overs."""
        if not analytics:
            return False
        return (analytics.bowling.phases.death.overs or 0.0) >= 1.0

    @staticmethod
    def is_finisher(analytics: Optional[PlayerAnalyticsOverviewResponse]) -> bool:
        """Check if batter is effective as a finisher in Death overs."""
        if not analytics:
            return False
        death_runs = analytics.batting.phases.death.runs or 0
        sr = analytics.batting.strike_rate.value or 0.0
        return death_runs >= 15 or sr >= 140.0
