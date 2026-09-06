"""
SuperScout Backend — Squad Intelligence Domain Exceptions
"""


class SquadError(Exception):
    """Base exception for squad domain errors."""

    pass


class SquadNotFoundError(SquadError):
    """Raised when a team or squad is not found."""

    def __init__(self, team_id: int):
        self.team_id = team_id
        super().__init__(f"Squad/Team with ID '{team_id}' was not found.")


class InsufficientSquadSizeError(SquadError):
    """Raised when squad size is insufficient for analysis or Playing XI (e.g. <11 players)."""

    def __init__(self, squad_size: int, minimum_required: int = 11):
        self.squad_size = squad_size
        self.minimum_required = minimum_required
        super().__init__(
            f"Squad size ({squad_size}) is insufficient. Minimum required is {minimum_required}."
        )


class OptimizationError(SquadError):
    """Raised when Playing XI optimization fails to satisfy core constraints."""

    pass
