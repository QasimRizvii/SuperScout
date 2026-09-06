"""
SuperScout Backend — Analytics Pydantic Response Schemas
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.models.enums import PlayerRole


class MetricValue(BaseModel):
    """Wrapper for statistical metric availability and sample context."""

    value: Optional[float] = None
    sample_size: int = 0
    metric_available: bool = True
    reason: Optional[str] = None


class PhaseBattingStats(BaseModel):
    """Batting metrics broken down by phase."""

    runs: int = 0
    balls: int = 0
    strike_rate: Optional[float] = None
    fours: int = 0
    sixes: int = 0
    boundary_runs: int = 0
    boundary_percentage: Optional[float] = None
    dot_balls: int = 0
    dot_ball_percentage: Optional[float] = None
    phase_contribution_pct: Optional[float] = None


class PhaseBowlingStats(BaseModel):
    """Bowling metrics broken down by phase."""

    overs: float = 0.0
    balls: int = 0
    runs_conceded: int = 0
    wickets: int = 0
    economy: Optional[float] = None
    dot_balls: int = 0
    phase_overs_pct: Optional[float] = None


class BattingPhaseAnalytics(BaseModel):
    """Container for Powerplay, Middle, and Death batting phases."""

    powerplay: PhaseBattingStats = Field(default_factory=PhaseBattingStats)
    middle: PhaseBattingStats = Field(default_factory=PhaseBattingStats)
    death: PhaseBattingStats = Field(default_factory=PhaseBattingStats)


class BowlingPhaseAnalytics(BaseModel):
    """Container for Powerplay, Middle, and Death bowling phases."""

    powerplay: PhaseBowlingStats = Field(default_factory=PhaseBowlingStats)
    middle: PhaseBowlingStats = Field(default_factory=PhaseBowlingStats)
    death: PhaseBowlingStats = Field(default_factory=PhaseBowlingStats)


class BattingAnalyticsResponse(BaseModel):
    """Comprehensive player batting statistics."""

    player_id: int
    player_name: str
    sample_size: int = 0  # Number of innings
    innings: int = 0
    runs: int = 0
    balls_faced: int = 0
    dismissals: int = 0
    not_outs: int = 0
    highest_score: int = 0
    batting_average: MetricValue = Field(default_factory=MetricValue)
    strike_rate: MetricValue = Field(default_factory=MetricValue)
    fours: int = 0
    sixes: int = 0
    boundary_runs: int = 0
    boundary_percentage: MetricValue = Field(default_factory=MetricValue)
    balls_per_boundary: MetricValue = Field(default_factory=MetricValue)
    dot_balls: int = 0
    dot_ball_percentage: MetricValue = Field(default_factory=MetricValue)
    runs_per_innings: MetricValue = Field(default_factory=MetricValue)
    runs_per_100_balls: MetricValue = Field(default_factory=MetricValue)
    dismissal_rate: MetricValue = Field(default_factory=MetricValue)
    phases: BattingPhaseAnalytics = Field(default_factory=BattingPhaseAnalytics)


class BowlingAnalyticsResponse(BaseModel):
    """Comprehensive player bowling statistics."""

    player_id: int
    player_name: str
    sample_size: int = 0  # Number of innings bowled
    innings_bowled: int = 0
    balls_bowled: int = 0
    overs: float = 0.0
    runs_conceded: int = 0
    wickets: int = 0
    economy_rate: MetricValue = Field(default_factory=MetricValue)
    bowling_average: MetricValue = Field(default_factory=MetricValue)
    bowling_strike_rate: MetricValue = Field(default_factory=MetricValue)
    dot_balls: int = 0
    dot_ball_percentage: MetricValue = Field(default_factory=MetricValue)
    maidens: int = 0
    wides: int = 0
    no_balls: int = 0
    extras_conceded: int = 0
    wickets_per_innings: MetricValue = Field(default_factory=MetricValue)
    phases: BowlingPhaseAnalytics = Field(default_factory=BowlingPhaseAnalytics)


class ConsistencyMetrics(BaseModel):
    """Statistical dispersion and reliability metrics."""

    sample_size: int = 0
    mean_runs: MetricValue = Field(default_factory=MetricValue)
    median_runs: MetricValue = Field(default_factory=MetricValue)
    std_dev_runs: MetricValue = Field(default_factory=MetricValue)
    coefficient_of_variation: MetricValue = Field(default_factory=MetricValue)
    meaningful_contributions_pct: MetricValue = Field(default_factory=MetricValue)  # runs >= 30
    high_impact_performances_pct: MetricValue = Field(default_factory=MetricValue)  # runs >= 50 or SR >= 150
    low_score_frequency_pct: MetricValue = Field(default_factory=MetricValue)  # runs < 10
    sample_confidence: float = 0.0  # 0.0 to 1.0 multiplier based on sample size


class PerformanceMatchSummary(BaseModel):
    """Individual match performance snippet for recent form windowing."""

    match_id: int
    match_date: str
    opponent_team_name: Optional[str] = None
    competition: Optional[str] = None
    runs: Optional[int] = None
    balls_faced: Optional[int] = None
    strike_rate: Optional[float] = None
    wickets: Optional[int] = None
    runs_conceded: Optional[int] = None
    economy: Optional[float] = None


class RecentFormResponse(BaseModel):
    """Recent performance window analysis."""

    player_id: int
    player_name: str
    window_requested: int = 5
    actual_sample_size: int = 0
    recent_batting: BattingAnalyticsResponse
    recent_bowling: BowlingAnalyticsResponse
    match_summaries: List[PerformanceMatchSummary] = Field(default_factory=list)


class ScoreComponent(BaseModel):
    """Individual sub-score entry in Player Intelligence Score."""

    score: float = 0.0
    weight: float = 0.0
    weighted_score: float = 0.0
    description: str = ""


class IntelligenceScoreResponse(BaseModel):
    """Explainable statistical Player Intelligence Score."""

    player_id: int
    player_name: str
    role: PlayerRole
    overall_score: float = 0.0  # 0 to 100
    confidence_factor: float = 0.0  # 0.0 to 1.0 based on sample size
    sample_size: int = 0
    batting_score: ScoreComponent = Field(default_factory=ScoreComponent)
    bowling_score: ScoreComponent = Field(default_factory=ScoreComponent)
    consistency_score: ScoreComponent = Field(default_factory=ScoreComponent)
    recent_form_score: ScoreComponent = Field(default_factory=ScoreComponent)
    phase_impact_score: ScoreComponent = Field(default_factory=ScoreComponent)
    explanation: str = ""


class PlayerAnalyticsOverviewResponse(BaseModel):
    """Unified player intelligence and analytics dashboard profile."""

    player_id: int
    player_name: str
    short_name: Optional[str] = None
    role: PlayerRole
    nationality: Optional[str] = None
    is_active: bool = True
    intelligence_score: IntelligenceScoreResponse
    batting: BattingAnalyticsResponse
    bowling: BowlingAnalyticsResponse
    consistency: ConsistencyMetrics
    recent_form: RecentFormResponse


class PlayerComparisonMatrixItem(BaseModel):
    """Per-player entry in multi-player comparison response."""

    player_id: int
    player_name: str
    role: PlayerRole
    sample_size: int = 0
    overall_score: float = 0.0
    batting_average: Optional[float] = None
    strike_rate: Optional[float] = None
    boundary_pct: Optional[float] = None
    bowling_economy: Optional[float] = None
    bowling_average: Optional[float] = None
    wickets: int = 0
    consistency_cv: Optional[float] = None
    recent_form_runs: Optional[int] = None
    recent_form_sr: Optional[float] = None


class PlayerComparisonResponse(BaseModel):
    """Multi-player statistical comparison report."""

    players_compared: int
    players: List[PlayerComparisonMatrixItem] = Field(default_factory=list)
    top_batter_player_id: Optional[int] = None
    top_bowler_player_id: Optional[int] = None
    top_overall_player_id: Optional[int] = None
    summary: str = ""
