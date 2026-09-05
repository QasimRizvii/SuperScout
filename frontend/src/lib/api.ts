/**
 * SuperScout Frontend — API Client
 *
 * Centralised fetch wrapper that all frontend modules use to communicate
 * with the FastAPI backend.
 *
 * - Base URL is configured via NEXT_PUBLIC_API_URL environment variable.
 * - All errors are normalised into ApiError objects.
 * - Never hardcode connection status — always derive it from the actual API.
 */
import type { ApiError, HealthResponse } from "@/types/api";

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

// ── API Functions ─────────────────────────────────────────────────────────────

/**
 * Fetch the backend health status.
 *
 * Returns a HealthResponse if the API is reachable, or throws ApiError.
 * The frontend health hook uses this to determine connection status.
 */
export async function checkHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>("/api/v1/health");
}

// Export base URL for use in other client modules
export { API_BASE_URL };
