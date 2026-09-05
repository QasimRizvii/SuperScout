"use client";

/**
 * SuperScout — Page Header
 *
 * Top navigation bar with page title and backend status indicator.
 */
import React from "react";

import { BackendStatus } from "./BackendStatus";

interface HeaderProps {
  title: string;
  subtitle?: string;
}

export const Header: React.FC<HeaderProps> = ({ title, subtitle }) => {
  return (
    <header className="sticky top-0 z-10 flex items-center justify-between px-8 py-4 border-b border-white/[0.06] bg-navy-950/90 backdrop-blur-md">
      <div>
        <h1 className="text-lg font-semibold text-white leading-tight">
          {title}
        </h1>
        {subtitle && (
          <p className="text-sm text-slate-500 mt-0.5">{subtitle}</p>
        )}
      </div>
      <BackendStatus />
    </header>
  );
};
