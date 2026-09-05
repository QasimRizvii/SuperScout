"""
Tests for Team Entity Creation and Filtering
"""
from app.schemas.team import TeamCreate
from app.services.team_service import TeamService


def test_team_creation(db_session):
    team_in = TeamCreate(
        name="Royal Challengers Bengaluru",
        short_name="RCB",
        abbreviation="RCB",
        city="Bengaluru",
        is_active=True,
    )
    team = TeamService.create_team(db_session, team_in)

    assert team.id is not None
    assert team.name == "Royal Challengers Bengaluru"
    assert team.abbreviation == "RCB"
    assert team.city == "Bengaluru"


def test_team_filtering(db_session):
    TeamService.create_team(db_session, TeamCreate(name="Mumbai Indians", abbreviation="MI"))
    TeamService.create_team(db_session, TeamCreate(name="Chennai Super Kings", abbreviation="CSK"))

    items, total = TeamService.get_teams(db_session, name="Chennai")
    assert total >= 1
    assert items[0].abbreviation == "CSK"
