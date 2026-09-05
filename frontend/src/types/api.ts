/**
 * SuperScout Frontend — API Type Definitions
 *
 * TypeScript interfaces for all API responses consumed by the frontend.
 * Phase 2+ will extend this file with cricket-domain types.
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

// ── Error ─────────────────────────────────────────────────────────────────────

export interface ApiError {
  detail: string;
  status_code?: number;
}

// ── Future Cricket Domain Types (Phase 2+) ────────────────────────────────────
// Player, Squad, Match, Auction types will be added here.
