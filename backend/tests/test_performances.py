"""
Tests for Batting and Bowling Performance Metrics, Non-Negative Validations, and Safe Strike Rate & Economy Computations
"""
import pytest
from pydantic import ValidationError

from app.models.batting import BattingPerformance
from app.models.bowling import BowlingPerformance
from app.schemas.match import BattingPerformanceBase, BowlingPerformanceBase


def test_batting_strike_rate_calculation():
    # Normal strike rate
    sr1 = BattingPerformance.calculate_strike_rate(runs=50, balls_faced=25)
    assert sr1 == 200.0

    # Zero balls faced -> no division by zero
    sr0 = BattingPerformance.calculate_strike_rate(runs=0, balls_faced=0)
    assert sr0 == 0.0


def test_bowling_economy_calculation():
    # 4 overs (24 balls), 24 runs conceded -> 6.00 economy
    econ1 = BowlingPerformance.calculate_economy(runs_conceded=24, balls_bowled=24, overs=4.0)
    assert econ1 == 6.0

    # Zero balls bowled -> no division by zero
    econ0 = BowlingPerformance.calculate_economy(runs_conceded=10, balls_bowled=0, overs=0.0)
    assert econ0 == 0.0


def test_performance_schema_non_negative_validations():
    # Negative runs must fail validation
    with pytest.raises(ValidationError):
        BattingPerformanceBase(
            match_id=1,
            innings_id=1,
            player_id=1,
            team_id=1,
            runs=-5,
            balls_faced=10,
        )

    # Negative overs/runs conceded must fail validation
    with pytest.raises(ValidationError):
        BowlingPerformanceBase(
            match_id=1,
            innings_id=1,
            player_id=1,
            team_id=1,
            overs=-1.0,
            runs_conceded=-10,
        )
