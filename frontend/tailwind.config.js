/**
 * LuminaLearn AI — Project Aurora design tokens.
 *
 * The `slate` and `indigo` scales are remapped onto the Aurora palette so every page shares
 * one visual language: `slate` becomes the deep-space neutrals (#05050A / #0B0C15) and
 * `indigo` becomes the violet primary (#8B5CF6). Text shades are tuned for WCAG contrast
 * on the space background: slate-400 ≈ 9:1, slate-500 ≈ 7.3:1 (AAA), indigo-400 ≈ 7.5:1.
 */

const space = {
  50: "#F7F8FC",
  100: "#EDEFF7",
  200: "#DCDFEC",
  300: "#C2C7DC",
  400: "#A9AFCA",
  500: "#9399B7",
  600: "#5D6384",
  700: "#2E3248",
  800: "#181B2A",
  900: "#0B0C15",
  950: "#05060A",
};

const violet = {
  50: "#F5F3FF",
  100: "#EDE9FE",
  200: "#DDD6FE",
  300: "#C4B5FD",
  400: "#A78BFA",
  500: "#8B5CF6",
  600: "#7C3AED",
  700: "#6D28D9",
  800: "#5B21B6",
  900: "#4C1D95",
  950: "#2E1065",
};

/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/hooks/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        slate: space,
        indigo: violet,
        space,
        // Brand accents run teal -> cyan -> violet -> indigo. Amber is reserved for warnings/status.
        aurora: {
          teal: "#2DD4BF",
          cyan: "#22D3EE",
          violet: "#8B5CF6",
          indigo: "#6366F1",
          amber: "#F59E0B",
        },
        ink: {
          DEFAULT: "#05060A",
          text: "#E6E8EE",
          muted: "#8A90A2",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
          50: violet[50],
          100: violet[100],
          500: violet[500],
          600: violet[600],
          700: violet[700],
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        surface: {
          DEFAULT: "hsl(var(--surface))",
          subtle: "hsl(var(--surface-subtle))",
          glass: "rgba(255, 255, 255, 0.03)",
          glassDark: "rgba(11, 12, 21, 0.72)",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      boxShadow: {
        subtle: "0 1px 2px 0 rgba(0, 0, 0, 0.3)",
        glass: "0 1px 0 0 rgba(255, 255, 255, 0.04) inset, 0 24px 60px -24px rgba(0, 0, 0, 0.8)",
        card: "0 4px 24px -6px rgba(0, 0, 0, 0.6)",
        linear: "0 0 0 1px rgba(255, 255, 255, 0.08), 0 10px 30px -10px rgba(0, 0, 0, 0.7)",
        glow: "0 0 0 1px rgba(139, 92, 246, 0.35), 0 8px 32px -8px rgba(139, 92, 246, 0.55)",
        "glow-teal": "0 0 0 1px rgba(45, 212, 191, 0.35), 0 8px 32px -8px rgba(45, 212, 191, 0.5)",
        "glow-cyan": "0 0 0 1px rgba(34, 211, 238, 0.35), 0 8px 32px -8px rgba(34, 211, 238, 0.5)",
        "glow-violet": "0 0 0 1px rgba(139, 92, 246, 0.35), 0 8px 32px -8px rgba(139, 92, 246, 0.55)",
        "glow-indigo": "0 0 0 1px rgba(99, 102, 241, 0.35), 0 8px 32px -8px rgba(99, 102, 241, 0.55)",
        "glow-amber": "0 0 0 1px rgba(245, 158, 11, 0.4), 0 8px 32px -8px rgba(245, 158, 11, 0.5)",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        display: ["var(--font-display)", "-apple-system", "Segoe UI", "sans-serif"],
        accent: ["var(--font-accent)", "Georgia", "serif"],
        mono: ["var(--font-mono)", "SFMono-Regular", "Menlo", "Monaco", "monospace"],
      },
      keyframes: {
        "fade-in": {
          "0%": { opacity: 0, transform: "translateY(4px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
        "pulse-subtle": {
          "0%, 100%": { opacity: 1 },
          "50%": { opacity: 0.7 },
        },
        "aurora-drift": {
          "0%": { transform: "translate3d(-4%, -2%, 0) scale(1)" },
          "50%": { transform: "translate3d(4%, 3%, 0) scale(1.08)" },
          "100%": { transform: "translate3d(-4%, -2%, 0) scale(1)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        twinkle: {
          "0%, 100%": { opacity: 0.15 },
          "50%": { opacity: 0.9 },
        },
        "line-draw": {
          "0%": { transform: "scaleX(0)" },
          "100%": { transform: "scaleX(1)" },
        },
      },
      animation: {
        twinkle: "twinkle 4s ease-in-out infinite",
        "line-draw": "line-draw 1.2s cubic-bezier(0.16, 1, 0.3, 1) both",
        "fade-in": "fade-in 0.35s cubic-bezier(0.16, 1, 0.3, 1) both",
        "pulse-subtle": "pulse-subtle 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "aurora-drift": "aurora-drift 28s ease-in-out infinite",
        shimmer: "shimmer 2.4s linear infinite",
      },
    },
  },
  plugins: [],
};
