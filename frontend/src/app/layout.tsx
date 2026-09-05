import type { Metadata } from "next";
import { Inter } from "next/font/google";

import { Sidebar } from "@/components/dashboard/Sidebar";
import "./globals.css";

// ── Font ────────────────────────────────────────────────────────────────────
const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

// ── Metadata ─────────────────────────────────────────────────────────────────
export const metadata: Metadata = {
  title: {
    default: "SuperScout — Cricket Intelligence Platform",
    template: "%s | SuperScout",
  },
  description:
    "AI-powered cricket auction and match intelligence platform. Scout smarter, build stronger, play better.",
  keywords: [
    "cricket",
    "IPL",
    "auction",
    "analytics",
    "player intelligence",
    "squad building",
    "match strategy",
  ],
  robots: {
    index: false, // Private platform — do not index
    follow: false,
  },
};

// ── Root Layout ───────────────────────────────────────────────────────────────
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="flex h-screen overflow-hidden bg-[#050d1a]">
        {/* Sidebar navigation */}
        <Sidebar />

        {/* Main content area */}
        <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">
          {children}
        </main>
      </body>
    </html>
  );
}
