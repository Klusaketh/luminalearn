import { NextResponse, type NextRequest } from "next/server";
import { SESSION_COOKIE, isPublicPath, loginPathFor } from "@/utils/routes";

/**
 * Sends visitors without a session to sign-in before any workspace page is served.
 * The session cookie is only a hint: the API checks the real access token on every request,
 * and the client gate re-verifies the session, so a forged cookie reveals nothing but a spinner.
 */
export function middleware(request: NextRequest) {
  const { pathname, search } = request.nextUrl;
  if (isPublicPath(pathname) || request.cookies.has(SESSION_COOKIE)) {
    return NextResponse.next();
  }
  return NextResponse.redirect(new URL(loginPathFor(`${pathname}${search}`), request.url));
}

export const config = {
  // Pages only: skip the API proxy, Next.js internals and files with an extension (icons, robots.txt).
  matcher: ["/((?!api/|_next/|.*\\.[\\w]+$).*)"],
};
