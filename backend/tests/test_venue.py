"""
Tests for Venue Entity Creation with Optional Pitch & Capacity Attributes
"""
from app.schemas.venue import VenueCreate
from app.services.venue_service import VenueService


def test_venue_creation_with_optional_fields(db_session):
    venue_in = VenueCreate(
        name="M. Chinnaswamy Stadium",
        city="Bengaluru",
        country="India",
        capacity=40000,
        pitch_type="Batting Friendly",
    )
    venue = VenueService.create_venue(db_session, venue_in)

    assert venue.id is not None
    assert venue.name == "M. Chinnaswamy Stadium"
    assert venue.capacity == 40000
    assert venue.pitch_type == "Batting Friendly"


def test_venue_creation_with_unknown_capacity(db_session):
    venue_in = VenueCreate(
        name="Unknown Oval",
        city="Unknown City",
        country="Unknown",
        capacity=None,
        pitch_type=None,
    )
    venue = VenueService.create_venue(db_session, venue_in)

    assert venue.id is not None
    assert venue.capacity is None
    assert venue.pitch_type is None
