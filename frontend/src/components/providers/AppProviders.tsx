"use client";

import React, { useEffect } from "react";
import { usePathname } from "next/navigation";
import { MotionConfig } from "framer-motion";
import { useAuthStore } from "@/stores/useAuthStore";
import { Navbar } from "@/components/common/Navbar";
import { Footer } from "@/components/common/Footer";
import { ConnectionBanner } from "@/components/common/ConnectionBanner";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { isPublicPath } from "@/utils/routes";

/** Routes that behave like full-height apps rather than scrolling documents. */
const APP_SHELL_ROUTES = ["/tutor"];

export const AppProviders: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const initializeAuth = useAuthStore((s) => s.initializeAuth);
  const pathname = usePathname();
  const isAppShell = APP_SHELL_ROUTES.some((route) => pathname === route || pathname.startsWith(`${route}/`));
  // The marketing page renders its own floating LandingNav over the hero.
  const isLanding = pathname === "/";

  useEffect(() => {
    // Rehydrate the session on every page, so public pages know who is signed in too.
    void initializeAuth();
  }, [initializeAuth]);

  return (
    // reducedMotion="user": every framer-motion animation honors prefers-reduced-motion.
    <MotionConfig reducedMotion="user">
      <div className="flex min-h-screen flex-col text-slate-100">
        {!isLanding && <Navbar />}
        <ConnectionBanner />
        <div id="main-content" className="flex flex-1 flex-col">
          {/* Every workspace page requires a verified session; the middleware redirects first. */}
          {isPublicPath(pathname) ? children : <ProtectedRoute>{children}</ProtectedRoute>}
        </div>
        {!isAppShell && <Footer />}
      </div>
    </MotionConfig>
  );
};
