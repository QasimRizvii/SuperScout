"""
SuperScout Backend — Auction Intelligence Orchestrator Service

Orchestrates database queries, player analytics, squad intelligence, player valuation,
target rankings, purse budget allocation, fallback target trees, opportunity cost,
what-if scenario simulation, and comparable player price benchmarks.
"""
from typing import Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.auction import Auction, AuctionTransaction
from app.models.player import Player
from app.models.team import Team
from app.services.analytics.player import PlayerAnalyticsService
from app.services.analytics.schemas import PlayerAnalyticsOverviewResponse
from app.services.auction.alternative_engine import AlternativeEngine
from app.services.auction.budget_allocator import PurseBudgetAllocator
from app.services.auction.comparable_engine import ComparableEngine
from app.services.auction.exceptions import AuctionNotFoundError, InvalidPurseError
from app.services.auction.opportunity_cost_engine import OpportunityCostEngine
from app.services.auction.scenario_simulator import ScenarioSimulator
from app.services.auction.schemas import (
    AlternativeTargetResponse,
    AuctionScenarioResponse,
    AuctionTargetRankingResponse,
    ComparablePlayerResponse,
    OpportunityCostResponse,
    PlayerValuationResponse,
    PurseBudgetAllocationResponse,
)
from app.services.auction.squad_fit_engine import SquadFitEngine
from app.services.auction.target_ranker import TargetRanker
from app.services.auction.valuation_engine import ValuationEngine
from app.services.squad.squad_service import SquadIntelligenceService


class AuctionIntelligenceService:
    """Main orchestrator service for Auction Intelligence & Strategy Engine."""

    def __init__(self, db: Session):
        self.db = db
        self.analytics_svc = PlayerAnalyticsService(db)
        self.squad_svc = SquadIntelligenceService(db)

    def get_auction_or_raise(self, auction_id: int) -> Auction:
        """Fetch Auction entity or raise AuctionNotFoundError."""
        auction = self.db.scalar(select(Auction).where(Auction.id == auction_id))
        if not auction:
            raise AuctionNotFoundError(auction_id)
        return auction

    def get_candidate_pool(self) -> List[Player]:
        """Fetch all active candidate players available in database."""
        stmt = select(Player).where(Player.is_active == True)
        return list(self.db.scalars(stmt).all())

    def build_analytics_map(self, players: List[Player]) -> Dict[int, PlayerAnalyticsOverviewResponse]:
        """Compute Step 4 player analytics for candidate pool."""
        analytics_map: Dict[int, PlayerAnalyticsOverviewResponse] = {}
        for p in players:
            analytics_map[p.id] = self.analytics_svc.compute_overview(p.id)
        return analytics_map

    def compute_player_valuation(
        self,
        auction_id: int,
        player_id: int,
        team_id: Optional[int] = None,
        base_price: float = 20.0,
        remaining_purse: float = 1000.0,
        remaining_squad_slots: int = 5,
    ) -> PlayerValuationResponse:
        """Compute statistical fair value and recommended max bid ceiling for a player."""

        player = self.analytics_svc.get_player_or_raise(player_id)
        analytics = self.analytics_svc.compute_overview(player_id)

        fit = None
        if team_id:
            squad_players = self.squad_svc.get_squad_players(team_id)
            squad_map = self.build_analytics_map(squad_players)
            fit = SquadFitEngine.evaluate_fit(player, squad_players, analytics, squad_map)

        return ValuationEngine.calculate_valuation(
            player,
            base_price=base_price,
            analytics=analytics,
            fit_score=fit,
            remaining_purse=remaining_purse,
            remaining_squad_slots=remaining_squad_slots,
        )

    def rank_targets(
        self,
        auction_id: int,
        team_id: int,
        remaining_purse: float = 1000.0,
        remaining_squad_slots: int = 5,
    ) -> AuctionTargetRankingResponse:
        """Rank all candidate players for a franchise auction strategy."""
        team = self.squad_svc.get_team_or_raise(team_id)
        squad_players = self.squad_svc.get_squad_players(team_id)
        candidates = self.get_candidate_pool()

        all_players = list({p.id: p for p in (squad_players + candidates)}.values())
        analytics_map = self.build_analytics_map(all_players)

        return TargetRanker.rank_targets(
            auction_id=auction_id,
            team_id=team.id,
            team_name=team.name,
            squad_players=squad_players,
            candidates=candidates,
            analytics_map=analytics_map,
            remaining_purse=remaining_purse,
            remaining_squad_slots=remaining_squad_slots,
        )

    def allocate_purse(
        self,
        auction_id: int,
        team_id: int,
        total_purse: float = 1000.0,
        remaining_purse: float = 1000.0,
        remaining_squad_slots: int = 5,
    ) -> PurseBudgetAllocationResponse:
        """Compute dynamic purse allocation strategy across squad categories."""
        if remaining_purse < 0:
            raise InvalidPurseError(remaining_purse)

        team = self.squad_svc.get_team_or_raise(team_id)
        gaps = self.squad_svc.identify_gaps(team_id)

        return PurseBudgetAllocator.allocate_purse(
            auction_id=auction_id,
            team_id=team.id,
            team_name=team.name,
            total_purse=total_purse,
            remaining_purse=remaining_purse,
            remaining_squad_slots=remaining_squad_slots,
            gaps=gaps,
        )

    def get_alternative_targets(
        self,
        auction_id: int,
        player_id: int,
        team_id: int,
        remaining_purse: float = 1000.0,
        remaining_squad_slots: int = 5,
    ) -> AlternativeTargetResponse:
        """Find fallback target players if primary target exceeds max bid ceiling."""
        player = self.analytics_svc.get_player_or_raise(player_id)
        squad_players = self.squad_svc.get_squad_players(team_id)
        candidates = self.get_candidate_pool()

        all_players = list({p.id: p for p in ([player] + squad_players + candidates)}.values())
        analytics_map = self.build_analytics_map(all_players)

        return AlternativeEngine.find_alternatives(
            primary_player=player,
            squad_players=squad_players,
            candidates=candidates,
            analytics_map=analytics_map,
            remaining_purse=remaining_purse,
            remaining_squad_slots=remaining_squad_slots,
        )

    def evaluate_opportunity_cost(
        self,
        auction_id: int,
        player_id: int,
        team_id: int,
        proposed_bid: float,
        remaining_purse: float = 1000.0,
        remaining_squad_slots: int = 5,
    ) -> OpportunityCostResponse:
        """Analyze trade-offs and opportunity costs for a proposed auction bid."""
        player = self.analytics_svc.get_player_or_raise(player_id)
        gaps = self.squad_svc.identify_gaps(team_id)

        return OpportunityCostEngine.evaluate_opportunity_cost(
            player=player,
            proposed_bid=proposed_bid,
            remaining_purse=remaining_purse,
            remaining_squad_slots=remaining_squad_slots,
            squad_gaps=gaps,
        )

    def simulate_scenario(
        self,
        auction_id: int,
        team_id: int,
        target_player_id: int,
        bid_price: float,
        outcome: str = "purchased",
        remaining_purse: float = 1000.0,
    ) -> AuctionScenarioResponse:
        """Simulate What-If auction event (acquisition, outbid, or price surge)."""
        team = self.squad_svc.get_team_or_raise(team_id)
        player = self.analytics_svc.get_player_or_raise(target_player_id)
        squad_players = self.squad_svc.get_squad_players(team_id)

        all_players = list({p.id: p for p in ([player] + squad_players)}.values())
        analytics_map = self.build_analytics_map(all_players)

        return ScenarioSimulator.simulate_scenario(
            auction_id=auction_id,
            team_id=team.id,
            team_name=team.name,
            target_player=player,
            bid_price=bid_price,
            outcome=outcome,
            current_squad=squad_players,
            analytics_map=analytics_map,
            remaining_purse=remaining_purse,
        )

    def get_comparables(
        self,
        auction_id: int,
        player_id: int,
    ) -> ComparablePlayerResponse:
        """Find statistically similar players and benchmark transaction prices."""
        player = self.analytics_svc.get_player_or_raise(player_id)
        candidates = self.get_candidate_pool()
        analytics_map = self.build_analytics_map(candidates)

        return ComparableEngine.find_comparables(
            db=self.db,
            target_player=player,
            candidate_pool=candidates,
            analytics_map=analytics_map,
        )
