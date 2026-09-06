"""
SuperScout Ingestion Package Wrapper
"""
from app.services.ingestion.base import BaseIngestor, DataSource
from app.services.ingestion.pipeline import IngestionPipeline
from app.services.ingestion.loader import DatabaseLoader
from app.services.ingestion.schemas import IngestionReport, ImportResult, IngestionIssue, RecordStatus

__all__ = [
    "BaseIngestor",
    "DataSource",
    "IngestionPipeline",
    "DatabaseLoader",
    "IngestionReport",
    "ImportResult",
    "IngestionIssue",
    "RecordStatus",
]
