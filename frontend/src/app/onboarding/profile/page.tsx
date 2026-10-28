"use client";

import React, { useCallback, useEffect, useState } from "react";
import { useOnReconnect } from "@/hooks/useOnReconnect";
import Link from "next/link";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { useAuthStore } from "@/stores/useAuthStore";
import { onboardingService, LearnerProfile } from "@/services/onboardingService";
import {
  FileText,
  CheckCircle2,
  AlertCircle,
  Compass,
  ArrowRight,
  TrendingUp
} from "lucide-react";

export default function LearnerProfilePage() {
  const { user, accessToken } = useAuthStore();
  const [profile, setProfile] = useState<LearnerProfile | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fetchProfile = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      if (accessToken) {
        const res = await onboardingService.getLearnerProfile(accessToken);
        setProfile(res);
      }
    } catch (err: any) {
      setErrorMessage("Learner profile not found. Please complete the onboarding diagnostic assessment.");
    } finally {
      setIsLoading(false);
    }
  }, [accessToken]);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  // After a server outage, reload by itself if this page is showing a load error.
  useOnReconnect(() => {
    if (errorMessage) void fetchProfile();
  });

  return (
    <ProtectedRoute allowedRoles={["student"]}>
      <div className="flex-1 text-slate-100 p-4 sm:p-6 lg:p-8 relative overflow-hidden font-sans flex flex-col">

        <div className="max-w-4xl mx-auto w-full space-y-8 relative z-10 flex-1">
          
          {/* Header */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold mb-2">
                <FileText className="w-3.5 h-3.5" />
                Student Cognitive Profile
              </div>
              <h1 className="font-display leading-tight text-white text-4xl">Learner Profile</h1>
              <p className="text-xs sm:text-sm text-slate-400">
                Cognitive diagnostics and VARK personalization preferences for {user?.full_name}
              </p>
            </div>

            <Link href="/onboarding/roadmap">
              <button className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-colors flex items-center gap-1.5 shadow-md shadow-indigo-600/20">
                <Compass className="w-3.5 h-3.5" />
                View Study Roadmap
              </button>
            </Link>
          </div>

          {/* Loading State */}
          {isLoading && (
            <div className="p-12 rounded-2xl bg-slate-900/40 border border-slate-800 flex flex-col items-center justify-center gap-4">
              <div className="w-10 h-10 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
              <p className="text-xs text-slate-400 font-mono animate-pulse">
                Fetching diagnostic profile...
              </p>
            </div>
          )}

          {/* Error / Empty State */}
          {!isLoading && (!profile || errorMessage) && (
            <div className="p-8 rounded-2xl bg-slate-900/60 border border-slate-800 text-center space-y-4">
              <AlertCircle className="w-10 h-10 text-amber-400 mx-auto" />
              <h3 className="text-lg font-bold text-white">No Learner Profile Found</h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                {errorMessage || "You haven't completed the diagnostic assessment wizard yet."}
              </p>
              <Link href="/onboarding" className="inline-block pt-2">
                <button className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs flex items-center gap-2">
                  Take Onboarding Assessment
                  <ArrowRight className="w-4 h-4" />
                </button>
              </Link>
            </div>
          )}

          {/* Profile Card View */}
          {!isLoading && profile && (
            <div className="space-y-6">
              
              {/* Primary Stats Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                
                <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-2">
                  <span className="text-xs text-slate-400 block">Assessment Score</span>
                  <div className="text-3xl font-extrabold text-indigo-400">
                    {profile.assessment_score}%
                  </div>
                  <span className="text-[11px] text-slate-500 block">Diagnostic evaluation</span>
                </div>

                <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-2">
                  <span className="text-xs text-slate-400 block">VARK Modality</span>
                  <div className="text-2xl font-extrabold text-purple-400 capitalize">
                    {user?.preferred_modality || "Visual"}
                  </div>
                  <span className="text-[11px] text-slate-500 block">Cognitive learning style</span>
                </div>

                <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-2">
                  <span className="text-xs text-slate-400 block">Recommended Target</span>
                  <div className="text-2xl font-extrabold text-emerald-400">
                    {profile.recommended_weekly_hours} hrs/wk
                  </div>
                  <span className="text-[11px] text-slate-500 block">Suggested weekly velocity</span>
                </div>

              </div>

              {/* Strengths & Weak Areas */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-3">
                  <h3 className="text-sm font-bold text-emerald-400 flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" />
                    Identified Strengths
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {profile.strengths.map((str, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-medium"
                      >
                        {str}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-3">
                  <h3 className="text-sm font-bold text-amber-400 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4" />
                    Areas for Growth
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {profile.weak_areas.map((weak, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs font-medium"
                      >
                        {weak}
                      </span>
                    ))}
                  </div>
                </div>

              </div>

              {/* Selected Subjects & Goals */}
              <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-4">
                <div>
                  <h3 className="text-sm font-bold text-white mb-2">Target Subjects</h3>
                  <div className="flex flex-wrap gap-2">
                    {profile.selected_subjects.map((subj, idx) => (
                      <span key={idx} className="px-3 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-medium">
                        {subj}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-bold text-white mb-2">Learning Goals</h3>
                  <div className="flex flex-wrap gap-2">
                    {profile.goals.map((goal, idx) => (
                      <span key={idx} className="px-3 py-1 rounded-lg bg-purple-500/10 border border-purple-500/20 text-purple-300 text-xs font-medium">
                        {goal}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

            </div>
          )}

        </div>
      </div>
    </ProtectedRoute>
  );
}
