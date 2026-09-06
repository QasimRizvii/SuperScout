"""
SuperScout Backend — Cricket Data Enums

Centralized Python Enum definitions for domain models, validation, and schemas.
Ensures consistency across database, service layer, and API contracts.
"""
from enum import Enum


class PlayerRole(str, Enum):
    BATTER = "batter"
    WICKETKEEPER_BATTER = "wicketkeeper_batter"
    ALL_ROUNDER = "all_rounder"
    BOWLING_ALL_ROUNDER = "bowling_all_rounder"
    FAST_BOWLER = "fast_bowler"
    MEDIUM_FAST_BOWLER = "medium_fast_bowler"
    SPINNER = "spinner"
    WICKETKEEPER = "wicketkeeper"
    BOWLER = "bowler"


class MatchType(str, Enum):
    T20 = "T20"
    ODI = "ODI"
    TEST = "Test"
    T10 = "T10"
    OTHER = "Other"


class AuctionType(str, Enum):
    MEGA = "mega"
    MINI = "mini"
    OTHER = "other"


class AuctionStatus(str, Enum):
    SOLD = "sold"
    UNSOLD = "unsold"
    RETAINED = "retained"
    OTHER = "other"


class DismissalType(str, Enum):
    BOWLED = "bowled"
    CAUGHT = "caught"
    LBW = "lbw"
    RUN_OUT = "run_out"
    STUMPED = "stumped"
    HIT_WICKET = "hit_wicket"
    RETIRED = "retired"
    NOT_OUT = "not_out"
    OTHER = "other"
