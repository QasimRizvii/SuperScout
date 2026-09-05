import type { Metadata } from "next";
import { Swords } from "lucide-react";

import { PlaceholderPage } from "@/components/dashboard/PlaceholderPage";

export const metadata: Metadata = {
  title: "Matchups",
  description: "Batter-bowler matchup analysis — coming soon.",
};

export default function MatchupsPage() {
  return (
    <PlaceholderPage
      title="Matchup Engine"
      subtitle="Batter vs. bowler matchup analysis and tactical recommendations"
      icon={Swords}
      phase="Phase 7 — Match Intelligence"
      accentColor="text-orange-400"
      description="The Matchup Engine will analyse historical batter-bowler confrontations to identify favourable and unfavourable matchups. Phase-wise, venue-specific, and condition-adjusted matchup scores will drive bowling plan recommendations and batting order decisions."
      plannedCapabilities={[
        "Historical matchup records",
        "Batter weakness profiling",
        "Bowler strength analysis",
        "Phase-specific matchup scoring",
        "Venue-adjusted matchup data",
        "Bowling plan recommendations",
        "Batting order insights",
        "Risk level assessment",
      ]}
    />
  );
}
