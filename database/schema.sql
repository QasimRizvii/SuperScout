-- SuperScout Database — Phase 2 Schema Definition
-- ─────────────────────────────────────────────────────────────────────────────
-- Complete relational DDL for SuperScout Phase 2: Cricket Data Foundation.
-- Keeps SQL schema and SQLAlchemy models 100% consistent.
-- ─────────────────────────────────────────────────────────────────────────────

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. PLAYERS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    short_name VARCHAR(100),
    role VARCHAR(50) NOT NULL DEFAULT 'batter',
    batting_style VARCHAR(100),
    bowling_style VARCHAR(100),
    nationality VARCHAR(100),
    date_of_birth DATE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_players_name ON players (name);
CREATE INDEX IF NOT EXISTS ix_players_role ON players (role);
CREATE INDEX IF NOT EXISTS ix_players_nationality ON players (nationality);

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. TEAMS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    short_name VARCHAR(100),
    abbreviation VARCHAR(20),
    city VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_teams_name ON teams (name);
CREATE INDEX IF NOT EXISTS ix_teams_abbreviation ON teams (abbreviation);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. VENUES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS venues (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    city VARCHAR(100),
    country VARCHAR(100),
    capacity INT,
    pitch_type VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_venues_name ON venues (name);
CREATE INDEX IF NOT EXISTS ix_venues_city ON venues (city);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4. MATCHES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(100) UNIQUE,
    season VARCHAR(50) NOT NULL,
    match_date DATE NOT NULL,
    match_type VARCHAR(20) NOT NULL DEFAULT 'T20',
    venue_id INT NOT NULL REFERENCES venues(id) ON DELETE RESTRICT,
    team_1_id INT NOT NULL REFERENCES teams(id) ON DELETE RESTRICT,
    team_2_id INT NOT NULL REFERENCES teams(id) ON DELETE RESTRICT,
    winner_team_id INT REFERENCES teams(id) ON DELETE SET NULL,
    result_description VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_matches_external_id ON matches (external_id);
CREATE INDEX IF NOT EXISTS ix_matches_season ON matches (season);
CREATE INDEX IF NOT EXISTS ix_matches_match_date ON matches (match_date);
CREATE INDEX IF NOT EXISTS ix_matches_venue_id ON matches (venue_id);
CREATE INDEX IF NOT EXISTS ix_matches_team_1_id ON matches (team_1_id);
CREATE INDEX IF NOT EXISTS ix_matches_team_2_id ON matches (team_2_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 5. INNINGS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS innings (
    id SERIAL PRIMARY KEY,
    match_id INT NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    innings_number INT NOT NULL,
    batting_team_id INT NOT NULL REFERENCES teams(id) ON DELETE RESTRICT,
    bowling_team_id INT NOT NULL REFERENCES teams(id) ON DELETE RESTRICT,
    total_runs INT NOT NULL DEFAULT 0,
    wickets INT NOT NULL DEFAULT 0,
    overs DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_match_innings_number UNIQUE (match_id, innings_number)
);

CREATE INDEX IF NOT EXISTS ix_innings_match_id ON innings (match_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 6. BATTING PERFORMANCES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS batting_performances (
    id SERIAL PRIMARY KEY,
    match_id INT NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    innings_id INT NOT NULL REFERENCES innings(id) ON DELETE CASCADE,
    player_id INT NOT NULL REFERENCES players(id) ON DELETE RESTRICT,
    team_id INT NOT NULL REFERENCES teams(id) ON DELETE RESTRICT,
    batting_position INT,
    runs INT NOT NULL DEFAULT 0,
    balls_faced INT NOT NULL DEFAULT 0,
    fours INT NOT NULL DEFAULT 0,
    sixes INT NOT NULL DEFAULT 0,
    strike_rate DOUBLE PRECISION,
    dismissal_type VARCHAR(50),
    dismissed_by_player_id INT REFERENCES players(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_batting_performances_match_id ON batting_performances (match_id);
CREATE INDEX IF NOT EXISTS ix_batting_performances_innings_id ON batting_performances (innings_id);
CREATE INDEX IF NOT EXISTS ix_batting_performances_player_id ON batting_performances (player_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 7. BOWLING PERFORMANCES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bowling_performances (
    id SERIAL PRIMARY KEY,
    match_id INT NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    innings_id INT NOT NULL REFERENCES innings(id) ON DELETE CASCADE,
    player_id INT NOT NULL REFERENCES players(id) ON DELETE RESTRICT,
    team_id INT NOT NULL REFERENCES teams(id) ON DELETE RESTRICT,
    overs DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    balls_bowled INT NOT NULL DEFAULT 0,
    maidens INT NOT NULL DEFAULT 0,
    runs_conceded INT NOT NULL DEFAULT 0,
    wickets INT NOT NULL DEFAULT 0,
    wides INT NOT NULL DEFAULT 0,
    no_balls INT NOT NULL DEFAULT 0,
    economy DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_bowling_performances_match_id ON bowling_performances (match_id);
CREATE INDEX IF NOT EXISTS ix_bowling_performances_innings_id ON bowling_performances (innings_id);
CREATE INDEX IF NOT EXISTS ix_bowling_performances_player_id ON bowling_performances (player_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 8. PLAYER MATCHUPS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS player_matchups (
    id SERIAL PRIMARY KEY,
    batter_id INT NOT NULL REFERENCES players(id) ON DELETE RESTRICT,
    bowler_id INT NOT NULL REFERENCES players(id) ON DELETE RESTRICT,
    matches INT NOT NULL DEFAULT 0,
    balls INT NOT NULL DEFAULT 0,
    runs INT NOT NULL DEFAULT 0,
    dismissals INT NOT NULL DEFAULT 0,
    fours INT NOT NULL DEFAULT 0,
    sixes INT NOT NULL DEFAULT 0,
    strike_rate DOUBLE PRECISION,
    average DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_batter_bowler_matchup UNIQUE (batter_id, bowler_id)
);

CREATE INDEX IF NOT EXISTS ix_player_matchups_batter_id ON player_matchups (batter_id);
CREATE INDEX IF NOT EXISTS ix_player_matchups_bowler_id ON player_matchups (bowler_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 9. AUCTIONS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS auctions (
    id SERIAL PRIMARY KEY,
    season VARCHAR(50) NOT NULL,
    auction_name VARCHAR(150) NOT NULL,
    auction_date DATE,
    auction_type VARCHAR(20) NOT NULL DEFAULT 'mega',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_auctions_season ON auctions (season);
CREATE INDEX IF NOT EXISTS ix_auctions_auction_type ON auctions (auction_type);

-- ─────────────────────────────────────────────────────────────────────────────
-- 10. AUCTION TRANSACTIONS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS auction_transactions (
    id SERIAL PRIMARY KEY,
    auction_id INT NOT NULL REFERENCES auctions(id) ON DELETE CASCADE,
    player_id INT NOT NULL REFERENCES players(id) ON DELETE RESTRICT,
    team_id INT REFERENCES teams(id) ON DELETE SET NULL,
    base_price DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    final_price DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    status VARCHAR(20) NOT NULL DEFAULT 'sold',
    purse_before DOUBLE PRECISION,
    purse_after DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_auction_transactions_auction_id ON auction_transactions (auction_id);
CREATE INDEX IF NOT EXISTS ix_auction_transactions_player_id ON auction_transactions (player_id);
CREATE INDEX IF NOT EXISTS ix_auction_transactions_status ON auction_transactions (status);
