"""
SuperScout Backend — Sample Player Dataset Ingestor

Example concrete ingestor implementing BaseIngestor for importing player datasets.
"""
from typing import Any, Dict, List, Tuple, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.player import Player
from app.models.enums import PlayerRole
from app.services.ingestion.base import BaseIngestor


class PlayerIngestor(BaseIngestor):
    def __init__(self):
        super().__init__(name="PlayerIngestor")

    def load_raw(self, source_input: Any) -> List[Dict[str, Any]]:
        """Load raw record dicts from input list or file."""
        if isinstance(source_input, list):
            return source_input
        raise ValueError("Source input must be a list of player dictionary records")

    def validate_record(self, record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate required player fields."""
        if not record.get("name") or not str(record.get("name")).strip():
            return False, "Player name is required"

        role_str = str(record.get("role", "batter")).lower().strip()
        valid_roles = [r.value for r in PlayerRole]
        if role_str not in valid_roles:
            return False, f"Invalid role '{role_str}'. Valid roles: {valid_roles}"

        return True, None

    def normalize_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize player record attributes."""
        role_str = str(record.get("role", "batter")).lower().strip()
        return {
            "name": str(record["name"]).strip(),
            "short_name": record.get("short_name", "").strip() or None,
            "role": PlayerRole(role_str),
            "batting_style": record.get("batting_style"),
            "bowling_style": record.get("bowling_style"),
            "nationality": record.get("nationality"),
            "is_active": record.get("is_active", True),
        }

    def is_duplicate(self, db: Session, record: Dict[str, Any]) -> bool:
        """Check for existing player by name and nationality."""
        stmt = select(Player).where(
            Player.name == record["name"],
            Player.nationality == record.get("nationality"),
        )
        return db.scalar(stmt) is not None

    def save_record(self, db: Session, record: Dict[str, Any]) -> Player:
        """Insert normalized player into DB."""
        player = Player(**record)
        db.add(player)
        db.commit()
        db.refresh(player)
        return player
