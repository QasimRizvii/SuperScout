"""
SuperScout Backend — Developer CLI for Ingestion Pipeline

Usage:
  python -m app.services.ingestion.cli import --file <path> [--entity players|teams|venues|matches|all] [--dry-run]
  python -m app.services.ingestion.cli validate --file <path> [--entity players|teams|venues|matches]
  python -m app.services.ingestion.cli import-sample [--dry-run]
"""
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any

from app.db.session import SessionLocal
from app.services.ingestion.pipeline import IngestionPipeline
from app.services.ingestion.loader import DatabaseLoader
from app.services.ingestion.schemas import IngestionReport, RecordStatus


def get_sample_dir() -> Path:
    """Resolve workspace root data/sample directory."""
    return Path(__file__).resolve().parents[4] / "data" / "sample"


def run_sample_import(is_dry_run: bool = False) -> None:
    """Helper to run multi-entity import from data/sample directory."""
    sample_dir = get_sample_dir()
    if not sample_dir.exists():
        print(f"Error: Sample data directory not found at '{sample_dir}'")
        sys.exit(1)

    print(f"Loading sample dataset from '{sample_dir}' (dry_run={is_dry_run})...")

    def load_if_exists(filename: str) -> List[Dict[str, Any]]:
        p = sample_dir / filename
        if p.exists():
            return IngestionPipeline.load_file_records(str(p))
        return []

    teams = load_if_exists("teams.csv")
    players = load_if_exists("players.csv")
    venues = load_if_exists("venues.csv")
    matches = load_if_exists("matches.csv")
    innings = load_if_exists("innings.csv")
    batting = load_if_exists("batting_performances.csv")
    bowling = load_if_exists("bowling_performances.csv")
    matchups = load_if_exists("matchups.csv")

    pipeline = IngestionPipeline(is_dry_run=is_dry_run)
    with SessionLocal() as db:
        reports = pipeline.run_multi_entity_import(
            db,
            teams_records=teams,
            players_records=players,
            venues_records=venues,
            matches_records=matches,
            innings_records=innings,
            batting_records=batting,
            bowling_records=bowling,
            matchup_records=matchups,
            source_name="sample_dataset",
        )

        for rep in reports:
            print(rep.format_cli_summary())


def main():
    parser = argparse.ArgumentParser(prog="superscout-ingest", description="SuperScout Cricket Data Ingestion CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Command: import
    import_parser = subparsers.add_parser("import", help="Import CSV or JSON file into SuperScout DB")
    import_parser.add_argument("--file", required=True, help="Path to input CSV or JSON file")
    import_parser.add_argument(
        "--entity",
        choices=["players", "teams", "venues", "matches", "innings", "batting", "bowling", "matchups"],
        default="players",
        help="Target entity type",
    )
    import_parser.add_argument("--dry-run", action="store_true", help="Perform validation and duplicate check without committing DB changes")

    # Command: validate
    val_parser = subparsers.add_parser("validate", help="Validate input file records without inserting")
    val_parser.add_argument("--file", required=True, help="Path to input CSV or JSON file")
    val_parser.add_argument(
        "--entity",
        choices=["players", "teams", "venues", "matches", "innings", "batting", "bowling", "matchups"],
        default="players",
        help="Target entity type",
    )

    # Command: import-sample
    sample_parser = subparsers.add_parser("import-sample", help="Import default deterministic sample dataset from data/sample/")
    sample_parser.add_argument("--dry-run", action="store_true", help="Run sample import in dry-run mode")

    args = parser.parse_args()

    if args.command == "import-sample":
        run_sample_import(is_dry_run=args.dry_run)
        return

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found at '{file_path}'")
        sys.exit(1)

    try:
        records = IngestionPipeline.load_file_records(str(file_path))
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        sys.exit(1)

    is_dry_run = args.dry_run if hasattr(args, "dry_run") else True
    if args.command == "validate":
        is_dry_run = True

    loader = DatabaseLoader(is_dry_run=is_dry_run)

    with SessionLocal() as db:
        if args.entity == "players":
            report = loader.load_players(db, records, source_name=str(file_path))
        elif args.entity == "teams":
            report = loader.load_teams(db, records, source_name=str(file_path))
        elif args.entity == "venues":
            report = loader.load_venues(db, records, source_name=str(file_path))
        elif args.entity == "matches":
            report = loader.load_matches(db, records, source_name=str(file_path))
        elif args.entity == "innings":
            report = loader.load_innings(db, records, source_name=str(file_path))
        elif args.entity == "batting":
            report = loader.load_batting_performances(db, records, source_name=str(file_path))
        elif args.entity == "bowling":
            report = loader.load_bowling_performances(db, records, source_name=str(file_path))
        elif args.entity == "matchups":
            report = loader.load_matchups(db, records, source_name=str(file_path))
        else:
            print(f"Error: Unsupported entity '{args.entity}'")
            sys.exit(1)

        print(report.format_cli_summary())


if __name__ == "__main__":
    main()
