"use client";

import React, { useCallback, useEffect, useState } from "react";
import { useOnReconnect } from "@/hooks/useOnReconnect";
import Link from "next/link";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { useAuthStore } from "@/stores/useAuthStore";
import { onboardingService, PersonalizedRoadmap } from "@/services/onboardingService";
import {
  Compass,
  AlertCircle,
  BookOpen,
  ArrowRight,
  FileText,
  LayoutDashboard
} from "lucide-react";

export default function PersonalizedRoadmapPage() {
  const { user, accessToken } = useAuthStore();
  const [roadmap, setRoadmap] = useState<PersonalizedRoadmap | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fetchRoadmap = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      if (accessToken) {
        const res = await onboardingService.getPersonalizedRoadmap(accessToken);
        setRoadmap(res);
      }
    } catch (err: any) {
      setErrorMessage("Roadmap not found. Please complete the onboarding diagnostic assessment wizard first.");
    } finally {
      setIsLoading(false);
    }
  }, [accessToken]);

  useEffect(() => {
    fetchRoadmap();
  }, [fetchRoadmap]);

  // After a server outage, reload by itself if this page is showing a load error.
  useOnReconnect(() => {
    if (errorMessage) void fetchRoadmap();
  });

  return (
    <ProtectedRoute allowedRoles={["student"]}>
      <div className="flex-1 text-slate-100 p-4 sm:p-6 lg:p-8 relative overflow-hidden font-sans flex flex-col">

        <div className="max-w-4xl mx-auto w-full space-y-8 relative z-10 flex-1">
          
          {/* Header */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-xs font-semibold mb-2">
                <Compass className="w-3.5 h-3.5" />
                Adaptive Learning Pathway
              </div>
              <h1 className="font-display leading-tight text-white text-4xl">Personalized Roadmap</h1>
              <p className="text-xs sm:text-sm text-slate-400">
                Custom structured study modules generated for {user?.full_name}
              </p>
            </div>

            <div className="flex items-center gap-2">
              <Link href="/dashboard">
                <button className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 font-semibold text-xs transition-colors flex items-center gap-1.5">
                  <LayoutDashboard className="w-3.5 h-3.5 text-indigo-400" />
                  Dashboard
                </button>
              </Link>
              <Link href="/onboarding/profile">
                <button className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-colors flex items-center gap-1.5 shadow-md shadow-indigo-600/20">
                  <FileText className="w-3.5 h-3.5" />
                  Profile
                </button>
              </Link>
            </div>
          </div>

          {/* Loading State */}
          {isLoading && (
            <div className="p-12 rounded-2xl bg-slate-900/40 border border-slate-800 flex flex-col items-center justify-center gap-4">
              <div className="w-10 h-10 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin" />
              <p className="text-xs text-slate-400 font-mono animate-pulse">
                Fetching study roadmap pathway...
              </p>
            </div>
          )}

          {/* Error / Empty State */}
          {!isLoading && (!roadmap || errorMessage) && (
            <div className="p-8 rounded-2xl bg-slate-900/60 border border-slate-800 text-center space-y-4">
              <AlertCircle className="w-10 h-10 text-amber-400 mx-auto" />
              <h3 className="text-lg font-bold text-white">No Roadmap Found</h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                {errorMessage || "You haven't completed the diagnostic assessment wizard yet."}
              </p>
              <Link href="/onboarding" className="inline-block pt-2">
                <button className="px-6 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs flex items-center gap-2">
                  Take Onboarding Assessment
                  <ArrowRight className="w-4 h-4" />
                </button>
              </Link>
            </div>
          )}

          {/* Roadmap Card View */}
          {!isLoading && roadmap && (
            <div className="space-y-6">
              
              {/* Course Overview Banner */}
              <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/30 to-purple-950/30 border border-slate-800 space-y-4">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
                  <h2 className="text-xl font-extrabold text-white">
                    {roadmap.recommended_course}
                  </h2>
                  <span className="px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold">
                    Starting Focus: {roadmap.starting_module}
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs">
                  <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">Weekly Goal</span>
                    <span className="text-base font-bold text-white">{roadmap.weekly_goal_hours} Hours</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">Daily Target</span>
                    <span className="text-base font-bold text-indigo-400">{roadmap.daily_target_minutes} Minutes</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 col-span-2 sm:col-span-1">
                    <span className="text-slate-400 block text-[11px]">Total Modules</span>
                    <span className="text-base font-bold text-purple-400">{roadmap.roadmap_modules.length} Modules</span>
                  </div>
                </div>
              </div>

              {/* Modules Breakdown */}
              <div className="space-y-3">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-indigo-400" />
                  Sequential Study Modules
                </h3>

                <div className="space-y-3">
                  {roadmap.roadmap_modules.map((mod) => (
                    <div
                      key={mod.id}
                      className={`p-5 rounded-2xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 transition-all ${
                        mod.is_key_focus
                          ? "bg-indigo-600/15 border-indigo-500/60 ring-1 ring-indigo-500/30"
                          : "bg-slate-900/50 border-slate-800"
                      }`}
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <h4 className="text-sm font-bold text-white">{mod.title}</h4>
                          {mod.is_key_focus && (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500 text-white">
                              Priority Focus
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">{mod.description}</p>
                      </div>

                      <div className="flex items-center gap-3 shrink-0">
                        <span className="text-xs font-mono text-slate-400 bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800">
                          {mod.estimated_hours} hrs
                        </span>
                        <span className="text-[11px] font-semibold text-indigo-400 capitalize bg-indigo-500/10 px-2 py-1 rounded">
                          {mod.difficulty}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          )}

        </div>
      </div>
    </ProtectedRoute>
  );
}
