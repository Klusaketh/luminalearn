import type { Metadata, Viewport } from "next";
import "@/styles/globals.css";
import { APP_NAME, APP_TAGLINE } from "@/utils/constants";
import { AppProviders } from "@/components/providers/AppProviders";

export const metadata: Metadata = {
  title: `${APP_NAME} — ${APP_TAGLINE}`,
  description:
    "An AI-powered adaptive learning ecosystem that personalizes education through Artificial Intelligence, Learning Analytics, Accessibility, and Explainable AI.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark selection:bg-primary/20 selection:text-primary">
      <body className="min-h-screen bg-slate-950 text-slate-100 antialiased flex flex-col font-sans">
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
