"""
SuperScout Backend — Data Completeness Evaluator

Evaluates field-level completeness and missing data ratios across all core domain entities.
"""
from typing import Dict, List, Any, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.player import Player
from app.models.team import Team
from app.models.venue import Venue
from app.models.match import Match
from app.models.batting import BattingPerformance
from app.models.bowling import BowlingPerformance
from app.services.data_quality.schemas import (
    CompletenessReportResponse,
    EntityCompletenessSummary,
    FieldCompletenessItem,
    CompletenessReport,
)


class CompletenessChecker:
    """Evaluates field completeness percentages and missing field alerts across entities."""

    def __init__(self, db: Session):
        self.db = db

    def check_player_completeness(self, player_id: Optional[int] = None) -> CompletenessReport:
        if player_id:
            player = self.db.execute(select(Player).where(Player.id == player_id)).scalar_one_or_none()
            if not player:
                return CompletenessReport(
                    entity_name="Player",
                    total_records=0,
                    complete_records=0,
                    completeness_percentage=0.0,
                    missing_fields=["Player record not found"]
                )
            
            fields = ["name", "country", "primary_role", "batting_style", "bowling_style", "dob"]
            missing = []
            present_count = 0
            for f in fields:
                val = getattr(player, f, None)
                if val is not None and str(val).strip() != "":
                    present_count += 1
                else:
                    missing.append(f)

            pct = (present_count / len(fields)) * 100.0
            return CompletenessReport(
                entity_name="Player",
                total_records=1,
                complete_records=1 if len(missing) == 0 else 0,
                completeness_percentage=round(pct, 2),
                missing_fields=missing
            )
        else:
            players = list(self.db.scalars(select(Player)).all())
            total = len(players)
            if total == 0:
                return CompletenessReport(
                    entity_name="Player",
                    total_records=0,
                    complete_records=0,
                    completeness_percentage=100.0,
                    missing_fields=[]
                )
            fields = ["name", "country", "primary_role", "batting_style", "bowling_style", "dob"]
            complete_count = 0
            missing_set = set()
            for p in players:
                is_complete = True
                for f in fields:
                    val = getattr(p, f, None)
                    if val is None or str(val).strip() == "":
                        is_complete = False
                        missing_set.add(f)
                if is_complete:
                    complete_count += 1
            pct = (complete_count / total) * 100.0
            return CompletenessReport(
                entity_name="Player",
                total_records=total,
                complete_records=complete_count,
                completeness_percentage=round(pct, 2),
                missing_fields=list(missing_set)
            )

    def check_match_completeness(self) -> CompletenessReport:
        matches = list(self.db.scalars(select(Match)).all())
        total = len(matches)
        if total == 0:
            return CompletenessReport(
                entity_name="Match",
                total_records=0,
                complete_records=0,
                completeness_percentage=100.0,
                missing_fields=[]
            )
        fields = ["date", "venue", "format", "season"]
        complete_count = 0
        missing_set = set()
        for m in matches:
            is_complete = True
            for f in fields:
                val = getattr(m, f, None)
                if val is None or str(val).strip() == "":
                    is_complete = False
                    missing_set.add(f)
            if is_complete:
                complete_count += 1
        pct = (complete_count / total) * 100.0
        return CompletenessReport(
            entity_name="Match",
            total_records=total,
            complete_records=complete_count,
            completeness_percentage=round(pct, 2),
            missing_fields=list(missing_set)
        )

    def check_performance_completeness(self) -> CompletenessReport:
        perfs = list(self.db.scalars(select(BattingPerformance)).all())
        total = len(perfs)
        if total == 0:
            return CompletenessReport(
                entity_name="BattingPerformance",
                total_records=0,
                complete_records=0,
                completeness_percentage=100.0,
                missing_fields=[]
            )
        fields = ["player_id", "match_id", "runs", "balls_faced"]
        complete_count = 0
        missing_set = set()
        for p in perfs:
            is_complete = True
            for f in fields:
                val = getattr(p, f, None)
                if val is None:
                    is_complete = False
                    missing_set.add(f)
            if is_complete:
                complete_count += 1
        pct = (complete_count / total) * 100.0
        return CompletenessReport(
            entity_name="BattingPerformance",
            total_records=total,
            complete_records=complete_count,
            completeness_percentage=round(pct, 2),
            missing_fields=list(missing_set)
        )


class CompletenessEvaluator(CompletenessChecker):
    """Alias for backwards compatibility if needed."""
    def evaluate_all(self) -> CompletenessReportResponse:
        player_report = self.check_player_completeness()
        return CompletenessReportResponse(
            overall_completeness_score=player_report.completeness_percentage,
            entities={}
        )
