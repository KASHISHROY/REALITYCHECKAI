import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        muted: "hsl(var(--muted))",
        "muted-foreground": "hsl(var(--muted-foreground))",
        border: "hsl(var(--border))",
        surface: "hsl(var(--surface))",
        "surface-strong": "hsl(var(--surface-strong))",
        accent: "hsl(var(--accent))",
        warning: "hsl(var(--warning))",
        danger: "hsl(var(--danger))",
      },
      boxShadow: {
        glow: "0 0 80px rgba(20, 184, 166, 0.12)",
      },
    },
  },
  plugins: [],
};

export default config;

