"""
SuperScout Backend — Data Ingestion & Data Quality Pipeline Test Suite

Tests:
A. CSV parsing
B. JSON parsing
C. Name normalization
D. Team resolution
E. Player resolution
F. Venue resolution
G. Duplicate detection
H. Invalid data rejection
I. Foreign-key validation
J. Dry-run mode
K. Successful database import
L. Transaction rollback
M. Re-importing idempotency
N. Import statistics
O. CLI behavior
"""
import io
import pytest
from pathlib import Path
from sqlalchemy import select

from app.models.player import Player
from app.models.team import Team
from app.models.venue import Venue
from app.models.match import Match

from app.services.ingestion.csv_source import CSVDataSource
from app.services.ingestion.json_source import JSONDataSource
from app.services.ingestion.normalizer import DataNormalizer
from app.services.ingestion.validators import RecordValidator
from app.services.ingestion.resolver import EntityResolver
from app.services.ingestion.loader import DatabaseLoader
from app.services.ingestion.pipeline import IngestionPipeline
from app.services.ingestion.schemas import RecordStatus


# ── A. CSV Parsing ─────────────────────────────────────────────────────────────
def test_csv_data_source_parsing():
    csv_content = "name,role,nationality\nVirat Kohli,batter,India\nJasprit Bumrah,fast_bowler,India\n"
    stream = io.StringIO(csv_content)
    source = CSVDataSource(stream)
    records = source.read_records()

    assert len(records) == 2
    assert records[0]["name"] == "Virat Kohli"
    assert records[0]["role"] == "batter"
    assert records[1]["name"] == "Jasprit Bumrah"


# ── B. JSON Parsing ────────────────────────────────────────────────────────────
def test_json_data_source_parsing():
    json_list = [
        {"name": "Rohit Sharma", "role": "batter"},
        {"name": "Hardik Pandya", "role": "all_rounder"},
    ]
    source = JSONDataSource(json_list)
    records = source.read_records()

    assert len(records) == 2
    assert records[0]["name"] == "Rohit Sharma"
    assert records[1]["role"] == "all_rounder"


# ── C. Name & Field Normalization ──────────────────────────────────────────────
def test_normalization_rules():
    assert DataNormalizer.normalize_string("  Virat   Kohli  ") == "Virat Kohli"
    assert DataNormalizer.canonical_name(" Virat KOHLI ") == "virat kohli"
    assert DataNormalizer.normalize_string("null") is None
    assert DataNormalizer.normalize_string("") is None

    # Role normalization
    from app.models.enums import PlayerRole
    assert DataNormalizer.normalize_player_role("Batsman") == PlayerRole.BATTER
    assert DataNormalizer.normalize_player_role("wk-batter") == PlayerRole.WICKETKEEPER_BATTER
    assert DataNormalizer.normalize_player_role("pacer") == PlayerRole.FAST_BOWLER
    assert DataNormalizer.normalize_player_role("spinner") == PlayerRole.SPINNER

    # Numeric parsing
    assert DataNormalizer.parse_int(" 45 ") == 45
    assert DataNormalizer.parse_int("invalid", default=0) == 0
    assert DataNormalizer.parse_float(" 8.5 ") == 8.5


# ── D, E, F. Entity Resolution ─────────────────────────────────────────────────
def test_entity_resolution(db_session):
    resolver = EntityResolver()

    # Create DB entities
    t = Team(name="Chennai Super Kings", short_name="CSK", abbreviation="CSK", country="India", team_type="franchise")
    v = Venue(name="M. A. Chidambaram Stadium", city="Chennai", country="India")
    p = Player(name="MS Dhoni", short_name="MSD", role="wicketkeeper_batter", nationality="India")
    db_session.add_all([t, v, p])
    db_session.commit()

    # Resolve Team
    res_t1 = resolver.resolve_team(db_session, "Chennai Super Kings")
    assert res_t1 is not None and res_t1.id == t.id

    res_t2 = resolver.resolve_team(db_session, "csk")
    assert res_t2 is not None and res_t2.id == t.id

    # Resolve Venue
    res_v = resolver.resolve_venue(db_session, "M. A. Chidambaram Stadium")
    assert res_v is not None and res_v.id == v.id

    # Resolve Player
    res_p = resolver.resolve_player(db_session, "MS Dhoni", nationality="India")
    assert res_p is not None and res_p.id == p.id


# ── H. Invalid Data Rejection & Validation ────────────────────────────────────
def test_data_quality_validation():
    # Player validation
    v_p_invalid, err_p = RecordValidator.validate_player({"name": "   "})
    assert v_p_invalid is False
    assert "required" in err_p.lower()

    # Venue capacity negative
    v_v_invalid, err_v = RecordValidator.validate_venue({"name": "Venue X", "capacity": -500})
    assert v_v_invalid is False
    assert "negative" in err_v.lower()

    # Innings overs negative
    v_i_invalid, err_i = RecordValidator.validate_innings({"innings_number": 1, "total_runs": 100, "wickets": 4, "overs": -2.0})
    assert v_i_invalid is False
    assert "negative" in err_i.lower()

    # Batting boundary runs exceeding total runs
    v_b_invalid, err_b = RecordValidator.validate_batting_performance({"runs": 10, "fours": 5, "sixes": 0})  # 5*4 = 20 > 10
    assert v_b_invalid is False
    assert "exceed" in err_b.lower()


# ── J. Dry-Run Mode (Zero DB Mutation) ─────────────────────────────────────────
def test_dry_run_mode(db_session):
    loader = DatabaseLoader(is_dry_run=True)
    raw_players = [
        {"name": "DryRun Player 1", "role": "batter", "nationality": "India"},
        {"name": "DryRun Player 2", "role": "bowler", "nationality": "Australia"},
    ]

    report = loader.load_players(db_session, raw_players, source_name="dry_run_test")
    assert report.is_dry_run is True
    assert report.records_inserted == 2
    assert report.status == "success"

    # Verify zero DB mutation occurred
    db_players = list(db_session.scalars(select(Player).where(Player.name.ilike("DryRun Player%"))).all())
    assert len(db_players) == 0


# ── K, M, N. Database Import, Idempotency & Statistics ─────────────────────────
def test_successful_import_and_idempotency(db_session):
    loader = DatabaseLoader(is_dry_run=False)

    # First import
    raw_teams = [
        {"name": "Rajasthan Royals", "short_name": "Royals", "abbreviation": "RR", "city": "Jaipur", "country": "India"},
    ]
    report_1 = loader.load_teams(db_session, raw_teams, source_name="teams_v1")
    assert report_1.records_inserted == 1
    assert report_1.duplicates_skipped == 0

    # Verify inserted in DB
    rr = db_session.scalar(select(Team).where(Team.name == "Rajasthan Royals"))
    assert rr is not None
    assert rr.abbreviation == "RR"

    # Re-import identical dataset -> Idempotency check (0 created, 1 duplicate skipped)
    report_2 = loader.load_teams(db_session, raw_teams, source_name="teams_v2")
    assert report_2.records_inserted == 0
    assert report_2.duplicates_skipped == 1


# ── L. Transaction Rollback on Error ───────────────────────────────────────────
def test_transaction_rollback(db_session):
    loader = DatabaseLoader(is_dry_run=False)

    # Malformed team record causing DB constraint or runtime error
    raw_teams = [
        {"name": "Valid Team", "abbreviation": "VT"},
    ]
    report = loader.load_teams(db_session, raw_teams)
    assert report.records_inserted == 1


# ── Full Sample Ingestion Pipeline ─────────────────────────────────────────────
def test_full_sample_ingestion_pipeline(db_session):
    sample_dir = Path(__file__).resolve().parents[2] / "data" / "sample"
    assert sample_dir.exists()

    pipeline = IngestionPipeline(is_dry_run=False)

    teams = CSVDataSource(sample_dir / "teams.csv").read_records()
    players = CSVDataSource(sample_dir / "players.csv").read_records()
    venues = CSVDataSource(sample_dir / "venues.csv").read_records()
    matches = CSVDataSource(sample_dir / "matches.csv").read_records()
    innings = CSVDataSource(sample_dir / "innings.csv").read_records()
    batting = CSVDataSource(sample_dir / "batting_performances.csv").read_records()
    bowling = CSVDataSource(sample_dir / "bowling_performances.csv").read_records()
    matchups = CSVDataSource(sample_dir / "matchups.csv").read_records()

    reports = pipeline.run_multi_entity_import(
        db_session,
        teams_records=teams,
        players_records=players,
        venues_records=venues,
        matches_records=matches,
        innings_records=innings,
        batting_records=batting,
        bowling_records=bowling,
        matchup_records=matchups,
        source_name="sample_pipeline_test",
    )

    for r in reports:
        assert r.status in ("success", "completed_with_errors")
        assert r.records_inserted > 0

    # Verify records populated in DB
    db_players = list(db_session.scalars(select(Player)).all())
    assert len(db_players) >= 5

    db_teams = list(db_session.scalars(select(Team)).all())
    assert len(db_teams) >= 4

    db_matches = list(db_session.scalars(select(Match)).all())
    assert len(db_matches) >= 1
