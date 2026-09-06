"""
SuperScout Backend — Data Normalization Layer

Provides robust normalization functions for player/team/venue names, cricket roles,
batting/bowling styles, match formats, ISO dates, and numeric values.
"""
import re
import unicodedata
from datetime import date, datetime
from typing import Any, Optional, Dict

from app.models.enums import PlayerRole, MatchType, DismissalType


class DataNormalizer:
    """
    Utility class for string, enum, and numeric field normalization.
    """

    @staticmethod
    def normalize_string(val: Optional[Any]) -> Optional[str]:
        """
        Clean whitespace, remove repeated internal spaces, handle unicode.

        Returns None for empty strings or null-like values.
        """
        if val is None:
            return None
        text = str(val).strip()
        if not text or text.lower() in ("null", "none", "nan", "undefined", ""):
            return None

        # Unicode normalization (NFC)
        text = unicodedata.normalize("NFC", text)
        # Collapse multiple spaces into single space
        text = re.sub(r"\s+", " ", text)
        return text

    @staticmethod
    def canonical_name(name: Optional[Any]) -> Optional[str]:
        """
        Derive lowercased, stripped, search-optimized representation.

        Example: " Virat   Kohli " -> "virat kohli"
        """
        clean = DataNormalizer.normalize_string(name)
        if not clean:
            return None
        return clean.lower()

    @staticmethod
    def parse_date(val: Optional[Any]) -> Optional[date]:
        """
        Parse date from date object, string ISO format (YYYY-MM-DD), or common date strings.
        """
        if val is None:
            return None
        if isinstance(val, date) and not isinstance(val, datetime):
            return val
        if isinstance(val, datetime):
            return val.date()

        clean_str = DataNormalizer.normalize_string(val)
        if not clean_str:
            return None

        # Try common date formats
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%B %d, %Y",
            "%d %B %Y",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(clean_str, fmt).date()
            except ValueError:
                continue

        return None

    @staticmethod
    def normalize_player_role(val: Optional[Any]) -> PlayerRole:
        """Map raw role string to valid PlayerRole enum."""
        clean = DataNormalizer.canonical_name(val)
        if not clean:
            return PlayerRole.BATTER

        role_mapping: Dict[str, PlayerRole] = {
            "batter": PlayerRole.BATTER,
            "batsman": PlayerRole.BATTER,
            "batting": PlayerRole.BATTER,
            "wicketkeeper_batter": PlayerRole.WICKETKEEPER_BATTER,
            "wicketkeeper-batter": PlayerRole.WICKETKEEPER_BATTER,
            "wk-batter": PlayerRole.WICKETKEEPER_BATTER,
            "wk batter": PlayerRole.WICKETKEEPER_BATTER,
            "all_rounder": PlayerRole.ALL_ROUNDER,
            "all rounder": PlayerRole.ALL_ROUNDER,
            "allrounder": PlayerRole.ALL_ROUNDER,
            "bowling_all_rounder": PlayerRole.BOWLING_ALL_ROUNDER,
            "bowling all-rounder": PlayerRole.BOWLING_ALL_ROUNDER,
            "fast_bowler": PlayerRole.FAST_BOWLER,
            "fast bowler": PlayerRole.FAST_BOWLER,
            "pacer": PlayerRole.FAST_BOWLER,
            "medium_fast_bowler": PlayerRole.MEDIUM_FAST_BOWLER,
            "medium fast": PlayerRole.MEDIUM_FAST_BOWLER,
            "spinner": PlayerRole.SPINNER,
            "spin bowler": PlayerRole.SPINNER,
            "wicketkeeper": PlayerRole.WICKETKEEPER,
            "keeper": PlayerRole.WICKETKEEPER,
            "bowler": PlayerRole.BOWLER,
        }

        return role_mapping.get(clean, PlayerRole.BATTER)

    @staticmethod
    def normalize_match_format(val: Optional[Any]) -> MatchType:
        """Map format string to MatchType enum."""
        clean = DataNormalizer.canonical_name(val)
        if not clean:
            return MatchType.T20

        if "t20" in clean or "twenty20" in clean or "ipl" in clean:
            return MatchType.T20
        if "odi" in clean or "one day" in clean:
            return MatchType.ODI
        if "test" in clean:
            return MatchType.TEST
        if "t10" in clean:
            return MatchType.T10
        return MatchType.OTHER

    @staticmethod
    def parse_int(val: Optional[Any], default: int = 0) -> int:
        """Safely convert value to integer."""
        if val is None:
            return default
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return default

    @staticmethod
    def parse_float(val: Optional[Any], default: Optional[float] = None) -> Optional[float]:
        """Safely convert value to float."""
        if val is None:
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def parse_bool(val: Optional[Any], default: bool = True) -> bool:
        """Safely convert value to boolean."""
        if val is None:
            return default
        if isinstance(val, bool):
            return val
        s = str(val).strip().lower()
        if s in ("true", "1", "yes", "y", "t"):
            return True
        if s in ("false", "0", "no", "n", "f"):
            return False
        return default
