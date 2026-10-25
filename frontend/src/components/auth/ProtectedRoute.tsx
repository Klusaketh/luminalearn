"use client";

import React, { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { CloudOff, RotateCw } from "lucide-react";
import { useAuthStore } from "../../stores/useAuthStore";
import { onReachabilityChange } from "../../services/apiClient";
import { homePathFor, loginPathFor, type WorkspaceRole } from "../../utils/routes";

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: WorkspaceRole[];
}

/**
 * Renders its children only for a verified session (and, optionally, an allowed role).
 * Redirects are decided from the settled session status, never from the initial "unknown"
 * state, so a signed-in learner who refreshes the page is not bounced through sign-in.
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, allowedRoles }) => {
  const router = useRouter();
  const pathname = usePathname();
  const user = useAuthStore((s) => s.user);
  const sessionStatus = useAuthStore((s) => s.sessionStatus);
  const signedOutByUser = useAuthStore((s) => s.signedOutByUser);
  const initializeAuth = useAuthStore((s) => s.initializeAuth);
  const roleAllowed = !allowedRoles || (user !== null && allowedRoles.includes(user.role));

  useEffect(() => {
    void initializeAuth();
  }, [initializeAuth]);

  // The server was unreachable while checking the session: check again the moment it's back.
  useEffect(() => {
    if (sessionStatus !== "unreachable") return;
    return onReachabilityChange((reachable) => {
      if (reachable) void initializeAuth();
    });
  }, [sessionStatus, initializeAuth]);

  useEffect(() => {
    if (sessionStatus === "anonymous") {
      router.replace(signedOutByUser ? "/" : loginPathFor(`${pathname}${window.location.search}`));
    } else if (sessionStatus === "authenticated" && user && !roleAllowed) {
      router.replace(homePathFor(user.role));
    }
  }, [sessionStatus, signedOutByUser, user, roleAllowed, pathname, router]);

  if (sessionStatus === "authenticated" && roleAllowed) {
    return <>{children}</>;
  }

  if (sessionStatus === "unreachable") {
    return (
      <div className="flex flex-1 items-center justify-center px-4 py-24" role="alert">
        <div className="glass flex max-w-md flex-col items-center gap-4 rounded-3xl p-8 text-center">
          <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-amber-400/10 text-amber-200">
            <CloudOff className="h-6 w-6" aria-hidden="true" />
          </span>
          <div>
            <h1 className="font-display text-3xl leading-tight text-white">The server is out of reach</h1>
            <p className="mt-2 text-sm leading-relaxed text-slate-300">
              You&apos;re still signed in. This page reconnects automatically as soon as the LuminaLearn server is back.
            </p>
          </div>
          <button
            type="button"
            onClick={() => void initializeAuth()}
            className="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2 text-sm font-semibold text-space-950 outline-none transition-transform hover:-translate-y-px focus-visible:ring-2 focus-visible:ring-indigo-300"
          >
            <RotateCw className="h-4 w-4" aria-hidden="true" />
            Try now
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-1 items-center justify-center py-24 text-slate-100" role="status" aria-live="polite">
      <div className="flex flex-col items-center gap-4">
        <div className="h-10 w-10 animate-spin rounded-full border-[3px] border-indigo-500/25 border-t-indigo-300" aria-hidden="true" />
        <p className="text-sm text-slate-400">
          {sessionStatus === "anonymous" ? "Taking you to sign in" : "Checking your session"}
        </p>
      </div>
    </div>
  );
};
