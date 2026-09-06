"""
SuperScout Backend — Match, Innings, Batting, Bowling Pydantic Schemas
"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import MatchType
from app.schemas.team import TeamResponse
from app.schemas.venue import VenueResponse
from app.schemas.player import PlayerResponse


class BattingPerformanceBase(BaseModel):
    match_id: int
    innings_id: int
    player_id: int
    team_id: int
    batting_position: Optional[int] = Field(None, ge=1)
    runs: int = Field(0, ge=0)
    balls_faced: int = Field(0, ge=0)
    fours: int = Field(0, ge=0)
    sixes: int = Field(0, ge=0)
    dot_balls: int = Field(0, ge=0)
    runs_powerplay: Optional[int] = Field(None, ge=0)
    runs_middle: Optional[int] = Field(None, ge=0)
    runs_death: Optional[int] = Field(None, ge=0)
    strike_rate: Optional[float] = Field(None, ge=0.0)
    dismissal_type: Optional[str] = None
    dismissed_by_player_id: Optional[int] = None
    fielder_player_id: Optional[int] = None


class BattingPerformanceCreate(BattingPerformanceBase):
    pass


class BattingPerformanceResponse(BattingPerformanceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    player: Optional[PlayerResponse] = None
    dismissed_by: Optional[PlayerResponse] = None
    fielder: Optional[PlayerResponse] = None
    boundary_percentage: Optional[float] = None
    balls_per_boundary: Optional[float] = None


class BowlingPerformanceBase(BaseModel):
    match_id: int
    innings_id: int
    player_id: int
    team_id: int
    bowling_position: Optional[int] = Field(None, ge=1)
    overs: float = Field(0.0, ge=0.0)
    balls_bowled: int = Field(0, ge=0)
    maidens: int = Field(0, ge=0)
    runs_conceded: int = Field(0, ge=0)
    wickets: int = Field(0, ge=0)
    wides: int = Field(0, ge=0)
    no_balls: int = Field(0, ge=0)
    dot_balls: int = Field(0, ge=0)
    overs_powerplay: Optional[float] = Field(None, ge=0.0)
    overs_middle: Optional[float] = Field(None, ge=0.0)
    overs_death: Optional[float] = Field(None, ge=0.0)
    economy: Optional[float] = Field(None, ge=0.0)


class BowlingPerformanceCreate(BowlingPerformanceBase):
    pass


class BowlingPerformanceResponse(BowlingPerformanceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    player: Optional[PlayerResponse] = None


class InningsBase(BaseModel):
    match_id: int
    innings_number: int = Field(..., ge=1, le=4)
    batting_team_id: int
    bowling_team_id: int
    total_runs: int = Field(0, ge=0)
    wickets: int = Field(0, ge=0, le=10)
    overs: float = Field(0.0, ge=0.0)
    run_rate: Optional[float] = Field(None, ge=0.0)
    extras: int = Field(0, ge=0)
    powerplay_runs: Optional[int] = Field(None, ge=0)


class InningsCreate(InningsBase):
    pass


class InningsResponse(InningsBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    batting_team: Optional[TeamResponse] = None
    bowling_team: Optional[TeamResponse] = None
    batting_performances: List[BattingPerformanceResponse] = []
    bowling_performances: List[BowlingPerformanceResponse] = []


class MatchBase(BaseModel):
    external_id: Optional[str] = Field(None, max_length=100)
    season: str = Field(..., max_length=50)
    match_date: date
    match_type: MatchType = MatchType.T20
    competition: Optional[str] = Field(None, max_length=100)
    status: str = Field("completed", max_length=50)
    venue_id: int
    team_1_id: int
    team_2_id: int
    winner_team_id: Optional[int] = None
    toss_winner_id: Optional[int] = None
    toss_decision: Optional[str] = Field(None, max_length=20)
    result_description: Optional[str] = Field(None, max_length=255)


class MatchCreate(MatchBase):
    pass


class MatchUpdate(BaseModel):
    external_id: Optional[str] = None
    season: Optional[str] = None
    match_date: Optional[date] = None
    match_type: Optional[MatchType] = None
    competition: Optional[str] = None
    status: Optional[str] = None
    venue_id: Optional[int] = None
    team_1_id: Optional[int] = None
    team_2_id: Optional[int] = None
    winner_team_id: Optional[int] = None
    toss_winner_id: Optional[int] = None
    toss_decision: Optional[str] = None
    result_description: Optional[str] = None


class MatchResponse(MatchBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    venue: Optional[VenueResponse] = None
    team_1: Optional[TeamResponse] = None
    team_2: Optional[TeamResponse] = None
    winner_team: Optional[TeamResponse] = None
    innings: List[InningsResponse] = []
