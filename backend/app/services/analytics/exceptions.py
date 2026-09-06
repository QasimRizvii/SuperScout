"""
SuperScout Backend — Analytics Domain Exceptions
"""


class AnalyticsError(Exception):
    """Base exception for analytics errors."""

    pass


class PlayerNotFoundError(AnalyticsError):
    """Raised when a player is not found in database."""

    def __init__(self, player_id: int):
        self.player_id = player_id
        super().__init__(f"Player with ID '{player_id}' was not found.")


class InsufficientDataError(AnalyticsError):
    """Raised when data is insufficient for a statistical metric."""

    def __init__(self, message: str, sample_size: int = 0):
        self.sample_size = sample_size
        super().__init__(message)


class InvalidComparisonError(AnalyticsError):
    """Raised when comparison constraints are violated (e.g., <2 or >5 players)."""

    pass
