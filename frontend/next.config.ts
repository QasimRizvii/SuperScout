import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable React Strict Mode for better development warnings
  reactStrictMode: true,

  // Output standalone build for Docker deployment
  output: "standalone",

  // Expose environment variables to the browser
  // Only variables prefixed with NEXT_PUBLIC_ are exposed automatically,
  // but we list them here for documentation clarity.
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  },

  // Image optimization — add external domains here as needed in Phase 2+
  images: {
    domains: [],
  },
};

export default nextConfig;
