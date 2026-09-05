import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // ── SuperScout Design Tokens ─────────────────────────────────────────
        // Dark navy base palette
        navy: {
          950: "#050d1a",
          900: "#0a1628",
          800: "#0f2040",
          700: "#152b56",
          600: "#1c3a70",
        },
        // Slate neutral palette
        slate: {
          850: "#0f172a",
        },
        // Green accent (primary action / positive state)
        emerald: {
          400: "#34d399",
          500: "#10b981",
          600: "#059669",
        },
        // Amber highlight (warnings / secondary actions)
        amber: {
          400: "#fbbf24",
          500: "#f59e0b",
        },
        // Status colors
        status: {
          healthy: "#34d399",
          unavailable: "#f87171",
          pending: "#fbbf24",
          comingsoon: "#60a5fa",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
        "glass-gradient":
          "linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)",
      },
      borderRadius: {
        "2xl": "1rem",
        "3xl": "1.5rem",
      },
      boxShadow: {
        card: "0 4px 24px rgba(0, 0, 0, 0.3), 0 1px 4px rgba(0, 0, 0, 0.2)",
        "card-hover":
          "0 8px 32px rgba(0, 0, 0, 0.4), 0 2px 8px rgba(0, 0, 0, 0.3)",
        glow: "0 0 20px rgba(52, 211, 153, 0.2)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "fade-in": "fadeIn 0.3s ease-in-out",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0", transform: "translateY(4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
