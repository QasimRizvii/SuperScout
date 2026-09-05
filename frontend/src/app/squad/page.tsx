import type { Metadata } from "next";
import { Target } from "lucide-react";

import { PlaceholderPage } from "@/components/dashboard/PlaceholderPage";

export const metadata: Metadata = {
  title: "Squad Intelligence",
  description: "Squad analysis and gap detection module — coming soon.",
};

export default function SquadPage() {
  return (
    <PlaceholderPage
      title="Squad Intelligence"
      subtitle="Squad analysis, gap detection, and auction target prioritisation"
      icon={Target}
      phase="Phase 4 — Squad Intelligence"
      accentColor="text-violet-400"
      description="Squad Intelligence will analyse the composition of a franchise's current squad and identify weaknesses. It will assess batting depth, bowling resources, role coverage, overseas balance, and backup strength to produce a prioritised list of roles to fill in the auction."
      plannedCapabilities={[
        "Squad composition analysis",
        "Role gap detection",
        "Batting depth assessment",
        "Bowling resource analysis",
        "Overseas balance evaluation",
        "Role priority scoring",
        "Redundancy detection",
        "Auction target prioritisation",
      ]}
    />
  );
}
