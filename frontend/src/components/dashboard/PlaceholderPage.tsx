/**
 * SuperScout — Placeholder Page Component
 *
 * Reusable under-development page for modules that are not yet implemented.
 * Shows the module name, description, planned phase, and planned capabilities.
 */
import React from "react";
import { LucideIcon } from "lucide-react";

import { Header } from "@/components/dashboard/Header";
import { Card, CardBody } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

interface PlaceholderPageProps {
  title: string;
  subtitle: string;
  icon: LucideIcon;
  phase: string;
  description: string;
  plannedCapabilities: string[];
  accentColor?: string;
}

export const PlaceholderPage: React.FC<PlaceholderPageProps> = ({
  title,
  subtitle,
  icon: Icon,
  phase,
  description,
  plannedCapabilities,
  accentColor = "text-slate-400",
}) => {
  return (
    <>
      <Header title={title} subtitle={subtitle} />

      <div className="flex-1 px-8 py-8 animate-fade-in">
        <Card className="max-w-2xl">
          <CardBody className="flex flex-col gap-6">
            {/* Icon + Badge */}
            <div className="flex items-start justify-between">
              <div className="w-14 h-14 rounded-2xl bg-white/[0.04] border border-white/[0.08] flex items-center justify-center">
                <Icon className={`w-7 h-7 ${accentColor}`} />
              </div>
              <div className="flex flex-col items-end gap-2">
                <Badge variant="coming-soon">Under Development</Badge>
                <span className="text-xs text-slate-600">{phase}</span>
              </div>
            </div>

            {/* Description */}
            <div>
              <h2 className="text-xl font-bold text-white mb-2">{title}</h2>
              <p className="text-slate-400 text-sm leading-relaxed">
                {description}
              </p>
            </div>

            {/* Planned Capabilities */}
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
                Planned Capabilities
              </p>
              <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {plannedCapabilities.map((capability) => (
                  <li key={capability} className="flex items-center gap-2 text-sm text-slate-400">
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-600 flex-shrink-0" />
                    {capability}
                  </li>
                ))}
              </ul>
            </div>

            {/* Status Note */}
            <div className="rounded-xl border border-blue-500/20 bg-blue-500/5 px-4 py-3">
              <p className="text-xs text-blue-400 leading-relaxed">
                <span className="font-semibold">Development status:</span> This
                module will be implemented in{" "}
                <span className="font-semibold">{phase}</span>. No cricket data
                or statistics are available yet. Data will be populated once the
                cricket data pipeline is implemented in Phase 2.
              </p>
            </div>
          </CardBody>
        </Card>
      </div>
    </>
  );
};
