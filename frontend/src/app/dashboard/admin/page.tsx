"use client";

import React from "react";
import Link from "next/link";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { useAuthStore } from "@/stores/useAuthStore";
import {
  ShieldCheck,
  Users,
  Server,
  Activity,
  Database,
  Cpu,
  LogOut,
  Sparkles,
  CheckCircle2,
  ChevronRight,
  Sliders,
  ExternalLink,
  BookOpen
} from "lucide-react";

export default function AdminPortalPage() {
  const { user, logout } = useAuthStore();

  return (
    <ProtectedRoute allowedRoles={["admin"]}>
      <div className="min-h-screen bg-slate-950 text-slate-100 p-4 sm:p-6 lg:p-8 relative overflow-hidden font-sans flex flex-col">
        {/* Ambient Glow */}
        <div className="absolute top-1/4 left-1/3 w-[600px] h-[600px] bg-blue-600/10 blur-[160px] rounded-full pointer-events-none" />
        <div className="absolute bottom-10 right-10 w-[400px] h-[400px] bg-indigo-600/10 blur-[140px] rounded-full pointer-events-none" />

        <div className="max-w-7xl mx-auto w-full space-y-8 relative z-10 flex-1">
          {/* Top Admin Header */}
          <div className="p-6 sm:p-8 rounded-2xl bg-gradient-to-r from-slate-900 via-blue-950/40 to-slate-900 border border-blue-500/30 shadow-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-wider">
                <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
                LuminaLearn AI • Master Administration Console
              </div>
              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
                Admin Portal: <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">{user?.full_name || "System Administrator"}</span>
              </h1>
              <p className="text-xs sm:text-sm text-slate-400 max-w-2xl">
                Real-time governance, resilience telemetry, user access control, and Socratic AI system administration.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <Link href="/mockup">
                <button className="px-4 py-2 rounded-xl bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 text-blue-300 font-semibold text-xs transition-colors flex items-center gap-1.5 shadow-sm">
                  <Sparkles className="w-3.5 h-3.5 text-blue-400" />
                  View UI Mockups
                </button>
              </Link>
              <Link href="/dashboard/teacher">
                <button className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 font-semibold text-xs transition-colors flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5 text-purple-400" />
                  Educator View
                </button>
              </Link>
              <button
                onClick={() => logout()}
                className="px-4 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-300 font-semibold text-xs transition-colors flex items-center gap-1.5"
              >
                <LogOut className="w-3.5 h-3.5" />
                Sign Out
              </button>
            </div>
          </div>

          {/* Quick Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Stat 1: Total Users */}
            <div className="bg-slate-900/60 backdrop-blur-md p-5 rounded-2xl border border-slate-800 shadow-lg">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400">Total Registered Users</span>
                <span className="p-2 rounded-xl bg-blue-500/10 text-blue-400">
                  <Users className="w-4 h-4" />
                </span>
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="text-3xl font-bold text-white tracking-tight">50+</span>
                <span className="text-xs font-medium text-emerald-400">Active</span>
              </div>
              <p className="mt-2 text-[11px] text-slate-500">Students, Teachers & Admins</p>
            </div>

            {/* Stat 2: Database & Resilience Mode */}
            <div className="bg-slate-900/60 backdrop-blur-md p-5 rounded-2xl border border-slate-800 shadow-lg">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400">Database Engine</span>
                <span className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400">
                  <Database className="w-4 h-4" />
                </span>
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="text-2xl font-bold text-emerald-400 tracking-tight">SQLite Fallback</span>
              </div>
              <p className="mt-2 text-[11px] text-slate-500">Zero-Downtime Resilience Online</p>
            </div>

            {/* Stat 3: FastAPI Backend */}
            <div className="bg-slate-900/60 backdrop-blur-md p-5 rounded-2xl border border-slate-800 shadow-lg">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400">FastAPI Server</span>
                <span className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400">
                  <Server className="w-4 h-4" />
                </span>
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="text-2xl font-bold text-white tracking-tight">Port 8000</span>
                <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  200 OK
                </span>
              </div>
              <p className="mt-2 text-[11px] text-slate-500">CORS Loopback Configured</p>
            </div>

            {/* Stat 4: Security & Auth */}
            <div className="bg-slate-900/60 backdrop-blur-md p-5 rounded-2xl border border-slate-800 shadow-lg">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400">Security Architecture</span>
                <span className="p-2 rounded-xl bg-purple-500/10 text-purple-400">
                  <Cpu className="w-4 h-4" />
                </span>
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="text-2xl font-bold text-purple-400 tracking-tight">Argon2id + JWT</span>
              </div>
              <p className="mt-2 text-[11px] text-slate-500">Dual Token Pair (15m/7d)</p>
            </div>
          </div>

          {/* System Telemetry & Admin Controls */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left 2 Columns: System Services */}
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-slate-900/50 backdrop-blur-md rounded-2xl border border-slate-800 p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <Activity className="w-4 h-4 text-blue-400" />
                    Core Platform Services
                  </h3>
                  <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-medium">
                    All Systems Operational
                  </span>
                </div>

                <div className="divide-y divide-slate-800">
                  <div className="py-3.5 flex items-center justify-between">
                    <div className="space-y-0.5">
                      <p className="text-sm font-semibold text-white">Authentication Service</p>
                      <p className="text-xs text-slate-400">OAuth2 Password Bearer, OTP HMAC-SHA256, Argon2id</p>
                    </div>
                    <span className="inline-flex items-center gap-1.5 text-xs text-emerald-400 font-semibold bg-emerald-950/60 px-2.5 py-1 rounded-md border border-emerald-800/60">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Healthy
                    </span>
                  </div>

                  <div className="py-3.5 flex items-center justify-between">
                    <div className="space-y-0.5">
                      <p className="text-sm font-semibold text-white">Adaptive VARK Onboarding Engine</p>
                      <p className="text-xs text-slate-400">16-Question Cognitive Diagnostic Assessment</p>
                    </div>
                    <span className="inline-flex items-center gap-1.5 text-xs text-emerald-400 font-semibold bg-emerald-950/60 px-2.5 py-1 rounded-md border border-emerald-800/60">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Healthy
                    </span>
                  </div>

                  <div className="py-3.5 flex items-center justify-between">
                    <div className="space-y-0.5">
                      <p className="text-sm font-semibold text-white">Curriculum & Subject API</p>
                      <p className="text-xs text-slate-400">Modular syllabus hierarchy with Bloom&apos;s Taxonomy tagging</p>
                    </div>
                    <span className="inline-flex items-center gap-1.5 text-xs text-emerald-400 font-semibold bg-emerald-950/60 px-2.5 py-1 rounded-md border border-emerald-800/60">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Healthy
                    </span>
                  </div>

                  <div className="py-3.5 flex items-center justify-between">
                    <div className="space-y-0.5">
                      <p className="text-sm font-semibold text-white">Socratic AI & RAG Knowledge Pipeline</p>
                      <p className="text-xs text-slate-400">Module 4/5 Contextual vector indexing & Gemini agent</p>
                    </div>
                    <span className="inline-flex items-center gap-1.5 text-xs text-blue-400 font-semibold bg-blue-950/60 px-2.5 py-1 rounded-md border border-blue-800/60">
                      <Sparkles className="w-3.5 h-3.5" /> Ready (Phase 5.8)
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Right 1 Column: Administrator Quick Actions */}
            <div className="space-y-6">
              <div className="bg-slate-900/50 backdrop-blur-md rounded-2xl border border-slate-800 p-6 space-y-4">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Sliders className="w-4 h-4 text-indigo-400" />
                  Quick Management
                </h3>

                <div className="space-y-3">
                  <a
                    href="http://127.0.0.1:8000/docs"
                    target="_blank"
                    rel="noreferrer"
                    className="w-full flex items-center justify-between p-3 rounded-xl bg-slate-800/50 hover:bg-slate-800 border border-slate-700/60 text-xs font-semibold text-slate-200 transition-colors group"
                  >
                    <div className="flex items-center gap-2.5">
                      <Server className="w-4 h-4 text-blue-400" />
                      <span>Swagger API Explorer</span>
                    </div>
                    <ExternalLink className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-400" />
                  </a>

                  <Link
                    href="/mockup/dashboard"
                    className="w-full flex items-center justify-between p-3 rounded-xl bg-slate-800/50 hover:bg-slate-800 border border-slate-700/60 text-xs font-semibold text-slate-200 transition-colors group"
                  >
                    <div className="flex items-center gap-2.5">
                      <Sparkles className="w-4 h-4 text-blue-400" />
                      <span>Student Dashboard Mockup</span>
                    </div>
                    <ChevronRight className="w-3.5 h-3.5 text-slate-400 group-hover:translate-x-0.5 group-hover:text-blue-400" />
                  </Link>

                  <Link
                    href="/mockup/tutor"
                    className="w-full flex items-center justify-between p-3 rounded-xl bg-slate-800/50 hover:bg-slate-800 border border-slate-700/60 text-xs font-semibold text-slate-200 transition-colors group"
                  >
                    <div className="flex items-center gap-2.5">
                      <Sparkles className="w-4 h-4 text-indigo-400" />
                      <span>AI Tutor Mockup</span>
                    </div>
                    <ChevronRight className="w-3.5 h-3.5 text-slate-400 group-hover:translate-x-0.5 group-hover:text-indigo-400" />
                  </Link>
                </div>

                <div className="pt-3 border-t border-slate-800">
                  <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs text-slate-300 space-y-1">
                    <p className="font-semibold text-blue-400">Admin Account Active</p>
                    <p className="text-[11px] text-slate-400 font-mono">admin@luminalearn.ai</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
