"""
Data Quality, Trust & Provenance API Endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.data_quality.data_quality_service import DataQualityService
from app.services.data_quality.schemas import (
    DataQualityReportResponse,
    PlayerTrustScoreResponse,
    DuplicateCandidate,
    AnomalyReport,
    ProvenanceRecordCreate,
    ProvenanceRecordResponse
)

router = APIRouter(prefix="/data-quality", tags=["Data Quality & Trust"])


@router.get("/report", response_model=DataQualityReportResponse)
def get_system_data_quality_report(db: Session = Depends(get_db)):
    """
    Retrieves complete system-wide data quality audit report.
    Includes completeness, consistency, anomalies, duplicate candidates, and relationship integrity.
    """
    service = DataQualityService(db)
    return service.get_full_quality_report()


@router.get("/trust-score/{player_id}", response_model=PlayerTrustScoreResponse)
def get_player_trust_score(player_id: int, db: Session = Depends(get_db)):
    """
    Computes and returns explainable Trust Score (0.0 - 100.0) for a specified player.
    """
    service = DataQualityService(db)
    score_res = service.get_player_trust_score(player_id)
    if any("Player record not found" in d for d in score_res.deductions):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with ID {player_id} not found."
        )
    return score_res


@router.get("/duplicates", response_model=List[DuplicateCandidate])
def get_duplicate_candidates(
    threshold: float = Query(0.85, ge=0.5, le=1.0, description="Similarity threshold for fuzzy matching"),
    db: Session = Depends(get_db)
):
    """
    Detects potential duplicate player records based on fuzzy name matching, country, and DOB.
    """
    service = DataQualityService(db)
    return service.detect_duplicates(name_threshold=threshold)


@router.get("/anomalies", response_model=List[AnomalyReport])
def get_statistical_anomalies(db: Session = Depends(get_db)):
    """
    Detects statistical performance anomalies and extreme outliers in match performances.
    """
    service = DataQualityService(db)
    return service.detect_anomalies()


@router.post("/provenance", response_model=ProvenanceRecordResponse, status_code=status.HTTP_201_CREATED)
def log_data_provenance(record: ProvenanceRecordCreate, db: Session = Depends(get_db)):
    """
    Logs a new data provenance audit entry for data lineage and ingestion tracking.
    """
    service = DataQualityService(db)
    return service.log_provenance(record)


@router.get("/provenance", response_model=List[ProvenanceRecordResponse])
def get_data_provenance_logs(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Retrieves data provenance logs sorted by recency.
    """
    service = DataQualityService(db)
    return service.get_provenance_logs(limit=limit, offset=offset)
