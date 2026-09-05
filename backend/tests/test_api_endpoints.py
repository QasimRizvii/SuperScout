"""
Tests for API v1 Pagination and Filtering Endpoints
"""
from datetime import date
from app.models.enums import PlayerRole, AuctionType
from app.schemas.player import PlayerCreate
from app.schemas.team import TeamCreate
from app.schemas.venue import VenueCreate
from app.schemas.match import MatchCreate
from app.schemas.auction import AuctionCreate
from app.services.player_service import PlayerService
from app.services.team_service import TeamService
from app.services.venue_service import VenueService
from app.services.match_service import MatchService
from app.services.auction_service import AuctionService


def test_players_api_pagination_and_filtering(client, db_session):
    PlayerService.create_player(db_session, PlayerCreate(name="Player Alpha", role=PlayerRole.BATTER, nationality="India"))
    PlayerService.create_player(db_session, PlayerCreate(name="Player Beta", role=PlayerRole.BOWLER, nationality="Australia"))

    # Test list
    res = client.get("/api/v1/players?page=1&page_size=10")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total"] >= 2

    # Test filtering by role
    res_role = client.get("/api/v1/players?role=bowler")
    assert res_role.status_code == 200
    data_role = res_role.json()
    assert any(p["name"] == "Player Beta" for p in data_role["items"])


def test_teams_api_endpoints(client, db_session):
    team = TeamService.create_team(db_session, TeamCreate(name="Delhi Capitals", abbreviation="DC"))

    res = client.get(f"/api/v1/teams/{team.id}")
    assert res.status_code == 200
    assert res.json()["name"] == "Delhi Capitals"

    # Not found
    res_404 = client.get("/api/v1/teams/999999")
    assert res_404.status_code == 404


def test_venues_api_endpoints(client, db_session):
    venue = VenueService.create_venue(db_session, VenueCreate(name="Eden Gardens", city="Kolkata"))

    res = client.get(f"/api/v1/venues/{venue.id}")
    assert res.status_code == 200
    assert res.json()["name"] == "Eden Gardens"


def test_matches_api_endpoints(client, db_session):
    t1 = TeamService.create_team(db_session, TeamCreate(name="Team 1", abbreviation="T1"))
    t2 = TeamService.create_team(db_session, TeamCreate(name="Team 2", abbreviation="T2"))
    v = VenueService.create_venue(db_session, VenueCreate(name="Venue 1"))

    match = MatchService.create_match(
        db_session,
        MatchCreate(season="2024", match_date=date(2024, 5, 1), venue_id=v.id, team_1_id=t1.id, team_2_id=t2.id),
    )

    res = client.get(f"/api/v1/matches/{match.id}")
    assert res.status_code == 200
    assert res.json()["season"] == "2024"


def test_auctions_api_endpoints(client, db_session):
    auction = AuctionService.create_auction(
        db_session,
        AuctionCreate(season="2025", auction_name="IPL 2025 Mini Auction", auction_type=AuctionType.MINI),
    )

    res = client.get(f"/api/v1/auctions/{auction.id}")
    assert res.status_code == 200
    assert res.json()["auction_type"] == "mini"
