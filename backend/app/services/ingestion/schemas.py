"""
SuperScout Backend — Data Ingestion Pipeline Schemas & Report Models
"""
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class RecordStatus(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    SKIPPED = "skipped"
    DUPLICATE = "duplicate"
    UNRESOLVED = "unresolved"
    INVALID = "invalid"


class IngestionIssue(BaseModel):
    record_identifier: str
    issue_type: RecordStatus
    message: str
    raw_data: Optional[Dict[str, Any]] = None


# Aliases for backward compatibility
IngestionError = IngestionIssue


class IngestionReport(BaseModel):
    ingestor_name: str
    source_name: str = "unknown"
    status: str = "success"  # success, completed_with_errors, failed
    is_dry_run: bool = False
    duration_seconds: float = 0.0
    total_records: int = 0
    records_loaded: int = 0
    records_validated: int = 0
    records_inserted: int = 0
    records_updated: int = 0
    duplicates_skipped: int = 0
    records_unresolved: int = 0
    records_invalid: int = 0
    issues: List[IngestionIssue] = Field(default_factory=list)

    def add_issue(
        self,
        identifier: str,
        issue_type: RecordStatus,
        message: str,
        raw_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Helper to append an issue record and update state counters."""
        self.issues.append(
            IngestionIssue(
                record_identifier=identifier,
                issue_type=issue_type,
                message=message,
                raw_data=raw_data,
            )
        )
        if issue_type == RecordStatus.DUPLICATE:
            self.duplicates_skipped += 1
        elif issue_type == RecordStatus.UNRESOLVED:
            self.records_unresolved += 1
        elif issue_type == RecordStatus.INVALID:
            self.records_invalid += 1

    def format_cli_summary(self) -> str:
        """Format report stats into a human-readable CLI summary table."""
        mode_str = " [DRY RUN]" if self.is_dry_run else ""
        lines = [
            f"\nSuperScout Cricket Import{mode_str}",
            "-------------------------",
            f"Ingestor:           {self.ingestor_name}",
            f"Source:             {self.source_name}",
            f"Duration:           {self.duration_seconds:.3f}s",
            "",
            f"Records read:        {self.records_loaded}",
            f"Created:             {self.records_inserted}",
            f"Updated:             {self.records_updated}",
            f"Duplicates:          {self.duplicates_skipped}",
            f"Skipped:             {self.records_loaded - self.records_inserted - self.records_updated}",
            f"Invalid:             {self.records_invalid}",
            f"Unresolved:          {self.records_unresolved}",
            "",
            f"Status: {self.status.upper()}",
        ]
        if self.issues:
            lines.append(f"Issues count: {len(self.issues)}")
            sample_errors = [i for i in self.issues if i.issue_type in (RecordStatus.INVALID, RecordStatus.UNRESOLVED)][:3]
            for err in sample_errors:
                lines.append(f"  - [{err.issue_type.value.upper()}] ID '{err.record_identifier}': {err.message}")
        return "\n".join(lines)


ImportResult = IngestionReport
