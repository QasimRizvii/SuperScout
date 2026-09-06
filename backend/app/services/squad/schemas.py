"""
SuperScout Backend — Squad Intelligence Pydantic Response Schemas
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.models.enums import PlayerRole


class RoleDistributionSummary(BaseModel):
    """Counts of players across role classifications."""

    total_squad_size: int = 0
    batters_count: int = 0
    bowlers_count: int = 0
    all_rounders_count: int = 0
    wicketkeepers_count: int = 0
    pace_bowlers_count: int = 0
    spin_bowlers_count: int = 0


class PhaseCoverageSummary(BaseModel):
    """Resource coverage across Powerplay, Middle, and Death overs."""

    powerplay_batters_count: int = 0
    middle_batters_count: int = 0
    finishers_count: int = 0
    powerplay_bowlers_count: int = 0
    middle_bowlers_count: int = 0
    death_bowlers_count: int = 0


class BalanceSubScore(BaseModel):
    """Component score entry in Squad Balance calculation."""

    score: float = 0.0
    weight: float = 0.0
    weighted_score: float = 0.0
    description: str = ""


class SquadBalanceResponse(BaseModel):
    """Explainable Squad Balance Score and tactical audit."""

    team_id: int
    team_name: str
    squad_size: int = 0
    overall_balance_score: float = 0.0  # 0 to 100
    role_coverage_score: BalanceSubScore = Field(default_factory=BalanceSubScore)
    depth_score: BalanceSubScore = Field(default_factory=BalanceSubScore)
    phase_balance_score: BalanceSubScore = Field(default_factory=BalanceSubScore)
    specialist_cover_score: BalanceSubScore = Field(default_factory=BalanceSubScore)
    versatility_score: BalanceSubScore = Field(default_factory=BalanceSubScore)
    role_distribution: RoleDistributionSummary = Field(default_factory=RoleDistributionSummary)
    phase_coverage: PhaseCoverageSummary = Field(default_factory=PhaseCoverageSummary)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)


class PlayingXIPlayer(BaseModel):
    """Individual player entry in recommended Playing XI."""

    player_id: int
    player_name: str
    role: PlayerRole
    batting_position: int  # 1 to 11
    is_captain: bool = False
    is_wicketkeeper: bool = False
    primary_capability: str = ""
    bowling_phase_assignment: Optional[str] = None  # Powerplay, Middle, Death, None
    selection_reason: str = ""


class PlayingXIOptimizationResponse(BaseModel):
    """Recommended Playing XI and tactical breakdown."""

    team_id: int
    team_name: str
    recommended_xi: List[PlayingXIPlayer] = Field(default_factory=list)
    captain_player_id: Optional[int] = None
    captain_player_name: Optional[str] = None
    wicketkeeper_player_id: Optional[int] = None
    wicketkeeper_player_name: Optional[str] = None
    batting_order_summary: List[str] = Field(default_factory=list)
    powerplay_bowlers: List[str] = Field(default_factory=list)
    middle_bowlers: List[str] = Field(default_factory=list)
    death_bowlers: List[str] = Field(default_factory=list)
    impact_substitute_candidates: List[str] = Field(default_factory=list)
    tactical_summary: str = ""


class InternalReplacementOption(BaseModel):
    """Bench player recommendation when a key player is unavailable."""

    player_id: int
    player_name: str
    role: PlayerRole
    intelligence_score: float = 0.0
    replacement_fit_reason: str = ""


class ScenarioAnalysisRequest(BaseModel):
    """Request model for player unavailability scenario simulation."""

    unavailable_player_ids: List[int] = Field(..., description="IDs of unavailable/injured players")


class ScenarioAnalysisResponse(BaseModel):
    """Squad balance impact report when key players are unavailable."""

    team_id: int
    team_name: str
    unavailable_player_ids: List[int] = Field(default_factory=list)
    baseline_balance_score: float = 0.0
    scenario_balance_score: float = 0.0
    score_delta: float = 0.0
    newly_exposed_gaps: List[str] = Field(default_factory=list)
    recommended_replacements: List[InternalReplacementOption] = Field(default_factory=list)
    explanation: str = ""


class RecruitCandidate(BaseModel):
    """Database player candidate for recruitment gap filling."""

    player_id: int
    player_name: str
    role: PlayerRole
    current_team_name: Optional[str] = None
    intelligence_score: float = 0.0
    fit_reason: str = ""


class RoleGapRecommendation(BaseModel):
    """Identified squad role deficiency and recruitment target profile."""

    gap_title: str
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    reason: str
    target_player_profile: str
    candidate_players: List[RecruitCandidate] = Field(default_factory=list)


class SquadRoleAnalysisResponse(BaseModel):
    """Detailed role coverage and resources breakdown."""

    team_id: int
    team_name: str
    role_distribution: RoleDistributionSummary
    phase_coverage: PhaseCoverageSummary
    pace_spin_breakdown: Dict[str, int] = Field(default_factory=dict)


class SquadComparisonItem(BaseModel):
    """Side-by-side metric comparison entry."""

    dimension: str
    team_1_value: Any
    team_2_value: Any
    advantage_team_id: Optional[int] = None
    note: str = ""


class SquadComparisonResponse(BaseModel):
    """Head-to-head multi-squad comparison report."""

    team_1_id: int
    team_1_name: str
    team_2_id: int
    team_2_name: str
    comparison_matrix: List[SquadComparisonItem] = Field(default_factory=list)
    team_1_strengths: List[str] = Field(default_factory=list)
    team_2_strengths: List[str] = Field(default_factory=list)
    overall_advantage_team_id: Optional[int] = None
    summary: str = ""


class SquadIntelligenceOverviewResponse(BaseModel):
    """Unified squad intelligence dashboard profile."""

    team_id: int
    team_name: str
    squad_size: int = 0
    balance: SquadBalanceResponse
    playing_xi: PlayingXIOptimizationResponse
    gaps: List[RoleGapRecommendation] = Field(default_factory=list)
