-- SuperScout Database — Foundation Schema
-- ─────────────────────────────────────────────────────────────────────────────
-- Phase 1: Foundation only.
-- This file establishes the database baseline for future cricket schema.
-- Full cricket schema will be implemented in Phase 2: Cricket Data Architecture.
-- ─────────────────────────────────────────────────────────────────────────────

-- Enable UUID generation (used by future models as primary keys)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_trgm for future fuzzy text search on player names, teams, etc.
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ─────────────────────────────────────────────────────────────────────────────
-- PHASE 2 TABLES (to be implemented)
-- ─────────────────────────────────────────────────────────────────────────────
-- The following tables will be created in Phase 2 — Cricket Data Architecture:
--
-- Core Entities:
--   players          — Player profiles, roles, nationality
--   teams            — Franchise / national team information
--   venues           — Cricket grounds with pitch/conditions metadata
--   matches          — Match metadata (format, date, venue, result)
--   innings          — Per-match innings records
--
-- Performance Records:
--   batting_records  — Ball-by-ball and innings batting data
--   bowling_records  — Over-by-over and innings bowling data
--   fielding_records — Catches, run-outs, stumpings
--
-- Auction Domain:
--   auctions         — Auction events (IPL, etc.)
--   auction_lots     — Individual player lots within an auction
--   auction_results  — Sold/unsold outcomes and final prices
--
-- Intelligence Domain:
--   player_ratings   — Computed player ratings and form scores
--   squad_snapshots  — Point-in-time squad compositions
--   matchups         — Historical batter-bowler matchup records
-- ─────────────────────────────────────────────────────────────────────────────
