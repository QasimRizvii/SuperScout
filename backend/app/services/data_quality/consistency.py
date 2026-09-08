"""
SuperScout Backend — Cricket Logical Consistency Engine

Validates domain business rules and cricket statistical logic across performances, innings, and matches.
"""
from typing import Dict, List, Optional, Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.batting import BattingPerformance
from app.models.bowling import BowlingPerformance
from app.models.match import Match
from app.models.innings import Innings
from app.services.data_quality.schemas import (
    ConsistencyCheckRequest,
    ConsistencyCheckResponse,
    InconsistencyIssue,
    ConsistencyIssue,
)


class ConsistencyEngine:
    """Cricket-aware logical rule engine validating record integrity."""

    def __init__(self, db: Session):
        self.db = db

    def check_raw_performance(self, req: ConsistencyCheckRequest) -> ConsistencyCheckResponse:
        """Validate raw input parameters against cricket rules."""
        issues: List[InconsistencyIssue] = []

        # 1. Batting runs / balls non-negative
        if req.runs is not None and req.runs < 0:
            issues.append(
                InconsistencyIssue(
                    entity_type="BattingPerformance",
                    issue_code="NEGATIVE_RUNS",
                    message=f"Batting runs cannot be negative ({req.runs}).",
                    severity="critical",
                    field_name="runs",
                    invalid_value=req.runs,
                )
            )

        if req.balls is not None and req.balls < 0:
            issues.append(
                InconsistencyIssue(
                    entity_type="Performance",
                    issue_code="NEGATIVE_BALLS",
                    message=f"Balls count cannot be negative ({req.balls}).",
                    severity="critical",
                    field_name="balls",
                    invalid_value=req.balls,
                )
            )

        # 2. Wickets non-negative & max legal limit check
        if req.wickets is not None:
            if req.wickets < 0:
                issues.append(
                    InconsistencyIssue(
                        entity_type="BowlingPerformance",
                        issue_code="NEGATIVE_WICKETS",
                        message=f"Wickets cannot be negative ({req.wickets}).",
                        severity="critical",
                        field_name="wickets",
                        invalid_value=req.wickets,
                    )
                )
            elif req.wickets > 10:
                issues.append(
                    InconsistencyIssue(
                        entity_type="BowlingPerformance",
                        issue_code="EXCESS_WICKETS",
                        message=f"Individual wickets ({req.wickets}) exceeds maximum legal innings limit of 10.",
                        severity="critical",
                        field_name="wickets",
                        invalid_value=req.wickets,
                    )
                )

        # 3. Boundaries vs Runs consistency
        if req.runs is not None and req.fours is not None and req.sixes is not None:
            boundary_runs = (req.fours * 4) + (req.sixes * 6)
            if boundary_runs > req.runs:
                issues.append(
                    InconsistencyIssue(
                        entity_type="BattingPerformance",
                        issue_code="BOUNDARY_RUNS_EXCEED_TOTAL",
                        message=(
                            f"Boundary runs ({req.fours} fours + {req.sixes} sixes = {boundary_runs}) "
                            f"exceed total runs ({req.runs})."
                        ),
                        severity="critical",
                        field_name="boundary_runs",
                        invalid_value={"fours": req.fours, "sixes": req.sixes, "runs": req.runs},
                    )
                )

        # 4. Toss Winner vs Match Teams
        if req.toss_winner_team_id is not None and req.team1_id is not None and req.team2_id is not None:
            if req.toss_winner_team_id not in (req.team1_id, req.team2_id):
                issues.append(
                    InconsistencyIssue(
                        entity_type="Match",
                        issue_code="TOSS_WINNER_MISMATCH",
                        message=f"Toss winner team ID ({req.toss_winner_team_id}) is not one of the competing match teams ({req.team1_id}, {req.team2_id}).",
                        severity="critical",
                        field_name="toss_winner_team_id",
                        invalid_value=req.toss_winner_team_id,
                    )
                )

        return ConsistencyCheckResponse(
            is_valid=(len(issues) == 0),
            issues_found_count=len(issues),
            issues=issues,
        )

    def scan_all_database_records(self) -> List[InconsistencyIssue]:
        """Scan entire database for logical inconsistencies."""
        issues: List[InconsistencyIssue] = []

        # 1. Scan Batting Performances
        bat_perfs = list(self.db.scalars(select(BattingPerformance)).all())
        for b in bat_perfs:
            if b.runs < 0:
                issues.append(
                    InconsistencyIssue(
                        entity_type="BattingPerformance",
                        entity_id=b.id,
                        issue_code="NEGATIVE_RUNS",
                        message=f"Batting performance ID {b.id} has negative runs ({b.runs}).",
                        severity="critical",
                        field_name="runs",
                        invalid_value=b.runs,
                    )
                )
            if b.balls_faced < 0:
                issues.append(
                    InconsistencyIssue(
                        entity_type="BattingPerformance",
                        entity_id=b.id,
                        issue_code="NEGATIVE_BALLS",
                        message=f"Batting performance ID {b.id} has negative balls faced ({b.balls_faced}).",
                        severity="critical",
                        field_name="balls_faced",
                        invalid_value=b.balls_faced,
                    )
                )
            if b.fours is not None and b.sixes is not None:
                b_runs = (b.fours * 4) + (b.sixes * 6)
                if b_runs > b.runs:
                    issues.append(
                        InconsistencyIssue(
                            entity_type="BattingPerformance",
                            entity_id=b.id,
                            issue_code="BOUNDARY_RUNS_EXCEED_TOTAL",
                            message=f"Batting performance ID {b.id} boundary runs ({b_runs}) exceed total runs ({b.runs}).",
                            severity="critical",
                            field_name="fours/sixes",
                            invalid_value={"fours": b.fours, "sixes": b.sixes, "runs": b.runs},
                        )
                    )

        # 2. Scan Bowling Performances
        bowl_perfs = list(self.db.scalars(select(BowlingPerformance)).all())
        for bw in bowl_perfs:
            if bw.runs_conceded < 0:
                issues.append(
                    InconsistencyIssue(
                        entity_type="BowlingPerformance",
                        entity_id=bw.id,
                        issue_code="NEGATIVE_RUNS_CONCEDED",
                        message=f"Bowling performance ID {bw.id} has negative runs conceded ({bw.runs_conceded}).",
                        severity="critical",
                        field_name="runs_conceded",
                        invalid_value=bw.runs_conceded,
                    )
                )
            if bw.wickets < 0:
                issues.append(
                    InconsistencyIssue(
                        entity_type="BowlingPerformance",
                        entity_id=bw.id,
                        issue_code="NEGATIVE_WICKETS",
                        message=f"Bowling performance ID {bw.id} has negative wickets ({bw.wickets}).",
                        severity="critical",
                        field_name="wickets",
                        invalid_value=bw.wickets,
                    )
                )
            elif bw.wickets > 10:
                issues.append(
                    InconsistencyIssue(
                        entity_type="BowlingPerformance",
                        entity_id=bw.id,
                        issue_code="EXCESS_WICKETS",
                        message=f"Bowling performance ID {bw.id} has {bw.wickets} wickets (exceeds max 10).",
                        severity="critical",
                        field_name="wickets",
                        invalid_value=bw.wickets,
                    )
                )

        # 3. Scan Matches
        matches = list(self.db.scalars(select(Match)).all())
        for m in matches:
            t1 = getattr(m, "team_1_id", getattr(m, "team1_id", None))
            t2 = getattr(m, "team_2_id", getattr(m, "team2_id", None))
            if t1 and t2 and t1 == t2:
                issues.append(
                    InconsistencyIssue(
                        entity_type="Match",
                        entity_id=m.id,
                        issue_code="SAME_TEAM_MATCH",
                        message=f"Match ID {m.id} has identical team1 and team2 ID ({t1}).",
                        severity="critical",
                        field_name="team1_id/team2_id",
                        invalid_value=t1,
                    )
                )
            if m.winner_team_id and t1 and t2 and m.winner_team_id not in (t1, t2):
                issues.append(
                    InconsistencyIssue(
                        entity_type="Match",
                        entity_id=m.id,
                        issue_code="WINNER_TEAM_MISMATCH",
                        message=f"Match ID {m.id} winner team ID {m.winner_team_id} is not one of competing teams ({t1}, {t2}).",
                        severity="critical",
                        field_name="winner_team_id",
                        invalid_value=m.winner_team_id,
                    )
                )

        return issues


class ConsistencyChecker(ConsistencyEngine):
    """Bridge wrapper class providing standardized method signatures."""

    def check_all_consistency(self) -> List[ConsistencyIssue]:
        raw_issues = self.scan_all_database_records()
        converted: List[ConsistencyIssue] = []
        for i in raw_issues:
            converted.append(
                ConsistencyIssue(
                    entity=i.entity_type,
                    entity_id=i.entity_id or 0,
                    rule_broken=i.issue_code,
                    description=i.message,
                    severity="HIGH" if i.severity == "critical" else "MEDIUM"
                )
            )
        return converted

    def check_player_performance_consistency(self, player_id: int) -> List[ConsistencyIssue]:
        all_issues = self.check_all_consistency()
        # Filter for player performances if entity_id matches or player related
        return [i for i in all_issues if i.entity_id == player_id or "performance" in i.entity.lower()]
