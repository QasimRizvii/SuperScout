import type { Metadata } from "next";
import { Zap } from "lucide-react";

import { PlaceholderPage } from "@/components/dashboard/PlaceholderPage";

export const metadata: Metadata = {
  title: "Super Over Intelligence",
  description: "Super Over batter and bowler selection engine — coming soon.",
};

export default function SuperOverPage() {
  return (
    <PlaceholderPage
      title="Super Over Intelligence"
      subtitle="Optimal batter selection and bowler choice for Super Over situations"
      icon={Zap}
      phase="Phase 9 — Super Over"
      accentColor="text-yellow-400"
      description="The Super Over Intelligence engine will provide data-driven recommendations for both batting and bowling in a Super Over. It will consider matchup data, power hitting records, bowler precision under pressure, opponent batter profiles, and simulation results to recommend the optimal Super Over combination."
      plannedCapabilities={[
        "Best 3 batters selection",
        "Optimal bowler recommendation",
        "Opponent-specific matchup analysis",
        "Power hitting assessment",
        "Yorker and boundary prevention analysis",
        "Pressure performance records",
        "Super Over simulation",
        "Scenario-based recommendations",
      ]}
    />
  );
}
