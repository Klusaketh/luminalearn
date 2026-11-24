"use client";

import React, { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { ArrowRight, CheckCircle2, Code2, Cpu, ShieldCheck } from "lucide-react";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { GlassPanel } from "@/components/ui/GlassPanel";
import { SegmentedControl } from "@/components/ui/SegmentedControl";
import { DIFFICULTY_TONE } from "@/components/practice/format";
import { practiceService, type PracticeProblemList } from "@/services/practiceService";
import { cn } from "@/utils/cn";

type Filter = "all" | "Easy" | "Medium" | "todo";

const FILTERS = [
  { value: "all" as const, label: "All" },
  { value: "Easy" as const, label: "Easy" },
  { value: "Medium" as const, label: "Medium" },
  { value: "todo" as const, label: "Unsolved" },
];

function PracticeList() {
  const [data, setData] = useState<PracticeProblemList | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<Filter>("all");

  useEffect(() => {
    const controller = new AbortController();
    practiceService
      .list(controller.signal)
      .then(setData)
      .catch((err: unknown) => {
        if (!controller.signal.aborted) setError(err instanceof Error ? err.message : "Could not load the problems.");
      });
    return () => controller.abort();
  }, []);

  const problems = useMemo(() => {
    const all = data?.problems ?? [];
    if (filter === "todo") return all.filter((p) => !p.solved);
    if (filter === "all") return all;
    return all.filter((p) => p.difficulty === filter);
  }, [data, filter]);

  const percent = data && data.total_count ? Math.round((data.solved_count / data.total_count) * 100) : 0;

  return (
    <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:px-6 sm:py-12 lg:px-8">
      <p className="text-sm font-medium text-indigo-300">Coding practice</p>
      <h1 className="mt-2 font-display text-4xl text-white sm:text-5xl">Practise, run, get unstuck</h1>
      <p className="mt-3 max-w-2xl text-slate-300">
        Solve interview-style problems in Python or JavaScript. Your code runs instantly in your browser against real tests, and when
        you are stuck the Socratic tutor guides you with questions instead of handing you the answer.
      </p>

      <div className="mt-6 grid gap-3 sm:grid-cols-3">
        {[
          { icon: Code2, title: "Real editor", text: "Syntax highlighting, auto-indent, Ctrl+Enter to run." },
          { icon: Cpu, title: "Runs in your browser", text: "Python via WebAssembly and JavaScript in a sandboxed worker. Nothing runs on our servers." },
          { icon: ShieldCheck, title: "Hints, not answers", text: "A three-step hint ladder and the Socratic tutor." },
        ].map(({ icon: Icon, title, text }) => (
          <div key={title} className="rounded-2xl bg-white/[0.02] p-4 ring-1 ring-white/[0.07]">
            <Icon className="h-5 w-5 text-indigo-300" aria-hidden="true" />
            <p className="mt-2 font-semibold text-white">{title}</p>
            <p className="mt-1 text-sm text-slate-400">{text}</p>
          </div>
        ))}
      </div>

      {data && (
        <GlassPanel className="mt-8 p-5">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-sm text-slate-400">Your progress</p>
              <p className="mt-1 text-2xl font-semibold text-white">
                {data.solved_count} <span className="text-base font-normal text-slate-400">of {data.total_count} solved</span>
              </p>
            </div>
            <SegmentedControl label="Filter problems" options={FILTERS} value={filter} onChange={setFilter} />
          </div>
          <div
            className="mt-4 h-2 overflow-hidden rounded-full bg-white/[0.06]"
            role="progressbar"
            aria-label="Problems solved"
            aria-valuenow={percent}
            aria-valuemin={0}
            aria-valuemax={100}
          >
            <div className="h-full rounded-full bg-gradient-to-r from-indigo-400 to-cyan-300 transition-all" style={{ width: `${percent}%` }} />
          </div>
        </GlassPanel>
      )}

      {error && (
        <p role="alert" className="mt-8 rounded-2xl bg-rose-500/10 px-4 py-3 text-sm text-rose-100 ring-1 ring-rose-400/25">
          {error}
        </p>
      )}
      {!data && !error && <div className="mt-8 h-64 animate-pulse rounded-3xl bg-white/[0.03]" aria-busy="true" />}

      <ul className="mt-6 grid gap-3 md:grid-cols-2">
        {problems.map((problem) => (
          <li key={problem.slug}>
            <Link
              href={`/practice/${problem.slug}`}
              className="group flex h-full items-center gap-4 rounded-2xl bg-white/[0.02] p-4 ring-1 ring-white/[0.07] transition hover:bg-white/[0.04] hover:ring-indigo-400/30"
            >
              <span
                className={cn(
                  "grid h-10 w-10 shrink-0 place-items-center rounded-xl text-sm font-semibold ring-1",
                  problem.solved ? "bg-emerald-400/10 text-emerald-200 ring-emerald-300/25" : "bg-white/[0.03] text-slate-300 ring-white/[0.08]",
                )}
              >
                {problem.solved ? <CheckCircle2 className="h-5 w-5" aria-label="Solved" /> : problem.order}
              </span>
              <span className="min-w-0 flex-1">
                <span className="block truncate font-semibold text-white">{problem.title}</span>
                <span className="mt-1 flex flex-wrap items-center gap-1.5 text-xs">
                  <span className={cn("rounded-full px-2 py-0.5 ring-1", DIFFICULTY_TONE[problem.difficulty])}>{problem.difficulty}</span>
                  {problem.tags.map((tag) => (
                    <span key={tag} className="rounded-full bg-white/[0.04] px-2 py-0.5 text-slate-400">
                      {tag}
                    </span>
                  ))}
                  {problem.attempts > 0 && !problem.solved && <span className="text-slate-500">{problem.attempts} attempt(s)</span>}
                </span>
              </span>
              <ArrowRight className="h-4 w-4 shrink-0 text-slate-500 transition group-hover:translate-x-0.5 group-hover:text-indigo-300" aria-hidden="true" />
            </Link>
          </li>
        ))}
      </ul>
      {data && problems.length === 0 && <p className="mt-6 text-slate-400">Every problem in this list is solved. Nice work!</p>}
    </main>
  );
}

export default function PracticePage() {
  return (
    <ProtectedRoute>
      <PracticeList />
    </ProtectedRoute>
  );
}
