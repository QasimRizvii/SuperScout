"use client";

/**
 * SuperScout — Backend Status Indicator
 *
 * Displays real-time backend connectivity status derived from the health API.
 * Status is NEVER hardcoded — it always reflects the actual API response.
 */
import React from "react";

import { useHealth } from "@/hooks/useHealth";
import { StatusBadge } from "@/components/ui/StatusBadge";
import type { StatusVariant } from "@/components/ui/StatusBadge";

export const BackendStatus: React.FC = () => {
  const { connectionStatus, health, error } = useHealth();

  const statusVariant: StatusVariant =
    connectionStatus === "connected"
      ? "connected"
      : connectionStatus === "loading"
        ? "loading"
        : "disconnected";

  const label =
    connectionStatus === "connected"
      ? "Connected"
      : connectionStatus === "loading"
        ? "Checking..."
        : "Disconnected";

  return (
    <div
      className="flex items-center gap-3 px-4 py-2 rounded-xl border border-white/[0.06] bg-white/[0.02]"
      title={
        error
          ? `Backend error: ${error}`
          : health
            ? `SuperScout API v${health.version} — DB: ${health.database.status}`
            : "Checking backend status..."
      }
    >
      <span className="text-xs text-slate-500 font-medium">Backend</span>
      <StatusBadge status={statusVariant} label={label} size="sm" />
    </div>
  );
};
