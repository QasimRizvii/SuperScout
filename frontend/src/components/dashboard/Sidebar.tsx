"use client";

/**
 * SuperScout — Sidebar Navigation
 *
 * Left sidebar with SuperScout branding, primary navigation links,
 * and active state management.
 */
import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  ChevronRight,
  Cpu,
  LayoutDashboard,
  Swords,
  Target,
  Trophy,
  Users,
  Zap,
} from "lucide-react";

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  isActive?: boolean;
}

const navItems: NavItem[] = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Auction Intelligence", href: "/auction", icon: Trophy },
  { label: "Player Intelligence", href: "/players", icon: Users },
  { label: "Squad Intelligence", href: "/squad", icon: Target },
  { label: "Match Intelligence", href: "/matches", icon: Activity },
  { label: "Playing XI", href: "/playing-xi", icon: Cpu },
  { label: "Matchups", href: "/matchups", icon: Swords },
  { label: "Super Over", href: "/super-over", icon: Zap },
];

export const Sidebar: React.FC = () => {
  const pathname = usePathname();

  return (
    <aside
      className="w-64 flex-shrink-0 flex flex-col h-screen sticky top-0 border-r border-white/[0.06] bg-navy-900/80 backdrop-blur-sm"
      aria-label="Main navigation"
    >
      {/* ── Brand ─────────────────────────────────────────────────────────── */}
      <div className="px-6 py-6 border-b border-white/[0.06]">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center shadow-glow flex-shrink-0">
            <span className="text-white font-bold text-sm leading-none">S</span>
          </div>
          <div>
            <p className="text-white font-bold text-base leading-tight tracking-tight">
              SuperScout
            </p>
            <p className="text-slate-500 text-xs leading-tight mt-0.5">
              Cricket Intelligence
            </p>
          </div>
        </Link>
      </div>

      {/* ── Navigation ────────────────────────────────────────────────────── */}
      <nav className="flex-1 px-3 py-4 overflow-y-auto" aria-label="Sidebar navigation">
        <p className="px-3 mb-2 text-[10px] font-semibold tracking-widest uppercase text-slate-600">
          Intelligence Modules
        </p>
        <ul className="space-y-0.5" role="list">
          {navItems.map((item) => {
            const isActive =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);
            const Icon = item.icon;

            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={`group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 ${
                    isActive
                      ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                      : "text-slate-400 hover:text-slate-200 hover:bg-white/[0.04] border border-transparent"
                  }`}
                  aria-current={isActive ? "page" : undefined}
                >
                  <Icon
                    className={`w-4 h-4 flex-shrink-0 ${
                      isActive
                        ? "text-emerald-400"
                        : "text-slate-500 group-hover:text-slate-300"
                    }`}
                  />
                  <span className="flex-1 truncate">{item.label}</span>
                  {isActive && (
                    <ChevronRight className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" />
                  )}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* ── Footer ────────────────────────────────────────────────────────── */}
      <div className="px-6 py-4 border-t border-white/[0.06]">
        <p className="text-[11px] text-slate-600 leading-tight">
          Phase 1 — Foundation
        </p>
        <p className="text-[10px] text-slate-700 mt-0.5">
          v1.0.0
        </p>
      </div>
    </aside>
  );
};
