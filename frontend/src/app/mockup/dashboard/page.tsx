"use client";

import React from "react";
import Link from "next/link";
import {
  LayoutDashboard,
  BookOpen,
  GitFork,
  Sparkles,
  HelpCircle,
  BarChart3,
  Trophy,
  Search,
  Bell,
  Check,
  ArrowRight,
  Flame,
  Award,
  BookMarked,
  FileCheck2,
  ChevronRight,
  AlertTriangle,
  GraduationCap
} from "lucide-react";

export default function StudentDashboardMockup() {

  return (
    <div className="w-full min-h-screen bg-[#F8FAFC] text-slate-900 flex font-sans antialiased">
      {/* LEFT SIDEBAR */}
      <aside className="w-64 bg-white border-r border-slate-200/80 flex flex-col justify-between shrink-0 shadow-[1px_0_3px_rgba(0,0,0,0.02)]">
        <div>
          {/* Logo */}
          <div className="h-16 px-6 flex items-center gap-3 border-b border-slate-100">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-600 via-indigo-600 to-violet-500 flex items-center justify-center shadow-sm shadow-blue-500/20">
              <span className="text-white font-bold text-sm tracking-tight">L</span>
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-slate-900 text-base tracking-tight leading-none">
                LuminaLearn <span className="text-blue-600">AI</span>
              </span>
              <span className="text-[10px] text-slate-400 font-medium tracking-wider uppercase mt-0.5">
                Adaptive Platform
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-3 space-y-1">
            {[
              { name: "Dashboard", icon: LayoutDashboard, href: "/mockup/dashboard", active: true },
              { name: "My Courses", icon: BookOpen, href: "#" },
              { name: "Learning Path", icon: GitFork, href: "#" },
              { name: "AI Tutor", icon: Sparkles, href: "/mockup/tutor", badge: "Live" },
              { name: "Quizzes", icon: HelpCircle, href: "#" },
              { name: "Progress", icon: BarChart3, href: "#" },
              { name: "Achievements", icon: Trophy, href: "#" }
            ].map((item) => {
              const Icon = item.icon;
              const isActive = item.active;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? "bg-blue-50 text-blue-700 font-semibold shadow-xs"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon
                      className={`w-4 h-4 ${
                        isActive ? "text-blue-600" : "text-slate-400"
                      }`}
                    />
                    <span>{item.name}</span>
                  </div>
                  {item.badge && (
                    <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-blue-100/80 text-blue-700 border border-blue-200">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Sidebar Footer User Card */}
        <div className="p-4 border-t border-slate-100">
          <div className="flex items-center gap-3 p-2 rounded-lg bg-slate-50 border border-slate-100">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-700 to-indigo-900 text-white font-semibold text-xs flex items-center justify-center">
              SK
            </div>
            <div className="flex flex-col min-w-0 flex-1">
              <span className="text-xs font-semibold text-slate-800 truncate">Saketh</span>
              <span className="text-[11px] text-slate-500 truncate">saketh@university.edu</span>
            </div>
          </div>
        </div>
      </aside>

      {/* MAIN CONTAINER */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* TOP BAR */}
        <header className="h-16 bg-white border-b border-slate-200/80 px-8 flex items-center justify-between shrink-0 sticky top-0 z-20 shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
          {/* Search */}
          <div className="relative w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search concepts, modules, quizzes..."
              className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-50 hover:bg-slate-100/70 focus:bg-white border border-slate-200 rounded-lg text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            />
          </div>

          {/* Right Top Bar Items */}
          <div className="flex items-center gap-5">
            {/* Notification */}
            <button className="relative p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors">
              <Bell className="w-4 h-4" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-blue-600 rounded-full ring-2 ring-white"></span>
            </button>

            <div className="h-5 w-px bg-slate-200" />

            {/* Student profile greeting */}
            <div className="flex items-center gap-3">
              <div className="text-right">
                <p className="text-sm font-semibold text-slate-900 leading-tight">
                  Good morning, Saketh
                </p>
                <p className="text-[11px] text-slate-500 font-medium">B.S. Computer Science • Sem 4</p>
              </div>
              <div className="w-9 h-9 rounded-full ring-2 ring-blue-500/20 bg-blue-100 text-blue-700 font-bold text-xs flex items-center justify-center">
                SK
              </div>
            </div>
          </div>
        </header>

        {/* DASHBOARD CONTENT BODY */}
        <main className="p-8 max-w-[1400px] w-full mx-auto space-y-6">
          {/* TOP SUMMARY CARDS (4 CARDS) */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Card 1: Learning Progress */}
            <div className="bg-white p-5 rounded-xl border border-slate-200/90 shadow-xs hover:border-slate-300 transition-all">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-500">Learning Progress</span>
                <span className="p-2 rounded-lg bg-blue-50 text-blue-600">
                  <GraduationCap className="w-4 h-4" />
                </span>
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="text-2xl font-bold text-slate-900 tracking-tight">72%</span>
                <span className="text-xs font-semibold text-emerald-600 flex items-center">
                  +4% this week
                </span>
              </div>
              <div className="mt-3 w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-blue-600 h-1.5 rounded-full transition-all duration-500"
                  style={{ width: "72%" }}
                />
              </div>
            </div>

            {/* Card 2: Current Streak */}
            <div className="bg-white p-5 rounded-xl border border-slate-200/90 shadow-xs hover:border-slate-300 transition-all">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-500">Current Streak</span>
                <span className="p-2 rounded-lg bg-amber-50 text-amber-600">
                  <Flame className="w-4 h-4 fill-amber-500/20" />
                </span>
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="text-2xl font-bold text-slate-900 tracking-tight">8 Days</span>
                <span className="text-xs font-medium text-slate-500">Personal Best: 14</span>
              </div>
              <p className="mt-3 text-[11px] text-slate-400">Keep it going! Study today to maintain streak.</p>
            </div>

            {/* Card 3: Quiz Average */}
            <div className="bg-white p-5 rounded-xl border border-slate-200/90 shadow-xs hover:border-slate-300 transition-all">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-500">Quiz Average</span>
                <span className="p-2 rounded-lg bg-indigo-50 text-indigo-600">
                  <Award className="w-4 h-4" />
                </span>
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="text-2xl font-bold text-slate-900 tracking-tight">81%</span>
                <span className="text-xs font-semibold text-emerald-600 flex items-center">
                  Top 15% class
                </span>
              </div>
              <p className="mt-3 text-[11px] text-slate-400">Based on 12 verified cognitive checks.</p>
            </div>

            {/* Card 4: Courses Active */}
            <div className="bg-white p-5 rounded-xl border border-slate-200/90 shadow-xs hover:border-slate-300 transition-all">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-500">Courses Active</span>
                <span className="p-2 rounded-lg bg-violet-50 text-violet-600">
                  <BookMarked className="w-4 h-4" />
                </span>
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="text-2xl font-bold text-slate-900 tracking-tight">4</span>
                <span className="text-xs font-medium text-slate-500">Curricula</span>
              </div>
              <p className="mt-3 text-[11px] text-slate-400">Next milestone: OOP Mastery check.</p>
            </div>
          </div>

          {/* MAIN GRID: 2 COLUMNS (LEFT 2/3, RIGHT 1/3) */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* LEFT / CENTER 2 COLUMNS */}
            <div className="lg:col-span-2 space-y-6">
              {/* SECTION: YOUR PERSONALIZED LEARNING PATH */}
              <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h2 className="text-base font-bold text-slate-900 tracking-tight">
                      Your Personalized Learning Path
                    </h2>
                    <p className="text-xs text-blue-600 font-medium mt-0.5 flex items-center gap-1.5">
                      <span className="inline-block w-1.5 h-1.5 rounded-full bg-blue-600 animate-pulse" />
                      Recommended based on your recent performance
                    </p>
                  </div>
                  <span className="text-xs px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 font-medium">
                    Adaptive Sequence
                  </span>
                </div>

                {/* Horizontal Roadmap */}
                <div className="pt-6 pb-4 px-2">
                  <div className="relative flex items-center justify-between">
                    {/* Background track line */}
                    <div className="absolute left-6 right-6 top-4 h-0.5 bg-slate-200 -z-0" />
                    {/* Active track progress fill up to OOP (50%) */}
                    <div className="absolute left-6 w-[48%] top-4 h-0.5 bg-blue-600 -z-0" />

                    {/* Step 1: Python Basics (Completed) */}
                    <div className="flex flex-col items-center relative z-10">
                      <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center shadow-xs ring-4 ring-white">
                        <Check className="w-4 h-4 stroke-[2.5]" />
                      </div>
                      <span className="mt-2 text-xs font-semibold text-slate-800">
                        Python Basics
                      </span>
                      <span className="text-[10px] text-emerald-600 font-medium">Completed</span>
                    </div>

                    {/* Step 2: Functions (Completed) */}
                    <div className="flex flex-col items-center relative z-10">
                      <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center shadow-xs ring-4 ring-white">
                        <Check className="w-4 h-4 stroke-[2.5]" />
                      </div>
                      <span className="mt-2 text-xs font-semibold text-slate-800">
                        Functions
                      </span>
                      <span className="text-[10px] text-emerald-600 font-medium">Completed</span>
                    </div>

                    {/* Step 3: OOP (Current) */}
                    <div className="flex flex-col items-center relative z-10">
                      <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center ring-4 ring-blue-100 shadow-sm shadow-blue-500/20">
                        <span className="w-2.5 h-2.5 rounded-full bg-white animate-pulse" />
                      </div>
                      <span className="mt-2 text-xs font-bold text-blue-700">OOP</span>
                      <span className="text-[10px] px-2 py-0.2 rounded-full bg-blue-100 text-blue-700 font-semibold uppercase tracking-wider">
                        Current
                      </span>
                    </div>

                    {/* Step 4: Exception Handling (Upcoming) */}
                    <div className="flex flex-col items-center relative z-10">
                      <div className="w-8 h-8 rounded-full bg-slate-100 border-2 border-slate-300 text-slate-400 flex items-center justify-center ring-4 ring-white">
                        <span className="w-2 h-2 rounded-full bg-slate-300" />
                      </div>
                      <span className="mt-2 text-xs font-medium text-slate-500">
                        Exception Handling
                      </span>
                      <span className="text-[10px] text-slate-400">Upcoming</span>
                    </div>

                    {/* Step 5: Data Structures (Upcoming) */}
                    <div className="flex flex-col items-center relative z-10">
                      <div className="w-8 h-8 rounded-full bg-slate-100 border-2 border-slate-300 text-slate-400 flex items-center justify-center ring-4 ring-white">
                        <span className="w-2 h-2 rounded-full bg-slate-300" />
                      </div>
                      <span className="mt-2 text-xs font-medium text-slate-500">
                        Data Structures
                      </span>
                      <span className="text-[10px] text-slate-400">Upcoming</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* SECOND SECTION: CONTINUE LEARNING */}
              <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-base font-bold text-slate-900 tracking-tight">
                    Continue Learning
                  </h2>
                  <Link
                    href="#"
                    className="text-xs text-blue-600 font-semibold hover:text-blue-700 flex items-center gap-1"
                  >
                    View syllabus <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>

                <div className="p-5 rounded-lg border border-slate-200 bg-slate-50/50 hover:bg-slate-50 transition-colors">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="space-y-1.5 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-100/70 text-blue-700">
                          Primary Course
                        </span>
                        <span className="text-xs text-slate-400">• Module 5 of 8</span>
                      </div>
                      <h3 className="text-lg font-bold text-slate-900">
                        Python Programming
                      </h3>
                      <p className="text-xs text-slate-600">
                        Current Topic:{" "}
                        <span className="font-semibold text-slate-800">
                          Object-Oriented Programming (Classes & Inheritance)
                        </span>
                      </p>

                      {/* Progress Bar */}
                      <div className="pt-2 max-w-md">
                        <div className="flex justify-between text-xs text-slate-500 mb-1">
                          <span>Overall Progress</span>
                          <span className="font-bold text-slate-800">68%</span>
                        </div>
                        <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all"
                            style={{ width: "68%" }}
                          />
                        </div>
                      </div>
                    </div>

                    <div className="shrink-0 flex items-center">
                      <button className="px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs tracking-wide shadow-sm shadow-blue-600/30 transition-all flex items-center gap-2">
                        Continue Learning
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* BOTTOM SECTION: RECENT QUIZ PERFORMANCE & WEAK TOPICS */}
              <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-base font-bold text-slate-900 tracking-tight">
                      Recent Quiz Performance
                    </h2>
                    <p className="text-xs text-slate-500">
                      Adaptive evaluation across your last 7 assessment attempts
                    </p>
                  </div>
                  <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2.5 py-1 rounded-md">
                    Last 14 Days
                  </span>
                </div>

                {/* Line Chart */}
                <div className="pt-2">
                  <div className="h-44 w-full relative">
                    {/* SVG Chart */}
                    <svg className="w-full h-full overflow-visible" viewBox="0 0 600 160">
                      <defs>
                        <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#2563EB" stopOpacity="0.18" />
                          <stop offset="100%" stopColor="#2563EB" stopOpacity="0.0" />
                        </linearGradient>
                      </defs>

                      {/* Horizontal Grid lines */}
                      <line x1="40" y1="20" x2="590" y2="20" stroke="#F1F5F9" strokeWidth="1" />
                      <line x1="40" y1="60" x2="590" y2="60" stroke="#F1F5F9" strokeWidth="1" />
                      <line x1="40" y1="100" x2="590" y2="100" stroke="#F1F5F9" strokeWidth="1" />
                      <line x1="40" y1="140" x2="590" y2="140" stroke="#E2E8F0" strokeWidth="1" />

                      {/* Y-Axis Labels */}
                      <text x="10" y="24" fontSize="10" fill="#94A3B8" fontWeight="500">100%</text>
                      <text x="15" y="64" fontSize="10" fill="#94A3B8" fontWeight="500">80%</text>
                      <text x="15" y="104" fontSize="10" fill="#94A3B8" fontWeight="500">60%</text>
                      <text x="15" y="144" fontSize="10" fill="#94A3B8" fontWeight="500">40%</text>

                      {/* Area Fill */}
                      <path
                        d="M 60 95 L 140 68 L 220 80 L 300 48 L 380 62 L 460 32 L 540 62 L 540 140 L 60 140 Z"
                        fill="url(#chartGradient)"
                      />

                      {/* Trend Line */}
                      <path
                        d="M 60 95 L 140 68 L 220 80 L 300 48 L 380 62 L 460 32 L 540 62"
                        fill="none"
                        stroke="#2563EB"
                        strokeWidth="2.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />

                      {/* Data Point Dots */}
                      {[
                        { cx: 60, cy: 95, val: "65%" },
                        { cx: 140, cy: 68, val: "78%" },
                        { cx: 220, cy: 80, val: "72%" },
                        { cx: 300, cy: 48, val: "88%" },
                        { cx: 380, cy: 62, val: "81%" },
                        { cx: 460, cy: 32, val: "94%" },
                        { cx: 540, cy: 62, val: "81%" }
                      ].map((pt, idx) => (
                        <g key={idx} className="group cursor-pointer">
                          <circle
                            cx={pt.cx}
                            cy={pt.cy}
                            r="4"
                            fill="#FFFFFF"
                            stroke="#2563EB"
                            strokeWidth="2.5"
                          />
                        </g>
                      ))}

                      {/* X-Axis labels */}
                      <text x="50" y="156" fontSize="10" fill="#64748B">Quiz 1</text>
                      <text x="130" y="156" fontSize="10" fill="#64748B">Quiz 2</text>
                      <text x="210" y="156" fontSize="10" fill="#64748B">Quiz 3</text>
                      <text x="290" y="156" fontSize="10" fill="#64748B">Quiz 4</text>
                      <text x="370" y="156" fontSize="10" fill="#64748B">Quiz 5</text>
                      <text x="450" y="156" fontSize="10" fill="#64748B">Quiz 6</text>
                      <text x="530" y="156" fontSize="10" fill="#64748B">Quiz 7</text>
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            {/* RIGHT PANEL (1 COLUMN) */}
            <div className="space-y-6">
              {/* AI RECOMMENDATION CARD */}
              <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs relative overflow-hidden">
                <div className="absolute top-0 right-0 w-24 h-24 bg-violet-500/5 rounded-full blur-2xl pointer-events-none" />
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-6 h-6 rounded-md bg-blue-50 text-blue-600 flex items-center justify-center">
                    <Sparkles className="w-3.5 h-3.5" />
                  </div>
                  <h3 className="text-sm font-bold text-slate-900 tracking-tight">
                    AI Recommendation
                  </h3>
                </div>

                <div className="p-3.5 rounded-lg bg-blue-50/50 border border-blue-100 text-xs text-slate-700 leading-relaxed">
                  “You performed well in <span className="font-semibold text-slate-900">Functions</span> but need more practice in <span className="font-semibold text-blue-700">Classes & Objects</span>.”
                </div>

                <div className="mt-4">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                    Recommended Actions
                  </span>
                  <div className="mt-2.5 space-y-2">
                    <button className="w-full text-left p-3 rounded-lg border border-slate-200 hover:border-blue-400 hover:bg-blue-50/30 transition-all flex items-center justify-between group">
                      <div className="flex items-center gap-2.5">
                        <BookOpen className="w-4 h-4 text-blue-600" />
                        <span className="text-xs font-semibold text-slate-800 group-hover:text-blue-700">
                          Review Classes & Objects
                        </span>
                      </div>
                      <ChevronRight className="w-3.5 h-3.5 text-slate-400 group-hover:translate-x-0.5 group-hover:text-blue-600 transition-all" />
                    </button>

                    <button className="w-full text-left p-3 rounded-lg border border-slate-200 hover:border-blue-400 hover:bg-blue-50/30 transition-all flex items-center justify-between group">
                      <div className="flex items-center gap-2.5">
                        <FileCheck2 className="w-4 h-4 text-violet-600" />
                        <span className="text-xs font-semibold text-slate-800 group-hover:text-violet-700">
                          Take 5-question practice quiz
                        </span>
                      </div>
                      <ChevronRight className="w-3.5 h-3.5 text-slate-400 group-hover:translate-x-0.5 group-hover:text-violet-600 transition-all" />
                    </button>
                  </div>
                </div>
              </div>

              {/* WEAK TOPICS CARD */}
              <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-500" />
                    Weak Topics
                  </h3>
                  <span className="text-[11px] text-slate-400">Needs Review</span>
                </div>

                <p className="text-xs text-slate-500 mb-4">
                  Flagged by cognitive diagnostic engine for immediate reinforcement.
                </p>

                <div className="space-y-3">
                  <div className="p-3 rounded-lg border border-slate-100 bg-slate-50/80 flex items-center justify-between">
                    <div>
                      <p className="text-xs font-semibold text-slate-800">Classes & Objects</p>
                      <p className="text-[11px] text-slate-500">Score: 54% • OOP Basics</p>
                    </div>
                    <span className="px-2.5 py-1 rounded-md bg-violet-100 text-violet-700 text-xs font-semibold">
                      Weak Topic
                    </span>
                  </div>

                  <div className="p-3 rounded-lg border border-slate-100 bg-slate-50/80 flex items-center justify-between">
                    <div>
                      <p className="text-xs font-semibold text-slate-800">Recursion</p>
                      <p className="text-[11px] text-slate-500">Score: 58% • Call Stack</p>
                    </div>
                    <span className="px-2.5 py-1 rounded-md bg-violet-100 text-violet-700 text-xs font-semibold">
                      Weak Topic
                    </span>
                  </div>
                </div>

                {/* AI Tutor Direct Link */}
                <div className="mt-4 pt-4 border-t border-slate-100">
                  <Link
                    href="/mockup/tutor"
                    className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-semibold transition-colors"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    Ask Lumina AI Tutor to Explain
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
