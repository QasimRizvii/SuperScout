"""
SuperScout Backend — Tactical Role Simulation Engine

Lightweight tactical usage evaluator assessing role suitability against empirical metrics.
"""
from typing import Dict, List, Optional, Any, Tuple
from app.models.player import Player
from app.services.analytics.schemas import PlayerAnalyticsOverviewResponse
from app.services.scouting.schemas import TacticalRoleFitResponse


class TacticalSimulatorEngine:
    """Evaluates player tactical role fit against specific match scenarios."""

    @staticmethod
    def evaluate_tactical_role(
        player: Player,
        analytics: PlayerAnalyticsOverviewResponse,
        evaluated_role: str,
    ) -> TacticalRoleFitResponse:
        
        req_clean = evaluated_role.strip().lower()
        score_obj = analytics.intelligence_score
        batting = analytics.batting
        bowling = analytics.bowling
        confidence = score_obj.confidence_factor if score_obj else 0.5

        runs = batting.runs if batting else 0
        bat_avg = (batting.batting_average.value or 0.0) if (batting and batting.batting_average) else 0.0
        sr = (batting.strike_rate.value or 0.0) if (batting and batting.strike_rate) else 0.0
        wickets = bowling.wickets if bowling else 0
        econ = (bowling.economy_rate.value or 99.0) if (bowling and bowling.economy_rate) else 99.0

        bat_phases = batting.phases.model_dump() if (batting and hasattr(batting, "phases")) else {}
        bowl_phases = bowling.phases.model_dump() if (bowling and hasattr(bowling, "phases")) else {}

        advantages: List[str] = []
        disadvantages: List[str] = []
        supporting_metrics: Dict[str, Any] = {}

        # 1. Opener
        if "opener" in req_clean or "opening" in req_clean:
            pp_bat = bat_phases.get("powerplay", {})
            pp_sr = pp_bat.get("strike_rate", sr)
            suitability = round(min(100.0, (bat_avg * 1.5 + (sr / 1.5)) * 0.5 + (score_obj.overall_score * 0.5 if score_obj else 0)), 1)
            supporting_metrics = {"batting_average": bat_avg, "overall_strike_rate": sr, "powerplay_strike_rate": pp_sr}
            if bat_avg >= 30.0:
                advantages.append(f"Proven top-order run producer (average {bat_avg:.1f}).")
            if sr >= 130.0:
                advantages.append(f"Fast powerplay starter ({sr:.1f} SR).")
            if bat_avg < 20.0:
                disadvantages.append("Low batting average increases top-order collapse risk.")
            if sr < 115.0:
                disadvantages.append("Slow scoring rate reduces powerplay efficiency.")

        # 2. Middle Order
        elif "middle" in req_clean:
            suitability = round(min(100.0, (bat_avg * 1.6 + sr * 0.4) * 0.5 + (score_obj.overall_score * 0.5 if score_obj else 0)), 1)
            supporting_metrics = {"batting_average": bat_avg, "strike_rate": sr, "total_runs": runs}
            if bat_avg >= 32.0:
                advantages.append(f"Strong middle-overs anchor ({bat_avg:.1f} average).")
            if sr >= 125.0:
                advantages.append("Good spin and pace rotation capability.")
            if sr < 110.0:
                disadvantages.append("Inability to accelerate when run rate required rises.")

        # 3. Finisher
        elif "finisher" in req_clean:
            death_bat = bat_phases.get("death_overs", {})
            death_sr = death_bat.get("strike_rate", sr)
            b_pct = batting.boundary_percentage.value if (batting and batting.boundary_percentage) else 0.0
            suitability = round(min(100.0, (sr * 0.5 + b_pct * 0.5) * 0.6 + (score_obj.impact_score * 0.4 if score_obj else 0)), 1)
            supporting_metrics = {"death_strike_rate": death_sr, "overall_strike_rate": sr, "boundary_pct": b_pct}
            if sr >= 140.0:
                advantages.append(f"Explosive strike rate ({sr:.1f}) in final overs.")
            if b_pct >= 60.0:
                advantages.append(f"High boundary production ({b_pct:.1f}% runs from boundaries).")
            if sr < 125.0:
                disadvantages.append("Lacks power hitting needed for death overs finishing.")

        # 4. Powerplay Bowler
        elif "powerplay" in req_clean:
            pp_bowl = bowl_phases.get("powerplay", {})
            pp_econ = pp_bowl.get("economy", econ)
            suitability = round(min(100.0, max(0.0, (10.0 - pp_econ)) * 10.0 * 0.5 + (score_obj.overall_score * 0.5 if score_obj else 0)), 1)
            supporting_metrics = {"powerplay_economy": pp_econ, "overall_economy": econ, "total_wickets": wickets}
            if pp_econ <= 7.5:
                advantages.append(f"Tight new-ball economy ({pp_econ:.2f}).")
            if wickets >= 5:
                advantages.append("Early wicket threat in opening 6 overs.")
            if pp_econ >= 9.0:
                disadvantages.append("High powerplay economy rate.")

        # 5. Death Bowler
        elif "death" in req_clean:
            death_bowl = bowl_phases.get("death_overs", {})
            death_econ = death_bowl.get("economy", econ)
            suitability = round(min(100.0, max(0.0, (12.0 - death_econ)) * 8.0 * 0.5 + (score_obj.overall_score * 0.5 if score_obj else 0)), 1)
            supporting_metrics = {"death_economy": death_econ, "overall_economy": econ, "wickets": wickets}
            if death_econ <= 8.5:
                advantages.append(f"Exceptional death overs execution ({death_econ:.2f} economy).")
            if death_econ >= 10.5:
                disadvantages.append("Concedes high run volume in closing overs.")

        # 6. All-rounder / Default
        else:
            player_role_str = str(player.role.value if hasattr(player.role, "value") else player.role).lower()
            is_ar = "all_rounder" in player_role_str or "all-rounder" in player_role_str
            base_score = 85.0 if is_ar else 55.0
            suitability = round(min(100.0, base_score * 0.5 + (score_obj.overall_score * 0.5 if score_obj else 0)), 1)
            supporting_metrics = {"batting_average": bat_avg, "strike_rate": sr, "wickets": wickets, "economy": econ}
            if is_ar:
                advantages.append("Dual capability balances team playing XI composition.")
            else:
                advantages.append("Specialist focus provides baseline role reliability.")

        if not advantages:
            advantages.append("Provides functional baseline performance for requested role.")
        if not disadvantages:
            disadvantages.append("No critical metric vulnerability detected in available match data.")

        return TacticalRoleFitResponse(
            player_id=player.id,
            player_name=player.name,
            evaluated_role=evaluated_role,
            suitability_score=suitability,
            supporting_metrics=supporting_metrics,
            advantages=advantages,
            disadvantages=disadvantages,
            confidence=round(confidence, 2),
        )
