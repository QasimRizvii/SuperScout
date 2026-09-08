"""
System Data Quality Engine for SuperScout.

Aggregates entity completeness, cross-entity consistency, statistical anomaly detection,
duplicate detection, and relationship integrity into a comprehensive System Data Quality Report.
"""

from typing import Dict, List, Any
from sqlalchemy.orm import Session

from app.services.data_quality.completeness import CompletenessChecker
from app.services.data_quality.consistency import ConsistencyChecker
from app.services.data_quality.anomaly_detector import AnomalyDetector
from app.services.data_quality.duplicate_detector import DuplicateDetector
from app.services.data_quality.relationship_integrity import RelationshipIntegrityEngine
from app.services.data_quality.schemas import (
    DataQualityReportResponse,
    CompletenessReport,
    ConsistencyIssue,
    AnomalyReport,
    DuplicateCandidate,
    IntegrityIssue
)


class DataQualityEngine:
    """
    Executes end-to-end data quality checks across the entire system database.
    """

    def __init__(self, db_session: Session):
        self.db = db_session
        self.completeness_checker = CompletenessChecker(db_session)
        self.consistency_checker = ConsistencyChecker(db_session)
        self.anomaly_detector = AnomalyDetector(db_session)
        self.duplicate_detector = DuplicateDetector(db_session)
        self.integrity_engine = RelationshipIntegrityEngine(db_session)

    def generate_full_report(self) -> DataQualityReportResponse:
        """
        Runs comprehensive data quality audits across all system entities.
        """
        # 1. Completeness Reports
        completeness_reports: List[CompletenessReport] = [
            self.completeness_checker.check_player_completeness(),
            self.completeness_checker.check_match_completeness(),
            self.completeness_checker.check_performance_completeness()
        ]
        avg_completeness = sum(c.completeness_percentage for c in completeness_reports) / max(1, len(completeness_reports))

        # 2. Consistency Issues
        consistency_issues: List[ConsistencyIssue] = self.consistency_checker.check_all_consistency()

        # 3. Anomalies
        anomalies: List[AnomalyReport] = self.anomaly_detector.detect_all_anomalies()

        # 4. Duplicates
        duplicate_candidates: List[DuplicateCandidate] = self.duplicate_detector.find_duplicate_players()

        # 5. Integrity Issues
        integrity_issues: List[IntegrityIssue] = self.integrity_engine.check_all_integrity()

        # Calculate Overall Health Index (0-100)
        # Deduct for consistency issues, anomalies, duplicates, integrity errors
        deduction = (
            (len(consistency_issues) * 2.0) +
            (len(anomalies) * 3.0) +
            (len(duplicate_candidates) * 5.0) +
            (len(integrity_issues) * 10.0)
        )
        overall_score = max(0.0, min(100.0, avg_completeness - deduction))
        overall_score = round(overall_score, 2)

        # Build summary metrics
        summary = {
            "overall_health_score": overall_score,
            "average_completeness_percentage": round(avg_completeness, 2),
            "total_consistency_issues": len(consistency_issues),
            "total_anomalies_detected": len(anomalies),
            "total_duplicate_candidates": len(duplicate_candidates),
            "total_integrity_issues": len(integrity_issues),
            "health_grade": "A" if overall_score >= 90 else "B" if overall_score >= 75 else "C" if overall_score >= 60 else "D"
        }

        # Recommendations
        recommendations: List[str] = []
        if duplicate_candidates:
            recommendations.append(f"Resolve {len(duplicate_candidates)} duplicate candidate player records")
        if integrity_issues:
            recommendations.append(f"Clean up {len(integrity_issues)} orphaned records violating foreign key constraints")
        if anomalies:
            recommendations.append(f"Investigate {len(anomalies)} statistical anomaly outliers in player performances")
        if avg_completeness < 90.0:
            recommendations.append("Enhance data ingestion pipelines to populate missing mandatory metadata fields")

        return DataQualityReportResponse(
            overall_score=overall_score,
            completeness=completeness_reports,
            consistency_issues=consistency_issues,
            anomalies=anomalies,
            duplicate_candidates=duplicate_candidates,
            integrity_issues=integrity_issues,
            summary=summary,
            recommendations=recommendations
        )
