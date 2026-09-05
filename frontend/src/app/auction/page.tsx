import type { Metadata } from "next";
import { Trophy } from "lucide-react";

import { PlaceholderPage } from "@/components/dashboard/PlaceholderPage";

export const metadata: Metadata = {
  title: "Auction Intelligence",
  description: "Player valuation and auction strategy module — coming soon.",
};

export default function AuctionPage() {
  return (
    <PlaceholderPage
      title="Auction Intelligence"
      subtitle="Player valuation, price prediction, and auction strategy"
      icon={Trophy}
      phase="Phase 5 — Auction Intelligence"
      accentColor="text-amber-400"
      description="The Auction Intelligence engine will help franchises make rational, data-driven auction decisions. It will combine player quality, squad requirements, competitor demand, market analysis, and remaining budget to recommend whether to target, bid, or pass on each player."
      plannedCapabilities={[
        "Player valuation modelling",
        "Auction price prediction",
        "Maximum bid calculation",
        "Competitor demand analysis",
        "Hidden gems identification",
        "Budget scenario planning",
        "BUY / PASS / WAIT recommendations",
        "Auction simulation",
      ]}
    />
  );
}
