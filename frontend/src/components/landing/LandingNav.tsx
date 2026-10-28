"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { useAuthStore } from "@/stores/useAuthStore";
import { BrandMark } from "@/components/common/BrandMark";
import { MagneticButton } from "@/components/ui/MagneticButton";
import { homePathFor } from "@/utils/routes";

const LINKS = [
  { label: "Home", href: "#top" },
  { label: "Features", href: "#features" },
  { label: "How it works", href: "#how-it-works" },
  { label: "About", href: "#about" },
];

/** Floating glass navigation for the marketing page (the workspace keeps the full Navbar). */
export function LandingNav() {
  const { isAuthenticated, user, sessionStatus } = useAuthStore();
  const signedIn = isAuthenticated && user !== null;
  const pending = sessionStatus === "unknown" || sessionStatus === "checking";

  return (
    <motion.header
      initial={{ opacity: 0, y: -16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
      className="fixed inset-x-0 top-4 z-50 flex justify-center px-4"
    >
      <div className="glass-strong flex h-14 w-full max-w-4xl items-center justify-between gap-3 rounded-2xl pl-3 pr-2 shadow-glass">
        <Link
          href="/"
          className="group flex items-center gap-2 rounded-xl outline-none focus-visible:ring-2 focus-visible:ring-aurora-teal"
          aria-label="LuminaLearn AI home"
        >
          <BrandMark className="h-8 w-8 transition-transform duration-500 group-hover:rotate-[8deg]" />
          <span className="text-[15px] font-semibold tracking-tight text-white">LuminaLearn</span>
        </Link>

        <nav aria-label="Page sections" className="hidden items-center gap-1 md:flex">
          {LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="rounded-xl px-3 py-2 text-[13px] font-medium text-slate-400 outline-none transition-colors hover:text-white focus-visible:ring-2 focus-visible:ring-aurora-teal"
            >
              {link.label}
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-1.5">
          {!pending && !signedIn && (
            <Link
              href="/login"
              className="rounded-xl px-3 py-2 text-[13px] font-medium text-slate-300 outline-none transition-colors hover:text-white focus-visible:ring-2 focus-visible:ring-aurora-teal"
            >
              Sign in
            </Link>
          )}
          <MagneticButton
            href={signedIn && user ? homePathFor(user.role) : "/register/student"}
            variant="outline"
            size="sm"
            strength={0.3}
            cursorLabel={signedIn ? "Open" : "Start"}
          >
            {signedIn ? "Dashboard" : "Get Started"}
          </MagneticButton>
        </div>
      </div>
    </motion.header>
  );
}
