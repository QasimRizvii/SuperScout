"use client";

/**
 * SuperScout Frontend — useHealth Hook
 *
 * Polls the backend health endpoint and returns the current connectivity state.
 * The status is never hardcoded — it always reflects the actual API response.
 */
import { useCallback, useEffect, useState } from "react";

import { checkHealth } from "@/lib/api";
import type { HealthResponse } from "@/types/api";

export type ConnectionStatus = "connected" | "disconnected" | "loading";

export interface UseHealthResult {
  /** Current connection status derived from the API response. */
  connectionStatus: ConnectionStatus;
  /** The full health response, or null if unavailable. */
  health: HealthResponse | null;
  /** Whether the initial check is still in progress. */
  isLoading: boolean;
  /** Error message if the last check failed. */
  error: string | null;
  /** Manually trigger a health re-check. */
  refresh: () => void;
}

/** How often to re-check health in milliseconds. */
const POLL_INTERVAL_MS = 30_000;

export function useHealth(): UseHealthResult {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHealth = useCallback(async () => {
    try {
      const data = await checkHealth();
      setHealth(data);
      setError(null);
    } catch (err) {
      const apiError = err as { detail?: string };
      setError(apiError.detail ?? "Backend is unavailable.");
      setHealth(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();

    // Poll on an interval so the status updates automatically
    const interval = setInterval(fetchHealth, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [fetchHealth]);

  const connectionStatus: ConnectionStatus = isLoading
    ? "loading"
    : health !== null
      ? "connected"
      : "disconnected";

  return {
    connectionStatus,
    health,
    isLoading,
    error,
    refresh: fetchHealth,
  };
}
