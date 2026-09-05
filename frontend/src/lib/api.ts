/**
 * SuperScout Frontend — API Client
 *
 * Centralised fetch wrapper that all frontend modules use to communicate
 * with the FastAPI backend.
 */
import type {
  ApiError,
  HealthResponse,
  PaginatedResponse,
  Player,
  Team,
  Venue,
  Match,
  Auction,
} from "@/types/api";

// ── Base URL ──────────────────────────────────────────────────────────────────
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ── Generic Fetch Wrapper ─────────────────────────────────────────────────────

interface FetchOptions extends RequestInit {
  timeoutMs?: number;
}

/**
 * Fetch a JSON response from the API.
 *
 * @throws {ApiError} if the request fails or the server returns a non-2xx status.
 */
async function apiFetch<T>(
  path: string,
  options: FetchOptions = {}
): Promise<T> {
  const { timeoutMs = 5000, ...fetchOptions } = options;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...fetchOptions,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...fetchOptions.headers,
      },
    });

    if (!response.ok) {
      let errorDetail = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const errorBody = await response.json();
        errorDetail = errorBody.detail ?? errorDetail;
      } catch {
        // Response body wasn't valid JSON — use the status text
      }
      throw { detail: errorDetail, status_code: response.status } as ApiError;
    }

    return response.json() as Promise<T>;
  } catch (err) {
    if ((err as Error).name === "AbortError") {
      throw {
        detail: "Request timed out. The API may be unavailable.",
      } as ApiError;
    }
    // Re-throw structured ApiErrors; wrap unexpected errors
    if ((err as ApiError).detail) {
      throw err;
    }
    throw {
      detail: "Unable to connect to the SuperScout API.",
    } as ApiError;
  } finally {
    clearTimeout(timeoutId);
  }
}

// ── Health API ────────────────────────────────────────────────────────────────

export async function checkHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>("/api/v1/health");
}

// ── Phase 2 Cricket Data API Functions ────────────────────────────────────────

export async function getPlayers(
  params: { page?: number; page_size?: number; name?: string; role?: string } = {}
): Promise<PaginatedResponse<Player>> {
  const query = new URLSearchParams();
  if (params.page) query.set("page", params.page.toString());
  if (params.page_size) query.set("page_size", params.page_size.toString());
  if (params.name) query.set("name", params.name);
  if (params.role) query.set("role", params.role);
  const path = `/api/v1/players${query.toString() ? `?${query.toString()}` : ""}`;
  return apiFetch<PaginatedResponse<Player>>(path);
}

export async function getTeams(
  params: { page?: number; page_size?: number; name?: string } = {}
): Promise<PaginatedResponse<Team>> {
  const query = new URLSearchParams();
  if (params.page) query.set("page", params.page.toString());
  if (params.page_size) query.set("page_size", params.page_size.toString());
  if (params.name) query.set("name", params.name);
  const path = `/api/v1/teams${query.toString() ? `?${query.toString()}` : ""}`;
  return apiFetch<PaginatedResponse<Team>>(path);
}

export async function getVenues(
  params: { page?: number; page_size?: number; city?: string } = {}
): Promise<PaginatedResponse<Venue>> {
  const query = new URLSearchParams();
  if (params.page) query.set("page", params.page.toString());
  if (params.page_size) query.set("page_size", params.page_size.toString());
  if (params.city) query.set("city", params.city);
  const path = `/api/v1/venues${query.toString() ? `?${query.toString()}` : ""}`;
  return apiFetch<PaginatedResponse<Venue>>(path);
}

export async function getMatches(
  params: { page?: number; page_size?: number; season?: string } = {}
): Promise<PaginatedResponse<Match>> {
  const query = new URLSearchParams();
  if (params.page) query.set("page", params.page.toString());
  if (params.page_size) query.set("page_size", params.page_size.toString());
  if (params.season) query.set("season", params.season);
  const path = `/api/v1/matches${query.toString() ? `?${query.toString()}` : ""}`;
  return apiFetch<PaginatedResponse<Match>>(path);
}

export async function getAuctions(
  params: { page?: number; page_size?: number; season?: string } = {}
): Promise<PaginatedResponse<Auction>> {
  const query = new URLSearchParams();
  if (params.page) query.set("page", params.page.toString());
  if (params.page_size) query.set("page_size", params.page_size.toString());
  if (params.season) query.set("season", params.season);
  const path = `/api/v1/auctions${query.toString() ? `?${query.toString()}` : ""}`;
  return apiFetch<PaginatedResponse<Auction>>(path);
}

// Export base URL
export { API_BASE_URL };
