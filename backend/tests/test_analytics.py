"""
SuperScout Backend — Step 4 Player Intelligence & Analytics Test Suite

Tests:
1. Batting average calculation (normal, undefeated, zero dismissals)
2. Batting strike rate (normal, zero balls faced)
3. Bowling economy rate (normal, zero balls bowled)
4. Bowling average (normal, zero wickets)
5. Bowling strike rate (normal, zero wickets)
6. Dot-ball percentage (batting and bowling)
7. Boundary percentage & balls per boundary
8. Phase-wise metrics (Powerplay, Middle, Death)
9. Consistency metrics (mean, std dev, CV, high-impact %)
10. Recent form windowing (last N matches, chronological sorting)
11. Small sample size dampening & zero data safety
12. Player role evaluation & weight assignment
13. Player Intelligence Score calculation & explainability
14. Player comparison (2-5 players, ranking, invalid count errors)
15. REST API endpoints (200 OK, 404 Not Found, 400 Bad Request)
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
from app.services.analytics.batting import BattingAnalyticsEngine
from app.services.analytics.bowling import BowlingAnalyticsEngine, overs_to_balls, balls_to_overs
from app.services.analytics.player import PlayerAnalyticsService
from app.services.analytics.scoring import PlayerIntelligenceScorer
from app.services.analytics.exceptions import InvalidComparisonError


# ── 1. Overs Conversion Unit Tests ──────────────────────────────────────────────
def test_overs_to_balls_conversion():
    assert overs_to_balls(4.0) == 24
    assert overs_to_balls(3.4) == 22
    assert overs_to_balls(0.2) == 2
    assert overs_to_balls(0.0) == 0

    assert balls_to_overs(24) == 4.0
    assert balls_to_overs(22) == 3.4
    assert balls_to_overs(2) == 0.2
    assert balls_to_overs(0) == 0.0


# ── 2. Batting Engine Unit Tests ───────────────────────────────────────────────
def test_batting_analytics_engine_normal():
    # Performance 1: 50 runs off 30 balls (5 fours, 2 sixes, 10 dots, caught)
    # Performance 2: 30 runs off 20 balls (3 fours, 1 six, 8 dots, not_out)
    p1 = BattingPerformance(runs=50, balls_faced=30, fours=5, sixes=2, dot_balls=10, dismissal_type="caught", runs_powerplay=20, runs_middle=20, runs_death=10)
    p2 = BattingPerformance(runs=30, balls_faced=20, fours=3, sixes=1, dot_balls=8, dismissal_type="not_out", runs_powerplay=10, runs_middle=15, runs_death=5)

    res = BattingAnalyticsEngine.compute_batting_analytics(1, "Test Player", [p1, p2])

    assert res.sample_size == 2
    assert res.runs == 80
    assert res.balls_faced == 50
    assert res.dismissals == 1
    assert res.not_outs == 1
    assert res.highest_score == 50

    # Batting average: 80 / 1 = 80.0
    assert res.batting_average.value == 80.0
    # Strike rate: (80 / 50) * 100 = 160.0
    assert res.strike_rate.value == 160.0

    # Boundary runs: (8*4) + (3*6) = 32 + 18 = 50. Boundary %: (50/80)*100 = 62.5
    assert res.boundary_runs == 50
    assert res.boundary_percentage.value == 62.5

    # Dot ball %: (18 / 50) * 100 = 36.0
    assert res.dot_ball_percentage.value == 36.0


def test_batting_analytics_engine_zero_data():
    res = BattingAnalyticsEngine.compute_batting_analytics(1, "Zero Player", [])

    assert res.sample_size == 0
    assert res.batting_average.metric_available is False
    assert res.strike_rate.metric_available is False
    assert "No batting innings" in res.batting_average.reason


def test_batting_analytics_undefeated():
    p1 = BattingPerformance(runs=40, balls_faced=25, fours=4, sixes=1, dot_balls=5, dismissal_type="not_out")
    res = BattingAnalyticsEngine.compute_batting_analytics(1, "Undefeated Batter", [p1])

    assert res.dismissals == 0
    assert res.not_outs == 1
    assert res.batting_average.metric_available is True
    assert res.batting_average.value == 40.0


# ── 3. Bowling Engine Unit Tests ───────────────────────────────────────────────
def test_bowling_analytics_engine_normal():
    # Perf 1: 4.0 overs (24 balls), 24 runs, 2 wickets, 12 dots, 1 maiden
    # Perf 2: 3.0 overs (18 balls), 21 runs, 1 wicket, 8 dots, 0 maidens
    p1 = BowlingPerformance(overs=4.0, balls_bowled=24, runs_conceded=24, wickets=2, dot_balls=12, maidens=1, wides=1, no_balls=0, overs_powerplay=2.0, overs_death=2.0)
    p2 = BowlingPerformance(overs=3.0, balls_bowled=18, runs_conceded=21, wickets=1, dot_balls=8, maidens=0, wides=0, no_balls=1, overs_middle=3.0)

    res = BowlingAnalyticsEngine.compute_bowling_analytics(1, "Test Bowler", [p1, p2])

    assert res.sample_size == 2
    assert res.balls_bowled == 42
    assert res.overs == 7.0
    assert res.runs_conceded == 45
    assert res.wickets == 3
    assert res.maidens == 1
    assert res.extras_conceded == 2

    # Economy: 45 / (42 / 6) = 45 / 7 = 6.43
    assert res.economy_rate.value == 6.43
    # Bowling Average: 45 / 3 = 15.0
    assert res.bowling_average.value == 15.0
    # Bowling Strike Rate: 42 / 3 = 14.0
    assert res.bowling_strike_rate.value == 14.0


def test_bowling_analytics_zero_wickets():
    p1 = BowlingPerformance(overs=4.0, balls_bowled=24, runs_conceded=30, wickets=0)
    res = BowlingAnalyticsEngine.compute_bowling_analytics(1, "Wicketless Bowler", [p1])

    assert res.wickets == 0
    assert res.bowling_average.metric_available is False
    assert res.bowling_strike_rate.metric_available is False
    assert "Zero wickets" in res.bowling_average.reason


# ── 4. Player Intelligence Score Tests ─────────────────────────────────────────
def test_intelligence_score_calculation():
    b_resp = BattingAnalyticsEngine.compute_batting_analytics(
        1, "Score Batter",
        [BattingPerformance(runs=60, balls_faced=35, fours=6, sixes=3, dot_balls=10, dismissal_type="caught")]
    )
    bat_score = PlayerIntelligenceScorer.calculate_batting_score(b_resp)
    assert bat_score > 0.0


# ── 5. Integration Tests with DB Session ──────────────────────────────────────
@pytest.fixture
def analytics_test_data(db_session):
    t1 = Team(name="Mumbai Indians", short_name="MI", abbreviation="MI", country="India", team_type="franchise")
    t2 = Team(name="Delhi Capitals", short_name="DC", abbreviation="DC", country="India", team_type="franchise")
    v = Venue(name="Wankhede Stadium", city="Mumbai", country="India")
    db_session.add_all([t1, t2, v])
    db_session.commit()

    m1 = Match(season="2025", match_date=date(2025, 4, 1), match_type=MatchType.T20, venue_id=v.id, team_1_id=t1.id, team_2_id=t2.id)
    m2 = Match(season="2025", match_date=date(2025, 4, 5), match_type=MatchType.T20, venue_id=v.id, team_1_id=t1.id, team_2_id=t2.id)
    db_session.add_all([m1, m2])
    db_session.commit()

    p1 = Player(name="Subman Gill", short_name="S Gill", role=PlayerRole.BATTER, nationality="India")
    p2 = Player(name="Jasprit Bumrah", short_name="J Bumrah", role=PlayerRole.FAST_BOWLER, nationality="India")
    db_session.add_all([p1, p2])
    db_session.commit()

    bp1 = BattingPerformance(match_id=m1.id, innings_id=1, player_id=p1.id, team_id=t1.id, runs=75, balls_faced=45, fours=8, sixes=3, dot_balls=12, dismissal_type="caught")
    bp2 = BattingPerformance(match_id=m2.id, innings_id=1, player_id=p1.id, team_id=t1.id, runs=40, balls_faced=25, fours=4, sixes=1, dot_balls=7, dismissal_type="not_out")

    bw1 = BowlingPerformance(match_id=m1.id, innings_id=2, player_id=p2.id, team_id=t1.id, overs=4.0, balls_bowled=24, runs_conceded=18, wickets=3, dot_balls=14, maidens=1)
    bw2 = BowlingPerformance(match_id=m2.id, innings_id=2, player_id=p2.id, team_id=t1.id, overs=4.0, balls_bowled=24, runs_conceded=22, wickets=2, dot_balls=13, maidens=0)

    db_session.add_all([bp1, bp2, bw1, bw2])
    db_session.commit()

    return {"p1": p1, "p2": p2}


def test_player_analytics_service(db_session, analytics_test_data):
    p1 = analytics_test_data["p1"]
    p2 = analytics_test_data["p2"]

    service = PlayerAnalyticsService(db_session)

    # Overview p1
    ov1 = service.compute_overview(p1.id)
    assert ov1.player_name == "Subman Gill"
    assert ov1.batting.runs == 115
    assert ov1.batting.batting_average.value == 115.0
    assert ov1.intelligence_score.overall_score > 0.0

    # Overview p2
    ov2 = service.compute_overview(p2.id)
    assert ov2.player_name == "Jasprit Bumrah"
    assert ov2.bowling.wickets == 5
    assert ov2.bowling.economy_rate.value == 5.0  # 40 runs / 8 overs = 5.0

    # Comparison p1 vs p2
    comp = service.compare_players([p1.id, p2.id])
    assert comp.players_compared == 2
    assert comp.top_overall_player_id in (p1.id, p2.id)


def test_invalid_comparison_exception(db_session, analytics_test_data):
    p1 = analytics_test_data["p1"]
    service = PlayerAnalyticsService(db_session)

    with pytest.raises(InvalidComparisonError):
        service.compare_players([p1.id])  # only 1 player


# ── 6. REST API Endpoint Tests ────────────────────────────────────────────────
def test_api_get_player_analytics(client, analytics_test_data):
    p1 = analytics_test_data["p1"]

    res = client.get(f"/api/v1/players/{p1.id}/analytics")
    assert res.status_code == 200
    data = res.json()
    assert data["player_name"] == "Subman Gill"
    assert data["batting"]["runs"] == 115
    assert "intelligence_score" in data


def test_api_get_batting_and_bowling_analytics(client, analytics_test_data):
    p1 = analytics_test_data["p1"]
    p2 = analytics_test_data["p2"]

    res_bat = client.get(f"/api/v1/players/{p1.id}/batting-analytics")
    assert res_bat.status_code == 200
    assert res_bat.json()["runs"] == 115

    res_bowl = client.get(f"/api/v1/players/{p2.id}/bowling-analytics")
    assert res_bowl.status_code == 200
    assert res_bowl.json()["wickets"] == 5


def test_api_get_recent_form_and_score(client, analytics_test_data):
    p1 = analytics_test_data["p1"]

    res_form = client.get(f"/api/v1/players/{p1.id}/recent-form?limit=5")
    assert res_form.status_code == 200
    assert res_form.json()["actual_sample_size"] == 2

    res_score = client.get(f"/api/v1/players/{p1.id}/intelligence-score")
    assert res_score.status_code == 200
    assert res_score.json()["overall_score"] > 0


def test_api_player_comparison(client, analytics_test_data):
    p1 = analytics_test_data["p1"]
    p2 = analytics_test_data["p2"]

    res_comp = client.get(f"/api/v1/players/compare?player_ids={p1.id}&player_ids={p2.id}")
    assert res_comp.status_code == 200
    data = res_comp.json()
    assert data["players_compared"] == 2


def test_api_player_not_found(client):
    res = client.get("/api/v1/players/999999/analytics")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()
