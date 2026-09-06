"""
SuperScout Backend — Auction Intelligence Pydantic Response Schemas
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.models.enums import PlayerRole


class PlayerValuationResponse(BaseModel):
    """Detailed statistical fair value and recommended maximum bid ceiling."""

    player_id: int
    player_name: str
    role: PlayerRole
    intelligence_score: float = 0.0
    base_price: float = 0.0  # In INR Lakhs
    estimated_fair_value: float = 0.0  # In INR Lakhs
    recommended_max_bid: float = 0.0  # In INR Lakhs
    confidence: str = "MEDIUM"  # HIGH, MEDIUM, LOW
    sample_size: int = 0
    explanation: str = ""


class SquadFitScore(BaseModel):
    """Evaluation of how well a player fits a specific franchise squad."""

    player_quality_score: float = 0.0  # 0 to 100
    squad_fit_score: float = 0.0  # 0 to 100
    gap_severity: str = "MEDIUM"  # CRITICAL, HIGH, MEDIUM, LOW, OVERSTOCKED
    role_scarcity_level: str = "MEDIUM"  # HIGH, MEDIUM, LOW
    expected_contribution_rating: str = "STARTER"  # STARTER, ROTATION, BENCH
    overall_priority: str = "TIER_2"  # TIER_1, TIER_2, TIER_3, AVOID


class AuctionTargetItem(BaseModel):
    """Ranked target entry for a franchise in an auction."""

    rank: int
    player_id: int
    player_name: str
    role: PlayerRole
    intelligence_score: float = 0.0
    squad_fit_score: float = 0.0
    role_scarcity: str = "MEDIUM"
    base_price: float = 0.0
    estimated_fair_value: float = 0.0
    recommended_max_bid: float = 0.0
    priority: str = "TIER_2"
    confidence: str = "MEDIUM"
    fit_explanation: str = ""


class AuctionTargetRankingResponse(BaseModel):
    """Ranked auction target report for a franchise."""

    auction_id: int
    team_id: int
    team_name: str
    remaining_purse: float = 0.0  # In INR Lakhs
    total_targets_ranked: int = 0
    targets: List[AuctionTargetItem] = Field(default_factory=list)
    tactical_summary: str = ""


class BudgetAllocationBreakdown(BaseModel):
    """Purse allocation breakdown across squad categories."""

    batting_budget: float = 0.0
    bowling_budget: float = 0.0
    all_rounder_budget: float = 0.0
    wicketkeeper_budget: float = 0.0
    reserve_budget: float = 0.0


class PurseBudgetAllocationResponse(BaseModel):
    """Dynamic purse allocation strategy for a franchise."""

    auction_id: int
    team_id: int
    team_name: str
    total_purse: float = 0.0
    remaining_purse: float = 0.0
    remaining_squad_slots: int = 0
    allocation: BudgetAllocationBreakdown = Field(default_factory=BudgetAllocationBreakdown)
    allocation_rationale: str = ""


class AlternativeTarget(BaseModel):
    """Fallback player target if primary target exceeds bid ceiling."""

    player_id: int
    player_name: str
    role: PlayerRole
    intelligence_score: float = 0.0
    base_price: float = 0.0
    estimated_fair_value: float = 0.0
    recommended_max_bid: float = 0.0
    transition_rationale: str = ""


class AlternativeTargetResponse(BaseModel):
    """Fallback tree for a primary auction target."""

    primary_player_id: int
    primary_player_name: str
    primary_max_bid: float = 0.0
    alternatives: List[AlternativeTarget] = Field(default_factory=list)
    recommendation: str = ""


class OpportunityCostResponse(BaseModel):
    """Evaluation of trade-offs when placing a high bid."""

    player_id: int
    player_name: str
    proposed_bid: float = 0.0
    cost_level: str = "LOW"  # HIGH, MEDIUM, LOW
    sacrificed_roles: List[str] = Field(default_factory=list)
    explanation: str = ""


class AuctionScenarioRequest(BaseModel):
    """Request model for simulating an auction event."""

    team_id: int
    target_player_id: int
    bid_price: float = 0.0
    outcome: str = "purchased"  # purchased, outbid, surged


class AuctionScenarioResponse(BaseModel):
    """What-If auction scenario simulation report."""

    auction_id: int
    team_id: int
    team_name: str
    target_player_id: int
    target_player_name: str
    bid_price: float = 0.0
    outcome: str = "purchased"
    updated_remaining_purse: float = 0.0
    squad_balance_before: float = 0.0
    squad_balance_after: float = 0.0
    score_delta: float = 0.0
    remaining_gaps: List[str] = Field(default_factory=list)
    next_recommended_targets: List[str] = Field(default_factory=list)
    scenario_summary: str = ""


class ComparablePlayerItem(BaseModel):
    """Statistically & strategically similar player benchmark."""

    player_id: int
    player_name: str
    role: PlayerRole
    intelligence_score: float = 0.0
    historical_final_price: Optional[float] = None
    similarity_score: float = 0.0
    key_matching_reason: str = ""


class ComparablePlayerResponse(BaseModel):
    """Comparable player price benchmark report."""

    target_player_id: int
    target_player_name: str
    role: PlayerRole
    intelligence_score: float = 0.0
    comparables: List[ComparablePlayerItem] = Field(default_factory=list)
    average_price_benchmark: float = 0.0
    valuation_guidance: str = ""
