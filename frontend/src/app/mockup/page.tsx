"use client";

import React, { useState } from "react";
import StudentDashboardMockup from "./dashboard/page";
import AITutorMockup from "./tutor/page";
import { Sparkles, LayoutDashboard, ExternalLink } from "lucide-react";
import Link from "next/link";

export default function MockupViewerPage() {
  const [screen, setScreen] = useState<"dashboard" | "tutor">("dashboard");

  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col font-sans">
      {/* Top Switcher Navigation Bar */}
      <div className="h-12 bg-slate-950 border-b border-slate-800 px-6 flex items-center justify-between z-30 shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs font-bold text-slate-200 tracking-wide uppercase">
              LuminaLearn AI Mockups
            </span>
          </div>
          <span className="text-slate-600">|</span>
          <span className="text-xs text-slate-400">
            High-Fidelity 1440x900 Desktop SaaS
          </span>
        </div>

        {/* Screen Switcher Tabs */}
        <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800">
          <button
            onClick={() => setScreen("dashboard")}
            className={`flex items-center gap-2 px-3.5 py-1 rounded-md text-xs font-semibold transition-all ${
              screen === "dashboard"
                ? "bg-blue-600 text-white shadow-xs"
                : "text-slate-400 hover:text-white hover:bg-slate-800/60"
            }`}
          >
            <LayoutDashboard className="w-3.5 h-3.5" />
            Student Dashboard
          </button>
          <button
            onClick={() => setScreen("tutor")}
            className={`flex items-center gap-2 px-3.5 py-1 rounded-md text-xs font-semibold transition-all ${
              screen === "tutor"
                ? "bg-blue-600 text-white shadow-xs"
                : "text-slate-400 hover:text-white hover:bg-slate-800/60"
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            AI Tutor
          </button>
        </div>

        {/* Direct links */}
        <div className="flex items-center gap-3 text-xs text-slate-400">
          <Link
            href="/mockup/dashboard"
            target="_blank"
            className="hover:text-blue-400 flex items-center gap-1"
          >
            Dashboard Standalone <ExternalLink className="w-3 h-3" />
          </Link>
          <span>•</span>
          <Link
            href="/mockup/tutor"
            target="_blank"
            className="hover:text-blue-400 flex items-center gap-1"
          >
            AI Tutor Standalone <ExternalLink className="w-3 h-3" />
          </Link>
        </div>
      </div>

      {/* Screen Frame */}
      <div className="flex-1 w-full bg-[#F8FAFC]">
        {screen === "dashboard" ? (
          <StudentDashboardMockup />
        ) : (
          <AITutorMockup />
        )}
      </div>
    </div>
  );
}
