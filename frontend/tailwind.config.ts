import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        lore: {
          charcoal: "#1f2321",
          ivory: "#f6f0e3",
          terracotta: "#b05b3b",
          forest: "#375043",
          gold: "#b89950",
          smoke: "#6a6d70",
          slate: "#4e5d63",
          ember: "#d26f34",
          night: "#111416",
          ocean: "#1f6f8b",
          turquoise: "#2ea5a0",
          indigo: "#2a3b73",
          sunrise: "#ef8a3d"
        }
      },
      fontFamily: {
        display: ["Fraunces", "Georgia", "serif"],
        body: ["Source Serif 4", "Georgia", "serif"],
        sans: ["Manrope", "system-ui", "sans-serif"]
      },
      boxShadow: {
        vellum: "0 10px 35px rgba(31, 35, 33, 0.15)",
        glow: "0 14px 38px rgba(31, 111, 139, 0.18)",
      },
      backgroundImage: {
        parchment:
          "radial-gradient(circle at 20% 10%, rgba(182,153,80,0.12), transparent 35%), radial-gradient(circle at 80% 90%, rgba(176,91,59,0.12), transparent 30%), linear-gradient(180deg, #f6f0e3 0%, #f2e8d8 100%)",
        tide:
          "radial-gradient(circle at 12% 15%, rgba(46,165,160,0.16), transparent 34%), radial-gradient(circle at 85% 8%, rgba(42,59,115,0.14), transparent 28%), radial-gradient(circle at 78% 86%, rgba(239,138,61,0.14), transparent 30%), linear-gradient(180deg, rgba(246,240,227,0.95) 0%, rgba(243,232,216,0.92) 100%)",
      },
      animation: {
        "pulse-soft": "pulseSoft 2.8s ease-in-out infinite",
        "fade-rise": "fadeRise 480ms ease-out",
      },
      keyframes: {
        pulseSoft: {
          "0%, 100%": { transform: "scale(1)", opacity: "1" },
          "50%": { transform: "scale(1.03)", opacity: "0.9" },
        },
        fadeRise: {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
