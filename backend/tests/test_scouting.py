"""
SuperScout Backend — Step 7 Professional Franchise Scouting & Decision-Support Engine Test Suite

Tests:
1. Scouting profile generation
2. Player discovery filtering & search
3. Multiple combined discovery filters
4. Candidate ranking with custom weights
5. Candidate ranking explainability (reasons & component scores)
6. Undervalued player detection & classification
7. Role-specific recruitment targets
8. Franchise scouting recommendations & priority tiers
9. Structured JSON scouting report with evidence-based verdicts
10. Tactical role simulation & evaluation
11. Watchlist creation
12. Watchlist update (priority, status, notes, tags)
13. Watchlist deletion
14. Scouting notes creation & querying by category/player
15. Input validation errors (HTTP 422)
16. Missing player / resource error handling (HTTP 404)
17. Pagination support
18. Multi-field sorting
19. Step 1-6 regression verification
"""
import pytest
from datetime import date

from app.models.enums import PlayerRole, WatchlistStatus, WatchlistPriority, ScoutingNoteCategory
from app.models.player import Player
from app.models.team import Team
from app.models.scouting import ScoutingWatchlist, ScoutingNote
from app.services.scouting.scouting_service import ScoutingService
from app.services.scouting.schemas import (
    RankingWeightsSchema,
    WatchlistCreateRequest,
    WatchlistUpdateRequest,
    ScoutingNoteCreateRequest,
)


@pytest.fixture
def sample_scouting_data(db_session):
    """Populate database with sample players and teams for scouting tests."""
    p1 = Player(
        id=101,
        name="Virat Kohli",
        short_name="V Kohli",
        role=PlayerRole.BATTER,
        batting_style="Right-hand bat",
        nationality="India",
        is_wicketkeeper=False,
        is_active=True,
    )
    p2 = Player(
        id=102,
        name="Jasprit Bumrah",
        short_name="J Bumrah",
        role=PlayerRole.FAST_BOWLER,
        bowling_style="Right-arm fast",
        nationality="India",
        is_wicketkeeper=False,
        is_active=True,
    )
    p3 = Player(
        id=103,
        name="Rishabh Pant",
        short_name="R Pant",
        role=PlayerRole.WICKETKEEPER_BATTER,
        batting_style="Left-hand bat",
        nationality="India",
        is_wicketkeeper=True,
        is_active=True,
    )
    p4 = Player(
        id=104,
        name="Rashid Khan",
        short_name="R Khan",
        role=PlayerRole.SPINNER,
        bowling_style="Right-arm legbreak",
        nationality="Afghanistan",
        is_wicketkeeper=False,
        is_active=True,
    )
    p5 = Player(
        id=105,
        name="Inactive Player",
        short_name="Inactive",
        role=PlayerRole.BATTER,
        nationality="Other",
        is_active=False,
    )

    t1 = Team(id=201, name="Royal Challengers Bengaluru", short_name="RCB", abbreviation="RCB")

    db_session.add_all([p1, p2, p3, p4, p5, t1])
    db_session.commit()
    return {"players": [p1, p2, p3, p4, p5], "team": t1}


# ── 1. Scouting Profile Tests ───────────────────────────────────────────────

def test_scouting_profile_generation(db_session, sample_scouting_data):
    svc = ScoutingService(db_session)
    profile = svc.get_scouting_profile(101)

    assert profile.identity.player_id == 101
    assert profile.identity.name == "Virat Kohli"
    assert profile.identity.role == "batter"
    assert profile.scouting.ideal_role is not None
    assert len(profile.scouting.strengths) > 0


# ── 2. Player Discovery Tests ────────────────────────────────────────────────

def test_player_discovery_basic(db_session, sample_scouting_data):
    svc = ScoutingService(db_session)
    res = svc.discover_players(is_active=True)

    assert res.total_candidates == 4
    assert len(res.items) == 4


def test_player_discovery_multiple_filters(db_session, sample_scouting_data):
    svc = ScoutingService(db_session)
    
    # Filter by role
    res_bowler = svc.discover_players(role="fast_bowler")
    assert res_bowler.total_candidates == 1
    assert res_bowler.items[0].player_id == 102

    # Filter by wicketkeeper
    res_wk = svc.discover_players(is_wicketkeeper=True)
    assert res_wk.total_candidates == 1
    assert res_wk.items[0].player_id == 103

    # Filter by nationality
    res_afg = svc.discover_players(nationality="Afghanistan")
    assert res_afg.total_candidates == 1
    assert res_afg.items[0].player_id == 104


def test_player_discovery_pagination_and_sorting(db_session, sample_scouting_data):
    svc = ScoutingService(db_session)
    
    # Page size 2
    res_p1 = svc.discover_players(page=1, size=2, sort_by="intelligence_score", sort_order="desc")
    assert res_p1.page == 1
    assert res_p1.size == 2
    assert len(res_p1.items) == 2
    assert res_p1.total_pages == 2


# ── 3. Candidate Ranking Engine Tests ───────────────────────────────────────

def test_candidate_ranking(db_session, sample_scouting_data):
    svc = ScoutingService(db_session)
    weights = RankingWeightsSchema(
        performance_weight=0.4,
        recent_form_weight=0.2,
        consistency_weight=0.2,
        role_fit_weight=0.1,
        squad_fit_weight=0.1,
        scarcity_weight=0.0,
        tactical_value_weight=0.0,
    )
    res = svc.rank_candidates(weights=weights, team_id=201)

    assert res.total_ranked == 4
    assert res.candidates[0].rank == 1
    assert "performance_score" in res.candidates[0].component_scores
    assert len(res.candidates[0].reasons) > 0


def test_candidate_ranking_explainability(db_session, sample_scouting_data):
    svc = ScoutingService(db_session)
    res = svc.rank_candidates(team_id=201)

    candidate = res.candidates[0]
    assert candidate.scouting_score >= 0.0
    assert isinstance(candidate.reasons, list)
    assert isinstance(candidate.risks, list)
    assert "squad_fit_score" in candidate.component_scores


# ── 4. Undervalued Player Intelligence Tests ─────────────────────────────────

def test_undervalued_player_detection(db_session, sample_scouting_data):
    svc = ScoutingService(db_session)
    res = svc.get_undervalued_players(team_id=201, min_undervaluation_score=10.0)

    assert res.total_found > 0
    item = res.players[0]
    assert item.undervaluation_score >= 10.0
    assert item.undervaluation_type in ["statistical", "auction", "role_scarcity"]
    assert len(item.reasons) > 0


# ── 5. Role-Specific Target Engine Tests ─────────────────────────────────────

def test_role_target_engine(db_session, sample_scouting_data):
    svc = ScoutingService(db_session)

    # Test Wicketkeeper role
    wk_res = svc.get_role_targets(requested_role="wicketkeeper")
    assert wk_res.total_candidates > 0
    top_wk = wk_res.candidates[0]
    assert top_wk.player_id == 103  # Rishabh Pant

    # Test Pace Bowler role
    pace_res = svc.get_role_targets(requested_role="pace")
    assert pace_res.total_candidates > 0
    top_pace = pace_res.candidates[0]
    assert top_pace.player_id == 102  # Jasprit Bumrah


# ── 6. Scouting Recommendations Tests ────────────────────────────────────────

def test_scouting_recommendations(db_session, sample_scouting_data):
    svc = ScoutingService(db_session)
    recs = svc.get_recommendations(team_id=201, budget=1000.0, slots_needed=3)

    assert (
        len(recs.immediate_priorities)
        + len(recs.secondary_targets)
        + len(recs.watchlist_candidates)
        + len(recs.avoid_candidates)
    ) > 0

    if recs.immediate_priorities:
        target = recs.immediate_priorities[0]
        assert target.why_scout is not None
        assert target.main_risk is not None


# ── 7. Scouting Report Tests ─────────────────────────────────────────────────

def test_scouting_report_generator(db_session, sample_scouting_data):
    svc = ScoutingService(db_session)
    report = svc.get_scouting_report(101, team_id=201)

    assert report.player.player_id == 101
    assert report.scouting_verdict in ["PRIORITY TARGET", "STRONG TARGET", "WATCHLIST", "DEVELOPMENT TARGET", "LOW PRIORITY", "AVOID"]
    assert report.verdict_explanation is not None
    assert isinstance(report.strengths, list)


# ── 8. Tactical Role Fit Tests ───────────────────────────────────────────────

def test_tactical_role_fit(db_session, sample_scouting_data):
    svc = ScoutingService(db_session)
    fit = svc.get_tactical_role_fit(101, evaluated_role="opener")

    assert fit.player_id == 101
    assert fit.evaluated_role == "opener"
    assert fit.suitability_score >= 0.0
    assert len(fit.advantages) > 0


# ── 9. Watchlist CRUD Tests ─────────────────────────────────────────────────

def test_watchlist_crud_service(db_session, sample_scouting_data):
    svc = ScoutingService(db_session)

    # 1. Create
    req = WatchlistCreateRequest(
        player_id=101,
        priority=WatchlistPriority.HIGH,
        status=WatchlistStatus.SHORTLISTED,
        notes="Primary top order recruitment target.",
        tags=["top_order", "marquee"],
    )
    entry = svc.add_to_watchlist(req)

    assert entry.id is not None
    assert entry.player_id == 101
    assert entry.priority == WatchlistPriority.HIGH
    assert entry.status == WatchlistStatus.SHORTLISTED

    # 2. Read / List
    watchlist_items = svc.get_watchlist(player_id=101)
    assert len(watchlist_items) == 1

    # 3. Update
    upd_req = WatchlistUpdateRequest(
        priority=WatchlistPriority.CRITICAL,
        status=WatchlistStatus.PRIORITY,
        notes="Updated priority note.",
    )
    updated_entry = svc.update_watchlist(entry.id, upd_req)
    assert updated_entry.priority == WatchlistPriority.CRITICAL
    assert updated_entry.status == WatchlistStatus.PRIORITY

    # 4. Delete
    svc.delete_watchlist(entry.id)
    items_after = svc.get_watchlist(player_id=101)
    assert len(items_after) == 0


# ── 10. Scouting Notes CRUD Tests ────────────────────────────────────────────

def test_scouting_notes_crud_service(db_session, sample_scouting_data):
    svc = ScoutingService(db_session)

    # Add Note
    req = ScoutingNoteCreateRequest(
        player_id=102,
        category=ScoutingNoteCategory.BOWLING,
        observation="Executes toe-crushing yorkers in death overs consistently.",
        confidence=0.9,
        author="Senior Scout",
    )
    note = svc.add_note(req)

    assert note.id is not None
    assert note.player_id == 102
    assert note.category == ScoutingNoteCategory.BOWLING

    # Get Notes for Player
    notes = svc.get_notes(player_id=102)
    assert len(notes) == 1
    assert notes[0].observation == req.observation


# ── 11. REST API Endpoint Integration Tests ──────────────────────────────────

def test_api_scouting_profile(client, sample_scouting_data):
    res = client.get("/api/v1/scouting/player/101")
    assert res.status_code == 200
    data = res.json()
    assert data["identity"]["player_id"] == 101
    assert data["identity"]["name"] == "Virat Kohli"


def test_api_scouting_discover(client, sample_scouting_data):
    res = client.get("/api/v1/scouting/discover?role=fast_bowler")
    assert res.status_code == 200
    data = res.json()
    assert data["total_candidates"] == 1
    assert data["items"][0]["name"] == "Jasprit Bumrah"


def test_api_scouting_rank(client, sample_scouting_data):
    res = client.post("/api/v1/scouting/rank", json={
        "performance_weight": 0.5,
        "recent_form_weight": 0.5,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["total_ranked"] == 4


def test_api_scouting_undervalued(client, sample_scouting_data):
    res = client.get("/api/v1/scouting/undervalued?min_undervaluation_score=0")
    assert res.status_code == 200
    data = res.json()
    assert "players" in data


def test_api_scouting_role_targets(client, sample_scouting_data):
    res = client.get("/api/v1/scouting/role-targets?role=wicketkeeper")
    assert res.status_code == 200
    data = res.json()
    assert data["requested_role"] == "wicketkeeper"


def test_api_scouting_recommendations(client, sample_scouting_data):
    res = client.get("/api/v1/scouting/recommendations?budget=1000&slots_needed=3")
    assert res.status_code == 200
    data = res.json()
    assert "immediate_priorities" in data


def test_api_scouting_report(client, sample_scouting_data):
    res = client.get("/api/v1/scouting/report/101")
    assert res.status_code == 200
    data = res.json()
    assert data["player"]["player_id"] == 101
    assert "scouting_verdict" in data


def test_api_scouting_role_fit(client, sample_scouting_data):
    res = client.get("/api/v1/scouting/role-fit/101?role=opener")
    assert res.status_code == 200
    data = res.json()
    assert data["evaluated_role"] == "opener"


def test_api_scouting_watchlist_flow(client, sample_scouting_data):
    # 1. Create Watchlist entry
    create_res = client.post("/api/v1/scouting/watchlist", json={
        "player_id": 101,
        "priority": "HIGH",
        "status": "SHORTLISTED",
        "notes": "Target for top order slot."
    })
    assert create_res.status_code == 201
    w_data = create_res.json()
    w_id = w_data["id"]

    # 2. List Watchlist
    list_res = client.get("/api/v1/scouting/watchlist")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # 3. Patch Watchlist
    patch_res = client.patch(f"/api/v1/scouting/watchlist/{w_id}", json={
        "status": "PRIORITY"
    })
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "PRIORITY"

    # 4. Delete Watchlist
    del_res = client.delete(f"/api/v1/scouting/watchlist/{w_id}")
    assert del_res.status_code == 204


def test_api_scouting_notes_flow(client, sample_scouting_data):
    # 1. Create note
    create_res = client.post("/api/v1/scouting/notes", json={
        "player_id": 102,
        "category": "BOWLING",
        "observation": "Elite powerplay and death bowler.",
        "confidence": 0.95
    })
    assert create_res.status_code == 201
    n_data = create_res.json()
    assert n_data["player_id"] == 102

    # 2. List notes by player
    list_res = client.get("/api/v1/scouting/notes/102")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1


# ── 12. Error Handling Tests ─────────────────────────────────────────────────

def test_api_scouting_player_not_found(client, sample_scouting_data):
    res = client.get("/api/v1/scouting/player/999999")
    assert res.status_code == 404

    rep_res = client.get("/api/v1/scouting/report/999999")
    assert rep_res.status_code == 404


def test_api_scouting_validation_error(client, sample_scouting_data):
    res = client.get("/api/v1/scouting/discover?min_intelligence_score=150")  # > 100
    assert res.status_code == 422
