/**
 * SuperScout UI — StatusBadge
 *
 * A coloured dot + label indicating a live status.
 * Used for backend connectivity, database status, module readiness, etc.
 */
import React from "react";

export type StatusVariant =
  | "connected"
  | "disconnected"
  | "loading"
  | "healthy"
  | "unavailable"
  | "coming-soon"
  | "active";

interface StatusBadgeProps {
  status: StatusVariant;
  label?: string;
  size?: "sm" | "md";
  className?: string;
}

const statusConfig: Record<
  StatusVariant,
  { dotClass: string; textClass: string; defaultLabel: string }
> = {
  connected: {
    dotClass: "bg-emerald-400",
    textClass: "text-emerald-400",
    defaultLabel: "Connected",
  },
  healthy: {
    dotClass: "bg-emerald-400",
    textClass: "text-emerald-400",
    defaultLabel: "Healthy",
  },
  active: {
    dotClass: "bg-emerald-400",
    textClass: "text-emerald-400",
    defaultLabel: "Active",
  },
  disconnected: {
    dotClass: "bg-red-400",
    textClass: "text-red-400",
    defaultLabel: "Disconnected",
  },
  unavailable: {
    dotClass: "bg-red-400",
    textClass: "text-red-400",
    defaultLabel: "Unavailable",
  },
  loading: {
    dotClass: "bg-amber-400 animate-pulse",
    textClass: "text-amber-400",
    defaultLabel: "Checking...",
  },
  "coming-soon": {
    dotClass: "bg-blue-400",
    textClass: "text-blue-400",
    defaultLabel: "Coming Soon",
  },
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  label,
  size = "md",
  className = "",
}) => {
  const config = statusConfig[status];
  const dotSize = size === "sm" ? "w-1.5 h-1.5" : "w-2 h-2";
  const textSize = size === "sm" ? "text-xs" : "text-sm";

  return (
    <span
      className={`inline-flex items-center gap-1.5 ${className}`}
      role="status"
      aria-label={label ?? config.defaultLabel}
    >
      <span
        className={`${dotSize} rounded-full flex-shrink-0 ${config.dotClass}`}
        aria-hidden="true"
      />
      <span className={`${textSize} font-medium ${config.textClass}`}>
        {label ?? config.defaultLabel}
      </span>
    </span>
  );
};
