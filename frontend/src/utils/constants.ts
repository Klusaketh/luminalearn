/**
 * Shared System Constants for LuminaLearn AI Frontend.
 */

export const APP_NAME = "LuminaLearn AI";
export const APP_TAGLINE = "Illuminate Every Learning Journey";
export const APP_VERSION = "1.0.0";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

export const NAVIGATION_LINKS = [
  { label: "Dashboard", href: "/dashboard" },
  { label: "Knowledge Graph", href: "/graph" },
  { label: "Socratic Tutor", href: "/tutor" },
  { label: "Analytics", href: "/analytics" },
] as const;
