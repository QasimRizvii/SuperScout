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
    )
    player = PlayerService.create_player(db_session, player_in)

    assert player.id is not None
    assert player.name == "Virat Kohli"
    assert player.role == PlayerRole.BATTER
    assert player.is_active is True


def test_player_filtering_by_role_and_nationality(db_session):
    PlayerService.create_player(
        db_session,
        PlayerCreate(name="Jasprit Bumrah", role=PlayerRole.BOWLER, nationality="India"),
    )
    PlayerService.create_player(
        db_session,
        PlayerCreate(name="Pat Cummins", role=PlayerRole.ALL_ROUNDER, nationality="Australia"),
    )

    items, total = PlayerService.get_players(db_session, role=PlayerRole.BOWLER)
    assert total >= 1
    assert any(p.name == "Jasprit Bumrah" for p in items)

    items_aus, total_aus = PlayerService.get_players(db_session, nationality="Australia")
    assert total_aus >= 1
    assert any(p.name == "Pat Cummins" for p in items_aus)
