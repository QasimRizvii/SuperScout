"""
SuperScout Backend — Role-Specific Target Engine

Evaluates candidates for specific tactical cricket roles using granular role metrics.
"""
from typing import Dict, List, Optional, Any, Tuple
from app.models.player import Player
from app.services.analytics.schemas import PlayerAnalyticsOverviewResponse
from app.services.auction.valuation_engine import ValuationEngine
from app.services.scouting.schemas import (
    RoleTargetItem,
    RoleTargetResponse,
)


class RoleTargetEngine:
    """Evaluates candidates against 11 granular cricket roles using specific performance metrics."""

    @staticmethod
    def evaluate_role_targets(
        requested_role: str,
        candidates: List[Player],
        analytics_map: Dict[int, PlayerAnalyticsOverviewResponse],
        squad_fit_map: Optional[Dict[int, float]] = None,
    ) -> RoleTargetResponse:
        
        req_clean = requested_role.strip().lower()
        items: List[RoleTargetItem] = []

        for p in candidates:
            analytics = analytics_map.get(p.id)
            if not analytics:
                continue

            score_obj = analytics.intelligence_score
            batting = analytics.batting
            bowling = analytics.bowling
            sample_confidence = score_obj.confidence_factor if score_obj else 0.5
            player_role_str = str(p.role.value if hasattr(p.role, "value") else p.role)

            suitability_score, rel_stats, reason, risk = RoleTargetEngine._evaluate_specific_role(
                req_clean, p, batting, bowling, score_obj
            )

            if suitability_score <= 30.0:
                continue

            fit_val = squad_fit_map.get(p.id, 70.0) if squad_fit_map else None
            val_eval = ValuationEngine.calculate_valuation(p, base_price=20.0, analytics=analytics, fit_score=None)

            items.append(
                RoleTargetItem(
                    player_id=p.id,
                    player_name=p.name,
                    primary_role=player_role_str,
                    suitability_score=round(suitability_score, 1),
                    relevant_statistics=rel_stats,
                    squad_fit=fit_val,
                    scarcity_score=60.0,
                    estimated_value=val_eval.estimated_fair_value,
                    recommendation_reason=reason,
                    risk=risk,
                )
            )

        items.sort(key=lambda x: x.suitability_score, reverse=True)

        return RoleTargetResponse(
            requested_role=requested_role,
            total_candidates=len(items),
            candidates=items,
        )

    @staticmethod
    def _evaluate_specific_role(
        role_req: str,
        player: Player,
        batting: Any,
        bowling: Any,
        score_obj: Any,
    ) -> Tuple[float, Dict[str, Any], str, str]:
        
        runs = batting.runs if batting else 0
        bat_avg = (batting.batting_average.value or 0.0) if (batting and batting.batting_average) else 0.0
        sr = (batting.strike_rate.value or 0.0) if (batting and batting.strike_rate) else 0.0
        wickets = bowling.wickets if bowling else 0
        econ = (bowling.economy_rate.value or 99.0) if (bowling and bowling.economy_rate) else 99.0
        bowl_sr = (bowling.bowling_strike_rate.value or 99.0) if (bowling and bowling.bowling_strike_rate) else 99.0
        
        player_role = str(player.role.value if hasattr(player.role, "value") else player.role).lower()

        # Phase details
        bat_phases = batting.phases.model_dump() if (batting and hasattr(batting, "phases")) else {}
        bowl_phases = bowling.phases.model_dump() if (bowling and hasattr(bowling, "phases")) else {}

        # 1. Opening Batter
        if "opening" in role_req or "opener" in role_req:
            pp_bat = bat_phases.get("powerplay", {})
            pp_runs = pp_bat.get("runs", 0)
            pp_sr = pp_bat.get("strike_rate", sr)
            score = (bat_avg * 1.2 + (sr / 1.5)) * 0.5 + (score_obj.overall_score * 0.5 if score_obj else 0)
            stats = {"batting_average": bat_avg, "strike_rate": sr, "powerplay_runs": pp_runs, "powerplay_sr": pp_sr}
            reason = f"Top-order scoring capability with {bat_avg:.1f} average and {sr:.1f} strike rate."
            risk = "Susceptible to swing in early powerplay overs." if (sr < 120 and bat_avg < 25) else "Standard top-order risk."
            return score, stats, reason, risk

        # 2. Middle-Order Batter
        elif "middle" in role_req:
            mid_bat = bat_phases.get("middle_overs", {})
            score = (bat_avg * 1.5 + sr * 0.5) * 0.5 + (score_obj.overall_score * 0.5 if score_obj else 0)
            stats = {"batting_average": bat_avg, "strike_rate": sr, "total_runs": runs}
            reason = f"Middle-overs accumulator with reliable {bat_avg:.1f} average."
            risk = "Struggle against spin in middle overs." if sr < 115 else "Low middle-order risk."
            return score, stats, reason, risk

        # 3. Finisher
        elif "finisher" in role_req or "death_batter" in role_req:
            death_bat = bat_phases.get("death_overs", {})
            death_sr = death_bat.get("strike_rate", sr)
            b_pct = batting.boundary_percentage.value if (batting and batting.boundary_percentage) else 0.0
            score = (sr * 0.5 + b_pct * 0.5) * 0.6 + (score_obj.impact_score * 0.4 if score_obj else 0)
            stats = {"strike_rate": sr, "boundary_percentage": b_pct, "death_sr": death_sr}
            reason = f"Explosive death-overs hitter with {sr:.1f} strike rate and {b_pct:.1f}% boundary rate."
            risk = "High early-wicket vulnerability when pushing run rate immediately."
            return score, stats, reason, risk

        # 4. Wicketkeeper
        elif "keeper" in role_req or "wicketkeeper" in role_req:
            is_wk = player.is_wicketkeeper or "wicketkeeper" in player_role
            base = 90.0 if is_wk else 20.0
            score = base * 0.5 + (score_obj.overall_score * 0.5 if score_obj else 0)
            stats = {"is_wicketkeeper": is_wk, "batting_average": bat_avg, "strike_rate": sr}
            reason = f"Specialist wicketkeeper option with primary role fit."
            risk = "Secondary skill dependency if batting form drops."
            return score, stats, reason, risk

        # 5. Death Bowler
        elif "death_bowler" in role_req or "death" in role_req:
            death_bowl = bowl_phases.get("death_overs", {})
            death_econ = death_bowl.get("economy", econ)
            score = (max(0, (12.0 - death_econ)) * 8.0 + wickets * 2.0) * 0.5 + (score_obj.overall_score * 0.5 if score_obj else 0)
            stats = {"death_economy": death_econ, "overall_economy": econ, "total_wickets": wickets}
            reason = f"Death overs execution bowler maintaining {death_econ:.2f} economy under pressure."
            risk = "Full-toss or boundary leakage risk in final 4 overs."
            return score, stats, reason, risk

        # 6. Powerplay Bowler
        elif "powerplay" in role_req:
            pp_bowl = bowl_phases.get("powerplay", {})
            pp_econ = pp_bowl.get("economy", econ)
            score = (max(0, (10.0 - pp_econ)) * 10.0) * 0.5 + (score_obj.overall_score * 0.5 if score_obj else 0)
            stats = {"powerplay_economy": pp_econ, "overall_economy": econ, "wickets": wickets}
            reason = f"Powerplay new-ball specialist restricting scoring to {pp_econ:.2f} economy."
            risk = "Vulnerable if new ball does not swing."
            return score, stats, reason, risk

        # 7. Pace Bowler / Fast Bowler
        elif "pace" in role_req or "fast" in role_req:
            is_fast = "fast" in player_role or "medium" in player_role or "bowler" in player_role
            base = 80.0 if is_fast else 40.0
            score = base * 0.4 + (max(0, (12.0 - econ)) * 4.0 + wickets * 1.5) * 0.6
            stats = {"wickets": wickets, "economy": econ, "bowling_sr": bowl_sr}
            reason = f"Frontline pace bowling candidate with {wickets} wickets and {econ:.2f} economy."
            risk = "Injury risk associated with fast bowling workload."
            return score, stats, reason, risk

        # 8. Spin Bowler
        elif "spin" in role_req:
            is_spin = "spin" in player_role or "spinner" in player_role
            base = 85.0 if is_spin else 30.0
            score = base * 0.4 + (max(0, (10.0 - econ)) * 5.0 + wickets * 1.5) * 0.6
            stats = {"wickets": wickets, "economy": econ, "bowling_sr": bowl_sr}
            reason = f"Specialist spin bowler maintaining {econ:.2f} economy rate."
            risk = "Vulnerable on flat pitches with minimal turn."
            return score, stats, reason, risk

        # 9. All-Rounder / Batting All-Rounder / Bowling All-Rounder
        else:
            is_ar = "all_rounder" in player_role or "all-rounder" in player_role
            ar_bonus = 85.0 if is_ar else 50.0
            score = ar_bonus * 0.4 + (bat_avg * 0.8 + (10.0 - min(econ, 10.0)) * 5.0) * 0.6
            stats = {"batting_average": bat_avg, "strike_rate": sr, "wickets": wickets, "economy": econ}
            reason = f"Dual-skill all-rounder offering {bat_avg:.1f} batting avg and {wickets} wickets."
            risk = "Over-reliance on one primary discipline."
            return score, stats, reason, risk
