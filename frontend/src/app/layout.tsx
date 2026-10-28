import type { Metadata, Viewport } from "next";
import localFont from "next/font/local";
import "@/styles/globals.css";
import "katex/dist/katex.min.css";
import { APP_NAME, APP_TAGLINE } from "@/utils/constants";
import { AppProviders } from "@/components/providers/AppProviders";
import { AuroraBackground } from "@/components/ui/AuroraBackground";

// Self-hosted (fontsource) so builds never depend on a font CDN.
const sans = localFont({
  src: "../../node_modules/@fontsource-variable/geist/files/geist-latin-wght-normal.woff2",
  variable: "--font-sans",
  weight: "100 900",
  display: "swap",
});

// Headings: Space Grotesk Light (300), with 400/500 for small headings that need more weight.
const display = localFont({
  src: [
    { path: "../../node_modules/@fontsource/space-grotesk/files/space-grotesk-latin-300-normal.woff2", style: "normal", weight: "300" },
    { path: "../../node_modules/@fontsource/space-grotesk/files/space-grotesk-latin-400-normal.woff2", style: "normal", weight: "400" },
    { path: "../../node_modules/@fontsource/space-grotesk/files/space-grotesk-latin-500-normal.woff2", style: "normal", weight: "500" },
  ],
  variable: "--font-display",
  display: "swap",
});

// Accent words inside headlines ("Learning that *adapts* to you").
const accent = localFont({
  src: [
    { path: "../../node_modules/@fontsource/instrument-serif/files/instrument-serif-latin-400-normal.woff2", style: "normal", weight: "400" },
    { path: "../../node_modules/@fontsource/instrument-serif/files/instrument-serif-latin-400-italic.woff2", style: "italic", weight: "400" },
  ],
  variable: "--font-accent",
  display: "swap",
});

const mono = localFont({
  src: "../../node_modules/@fontsource-variable/jetbrains-mono/files/jetbrains-mono-latin-wght-normal.woff2",
  variable: "--font-mono",
  weight: "100 800",
  display: "swap",
});

export const metadata: Metadata = {
  title: `${APP_NAME} — ${APP_TAGLINE}`,
  description:
    "An AI-powered adaptive learning ecosystem with a multi-agent Socratic tutor, live voice tutoring, Bayesian mastery tracking and VARK-adaptive explanations.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#05060A",
  colorScheme: "dark",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`dark ${sans.variable} ${display.variable} ${accent.variable} ${mono.variable}`}>
      <body className="flex min-h-screen flex-col font-sans antialiased">
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[100] focus:rounded-xl focus:bg-indigo-600 focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-white"
        >
          Skip to content
        </a>
        <AuroraBackground />
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
