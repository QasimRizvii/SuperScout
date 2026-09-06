"""
SuperScout Backend — Auction Intelligence Domain Exceptions
"""


class AuctionError(Exception):
    """Base exception for auction domain errors."""

    pass


class AuctionNotFoundError(AuctionError):
    """Raised when an auction is not found."""

    def __init__(self, auction_id: int):
        self.auction_id = auction_id
        super().__init__(f"Auction with ID '{auction_id}' was not found.")


class InvalidPurseError(AuctionError):
    """Raised when purse values are negative or invalid."""

    def __init__(self, purse: float):
        self.purse = purse
        super().__init__(f"Invalid purse value: ₹{purse} Lakhs. Purse cannot be negative.")


class ValuationError(AuctionError):
    """Raised when valuation calculation fails or missing critical data."""

    pass
