"""
SuperScout Backend — Data Ingestion Pipeline Schemas
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class IngestionError(BaseModel):
    record_identifier: str
    error_message: str
    raw_data: Optional[Dict[str, Any]] = None


class IngestionReport(BaseModel):
    ingestor_name: str
    status: str = "success"
    total_records: int = 0
    records_loaded: int = 0
    records_validated: int = 0
    records_inserted: int = 0
    duplicates_skipped: int = 0
    errors: List[IngestionError] = Field(default_factory=list)
