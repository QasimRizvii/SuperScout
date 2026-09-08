"""
SuperScout Backend — Scouting Schemas
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from app.models.enums import (
    PlayerRole,
    WatchlistStatus,
    WatchlistPriority,
    ScoutingNoteCategory,
)


# ── Scouting Profile Schemas ───────────────────────────────────────────────────

class PlayerIdentitySchema(BaseModel):
    player_id: int
    name: str
    short_name: Optional[str] = None
    nationality: Optional[str] = None
    age: Optional[int] = None
    role: str
    batting_style: Optional[str] = None
    bowling_style: Optional[str] = None
    is_wicketkeeper: bool = False
    is_active: bool = True


class PerformanceSummarySchema(BaseModel):
    runs: int = 0
    batting_average: Optional[float] = None
    strike_rate: Optional[float] = None
    highest_score: int = 0
    boundary_percentage: Optional[float] = None
    dot_ball_percentage: Optional[float] = None
    balls_per_boundary: Optional[float] = None
    wickets: int = 0
    economy: Optional[float] = None
    bowling_average: Optional[float] = None
    bowling_strike_rate: Optional[float] = None
    bowling_dot_ball_percentage: Optional[float] = None
    phase_performance: Dict[str, Any] = Field(default_factory=dict)
    recent_form_summary: Dict[str, Any] = Field(default_factory=dict)
    consistency_summary: Dict[str, Any] = Field(default_factory=dict)


class IntelligenceSummarySchema(BaseModel):
    intelligence_score: float = 0.0
    sample_confidence: float = 0.0
    recent_form_score: float = 0.0
    role_score: float = 0.0
    consistency_score: float = 0.0
    impact_score: float = 0.0


class AuctionSummarySchema(BaseModel):
    estimated_fair_value: float = 0.0
    squad_fit_score: Optional[float] = None
    scarcity_score: float = 0.0
    recommended_bid_ceiling: float = 0.0
    target_tier: str = "TIER_3"
    opportunity_cost_summary: Optional[Dict[str, Any]] = None


class ScoutingAssessmentSchema(BaseModel):
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    ideal_role: str = "General Squad Member"
    secondary_role: Optional[str] = None
    tactical_value: str = ""
    risk_indicators: List[str] = Field(default_factory=list)
    development_indicators: List[str] = Field(default_factory=list)
    recommended_usage: str = ""


class ScoutingProfileResponse(BaseModel):
    identity: PlayerIdentitySchema
    performance: PerformanceSummarySchema
    intelligence: IntelligenceSummarySchema
    auction: AuctionSummarySchema
    scouting: ScoutingAssessmentSchema


# ── Player Discovery Schemas ───────────────────────────────────────────────────

class DiscoveredPlayerItem(BaseModel):
    player_id: int
    name: str
    role: str
    nationality: Optional[str] = None
    batting_style: Optional[str] = None
    bowling_style: Optional[str] = None
    is_wicketkeeper: bool = False
    is_active: bool = True
    intelligence_score: float = 0.0
    recent_form_score: float = 0.0
    consistency_score: float = 0.0
    impact_score: float = 0.0
    squad_fit_score: Optional[float] = None
    scarcity_score: float = 0.0
    estimated_value: float = 0.0
    value_for_money_score: float = 0.0
    runs: int = 0
    batting_average: Optional[float] = None
    strike_rate: Optional[float] = None
    wickets: int = 0
    economy: Optional[float] = None


class PlayerDiscoveryResponse(BaseModel):
    total_candidates: int
    page: int
    size: int
    total_pages: int
    items: List[DiscoveredPlayerItem]


# ── Candidate Ranking Schemas ──────────────────────────────────────────────────

class RankingWeightsSchema(BaseModel):
    performance_weight: float = 0.25
    recent_form_weight: float = 0.20
    consistency_weight: float = 0.15
    role_fit_weight: float = 0.15
    squad_fit_weight: float = 0.10
    scarcity_weight: float = 0.10
    tactical_value_weight: float = 0.05


class RankedCandidateItem(BaseModel):
    rank: int
    player_id: int
    player_name: str
    role: str
    scouting_score: float
    confidence: float
    component_scores: Dict[str, float]
    reasons: List[str]
    risks: List[str]


class CandidateRankingResponse(BaseModel):
    team_id: Optional[int] = None
    weights_used: RankingWeightsSchema
    total_ranked: int
    candidates: List[RankedCandidateItem]


# ── Undervalued Player Schemas ────────────────────────────────────────────────

class UndervaluedPlayerItem(BaseModel):
    player_id: int
    player_name: str
    role: str
    undervaluation_score: float
    estimated_value: float
    expected_contribution: str
    price_value_relationship: str
    undervaluation_type: str  # statistical, auction, role_scarcity
    reasons: List[str]
    confidence: float
    risk_factors: List[str]


class UndervaluedPlayerResponse(BaseModel):
    total_found: int
    players: List[UndervaluedPlayerItem]


# ── Role Target Schemas ────────────────────────────────────────────────────────

class RoleTargetItem(BaseModel):
    player_id: int
    player_name: str
    primary_role: str
    suitability_score: float
    relevant_statistics: Dict[str, Any]
    squad_fit: Optional[float] = None
    scarcity_score: float = 0.0
    estimated_value: float = 0.0
    recommendation_reason: str
    risk: str


class RoleTargetResponse(BaseModel):
    requested_role: str
    total_candidates: int
    candidates: List[RoleTargetItem]


# ── Scouting Recommendation Schemas ─────────────────────────────────────────

class ScoutingTargetRecommendation(BaseModel):
    rank: int
    player_id: int
    player_name: str
    primary_role: str
    scouting_score: float
    squad_fit: Optional[float] = None
    estimated_value: float
    why_scout: str
    main_risk: str
    expected_tactical_use: str
    confidence: float


class ScoutingRecommendationResponse(BaseModel):
    team_id: Optional[int] = None
    budget: float = 1000.0
    slots_needed: int = 5
    immediate_priorities: List[ScoutingTargetRecommendation]
    secondary_targets: List[ScoutingTargetRecommendation]
    watchlist_candidates: List[ScoutingTargetRecommendation]
    avoid_candidates: List[ScoutingTargetRecommendation]


# ── Scouting Report Schemas ────────────────────────────────────────────────────

class ScoutingReportResponse(BaseModel):
    player: PlayerIdentitySchema
    summary: str
    role_assessment: Dict[str, Any]
    batting_assessment: Dict[str, Any]
    bowling_assessment: Dict[str, Any]
    phase_assessment: Dict[str, Any]
    recent_form: Dict[str, Any]
    consistency: Dict[str, Any]
    squad_fit: Dict[str, Any]
    auction_assessment: Dict[str, Any]
    strengths: List[str]
    weaknesses: List[str]
    risks: List[str]
    recommended_usage: List[str]
    scouting_verdict: str  # PRIORITY TARGET, STRONG TARGET, WATCHLIST, DEVELOPMENT TARGET, LOW PRIORITY, AVOID
    verdict_explanation: str
    confidence: float


# ── Tactical Role Fit Schemas ──────────────────────────────────────────────────

class TacticalRoleFitResponse(BaseModel):
    player_id: int
    player_name: str
    evaluated_role: str
    suitability_score: float
    supporting_metrics: Dict[str, Any]
    advantages: List[str]
    disadvantages: List[str]
    confidence: float


# ── Watchlist Schemas ──────────────────────────────────────────────────────────

class WatchlistCreateRequest(BaseModel):
    player_id: int
    priority: WatchlistPriority = WatchlistPriority.MEDIUM
    status: WatchlistStatus = WatchlistStatus.NEW
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class WatchlistUpdateRequest(BaseModel):
    priority: Optional[WatchlistPriority] = None
    status: Optional[WatchlistStatus] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class WatchlistResponse(BaseModel):
    id: int
    player_id: int
    player_name: str
    role: str
    priority: WatchlistPriority
    status: WatchlistStatus
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime


# ── Scouting Note Schemas ──────────────────────────────────────────────────────

class ScoutingNoteCreateRequest(BaseModel):
    player_id: int
    category: ScoutingNoteCategory = ScoutingNoteCategory.GENERAL
    observation: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    author: Optional[str] = "Scout Analyst"


class ScoutingNoteResponse(BaseModel):
    id: int
    player_id: int
    player_name: str
    category: ScoutingNoteCategory
    observation: str
    confidence: float
    author: Optional[str] = None
    created_at: datetime
    updated_at: datetime
