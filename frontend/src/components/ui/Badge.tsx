/**
 * SuperScout UI — Badge
 *
 * Small inline label pill. Used for module status tags like "Coming Soon".
 */
import React from "react";

export type BadgeVariant =
  | "coming-soon"
  | "active"
  | "beta"
  | "new"
  | "planned";

interface BadgeProps {
  variant?: BadgeVariant;
  children: React.ReactNode;
  className?: string;
}

const variantClass: Record<BadgeVariant, string> = {
  "coming-soon":
    "bg-blue-500/10 text-blue-400 border border-blue-500/20",
  active:
    "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20",
  beta: "bg-amber-500/10 text-amber-400 border border-amber-500/20",
  new: "bg-violet-500/10 text-violet-400 border border-violet-500/20",
  planned: "bg-slate-500/10 text-slate-400 border border-slate-500/20",
};

export const Badge: React.FC<BadgeProps> = ({
  variant = "planned",
  children,
  className = "",
}) => (
  <span
    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold tracking-wide uppercase ${variantClass[variant]} ${className}`}
  >
    {children}
  </span>
);
