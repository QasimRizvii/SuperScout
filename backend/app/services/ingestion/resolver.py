"""
SuperScout Backend — Entity Resolution Engine

Safely resolves incoming entities (Players, Teams, Venues) against existing database records.
Uses a strict 4-stage resolution cascade:
1. Database ID lookup
2. External ID / Abbreviation lookup
3. Exact canonical name match
4. Case-insensitive normalized name match

Unsafe fuzzy merges are prohibited. Low-confidence records are flagged as unresolved.
"""
from datetime import date
from typing import Any, Optional, List
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.player import Player
from app.models.team import Team
from app.models.venue import Venue
from app.services.ingestion.normalizer import DataNormalizer


class EntityResolver:
    """
    Stateful entity resolver with memory caching for batch performance.
    """

    def __init__(self):
        # Local caches for resolution within session
        self._player_cache = {}
        self._team_cache = {}
        self._venue_cache = {}

    def clear_cache(self) -> None:
        """Reset internal lookup caches."""
        self._player_cache.clear()
        self._team_cache.clear()
        self._venue_cache.clear()

    def resolve_team(self, db: Session, identifier_or_name: Any, country: Optional[str] = None) -> Optional[Team]:
        """
        Resolve team using:
        1. Exact DB ID
        2. Exact Name
        3. Abbreviation
        4. Case-insensitive Name Match
        """
        if not identifier_or_name:
            return None

        # Check if integer ID supplied
        if isinstance(identifier_or_name, int) or (isinstance(identifier_or_name, str) and identifier_or_name.isdigit()):
            t_id = int(identifier_or_name)
            team = db.scalar(select(Team).where(Team.id == t_id))
            if team:
                return team

        clean_str = DataNormalizer.normalize_string(identifier_or_name)
        if not clean_str:
            return None

        cache_key = f"team:{clean_str.lower()}"
        if cache_key in self._team_cache:
            return self._team_cache[cache_key]

        # Stage 1: Exact name
        team = db.scalar(select(Team).where(Team.name == clean_str))
        if not team:
            # Stage 2: Abbreviation match
            team = db.scalar(select(Team).where(Team.abbreviation.ilike(clean_str)))
        if not team:
            # Stage 3: Case-insensitive name match
            team = db.scalar(select(Team).where(Team.name.ilike(clean_str)))
        if not team:
            # Stage 4: Short name match
            team = db.scalar(select(Team).where(Team.short_name.ilike(clean_str)))

        if team:
            self._team_cache[cache_key] = team
        return team

    def resolve_player(
        self,
        db: Session,
        identifier_or_name: Any,
        nationality: Optional[str] = None,
        dob: Optional[date] = None,
    ) -> Optional[Player]:
        """
        Resolve player using:
        1. Exact DB ID
        2. Name + Nationality exact match
        3. Exact Full Name match
        4. Case-insensitive Name Match
        """
        if not identifier_or_name:
            return None

        if isinstance(identifier_or_name, int) or (isinstance(identifier_or_name, str) and identifier_or_name.isdigit()):
            p_id = int(identifier_or_name)
            player = db.scalar(select(Player).where(Player.id == p_id))
            if player:
                return player

        clean_str = DataNormalizer.normalize_string(identifier_or_name)
        if not clean_str:
            return None

        cache_key = f"player:{clean_str.lower()}:{nationality or ''}"
        if cache_key in self._player_cache:
            return self._player_cache[cache_key]

        stmt = select(Player)
        player = None
        if nationality:
            # Stage 1: Name + Nationality exact
            exact_nat_stmt = stmt.where(
                Player.name.ilike(clean_str),
                Player.nationality.ilike(nationality),
            )
            player = db.scalar(exact_nat_stmt)

        if not player:
            # Stage 2: Exact Name match
            player = db.scalar(select(Player).where(Player.name == clean_str))

        if not player:
            # Stage 3: Case-insensitive name match
            players = list(db.scalars(select(Player).where(Player.name.ilike(clean_str))).all())
            if len(players) == 1:
                player = players[0]

        if not player:
            # Stage 4: Short name match
            players_short = list(db.scalars(select(Player).where(Player.short_name.ilike(clean_str))).all())
            if len(players_short) == 1:
                player = players_short[0]

        if player:
            self._player_cache[cache_key] = player
        return player

    def resolve_venue(self, db: Session, identifier_or_name: Any, city: Optional[str] = None) -> Optional[Venue]:
        """
        Resolve venue using:
        1. Exact DB ID
        2. Exact Name
        3. Name + City match
        4. Case-insensitive Name Match
        """
        if not identifier_or_name:
            return None

        if isinstance(identifier_or_name, int) or (isinstance(identifier_or_name, str) and identifier_or_name.isdigit()):
            v_id = int(identifier_or_name)
            venue = db.scalar(select(Venue).where(Venue.id == v_id))
            if venue:
                return venue

        clean_str = DataNormalizer.normalize_string(identifier_or_name)
        if not clean_str:
            return None

        cache_key = f"venue:{clean_str.lower()}:{city or ''}"
        if cache_key in self._venue_cache:
            return self._venue_cache[cache_key]

        venue = db.scalar(select(Venue).where(Venue.name == clean_str))
        if not venue:
            venue = db.scalar(select(Venue).where(Venue.name.ilike(clean_str)))

        if venue:
            self._venue_cache[cache_key] = venue
        return venue
