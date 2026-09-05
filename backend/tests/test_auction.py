"""
Tests for Auction and AuctionTransaction Validations
"""
from datetime import date
import pytest
from pydantic import ValidationError

from app.models.enums import AuctionType, AuctionStatus
from app.models.auction import Auction, AuctionTransaction
from app.schemas.auction import AuctionTransactionBase, AuctionCreate
from app.services.auction_service import AuctionService


def test_auction_and_transaction_creation(db_session):
    auction_in = AuctionCreate(
        season="2024",
        auction_name="IPL 2024 Mega Auction",
        auction_date=date(2024, 2, 1),
        auction_type=AuctionType.MEGA,
    )
    auction = AuctionService.create_auction(db_session, auction_in)
    assert auction.id is not None
    assert auction.auction_type == AuctionType.MEGA

    tx = AuctionTransaction(
        auction_id=auction.id,
        player_id=1,
        team_id=1,
        base_price=2000000.0,
        final_price=12000000.0,
        status=AuctionStatus.SOLD,
    )
    db_session.add(tx)
    db_session.commit()
    assert tx.id is not None
    assert tx.status == AuctionStatus.SOLD


def test_auction_transaction_price_validation():
    # Negative prices must fail Pydantic schema validation
    with pytest.raises(ValidationError):
        AuctionTransactionBase(
            auction_id=1,
            player_id=1,
            base_price=-100.0,
            final_price=0.0,
        )
