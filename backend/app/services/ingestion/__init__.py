"""
SuperScout Backend — Data Ingestion Package
"""
from app.services.ingestion.base import BaseIngestor
from app.services.ingestion.schemas import IngestionReport, IngestionError
from app.services.ingestion.sample_ingestor import PlayerIngestor

__all__ = [
    "BaseIngestor",
    "IngestionReport",
    "IngestionError",
    "PlayerIngestor",
]
