"""
SuperScout Backend — Scouting Profile Engine

Builds evidence-based unified scouting profiles combining Step 4 analytics,
Step 6 auction intelligence, phase breakdowns, and tactical evaluations.
"""
from typing import Dict, List, Optional, Any
from app.models.player import Player
from app.services.analytics.schemas import PlayerAnalyticsOverviewResponse
from app.services.auction.schemas import PlayerValuationResponse
from app.services.scouting.schemas import (
    AuctionSummarySchema,
    IntelligenceSummarySchema,
    PerformanceSummarySchema,
    PlayerIdentitySchema,
    ScoutingAssessmentSchema,
    ScoutingProfileResponse,
)


class ScoutingProfileEngine:
    """Generates unified, explainable scouting profiles from analytics & auction intelligence."""

    @staticmethod
    def build_profile(
        player: Player,
        analytics: PlayerAnalyticsOverviewResponse,
        valuation: Optional[PlayerValuationResponse] = None,
        squad_fit_score: Optional[float] = None,
    ) -> ScoutingProfileResponse:
        
        # 1. Identity
        identity = PlayerIdentitySchema(
            player_id=player.id,
            name=player.name,
            short_name=player.short_name,
            nationality=player.nationality,
            age=None,  # calculated from date_of_birth if available
            role=str(player.role.value if hasattr(player.role, "value") else player.role),
            batting_style=player.batting_style,
            bowling_style=player.bowling_style,
            is_wicketkeeper=player.is_wicketkeeper,
            is_active=player.is_active,
        )

        # Calculate age if date_of_birth is available
        if player.date_of_birth:
            from datetime import date
            today = date.today()
            identity.age = today.year - player.date_of_birth.year - (
                (today.month, today.day) < (player.date_of_birth.month, player.date_of_birth.day)
            )

        # 2. Performance Summary
        batting = analytics.batting
        bowling = analytics.bowling
        consistency = analytics.consistency
        recent_form = analytics.recent_form

        perf_summary = PerformanceSummarySchema(
            runs=batting.runs if batting else 0,
            batting_average=batting.batting_average.value if (batting and batting.batting_average) else None,
            strike_rate=batting.strike_rate.value if (batting and batting.strike_rate) else None,
            highest_score=batting.highest_score if batting else 0,
            boundary_percentage=batting.boundary_percentage.value if (batting and batting.boundary_percentage) else None,
            dot_ball_percentage=batting.dot_ball_percentage.value if (batting and batting.dot_ball_percentage) else None,
            balls_per_boundary=batting.balls_per_boundary.value if (batting and batting.balls_per_boundary) else None,
            wickets=bowling.wickets if bowling else 0,
            economy=bowling.economy_rate.value if (bowling and bowling.economy_rate) else None,
            bowling_average=bowling.bowling_average.value if (bowling and bowling.bowling_average) else None,
            bowling_strike_rate=bowling.bowling_strike_rate.value if (bowling and bowling.bowling_strike_rate) else None,
            bowling_dot_ball_percentage=bowling.dot_ball_percentage.value if (bowling and bowling.dot_ball_percentage) else None,
            phase_performance={
                "batting_phases": batting.phases.model_dump() if (batting and hasattr(batting, "phases")) else {},
                "bowling_phases": bowling.phases.model_dump() if (bowling and hasattr(bowling, "phases")) else {},
            },
            recent_form_summary={
                "sample_size": recent_form.actual_sample_size if recent_form else 0,
                "recent_runs": recent_form.recent_batting.runs if (recent_form and recent_form.recent_batting) else 0,
                "recent_sr": recent_form.recent_batting.strike_rate.value if (recent_form and recent_form.recent_batting and recent_form.recent_batting.strike_rate) else None,
                "recent_wickets": recent_form.recent_bowling.wickets if (recent_form and recent_form.recent_bowling) else 0,
            },
            consistency_summary={
                "sample_size": consistency.sample_size if consistency else 0,
                "sample_confidence": consistency.sample_confidence if consistency else 0.0,
                "high_impact_pct": consistency.high_impact_performances_pct.value if (consistency and consistency.high_impact_performances_pct) else None,
                "low_score_pct": consistency.low_score_frequency_pct.value if (consistency and consistency.low_score_frequency_pct) else None,
            },
        )

        # 3. Intelligence Summary
        score = analytics.intelligence_score
        intel_summary = IntelligenceSummarySchema(
            intelligence_score=score.overall_score if score else 0.0,
            sample_confidence=score.confidence_factor if score else 0.0,
            recent_form_score=score.recent_form_score.score if score else 0.0,
            role_score=score.phase_impact_score.score if score else 0.0,
            consistency_score=score.consistency_score.score if score else 0.0,
            impact_score=score.phase_impact_score.score if score else 0.0,
        )

        # 4. Auction Summary
        if valuation:
            tier = "TIER_1" if valuation.estimated_fair_value >= 250.0 else ("TIER_2" if valuation.estimated_fair_value >= 100.0 else "TIER_3")
            auc_summary = AuctionSummarySchema(
                estimated_fair_value=valuation.estimated_fair_value,
                squad_fit_score=squad_fit_score,
                scarcity_score=60.0,
                recommended_bid_ceiling=valuation.recommended_max_bid,
                target_tier=tier,
                opportunity_cost_summary=None,
            )
        else:
            auc_summary = AuctionSummarySchema(
                estimated_fair_value=0.0,
                squad_fit_score=squad_fit_score,
                scarcity_score=0.0,
                recommended_bid_ceiling=0.0,
                target_tier="TIER_3",
            )

        # 5. Evidence-based Scouting Assessment
        assessment = ScoutingProfileEngine._generate_assessment(
            player, batting, bowling, consistency, recent_form, score, auc_summary
        )

        return ScoutingProfileResponse(
            identity=identity,
            performance=perf_summary,
            intelligence=intel_summary,
            auction=auc_summary,
            scouting=assessment,
        )

    @staticmethod
    def _generate_assessment(
        player: Player,
        batting: Any,
        bowling: Any,
        consistency: Any,
        recent_form: Any,
        score: Any,
        auction: AuctionSummarySchema,
    ) -> ScoutingAssessmentSchema:
        strengths: List[str] = []
        weaknesses: List[str] = []
        risk_indicators: List[str] = []
        dev_indicators: List[str] = []

        total_bat_innings = batting.innings if batting else 0
        total_bowl_innings = bowling.innings_bowled if bowling else 0

        # Sample check
        if total_bat_innings < 3 and total_bowl_innings < 3:
            return ScoutingAssessmentSchema(
                strengths=["Insufficient sample to identify key strengths."],
                weaknesses=["Insufficient sample to evaluate technical weaknesses."],
                ideal_role=str(player.role.value if hasattr(player.role, "value") else player.role),
                secondary_role=None,
                tactical_value="Limited sample available. Monitor match opportunities.",
                risk_indicators=["Insufficient sample size for statistical reliability."],
                development_indicators=["Build career match sample size."],
                recommended_usage="Insufficient sample.",
            )

        # Batting evaluation
        if batting and total_bat_innings >= 3:
            sr = batting.strike_rate.value if batting.strike_rate else 0.0
            avg = batting.batting_average.value if batting.batting_average else 0.0
            b_pct = batting.boundary_percentage.value if batting.boundary_percentage else 0.0
            dot_pct = batting.dot_ball_percentage.value if batting.dot_ball_percentage else 0.0

            if sr and sr >= 140.0:
                strengths.append(f"High strike rate batter ({sr:.1f}) with rapid scoring capability.")
            elif sr and sr < 115.0:
                weaknesses.append(f"Below-average strike rate ({sr:.1f}) in T20 format.")

            if avg and avg >= 35.0:
                strengths.append(f"Strong run-producing anchor with high batting average ({avg:.1f}).")
            elif avg and avg < 18.0:
                weaknesses.append(f"Low batting average ({avg:.1f}) indicates vulnerability.")

            if b_pct and b_pct >= 60.0:
                strengths.append(f"Exceptional boundary hitter ({b_pct:.1f}% runs from boundaries).")

            if dot_pct and dot_pct >= 45.0:
                weaknesses.append(f"High dot-ball frequency ({dot_pct:.1f}%), stalling innings momentum.")

        # Bowling evaluation
        if bowling and total_bowl_innings >= 3:
            econ = bowling.economy_rate.value if bowling.economy_rate else 0.0
            b_avg = bowling.bowling_average.value if bowling.bowling_average else 0.0
            b_sr = bowling.bowling_strike_rate.value if bowling.bowling_strike_rate else 0.0
            wickets = bowling.total_wickets

            if econ and econ <= 7.2:
                strengths.append(f"Economical bowling option with impressive economy rate ({econ:.2f}).")
            elif econ and econ >= 9.5:
                weaknesses.append(f"Expensive bowling option giving up {econ:.2f} runs per over.")

            if b_sr and b_sr <= 16.0:
                strengths.append(f"Genuine wicket-taking bowler (strike rate {b_sr:.1f} balls/wicket).")
            elif b_avg and b_avg >= 38.0:
                weaknesses.append(f"High bowling average ({b_avg:.1f}) per wicket.")

        # Consistency & Form evaluation
        if consistency and consistency.sample_size >= 3:
            cv = consistency.coefficient_of_variation.value if consistency.coefficient_of_variation else None
            high_impact = consistency.high_impact_performances_pct.value if consistency.high_impact_performances_pct else 0.0
            low_score = consistency.low_score_frequency_pct.value if consistency.low_score_frequency_pct else 0.0

            if high_impact and high_impact >= 35.0:
                strengths.append(f"Match winner: High impact performance in {high_impact:.1f}% of games.")
            if cv and cv > 0.8:
                risk_indicators.append(f"High scoring volatility (CV: {cv:.2f}).")
            if low_score and low_score >= 40.0:
                risk_indicators.append(f"Frequent low-scoring outputs in {low_score:.1f}% of innings.")

        if score and score.confidence_factor < 0.5:
            risk_indicators.append("Low sample confidence factor increases prediction risk.")

        # Role & Tactical Usage Determination
        player_role_str = str(player.role.value if hasattr(player.role, "value") else player.role).lower()

        if "wicketkeeper" in player_role_str or player.is_wicketkeeper:
            ideal_role = "Wicketkeeper-Batter"
            sec_role = "Middle-order Stabilizer"
            tactical_val = "Provides vital dual-skill wicketkeeping and batting depth."
            rec_usage = "Primary wicketkeeper and middle-order contributor."
        elif "all_rounder" in player_role_str or "all-rounder" in player_role_str:
            ideal_role = "Pinch-hitting All-Rounder"
            sec_role = "Secondary Bowling Option"
            tactical_val = "Balances squad composition by offering both bat and ball options."
            rec_usage = "Deploy in flexible order depending on match situations."
        elif "bowler" in player_role_str or total_bowl_innings > total_bat_innings:
            ideal_role = "Specialist Bowler"
            sec_role = "Tail-end Contributor"
            tactical_val = "Primary attack bowler responsible for key match phases."
            rec_usage = "Use in designated powerplay or death overs."
        else:
            ideal_role = "Top-Order Batter"
            sec_role = "Middle-Order Accumulator"
            tactical_val = "Specialist run scorer tasked with building match totals."
            rec_usage = "Deploy in top 4 batting slots to maximize impact."

        if not strengths:
            strengths.append("Steady squad player with balanced baseline metrics.")
        if not weaknesses:
            weaknesses.append("No critical statistical flaws observed in sample.")
        if not dev_indicators:
            dev_indicators.append("Refine match-phase execution and adaptability.")

        return ScoutingAssessmentSchema(
            strengths=strengths,
            weaknesses=weaknesses,
            ideal_role=ideal_role,
            secondary_role=sec_role,
            tactical_value=tactical_val,
            risk_indicators=risk_indicators,
            development_indicators=dev_indicators,
            recommended_usage=rec_usage,
        )
