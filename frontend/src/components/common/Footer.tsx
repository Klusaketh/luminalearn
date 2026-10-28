"use client";

import React from "react";
import Link from "next/link";
import { ShieldCheck } from "lucide-react";
import { APP_NAME, APP_TAGLINE } from "@/utils/constants";
import { BrandMark } from "@/components/common/BrandMark";
import { useAuthStore } from "@/stores/useAuthStore";
import { homePathFor, type WorkspaceRole } from "@/utils/routes";

interface FooterColumn {
  title: string;
  links: { label: string; href: string }[];
}

/** Visitors only see the doors in; the workspace links appear once someone is signed in. */
const VISITOR_COLUMNS: FooterColumn[] = [
  {
    title: "Get started",
    links: [
      { label: "Create a student account", href: "/register/student" },
      { label: "Teacher portal", href: "/register/teacher" },
      { label: "Sign in", href: "/login" },
    ],
  },
  {
    title: "Account help",
    links: [
      { label: "Forgot your password", href: "/forgot-password" },
      { label: "Verify your email", href: "/verify-email" },
    ],
  },
];

function workspaceColumns(role: WorkspaceRole): FooterColumn[] {
  return [
    {
      title: "Learn",
      links: [
        { label: "Socratic tutor", href: "/tutor" },
        { label: "Adaptive quiz", href: "/quiz" },
        { label: "Subject catalog", href: "/subjects" },
      ],
    },
    {
      title: "Your account",
      links: [
        { label: "Dashboard", href: homePathFor(role) },
        ...(role === "student"
          ? [
              { label: "Learning roadmap", href: "/onboarding/roadmap" },
              { label: "Learner profile", href: "/onboarding/profile" },
            ]
          : []),
      ],
    },
  ];
}

export const Footer: React.FC = () => {
  const user = useAuthStore((s) => (s.isAuthenticated ? s.user : null));
  const sessionKnown = useAuthStore((s) => s.sessionStatus === "authenticated" || s.sessionStatus === "anonymous");
  const columns = user ? workspaceColumns(user.role) : VISITOR_COLUMNS;

  return (
    <footer className="relative w-full border-t border-white/[0.06] bg-space-950/60 px-4 py-14 text-slate-400 backdrop-blur-xl sm:px-6 lg:px-8">
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-10 md:grid-cols-[1.4fr_1fr_1fr_1.2fr]">
        <div className="space-y-4">
          <div className="flex items-center gap-2.5">
            <BrandMark className="h-8 w-8" />
            <span className="text-[15px] font-semibold tracking-tight text-white">{APP_NAME}</span>
          </div>
          <p className="max-w-xs text-sm leading-relaxed text-slate-400">{APP_TAGLINE}. A tutor that answers with a better question.</p>
        </div>

        {columns.map((column) => (
          // Hidden, not removed, until the session is known: keeps the layout and never offers "Sign in" to a signed-in learner.
          <nav key={column.title} aria-label={column.title} aria-hidden={!sessionKnown || undefined} className={`space-y-3 ${sessionKnown ? "" : "invisible"}`}>
            <h2 className="text-xs font-semibold text-slate-200">{column.title}</h2>
            <ul className="space-y-2 text-sm">
              {column.links.map((link) => (
                <li key={link.href}>
                  <Link href={link.href} className="rounded transition-colors hover:text-white focus-visible:text-white">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        ))}

        <div className="space-y-3">
          <h2 className="text-xs font-semibold text-slate-200">Privacy and security</h2>
          <div className="glass flex gap-3 rounded-2xl p-4">
            <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-indigo-300" aria-hidden="true" />
            <p className="text-[13px] leading-snug text-slate-400">
              Passwords are hashed with Argon2id, sessions use short-lived JWTs, and voice audio is processed per turn and never saved by LuminaLearn.
            </p>
          </div>
        </div>
      </div>

      <div className="mx-auto mt-12 flex max-w-7xl flex-col items-center justify-between gap-3 border-t border-white/[0.06] pt-6 text-xs text-slate-500 md:flex-row">
        <p suppressHydrationWarning>© {new Date().getFullYear()} LuminaLearn AI. All rights reserved.</p>
        <p>Project Aurora</p>
      </div>
    </footer>
  );
};
