"use client";

import React, { useEffect, useId, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { LogOut, Menu, X, User } from "lucide-react";
import { useAuthStore } from "@/stores/useAuthStore";
import { BrandMark } from "@/components/common/BrandMark";
import { cn } from "@/utils/cn";
import { homePathFor } from "@/utils/routes";

interface NavItem {
  label: string;
  href: string;
  match: (path: string) => boolean;
}

const HOME_LINK: NavItem = { label: "Home", href: "/", match: (p) => p === "/" };

/** The workspace: shown only to signed-in learners (every one of these pages requires a session). */
const WORKSPACE_LINKS: NavItem[] = [
  {
    label: "Subjects",
    href: "/subjects",
    match: (p) => ["/subjects", "/courses", "/topics", "/lessons"].some((prefix) => p.startsWith(prefix)),
  },
  { label: "Tutor", href: "/tutor", match: (p) => p.startsWith("/tutor") },
  { label: "Quiz", href: "/quiz", match: (p) => p.startsWith("/quiz") },
];

export const Navbar: React.FC = () => {
  const pathname = usePathname();
  const { user, isAuthenticated, sessionStatus, logout } = useAuthStore();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuId = useId();
  const signedIn = isAuthenticated && user !== null;
  // Until a stored session is confirmed (or while the server can't confirm it), show neither the
  // workspace nor "Sign in": no flicker on load, and no "Sign in" next to "you're still signed in".
  const sessionPending = sessionStatus === "unknown" || sessionStatus === "checking" || sessionStatus === "unreachable";

  const dashboardPath = user ? homePathFor(user.role) : "/dashboard";
  const links: NavItem[] = [HOME_LINK];
  if (signedIn) {
    links.push({ label: "Dashboard", href: dashboardPath, match: (p) => p.startsWith("/dashboard") }, ...WORKSPACE_LINKS);
    if (user.role === "student") {
      links.push({ label: "Roadmap", href: "/onboarding/roadmap", match: (p) => p === "/onboarding/roadmap" });
    }
  }

  useEffect(() => {
    setMenuOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (!menuOpen) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMenuOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [menuOpen]);

  const handleLogout = async () => {
    setMenuOpen(false);
    await logout();
    // A full page load: it drops every cached workspace page and the in-memory tutor conversation,
    // so nothing from this session survives for the next person on a shared computer.
    window.location.replace("/");
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/[0.06] bg-space-950/70 backdrop-blur-2xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <Link href="/" className="group flex items-center gap-2.5 rounded-xl outline-none focus-visible:ring-2 focus-visible:ring-indigo-300" aria-label="LuminaLearn AI home">
          <BrandMark className="h-9 w-9 transition-transform duration-500 group-hover:rotate-[8deg]" />
          <span className="text-[15px] font-semibold tracking-tight text-white">
            LuminaLearn <span className="font-display text-[17px] italic text-indigo-300">AI</span>
          </span>
        </Link>

        <nav aria-label="Primary" className="hidden items-center gap-1 md:flex">
          {links.map((link) => {
            const active = link.match(pathname);
            return (
              <Link
                key={link.href}
                href={link.href}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "relative rounded-xl px-3.5 py-2 text-[13px] font-medium outline-none transition-colors focus-visible:ring-2 focus-visible:ring-indigo-300",
                  active ? "text-white" : "text-slate-400 hover:text-white"
                )}
              >
                {active && (
                  <motion.span
                    layoutId="nav-active-pill"
                    aria-hidden="true"
                    className="absolute inset-0 rounded-xl bg-white/[0.07] shadow-[inset_0_0_0_1px_rgba(255,255,255,0.08)]"
                    transition={{ type: "spring", stiffness: 380, damping: 32 }}
                  />
                )}
                <span className="relative">{link.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="hidden items-center gap-2 md:flex">
          {sessionPending ? (
            <span className="h-9 w-40 animate-pulse rounded-full bg-white/[0.04]" aria-hidden="true" />
          ) : signedIn ? (
            <>
              <Link
                href={user.role === "student" ? "/onboarding/profile" : dashboardPath}
                className="flex items-center gap-2 rounded-full border border-white/[0.08] bg-white/[0.03] py-1 pl-1 pr-3 text-left outline-none transition-colors hover:border-white/20 focus-visible:ring-2 focus-visible:ring-indigo-300"
              >
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-[linear-gradient(135deg,#7C3AED,#0891B2)] text-xs font-semibold text-white">
                  {user.full_name ? user.full_name.charAt(0).toUpperCase() : <User className="h-3.5 w-3.5" aria-hidden="true" />}
                </span>
                <span className="flex flex-col leading-tight">
                  <span className="max-w-[9rem] truncate text-xs font-semibold text-slate-100">{user.full_name}</span>
                  <span className="text-[11px] capitalize text-slate-400">{user.role}</span>
                </span>
              </Link>
              <button
                type="button"
                onClick={handleLogout}
                aria-label="Sign out"
                title="Sign out"
                className="rounded-xl border border-white/[0.08] p-2 text-slate-400 outline-none transition-colors hover:border-rose-400/40 hover:bg-rose-500/10 hover:text-rose-300 focus-visible:ring-2 focus-visible:ring-rose-300"
              >
                <LogOut className="h-4 w-4" aria-hidden="true" />
              </button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="rounded-xl px-3.5 py-2 text-[13px] font-medium text-slate-300 outline-none transition-colors hover:text-white focus-visible:ring-2 focus-visible:ring-indigo-300"
              >
                Sign in
              </Link>
              <Link
                href="/register/student"
                className="rounded-xl bg-white px-3.5 py-2 text-[13px] font-semibold text-space-950 outline-none transition-transform hover:-translate-y-px focus-visible:ring-2 focus-visible:ring-indigo-300 focus-visible:ring-offset-2 focus-visible:ring-offset-space-950"
              >
                Create account
              </Link>
            </>
          )}
        </div>

        <button
          type="button"
          onClick={() => setMenuOpen((open) => !open)}
          aria-expanded={menuOpen}
          aria-controls={menuId}
          aria-label={menuOpen ? "Close menu" : "Open menu"}
          className="rounded-xl border border-white/[0.08] p-2 text-slate-300 outline-none hover:text-white focus-visible:ring-2 focus-visible:ring-indigo-300 md:hidden"
        >
          {menuOpen ? <X className="h-5 w-5" aria-hidden="true" /> : <Menu className="h-5 w-5" aria-hidden="true" />}
        </button>
      </div>

      <AnimatePresence initial={false}>
        {menuOpen && (
          <motion.div
            id={menuId}
            key="mobile-menu"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ type: "spring", stiffness: 320, damping: 34 }}
            className="overflow-hidden border-t border-white/[0.06] bg-space-950/95 backdrop-blur-2xl md:hidden"
          >
            <nav aria-label="Mobile" className="flex flex-col gap-1 px-4 pb-5 pt-3">
              {links.map((link) => {
                const active = link.match(pathname);
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    aria-current={active ? "page" : undefined}
                    className={cn(
                      "rounded-xl px-3 py-2.5 text-[15px] font-medium outline-none focus-visible:ring-2 focus-visible:ring-indigo-300",
                      active ? "bg-white/[0.07] text-white" : "text-slate-300 hover:text-white"
                    )}
                  >
                    {link.label}
                  </Link>
                );
              })}
              <div className="mt-3 border-t border-white/[0.06] pt-4">
                {signedIn ? (
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="flex w-full items-center justify-center gap-2 rounded-xl border border-rose-400/20 bg-rose-500/10 py-2.5 text-sm font-semibold text-rose-300"
                  >
                    <LogOut className="h-4 w-4" aria-hidden="true" />
                    Sign out of {user.full_name?.split(" ")[0] || "your account"}
                  </button>
                ) : (
                  <div className="grid grid-cols-2 gap-2">
                    <Link href="/login" className="rounded-xl border border-white/10 py-2.5 text-center text-sm font-semibold text-white">
                      Sign in
                    </Link>
                    <Link href="/register/student" className="rounded-xl bg-white py-2.5 text-center text-sm font-semibold text-space-950">
                      Create account
                    </Link>
                  </div>
                )}
                <Link href="/register/teacher" className="mt-3 block text-center text-xs text-slate-400 underline-offset-4 hover:text-slate-200 hover:underline">
                  For teachers
                </Link>
              </div>
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
};
