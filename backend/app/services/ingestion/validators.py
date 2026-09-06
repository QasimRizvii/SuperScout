"""
SuperScout Backend — Data Quality Validators

Validates cricket domain rules before persistence. Ensures clean error reporting without database exceptions.
"""
from typing import Any, Dict, Tuple, Optional
from app.services.ingestion.normalizer import DataNormalizer


class RecordValidator:
    """
    Cricket domain rules validator for raw/normalized dictionary records.
    """

    @staticmethod
    def validate_player(record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate Player record."""
        name = DataNormalizer.normalize_string(record.get("name"))
        if not name:
            return False, "Player 'name' is required and cannot be empty"
        return True, None

    @staticmethod
    def validate_team(record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate Team record."""
        name = DataNormalizer.normalize_string(record.get("name"))
        if not name:
            return False, "Team 'name' is required and cannot be empty"
        return True, None

    @staticmethod
    def validate_venue(record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate Venue record."""
        name = DataNormalizer.normalize_string(record.get("name"))
        if not name:
            return False, "Venue 'name' is required and cannot be empty"

        capacity = record.get("capacity")
        if capacity is not None:
            c_int = DataNormalizer.parse_int(capacity, default=-1)
            if c_int < 0:
                return False, f"Venue capacity cannot be negative (got {capacity})"

        lat = record.get("latitude")
        if lat is not None:
            l_flt = DataNormalizer.parse_float(lat)
            if l_flt is not None and not (-90.0 <= l_flt <= 90.0):
                return False, f"Venue latitude must be between -90 and 90 (got {lat})"

        lng = record.get("longitude")
        if lng is not None:
            g_flt = DataNormalizer.parse_float(lng)
            if g_flt is not None and not (-180.0 <= g_flt <= 180.0):
                return False, f"Venue longitude must be between -180 and 180 (got {lng})"

        return True, None

    @staticmethod
    def validate_match(record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate Match record."""
        season = DataNormalizer.normalize_string(record.get("season"))
        if not season:
            return False, "Match 'season' is required"

        match_date = DataNormalizer.parse_date(record.get("match_date"))
        if not match_date:
            return False, f"Match 'match_date' must be a valid date (got {record.get('match_date')})"

        # Verify teams presence
        t1 = record.get("team_1_id") or record.get("team_1_name") or record.get("team_1")
        t2 = record.get("team_2_id") or record.get("team_2_name") or record.get("team_2")
        if not t1 or not t2:
            return False, "Match requires both team_1 and team_2 references"

        return True, None

    @staticmethod
    def validate_innings(record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate Innings record."""
        innings_num = DataNormalizer.parse_int(record.get("innings_number"), default=0)
        if not (1 <= innings_num <= 4):
            return False, f"Innings number must be between 1 and 4 (got {innings_num})"

        total_runs = DataNormalizer.parse_int(record.get("total_runs"), default=0)
        if total_runs < 0:
            return False, f"Innings total_runs cannot be negative (got {total_runs})"

        wickets = DataNormalizer.parse_int(record.get("wickets"), default=0)
        if not (0 <= wickets <= 10):
            return False, f"Innings wickets must be between 0 and 10 (got {wickets})"

        overs = DataNormalizer.parse_float(record.get("overs"), default=0.0)
        if overs is not None and overs < 0.0:
            return False, f"Innings overs cannot be negative (got {overs})"

        extras = DataNormalizer.parse_int(record.get("extras"), default=0)
        if extras < 0:
            return False, f"Innings extras cannot be negative (got {extras})"

        return True, None

    @staticmethod
    def validate_batting_performance(record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate BattingPerformance record."""
        runs = DataNormalizer.parse_int(record.get("runs"), default=0)
        if runs < 0:
            return False, f"Batting runs cannot be negative (got {runs})"

        balls = DataNormalizer.parse_int(record.get("balls_faced"), default=0)
        if balls < 0:
            return False, f"Batting balls_faced cannot be negative (got {balls})"

        fours = DataNormalizer.parse_int(record.get("fours"), default=0)
        if fours < 0:
            return False, f"Batting fours cannot be negative (got {fours})"

        sixes = DataNormalizer.parse_int(record.get("sixes"), default=0)
        if sixes < 0:
            return False, f"Batting sixes cannot be negative (got {sixes})"

        dot_balls = DataNormalizer.parse_int(record.get("dot_balls"), default=0)
        if dot_balls < 0:
            return False, f"Batting dot_balls cannot be negative (got {dot_balls})"

        # Sensible check: boundary runs cannot exceed total runs
        boundary_runs = (fours * 4) + (sixes * 6)
        if boundary_runs > runs:
            return False, f"Boundary runs ({boundary_runs}) cannot exceed total runs ({runs})"

        return True, None

    @staticmethod
    def validate_bowling_performance(record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate BowlingPerformance record."""
        runs = DataNormalizer.parse_int(record.get("runs_conceded"), default=0)
        if runs < 0:
            return False, f"Bowling runs_conceded cannot be negative (got {runs})"

        wickets = DataNormalizer.parse_int(record.get("wickets"), default=0)
        if wickets < 0:
            return False, f"Bowling wickets cannot be negative (got {wickets})"

        maidens = DataNormalizer.parse_int(record.get("maidens"), default=0)
        if maidens < 0:
            return False, f"Bowling maidens cannot be negative (got {maidens})"

        overs = DataNormalizer.parse_float(record.get("overs"), default=0.0)
        if overs is not None and overs < 0.0:
            return False, f"Bowling overs cannot be negative (got {overs})"

        return True, None

    @staticmethod
    def validate_matchup(record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate PlayerMatchup record."""
        balls = DataNormalizer.parse_int(record.get("balls"), default=0)
        if balls < 0:
            return False, f"Matchup balls cannot be negative (got {balls})"

        runs = DataNormalizer.parse_int(record.get("runs"), default=0)
        if runs < 0:
            return False, f"Matchup runs cannot be negative (got {runs})"

        dismissals = DataNormalizer.parse_int(record.get("dismissals"), default=0)
        if dismissals < 0:
            return False, f"Matchup dismissals cannot be negative (got {dismissals})"

        return True, None
