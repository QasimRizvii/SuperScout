"""
SuperScout Backend — Scouting Exceptions
"""

class ScoutingError(Exception):
    """Base exception for scouting domain."""
    pass

class PlayerNotFoundError(ScoutingError):
    def __init__(self, player_id: int):
        self.player_id = player_id
        super().__init__(f"Player with ID {player_id} not found.")

class WatchlistNotFoundError(ScoutingError):
    def __init__(self, watchlist_id: int):
        self.watchlist_id = watchlist_id
        super().__init__(f"Watchlist entry with ID {watchlist_id} not found.")

class ScoutingNoteNotFoundError(ScoutingError):
    def __init__(self, note_id: int):
        self.note_id = note_id
        super().__init__(f"Scouting note with ID {note_id} not found.")

class InvalidScoutingFilterError(ScoutingError):
    def __init__(self, message: str):
        super().__init__(f"Invalid scouting filter: {message}")
