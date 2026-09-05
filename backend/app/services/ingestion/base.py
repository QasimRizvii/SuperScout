"""
SuperScout Backend — Abstract Data Ingestor Interface

Defines the standard 5-stage ingestion pipeline for all future cricket datasets:
1. Load Raw Data
2. Validate Records
3. Normalize Fields
4. Detect Duplicates
5. Ingest to Database
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Optional
from sqlalchemy.orm import Session

from app.services.ingestion.schemas import IngestionReport, IngestionError


class BaseIngestor(ABC):
    """
    Abstract base class for all cricket data ingestors.

    Ensures consistent pipeline execution, error isolation, and prevention of database corruption.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def load_raw(self, source_path_or_data: Any) -> List[Dict[str, Any]]:
        """Stage 1: Load raw data records from source."""
        pass

    @abstractmethod
    def validate_record(self, record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Stage 2: Validate individual raw record fields."""
        pass

    @abstractmethod
    def normalize_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 3: Normalize field types, names, and formats."""
        pass

    @abstractmethod
    def is_duplicate(self, db: Session, record: Dict[str, Any]) -> bool:
        """Stage 4: Check if record already exists in database."""
        pass

    @abstractmethod
    def save_record(self, db: Session, record: Dict[str, Any]) -> Any:
        """Stage 5: Persist validated & normalized record into database."""
        pass

    def run(self, db: Session, source_input: Any) -> IngestionReport:
        """
        Execute full pipeline securely with transaction management.
        """
        report = IngestionReport(ingestor_name=self.name)

        try:
            raw_records = self.load_raw(source_input)
            report.total_records = len(raw_records)
            report.records_loaded = len(raw_records)
        except Exception as e:
            report.status = "failed"
            report.errors.append(
                IngestionError(record_identifier="FILE_LOAD", error_message=str(e))
            )
            return report

        for idx, raw_record in enumerate(raw_records):
            record_id = raw_record.get("id") or f"row_{idx}"

            # Step 2: Validate
            try:
                is_valid, err_msg = self.validate_record(raw_record)
                if not is_valid:
                    report.errors.append(
                        IngestionError(
                            record_identifier=str(record_id),
                            error_message=err_msg or "Validation failed",
                            raw_data=raw_record,
                        )
                    )
                    continue
                report.records_validated += 1
            except Exception as e:
                report.errors.append(
                    IngestionError(
                        record_identifier=str(record_id),
                        error_message=f"Validation exception: {str(e)}",
                        raw_data=raw_record,
                    )
                )
                continue

            # Step 3: Normalize
            try:
                normalized = self.normalize_record(raw_record)
            except Exception as e:
                report.errors.append(
                    IngestionError(
                        record_identifier=str(record_id),
                        error_message=f"Normalization exception: {str(e)}",
                        raw_data=raw_record,
                    )
                )
                continue

            # Step 4: Duplicate Check
            try:
                if self.is_duplicate(db, normalized):
                    report.duplicates_skipped += 1
                    continue
            except Exception as e:
                report.errors.append(
                    IngestionError(
                        record_identifier=str(record_id),
                        error_message=f"Duplicate check exception: {str(e)}",
                        raw_data=raw_record,
                    )
                )
                continue

            # Step 5: Save Record
            try:
                self.save_record(db, normalized)
                report.records_inserted += 1
            except Exception as e:
                db.rollback()
                report.errors.append(
                    IngestionError(
                        record_identifier=str(record_id),
                        error_message=f"Save exception: {str(e)}",
                        raw_data=raw_record,
                    )
                )

        if report.errors:
            report.status = "completed_with_errors" if report.records_inserted > 0 else "failed"

        return report
