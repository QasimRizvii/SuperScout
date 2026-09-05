/**
 * SuperScout — Module Card
 *
 * Card representing a single intelligence module on the dashboard.
 * Shows the module name, description, and development status.
 */
import React from "react";
import Link from "next/link";
import { ArrowRight, LucideIcon } from "lucide-react";

import { Card, CardBody } from "@/components/ui/Card";
import { Badge, BadgeVariant } from "@/components/ui/Badge";

export interface ModuleCardProps {
  title: string;
  description: string;
  href: string;
  icon: LucideIcon;
  status: BadgeVariant;
  statusLabel?: string;
  phase?: string;
  /** Accent gradient class for the top border */
  accentGradient?: string;
}

export const ModuleCard: React.FC<ModuleCardProps> = ({
  title,
  description,
  href,
  icon: Icon,
  status,
  statusLabel,
  phase,
  accentGradient = "from-emerald-500/60 to-blue-500/60",
}) => {
  const isComingSoon = status === "coming-soon" || status === "planned";

  const cardContent = (
    <Card
      hoverable={!isComingSoon || true}
      className="h-full group"
    >
      {/* Top accent line */}
      <div
        className={`absolute top-0 left-0 right-0 h-px rounded-t-2xl bg-gradient-to-r ${accentGradient} opacity-0 group-hover:opacity-100 transition-opacity duration-200`}
      />

      <CardBody className="flex flex-col gap-4 h-full">
        {/* Icon + Status */}
        <div className="flex items-start justify-between">
          <div className="w-10 h-10 rounded-xl bg-white/[0.05] border border-white/[0.08] flex items-center justify-center flex-shrink-0">
            <Icon className="w-5 h-5 text-slate-400 group-hover:text-slate-300 transition-colors" />
          </div>
          <div className="flex flex-col items-end gap-1">
            <Badge variant={status}>
              {statusLabel ?? (status === "coming-soon" ? "Coming Soon" : status)}
            </Badge>
            {phase && (
              <span className="text-[10px] text-slate-600">{phase}</span>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1">
          <h3 className="text-base font-semibold text-slate-200 leading-tight mb-1.5">
            {title}
          </h3>
          <p className="text-sm text-slate-500 leading-relaxed">
            {description}
          </p>
        </div>

        {/* CTA */}
        {!isComingSoon && (
          <div className="flex items-center gap-1.5 text-xs font-medium text-emerald-400 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <span>Open module</span>
            <ArrowRight className="w-3 h-3" />
          </div>
        )}
      </CardBody>
    </Card>
  );

  if (isComingSoon) {
    return <div className="h-full opacity-70">{cardContent}</div>;
  }

  return (
    <Link href={href} className="h-full block">
      {cardContent}
    </Link>
  );
};
