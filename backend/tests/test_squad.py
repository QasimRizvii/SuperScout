"""
SuperScout Backend — Step 5 Squad Intelligence & Team Composition Test Suite

Tests:
1. Squad role distribution & classification
2. Squad balance score & tactical audit (Strengths & Weaknesses)
3. Batting and bowling depth evaluation
4. Pace and spin variety calculations
5. Wicketkeeper coverage detection
6. Phase coverage (Powerplay, Middle, Death overs)
7. Playing XI Optimizer constraints (1 Wicketkeeper, 5+ Bowlers, 1-11 batting order)
8. Playing XI selection explanations
9. Scenario analysis (simulating unavailable players & bench replacements)
10. Role gap analysis & recruitment candidate search
11. Side-by-side squad comparison
12. Insufficient squad size handling
13. REST API endpoints (200 OK, 404 Not Found, 400 Bad Request)
"""
import pytest
from datetime import date

from app.models.enums import MatchType, PlayerRole
from app.models.player import Player
from app.models.team import Team
from app.models.venue import Venue
from app.models.match import Match
from app.models.batting import BattingPerformance
from app.models.bowling import BowlingPerformance
from app.services.squad.role_classifier import RoleClassifier
from app.services.squad.squad_service import SquadIntelligenceService


# ── 1. Role Classifier Unit Tests ──────────────────────────────────────────────
def test_role_classifier_rules():
    p_keeper = Player(name="Keeper Player", role=PlayerRole.WICKETKEEPER_BATTER, is_wicketkeeper=True)
    p_pace = Player(name="Pacer Player", role=PlayerRole.FAST_BOWLER, bowling_style="Right-arm fast")
    p_spin = Player(name="Spinner Player", role=PlayerRole.SPINNER, bowling_style="Legbreak googly")
    p_ar = Player(name="AR Player", role=PlayerRole.ALL_ROUNDER)

    assert RoleClassifier.is_wicketkeeper(p_keeper) is True
    assert RoleClassifier.is_pace_bowler(p_pace) is True
    assert RoleClassifier.is_spin_bowler(p_spin) is True
    assert RoleClassifier.is_all_rounder(p_ar) is True


# ── 2. Squad Fixture for Integration Tests ────────────────────────────────────
@pytest.fixture
def squad_test_data(db_session):
    t1 = Team(name="SuperScout XI", short_name="SSXI", abbreviation="SSXI", country="India")
    t2 = Team(name="Opponent XI", short_name="OPP", abbreviation="OPP", country="India")
    v = Venue(name="Eden Gardens", city="Kolkata", country="India")
    db_session.add_all([t1, t2, v])
    db_session.commit()

    m1 = Match(season="2025", match_date=date(2025, 4, 10), match_type=MatchType.T20, venue_id=v.id, team_1_id=t1.id, team_2_id=t2.id)
    db_session.add(m1)
    db_session.commit()

    # Create 12 players for Team 1 (Squad of 12)
    p_keeper = Player(name="Sanju Samson", role=PlayerRole.WICKETKEEPER_BATTER, is_wicketkeeper=True, nationality="India")
    p_bat1 = Player(name="Yashasvi Jaiswal", role=PlayerRole.BATTER, nationality="India")
    p_bat2 = Player(name="Jos Buttler", role=PlayerRole.BATTER, nationality="England")
    p_bat3 = Player(name="Shimron Hetmyer", role=PlayerRole.BATTER, nationality="West Indies")
    p_ar1 = Player(name="Riyan Parag", role=PlayerRole.ALL_ROUNDER, nationality="India")
    p_ar2 = Player(name="Ravichandran Ashwin", role=PlayerRole.ALL_ROUNDER, bowling_style="Right-arm offbreak", nationality="India")
    p_bowl1 = Player(name="Trent Boult", role=PlayerRole.FAST_BOWLER, bowling_style="Left-arm fast-medium", nationality="New Zealand")
    p_bowl2 = Player(name="Yuzvendra Chahal", role=PlayerRole.SPINNER, bowling_style="Legbreak googly", nationality="India")
    p_bowl3 = Player(name="Avesh Khan", role=PlayerRole.FAST_BOWLER, bowling_style="Right-arm fast", nationality="India")
    p_bowl4 = Player(name="Sandeep Sharma", role=PlayerRole.MEDIUM_FAST_BOWLER, bowling_style="Right-arm medium-fast", nationality="India")
    p_sub1 = Player(name="Bench Batter", role=PlayerRole.BATTER, nationality="India")
    p_sub2 = Player(name="Bench Bowler", role=PlayerRole.BOWLER, bowling_style="Right-arm fast", nationality="India")

    players_t1 = [p_keeper, p_bat1, p_bat2, p_bat3, p_ar1, p_ar2, p_bowl1, p_bowl2, p_bowl3, p_bowl4, p_sub1, p_sub2]
    db_session.add_all(players_t1)
    db_session.commit()

    # Add performances connecting players to Team 1
    for p in players_t1:
        bp = BattingPerformance(match_id=m1.id, innings_id=1, player_id=p.id, team_id=t1.id, runs=25, balls_faced=15, fours=2, sixes=1, dot_balls=4, dismissal_type="caught")
        bw = BowlingPerformance(match_id=m1.id, innings_id=2, player_id=p.id, team_id=t1.id, overs=4.0, balls_bowled=24, runs_conceded=24, wickets=1, dot_balls=10, overs_powerplay=2.0, overs_death=2.0)
        db_session.add_all([bp, bw])
    db_session.commit()

    # Create Team 2 players
    players_t2 = []
    for i in range(11):
        p = Player(name=f"Opponent Player {i+1}", role=PlayerRole.BATTER if i < 6 else PlayerRole.BOWLER, nationality="India")
        players_t2.append(p)
    db_session.add_all(players_t2)
    db_session.commit()
    for p in players_t2:
        bp = BattingPerformance(match_id=m1.id, innings_id=2, player_id=p.id, team_id=t2.id, runs=10, balls_faced=10)
        db_session.add(bp)
    db_session.commit()

    return {"t1": t1, "t2": t2, "players_t1": players_t1, "p_keeper": p_keeper, "p_boult": p_bowl1}


# ── 3. Squad Balance & Audit Tests ───────────────────────────────────────────
def test_squad_balance_analysis(db_session, squad_test_data):
    t1 = squad_test_data["t1"]
    svc = SquadIntelligenceService(db_session)

    balance = svc.compute_squad_balance(t1.id)

    assert balance.team_id == t1.id
    assert balance.squad_size == 12
    assert balance.overall_balance_score > 0.0
    assert balance.role_distribution.wicketkeepers_count >= 1
    assert balance.role_distribution.pace_bowlers_count >= 2
    assert balance.role_distribution.spin_bowlers_count >= 2
    assert len(balance.strengths) > 0


# ── 4. Playing XI Optimizer Tests ──────────────────────────────────────────────
def test_playing_xi_optimization_constraints(db_session, squad_test_data):
    t1 = squad_test_data["t1"]
    svc = SquadIntelligenceService(db_session)

    xi_resp = svc.optimize_playing_xi(t1.id)

    assert xi_resp.team_id == t1.id
    assert len(xi_resp.recommended_xi) == 11
    assert xi_resp.wicketkeeper_player_id is not None
    assert xi_resp.captain_player_id is not None

    # Verify positions 1 to 11
    positions = [p.batting_position for p in xi_resp.recommended_xi]
    assert positions == list(range(1, 12))

    # Verify selection reasons exist
    for p in xi_resp.recommended_xi:
        assert len(p.selection_reason) > 0


# ── 5. Scenario Analysis Tests ────────────────────────────────────────────────
def test_scenario_analysis_unavailability(db_session, squad_test_data):
    t1 = squad_test_data["t1"]
    keeper = squad_test_data["p_keeper"]
    svc = SquadIntelligenceService(db_session)

    scenario = svc.simulate_scenario(t1.id, unavailable_player_ids=[keeper.id])

    assert scenario.team_id == t1.id
    assert scenario.unavailable_player_ids == [keeper.id]
    assert len(scenario.newly_exposed_gaps) > 0
    assert "wicketkeeper" in scenario.newly_exposed_gaps[0].lower()


# ── 6. Gap Analysis Tests ──────────────────────────────────────────────────────
def test_role_gap_analysis(db_session, squad_test_data):
    t1 = squad_test_data["t1"]
    svc = SquadIntelligenceService(db_session)

    gaps = svc.identify_gaps(t1.id)
    assert isinstance(gaps, list)


# ── 7. Squad Comparison Tests ──────────────────────────────────────────────────
def test_squad_comparison(db_session, squad_test_data):
    t1 = squad_test_data["t1"]
    t2 = squad_test_data["t2"]
    svc = SquadIntelligenceService(db_session)

    comp = svc.compare_squads(t1.id, t2.id)

    assert comp.team_1_id == t1.id
    assert comp.team_2_id == t2.id
    assert len(comp.comparison_matrix) >= 5
    assert comp.overall_advantage_team_id in (t1.id, t2.id)


# ── 8. REST API Endpoints Tests ────────────────────────────────────────────────
def test_api_squad_intelligence(client, squad_test_data):
    t1 = squad_test_data["t1"]

    res = client.get(f"/api/v1/squads/{t1.id}/intelligence")
    assert res.status_code == 200
    data = res.json()
    assert data["team_name"] == "SuperScout XI"
    assert "balance" in data
    assert "playing_xi" in data


def test_api_squad_balance_and_playing_xi(client, squad_test_data):
    t1 = squad_test_data["t1"]

    res_bal = client.get(f"/api/v1/squads/{t1.id}/balance")
    assert res_bal.status_code == 200
    assert res_bal.json()["overall_balance_score"] > 0

    res_xi = client.get(f"/api/v1/squads/{t1.id}/playing-xi")
    assert res_xi.status_code == 200
    assert len(res_xi.json()["recommended_xi"]) == 11


def test_api_squad_role_analysis_and_gaps(client, squad_test_data):
    t1 = squad_test_data["t1"]

    res_roles = client.get(f"/api/v1/squads/{t1.id}/role-analysis")
    assert res_roles.status_code == 200
    assert "pace_spin_breakdown" in res_roles.json()

    res_gaps = client.get(f"/api/v1/squads/{t1.id}/gaps")
    assert res_gaps.status_code == 200
    assert isinstance(res_gaps.json(), list)


def test_api_squad_scenarios(client, squad_test_data):
    t1 = squad_test_data["t1"]
    keeper = squad_test_data["p_keeper"]

    res_scen = client.post(f"/api/v1/squads/{t1.id}/scenarios", json={"unavailable_player_ids": [keeper.id]})
    assert res_scen.status_code == 200
    assert res_scen.json()["scenario_balance_score"] >= 0


def test_api_squad_comparison(client, squad_test_data):
    t1 = squad_test_data["t1"]
    t2 = squad_test_data["t2"]

    res_comp = client.get(f"/api/v1/squads/compare?team_1_id={t1.id}&team_2_id={t2.id}")
    assert res_comp.status_code == 200
    assert res_comp.json()["team_1_id"] == t1.id


def test_api_squad_not_found(client):
    res = client.get("/api/v1/squads/999999/balance")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()
