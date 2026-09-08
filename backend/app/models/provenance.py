"""
SuperScout Backend — Data Provenance & Audit Log ORM Model

Model for tracking data import provenance, source origins, dataset versions, and batch ingestion history.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Integer, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DataProvenanceLog(Base):
    __tablename__ = "data_provenance_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    batch_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="csv")
    source_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dataset_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default="1.0")
    records_processed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="completed")
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<DataProvenanceLog(id={self.id}, batch_id='{self.batch_id}', source_name='{self.source_name}')>"
