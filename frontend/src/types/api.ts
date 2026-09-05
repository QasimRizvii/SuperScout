/**
 * SuperScout Frontend — API Type Definitions
 *
 * TypeScript interfaces for all API responses consumed by the frontend.
 */

// ── Health ────────────────────────────────────────────────────────────────────

export type DatabaseStatusType = "healthy" | "unavailable";
export type ApiStatusType = "healthy";

export interface DatabaseStatus {
  status: DatabaseStatusType;
  detail?: string;
}

export interface HealthResponse {
  status: ApiStatusType;
  service: string;
  version: string;
  database: DatabaseStatus;
}

// ── Generic Paginated Response ───────────────────────────────────────────────

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ── Error ─────────────────────────────────────────────────────────────────────

export interface ApiError {
  detail: string;
  status_code?: number;
}

// ── Phase 2 Cricket Domain Types ─────────────────────────────────────────────

export type PlayerRole = "batter" | "wicketkeeper" | "all_rounder" | "bowler";
export type MatchType = "T20" | "ODI" | "Test" | "T10" | "Other";
export type AuctionType = "mega" | "mini" | "other";
export type AuctionStatus = "sold" | "unsold" | "retained" | "other";

export interface Player {
  id: number;
  name: string;
  short_name?: string | null;
  role: PlayerRole;
  batting_style?: string | null;
  bowling_style?: string | null;
  nationality?: string | null;
  date_of_birth?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Team {
  id: number;
  name: string;
  short_name?: string | null;
  abbreviation?: string | null;
  city?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Venue {
  id: number;
  name: string;
  city?: string | null;
  country?: string | null;
  capacity?: number | null;
  pitch_type?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Match {
  id: number;
  external_id?: string | null;
  season: string;
  match_date: string;
  match_type: MatchType;
  venue_id: number;
  team_1_id: number;
  team_2_id: number;
  winner_team_id?: number | null;
  result_description?: string | null;
  created_at: string;
  updated_at: string;
  venue?: Venue | null;
  team_1?: Team | null;
  team_2?: Team | null;
  winner_team?: Team | null;
}

export interface Auction {
  id: number;
  season: string;
  auction_name: string;
  auction_date?: string | null;
  auction_type: AuctionType;
  created_at: string;
}
