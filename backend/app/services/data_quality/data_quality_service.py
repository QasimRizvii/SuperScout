"""
Unified Data Quality & Trust Service for SuperScout.

Provides an entrypoint for API routes and business logic callers.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.provenance import DataProvenanceLog
from app.services.data_quality.quality_engine import DataQualityEngine
from app.services.data_quality.trust_score_engine import TrustScoreEngine
from app.services.data_quality.duplicate_detector import DuplicateDetector
from app.services.data_quality.anomaly_detector import AnomalyDetector
from app.services.data_quality.provenance_manager import ProvenanceManager
from app.services.data_quality.schemas import (
    DataQualityReportResponse,
    PlayerTrustScoreResponse,
    DuplicateCandidate,
    AnomalyReport,
    ProvenanceRecordCreate,
    ProvenanceRecordResponse
)


class DataQualityService:
    """
    Unified service facade for data quality, trust scoring, duplicate merging detection,
    anomaly detection, and provenance tracking.
    """

    def __init__(self, db_session: Session):
        self.db = db_session
        self.quality_engine = DataQualityEngine(db_session)
        self.trust_engine = TrustScoreEngine(db_session)
        self.duplicate_detector = DuplicateDetector(db_session)
        self.anomaly_detector = AnomalyDetector(db_session)
        self.provenance_manager = ProvenanceManager(db_session)

    def get_full_quality_report(self) -> DataQualityReportResponse:
        """Returns full system-wide data quality audit report."""
        return self.quality_engine.generate_full_report()

    def get_player_trust_score(self, player_id: int) -> PlayerTrustScoreResponse:
        """Returns trust score and audit details for a specific player."""
        return self.trust_engine.calculate_player_trust_score(player_id)

    def detect_duplicates(self, name_threshold: float = 0.85) -> List[DuplicateCandidate]:
        """Runs duplicate detection for players."""
        return self.duplicate_detector.find_duplicate_players(name_similarity_threshold=name_threshold)

    def detect_anomalies(self) -> List[AnomalyReport]:
        """Runs anomaly detection for match performances."""
        return self.anomaly_detector.detect_all_anomalies()

    def log_provenance(self, record: ProvenanceRecordCreate) -> ProvenanceRecordResponse:
        """Logs a data provenance audit trail record."""
        db_log = self.provenance_manager.log_provenance(record)
        return self._convert_provenance_log(db_log)

    def get_provenance_logs(self, limit: int = 50, offset: int = 0) -> List[ProvenanceRecordResponse]:
        """Retrieves provenance logs."""
        logs = self.provenance_manager.get_provenance_logs(limit=limit, offset=offset)
        return [self._convert_provenance_log(log) for log in logs]

    @staticmethod
    def _convert_provenance_log(db_log: DataProvenanceLog) -> ProvenanceRecordResponse:
        details = db_log.details or {}
        return ProvenanceRecordResponse(
            id=db_log.id,
            source_name=db_log.source_name,
            source_type=db_log.source_type,
            dataset_name=details.get("dataset_name", "Unknown Dataset"),
            batch_id=db_log.batch_id,
            records_ingested=db_log.records_processed,
            records_failed=details.get("records_failed", 0),
            ingested_by=details.get("ingested_by", "system"),
            is_verified=details.get("is_verified", True),
            verification_method=details.get("verification_method", "checksum"),
            notes=details.get("notes"),
            meta_info=details,
            timestamp=db_log.imported_at
        )
