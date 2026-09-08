"""
SuperScout Backend — Data Quality Schemas
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ── Completeness Schemas ──────────────────────────────────────────────────────

class FieldCompletenessItem(BaseModel):
    field_name: str
    missing_count: int
    present_count: int
    field_completeness_pct: float


class EntityCompletenessSummary(BaseModel):
    entity_type: str
    total_records: int
    overall_completeness_pct: float
    field_breakdown: List[FieldCompletenessItem] = Field(default_factory=list)
    affected_records_count: int = 0
    severity: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL


class CompletenessReportResponse(BaseModel):
    overall_completeness_score: float
    entities: Dict[str, EntityCompletenessSummary] = Field(default_factory=dict)


class CompletenessReport(BaseModel):
    entity_name: str
    total_records: int
    complete_records: int
    completeness_percentage: float
    missing_fields: List[str] = Field(default_factory=list)


# ── Consistency Schemas ───────────────────────────────────────────────────────

class InconsistencyIssue(BaseModel):
    entity_type: str
    entity_id: Optional[int] = None
    issue_code: str
    message: str
    severity: str = "warning"  # warning, critical
    field_name: Optional[str] = None
    invalid_value: Optional[Any] = None


class ConsistencyCheckRequest(BaseModel):
    runs: Optional[int] = None
    balls: Optional[int] = None
    wickets: Optional[int] = None
    overs: Optional[float] = None
    fours: Optional[int] = None
    sixes: Optional[int] = None
    toss_winner_team_id: Optional[int] = None
    team1_id: Optional[int] = None
    team2_id: Optional[int] = None


class ConsistencyCheckResponse(BaseModel):
    is_valid: bool
    issues_found_count: int
    issues: List[InconsistencyIssue] = Field(default_factory=list)


class ConsistencyIssue(BaseModel):
    entity: str
    entity_id: int
    rule_broken: str
    description: str
    severity: str = "HIGH"


# ── Anomaly Detection Schemas ─────────────────────────────────────────────────

class PerformanceAnomalyItem(BaseModel):
    performance_id: int
    performance_type: str  # batting, bowling
    match_id: int
    player_id: int
    player_name: str
    metric_name: str
    metric_value: float
    benchmark_expected: str
    anomaly_type: str
    severity: str = "informational"  # informational, warning, critical
    explanation: str


class AnomalyReportResponse(BaseModel):
    total_performances_scanned: int
    anomalies_detected_count: int
    critical_count: int
    warning_count: int
    informational_count: int
    anomalies: List[PerformanceAnomalyItem] = Field(default_factory=list)


class AnomalyReport(BaseModel):
    entity: str
    entity_id: int
    anomaly_type: str
    metric_name: str
    observed_value: float
    expected_range: str
    severity: str = "HIGH"
    description: str


# ── Duplicate Detection Schemas ───────────────────────────────────────────────

class DuplicateCandidatePair(BaseModel):
    entity_type: str
    entity_1_id: int
    entity_1_name: str
    entity_2_id: int
    entity_2_name: str
    similarity_score: float  # 0 to 100
    matching_factors: List[str] = Field(default_factory=list)
    review_status: str = "PENDING_REVIEW"


class DuplicateReportResponse(BaseModel):
    entity_type: str
    total_candidates_checked: int
    duplicate_pairs_found: int
    duplicates: List[DuplicateCandidatePair] = Field(default_factory=list)


class DuplicateCandidate(BaseModel):
    player1_id: int
    player1_name: str
    player2_id: int
    player2_name: str
    similarity_score: float
    matching_fields: List[str] = Field(default_factory=list)
    recommendation: str


# ── Relationship Integrity Schemas ───────────────────────────────────────────

class RelationshipIntegrityItem(BaseModel):
    relationship_name: str
    total_checked: int
    orphan_count: int
    integrity_pct: float
    sample_orphan_ids: List[int] = Field(default_factory=list)
    description: str


class RelationshipIntegrityResponse(BaseModel):
    overall_integrity_score: float
    relationships: List[RelationshipIntegrityItem] = Field(default_factory=list)


class IntegrityIssue(BaseModel):
    entity: str
    entity_id: int
    issue_type: str
    description: str
    referenced_entity: str
    referenced_id: int


# ── Player Trust Score Schemas ────────────────────────────────────────────────

class PlayerTrustScoreResponse(BaseModel):
    player_id: int
    player_name: str
    trust_score: float  # 0 to 100
    confidence_rating: str  # HIGH, MEDIUM, LOW, UNTRUSTY
    completeness_score: float
    consistency_score: float
    sample_size_confidence: float
    recency_score: float
    deductions: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    explainability_notes: Dict[str, Any] = Field(default_factory=dict)


# ── Data Provenance Schemas ───────────────────────────────────────────────────

class ProvenanceRecordCreate(BaseModel):
    source_name: str
    source_type: str
    dataset_name: str
    batch_id: str
    records_ingested: int
    records_failed: int = 0
    ingested_by: str = "system"
    is_verified: bool = True
    verification_method: Optional[str] = "checksum"
    notes: Optional[str] = None
    meta_info: Optional[Dict[str, Any]] = None


class ProvenanceRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_name: str
    source_type: str
    dataset_name: str
    batch_id: str
    records_ingested: int
    records_failed: int
    ingested_by: str
    is_verified: bool
    verification_method: Optional[str] = None
    notes: Optional[str] = None
    meta_info: Optional[Dict[str, Any]] = None
    timestamp: datetime


class ProvenanceLogCreateRequest(BaseModel):
    batch_id: str
    source_name: str
    source_type: str = "csv"
    source_url: Optional[str] = None
    dataset_version: Optional[str] = "1.0"
    records_processed: int = 0
    status: str = "completed"
    details: Optional[Dict[str, Any]] = None


class ProvenanceLogResponse(BaseModel):
    id: int
    batch_id: str
    source_name: str
    source_type: str
    source_url: Optional[str] = None
    dataset_version: Optional[str] = None
    records_processed: int
    status: str
    details: Optional[Dict[str, Any]] = None
    imported_at: datetime


# ── System Data Quality Overview ──────────────────────────────────────────────

class DataQualityReportResponse(BaseModel):
    overall_score: float  # 0 to 100
    completeness: List[CompletenessReport] = Field(default_factory=list)
    consistency_issues: List[ConsistencyIssue] = Field(default_factory=list)
    anomalies: List[AnomalyReport] = Field(default_factory=list)
    duplicate_candidates: List[DuplicateCandidate] = Field(default_factory=list)
    integrity_issues: List[IntegrityIssue] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)


class DataQualityOverviewResponse(BaseModel):
    overall_quality_score: float  # 0 to 100
    completeness_score: float
    consistency_score: float
    uniqueness_score: float
    anomaly_score: float
    relationship_integrity_score: float
    total_entities_evaluated: int
    warnings_count: int
    critical_issues_count: int
    score_explanation: str
    recommended_actions: List[str] = Field(default_factory=list)
