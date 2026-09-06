"""
SuperScout Backend — Auction Role Scarcity Engine

Calculates dynamic role scarcity across the available candidate player pool.
"""
from typing import Dict, List
from app.models.enums import PlayerRole
from app.models.player import Player


class RoleScarcityEngine:
    """Engine for determining market scarcity levels for player roles."""

    @classmethod
    def compute_role_scarcity(
        cls,
        target_role: PlayerRole,
        candidate_pool: List[Player],
    ) -> str:
        """
        Compute role scarcity level (HIGH, MEDIUM, LOW) based on candidate supply.
        """
        matching_count = 0
        for p in candidate_pool:
            if p.role == target_role or (
                target_role in (PlayerRole.WICKETKEEPER, PlayerRole.WICKETKEEPER_BATTER)
                and p.is_wicketkeeper
            ):
                matching_count += 1

        if matching_count <= 2:
            return "HIGH"
        elif matching_count <= 5:
            return "MEDIUM"
        else:
            return "LOW"

    @classmethod
    def get_scarcity_multiplier(cls, scarcity_level: str) -> float:
        """Return valuation multiplier based on scarcity."""
        if scarcity_level == "HIGH":
            return 1.25  # 25% premium for rare roles
        elif scarcity_level == "MEDIUM":
            return 1.10  # 10% premium
        else:
            return 1.00  # Standard pricing
