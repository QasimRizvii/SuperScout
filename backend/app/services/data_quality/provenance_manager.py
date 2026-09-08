"""
Data Provenance Manager for SuperScout.

Tracks data lineage, source provenance, ingestion timestamp, verification status,
and batch metadata in DataProvenanceLog.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.models.provenance import DataProvenanceLog
from app.services.data_quality.schemas import ProvenanceRecordCreate


class ProvenanceManager:
    """
    Manages data lineage, provenance, and audit logs.
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def log_provenance(self, record: ProvenanceRecordCreate) -> DataProvenanceLog:
        """
        Creates and persists a new data provenance audit log record.
        """
        details = {
            "dataset_name": record.dataset_name,
            "records_failed": record.records_failed,
            "ingested_by": record.ingested_by,
            "is_verified": record.is_verified,
            "verification_method": record.verification_method,
            "notes": record.notes,
            **(record.meta_info or {})
        }

        db_log = DataProvenanceLog(
            batch_id=record.batch_id,
            source_name=record.source_name,
            source_type=record.source_type,
            source_url=None,
            dataset_version="1.0",
            records_processed=record.records_ingested,
            status="completed",
            details=details
        )
        self.db.add(db_log)
        self.db.commit()
        self.db.refresh(db_log)
        return db_log

    def get_provenance_logs(self, limit: int = 50, offset: int = 0) -> List[DataProvenanceLog]:
        """
        Retrieves recent provenance logs ordered by timestamp descending.
        """
        stmt = (
            select(DataProvenanceLog)
            .order_by(desc(DataProvenanceLog.imported_at))
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_provenance_by_batch(self, batch_id: str) -> List[DataProvenanceLog]:
        """
        Retrieves provenance logs for a specific batch ID.
        """
        stmt = (
            select(DataProvenanceLog)
            .where(DataProvenanceLog.batch_id == batch_id)
            .order_by(desc(DataProvenanceLog.imported_at))
        )
        return list(self.db.execute(stmt).scalars().all())
