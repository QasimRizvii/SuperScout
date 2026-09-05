/**
 * SuperScout UI — Card
 *
 * Reusable glassmorphism card with optional header, footer, and hover variants.
 */
import React from "react";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  /** Whether to add a hover elevation effect */
  hoverable?: boolean;
  /** Optional top border accent colour class */
  accentColor?: string;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = "",
  hoverable = false,
  accentColor,
}) => {
  const baseClass =
    "relative rounded-2xl border border-white/[0.06] bg-white/[0.03] backdrop-blur-sm";
  const hoverClass = hoverable
    ? "transition-all duration-200 hover:border-white/[0.12] hover:bg-white/[0.05] hover:shadow-card-hover cursor-pointer"
    : "";
  const accentClass = accentColor
    ? `before:absolute before:top-0 before:left-0 before:right-0 before:h-px before:rounded-t-2xl before:${accentColor}`
    : "";

  return (
    <div
      className={`${baseClass} ${hoverClass} ${accentClass} ${className}`}
    >
      {children}
    </div>
  );
};

interface CardHeaderProps {
  children: React.ReactNode;
  className?: string;
}

export const CardHeader: React.FC<CardHeaderProps> = ({
  children,
  className = "",
}) => (
  <div className={`px-6 pt-6 pb-4 border-b border-white/[0.06] ${className}`}>
    {children}
  </div>
);

interface CardBodyProps {
  children: React.ReactNode;
  className?: string;
}

export const CardBody: React.FC<CardBodyProps> = ({
  children,
  className = "",
}) => (
  <div className={`px-6 py-5 ${className}`}>
    {children}
  </div>
);

interface CardFooterProps {
  children: React.ReactNode;
  className?: string;
}

export const CardFooter: React.FC<CardFooterProps> = ({
  children,
  className = "",
}) => (
  <div className={`px-6 py-4 border-t border-white/[0.06] ${className}`}>
    {children}
  </div>
);
