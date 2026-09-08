"""
SuperScout Backend — Scouting Report Generator

Generates comprehensive, machine-readable JSON scouting reports with evidence-based verdicts.
"""
from typing import Dict, List, Optional, Any, Tuple
from app.models.player import Player
from app.services.analytics.schemas import PlayerAnalyticsOverviewResponse
from app.services.auction.schemas import PlayerValuationResponse
from app.services.scouting.schemas import (
    PlayerIdentitySchema,
    ScoutingReportResponse,
)
from app.services.scouting.scouting_profile import ScoutingProfileEngine


class ScoutingReportGenerator:
    """Generates structured scouting report with evidence-backed verdicts."""

    @staticmethod
    def generate_report(
        player: Player,
        analytics: PlayerAnalyticsOverviewResponse,
        valuation: Optional[PlayerValuationResponse] = None,
        squad_fit_score: Optional[float] = None,
    ) -> ScoutingReportResponse:
        
        # Build unified scouting profile first
        profile = ScoutingProfileEngine.build_profile(player, analytics, valuation, squad_fit_score)
        
        intel = analytics.intelligence_score
        batting = analytics.batting
        bowling = analytics.bowling
        consistency = analytics.consistency
        recent = analytics.recent_form
        confidence = intel.confidence_factor if intel else 0.5
        intel_score = intel.overall_score if intel else 0.0

        # Determine Verdict Category and Explanation
        verdict, explanation = ScoutingReportGenerator._determine_verdict(
            intel_score, confidence, squad_fit_score, profile.scouting.strengths, profile.scouting.risk_indicators
        )

        player_role_str = str(player.role.value if hasattr(player.role, "value") else player.role)

        summary = (
            f"Comprehensive scouting report for {player.name} ({player_role_str}). "
            f"Evaluated Intelligence Score: {intel_score:.1f}/100 with confidence factor {confidence:.2f}. "
            f"Scouting Verdict: {verdict}."
        )

        return ScoutingReportResponse(
            player=profile.identity,
            summary=summary,
            role_assessment={
                "ideal_role": profile.scouting.ideal_role,
                "secondary_role": profile.scouting.secondary_role,
                "tactical_value": profile.scouting.tactical_value,
                "role_score": intel.phase_impact_score.score if intel else 0.0,
            },
            batting_assessment={
                "runs": batting.runs if batting else 0,
                "batting_average": batting.batting_average.value if (batting and batting.batting_average) else None,
                "strike_rate": batting.strike_rate.value if (batting and batting.strike_rate) else None,
                "boundary_pct": batting.boundary_percentage.value if (batting and batting.boundary_percentage) else None,
            },
            bowling_assessment={
                "wickets": bowling.wickets if bowling else 0,
                "economy": bowling.economy_rate.value if (bowling and bowling.economy_rate) else None,
                "bowling_average": bowling.bowling_average.value if (bowling and bowling.bowling_average) else None,
                "bowling_strike_rate": bowling.bowling_strike_rate.value if (bowling and bowling.bowling_strike_rate) else None,
            },
            phase_assessment=profile.performance.phase_performance,
            recent_form=profile.performance.recent_form_summary,
            consistency=profile.performance.consistency_summary,
            squad_fit={
                "squad_fit_score": profile.auction.squad_fit_score,
            },
            auction_assessment={
                "estimated_fair_value": profile.auction.estimated_fair_value,
                "recommended_bid_ceiling": profile.auction.recommended_bid_ceiling,
                "scarcity_score": profile.auction.scarcity_score,
                "target_tier": profile.auction.target_tier,
            },
            strengths=profile.scouting.strengths,
            weaknesses=profile.scouting.weaknesses,
            risks=profile.scouting.risk_indicators,
            recommended_usage=[profile.scouting.recommended_usage],
            scouting_verdict=verdict,
            verdict_explanation=explanation,
            confidence=round(confidence, 2),
        )

    @staticmethod
    def _determine_verdict(
        score: float,
        confidence: float,
        squad_fit: Optional[float],
        strengths: List[str],
        risks: List[str],
    ) -> Tuple[str, str]:
        
        fit = squad_fit if squad_fit is not None else 70.0

        if confidence < 0.35:
            return (
                "DEVELOPMENT TARGET",
                f"Candidate exhibits insufficient match sample size (confidence {confidence:.2f}). Recommended for scouting monitoring and development tracking.",
            )

        if score >= 78.0 and fit >= 70.0 and confidence >= 0.6:
            return (
                "PRIORITY TARGET",
                f"High-impact elite target with Intelligence Score {score:.1f}/100 and strong squad fit ({fit:.1f}/100). High priority scouting candidate.",
            )

        if score >= 65.0 or (fit >= 80.0 and score >= 55.0):
            return (
                "STRONG TARGET",
                f"Solid performance profile (Intelligence Score {score:.1f}/100) with proven tactical utility for franchise composition.",
            )

        if score >= 50.0:
            return (
                "WATCHLIST",
                f"Moderate performance metrics (Intelligence Score {score:.1f}/100). Place on active watchlist for situation-dependent squad inclusion.",
            )

        if score >= 35.0:
            return (
                "LOW PRIORITY",
                f"Below-average performance quality (Intelligence Score {score:.1f}/100). Secondary squad depth option.",
            )

        return (
            "AVOID",
            f"Low performance intelligence score ({score:.1f}/100) and elevated selection risk. Recruitment not recommended.",
        )
