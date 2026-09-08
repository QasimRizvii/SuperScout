"""
Player Trust Score Engine for SuperScout.

Evaluates data quality, completeness, consistency, sample size, and recency
for an individual player to produce an explainable Trust Score (0.0 to 100.0).
"""

from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc

from app.models.player import Player
from app.models.batting import BattingPerformance
from app.models.bowling import BowlingPerformance
from app.services.data_quality.completeness import CompletenessChecker
from app.services.data_quality.consistency import ConsistencyChecker
from app.services.data_quality.schemas import PlayerTrustScoreResponse


class TrustScoreEngine:
    """
    Calculates explainable data trust scores for players.
    """

    def __init__(self, db_session: Session):
        self.db = db_session
        self.completeness_checker = CompletenessChecker(db_session)
        self.consistency_checker = ConsistencyChecker(db_session)

    def calculate_player_trust_score(self, player_id: int) -> PlayerTrustScoreResponse:
        """
        Calculates a 0-100 Trust Score for a player with full breakdown of deductions and additions.
        """
        player = self.db.execute(
            select(Player).where(Player.id == player_id)
        ).scalar_one_or_none()

        if not player:
            return PlayerTrustScoreResponse(
                player_id=player_id,
                player_name="Unknown Player",
                trust_score=0.0,
                confidence_rating="UNTRUSTY",
                completeness_score=0.0,
                consistency_score=0.0,
                sample_size_confidence=0.0,
                recency_score=0.0,
                deductions=["Player record not found in database"],
                recommendations=["Verify player ID and re-import player data"],
                explainability_notes={"error": "Player not found"}
            )

        # 1. Completeness Score (Weight: 30%)
        comp_report = self.completeness_checker.check_player_completeness(player_id)
        completeness_score = comp_report.completeness_percentage

        # 2. Consistency Score (Weight: 30%)
        cons_issues = self.consistency_checker.check_player_performance_consistency(player_id)
        high_severity_count = sum(1 for i in cons_issues if i.severity == "HIGH")
        medium_severity_count = sum(1 for i in cons_issues if i.severity == "MEDIUM")
        
        consistency_score = max(0.0, 100.0 - (high_severity_count * 25.0 + medium_severity_count * 10.0))

        # 3. Sample Size Confidence (Weight: 25%)
        bat_count = self.db.execute(
            select(func.count(BattingPerformance.id)).where(BattingPerformance.player_id == player_id)
        ).scalar() or 0

        bowl_count = self.db.execute(
            select(func.count(BowlingPerformance.id)).where(BowlingPerformance.player_id == player_id)
        ).scalar() or 0

        perf_count = bat_count + bowl_count

        # Sample size benchmark: 20 matches = 100% confidence, scale linearly up to 20
        sample_size_confidence = min(100.0, (perf_count / 20.0) * 100.0)

        # 4. Recency Score (Weight: 15%)
        recency_score = 100.0 if perf_count > 0 else 0.0

        # Weighted Total
        raw_trust_score = (
            (completeness_score * 0.30) +
            (consistency_score * 0.30) +
            (sample_size_confidence * 0.25) +
            (recency_score * 0.15)
        )
        trust_score = round(raw_trust_score, 2)

        # Build deductions & recommendations
        deductions: List[str] = []
        recommendations: List[str] = []

        if completeness_score < 80.0:
            deductions.append(f"Incomplete profile metadata ({completeness_score:.1f}% completeness)")
            recommendations.append("Populate missing player bio fields (batting style, bowling style, DOB)")

        if cons_issues:
            deductions.append(f"Found {len(cons_issues)} statistical consistency flags")
            recommendations.append("Audit player match performances for contradictory stats")

        if perf_count < 5:
            deductions.append(f"Small match sample size ({perf_count} matches available)")
            recommendations.append("Ingest more historic match data for accurate scouting analysis")

        if trust_score >= 85.0:
            confidence_rating = "HIGH"
        elif trust_score >= 60.0:
            confidence_rating = "MEDIUM"
        elif trust_score >= 40.0:
            confidence_rating = "LOW"
        else:
            confidence_rating = "UNTRUSTY"

        explainability = {
            "completeness_weight": "30%",
            "consistency_weight": "30%",
            "sample_size_weight": "25%",
            "recency_weight": "15%",
            "total_matches_analyzed": perf_count,
            "consistency_flags_count": len(cons_issues),
            "missing_fields": comp_report.missing_fields
        }

        return PlayerTrustScoreResponse(
            player_id=player.id,
            player_name=player.name,
            trust_score=trust_score,
            confidence_rating=confidence_rating,
            completeness_score=round(completeness_score, 2),
            consistency_score=round(consistency_score, 2),
            sample_size_confidence=round(sample_size_confidence, 2),
            recency_score=round(recency_score, 2),
            deductions=deductions,
            recommendations=recommendations,
            explainability_notes=explainability
        )
