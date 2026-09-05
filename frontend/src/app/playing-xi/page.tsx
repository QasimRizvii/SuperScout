import type { Metadata } from "next";
import { Cpu } from "lucide-react";

import { PlaceholderPage } from "@/components/dashboard/PlaceholderPage";

export const metadata: Metadata = {
  title: "Playing XI",
  description: "Opponent-specific Playing XI recommendation — coming soon.",
};

export default function PlayingXIPage() {
  return (
    <PlaceholderPage
      title="Playing XI"
      subtitle="Opponent-specific team selection optimised for match conditions"
      icon={Cpu}
      phase="Phase 7 — Match Intelligence"
      accentColor="text-cyan-400"
      description="The Playing XI module will recommend the optimal 11-player lineup for a specific opponent, venue, and conditions. Rather than selecting a static 'best XI', it will optimise team composition based on opponent analysis, matchup data, squad constraints, and simulation results."
      plannedCapabilities={[
        "Opponent-specific XI optimisation",
        "Role balance constraints",
        "Matchup-driven selection",
        "Venue condition adjustments",
        "Overseas slot optimisation",
        "Specialist vs. all-rounder trade-offs",
        "Selection rationale (explainable AI)",
        "Alternative XI suggestions",
      ]}
    />
  );
}
