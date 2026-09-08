"""
Relationship Integrity Engine for SuperScout.

Validates foreign key integrity and identifies orphaned or dangling records across database models.
"""

from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, outerjoin

from app.models.player import Player
from app.models.match import Match
from app.models.batting import BattingPerformance
from app.models.bowling import BowlingPerformance
from app.models.scouting import ScoutingWatchlist, ScoutingNote
from app.services.data_quality.schemas import IntegrityIssue


class RelationshipIntegrityEngine:
    """
    Checks for orphaned records and foreign key inconsistency across entities.
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def check_all_integrity(self) -> List[IntegrityIssue]:
        """Runs all relationship integrity checks."""
        issues: List[IntegrityIssue] = []
        issues.extend(self.check_orphaned_batting_performances())
        issues.extend(self.check_orphaned_bowling_performances())
        issues.extend(self.check_orphaned_scouting_watchlists())
        issues.extend(self.check_orphaned_scouting_notes())
        return issues

    def check_orphaned_batting_performances(self) -> List[IntegrityIssue]:
        """Finds BattingPerformance records referencing non-existent Players or Matches."""
        issues: List[IntegrityIssue] = []

        # Batting -> Player
        stmt_p = (
            select(BattingPerformance.id, BattingPerformance.player_id)
            .outerjoin(Player, BattingPerformance.player_id == Player.id)
            .where(Player.id.is_(None))
        )
        orphaned_players = self.db.execute(stmt_p).all()
        for perf_id, player_id in orphaned_players:
            issues.append(
                IntegrityIssue(
                    entity="BattingPerformance",
                    entity_id=perf_id,
                    issue_type="orphaned_foreign_key",
                    description=f"BattingPerformance {perf_id} references missing Player ID {player_id}",
                    referenced_entity="Player",
                    referenced_id=player_id
                )
            )

        # Batting -> Match
        stmt_m = (
            select(BattingPerformance.id, BattingPerformance.match_id)
            .outerjoin(Match, BattingPerformance.match_id == Match.id)
            .where(Match.id.is_(None))
        )
        orphaned_matches = self.db.execute(stmt_m).all()
        for perf_id, match_id in orphaned_matches:
            issues.append(
                IntegrityIssue(
                    entity="BattingPerformance",
                    entity_id=perf_id,
                    issue_type="orphaned_foreign_key",
                    description=f"BattingPerformance {perf_id} references missing Match ID {match_id}",
                    referenced_entity="Match",
                    referenced_id=match_id
                )
            )

        return issues

    def check_orphaned_bowling_performances(self) -> List[IntegrityIssue]:
        """Finds BowlingPerformance records referencing non-existent Players or Matches."""
        issues: List[IntegrityIssue] = []

        # Bowling -> Player
        stmt_p = (
            select(BowlingPerformance.id, BowlingPerformance.player_id)
            .outerjoin(Player, BowlingPerformance.player_id == Player.id)
            .where(Player.id.is_(None))
        )
        orphaned_players = self.db.execute(stmt_p).all()
        for perf_id, player_id in orphaned_players:
            issues.append(
                IntegrityIssue(
                    entity="BowlingPerformance",
                    entity_id=perf_id,
                    issue_type="orphaned_foreign_key",
                    description=f"BowlingPerformance {perf_id} references missing Player ID {player_id}",
                    referenced_entity="Player",
                    referenced_id=player_id
                )
            )

        # Bowling -> Match
        stmt_m = (
            select(BowlingPerformance.id, BowlingPerformance.match_id)
            .outerjoin(Match, BowlingPerformance.match_id == Match.id)
            .where(Match.id.is_(None))
        )
        orphaned_matches = self.db.execute(stmt_m).all()
        for perf_id, match_id in orphaned_matches:
            issues.append(
                IntegrityIssue(
                    entity="BowlingPerformance",
                    entity_id=perf_id,
                    issue_type="orphaned_foreign_key",
                    description=f"BowlingPerformance {perf_id} references missing Match ID {match_id}",
                    referenced_entity="Match",
                    referenced_id=match_id
                )
            )

        return issues

    def check_orphaned_scouting_watchlists(self) -> List[IntegrityIssue]:
        """Finds ScoutingWatchlist records referencing non-existent Players."""
        issues: List[IntegrityIssue] = []
        stmt = (
            select(ScoutingWatchlist.id, ScoutingWatchlist.player_id)
            .outerjoin(Player, ScoutingWatchlist.player_id == Player.id)
            .where(Player.id.is_(None))
        )
        results = self.db.execute(stmt).all()
        for wl_id, player_id in results:
            issues.append(
                IntegrityIssue(
                    entity="ScoutingWatchlist",
                    entity_id=wl_id,
                    issue_type="orphaned_foreign_key",
                    description=f"ScoutingWatchlist {wl_id} references missing Player ID {player_id}",
                    referenced_entity="Player",
                    referenced_id=player_id
                )
            )
        return issues

    def check_orphaned_scouting_notes(self) -> List[IntegrityIssue]:
        """Finds ScoutingNote records referencing non-existent Players."""
        issues: List[IntegrityIssue] = []
        stmt = (
            select(ScoutingNote.id, ScoutingNote.player_id)
            .outerjoin(Player, ScoutingNote.player_id == Player.id)
            .where(Player.id.is_(None))
        )
        results = self.db.execute(stmt).all()
        for note_id, player_id in results:
            issues.append(
                IntegrityIssue(
                    entity="ScoutingNote",
                    entity_id=note_id,
                    issue_type="orphaned_foreign_key",
                    description=f"ScoutingNote {note_id} references missing Player ID {player_id}",
                    referenced_entity="Player",
                    referenced_id=player_id
                )
            )
        return issues
