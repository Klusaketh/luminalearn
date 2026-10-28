"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  LayoutDashboard,
  BookOpen,
  GitFork,
  Sparkles,
  HelpCircle,
  BarChart3,
  Trophy,
  Send,
  CheckCircle2,
  BookmarkCheck,
  Database,
  Code2,
  Copy,
  Check,
  RotateCcw,
  Sparkle
} from "lucide-react";

export default function AITutorMockup() {
  const [copied, setCopied] = useState(false);
  const [inputValue, setInputValue] = useState("");

  const handleCopy = () => {
    navigator.clipboard?.writeText(`def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

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
              { name: "Dashboard", icon: LayoutDashboard, href: "/mockup/dashboard" },
              { name: "My Courses", icon: BookOpen, href: "#" },
              { name: "Learning Path", icon: GitFork, href: "#" },
              { name: "AI Tutor", icon: Sparkles, href: "/mockup/tutor", active: true },
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
                  {isActive && (
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-600" />
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
      <div className="flex-1 flex flex-col min-w-0">
        {/* TOP BAR / APP HEADER */}
        <header className="h-16 bg-white border-b border-slate-200/80 px-8 flex items-center justify-between shrink-0 sticky top-0 z-20 shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold text-slate-900 tracking-tight">
                Lumina AI Tutor
              </h1>
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200/70 text-[11px] font-medium">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-pulse" />
                Active Context
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Ask questions based on your course material
            </p>
          </div>

          <div className="flex items-center gap-4">
            {/* Small status: Knowledge source */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200/80 text-xs">
              <div className="w-2 h-2 rounded-full bg-emerald-500" />
              <span className="text-slate-500 font-medium">Knowledge source:</span>
              <span className="font-semibold text-slate-800">
                Python Programming Course
              </span>
            </div>

            <div className="h-5 w-px bg-slate-200" />

            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full ring-2 ring-blue-500/20 bg-blue-100 text-blue-700 font-bold text-xs flex items-center justify-center">
                SK
              </div>
            </div>
          </div>
        </header>

        {/* WORKSPACE AREA: CHAT & LEARNING CONTEXT SIDE PANEL */}
        <div className="flex-1 flex min-h-0 overflow-hidden">
          {/* CHAT INTERFACE (FLEX-1) */}
          <div className="flex-1 flex flex-col min-w-0 bg-[#F8FAFC]">
            {/* Scrollable Conversation Thread */}
            <div className="flex-1 overflow-y-auto p-8 space-y-6 max-w-4xl mx-auto w-full">
              {/* Context Pill Indicator */}
              <div className="flex items-center justify-center">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white border border-slate-200/80 shadow-xs text-xs text-slate-500">
                  <Database className="w-3.5 h-3.5 text-blue-600" />
                  <span>Curriculum Vector Memory Synced • Module 4 & 5 Loaded</span>
                </div>
              </div>

              {/* Student Message */}
              <div className="flex justify-end items-start gap-3">
                <div className="bg-blue-600 text-white px-5 py-3 rounded-2xl rounded-tr-xs shadow-sm max-w-xl">
                  <p className="text-sm leading-relaxed">
                    Can you explain recursion with a simple example?
                  </p>
                </div>
                <div className="w-8 h-8 rounded-full bg-slate-200 text-slate-700 text-xs font-semibold flex items-center justify-center shrink-0">
                  SK
                </div>
              </div>

              {/* AI Tutor Response Card */}
              <div className="flex justify-start items-start gap-3.5">
                {/* AI Tutor Avatar */}
                <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-600 via-indigo-600 to-violet-600 text-white flex items-center justify-center shadow-xs shrink-0">
                  <Sparkles className="w-4 h-4" />
                </div>

                {/* Content Box */}
                <div className="flex-1 bg-white border border-slate-200/90 rounded-2xl rounded-tl-xs p-6 shadow-xs space-y-5 max-w-3xl">
                  {/* Explanation Paragraph */}
                  <div className="space-y-2">
                    <p className="text-sm text-slate-800 leading-relaxed font-normal">
                      Recursion is a technique where a function calls itself to solve a smaller version of the same problem.
                    </p>
                  </div>

                  {/* Code Snippet Box */}
                  <div className="rounded-xl overflow-hidden border border-slate-800 bg-[#0F172A] text-slate-100 shadow-sm">
                    {/* Header */}
                    <div className="flex items-center justify-between px-4 py-2 bg-slate-900 border-b border-slate-800 text-xs text-slate-400">
                      <div className="flex items-center gap-2">
                        <Code2 className="w-3.5 h-3.5 text-blue-400" />
                        <span className="font-mono text-[11px] font-semibold text-slate-300">
                          factorial_example.py
                        </span>
                      </div>
                      <button
                        onClick={handleCopy}
                        className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-white transition-colors"
                      >
                        {copied ? (
                          <>
                            <Check className="w-3 h-3 text-emerald-400" />
                            <span className="text-emerald-400">Copied</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3 h-3" />
                            <span>Copy code</span>
                          </>
                        )}
                      </button>
                    </div>

                    {/* Code Content */}
                    <div className="p-4 font-mono text-xs leading-relaxed overflow-x-auto text-slate-200">
                      <div>
                        <span className="text-violet-400 font-semibold">def</span>{" "}
                        <span className="text-blue-400">factorial</span>(n):
                      </div>
                      <div className="pl-4">
                        <span className="text-violet-400 font-semibold">if</span> n =={" "}
                        <span className="text-amber-400">0</span>:
                      </div>
                      <div className="pl-8">
                        <span className="text-violet-400 font-semibold">return</span>{" "}
                        <span className="text-amber-400">1</span>
                      </div>
                      <div className="pl-4">
                        <span className="text-violet-400 font-semibold">return</span> n *{" "}
                        <span className="text-blue-400">factorial</span>(n -{" "}
                        <span className="text-amber-400">1</span>)
                      </div>
                    </div>
                  </div>

                  {/* "Why this works" Section */}
                  <div className="space-y-2 pt-1">
                    <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                      Why this works
                    </h4>
                    <ul className="space-y-2 text-xs text-slate-600 pl-1">
                      <li className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-600 mt-1.5 shrink-0" />
                        <span>
                          <strong className="text-slate-800">Base case stops the recursion</strong> — prevents infinite call loop when n reaches 0.
                        </span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-600 mt-1.5 shrink-0" />
                        <span>
                          <strong className="text-slate-800">Each call reduces the problem size</strong> — n decrementing by 1 moves step-by-step toward the base condition.
                        </span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-600 mt-1.5 shrink-0" />
                        <span>
                          <strong className="text-slate-800">Results return back through previous calls</strong> — multiplying the stacked values as the call stack unwinds.
                        </span>
                      </li>
                    </ul>
                  </div>

                  {/* "Source Context" RAG indicator */}
                  <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80 flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-1.5 text-[11px] font-bold text-slate-800 uppercase tracking-wide">
                        <BookmarkCheck className="w-3.5 h-3.5 text-blue-600" />
                        Source Context
                      </div>
                      <div className="mt-1 text-xs text-slate-600 space-y-0.5">
                        <p>• Module 4: Functions</p>
                        <p>• Lesson: Recursion Basics</p>
                      </div>
                    </div>
                    <span className="text-[10px] font-medium text-slate-400 bg-white border border-slate-200 px-2 py-0.5 rounded">
                      Curriculum Verified
                    </span>
                  </div>

                  {/* Interactive Action Buttons */}
                  <div className="pt-2 flex flex-wrap items-center gap-2">
                    <button className="px-3.5 py-1.5 rounded-lg border border-slate-200 hover:border-blue-400 hover:bg-blue-50/50 text-xs font-semibold text-slate-700 hover:text-blue-700 transition-all flex items-center gap-1.5 shadow-2xs">
                      <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                      Explain Simpler
                    </button>
                    <button className="px-3.5 py-1.5 rounded-lg border border-slate-200 hover:border-blue-400 hover:bg-blue-50/50 text-xs font-semibold text-slate-700 hover:text-blue-700 transition-all flex items-center gap-1.5 shadow-2xs">
                      <RotateCcw className="w-3.5 h-3.5 text-indigo-600" />
                      Give Another Example
                    </button>
                    <button className="px-3.5 py-1.5 rounded-lg bg-blue-50 border border-blue-200 hover:bg-blue-100 text-xs font-semibold text-blue-700 transition-all flex items-center gap-1.5 shadow-2xs">
                      <CheckCircle2 className="w-3.5 h-3.5 text-blue-600" />
                      Practice This Topic
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* BOTTOM INPUT BAR */}
            <div className="p-4 bg-white border-t border-slate-200/80 shrink-0">
              <div className="max-w-4xl mx-auto flex items-center gap-3">
                <div className="relative flex-1">
                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="Ask anything about your course..."
                    className="w-full pl-4 pr-12 py-3 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-sm text-slate-800 placeholder-slate-400 transition-all"
                  />
                  <div className="absolute right-3 top-1/2 -translate-y-1/2 text-[11px] text-slate-400 font-mono">
                    ↵ Return
                  </div>
                </div>
                <button className="px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs tracking-wide shadow-sm shadow-blue-600/30 transition-all flex items-center gap-1.5 shrink-0">
                  <span>Send</span>
                  <Send className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>

          {/* RIGHT SIDE PANEL: "Your Learning Context" */}
          <aside className="w-80 bg-white border-l border-slate-200/80 p-6 flex flex-col justify-between shrink-0 overflow-y-auto">
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <h3 className="text-sm font-bold text-slate-900 tracking-tight">
                  Your Learning Context
                </h3>
                <span className="text-[11px] text-blue-600 font-semibold bg-blue-50 px-2 py-0.5 rounded">
                  Live Adaptive
                </span>
              </div>

              {/* Learning Context Cards */}
              <div className="space-y-4">
                {/* Current Course */}
                <div className="p-3.5 rounded-lg border border-slate-100 bg-slate-50/70">
                  <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">
                    Current Course
                  </span>
                  <p className="mt-1 text-sm font-bold text-slate-900">
                    Python Programming
                  </p>
                </div>

                {/* Current Level */}
                <div className="p-3.5 rounded-lg border border-slate-100 bg-slate-50/70">
                  <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">
                    Current Level
                  </span>
                  <p className="mt-1 text-sm font-bold text-slate-900">
                    Intermediate
                  </p>
                </div>

                {/* Weak Topic */}
                <div className="p-3.5 rounded-lg border border-slate-100 bg-slate-50/70">
                  <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">
                    Weak Topic
                  </span>
                  <div className="mt-1.5">
                    <span className="inline-block px-2.5 py-1 rounded-md bg-violet-100 text-violet-700 text-xs font-bold tracking-tight">
                      Recursion
                    </span>
                  </div>
                </div>

                {/* Recent Quiz */}
                <div className="p-3.5 rounded-lg border border-slate-100 bg-slate-50/70">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">
                      Recent Quiz
                    </span>
                    <span className="text-sm font-bold text-amber-600">58%</span>
                  </div>
                  <div className="mt-2 w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
                    <div
                      className="bg-amber-500 h-1.5 rounded-full"
                      style={{ width: "58%" }}
                    />
                  </div>
                </div>

                {/* Recommendation Box */}
                <div className="p-4 rounded-xl border border-blue-100 bg-blue-50/60 relative overflow-hidden">
                  <div className="flex items-start gap-2.5">
                    <div className="w-5 h-5 rounded-full bg-blue-600 text-white flex items-center justify-center shrink-0 mt-0.5">
                      <Sparkle className="w-3 h-3" />
                    </div>
                    <div className="space-y-1">
                      <span className="text-[11px] font-bold text-blue-900 uppercase tracking-wider">
                        Recommendation
                      </span>
                      <p className="text-xs text-blue-800 font-medium leading-relaxed">
                        “Practice recursion before moving to advanced functions.”
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Bottom Actions in Right Panel */}
            <div className="pt-6 border-t border-slate-100 space-y-2">
              <Link
                href="/mockup/dashboard"
                className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold transition-colors"
              >
                <LayoutDashboard className="w-3.5 h-3.5" />
                Return to Dashboard
              </Link>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
