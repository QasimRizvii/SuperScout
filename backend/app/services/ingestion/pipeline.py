"""
SuperScout Backend — Full Ingestion Pipeline Orchestrator

Executes multi-entity dataset ingestion in strict dependency order:
1. Teams -> 2. Players -> 3. Venues -> 4. Matches -> 5. Innings -> 6. Batting -> 7. Bowling -> 8. Matchups
"""
import time
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.services.ingestion.schemas import IngestionReport, RecordStatus
from app.services.ingestion.loader import DatabaseLoader
from app.services.ingestion.resolver import EntityResolver
from app.services.ingestion.csv_source import CSVDataSource
from app.services.ingestion.json_source import JSONDataSource


class IngestionPipeline:
    """
    High-level orchestrator for full dataset imports from CSV/JSON sources.
    """

    def __init__(self, is_dry_run: bool = False):
        self.is_dry_run = is_dry_run
        self.resolver = EntityResolver()
        self.loader = DatabaseLoader(resolver=self.resolver, is_dry_run=is_dry_run)

    def run_multi_entity_import(
        self,
        db: Session,
        teams_records: Optional[List[Dict[str, Any]]] = None,
        players_records: Optional[List[Dict[str, Any]]] = None,
        venues_records: Optional[List[Dict[str, Any]]] = None,
        matches_records: Optional[List[Dict[str, Any]]] = None,
        innings_records: Optional[List[Dict[str, Any]]] = None,
        batting_records: Optional[List[Dict[str, Any]]] = None,
        bowling_records: Optional[List[Dict[str, Any]]] = None,
        matchup_records: Optional[List[Dict[str, Any]]] = None,
        source_name: str = "multi_entity_dataset",
    ) -> List[IngestionReport]:
        """
        Execute dataset import across all supplied entities in dependency order.
        """
        reports: List[IngestionReport] = []

        # 1. Teams
        if teams_records:
            t_report = self.loader.load_teams(db, teams_records, source_name=f"{source_name}:teams")
            reports.append(t_report)

        # 2. Players
        if players_records:
            p_report = self.loader.load_players(db, players_records, source_name=f"{source_name}:players")
            reports.append(p_report)

        # 3. Venues
        if venues_records:
            v_report = self.loader.load_venues(db, venues_records, source_name=f"{source_name}:venues")
            reports.append(v_report)

        # 4. Matches
        if matches_records:
            m_report = self.loader.load_matches(db, matches_records, source_name=f"{source_name}:matches")
            reports.append(m_report)

        # 5. Innings
        if innings_records:
            i_report = self.loader.load_innings(db, innings_records, source_name=f"{source_name}:innings")
            reports.append(i_report)

        # 6. Batting
        if batting_records:
            b_report = self.loader.load_batting_performances(db, batting_records, source_name=f"{source_name}:batting")
            reports.append(b_report)

        # 7. Bowling
        if bowling_records:
            bw_report = self.loader.load_bowling_performances(db, bowling_records, source_name=f"{source_name}:bowling")
            reports.append(bw_report)

        # 8. Matchups
        if matchup_records:
            mu_report = self.loader.load_matchups(db, matchup_records, source_name=f"{source_name}:matchups")
            reports.append(mu_report)

        return reports

    @staticmethod
    def load_file_records(file_path: str, format_hint: Optional[str] = None) -> List[Dict[str, Any]]:
        """Utility to load records from CSV or JSON file path."""
        lower_path = file_path.lower()
        if format_hint == "csv" or lower_path.endswith(".csv"):
            return CSVDataSource(file_path).read_records()
        elif format_hint == "json" or lower_path.endswith(".json"):
            return JSONDataSource(file_path).read_records()
        else:
            raise ValueError(f"Unsupported file format for path '{file_path}'. Must be CSV or JSON.")
