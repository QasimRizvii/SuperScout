"""
SuperScout Backend — Player Analytics Orchestrator Service

Orchestrates database queries, statistical engines, consistency metrics, recent form,
role profile evaluation, and Player Intelligence Score generation.
"""
import math
import statistics
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.batting import BattingPerformance
from app.models.bowling import BowlingPerformance
from app.models.match import Match
from app.models.player import Player
from app.services.analytics.batting import BattingAnalyticsEngine
from app.services.analytics.bowling import BowlingAnalyticsEngine
from app.services.analytics.comparison import PlayerComparisonEngine
from app.services.analytics.exceptions import PlayerNotFoundError
from app.services.analytics.scoring import PlayerIntelligenceScorer
from app.services.analytics.schemas import (
    BattingAnalyticsResponse,
    BowlingAnalyticsResponse,
    ConsistencyMetrics,
    IntelligenceScoreResponse,
    MetricValue,
    PerformanceMatchSummary,
    PlayerAnalyticsOverviewResponse,
    PlayerComparisonResponse,
    RecentFormResponse,
)


class PlayerAnalyticsService:
    """Main orchestrator service for Player Intelligence & Analytics Engine."""

    def __init__(self, db: Session):
        self.db = db

    def get_player_or_raise(self, player_id: int) -> Player:
        """Fetch Player entity or raise PlayerNotFoundError."""
        player = self.db.scalar(select(Player).where(Player.id == player_id))
        if not player:
            raise PlayerNotFoundError(player_id)
        return player

    def get_batting_performances(self, player_id: int) -> List[BattingPerformance]:
        """Fetch all batting performances for player ordered chronologically."""
        stmt = (
            select(BattingPerformance)
            .options(selectinload(BattingPerformance.match))
            .where(BattingPerformance.player_id == player_id)
            .join(Match, BattingPerformance.match_id == Match.id)
            .order_by(Match.match_date.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_bowling_performances(self, player_id: int) -> List[BowlingPerformance]:
        """Fetch all bowling performances for player ordered chronologically."""
        stmt = (
            select(BowlingPerformance)
            .options(selectinload(BowlingPerformance.match))
            .where(BowlingPerformance.player_id == player_id)
            .join(Match, BowlingPerformance.match_id == Match.id)
            .order_by(Match.match_date.desc())
        )
        return list(self.db.scalars(stmt).all())

    def compute_batting_analytics(self, player_id: int) -> BattingAnalyticsResponse:
        """Compute complete career batting analytics for player."""
        player = self.get_player_or_raise(player_id)
        perfs = self.get_batting_performances(player_id)
        return BattingAnalyticsEngine.compute_batting_analytics(player.id, player.name, perfs)

    def compute_bowling_analytics(self, player_id: int) -> BowlingAnalyticsResponse:
        """Compute complete career bowling analytics for player."""
        player = self.get_player_or_raise(player_id)
        perfs = self.get_bowling_performances(player_id)
        return BowlingAnalyticsEngine.compute_bowling_analytics(player.id, player.name, perfs)

    def compute_consistency(self, player_id: int) -> ConsistencyMetrics:
        """Compute statistical dispersion and consistency metrics."""
        perfs = self.get_batting_performances(player_id)
        sample_size = len(perfs)

        if sample_size == 0:
            return ConsistencyMetrics(
                sample_size=0,
                mean_runs=MetricValue(value=None, sample_size=0, metric_available=False, reason="No batting innings"),
                median_runs=MetricValue(value=None, sample_size=0, metric_available=False, reason="No batting innings"),
                std_dev_runs=MetricValue(value=None, sample_size=0, metric_available=False, reason="No batting innings"),
                coefficient_of_variation=MetricValue(value=None, sample_size=0, metric_available=False, reason="No batting innings"),
                meaningful_contributions_pct=MetricValue(value=None, sample_size=0, metric_available=False, reason="No batting innings"),
                high_impact_performances_pct=MetricValue(value=None, sample_size=0, metric_available=False, reason="No batting innings"),
                low_score_frequency_pct=MetricValue(value=None, sample_size=0, metric_available=False, reason="No batting innings"),
                sample_confidence=0.0,
            )

        runs_list = [p.runs for p in perfs]
        mean_r = round(float(statistics.mean(runs_list)), 2)
        median_r = round(float(statistics.median(runs_list)), 2)

        if sample_size >= 2:
            std_dev_r = round(float(statistics.stdev(runs_list)), 2)
            cv_val = round(std_dev_r / mean_r, 2) if mean_r > 0 else None
            cv_metric = MetricValue(value=cv_val, sample_size=sample_size, metric_available=(cv_val is not None))
        else:
            std_dev_r = 0.0
            cv_metric = MetricValue(value=None, sample_size=1, metric_available=False, reason="Sample size < 2")

        meaningful_count = sum(1 for r in runs_list if r >= 30)
        high_impact_count = sum(
            1 for p in perfs if p.runs >= 50 or (p.balls_faced >= 10 and (p.strike_rate or 0) >= 150.0)
        )
        low_score_count = sum(1 for r in runs_list if r < 10)

        meaningful_pct = round((meaningful_count / sample_size) * 100.0, 2)
        high_impact_pct = round((high_impact_count / sample_size) * 100.0, 2)
        low_score_pct = round((low_score_count / sample_size) * 100.0, 2)

        confidence_factor = round(min(1.0, math.sqrt(sample_size / 10.0)), 2)

        return ConsistencyMetrics(
            sample_size=sample_size,
            mean_runs=MetricValue(value=mean_r, sample_size=sample_size, metric_available=True),
            median_runs=MetricValue(value=median_r, sample_size=sample_size, metric_available=True),
            std_dev_runs=MetricValue(value=std_dev_r, sample_size=sample_size, metric_available=(sample_size >= 2)),
            coefficient_of_variation=cv_metric,
            meaningful_contributions_pct=MetricValue(value=meaningful_pct, sample_size=sample_size, metric_available=True),
            high_impact_performances_pct=MetricValue(value=high_impact_pct, sample_size=sample_size, metric_available=True),
            low_score_frequency_pct=MetricValue(value=low_score_pct, sample_size=sample_size, metric_available=True),
            sample_confidence=confidence_factor,
        )

    def compute_recent_form(self, player_id: int, window: int = 5) -> RecentFormResponse:
        """Compute recent performance window metrics for player."""
        player = self.get_player_or_raise(player_id)
        window = max(1, min(window, 50))

        bat_perfs = self.get_batting_performances(player_id)[:window]
        bowl_perfs = self.get_bowling_performances(player_id)[:window]

        actual_size = max(len(bat_perfs), len(bowl_perfs))

        recent_batting = BattingAnalyticsEngine.compute_batting_analytics(
            player.id, player.name, bat_perfs
        )
        recent_bowling = BowlingAnalyticsEngine.compute_bowling_analytics(
            player.id, player.name, bowl_perfs
        )

        summaries: List[PerformanceMatchSummary] = []
        for p in bat_perfs:
            summaries.append(
                PerformanceMatchSummary(
                    match_id=p.match_id,
                    match_date=str(p.match.match_date) if p.match else "",
                    competition=p.match.competition if p.match else None,
                    runs=p.runs,
                    balls_faced=p.balls_faced,
                    strike_rate=p.strike_rate,
                )
            )

        return RecentFormResponse(
            player_id=player.id,
            player_name=player.name,
            window_requested=window,
            actual_sample_size=actual_size,
            recent_batting=recent_batting,
            recent_bowling=recent_bowling,
            match_summaries=summaries,
        )

    def compute_intelligence_score(self, player_id: int) -> IntelligenceScoreResponse:
        """Compute deterministic Player Intelligence Score for player."""
        player = self.get_player_or_raise(player_id)
        batting = self.compute_batting_analytics(player_id)
        bowling = self.compute_bowling_analytics(player_id)
        consistency = self.compute_consistency(player_id)
        recent_form = self.compute_recent_form(player_id, window=5)

        return PlayerIntelligenceScorer.compute_score(
            player.id,
            player.name,
            player.role,
            batting,
            bowling,
            consistency,
            recent_form,
        )

    def compute_overview(self, player_id: int) -> PlayerAnalyticsOverviewResponse:
        """Compute complete unified analytics overview for player."""
        player = self.get_player_or_raise(player_id)
        batting = self.compute_batting_analytics(player_id)
        bowling = self.compute_bowling_analytics(player_id)
        consistency = self.compute_consistency(player_id)
        recent_form = self.compute_recent_form(player_id, window=5)
        score = PlayerIntelligenceScorer.compute_score(
            player.id,
            player.name,
            player.role,
            batting,
            bowling,
            consistency,
            recent_form,
        )

        return PlayerAnalyticsOverviewResponse(
            player_id=player.id,
            player_name=player.name,
            short_name=player.short_name,
            role=player.role,
            nationality=player.nationality,
            is_active=player.is_active,
            intelligence_score=score,
            batting=batting,
            bowling=bowling,
            consistency=consistency,
            recent_form=recent_form,
        )

    def compare_players(self, player_ids: List[int]) -> PlayerComparisonResponse:
        """Compare 2 to 5 players head-to-head."""
        overviews: List[PlayerAnalyticsOverviewResponse] = []
        for pid in player_ids:
            overviews.append(self.compute_overview(pid))
        return PlayerComparisonEngine.compare_players(overviews)
