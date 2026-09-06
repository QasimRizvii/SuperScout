"""
SuperScout Backend — Transaction-Safe Database Loader

Handles single-entity & multi-entity database loads with batching,
dry-run support, duplicate detection, and automatic transaction rollback on failure.
"""
import time
from typing import Any, Dict, List, Optional, Callable
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.models.player import Player
from app.models.team import Team
from app.models.venue import Venue
from app.models.match import Match
from app.models.innings import Innings
from app.models.batting import BattingPerformance
from app.models.bowling import BowlingPerformance
from app.models.matchup import PlayerMatchup

from app.services.ingestion.schemas import IngestionReport, RecordStatus
from app.services.ingestion.normalizer import DataNormalizer
from app.services.ingestion.validators import RecordValidator
from app.services.ingestion.resolver import EntityResolver


class DatabaseLoader:
    """
    Transaction-safe loader executing 5-stage ingestion pipeline:
    Load -> Validate -> Normalize -> Resolve / Duplicate Check -> Persist
    """

    def __init__(self, resolver: Optional[EntityResolver] = None, is_dry_run: bool = False, batch_size: int = 500):
        self.resolver = resolver or EntityResolver()
        self.is_dry_run = is_dry_run
        self.batch_size = batch_size

    def load_teams(self, db: Session, raw_records: List[Dict[str, Any]], source_name: str = "teams") -> IngestionReport:
        report = IngestionReport(ingestor_name="TeamLoader", source_name=source_name, is_dry_run=self.is_dry_run)
        start_time = time.time()
        report.total_records = len(raw_records)
        report.records_loaded = len(raw_records)

        try:
            for idx, raw in enumerate(raw_records):
                rec_id = str(raw.get("id") or raw.get("name") or f"row_{idx}")

                # 1. Validate
                valid, err = RecordValidator.validate_team(raw)
                if not valid:
                    report.add_issue(rec_id, RecordStatus.INVALID, err or "Invalid team record", raw)
                    continue
                report.records_validated += 1

                # 2. Normalize
                name = DataNormalizer.normalize_string(raw.get("name"))
                short_name = DataNormalizer.normalize_string(raw.get("short_name"))
                abbreviation = DataNormalizer.normalize_string(raw.get("abbreviation"))
                city = DataNormalizer.normalize_string(raw.get("city"))
                country = DataNormalizer.normalize_string(raw.get("country"))
                team_type = DataNormalizer.normalize_string(raw.get("team_type")) or "franchise"
                logo_url = DataNormalizer.normalize_string(raw.get("logo_url"))
                is_active = DataNormalizer.parse_bool(raw.get("is_active"), True)

                # 3. Duplicate check
                existing = self.resolver.resolve_team(db, name)
                if existing:
                    report.add_issue(rec_id, RecordStatus.DUPLICATE, f"Team '{name}' already exists (ID {existing.id})", raw)
                    continue

                # 4. Save
                if not self.is_dry_run:
                    team = Team(
                        name=name,
                        short_name=short_name,
                        abbreviation=abbreviation,
                        city=city,
                        country=country,
                        team_type=team_type,
                        logo_url=logo_url,
                        is_active=is_active,
                    )
                    db.add(team)
                    db.flush()
                report.records_inserted += 1

            if not self.is_dry_run:
                db.commit()

        except Exception as exc:
            db.rollback()
            report.status = "failed"
            report.add_issue("FATAL_LOAD_ERROR", RecordStatus.INVALID, f"Transaction rolled back: {str(exc)}")
        finally:
            report.duration_seconds = round(time.time() - start_time, 4)

        return report

    def load_players(self, db: Session, raw_records: List[Dict[str, Any]], source_name: str = "players") -> IngestionReport:
        report = IngestionReport(ingestor_name="PlayerLoader", source_name=source_name, is_dry_run=self.is_dry_run)
        start_time = time.time()
        report.total_records = len(raw_records)
        report.records_loaded = len(raw_records)

        try:
            for idx, raw in enumerate(raw_records):
                rec_id = str(raw.get("id") or raw.get("name") or f"row_{idx}")

                # 1. Validate
                valid, err = RecordValidator.validate_player(raw)
                if not valid:
                    report.add_issue(rec_id, RecordStatus.INVALID, err or "Invalid player record", raw)
                    continue
                report.records_validated += 1

                # 2. Normalize
                name = DataNormalizer.normalize_string(raw.get("name"))
                short_name = DataNormalizer.normalize_string(raw.get("short_name"))
                role = DataNormalizer.normalize_player_role(raw.get("role"))
                batting_style = DataNormalizer.normalize_string(raw.get("batting_style"))
                bowling_style = DataNormalizer.normalize_string(raw.get("bowling_style"))
                nationality = DataNormalizer.normalize_string(raw.get("nationality"))
                dob = DataNormalizer.parse_date(raw.get("date_of_birth"))
                is_wicketkeeper = DataNormalizer.parse_bool(raw.get("is_wicketkeeper"), False)
                profile_image_url = DataNormalizer.normalize_string(raw.get("profile_image_url"))
                is_active = DataNormalizer.parse_bool(raw.get("is_active"), True)

                # 3. Duplicate check
                existing = self.resolver.resolve_player(db, name, nationality=nationality, dob=dob)
                if existing:
                    report.add_issue(rec_id, RecordStatus.DUPLICATE, f"Player '{name}' already exists (ID {existing.id})", raw)
                    continue

                # 4. Save
                if not self.is_dry_run:
                    player = Player(
                        name=name,
                        short_name=short_name,
                        role=role,
                        batting_style=batting_style,
                        bowling_style=bowling_style,
                        nationality=nationality,
                        date_of_birth=dob,
                        is_wicketkeeper=is_wicketkeeper,
                        profile_image_url=profile_image_url,
                        is_active=is_active,
                    )
                    db.add(player)
                    db.flush()
                report.records_inserted += 1

            if not self.is_dry_run:
                db.commit()

        except Exception as exc:
            db.rollback()
            report.status = "failed"
            report.add_issue("FATAL_LOAD_ERROR", RecordStatus.INVALID, f"Transaction rolled back: {str(exc)}")
        finally:
            report.duration_seconds = round(time.time() - start_time, 4)

        return report

    def load_venues(self, db: Session, raw_records: List[Dict[str, Any]], source_name: str = "venues") -> IngestionReport:
        report = IngestionReport(ingestor_name="VenueLoader", source_name=source_name, is_dry_run=self.is_dry_run)
        start_time = time.time()
        report.total_records = len(raw_records)
        report.records_loaded = len(raw_records)

        try:
            for idx, raw in enumerate(raw_records):
                rec_id = str(raw.get("id") or raw.get("name") or f"row_{idx}")

                # 1. Validate
                valid, err = RecordValidator.validate_venue(raw)
                if not valid:
                    report.add_issue(rec_id, RecordStatus.INVALID, err or "Invalid venue record", raw)
                    continue
                report.records_validated += 1

                # 2. Normalize
                name = DataNormalizer.normalize_string(raw.get("name"))
                city = DataNormalizer.normalize_string(raw.get("city"))
                country = DataNormalizer.normalize_string(raw.get("country"))
                capacity = DataNormalizer.parse_int(raw.get("capacity")) if raw.get("capacity") is not None else None
                pitch_type = DataNormalizer.normalize_string(raw.get("pitch_type"))
                latitude = DataNormalizer.parse_float(raw.get("latitude"))
                longitude = DataNormalizer.parse_float(raw.get("longitude"))
                timezone = DataNormalizer.normalize_string(raw.get("timezone"))

                # 3. Duplicate check
                existing = self.resolver.resolve_venue(db, name, city=city)
                if existing:
                    report.add_issue(rec_id, RecordStatus.DUPLICATE, f"Venue '{name}' already exists (ID {existing.id})", raw)
                    continue

                # 4. Save
                if not self.is_dry_run:
                    venue = Venue(
                        name=name,
                        city=city,
                        country=country,
                        capacity=capacity,
                        pitch_type=pitch_type,
                        latitude=latitude,
                        longitude=longitude,
                        timezone=timezone,
                    )
                    db.add(venue)
                    db.flush()
                report.records_inserted += 1

            if not self.is_dry_run:
                db.commit()

        except Exception as exc:
            db.rollback()
            report.status = "failed"
            report.add_issue("FATAL_LOAD_ERROR", RecordStatus.INVALID, f"Transaction rolled back: {str(exc)}")
        finally:
            report.duration_seconds = round(time.time() - start_time, 4)

        return report

    def load_matches(self, db: Session, raw_records: List[Dict[str, Any]], source_name: str = "matches") -> IngestionReport:
        report = IngestionReport(ingestor_name="MatchLoader", source_name=source_name, is_dry_run=self.is_dry_run)
        start_time = time.time()
        report.total_records = len(raw_records)
        report.records_loaded = len(raw_records)

        try:
            for idx, raw in enumerate(raw_records):
                rec_id = str(raw.get("id") or raw.get("external_id") or f"row_{idx}")

                # 1. Validate
                valid, err = RecordValidator.validate_match(raw)
                if not valid:
                    report.add_issue(rec_id, RecordStatus.INVALID, err or "Invalid match record", raw)
                    continue
                report.records_validated += 1

                # 2. Resolve Foreign Entities
                t1_ident = raw.get("team_1_id") or raw.get("team_1_name") or raw.get("team_1")
                team_1 = self.resolver.resolve_team(db, t1_ident)
                if not team_1:
                    report.add_issue(rec_id, RecordStatus.UNRESOLVED, f"Could not resolve team 1 '{t1_ident}'", raw)
                    continue

                t2_ident = raw.get("team_2_id") or raw.get("team_2_name") or raw.get("team_2")
                team_2 = self.resolver.resolve_team(db, t2_ident)
                if not team_2:
                    report.add_issue(rec_id, RecordStatus.UNRESOLVED, f"Could not resolve team 2 '{t2_ident}'", raw)
                    continue

                v_ident = raw.get("venue_id") or raw.get("venue_name") or raw.get("venue")
                venue = self.resolver.resolve_venue(db, v_ident)
                if not venue:
                    report.add_issue(rec_id, RecordStatus.UNRESOLVED, f"Could not resolve venue '{v_ident}'", raw)
                    continue

                winner_ident = raw.get("winner_team_id") or raw.get("winner_team_name") or raw.get("winner_team")
                winner_team = self.resolver.resolve_team(db, winner_ident) if winner_ident else None

                toss_winner_ident = raw.get("toss_winner_id") or raw.get("toss_winner_name") or raw.get("toss_winner")
                toss_winner = self.resolver.resolve_team(db, toss_winner_ident) if toss_winner_ident else None

                # 3. Normalize fields
                ext_id = DataNormalizer.normalize_string(raw.get("external_id"))
                season = DataNormalizer.normalize_string(raw.get("season"))
                match_date = DataNormalizer.parse_date(raw.get("match_date"))
                match_type = DataNormalizer.normalize_match_format(raw.get("match_type") or raw.get("format"))
                competition = DataNormalizer.normalize_string(raw.get("competition"))
                status = DataNormalizer.normalize_string(raw.get("status")) or "completed"
                toss_decision = DataNormalizer.normalize_string(raw.get("toss_decision"))
                result_desc = DataNormalizer.normalize_string(raw.get("result_description"))

                # 4. Duplicate check (by external_id or date + venue + team1 + team2)
                existing = None
                if ext_id:
                    existing = db.scalar(select(Match).where(Match.external_id == ext_id))
                if not existing:
                    existing = db.scalar(
                        select(Match).where(
                            Match.match_date == match_date,
                            Match.venue_id == venue.id,
                            or_(
                                Match.team_1_id == team_1.id,
                                Match.team_2_id == team_1.id,
                            ),
                            or_(
                                Match.team_1_id == team_2.id,
                                Match.team_2_id == team_2.id,
                            ),
                        )
                    )

                if existing:
                    report.add_issue(rec_id, RecordStatus.DUPLICATE, f"Match already exists (ID {existing.id})", raw)
                    continue

                # 5. Save
                if not self.is_dry_run:
                    match = Match(
                        external_id=ext_id,
                        season=season,
                        match_date=match_date,
                        match_type=match_type,
                        competition=competition,
                        status=status,
                        venue_id=venue.id,
                        team_1_id=team_1.id,
                        team_2_id=team_2.id,
                        winner_team_id=winner_team.id if winner_team else None,
                        toss_winner_id=toss_winner.id if toss_winner else None,
                        toss_decision=toss_decision,
                        result_description=result_desc,
                    )
                    db.add(match)
                    db.flush()
                report.records_inserted += 1

            if not self.is_dry_run:
                db.commit()

        except Exception as exc:
            db.rollback()
            report.status = "failed"
            report.add_issue("FATAL_LOAD_ERROR", RecordStatus.INVALID, f"Transaction rolled back: {str(exc)}")
        finally:
            report.duration_seconds = round(time.time() - start_time, 4)

        return report

    def load_innings(self, db: Session, raw_records: List[Dict[str, Any]], source_name: str = "innings") -> IngestionReport:
        report = IngestionReport(ingestor_name="InningsLoader", source_name=source_name, is_dry_run=self.is_dry_run)
        start_time = time.time()
        report.total_records = len(raw_records)
        report.records_loaded = len(raw_records)

        try:
            for idx, raw in enumerate(raw_records):
                rec_id = str(raw.get("id") or f"row_{idx}")

                # 1. Validate
                valid, err = RecordValidator.validate_innings(raw)
                if not valid:
                    report.add_issue(rec_id, RecordStatus.INVALID, err or "Invalid innings record", raw)
                    continue
                report.records_validated += 1

                # 2. Resolve parent Match & Teams
                match_ident = raw.get("match_id") or raw.get("match_external_id")
                match = None
                if isinstance(match_ident, int) or (isinstance(match_ident, str) and match_ident.isdigit()):
                    match = db.scalar(select(Match).where(Match.id == int(match_ident)))
                elif isinstance(match_ident, str):
                    match = db.scalar(select(Match).where(Match.external_id == match_ident))

                if not match:
                    report.add_issue(rec_id, RecordStatus.UNRESOLVED, f"Could not resolve match '{match_ident}'", raw)
                    continue

                batting_team = self.resolver.resolve_team(db, raw.get("batting_team_id") or raw.get("batting_team"))
                bowling_team = self.resolver.resolve_team(db, raw.get("bowling_team_id") or raw.get("bowling_team"))

                if not batting_team or not bowling_team:
                    report.add_issue(rec_id, RecordStatus.UNRESOLVED, "Could not resolve batting or bowling team", raw)
                    continue

                # 3. Duplicate check by unique constraint (match_id, innings_number)
                innings_num = DataNormalizer.parse_int(raw.get("innings_number"))
                existing = db.scalar(
                    select(Innings).where(
                        Innings.match_id == match.id,
                        Innings.innings_number == innings_num,
                    )
                )

                if existing:
                    report.add_issue(rec_id, RecordStatus.DUPLICATE, f"Innings {innings_num} for match {match.id} already exists", raw)
                    continue

                # 4. Save
                if not self.is_dry_run:
                    total_runs = DataNormalizer.parse_int(raw.get("total_runs"), 0)
                    wickets = DataNormalizer.parse_int(raw.get("wickets"), 0)
                    overs = DataNormalizer.parse_float(raw.get("overs"), 0.0) or 0.0
                    extras = DataNormalizer.parse_int(raw.get("extras"), 0)
                    powerplay = DataNormalizer.parse_int(raw.get("powerplay_runs")) if raw.get("powerplay_runs") is not None else None
                    rr = round(total_runs / overs, 2) if overs > 0 else None

                    innings = Innings(
                        match_id=match.id,
                        innings_number=innings_num,
                        batting_team_id=batting_team.id,
                        bowling_team_id=bowling_team.id,
                        total_runs=total_runs,
                        wickets=wickets,
                        overs=overs,
                        run_rate=rr,
                        extras=extras,
                        powerplay_runs=powerplay,
                    )
                    db.add(innings)
                    db.flush()
                report.records_inserted += 1

            if not self.is_dry_run:
                db.commit()

        except Exception as exc:
            db.rollback()
            report.status = "failed"
            report.add_issue("FATAL_LOAD_ERROR", RecordStatus.INVALID, f"Transaction rolled back: {str(exc)}")
        finally:
            report.duration_seconds = round(time.time() - start_time, 4)

        return report

    def load_batting_performances(self, db: Session, raw_records: List[Dict[str, Any]], source_name: str = "batting_performances") -> IngestionReport:
        report = IngestionReport(ingestor_name="BattingPerformanceLoader", source_name=source_name, is_dry_run=self.is_dry_run)
        start_time = time.time()
        report.total_records = len(raw_records)
        report.records_loaded = len(raw_records)

        try:
            for idx, raw in enumerate(raw_records):
                rec_id = str(raw.get("id") or f"row_{idx}")

                # 1. Validate
                valid, err = RecordValidator.validate_batting_performance(raw)
                if not valid:
                    report.add_issue(rec_id, RecordStatus.INVALID, err or "Invalid batting record", raw)
                    continue
                report.records_validated += 1

                # 2. Resolve entities
                player = self.resolver.resolve_player(db, raw.get("player_id") or raw.get("player_name") or raw.get("player"))
                if not player:
                    report.add_issue(rec_id, RecordStatus.UNRESOLVED, f"Could not resolve player '{raw.get('player_name') or raw.get('player')}'", raw)
                    continue

                team = self.resolver.resolve_team(db, raw.get("team_id") or raw.get("team_name") or raw.get("team"))
                if not team:
                    report.add_issue(rec_id, RecordStatus.UNRESOLVED, f"Could not resolve team '{raw.get('team')}'", raw)
                    continue

                match_ident = raw.get("match_id") or raw.get("match_external_id")
                match = None
                if isinstance(match_ident, int) or (isinstance(match_ident, str) and match_ident.isdigit()):
                    match = db.scalar(select(Match).where(Match.id == int(match_ident)))
                elif isinstance(match_ident, str):
                    match = db.scalar(select(Match).where(Match.external_id == match_ident))

                if not match:
                    report.add_issue(rec_id, RecordStatus.UNRESOLVED, f"Could not resolve match '{match_ident}'", raw)
                    continue

                innings_num = DataNormalizer.parse_int(raw.get("innings_number"), 1)
                innings = db.scalar(select(Innings).where(Innings.match_id == match.id, Innings.innings_number == innings_num))
                if not innings:
                    report.add_issue(rec_id, RecordStatus.UNRESOLVED, f"Could not resolve innings {innings_num} for match {match.id}", raw)
                    continue

                dismissed_by = self.resolver.resolve_player(db, raw.get("dismissed_by_player_id") or raw.get("bowler_name")) if raw.get("bowler_name") else None
                fielder = self.resolver.resolve_player(db, raw.get("fielder_player_id") or raw.get("fielder_name")) if raw.get("fielder_name") else None

                # 3. Duplicate check
                existing = db.scalar(
                    select(BattingPerformance).where(
                        BattingPerformance.match_id == match.id,
                        BattingPerformance.innings_id == innings.id,
                        BattingPerformance.player_id == player.id,
                    )
                )

                if existing:
                    report.add_issue(rec_id, RecordStatus.DUPLICATE, f"Batting record for player {player.name} in match {match.id} already exists", raw)
                    continue

                # 4. Save
                if not self.is_dry_run:
                    runs = DataNormalizer.parse_int(raw.get("runs"), 0)
                    balls = DataNormalizer.parse_int(raw.get("balls_faced"), 0)
                    fours = DataNormalizer.parse_int(raw.get("fours"), 0)
                    sixes = DataNormalizer.parse_int(raw.get("sixes"), 0)
                    dot_balls = DataNormalizer.parse_int(raw.get("dot_balls"), 0)
                    sr = BattingPerformance.calculate_strike_rate(runs, balls)

                    batting = BattingPerformance(
                        match_id=match.id,
                        innings_id=innings.id,
                        player_id=player.id,
                        team_id=team.id,
                        batting_position=DataNormalizer.parse_int(raw.get("batting_position")) if raw.get("batting_position") else None,
                        runs=runs,
                        balls_faced=balls,
                        fours=fours,
                        sixes=sixes,
                        dot_balls=dot_balls,
                        runs_powerplay=DataNormalizer.parse_int(raw.get("runs_powerplay")) if raw.get("runs_powerplay") is not None else None,
                        runs_middle=DataNormalizer.parse_int(raw.get("runs_middle")) if raw.get("runs_middle") is not None else None,
                        runs_death=DataNormalizer.parse_int(raw.get("runs_death")) if raw.get("runs_death") is not None else None,
                        strike_rate=sr,
                        dismissal_type=DataNormalizer.normalize_string(raw.get("dismissal_type")),
                        dismissed_by_player_id=dismissed_by.id if dismissed_by else None,
                        fielder_player_id=fielder.id if fielder else None,
                    )
                    db.add(batting)
                    db.flush()
                report.records_inserted += 1

            if not self.is_dry_run:
                db.commit()

        except Exception as exc:
            db.rollback()
            report.status = "failed"
            report.add_issue("FATAL_LOAD_ERROR", RecordStatus.INVALID, f"Transaction rolled back: {str(exc)}")
        finally:
            report.duration_seconds = round(time.time() - start_time, 4)

        return report

    def load_bowling_performances(self, db: Session, raw_records: List[Dict[str, Any]], source_name: str = "bowling_performances") -> IngestionReport:
        report = IngestionReport(ingestor_name="BowlingPerformanceLoader", source_name=source_name, is_dry_run=self.is_dry_run)
        start_time = time.time()
        report.total_records = len(raw_records)
        report.records_loaded = len(raw_records)

        try:
            for idx, raw in enumerate(raw_records):
                rec_id = str(raw.get("id") or f"row_{idx}")

                # 1. Validate
                valid, err = RecordValidator.validate_bowling_performance(raw)
                if not valid:
                    report.add_issue(rec_id, RecordStatus.INVALID, err or "Invalid bowling record", raw)
                    continue
                report.records_validated += 1

                # 2. Resolve entities
                player = self.resolver.resolve_player(db, raw.get("player_id") or raw.get("player_name") or raw.get("player"))
                if not player:
                    report.add_issue(rec_id, RecordStatus.UNRESOLVED, f"Could not resolve bowler '{raw.get('player_name') or raw.get('player')}'", raw)
                    continue

                team = self.resolver.resolve_team(db, raw.get("team_id") or raw.get("team_name") or raw.get("team"))
                if not team:
                    report.add_issue(rec_id, RecordStatus.UNRESOLVED, f"Could not resolve team '{raw.get('team')}'", raw)
                    continue

                match_ident = raw.get("match_id") or raw.get("match_external_id")
                match = None
                if isinstance(match_ident, int) or (isinstance(match_ident, str) and match_ident.isdigit()):
                    match = db.scalar(select(Match).where(Match.id == int(match_ident)))
                elif isinstance(match_ident, str):
                    match = db.scalar(select(Match).where(Match.external_id == match_ident))

                if not match:
                    report.add_issue(rec_id, RecordStatus.UNRESOLVED, f"Could not resolve match '{match_ident}'", raw)
                    continue

                innings_num = DataNormalizer.parse_int(raw.get("innings_number"), 1)
                innings = db.scalar(select(Innings).where(Innings.match_id == match.id, Innings.innings_number == innings_num))
                if not innings:
                    report.add_issue(rec_id, RecordStatus.UNRESOLVED, f"Could not resolve innings {innings_num} for match {match.id}", raw)
                    continue

                # 3. Duplicate check
                existing = db.scalar(
                    select(BowlingPerformance).where(
                        BowlingPerformance.match_id == match.id,
                        BowlingPerformance.innings_id == innings.id,
                        BowlingPerformance.player_id == player.id,
                    )
                )

                if existing:
                    report.add_issue(rec_id, RecordStatus.DUPLICATE, f"Bowling record for player {player.name} in match {match.id} already exists", raw)
                    continue

                # 4. Save
                if not self.is_dry_run:
                    runs = DataNormalizer.parse_int(raw.get("runs_conceded"), 0)
                    balls = DataNormalizer.parse_int(raw.get("balls_bowled"), 0)
                    overs = DataNormalizer.parse_float(raw.get("overs"), 0.0) or 0.0
                    wickets = DataNormalizer.parse_int(raw.get("wickets"), 0)
                    maidens = DataNormalizer.parse_int(raw.get("maidens"), 0)
                    wides = DataNormalizer.parse_int(raw.get("wides"), 0)
                    no_balls = DataNormalizer.parse_int(raw.get("no_balls"), 0)
                    dot_balls = DataNormalizer.parse_int(raw.get("dot_balls"), 0)
                    econ = BowlingPerformance.calculate_economy(runs, balls, overs)

                    bowling = BowlingPerformance(
                        match_id=match.id,
                        innings_id=innings.id,
                        player_id=player.id,
                        team_id=team.id,
                        bowling_position=DataNormalizer.parse_int(raw.get("bowling_position")) if raw.get("bowling_position") else None,
                        overs=overs,
                        balls_bowled=balls,
                        maidens=maidens,
                        runs_conceded=runs,
                        wickets=wickets,
                        wides=wides,
                        no_balls=no_balls,
                        dot_balls=dot_balls,
                        overs_powerplay=DataNormalizer.parse_float(raw.get("overs_powerplay")),
                        overs_middle=DataNormalizer.parse_float(raw.get("overs_middle")),
                        overs_death=DataNormalizer.parse_float(raw.get("overs_death")),
                        economy=econ,
                    )
                    db.add(bowling)
                    db.flush()
                report.records_inserted += 1

            if not self.is_dry_run:
                db.commit()

        except Exception as exc:
            db.rollback()
            report.status = "failed"
            report.add_issue("FATAL_LOAD_ERROR", RecordStatus.INVALID, f"Transaction rolled back: {str(exc)}")
        finally:
            report.duration_seconds = round(time.time() - start_time, 4)

        return report

    def load_matchups(self, db: Session, raw_records: List[Dict[str, Any]], source_name: str = "matchups") -> IngestionReport:
        report = IngestionReport(ingestor_name="MatchupLoader", source_name=source_name, is_dry_run=self.is_dry_run)
        start_time = time.time()
        report.total_records = len(raw_records)
        report.records_loaded = len(raw_records)

        try:
            for idx, raw in enumerate(raw_records):
                rec_id = str(raw.get("id") or f"row_{idx}")

                # 1. Validate
                valid, err = RecordValidator.validate_matchup(raw)
                if not valid:
                    report.add_issue(rec_id, RecordStatus.INVALID, err or "Invalid matchup record", raw)
                    continue
                report.records_validated += 1

                # 2. Resolve Players
                batter = self.resolver.resolve_player(db, raw.get("batter_id") or raw.get("batter_name") or raw.get("batter"))
                bowler = self.resolver.resolve_player(db, raw.get("bowler_id") or raw.get("bowler_name") or raw.get("bowler"))

                if not batter or not bowler:
                    report.add_issue(rec_id, RecordStatus.UNRESOLVED, f"Could not resolve batter '{raw.get('batter_name')}' or bowler '{raw.get('bowler_name')}'", raw)
                    continue

                # 3. Duplicate check by unique (batter_id, bowler_id)
                existing = db.scalar(
                    select(PlayerMatchup).where(
                        PlayerMatchup.batter_id == batter.id,
                        PlayerMatchup.bowler_id == bowler.id,
                    )
                )

                if existing:
                    report.add_issue(rec_id, RecordStatus.DUPLICATE, f"Matchup between {batter.name} and {bowler.name} already exists (ID {existing.id})", raw)
                    continue

                # 4. Save
                if not self.is_dry_run:
                    matches_cnt = DataNormalizer.parse_int(raw.get("matches"), 1)
                    balls = DataNormalizer.parse_int(raw.get("balls"), 0)
                    runs = DataNormalizer.parse_int(raw.get("runs"), 0)
                    dismissals = DataNormalizer.parse_int(raw.get("dismissals"), 0)
                    fours = DataNormalizer.parse_int(raw.get("fours"), 0)
                    sixes = DataNormalizer.parse_int(raw.get("sixes"), 0)
                    dot_balls = DataNormalizer.parse_int(raw.get("dot_balls"), 0)
                    sr = PlayerMatchup.calculate_strike_rate(runs, balls)
                    avg = PlayerMatchup.calculate_average(runs, dismissals)
                    boundary_pct = round(((fours * 4 + sixes * 6) / runs) * 100.0, 2) if runs > 0 else 0.0

                    matchup = PlayerMatchup(
                        batter_id=batter.id,
                        bowler_id=bowler.id,
                        matches=matches_cnt,
                        balls=balls,
                        runs=runs,
                        dismissals=dismissals,
                        fours=fours,
                        sixes=sixes,
                        dot_balls=dot_balls,
                        strike_rate=sr,
                        average=avg,
                        boundary_percentage=boundary_pct,
                    )
                    db.add(matchup)
                    db.flush()
                report.records_inserted += 1

            if not self.is_dry_run:
                db.commit()

        except Exception as exc:
            db.rollback()
            report.status = "failed"
            report.add_issue("FATAL_LOAD_ERROR", RecordStatus.INVALID, f"Transaction rolled back: {str(exc)}")
        finally:
            report.duration_seconds = round(time.time() - start_time, 4)

        return report
