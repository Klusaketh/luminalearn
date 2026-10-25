/**
 * Which pages are open to visitors and which belong to the signed-in workspace.
 * Shared by the edge middleware (redirects before any page code loads) and the client gate.
 * Everything not listed here is part of the workspace, so new pages are private by default.
 */

/** Pages a visitor can open without signing in. Each entry also covers its sub-paths. */
const PUBLIC_PATHS = ["/login", "/register", "/forgot-password", "/reset-password", "/verify-email"];

/** Set by the auth store while the browser holds a session. A hint for redirects, never a credential. */
export const SESSION_COOKIE = "lumina_session";

export function isPublicPath(pathname: string): boolean {
  return pathname === "/" || PUBLIC_PATHS.some((path) => pathname === path || pathname.startsWith(`${path}/`));
}

/**
 * A safe place to continue to after signing in: a same-site workspace path.
 * Rejects other origins ("//host", "/\\host") and the public pages themselves, since
 * returning to /login after signing in would bounce between the two pages forever.
 */
export function safeRedirectTarget(raw: string | null | undefined): string | null {
  if (!raw || !raw.startsWith("/") || raw.startsWith("//") || raw.startsWith("/\\")) return null;
  const pathname = raw.split(/[?#]/, 1)[0];
  return isPublicPath(pathname) ? null : raw;
}

export function loginPathFor(target: string): string {
  const safe = safeRedirectTarget(target);
  return safe ? `/login?redirect=${encodeURIComponent(safe)}` : "/login";
}

export type WorkspaceRole = "student" | "teacher" | "admin" | "parent";

/** Each role's own home in the workspace. */
export function homePathFor(role: WorkspaceRole): string {
  if (role === "admin") return "/dashboard/admin";
  if (role === "teacher") return "/dashboard/teacher";
  if (role === "student") return "/dashboard";
  return "/";
}
