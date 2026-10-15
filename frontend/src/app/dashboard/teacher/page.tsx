"use client";

import React from "react";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { useAuthStore } from "@/stores/useAuthStore";
import {
  School,
  Users,
  BookOpen,
  BarChart3,
  BrainCircuit
} from "lucide-react";

export default function TeacherDashboardPage() {
  const { user } = useAuthStore();

  return (
    <ProtectedRoute allowedRoles={["teacher", "admin"]}>
      <div className="min-h-screen bg-slate-950 text-slate-100 p-4 sm:p-6 lg:p-8 relative overflow-hidden font-sans flex flex-col">
        {/* Ambient Glow */}
        <div className="absolute top-1/4 right-1/3 w-[500px] h-[500px] bg-purple-600/10 blur-[150px] rounded-full pointer-events-none" />

        <div className="max-w-7xl mx-auto w-full space-y-8 relative z-10 flex-1">
          
          {/* Welcome Banner */}
          <div className="p-6 sm:p-8 rounded-2xl bg-gradient-to-r from-slate-900 via-purple-950/40 to-slate-900 border border-purple-500/30 shadow-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-xs font-semibold uppercase tracking-wider">
                <School className="w-3.5 h-3.5" />
                Educator Portal Dashboard
              </div>
              <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-white">
                Welcome, <span className="bg-gradient-to-r from-purple-400 to-indigo-400 bg-clip-text text-transparent">{user?.full_name || "Educator"}</span>!
              </h1>
              <p className="text-xs sm:text-sm text-slate-400 max-w-2xl">
                Manage your classrooms, review student diagnostic analytics, and leverage Explainable AI to address learning gaps.
              </p>
            </div>

            <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-purple-400 font-mono">
              <span>Role: Educator</span>
            </div>
          </div>

          {/* Teacher Tool Cards Grid (Coming Soon) */}
          <div className="space-y-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-purple-400" />
              Teacher Analytics & Classroom Management
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              
              {/* Class Insights */}
              <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800/80 relative overflow-hidden group">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl bg-purple-600/20 text-purple-400 flex items-center justify-center">
                    <Users className="w-5 h-5" />
                  </div>
                  <span className="px-2.5 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-[10px] font-bold uppercase tracking-wider">
                    Coming Soon
                  </span>
                </div>
                <h3 className="text-base font-bold text-white mb-2">Classroom Mastery Roster</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-4">
                  View individual student VARK learning styles, diagnostic scores, and active study pacing.
                </p>
                <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-500 font-mono">
                  <span>Status: UI Design</span>
                  <span>v1.2 Release</span>
                </div>
              </div>

              {/* Curriculum Manager */}
              <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800/80 relative overflow-hidden group">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center">
                    <BookOpen className="w-5 h-5" />
                  </div>
                  <span className="px-2.5 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[10px] font-bold uppercase tracking-wider">
                    Coming Soon
                  </span>
                </div>
                <h3 className="text-base font-bold text-white mb-2">Curriculum Builder</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-4">
                  Assign custom diagnostic quizzes and map course modules directly to student learning pathways.
                </p>
                <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-500 font-mono">
                  <span>Status: Schema Spec</span>
                  <span>v1.3 Release</span>
                </div>
              </div>

              {/* AI Interventions */}
              <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800/80 relative overflow-hidden group">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl bg-emerald-600/20 text-emerald-400 flex items-center justify-center">
                    <BrainCircuit className="w-5 h-5" />
                  </div>
                  <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-bold uppercase tracking-wider">
                    Coming Soon
                  </span>
                </div>
                <h3 className="text-base font-bold text-white mb-2">AI Knowledge Gap Heatmap</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-4">
                  Identify real-time class conceptual stumbling blocks and generate targeted remediation materials.
                </p>
                <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-500 font-mono">
                  <span>Status: Model Training</span>
                  <span>v1.4 Release</span>
                </div>
              </div>

            </div>
          </div>

        </div>
      </div>
    </ProtectedRoute>
  );
}
