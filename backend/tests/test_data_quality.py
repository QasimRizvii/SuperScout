"""
Step 8 — Data Quality, Trust & Provenance Tests for SuperScout.
"""

import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.player import Player
from app.models.team import Team
from app.models.match import Match
from app.models.innings import Innings
from app.models.batting import BattingPerformance
from app.models.bowling import BowlingPerformance
from app.models.provenance import DataProvenanceLog
from app.models.enums import PlayerRole
from app.services.data_quality.data_quality_service import DataQualityService
from app.services.data_quality.completeness import CompletenessChecker
from app.services.data_quality.consistency import ConsistencyChecker
from app.services.data_quality.anomaly_detector import AnomalyDetector
from app.services.data_quality.duplicate_detector import DuplicateDetector
from app.services.data_quality.relationship_integrity import RelationshipIntegrityEngine
from app.services.data_quality.trust_score_engine import TrustScoreEngine
from app.services.data_quality.provenance_manager import ProvenanceManager
from app.services.data_quality.schemas import ProvenanceRecordCreate


@pytest.fixture
def sample_data(db_session: Session):
    """Creates initial fixture data for testing quality engines."""
    p1 = Player(
        name="Jasprit Bumrah",
        date_of_birth=date(1993, 12, 6),
        nationality="India",
        role=PlayerRole.BOWLER,
        batting_style="Right-hand bat",
        bowling_style="Right-arm fast"
    )
    p2 = Player(
        name="Jasprit Bumrah",  # Duplicate candidate
        date_of_birth=date(1993, 12, 6),
        nationality="India",
        role=PlayerRole.BOWLER,
        batting_style=None,
        bowling_style=None
    )
    p3 = Player(
        name="Incomplete Player",
        nationality=None,
        role=PlayerRole.BATTER
    )

    db_session.add_all([p1, p2, p3])
    db_session.commit()
    db_session.refresh(p1)
    db_session.refresh(p2)
    db_session.refresh(p3)

    t1 = Team(name="Mumbai Indians", abbreviation="MI", country="India")
    t2 = Team(name="Chennai Super Kings", abbreviation="CSK", country="India")
    db_session.add_all([t1, t2])
    db_session.commit()
    db_session.refresh(t1)
    db_session.refresh(t2)

    m1 = Match(
        season="2025",
        match_date=date(2025, 4, 1),
        team_1_id=t1.id,
        team_2_id=t2.id,
        venue_id=1,
        match_type="T20",
        competition="IPL 2025"
    )
    db_session.add(m1)
    db_session.commit()
    db_session.refresh(m1)

    inn1 = Innings(
        match_id=m1.id,
        innings_number=1,
        batting_team_id=t1.id,
        bowling_team_id=t2.id
    )
    db_session.add(inn1)
    db_session.commit()
    db_session.refresh(inn1)

    perf1 = BattingPerformance(
        player_id=p1.id,
        match_id=m1.id,
        innings_id=inn1.id,
        team_id=t1.id,
        runs=45,
        balls_faced=15,  # SR = 300
        fours=4,
        sixes=3,
        strike_rate=300.0
    )
    perf_inconsistent = BattingPerformance(
        player_id=p2.id,
        match_id=m1.id,
        innings_id=inn1.id,
        team_id=t1.id,
        runs=10,
        balls_faced=0,  # Impossible: runs with 0 balls
        fours=5,
        sixes=5,  # Impossible: 5*4 + 5*6 = 50 > 10 runs
        strike_rate=0.0
    )
    db_session.add_all([perf1, perf_inconsistent])
    db_session.commit()

    return {
        "p1": p1,
        "p2": p2,
        "p3": p3,
        "m1": m1,
        "inn1": inn1,
        "t1": t1,
        "t2": t2,
        "perf1": perf1,
        "perf_inconsistent": perf_inconsistent
    }


def test_completeness_checker(db_session: Session, sample_data):
    checker = CompletenessChecker(db_session)
    player_comp = checker.check_player_completeness()
    assert player_comp.entity_name == "Player"
    assert player_comp.total_records >= 3

    single_comp = checker.check_player_completeness(sample_data["p1"].id)
    assert single_comp.completeness_percentage > 0.0

    p3_comp = checker.check_player_completeness(sample_data["p3"].id)
    assert p3_comp.completeness_percentage < 100.0


def test_consistency_checker(db_session: Session, sample_data):
    checker = ConsistencyChecker(db_session)
    issues = checker.check_all_consistency()
    assert len(issues) > 0
    issue_descriptions = [i.description for i in issues]
    assert any("boundary" in desc.lower() for desc in issue_descriptions) or any("exceed" in desc.lower() for desc in issue_descriptions)


def test_anomaly_detector(db_session: Session, sample_data):
    detector = AnomalyDetector(db_session)
    anomalies = detector.detect_all_anomalies()
    assert isinstance(anomalies, list)


def test_duplicate_detector(db_session: Session, sample_data):
    detector = DuplicateDetector(db_session)
    duplicates = detector.find_duplicate_players(name_similarity_threshold=0.8)
    assert len(duplicates) >= 1
    dup = duplicates[0]
    assert (dup.player1_name == "Jasprit Bumrah" and dup.player2_name == "Jasprit Bumrah")


def test_relationship_integrity(db_session: Session, sample_data):
    integrity = RelationshipIntegrityEngine(db_session)
    # Insert an orphaned performance
    orphaned_perf = BattingPerformance(
        player_id=99999,  # Non-existent player
        match_id=sample_data["m1"].id,
        innings_id=sample_data["inn1"].id,
        team_id=sample_data["t1"].id,
        runs=10,
        balls_faced=10
    )
    db_session.add(orphaned_perf)
    db_session.commit()

    issues = integrity.check_all_integrity()
    assert len(issues) >= 1
    assert any(i.referenced_id == 99999 for i in issues)


def test_trust_score_engine(db_session: Session, sample_data):
    trust_engine = TrustScoreEngine(db_session)
    res1 = trust_engine.calculate_player_trust_score(sample_data["p1"].id)
    assert res1.player_id == sample_data["p1"].id
    assert res1.trust_score > 0.0
    assert res1.confidence_rating in ["HIGH", "MEDIUM", "LOW", "UNTRUSTY"]

    res_unknown = trust_engine.calculate_player_trust_score(999999)
    assert res_unknown.trust_score == 0.0
    assert res_unknown.confidence_rating == "UNTRUSTY"


def test_provenance_manager(db_session: Session):
    manager = ProvenanceManager(db_session)
    rec = ProvenanceRecordCreate(
        source_name="BCCI Official API",
        source_type="API",
        dataset_name="IPL 2025 Player Stats",
        batch_id="BATCH_2025_001",
        records_ingested=120,
        records_failed=2,
        ingested_by="admin_user",
        is_verified=True,
        notes="Verified against official scorecard"
    )
    db_log = manager.log_provenance(rec)
    assert db_log.id is not None
    assert db_log.batch_id == "BATCH_2025_001"

    logs = manager.get_provenance_logs(limit=10)
    assert len(logs) >= 1
    batch_logs = manager.get_provenance_by_batch("BATCH_2025_001")
    assert len(batch_logs) == 1


# ── REST API Integration Tests ───────────────────────────────────────────────────

def test_api_system_data_quality_report(client: TestClient, sample_data):
    response = client.get("/api/v1/data-quality/report")
    assert response.status_code == 200
    data = response.json()
    assert "overall_score" in data
    assert "completeness" in data
    assert "consistency_issues" in data
    assert "anomalies" in data
    assert "duplicate_candidates" in data
    assert "integrity_issues" in data


def test_api_player_trust_score(client: TestClient, sample_data):
    p_id = sample_data["p1"].id
    response = client.get(f"/api/v1/data-quality/trust-score/{p_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["player_id"] == p_id
    assert "trust_score" in data
    assert "confidence_rating" in data

    response_404 = client.get("/api/v1/data-quality/trust-score/999999")
    assert response_404.status_code == 404


def test_api_duplicate_candidates(client: TestClient, sample_data):
    response = client.get("/api/v1/data-quality/duplicates?threshold=0.8")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_api_anomalies(client: TestClient, sample_data):
    response = client.get("/api/v1/data-quality/anomalies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_api_provenance(client: TestClient):
    payload = {
        "source_name": "Cricinfo Data Dump",
        "source_type": "CSV",
        "dataset_name": "IPL 2024 Retentions",
        "batch_id": "BATCH_2024_RET",
        "records_ingested": 50,
        "records_failed": 0,
        "ingested_by": "data_pipeline",
        "is_verified": True
    }
    post_res = client.post("/api/v1/data-quality/provenance", json=payload)
    assert post_res.status_code == 201
    post_data = post_res.json()
    assert post_data["batch_id"] == "BATCH_2024_RET"

    get_res = client.get("/api/v1/data-quality/provenance?limit=10")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert len(get_data) >= 1
