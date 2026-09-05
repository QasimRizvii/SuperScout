import type { Metadata } from "next";
import {
  Activity,
  Cpu,
  LayoutDashboard,
  Swords,
  Target,
  Trophy,
  Users,
  Zap,
} from "lucide-react";

import { Header } from "@/components/dashboard/Header";
import { ModuleCard, ModuleCardProps } from "@/components/dashboard/ModuleCard";
import { Card, CardBody } from "@/components/ui/Card";

export const metadata: Metadata = {
  title: "Dashboard — SuperScout",
  description:
    "SuperScout Cricket Intelligence Platform — overview of all intelligence modules.",
};

// ── Module Registry ───────────────────────────────────────────────────────────
const modules: ModuleCardProps[] = [
  {
    title: "Auction Intelligence",
    description:
      "Player valuation, price prediction, maximum bid recommendations, and competitor demand analysis for data-driven auction decisions.",
    href: "/auction",
    icon: Trophy,
    status: "coming-soon",
    phase: "Phase 5",
    accentGradient: "from-amber-500/60 to-orange-500/60",
  },
  {
    title: "Player Intelligence",
    description:
      "Deep player analysis across batting, bowling, and fielding. Phase-wise performance, venue records, matchup history, and player ratings.",
    href: "/players",
    icon: Users,
    status: "coming-soon",
    phase: "Phase 3",
    accentGradient: "from-blue-500/60 to-indigo-500/60",
  },
  {
    title: "Squad Intelligence",
    description:
      "Squad gap detection, role analysis, batting/bowling depth assessment, and auction target prioritisation based on squad composition.",
    href: "/squad",
    icon: Target,
    status: "coming-soon",
    phase: "Phase 4",
    accentGradient: "from-violet-500/60 to-purple-500/60",
  },
  {
    title: "Match Intelligence",
    description:
      "Opponent analysis, venue intelligence, batter-bowler matchups, and opponent-specific Playing XI recommendations.",
    href: "/matches",
    icon: Activity,
    status: "coming-soon",
    phase: "Phase 7",
    accentGradient: "from-rose-500/60 to-pink-500/60",
  },
  {
    title: "Playing XI",
    description:
      "Opponent-specific Playing XI selection optimised for the match conditions, venue characteristics, and available squad.",
    href: "/playing-xi",
    icon: Cpu,
    status: "coming-soon",
    phase: "Phase 7",
    accentGradient: "from-cyan-500/60 to-teal-500/60",
  },
  {
    title: "Matchup Engine",
    description:
      "Batter vs. bowler matchup analysis by phase, venue, and conditions. Tactical recommendations for bowling plans and batting orders.",
    href: "/matchups",
    icon: Swords,
    status: "coming-soon",
    phase: "Phase 7",
    accentGradient: "from-orange-500/60 to-red-500/60",
  },
  {
    title: "Super Over Intelligence",
    description:
      "Dedicated Super Over decision engine. Best batting combination and optimal bowler selection based on matchups and simulation.",
    href: "/super-over",
    icon: Zap,
    status: "coming-soon",
    phase: "Phase 9",
    accentGradient: "from-yellow-500/60 to-amber-500/60",
  },
];

// ── Page ──────────────────────────────────────────────────────────────────────
export default function DashboardPage() {
  return (
    <>
      <Header
        title="Dashboard"
        subtitle="SuperScout Cricket Intelligence Platform"
      />

      <div className="flex-1 px-8 py-8 space-y-8 animate-fade-in">
        {/* ── Platform Overview ──────────────────────────────────────────── */}
        <section aria-labelledby="overview-heading">
          <Card className="border-emerald-500/20 bg-gradient-to-r from-emerald-500/5 to-transparent">
            <CardBody className="flex items-start gap-6">
              <div className="flex-shrink-0 w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center shadow-glow">
                <LayoutDashboard className="w-6 h-6 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <h2
                  id="overview-heading"
                  className="text-xl font-bold text-white mb-1"
                >
                  SuperScout
                </h2>
                <p className="text-slate-400 text-sm leading-relaxed max-w-2xl">
                  AI-powered cricket auction and match intelligence platform.
                  From auction strategy to squad building, Playing XI selection
                  to Super Over decisions — SuperScout brings data-driven
                  intelligence to every stage of the game.
                </p>
                <div className="mt-4 flex flex-wrap gap-3">
                  <span className="inline-flex items-center gap-1.5 text-xs text-slate-500">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                    Foundation complete
                  </span>
                  <span className="inline-flex items-center gap-1.5 text-xs text-slate-500">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                    7 modules in development
                  </span>
                  <span className="inline-flex items-center gap-1.5 text-xs text-slate-500">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                    Phase 1 of 10
                  </span>
                </div>
              </div>
            </CardBody>
          </Card>
        </section>

        {/* ── Intelligence Modules Grid ──────────────────────────────────── */}
        <section aria-labelledby="modules-heading">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2
                id="modules-heading"
                className="text-base font-semibold text-slate-200"
              >
                Intelligence Modules
              </h2>
              <p className="text-sm text-slate-500 mt-0.5">
                All modules are under active development — see phase roadmap
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {modules.map((module) => (
              <div key={module.href} className="h-full">
                <ModuleCard {...module} />
              </div>
            ))}
          </div>
        </section>

        {/* ── Development Roadmap ────────────────────────────────────────── */}
        <section aria-labelledby="roadmap-heading">
          <Card>
            <CardBody>
              <h2
                id="roadmap-heading"
                className="text-base font-semibold text-slate-200 mb-4"
              >
                Development Roadmap
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                {[
                  { phase: "Phase 1", label: "Foundation", status: "active" },
                  { phase: "Phase 2", label: "Cricket Data", status: "next" },
                  {
                    phase: "Phase 3–4",
                    label: "Player & Squad",
                    status: "planned",
                  },
                  {
                    phase: "Phase 5–6",
                    label: "Auction Intelligence",
                    status: "planned",
                  },
                  {
                    phase: "Phase 7–9",
                    label: "Match & Super Over",
                    status: "planned",
                  },
                ].map(({ phase, label, status }) => (
                  <div
                    key={phase}
                    className={`p-3 rounded-xl border ${
                      status === "active"
                        ? "border-emerald-500/30 bg-emerald-500/5"
                        : status === "next"
                          ? "border-blue-500/20 bg-blue-500/5"
                          : "border-white/[0.05] bg-white/[0.02]"
                    }`}
                  >
                    <p
                      className={`text-xs font-semibold mb-0.5 ${
                        status === "active"
                          ? "text-emerald-400"
                          : status === "next"
                            ? "text-blue-400"
                            : "text-slate-500"
                      }`}
                    >
                      {phase}
                    </p>
                    <p className="text-xs text-slate-400">{label}</p>
                    <p
                      className={`text-[10px] mt-1 font-medium uppercase tracking-wider ${
                        status === "active"
                          ? "text-emerald-500"
                          : status === "next"
                            ? "text-blue-500"
                            : "text-slate-600"
                      }`}
                    >
                      {status === "active"
                        ? "In Progress"
                        : status === "next"
                          ? "Up Next"
                          : "Planned"}
                    </p>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        </section>
      </div>
    </>
  );
}
