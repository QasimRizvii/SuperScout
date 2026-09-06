"""
SuperScout Backend — Squad Intelligence Orchestrator Service

Orchestrates database queries, player analytics integration, squad balance auditing,
Playing XI optimization, scenario simulation, gap recruitment analysis, and squad comparison.
"""
from typing import Dict, List, Optional, Set
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.batting import BattingPerformance
from app.models.bowling import BowlingPerformance
from app.models.player import Player
from app.models.team import Team
from app.services.analytics.player import PlayerAnalyticsService
from app.services.analytics.schemas import PlayerAnalyticsOverviewResponse
from app.services.squad.balance_analyzer import SquadBalanceAnalyzer
from app.services.squad.exceptions import InsufficientSquadSizeError, SquadNotFoundError
from app.services.squad.gap_analyzer import RoleGapAnalyzer
from app.services.squad.playing_xi_optimizer import PlayingXIOptimizer
from app.services.squad.scenario_analyzer import ScenarioAnalyzer
from app.services.squad.schemas import (
    PlayingXIOptimizationResponse,
    RoleGapRecommendation,
    ScenarioAnalysisResponse,
    SquadBalanceResponse,
    SquadComparisonResponse,
    SquadIntelligenceOverviewResponse,
    SquadRoleAnalysisResponse,
)
from app.services.squad.squad_comparator import SquadComparator


class SquadIntelligenceService:
    """Main service for Squad Intelligence & Team Composition Engine."""

    def __init__(self, db: Session):
        self.db = db
        self.analytics_svc = PlayerAnalyticsService(db)

    def get_team_or_raise(self, team_id: int) -> Team:
        """Fetch Team entity or raise SquadNotFoundError."""
        team = self.db.scalar(select(Team).where(Team.id == team_id))
        if not team:
            raise SquadNotFoundError(team_id)
        return team

    def get_squad_players(self, team_id: int) -> List[Player]:
        """
        Fetch all players belonging to team's squad.

        Queries players associated with team_id via BattingPerformance, BowlingPerformance,
        or player pool.
        """
        team = self.get_team_or_raise(team_id)

        # Collect player IDs associated with team
        bat_pids = set(self.db.scalars(select(BattingPerformance.player_id).where(BattingPerformance.team_id == team_id).distinct()).all())
        bowl_pids = set(self.db.scalars(select(BowlingPerformance.player_id).where(BowlingPerformance.team_id == team_id).distinct()).all())
        pids = bat_pids.union(bowl_pids)

        if not pids:
            # Fallback query for demo/all active players if specific team has no performance records yet
            stmt = select(Player).where(Player.is_active == True).limit(20)
            players = list(self.db.scalars(stmt).all())
        else:
            stmt = select(Player).where(Player.id.in_(pids))
            players = list(self.db.scalars(stmt).all())

        if not players:
            raise SquadNotFoundError(team_id)

        return players

    def build_analytics_map(self, players: List[Player]) -> Dict[int, PlayerAnalyticsOverviewResponse]:
        """Compute Step 4 player analytics for all players in squad."""
        analytics_map: Dict[int, PlayerAnalyticsOverviewResponse] = {}
        for p in players:
            analytics_map[p.id] = self.analytics_svc.compute_overview(p.id)
        return analytics_map

    def compute_squad_balance(self, team_id: int) -> SquadBalanceResponse:
        """Compute 17-dimension Squad Balance Score and tactical audit."""
        team = self.get_team_or_raise(team_id)
        players = self.get_squad_players(team_id)
        analytics_map = self.build_analytics_map(players)
        return SquadBalanceAnalyzer.analyze_squad(team.id, team.name, players, analytics_map)

    def optimize_playing_xi(self, team_id: int) -> PlayingXIOptimizationResponse:
        """Generate recommended Playing XI and tactical breakdown."""
        team = self.get_team_or_raise(team_id)
        players = self.get_squad_players(team_id)
        analytics_map = self.build_analytics_map(players)
        return PlayingXIOptimizer.optimize_xi(team.id, team.name, players, analytics_map)

    def analyze_role_coverage(self, team_id: int) -> SquadRoleAnalysisResponse:
        """Compute detailed role coverage and phase resources analysis."""
        team = self.get_team_or_raise(team_id)
        players = self.get_squad_players(team_id)
        analytics_map = self.build_analytics_map(players)
        bal = SquadBalanceAnalyzer.analyze_squad(team.id, team.name, players, analytics_map)

        pace_spin = {
            "pace": bal.role_distribution.pace_bowlers_count,
            "spin": bal.role_distribution.spin_bowlers_count,
        }

        return SquadRoleAnalysisResponse(
            team_id=team.id,
            team_name=team.name,
            role_distribution=bal.role_distribution,
            phase_coverage=bal.phase_coverage,
            pace_spin_breakdown=pace_spin,
        )

    def identify_gaps(self, team_id: int) -> List[RoleGapRecommendation]:
        """Identify role deficiencies and recruit recommendations."""
        team = self.get_team_or_raise(team_id)
        players = self.get_squad_players(team_id)
        analytics_map = self.build_analytics_map(players)
        return RoleGapAnalyzer.identify_gaps(self.db, team.id, team.name, players, analytics_map)

    def simulate_scenario(self, team_id: int, unavailable_player_ids: List[int]) -> ScenarioAnalysisResponse:
        """Simulate squad balance impact when key players are unavailable."""
        team = self.get_team_or_raise(team_id)
        players = self.get_squad_players(team_id)
        analytics_map = self.build_analytics_map(players)
        return ScenarioAnalyzer.run_scenario(
            team.id, team.name, players, analytics_map, unavailable_player_ids
        )

    def compare_squads(self, team_1_id: int, team_2_id: int) -> SquadComparisonResponse:
        """Compare two team squads side-by-side."""
        team_1 = self.get_team_or_raise(team_1_id)
        team_2 = self.get_team_or_raise(team_2_id)

        players_1 = self.get_squad_players(team_1_id)
        players_2 = self.get_squad_players(team_2_id)

        map_1 = self.build_analytics_map(players_1)
        map_2 = self.build_analytics_map(players_2)

        return SquadComparator.compare_squads(
            team_1.id, team_1.name, players_1, map_1,
            team_2.id, team_2.name, players_2, map_2,
        )

    def get_overview(self, team_id: int) -> SquadIntelligenceOverviewResponse:
        """Compute unified squad intelligence overview."""
        team = self.get_team_or_raise(team_id)
        players = self.get_squad_players(team_id)
        analytics_map = self.build_analytics_map(players)

        bal = SquadBalanceAnalyzer.analyze_squad(team.id, team.name, players, analytics_map)
        xi = PlayingXIOptimizer.optimize_xi(team.id, team.name, players, analytics_map)
        gaps = RoleGapAnalyzer.identify_gaps(self.db, team.id, team.name, players, analytics_map)

        return SquadIntelligenceOverviewResponse(
            team_id=team.id,
            team_name=team.name,
            squad_size=len(players),
            balance=bal,
            playing_xi=xi,
            gaps=gaps,
        )
