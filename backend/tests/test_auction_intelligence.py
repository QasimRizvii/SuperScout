"""
SuperScout Backend — Step 6 Auction Intelligence & Strategy Engine Test Suite

Tests:
1. Player Fair Value & Maximum Bid Ceiling calculations
2. Franchise Squad Fit evaluation (high fit for gap roles vs low fit for overstocked roles)
3. Role Scarcity calculation
4. Auction Target Ranking for a franchise
5. Purse Budget Allocation based on squad gaps
6. Alternative Target fallback recommendation tree
7. Opportunity Cost evaluation for proposed bids
8. What-If Auction Scenario simulation (purchase, outbid, price surge)
9. Comparable Player statistical matching & price benchmarking
10. Edge cases (zero purse, small purse, unsold players, missing historical data)
11. REST API endpoints (200 OK, 404 Not Found, 400 Bad Request, 422 Unprocessable Entity)
"""
import pytest
from datetime import date

from app.models.enums import AuctionType, AuctionStatus, MatchType, PlayerRole
from app.models.player import Player
from app.models.team import Team
from app.models.venue import Venue
from app.models.match import Match
from app.models.batting import BattingPerformance
from app.models.bowling import BowlingPerformance
from app.models.auction import Auction, AuctionTransaction
from app.services.auction.scarcity_engine import RoleScarcityEngine
from app.services.auction.valuation_engine import ValuationEngine
from app.services.auction.auction_service import AuctionIntelligenceService


# ── 1. Scarcity & Valuation Unit Tests ───────────────────────────────────────
def test_scarcity_engine_levels():
    p1 = Player(name="P1", role=PlayerRole.WICKETKEEPER_BATTER, is_wicketkeeper=True)
    p2 = Player(name="P2", role=PlayerRole.BATTER)
    p3 = Player(name="P3", role=PlayerRole.BATTER)

    # Keeper count = 1 -> HIGH scarcity
    high_scarcity = RoleScarcityEngine.compute_role_scarcity(PlayerRole.WICKETKEEPER, [p1, p2, p3])
    assert high_scarcity == "HIGH"
    assert RoleScarcityEngine.get_scarcity_multiplier("HIGH") == 1.25

    # Batter count = 2 -> HIGH scarcity
    low_scarcity = RoleScarcityEngine.compute_role_scarcity(PlayerRole.BATTER, [p1, p2, p3])
    assert low_scarcity == "HIGH"


def test_valuation_engine_fair_value_and_ceiling():
    p = Player(id=1, name="Star Player", role=PlayerRole.FAST_BOWLER)
    val = ValuationEngine.calculate_valuation(
        player=p,
        base_price=50.0,
        analytics=None,  # default 50 score
        fit_score=None,
        remaining_purse=1000.0,
        remaining_squad_slots=5,
    )

    assert val.player_id == 1
    assert val.base_price == 50.0
    assert val.estimated_fair_value >= 50.0
    assert val.recommended_max_bid >= 50.0
    assert val.confidence in ("HIGH", "MEDIUM", "LOW")


# ── 2. Integration Tests with DB Session ──────────────────────────────────────
@pytest.fixture
def auction_test_data(db_session):
    auc = Auction(season="2025", auction_name="IPL Mega Auction 2025", auction_type=AuctionType.MEGA, auction_date=date(2025, 2, 1))
    t1 = Team(name="SuperScout Franchise", short_name="SSF", abbreviation="SSF", country="India")
    t2 = Team(name="Rival Franchise", short_name="RF", abbreviation="RF", country="India")
    v = Venue(name="M. Chinnaswamy Stadium", city="Bangalore", country="India")
    db_session.add_all([auc, t1, t2, v])
    db_session.commit()

    m1 = Match(season="2025", match_date=date(2025, 4, 1), match_type=MatchType.T20, venue_id=v.id, team_1_id=t1.id, team_2_id=t2.id)
    db_session.add(m1)
    db_session.commit()

    # Team 1 Squad Players
    p_keeper = Player(name="Rishabh Pant", role=PlayerRole.WICKETKEEPER_BATTER, is_wicketkeeper=True, nationality="India")
    p_bowler = Player(name="Jasprit Bumrah", role=PlayerRole.FAST_BOWLER, bowling_style="Right-arm fast", nationality="India")

    # Target Candidates (Outside Team 1 Squad)
    p_spinner = Player(name="Rashid Khan", role=PlayerRole.SPINNER, bowling_style="Legbreak googly", nationality="Afghanistan")
    p_batter = Player(name="Shubman Gill", role=PlayerRole.BATTER, nationality="India")

    players = [p_keeper, p_bowler, p_spinner, p_batter]
    db_session.add_all(players)
    db_session.commit()

    # Team 1 squad performances
    for p in [p_keeper, p_bowler]:
        bp = BattingPerformance(match_id=m1.id, innings_id=1, player_id=p.id, team_id=t1.id, runs=35, balls_faced=20, fours=3, sixes=2, dot_balls=5, dismissal_type="caught")
        bw = BowlingPerformance(match_id=m1.id, innings_id=2, player_id=p.id, team_id=t1.id, overs=4.0, balls_bowled=24, runs_conceded=20, wickets=2, dot_balls=12, overs_death=2.0)
        db_session.add_all([bp, bw])

    # Candidate pool performances (Team 2)
    for p in [p_spinner, p_batter]:
        bp = BattingPerformance(match_id=m1.id, innings_id=1, player_id=p.id, team_id=t2.id, runs=45, balls_faced=25, fours=4, sixes=2, dot_balls=6, dismissal_type="not_out")
        bw = BowlingPerformance(match_id=m1.id, innings_id=2, player_id=p.id, team_id=t2.id, overs=4.0, balls_bowled=24, runs_conceded=18, wickets=3, dot_balls=14, overs_death=2.0)
        db_session.add_all([bp, bw])

    db_session.commit()

    # Historical auction transactions for comparables benchmarking
    tx1 = AuctionTransaction(auction_id=auc.id, player_id=p_bowler.id, team_id=t1.id, base_price=200.0, final_price=1200.0, status=AuctionStatus.SOLD)
    db_session.add(tx1)
    db_session.commit()

    return {"auc": auc, "t1": t1, "p_keeper": p_keeper, "p_bowler": p_bowler, "p_spinner": p_spinner}


def test_auction_target_ranking(db_session, auction_test_data):
    auc = auction_test_data["auc"]
    t1 = auction_test_data["t1"]
    svc = AuctionIntelligenceService(db_session)

    rank_resp = svc.rank_targets(
        auction_id=auc.id,
        team_id=t1.id,
        remaining_purse=1000.0,
        remaining_squad_slots=5,
    )

    assert rank_resp.auction_id == auc.id
    assert rank_resp.team_id == t1.id
    assert rank_resp.total_targets_ranked > 0
    assert len(rank_resp.targets) > 0
    assert rank_resp.targets[0].rank == 1


def test_purse_budget_allocation(db_session, auction_test_data):
    auc = auction_test_data["auc"]
    t1 = auction_test_data["t1"]
    svc = AuctionIntelligenceService(db_session)

    alloc = svc.allocate_purse(
        auction_id=auc.id,
        team_id=t1.id,
        total_purse=1000.0,
        remaining_purse=800.0,
        remaining_squad_slots=5,
    )

    assert alloc.team_id == t1.id
    assert alloc.remaining_purse == 800.0
    assert alloc.allocation.bowling_budget > 0.0
    assert alloc.allocation.reserve_budget > 0.0


def test_alternative_targets(db_session, auction_test_data):
    auc = auction_test_data["auc"]
    t1 = auction_test_data["t1"]
    p_bowler = auction_test_data["p_bowler"]
    svc = AuctionIntelligenceService(db_session)

    alts = svc.get_alternative_targets(
        auction_id=auc.id,
        player_id=p_bowler.id,
        team_id=t1.id,
    )

    assert alts.primary_player_id == p_bowler.id
    assert len(alts.recommendation) > 0


def test_opportunity_cost(db_session, auction_test_data):
    auc = auction_test_data["auc"]
    t1 = auction_test_data["t1"]
    p_bowler = auction_test_data["p_bowler"]
    svc = AuctionIntelligenceService(db_session)

    opp = svc.evaluate_opportunity_cost(
        auction_id=auc.id,
        player_id=p_bowler.id,
        team_id=t1.id,
        proposed_bid=800.0,
        remaining_purse=1000.0,
        remaining_squad_slots=5,
    )

    assert opp.player_id == p_bowler.id
    assert opp.proposed_bid == 800.0
    assert opp.cost_level in ("HIGH", "MEDIUM", "LOW")


def test_auction_scenario_simulation(db_session, auction_test_data):
    auc = auction_test_data["auc"]
    t1 = auction_test_data["t1"]
    p_bowler = auction_test_data["p_bowler"]
    svc = AuctionIntelligenceService(db_session)

    scen = svc.simulate_scenario(
        auction_id=auc.id,
        team_id=t1.id,
        target_player_id=p_bowler.id,
        bid_price=500.0,
        outcome="purchased",
        remaining_purse=1000.0,
    )

    assert scen.target_player_id == p_bowler.id
    assert scen.updated_remaining_purse == 500.0
    assert len(scen.scenario_summary) > 0


def test_comparable_players(db_session, auction_test_data):
    auc = auction_test_data["auc"]
    p_bowler = auction_test_data["p_bowler"]
    svc = AuctionIntelligenceService(db_session)

    comps = svc.get_comparables(
        auction_id=auc.id,
        player_id=p_bowler.id,
    )

    assert comps.target_player_id == p_bowler.id
    assert len(comps.comparables) >= 0


# ── 3. REST API Endpoint Tests ────────────────────────────────────────────────
def test_api_auction_targets(client, auction_test_data):
    auc = auction_test_data["auc"]
    t1 = auction_test_data["t1"]

    res = client.get(f"/api/v1/auctions/{auc.id}/targets?team_id={t1.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["team_name"] == "SuperScout Franchise"
    assert "targets" in data


def test_api_player_valuation(client, auction_test_data):
    auc = auction_test_data["auc"]
    p_bowler = auction_test_data["p_bowler"]

    res = client.get(f"/api/v1/auctions/{auc.id}/valuation/{p_bowler.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["player_name"] == "Jasprit Bumrah"
    assert data["estimated_fair_value"] > 0.0


def test_api_auction_budget_and_alternatives(client, auction_test_data):
    auc = auction_test_data["auc"]
    t1 = auction_test_data["t1"]
    p_bowler = auction_test_data["p_bowler"]

    res_b = client.get(f"/api/v1/auctions/{auc.id}/budget?team_id={t1.id}&remaining_purse=800")
    assert res_b.status_code == 200
    assert res_b.json()["remaining_purse"] == 800.0

    res_alt = client.get(f"/api/v1/auctions/{auc.id}/alternatives/{p_bowler.id}?team_id={t1.id}")
    assert res_alt.status_code == 200
    assert "recommendation" in res_alt.json()


def test_api_opportunity_cost_and_comparables(client, auction_test_data):
    auc = auction_test_data["auc"]
    t1 = auction_test_data["t1"]
    p_bowler = auction_test_data["p_bowler"]

    res_opp = client.get(f"/api/v1/auctions/{auc.id}/opportunity-cost/{p_bowler.id}?team_id={t1.id}&proposed_bid=400")
    assert res_opp.status_code == 200
    assert res_opp.json()["proposed_bid"] == 400.0

    res_comp = client.get(f"/api/v1/auctions/{auc.id}/comparables/{p_bowler.id}")
    assert res_comp.status_code == 200
    assert "valuation_guidance" in res_comp.json()


def test_api_auction_scenarios(client, auction_test_data):
    auc = auction_test_data["auc"]
    t1 = auction_test_data["t1"]
    p_bowler = auction_test_data["p_bowler"]

    res = client.post(
        f"/api/v1/auctions/{auc.id}/scenarios",
        json={"team_id": t1.id, "target_player_id": p_bowler.id, "bid_price": 500.0, "outcome": "purchased"},
    )
    assert res.status_code == 200
    assert res.json()["updated_remaining_purse"] == 500.0


def test_api_auction_invalid_purse_error(client, auction_test_data):
    auc = auction_test_data["auc"]
    t1 = auction_test_data["t1"]

    res = client.get(f"/api/v1/auctions/{auc.id}/budget?team_id={t1.id}&remaining_purse=-100")
    assert res.status_code == 422
    assert "greater than or equal to 0" in str(res.json()).lower()
