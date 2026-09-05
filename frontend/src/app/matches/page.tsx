import type { Metadata } from "next";
import { Activity } from "lucide-react";

import { PlaceholderPage } from "@/components/dashboard/PlaceholderPage";

export const metadata: Metadata = {
  title: "Match Intelligence",
  description: "Opponent and venue analysis module — coming soon.",
};

export default function MatchesPage() {
  return (
    <PlaceholderPage
      title="Match Intelligence"
      subtitle="Opponent analysis, venue intelligence, and match preparation"
      icon={Activity}
      phase="Phase 7 — Match Intelligence"
      accentColor="text-rose-400"
      description="Match Intelligence will analyse the opposition, venue characteristics, and match conditions to inform pre-match decisions. It will evaluate opponent batting lineups, bowling attacks, batter weaknesses, and bowler strengths to provide match-specific strategic recommendations."
      plannedCapabilities={[
        "Opponent batting lineup analysis",
        "Opponent bowling attack evaluation",
        "Batter weakness profiling",
        "Bowler strength assessment",
        "Venue and pitch analysis",
        "Phase-wise opponent breakdown",
        "Batter-bowler matchup identification",
        "Pre-match strategic recommendations",
      ]}
    />
  );
}
