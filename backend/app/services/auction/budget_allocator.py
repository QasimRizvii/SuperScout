"""
SuperScout Backend — Purse Budget Allocator Module

Dynamically allocates remaining franchise auction purse across squad categories based on identified role gaps.
"""
from typing import List
from app.services.auction.schemas import (
    BudgetAllocationBreakdown,
    PurseBudgetAllocationResponse,
)
from app.services.squad.schemas import RoleGapRecommendation


class PurseBudgetAllocator:
    """Engine for recommending dynamic purse allocation strategy."""

    @classmethod
    def allocate_purse(
        cls,
        auction_id: int,
        team_id: int,
        team_name: str,
        total_purse: float,
        remaining_purse: float,
        remaining_squad_slots: int,
        gaps: List[RoleGapRecommendation],
    ) -> PurseBudgetAllocationResponse:

        rem_p = max(0.0, remaining_purse)

        # Baseline percentage splits
        p_bat = 0.25
        p_bowl = 0.30
        p_ar = 0.20
        p_wk = 0.15
        p_res = 0.10

        # Adjust percentages based on gap priorities
        has_wk_gap = any("Wicketkeep" in g.gap_title for g in gaps)
        has_bowl_gap = any("Bowling" in g.gap_title for g in gaps)
        has_ar_gap = any("All-Rounder" in g.gap_title for g in gaps)

        if has_wk_gap:
            p_wk += 0.10
            p_bat -= 0.05
            p_ar -= 0.05

        if has_bowl_gap:
            p_bowl += 0.10
            p_bat -= 0.05
            p_res -= 0.05

        if has_ar_gap:
            p_ar += 0.05
            p_bat -= 0.05

        # Normalize percentages
        total_pct = p_bat + p_bowl + p_ar + p_wk + p_res
        p_bat /= total_pct
        p_bowl /= total_pct
        p_ar /= total_pct
        p_wk /= total_pct
        p_res /= total_pct

        breakdown = BudgetAllocationBreakdown(
            batting_budget=round(rem_p * p_bat, 1),
            bowling_budget=round(rem_p * p_bowl, 1),
            all_rounder_budget=round(rem_p * p_ar, 1),
            wicketkeeper_budget=round(rem_p * p_wk, 1),
            reserve_budget=round(rem_p * p_res, 1),
        )

        rationale = (
            f"Purse strategy for {team_name}: ₹{rem_p:.1f}L remaining across {remaining_squad_slots} slots. "
            f"Allocating largest shares to Bowling (₹{breakdown.bowling_budget}L) and "
            f"Batting (₹{breakdown.batting_budget}L) based on {len(gaps)} identified squad gap(s)."
        )

        return PurseBudgetAllocationResponse(
            auction_id=auction_id,
            team_id=team_id,
            team_name=team_name,
            total_purse=total_purse,
            remaining_purse=rem_p,
            remaining_squad_slots=remaining_squad_slots,
            allocation=breakdown,
            allocation_rationale=rationale,
        )
