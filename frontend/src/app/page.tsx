"use client";

import React from "react";
import Link from "next/link";
import {
  Sparkles,
  ArrowRight,
  BrainCircuit,
  Compass,
  GraduationCap,
  School,
  ShieldCheck,
  Zap,
  Target,
  BarChart3,
  BookOpen,
  CheckCircle2,
  Lock,
  Cpu
} from "lucide-react";
import { Button } from "@/components/common/Button";
import { useAuthStore } from "@/stores/useAuthStore";
import { APP_NAME, APP_TAGLINE } from "@/utils/constants";

export default function Home() {
  const { isAuthenticated, user } = useAuthStore();

  const getDashboardLink = () => {
    if (!user) return "/dashboard";
    return user.role === "teacher" ? "/dashboard/teacher" : "/dashboard";
  };

  return (
    <main className="flex-1 flex flex-col items-center w-full relative overflow-hidden bg-slate-950 text-slate-100 font-sans">
      {/* Background Ambient Glows */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-indigo-600/15 blur-[160px] rounded-full pointer-events-none" />
      <div className="absolute top-1/3 right-10 w-[450px] h-[450px] bg-purple-600/10 blur-[140px] rounded-full pointer-events-none" />

      {/* Hero Section */}
      <section className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-20 md:pt-24 md:pb-32 flex flex-col items-center text-center relative z-10">
        
        {/* Eyebrow Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-8 backdrop-blur-md shadow-lg shadow-indigo-500/10 animate-fade-in">
          <Sparkles className="w-4 h-4 text-indigo-400 animate-pulse" />
          <span>Project Aurora • AI-Powered Adaptive Learning</span>
        </div>

        {/* Hero Title */}
        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight max-w-5xl leading-[1.1] mb-6 bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
          Personalized Socratic AI & Dynamic Learning Roadmaps
        </h1>

        {/* Hero Description */}
        <p className="text-base sm:text-xl text-slate-400 max-w-3xl font-normal leading-relaxed mb-10">
          {APP_NAME} — {APP_TAGLINE}. Our platform continuously evaluates your cognitive learning style (VARK model), diagnoses knowledge gaps with precision diagnostics, and guides your educational journey step-by-step.
        </p>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4 w-full max-w-md sm:max-w-none">
          {isAuthenticated && user ? (
            <Link href={getDashboardLink()}>
              <Button size="lg" className="bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold px-8 shadow-xl shadow-indigo-600/30 flex items-center gap-2 rounded-xl">
                Go to Your Dashboard ({user.role})
                <ArrowRight className="w-5 h-5" />
              </Button>
            </Link>
          ) : (
            <>
              <Link href="/register/student">
                <Button size="lg" className="bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold px-7 shadow-xl shadow-indigo-600/30 flex items-center gap-2 rounded-xl">
                  <GraduationCap className="w-5 h-5" />
                  Get Started as Student
                </Button>
              </Link>

              <Link href="/register/teacher">
                <Button size="lg" variant="outline" className="border-slate-800 bg-slate-900/80 hover:bg-slate-800 text-slate-200 font-semibold px-6 flex items-center gap-2 rounded-xl">
                  <School className="w-5 h-5 text-purple-400" />
                  Teacher Registration
                </Button>
              </Link>

              <Link href="/login">
                <Button size="lg" variant="ghost" className="text-slate-300 hover:text-white font-medium px-5">
                  Sign In
                </Button>
              </Link>
            </>
          )}
        </div>

        {/* Quick Highlights Pill Banner */}
        <div className="mt-16 pt-10 border-t border-slate-800/80 w-full max-w-4xl grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-medium text-slate-400">
          <div className="flex items-center justify-center gap-2 p-3 rounded-xl bg-slate-900/40 border border-slate-800/60">
            <Zap className="w-4 h-4 text-amber-400" />
            <span>VARK Personalization</span>
          </div>
          <div className="flex items-center justify-center gap-2 p-3 rounded-xl bg-slate-900/40 border border-slate-800/60">
            <BrainCircuit className="w-4 h-4 text-indigo-400" />
            <span>Socratic AI Diagnostics</span>
          </div>
          <div className="flex items-center justify-center gap-2 p-3 rounded-xl bg-slate-900/40 border border-slate-800/60">
            <Compass className="w-4 h-4 text-emerald-400" />
            <span>Adaptive Study Pathways</span>
          </div>
          <div className="flex items-center justify-center gap-2 p-3 rounded-xl bg-slate-900/40 border border-slate-800/60">
            <ShieldCheck className="w-4 h-4 text-purple-400" />
            <span>Enterprise Security</span>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 border-t border-slate-800/80 relative z-10">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <h2 className="text-xs font-bold uppercase tracking-widest text-indigo-400">
            Engineered For Excellence
          </h2>
          <h3 className="text-3xl sm:text-4xl font-extrabold text-white">
            Core Platform Features
          </h3>
          <p className="text-slate-400 text-sm sm:text-base leading-relaxed">
            LuminaLearn AI bridges cognitive psychology and artificial intelligence to deliver a truly custom educational environment.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          
          {/* Card 1 */}
          <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800/80 backdrop-blur-xl hover:border-indigo-500/40 transition-all group">
            <div className="w-12 h-12 rounded-xl bg-indigo-600/15 border border-indigo-500/30 flex items-center justify-center text-indigo-400 mb-5 group-hover:scale-110 transition-transform">
              <BrainCircuit className="w-6 h-6" />
            </div>
            <h4 className="text-lg font-bold text-white mb-2">Socratic AI Tutor</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Instead of giving direct answers, LuminaLearn guides students through guided questioning and step-by-step reasoning.
            </p>
          </div>

          {/* Card 2 */}
          <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800/80 backdrop-blur-xl hover:border-indigo-500/40 transition-all group">
            <div className="w-12 h-12 rounded-xl bg-purple-600/15 border border-purple-500/30 flex items-center justify-center text-purple-400 mb-5 group-hover:scale-110 transition-transform">
              <Zap className="w-6 h-6" />
            </div>
            <h4 className="text-lg font-bold text-white mb-2">VARK Modality Adaptation</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Adapts dynamically to Visual, Auditory, Read/Write, or Kinesthetic learning preferences for maximum comprehension.
            </p>
          </div>

          {/* Card 3 */}
          <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800/80 backdrop-blur-xl hover:border-indigo-500/40 transition-all group">
            <div className="w-12 h-12 rounded-xl bg-emerald-600/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mb-5 group-hover:scale-110 transition-transform">
              <Target className="w-6 h-6" />
            </div>
            <h4 className="text-lg font-bold text-white mb-2">Diagnostic Skill Assessment</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Real-time multi-subject quiz engine evaluating response accuracy and completion time to pin-point skill gaps.
            </p>
          </div>

          {/* Card 4 */}
          <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800/80 backdrop-blur-xl hover:border-indigo-500/40 transition-all group">
            <div className="w-12 h-12 rounded-xl bg-amber-600/15 border border-amber-500/30 flex items-center justify-center text-amber-400 mb-5 group-hover:scale-110 transition-transform">
              <Compass className="w-6 h-6" />
            </div>
            <h4 className="text-lg font-bold text-white mb-2">Personalized Study Roadmap</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Generates custom study modules, estimated weekly target hours, and tailored starting focus areas based on profile data.
            </p>
          </div>

          {/* Card 5 */}
          <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800/80 backdrop-blur-xl hover:border-indigo-500/40 transition-all group">
            <div className="w-12 h-12 rounded-xl bg-cyan-600/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400 mb-5 group-hover:scale-110 transition-transform">
              <BarChart3 className="w-6 h-6" />
            </div>
            <h4 className="text-lg font-bold text-white mb-2">Educator Analytics Dashboard</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Dedicated teacher portal providing macro-level class insights, student mastery tracking, and curriculum alignment tools.
            </p>
          </div>

          {/* Card 6 */}
          <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800/80 backdrop-blur-xl hover:border-indigo-500/40 transition-all group">
            <div className="w-12 h-12 rounded-xl bg-rose-600/15 border border-rose-500/30 flex items-center justify-center text-rose-400 mb-5 group-hover:scale-110 transition-transform">
              <Lock className="w-6 h-6" />
            </div>
            <h4 className="text-lg font-bold text-white mb-2">Enterprise Security & Auth</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              JWT token rotation, Argon2id password hashing, and role-based access control (RBAC) ensuring total privacy.
            </p>
          </div>

        </div>
      </section>

      {/* About Section */}
      <section id="about" className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 border-t border-slate-800/80 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-xs font-semibold uppercase tracking-wider">
              <BookOpen className="w-3.5 h-3.5" />
              <span>About LuminaLearn AI</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-white leading-tight">
              Transforming Education Through Explainable AI & Adaptive Pathways
            </h2>
            <p className="text-slate-400 text-sm leading-relaxed">
              LuminaLearn AI was founded on a singular premise: no two minds process information in the exact same manner. Traditional one-size-fits-all education leaves millions behind.
            </p>
            <p className="text-slate-400 text-sm leading-relaxed">
              By combining high-performance microservices, vector search, cognitive diagnostic modeling, and Explainable AI (XAI), our platform builds an accurate mental map for every learner.
            </p>

            <div className="space-y-3 pt-2">
              <div className="flex items-center gap-3 text-xs text-slate-200">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Continuous cognitive diagnostic evaluations</span>
              </div>
              <div className="flex items-center gap-3 text-xs text-slate-200">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Transparent Explainable AI (XAI) rationale for all recommendations</span>
              </div>
              <div className="flex items-center gap-3 text-xs text-slate-200">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Seamless integration across Student and Teacher workflows</span>
              </div>
            </div>
          </div>

          <div className="p-8 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900/90 to-indigo-950/40 border border-slate-800 shadow-2xl relative">
            <div className="space-y-6">
              <div className="flex items-center gap-3 pb-4 border-b border-slate-800">
                <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center text-white font-bold">
                  <Cpu className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white">Monorepo Engineering Architecture</h4>
                  <span className="text-xs text-slate-400 font-mono">Next.js 14 + FastAPI + PostgreSQL</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-xs font-mono">
                <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                  <span className="text-indigo-400 font-bold block mb-1">Frontend Client</span>
                  <span className="text-slate-400 text-[11px]">React 18, Tailwind CSS, Zustand, Lucide Icons</span>
                </div>
                <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                  <span className="text-purple-400 font-bold block mb-1">FastAPI Backend</span>
                  <span className="text-slate-400 text-[11px]">Async SQLAlchemy 2.0, Pydantic v2, Python 3.11</span>
                </div>
                <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                  <span className="text-emerald-400 font-bold block mb-1">Data Storage</span>
                  <span className="text-slate-400 text-[11px]">PostgreSQL 16, Redis Cache, Qdrant Vector</span>
                </div>
                <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                  <span className="text-amber-400 font-bold block mb-1">Security Standard</span>
                  <span className="text-slate-400 text-[11px]">OAuth2 JWT Bearer, Argon2id, RBAC</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* Role CTA Section */}
      <section className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 border-t border-slate-800/80 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* Student CTA */}
          <div className="p-8 rounded-2xl bg-gradient-to-br from-indigo-950/40 via-slate-900 to-slate-900 border border-indigo-500/30 flex flex-col justify-between space-y-6">
            <div>
              <div className="w-10 h-10 rounded-xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center mb-4">
                <GraduationCap className="w-5 h-5" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">Student Learning Portal</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Take your diagnostic assessment, unlock your VARK cognitive profile, and get your personalized roadmap.
              </p>
            </div>
            <Link href="/register/student">
              <Button size="default" className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold flex items-center justify-center gap-2">
                Register Student Account
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>

          {/* Teacher CTA */}
          <div className="p-8 rounded-2xl bg-gradient-to-br from-purple-950/40 via-slate-900 to-slate-900 border border-purple-500/30 flex flex-col justify-between space-y-6">
            <div>
              <div className="w-10 h-10 rounded-xl bg-purple-600/20 text-purple-400 flex items-center justify-center mb-4">
                <School className="w-5 h-5" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">Teacher & Educator Portal</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Access macro-level student analytics, monitor curriculum progress, and leverage AI diagnostic insights.
              </p>
            </div>
            <Link href="/register/teacher">
              <Button size="default" className="w-full bg-purple-600 hover:bg-purple-500 text-white font-semibold flex items-center justify-center gap-2">
                Register Teacher Account
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>

        </div>
      </section>

    </main>
  );
}
