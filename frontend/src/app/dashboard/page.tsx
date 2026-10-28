"use client";

import React, { useCallback, useEffect, useState } from "react";
import { useOnReconnect } from "@/hooks/useOnReconnect";
import Link from "next/link";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { useAuthStore } from "@/stores/useAuthStore";
import { onboardingService, LearnerProfile } from "@/services/onboardingService";
import { quizService, type TopicMasterySummary } from "@/services/quizService";
import { KnowledgeRadar } from "@/components/quiz/KnowledgeRadar";
import {
  GraduationCap,
  Sparkles,
  ArrowRight,
  BrainCircuit,
  BookOpen,
  BarChart3,
  Clock,
  Target,
  FileText,
  Compass,
  AlertCircle,
  RefreshCw,
  Zap,
  Mic
} from "lucide-react";

export default function StudentDashboardPage() {
  const { user, accessToken } = useAuthStore();

  const [profile, setProfile] = useState<LearnerProfile | null>(null);
  const [masteries, setMasteries] = useState<TopicMasterySummary[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadStudentData = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      if (accessToken) {
        const data = await onboardingService.getLearnerProfile(accessToken);
        setProfile(data);
      }
    } catch {
      // 404 or missing profile means onboarding is required
      setProfile(null);
    } finally {
      setIsLoading(false);
    }
    if (accessToken) {
      quizService.getMasteries(accessToken).then(setMasteries).catch(() => setMasteries([]));
    }
  }, [accessToken]);

  useEffect(() => {
    loadStudentData();
  }, [loadStudentData]);

  // After a server outage, reload by itself if this page is showing a load error.
  useOnReconnect(() => {
    if (errorMessage) void loadStudentData();
  });

  return (
    <ProtectedRoute allowedRoles={["student"]}>
      <div className="text-slate-100 p-4 sm:p-6 lg:p-8 relative font-sans flex flex-col flex-1">
        <div className="max-w-7xl mx-auto w-full space-y-8 relative z-10 flex-1">
          
          {/* Welcome Banner */}
          <div className="p-6 sm:p-8 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800/80 shadow-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold">
                <GraduationCap className="w-3.5 h-3.5" />
                Student Learning Dashboard
              </div>
              <h1 className="font-display leading-tight text-white text-3xl sm:text-5xl">
                Welcome back, <span className="bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">{user?.full_name || "Student"}</span>!
              </h1>
              <p className="text-xs sm:text-sm text-slate-400 max-w-2xl">
                Track your cognitive learning metrics, continue your adaptive roadmap, and engage with your Socratic AI ecosystem.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <Link href="/subjects">
                <button className="px-4 py-2.5 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-indigo-300 font-semibold text-xs transition-colors flex items-center gap-1.5 shadow-sm">
                  <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
                  Explore Subjects
                </button>
              </Link>
              <Link href="/onboarding/roadmap">
                <button className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/25 transition-all flex items-center gap-2 group">
                  Continue Learning
                  <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                </button>
              </Link>
              <Link href="/onboarding/profile">
                <button className="px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 font-semibold text-xs transition-colors flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5 text-indigo-400" />
                  View Profile
                </button>
              </Link>
            </div>
          </div>

          {/* Loading State */}
          {isLoading && (
            <div className="p-12 rounded-2xl bg-slate-900/40 border border-slate-800 flex flex-col items-center justify-center gap-4">
              <div className="w-10 h-10 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
              <p className="text-xs text-slate-400 font-mono animate-pulse">
                Loading learner progress metrics...
              </p>
            </div>
          )}

          {/* Error State */}
          {!isLoading && errorMessage && (
            <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <AlertCircle className="w-5 h-5 shrink-0" />
                <span>{errorMessage}</span>
              </div>
              <button
                onClick={loadStudentData}
                className="px-3 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-white font-semibold flex items-center gap-1.5 transition-colors"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Retry
              </button>
            </div>
          )}

          {/* Empty State: Onboarding Incomplete */}
          {!isLoading && !errorMessage && !profile && (
            <div className="p-8 sm:p-12 rounded-2xl bg-slate-900/60 border border-indigo-500/30 text-center space-y-5 max-w-3xl mx-auto shadow-2xl">
              <div className="w-14 h-14 rounded-2xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center mx-auto">
                <Sparkles className="w-7 h-7" />
              </div>
              <h3 className="text-xl font-bold text-white">Diagnostic Assessment Incomplete</h3>
              <p className="text-xs sm:text-sm text-slate-400 leading-relaxed max-w-lg mx-auto">
                To unlock your personalized VARK study roadmap and Socratic AI tutoring, please complete the initial 3-minute diagnostic assessment wizard.
              </p>
              <Link href="/onboarding" className="inline-block pt-2">
                <button className="px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 transition-all flex items-center gap-2">
                  Start Onboarding Assessment
                  <ArrowRight className="w-4 h-4" />
                </button>
              </Link>
            </div>
          )}

          {/* Learning Progress Section */}
          {!isLoading && profile && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-indigo-400" />
                  Your Learning Progress Summary
                </h2>
                <span className="text-xs text-slate-400 font-mono">
                  Assessed {new Date(profile.created_at).toLocaleDateString()}
                </span>
              </div>

              {/* Progress Metric Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                
                <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-3">
                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <span>Diagnostic Score</span>
                    <Target className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div className="text-3xl font-extrabold text-white">
                    {profile.assessment_score}<span className="text-sm font-normal text-slate-400">%</span>
                  </div>
                  <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                    <div
                      className="bg-emerald-500 h-full rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(100, Math.max(0, profile.assessment_score))}%` }}
                    />
                  </div>
                </div>

                <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-3">
                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <span>VARK Learning Style</span>
                    <Zap className="w-4 h-4 text-indigo-400" />
                  </div>
                  <div className="text-2xl font-extrabold text-indigo-400 capitalize">
                    {user?.preferred_modality || "Visual"}
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Content optimized for cognitive preference
                  </p>
                </div>

                <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-3">
                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <span>Weekly Target</span>
                    <Clock className="w-4 h-4 text-purple-400" />
                  </div>
                  <div className="text-3xl font-extrabold text-white">
                    {profile.recommended_weekly_hours} <span className="text-xs font-normal text-slate-400">hrs/wk</span>
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Recommended study pace
                  </p>
                </div>

                <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-3">
                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <span>Starting Focus</span>
                    <Compass className="w-4 h-4 text-amber-400" />
                  </div>
                  <div className="text-sm font-bold text-white truncate" title={profile.suggested_starting_topic}>
                    {profile.suggested_starting_topic}
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Priority focus module
                  </p>
                </div>

              </div>

              {/* Recommended Subjects from Onboarding */}
              {profile.selected_subjects && profile.selected_subjects.length > 0 && (
                <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800/80 flex flex-wrap items-center gap-2.5">
                  <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                    Recommended From Your Goals:
                  </span>
                  {profile.selected_subjects.map((subj, sIdx) => (
                    <Link
                      key={sIdx}
                      href="/subjects"
                      className="px-3 py-1 rounded-lg text-xs font-medium bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/20 transition-colors"
                    >
                      {subj}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Learning tools */}
          <div className="grid grid-cols-1 gap-6 pt-4 lg:grid-cols-[minmax(0,1fr)_22rem]">
            <div className="space-y-4">
              <h2 className="text-lg font-bold text-white">Keep learning</h2>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                {[
                  {
                    href: "/tutor",
                    icon: Mic,
                    tone: "text-indigo-300 bg-indigo-500/15",
                    title: "Socratic tutor",
                    body: "Talk or type through a problem. The faculty guides you with questions and hints, never the answer.",
                    cta: "Open the tutor",
                  },
                  {
                    href: "/quiz",
                    icon: BrainCircuit,
                    tone: "text-cyan-300 bg-cyan-500/15",
                    title: "Adaptive quiz",
                    body: "Calibrated questions that update your Bayesian mastery and name your misconceptions.",
                    cta: "Start a quiz",
                  },
                  {
                    href: "/subjects",
                    icon: BookOpen,
                    tone: "text-amber-300 bg-amber-500/15",
                    title: "Subject catalog",
                    body: "22 subjects with course tracks, syllabus modules and verified lessons.",
                    cta: "Browse subjects",
                  },
                ].map((card) => {
                  const Icon = card.icon;
                  return (
                    <Link
                      key={card.href}
                      href={card.href}
                      className="glass group flex flex-col rounded-3xl p-5 transition-colors hover:border-white/20 focus-visible:ring-2 focus-visible:ring-indigo-300"
                    >
                      <span className={`mb-4 flex h-10 w-10 items-center justify-center rounded-2xl ${card.tone}`}>
                        <Icon className="h-5 w-5" aria-hidden="true" />
                      </span>
                      <h3 className="text-base font-semibold text-white">{card.title}</h3>
                      <p className="mt-1.5 flex-1 text-sm leading-relaxed text-slate-300">{card.body}</p>
                      <span className="mt-4 inline-flex items-center gap-1.5 text-sm font-semibold text-indigo-300 group-hover:text-indigo-200">
                        {card.cta}
                        <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
                      </span>
                    </Link>
                  );
                })}
              </div>
            </div>
            <section aria-label="Mastery by topic" className="glass rounded-3xl p-5">
              <h2 className="text-sm font-semibold text-white">Mastery by topic</h2>
              <p className="mt-1 text-xs text-slate-400">Bayesian Knowledge Tracing from your quiz answers.</p>
              <div className="mt-4">
                {masteries.length > 0 ? (
                  <KnowledgeRadar items={masteries} />
                ) : (
                  <p className="rounded-2xl bg-white/[0.02] px-4 py-6 text-center text-sm text-slate-400">
                    Finish an adaptive quiz to see your mastery here.
                  </p>
                )}
              </div>
            </section>
          </div>

        </div>
      </div>
    </ProtectedRoute>
  );
}
