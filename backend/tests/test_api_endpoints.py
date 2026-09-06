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
    PlayerService.create_player(db_session, PlayerCreate(name="Virat Kohli", role=PlayerRole.BATTER, nationality="India"))
    PlayerService.create_player(db_session, PlayerCreate(name="Jasprit Bumrah", role=PlayerRole.FAST_BOWLER, nationality="India"))

    # Test list
    res = client.get("/api/v1/players?page=1&page_size=10")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total"] >= 2

    # Test search query param
    res_search = client.get("/api/v1/players?search=virat")
    assert res_search.status_code == 200
    data_search = res_search.json()
    assert any(p["name"] == "Virat Kohli" for p in data_search["items"])

    # Test role filtering
    res_role = client.get("/api/v1/players?role=fast_bowler")
    assert res_role.status_code == 200
    data_role = res_role.json()
    assert any(p["name"] == "Jasprit Bumrah" for p in data_role["items"])


def test_teams_api_endpoints(client, db_session):
    team = TeamService.create_team(db_session, TeamCreate(name="Delhi Capitals", abbreviation="DC", country="India", team_type="franchise"))

    res = client.get(f"/api/v1/teams/{team.id}")
    assert res.status_code == 200
    assert res.json()["name"] == "Delhi Capitals"
    assert res.json()["country"] == "India"

    # Filter teams by country
    res_country = client.get("/api/v1/teams?country=India")
    assert res_country.status_code == 200
    assert any(t["name"] == "Delhi Capitals" for t in res_country.json()["items"])

    # Not found
    res_404 = client.get("/api/v1/teams/999999")
    assert res_404.status_code == 404


def test_venues_api_endpoints(client, db_session):
    venue = VenueService.create_venue(db_session, VenueCreate(name="Eden Gardens", city="Kolkata", country="India", capacity=66000))

    res = client.get(f"/api/v1/venues/{venue.id}")
    assert res.status_code == 200
    assert res.json()["name"] == "Eden Gardens"
    assert res.json()["capacity"] == 66000


def test_matches_api_endpoints(client, db_session):
    t1 = TeamService.create_team(db_session, TeamCreate(name="Team 1", abbreviation="T1"))
    t2 = TeamService.create_team(db_session, TeamCreate(name="Team 2", abbreviation="T2"))
    v = VenueService.create_venue(db_session, VenueCreate(name="Venue 1"))

    match = MatchService.create_match(
        db_session,
        MatchCreate(season="2024", competition="IPL", match_date=date(2024, 5, 1), venue_id=v.id, team_1_id=t1.id, team_2_id=t2.id),
    )

    res = client.get(f"/api/v1/matches/{match.id}")
    assert res.status_code == 200
    assert res.json()["season"] == "2024"
    assert res.json()["competition"] == "IPL"


def test_pagination_and_validation_errors(client):
    # Invalid page number (ge=1)
    res_invalid_page = client.get("/api/v1/players?page=0")
    assert res_invalid_page.status_code == 422

    # Invalid page_size (le=100)
    res_invalid_size = client.get("/api/v1/players?page_size=200")
    assert res_invalid_size.status_code == 422


def test_auctions_api_endpoints(client, db_session):
    auction = AuctionService.create_auction(
        db_session,
        AuctionCreate(season="2025", auction_name="IPL 2025 Mini Auction", auction_type=AuctionType.MINI),
    )

    res = client.get(f"/api/v1/auctions/{auction.id}")
    assert res.status_code == 200
    assert res.json()["auction_type"] == "mini"
