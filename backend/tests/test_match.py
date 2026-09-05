"""
Tests for Match Entity Creation and Innings Unique Constraints
"""
from datetime import date
import pytest
from sqlalchemy.exc import IntegrityError

from app.models.enums import MatchType
from app.models.innings import Innings
from app.schemas.team import TeamCreate
from app.schemas.venue import VenueCreate
from app.schemas.match import MatchCreate
from app.services.team_service import TeamService
from app.services.venue_service import VenueService
from app.services.match_service import MatchService


def test_match_and_innings_creation(db_session):
    team1 = TeamService.create_team(db_session, TeamCreate(name="Team A", abbreviation="TA"))
    team2 = TeamService.create_team(db_session, TeamCreate(name="Team B", abbreviation="TB"))
    venue = VenueService.create_venue(db_session, VenueCreate(name="Stadium A"))

    match_in = MatchCreate(
        season="2024",
        match_date=date(2024, 4, 1),
        match_type=MatchType.T20,
        venue_id=venue.id,
        team_1_id=team1.id,
        team_2_id=team2.id,
        winner_team_id=team1.id,
        result_description="Team A won by 10 runs",
    )
    match = MatchService.create_match(db_session, match_in)

    assert match.id is not None
    assert match.winner_team_id == team1.id

    innings1 = Innings(
        match_id=match.id,
        innings_number=1,
        batting_team_id=team1.id,
        bowling_team_id=team2.id,
        total_runs=180,
        wickets=5,
        overs=20.0,
    )
    db_session.add(innings1)
    db_session.commit()
    assert innings1.id is not None


def test_innings_unique_constraint(db_session):
    team1 = TeamService.create_team(db_session, TeamCreate(name="Team C", abbreviation="TC"))
    team2 = TeamService.create_team(db_session, TeamCreate(name="Team D", abbreviation="TD"))
    venue = VenueService.create_venue(db_session, VenueCreate(name="Stadium B"))

    match = MatchService.create_match(
        db_session,
        MatchCreate(
            season="2024",
            match_date=date(2024, 4, 2),
            venue_id=venue.id,
            team_1_id=team1.id,
            team_2_id=team2.id,
        ),
    )

    inn1 = Innings(
        match_id=match.id,
        innings_number=1,
        batting_team_id=team1.id,
        bowling_team_id=team2.id,
    )
    db_session.add(inn1)
    db_session.commit()

    # Adding another innings with the same match_id and innings_number must trigger IntegrityError
    inn1_duplicate = Innings(
        match_id=match.id,
        innings_number=1,
        batting_team_id=team2.id,
        bowling_team_id=team1.id,
    )
    db_session.add(inn1_duplicate)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
