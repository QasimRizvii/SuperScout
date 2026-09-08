"""
SuperScout Backend — Scouting Orchestrator Service

Main service tying together discovery, unified profiles, candidate ranking, undervalued intelligence,
role targeting, recommendations, structured reports, tactical simulation, watchlist, and notes.
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.player import Player
from app.models.scouting import ScoutingWatchlist, ScoutingNote
from app.models.enums import WatchlistStatus, WatchlistPriority, ScoutingNoteCategory
from app.services.analytics.player import PlayerAnalyticsService
from app.services.analytics.schemas import PlayerAnalyticsOverviewResponse
from app.services.auction.auction_service import AuctionIntelligenceService
from app.services.scouting.candidate_ranker import CandidateRankerEngine
from app.services.scouting.exceptions import (
    PlayerNotFoundError,
    ScoutingNoteNotFoundError,
    WatchlistNotFoundError,
)
from app.services.scouting.player_discovery import PlayerDiscoveryEngine
from app.services.scouting.recommendation_engine import RecommendationEngine
from app.services.scouting.role_target_engine import RoleTargetEngine
from app.services.scouting.schemas import (
    CandidateRankingResponse,
    PlayerDiscoveryResponse,
    RankingWeightsSchema,
    RoleTargetResponse,
    ScoutingNoteCreateRequest,
    ScoutingNoteResponse,
    ScoutingProfileResponse,
    ScoutingRecommendationResponse,
    ScoutingReportResponse,
    TacticalRoleFitResponse,
    UndervaluedPlayerResponse,
    WatchlistCreateRequest,
    WatchlistResponse,
    WatchlistUpdateRequest,
)
from app.services.scouting.scouting_profile import ScoutingProfileEngine
from app.services.scouting.scouting_report import ScoutingReportGenerator
from app.services.scouting.tactical_simulator import TacticalSimulatorEngine
from app.services.scouting.underrated_player_engine import UnderratedPlayerEngine
from app.services.squad.squad_service import SquadIntelligenceService


class ScoutingService:
    """Central orchestrator service for Professional Scouting & Decision-Support Engine."""

    def __init__(self, db: Session):
        self.db = db
        self.analytics_svc = PlayerAnalyticsService(db)
        self.squad_svc = SquadIntelligenceService(db)
        self.auction_svc = AuctionIntelligenceService(db)
        self.discovery_engine = PlayerDiscoveryEngine(db)

    def get_player_or_raise(self, player_id: int) -> Player:
        """Fetch Player or raise PlayerNotFoundError."""
        player = self.db.scalar(select(Player).where(Player.id == player_id))
        if not player:
            raise PlayerNotFoundError(player_id)
        return player

    def get_candidate_pool(self) -> List[Player]:
        """Fetch all active candidate players in database."""
        stmt = select(Player).where(Player.is_active == True)
        return list(self.db.scalars(stmt).all())

    def build_analytics_map(self, players: List[Player]) -> Dict[int, PlayerAnalyticsOverviewResponse]:
        """Compute Step 4 analytics overview for candidate pool."""
        res: Dict[int, PlayerAnalyticsOverviewResponse] = {}
        for p in players:
            res[p.id] = self.analytics_svc.compute_overview(p.id)
        return res

    # ── Part A1: Scouting Profile ──────────────────────────────────────────────

    def get_scouting_profile(self, player_id: int, team_id: Optional[int] = None) -> ScoutingProfileResponse:
        player = self.get_player_or_raise(player_id)
        analytics = self.analytics_svc.compute_overview(player_id)

        fit_score = None
        valuation = None
        try:
            if team_id:
                squad_players = self.squad_svc.get_squad_players(team_id)
                squad_analytics_map = self.build_analytics_map(squad_players)
                from app.services.auction.squad_fit_engine import SquadFitEngine
                fit_eval = SquadFitEngine.evaluate_fit(player, squad_players, analytics, squad_analytics_map)
                fit_score = fit_eval.squad_fit_score
                valuation = self.auction_svc.compute_player_valuation(auction_id=1, player_id=player_id, team_id=team_id)
            else:
                valuation = self.auction_svc.compute_player_valuation(auction_id=1, player_id=player_id, team_id=None)
        except Exception:
            pass

        return ScoutingProfileEngine.build_profile(
            player=player,
            analytics=analytics,
            valuation=valuation,
            squad_fit_score=fit_score,
        )

    # ── Part A2: Player Discovery ─────────────────────────────────────────────

    def discover_players(
        self,
        role: Optional[str] = None,
        batting_style: Optional[str] = None,
        bowling_style: Optional[str] = None,
        nationality: Optional[str] = None,
        is_wicketkeeper: Optional[bool] = None,
        is_active: Optional[bool] = True,
        min_intelligence_score: Optional[float] = None,
        min_batting_strike_rate: Optional[float] = None,
        min_batting_average: Optional[float] = None,
        min_bowling_wickets: Optional[int] = None,
        max_economy: Optional[float] = None,
        min_recent_form_score: Optional[float] = None,
        min_consistency: Optional[float] = None,
        min_squad_fit: Optional[float] = None,
        team_id: Optional[int] = None,
        scarcity_tier: Optional[str] = None,
        sort_by: str = "intelligence_score",
        sort_order: str = "desc",
        page: int = 1,
        size: int = 20,
    ) -> PlayerDiscoveryResponse:
        return self.discovery_engine.discover_players(
            role=role,
            batting_style=batting_style,
            bowling_style=bowling_style,
            nationality=nationality,
            is_wicketkeeper=is_wicketkeeper,
            is_active=is_active,
            min_intelligence_score=min_intelligence_score,
            min_batting_strike_rate=min_batting_strike_rate,
            min_batting_average=min_batting_average,
            min_bowling_wickets=min_bowling_wickets,
            max_economy=max_economy,
            min_recent_form_score=min_recent_form_score,
            min_consistency=min_consistency,
            min_squad_fit=min_squad_fit,
            team_id=team_id,
            scarcity_tier=scarcity_tier,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            size=size,
        )

    # ── Part A3: Candidate Ranking ────────────────────────────────────────────

    def rank_candidates(
        self,
        weights: Optional[RankingWeightsSchema] = None,
        team_id: Optional[int] = None,
        requested_role: Optional[str] = None,
    ) -> CandidateRankingResponse:
        w = weights or RankingWeightsSchema()
        candidates = self.get_candidate_pool()
        analytics_map = self.build_analytics_map(candidates)

        squad_players = []
        squad_analytics_map = {}
        if team_id:
            try:
                squad_players = self.squad_svc.get_squad_players(team_id)
                squad_analytics_map = self.build_analytics_map(squad_players)
            except Exception:
                pass

        return CandidateRankerEngine.rank_candidates(
            candidates=candidates,
            analytics_map=analytics_map,
            weights=w,
            squad_players=squad_players,
            squad_analytics_map=squad_analytics_map,
            team_id=team_id,
            requested_role=requested_role,
        )

    # ── Part B: Undervalued Player Engine ─────────────────────────────────────

    def get_undervalued_players(self, team_id: Optional[int] = None, min_undervaluation_score: float = 60.0) -> UndervaluedPlayerResponse:
        candidates = self.get_candidate_pool()
        analytics_map = self.build_analytics_map(candidates)

        squad_fit_map: Dict[int, float] = {}
        if team_id:
            try:
                squad_players = self.squad_svc.get_squad_players(team_id)
                squad_analytics_map = self.build_analytics_map(squad_players)
                from app.services.auction.squad_fit_engine import SquadFitEngine
                for p in candidates:
                    fit_eval = SquadFitEngine.evaluate_fit(p, squad_players, analytics_map[p.id], squad_analytics_map)
                    squad_fit_map[p.id] = fit_eval.squad_fit_score
            except Exception:
                pass

        return UnderratedPlayerEngine.identify_undervalued_players(
            candidates=candidates,
            analytics_map=analytics_map,
            squad_fit_map=squad_fit_map if squad_fit_map else None,
            min_undervaluation_score=min_undervaluation_score,
        )

    # ── Part C: Role-Specific Target Engine ───────────────────────────────────

    def get_role_targets(self, requested_role: str, team_id: Optional[int] = None) -> RoleTargetResponse:
        candidates = self.get_candidate_pool()
        analytics_map = self.build_analytics_map(candidates)

        squad_fit_map: Dict[int, float] = {}
        if team_id:
            try:
                squad_players = self.squad_svc.get_squad_players(team_id)
                squad_analytics_map = self.build_analytics_map(squad_players)
                from app.services.auction.squad_fit_engine import SquadFitEngine
                for p in candidates:
                    fit_eval = SquadFitEngine.evaluate_fit(p, squad_players, analytics_map[p.id], squad_analytics_map)
                    squad_fit_map[p.id] = fit_eval.squad_fit_score
            except Exception:
                pass

        return RoleTargetEngine.evaluate_role_targets(
            requested_role=requested_role,
            candidates=candidates,
            analytics_map=analytics_map,
            squad_fit_map=squad_fit_map if squad_fit_map else None,
        )

    # ── Part D: Scouting Recommendation Engine ────────────────────────────────

    def get_recommendations(
        self,
        team_id: Optional[int] = None,
        budget: float = 1000.0,
        slots_needed: int = 5,
    ) -> ScoutingRecommendationResponse:
        candidates = self.get_candidate_pool()
        analytics_map = self.build_analytics_map(candidates)

        squad_fit_map: Dict[int, float] = {}
        if team_id:
            try:
                squad_players = self.squad_svc.get_squad_players(team_id)
                squad_analytics_map = self.build_analytics_map(squad_players)
                from app.services.auction.squad_fit_engine import SquadFitEngine
                for p in candidates:
                    fit_eval = SquadFitEngine.evaluate_fit(p, squad_players, analytics_map[p.id], squad_analytics_map)
                    squad_fit_map[p.id] = fit_eval.squad_fit_score
            except Exception:
                pass

        return RecommendationEngine.generate_recommendations(
            candidates=candidates,
            analytics_map=analytics_map,
            team_id=team_id,
            squad_fit_map=squad_fit_map if squad_fit_map else None,
            budget=budget,
            slots_needed=slots_needed,
        )

    # ── Part E: Scouting Report Generator ─────────────────────────────────────

    def get_scouting_report(self, player_id: int, team_id: Optional[int] = None) -> ScoutingReportResponse:
        player = self.get_player_or_raise(player_id)
        analytics = self.analytics_svc.compute_overview(player_id)

        fit_score = None
        valuation = None
        try:
            if team_id:
                squad_players = self.squad_svc.get_squad_players(team_id)
                squad_analytics_map = self.build_analytics_map(squad_players)
                from app.services.auction.squad_fit_engine import SquadFitEngine
                fit_eval = SquadFitEngine.evaluate_fit(player, squad_players, analytics, squad_analytics_map)
                fit_score = fit_eval.squad_fit_score
                valuation = self.auction_svc.compute_player_valuation(auction_id=1, player_id=player_id, team_id=team_id)
            else:
                valuation = self.auction_svc.compute_player_valuation(auction_id=1, player_id=player_id, team_id=None)
        except Exception:
            pass

        return ScoutingReportGenerator.generate_report(
            player=player,
            analytics=analytics,
            valuation=valuation,
            squad_fit_score=fit_score,
        )

    # ── Part F: Tactical Role Simulation ──────────────────────────────────────

    def get_tactical_role_fit(self, player_id: int, evaluated_role: str) -> TacticalRoleFitResponse:
        player = self.get_player_or_raise(player_id)
        analytics = self.analytics_svc.compute_overview(player_id)
        return TacticalSimulatorEngine.evaluate_tactical_role(
            player=player,
            analytics=analytics,
            evaluated_role=evaluated_role,
        )

    # ── Part G: Scouting Watchlist CRUD ───────────────────────────────────────

    def get_watchlist(
        self,
        priority: Optional[WatchlistPriority] = None,
        status: Optional[WatchlistStatus] = None,
        player_id: Optional[int] = None,
    ) -> List[WatchlistResponse]:
        stmt = select(ScoutingWatchlist)
        conds = []
        if priority:
            conds.append(ScoutingWatchlist.priority == priority)
        if status:
            conds.append(ScoutingWatchlist.status == status)
        if player_id:
            conds.append(ScoutingWatchlist.player_id == player_id)

        if conds:
            stmt = stmt.where(*conds)

        stmt = stmt.order_by(ScoutingWatchlist.updated_at.desc())
        entries = list(self.db.scalars(stmt).all())

        res: List[WatchlistResponse] = []
        for e in entries:
            player_name = e.player.name if e.player else "Unknown Player"
            role_str = str(e.player.role.value if hasattr(e.player.role, "value") else e.player.role) if e.player else "batter"
            res.append(
                WatchlistResponse(
                    id=e.id,
                    player_id=e.player_id,
                    player_name=player_name,
                    role=role_str,
                    priority=e.priority,
                    status=e.status,
                    notes=e.notes,
                    tags=e.tags,
                    created_at=e.created_at,
                    updated_at=e.updated_at,
                )
            )
        return res

    def add_to_watchlist(self, req: WatchlistCreateRequest) -> WatchlistResponse:
        self.get_player_or_raise(req.player_id)

        entry = ScoutingWatchlist(
            player_id=req.player_id,
            priority=req.priority,
            status=req.status,
            notes=req.notes,
            tags=req.tags or [],
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)

        return self.get_watchlist_by_id_or_raise(entry.id)

    def get_watchlist_by_id_or_raise(self, watchlist_id: int) -> WatchlistResponse:
        entry = self.db.scalar(select(ScoutingWatchlist).where(ScoutingWatchlist.id == watchlist_id))
        if not entry:
            raise WatchlistNotFoundError(watchlist_id)

        player_name = entry.player.name if entry.player else "Unknown Player"
        role_str = str(entry.player.role.value if hasattr(entry.player.role, "value") else entry.player.role) if entry.player else "batter"

        return WatchlistResponse(
            id=entry.id,
            player_id=entry.player_id,
            player_name=player_name,
            role=role_str,
            priority=entry.priority,
            status=entry.status,
            notes=entry.notes,
            tags=entry.tags,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
        )

    def update_watchlist(self, watchlist_id: int, req: WatchlistUpdateRequest) -> WatchlistResponse:
        entry = self.db.scalar(select(ScoutingWatchlist).where(ScoutingWatchlist.id == watchlist_id))
        if not entry:
            raise WatchlistNotFoundError(watchlist_id)

        if req.priority is not None:
            entry.priority = req.priority
        if req.status is not None:
            entry.status = req.status
        if req.notes is not None:
            entry.notes = req.notes
        if req.tags is not None:
            entry.tags = req.tags

        self.db.commit()
        self.db.refresh(entry)

        return self.get_watchlist_by_id_or_raise(entry.id)

    def delete_watchlist(self, watchlist_id: int) -> None:
        entry = self.db.scalar(select(ScoutingWatchlist).where(ScoutingWatchlist.id == watchlist_id))
        if not entry:
            raise WatchlistNotFoundError(watchlist_id)

        self.db.delete(entry)
        self.db.commit()

    # ── Part H: Scouting Notes CRUD ───────────────────────────────────────────

    def get_notes(
        self,
        player_id: Optional[int] = None,
        category: Optional[ScoutingNoteCategory] = None,
    ) -> List[ScoutingNoteResponse]:
        stmt = select(ScoutingNote)
        conds = []
        if player_id:
            conds.append(ScoutingNote.player_id == player_id)
        if category:
            conds.append(ScoutingNote.category == category)

        if conds:
            stmt = stmt.where(*conds)

        stmt = stmt.order_by(ScoutingNote.created_at.desc())
        notes = list(self.db.scalars(stmt).all())

        res: List[ScoutingNoteResponse] = []
        for n in notes:
            player_name = n.player.name if n.player else "Unknown Player"
            res.append(
                ScoutingNoteResponse(
                    id=n.id,
                    player_id=n.player_id,
                    player_name=player_name,
                    category=n.category,
                    observation=n.observation,
                    confidence=n.confidence,
                    author=n.author,
                    created_at=n.created_at,
                    updated_at=n.updated_at,
                )
            )
        return res

    def add_note(self, req: ScoutingNoteCreateRequest) -> ScoutingNoteResponse:
        self.get_player_or_raise(req.player_id)

        note = ScoutingNote(
            player_id=req.player_id,
            category=req.category,
            observation=req.observation,
            confidence=req.confidence,
            author=req.author,
        )
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)

        player_name = note.player.name if note.player else "Unknown Player"

        return ScoutingNoteResponse(
            id=note.id,
            player_id=note.player_id,
            player_name=player_name,
            category=note.category,
            observation=note.observation,
            confidence=note.confidence,
            author=note.author,
            created_at=note.created_at,
            updated_at=note.updated_at,
        )
