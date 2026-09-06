"""
Tests for Player Entity Creation, Role Validation, and Filtering
"""
from datetime import date
import pytest
from app.models.enums import PlayerRole
from app.schemas.player import PlayerCreate
from app.services.player_service import PlayerService


def test_player_creation_and_validation(db_session):
    player_in = PlayerCreate(
        name="Virat Kohli",
        short_name="V Kohli",
        role=PlayerRole.BATTER,
        batting_style="Right-hand bat",
        bowling_style="Right-arm medium",
        nationality="India",
        date_of_birth=date(1988, 11, 5),
        is_wicketkeeper=False,
    )
    player = PlayerService.create_player(db_session, player_in)

    assert player.id is not None
    assert player.name == "Virat Kohli"
    assert player.role == PlayerRole.BATTER
    assert player.is_wicketkeeper is False
    assert player.is_active is True


def test_player_filtering_by_role_and_nationality(db_session):
    PlayerService.create_player(
        db_session,
        PlayerCreate(name="Jasprit Bumrah", role=PlayerRole.FAST_BOWLER, nationality="India"),
    )
    PlayerService.create_player(
        db_session,
        PlayerCreate(name="Rashid Khan", role=PlayerRole.SPINNER, nationality="Afghanistan"),
    )

    items, total = PlayerService.get_players(db_session, role=PlayerRole.FAST_BOWLER)
    assert total >= 1
    assert any(p.name == "Jasprit Bumrah" for p in items)

    items_afg, total_afg = PlayerService.get_players(db_session, nationality="Afghanistan")
    assert total_afg >= 1
    assert any(p.name == "Rashid Khan" for p in items_afg)


def test_player_search_case_insensitive(db_session):
    PlayerService.create_player(
        db_session,
        PlayerCreate(name="Rohit Sharma", short_name="R Sharma", role=PlayerRole.BATTER),
    )

    # Full name partial search
    items_search, total_search = PlayerService.get_players(db_session, search="rohit")
    assert total_search >= 1
    assert any(p.name == "Rohit Sharma" for p in items_search)

    # Short name search
    items_short, total_short = PlayerService.get_players(db_session, search="sharma")
    assert total_short >= 1
    assert any(p.name == "Rohit Sharma" for p in items_short)
