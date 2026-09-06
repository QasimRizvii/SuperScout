"""
SuperScout Backend — Squad Comparator Module

Performs side-by-side head-to-head comparison of two team squads across 12 statistical dimensions.
"""
from typing import Dict, List
from app.models.player import Player
from app.services.analytics.schemas import PlayerAnalyticsOverviewResponse
from app.services.squad.balance_analyzer import SquadBalanceAnalyzer
from app.services.squad.schemas import (
    SquadComparisonItem,
    SquadComparisonResponse,
)


class SquadComparator:
    """Engine for comparing two team squads side-by-side across tactical dimensions."""

    @classmethod
    def compare_squads(
        cls,
        team_1_id: int,
        team_1_name: str,
        players_1: List[Player],
        analytics_map_1: Dict[int, PlayerAnalyticsOverviewResponse],
        team_2_id: int,
        team_2_name: str,
        players_2: List[Player],
        analytics_map_2: Dict[int, PlayerAnalyticsOverviewResponse],
    ) -> SquadComparisonResponse:

        bal_1 = SquadBalanceAnalyzer.analyze_squad(team_1_id, team_1_name, players_1, analytics_map_1)
        bal_2 = SquadBalanceAnalyzer.analyze_squad(team_2_id, team_2_name, players_2, analytics_map_2)

        items: List[SquadComparisonItem] = []

        # 1. Overall Balance Score
        adv_1 = team_1_id if bal_1.overall_balance_score > bal_2.overall_balance_score else (team_2_id if bal_2.overall_balance_score > bal_1.overall_balance_score else None)
        items.append(
            SquadComparisonItem(
                dimension="Overall Squad Balance Score",
                team_1_value=f"{bal_1.overall_balance_score}/100",
                team_2_value=f"{bal_2.overall_balance_score}/100",
                advantage_team_id=adv_1,
                note="Unified balance score across role coverage, depth & phase balance.",
            )
        )

        # 2. Squad Size
        adv_size = team_1_id if bal_1.squad_size > bal_2.squad_size else (team_2_id if bal_2.squad_size > bal_1.squad_size else None)
        items.append(
            SquadComparisonItem(
                dimension="Squad Size",
                team_1_value=bal_1.squad_size,
                team_2_value=bal_2.squad_size,
                advantage_team_id=adv_size,
                note="Total registered players available.",
            )
        )

        # 3. Wicketkeepers
        adv_wk = team_1_id if bal_1.role_distribution.wicketkeepers_count > bal_2.role_distribution.wicketkeepers_count else (team_2_id if bal_2.role_distribution.wicketkeepers_count > bal_1.role_distribution.wicketkeepers_count else None)
        items.append(
            SquadComparisonItem(
                dimension="Wicketkeeping Options",
                team_1_value=bal_1.role_distribution.wicketkeepers_count,
                team_2_value=bal_2.role_distribution.wicketkeepers_count,
                advantage_team_id=adv_wk,
                note="Specialist wicketkeepers in squad.",
            )
        )

        # 4. All-Rounders
        adv_ar = team_1_id if bal_1.role_distribution.all_rounders_count > bal_2.role_distribution.all_rounders_count else (team_2_id if bal_2.role_distribution.all_rounders_count > bal_1.role_distribution.all_rounders_count else None)
        items.append(
            SquadComparisonItem(
                dimension="All-Rounders",
                team_1_value=bal_1.role_distribution.all_rounders_count,
                team_2_value=bal_2.role_distribution.all_rounders_count,
                advantage_team_id=adv_ar,
                note="Dual-capability players providing tactical flexibility.",
            )
        )

        # 5. Death Bowlers
        adv_death = team_1_id if bal_1.phase_coverage.death_bowlers_count > bal_2.phase_coverage.death_bowlers_count else (team_2_id if bal_2.phase_coverage.death_bowlers_count > bal_1.phase_coverage.death_bowlers_count else None)
        items.append(
            SquadComparisonItem(
                dimension="Death Bowling Options",
                team_1_value=bal_1.phase_coverage.death_bowlers_count,
                team_2_value=bal_2.phase_coverage.death_bowlers_count,
                advantage_team_id=adv_death,
                note="Bowlers with proven death overs experience.",
            )
        )

        # 6. Pace vs Spin
        items.append(
            SquadComparisonItem(
                dimension="Pace vs Spin Breakdown",
                team_1_value=f"{bal_1.role_distribution.pace_bowlers_count} Pace / {bal_1.role_distribution.spin_bowlers_count} Spin",
                team_2_value=f"{bal_2.role_distribution.pace_bowlers_count} Pace / {bal_2.role_distribution.spin_bowlers_count} Spin",
                advantage_team_id=None,
                note="Bowling variety for different venue pitches.",
            )
        )

        overall_adv = team_1_id if bal_1.overall_balance_score >= bal_2.overall_balance_score else team_2_id
        adv_team_name = team_1_name if overall_adv == team_1_id else team_2_name

        summary = (
            f"Compared squads for {team_1_name} ({bal_1.overall_balance_score}/100) and "
            f"{team_2_name} ({bal_2.overall_balance_score}/100). Overall tactical advantage: {adv_team_name}."
        )

        return SquadComparisonResponse(
            team_1_id=team_1_id,
            team_1_name=team_1_name,
            team_2_id=team_2_id,
            team_2_name=team_2_name,
            comparison_matrix=items,
            team_1_strengths=bal_1.strengths,
            team_2_strengths=bal_2.strengths,
            overall_advantage_team_id=overall_adv,
            summary=summary,
        )
