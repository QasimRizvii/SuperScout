import type { Metadata } from "next";
import { Users } from "lucide-react";

import { PlaceholderPage } from "@/components/dashboard/PlaceholderPage";

export const metadata: Metadata = {
  title: "Player Intelligence",
  description: "Player analytics and profiling module — coming soon.",
};

export default function PlayersPage() {
  return (
    <PlaceholderPage
      title="Player Intelligence"
      subtitle="Deep player analysis, ratings, and team-fit scoring"
      icon={Users}
      phase="Phase 3 — Player Intelligence"
      accentColor="text-blue-400"
      description="Player Intelligence will evaluate players beyond raw statistics. It will analyse batting, bowling, fielding, recent form, phase-wise performance, venue history, batter-bowler matchups, and role suitability to produce a comprehensive player rating and team-fit score for each squad."
      plannedCapabilities={[
        "Batting performance analysis",
        "Bowling performance analysis",
        "Phase-wise breakdown (PP/Middle/Death)",
        "Venue and condition performance",
        "Batter-bowler matchup records",
        "Recent form tracking",
        "Player rating model",
        "Team-fit scoring",
      ]}
    />
  );
}
