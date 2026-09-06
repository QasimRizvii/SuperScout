"""
SuperScout Backend — Squad Role Gap & Recruitment Analyzer

Identifies squad deficiencies, assigns recruitment priorities, and searches database for target recruits.
"""
from typing import Dict, List, Set
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import PlayerRole
from app.models.player import Player
from app.services.analytics.schemas import PlayerAnalyticsOverviewResponse
from app.services.squad.balance_analyzer import SquadBalanceAnalyzer
from app.services.squad.role_classifier import RoleClassifier
from app.services.squad.schemas import (
    RecruitCandidate,
    RoleGapRecommendation,
)


class RoleGapAnalyzer:
    """Engine for auditing squad deficiencies and identifying database recruitment candidates."""

    @classmethod
    def identify_gaps(
        cls,
        db: Session,
        team_id: int,
        team_name: str,
        players: List[Player],
        analytics_map: Dict[int, PlayerAnalyticsOverviewResponse],
    ) -> List[RoleGapRecommendation]:

        squad_ids = {p.id for p in players}
        balance_report = SquadBalanceAnalyzer.analyze_squad(
            team_id, team_name, players, analytics_map
        )
        dist = balance_report.role_distribution
        phase = balance_report.phase_coverage

        gaps: List[RoleGapRecommendation] = []

        # Gap 1: Wicketkeeper
        if dist.wicketkeepers_count < 2:
            priority = "CRITICAL" if dist.wicketkeepers_count == 0 else "HIGH"
            reason = "Squad has 0 specialist keepers!" if dist.wicketkeepers_count == 0 else "Only 1 keeper in squad; backup required."
            target_profile = "Wicketkeeper-Batter with high intelligence score and reliable glovework."

            candidates = cls._find_candidates(db, squad_ids, roles=[PlayerRole.WICKETKEEPER, PlayerRole.WICKETKEEPER_BATTER])
            gaps.append(
                RoleGapRecommendation(
                    gap_title="Wicketkeeping Coverage & Depth",
                    priority=priority,
                    reason=reason,
                    target_player_profile=target_profile,
                    candidate_players=candidates,
                )
            )

        # Gap 2: Death Bowling
        if phase.death_bowlers_count < 2:
            priority = "HIGH" if phase.death_bowlers_count == 0 else "MEDIUM"
            reason = "Lack of proven death bowlers exposes squad to late-overs run leaks."
            target_profile = "Fast Bowler or Specialist death bowler with low economy rate in overs 16-20."

            candidates = cls._find_candidates(db, squad_ids, roles=[PlayerRole.FAST_BOWLER, PlayerRole.MEDIUM_FAST_BOWLER, PlayerRole.BOWLER])
            gaps.append(
                RoleGapRecommendation(
                    gap_title="Death Bowling Specialization",
                    priority=priority,
                    reason=reason,
                    target_player_profile=target_profile,
                    candidate_players=candidates,
                )
            )

        # Gap 3: All-Rounders
        if dist.all_rounders_count < 2:
            reason = "Insufficient all-rounders limits playing XI flexibility and bowling options."
            target_profile = "Pace or Spin All-Rounder capable of batting in middle order and bowling 2+ overs."

            candidates = cls._find_candidates(db, squad_ids, roles=[PlayerRole.ALL_ROUNDER, PlayerRole.BOWLING_ALL_ROUNDER])
            gaps.append(
                RoleGapRecommendation(
                    gap_title="All-Rounder Flexibility",
                    priority="MEDIUM",
                    reason=reason,
                    target_player_profile=target_profile,
                    candidate_players=candidates,
                )
            )

        # Gap 4: Pace/Spin Variety
        if dist.pace_bowlers_count == 0 or dist.spin_bowlers_count == 0:
            missing_type = "Pace" if dist.pace_bowlers_count == 0 else "Spin"
            target_roles = [PlayerRole.FAST_BOWLER, PlayerRole.MEDIUM_FAST_BOWLER] if dist.pace_bowlers_count == 0 else [PlayerRole.SPINNER]

            candidates = cls._find_candidates(db, squad_ids, roles=target_roles)
            gaps.append(
                RoleGapRecommendation(
                    gap_title=f"{missing_type} Bowling Variety Shortage",
                    priority="HIGH",
                    reason=f"Squad has zero {missing_type.lower()} bowlers available.",
                    target_player_profile=f"Specialist {missing_type} bowler for bowling variety across venues.",
                    candidate_players=candidates,
                )
            )

        return gaps

    @staticmethod
    def _find_candidates(
        db: Session,
        squad_ids: Set[int],
        roles: List[PlayerRole],
        limit: int = 3,
    ) -> List[RecruitCandidate]:
        """Find candidate players outside current squad matching target roles."""
        stmt = (
            select(Player)
            .where(Player.id.not_in(squad_ids))
            .where(Player.role.in_(roles))
            .limit(limit * 2)
        )
        candidates = list(db.scalars(stmt).all())
        results: List[RecruitCandidate] = []

        for p in candidates[:limit]:
            results.append(
                RecruitCandidate(
                    player_id=p.id,
                    player_name=p.name,
                    role=p.role,
                    current_team_name=p.nationality or "Available Pool",
                    intelligence_score=65.0,  # Benchmark score
                    fit_reason=f"Matches role requirements for {p.role.value.upper()}.",
                )
            )
        return results
