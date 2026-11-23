"use client";

import React, { useCallback, useEffect, useState } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { ArrowLeft, BookOpen, CheckCircle2, Lightbulb, Loader2, Play, RotateCcw } from "lucide-react";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { GlassPanel } from "@/components/ui/GlassPanel";
import { LessonMarkdown } from "@/components/subjects/LessonMarkdown";
import { AskTutor } from "@/components/practice/AskTutor";
import { TestResults } from "@/components/practice/TestResults";
import { DIFFICULTY_TONE } from "@/components/practice/format";
import { usePythonRunner, type RunOutcome } from "@/hooks/usePythonRunner";
import { practiceService, type PracticeProblemDetail } from "@/services/practiceService";
import { celebrateMastery } from "@/utils/confetti";
import { cn } from "@/utils/cn";

const CodeEditor = dynamic(() => import("@/components/practice/CodeEditor"), {
  ssr: false,
  loading: () => <div className="h-[420px] animate-pulse rounded-2xl bg-white/[0.03]" aria-hidden="true" />,
});

const HINT_LABELS = ["Nudge", "Scaffold", "Parallel example"];

/** Drafts survive reloads in this browser only; storage can be unavailable (private mode), so it is optional. */
function draftKey(slug: string) {
  return `lumina.practice.${slug}`;
}
function readDraft(slug: string): string | null {
  try {
    return window.localStorage.getItem(draftKey(slug));
  } catch {
    return null;
  }
}
function writeDraft(slug: string, code: string | null) {
  try {
    if (code === null) window.localStorage.removeItem(draftKey(slug));
    else window.localStorage.setItem(draftKey(slug), code);
  } catch {
    // Drafts are a convenience; ignore storage failures.
  }
}

function Workspace({ slug }: { slug: string }) {
  const [problem, setProblem] = useState<PracticeProblemDetail | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [code, setCode] = useState("");
  const [outcome, setOutcome] = useState<RunOutcome | null>(null);
  const [hintsShown, setHintsShown] = useState(0);
  const [solved, setSolved] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const runner = usePythonRunner();

  useEffect(() => {
    const controller = new AbortController();
    practiceService
      .get(slug, controller.signal)
      .then((detail) => {
        setProblem(detail);
        setSolved(detail.solved);
        setCode(readDraft(slug) ?? detail.starter_code);
      })
      .catch((err: unknown) => {
        if (!controller.signal.aborted) setLoadError(err instanceof Error ? err.message : "Could not load this problem.");
      });
    return () => controller.abort();
  }, [slug]);

  const onChange = useCallback(
    (value: string) => {
      setCode(value);
      writeDraft(slug, value);
    },
    [slug],
  );

  const runTests = useCallback(async () => {
    if (!problem || runner.status === "running") return;
    const result = await runner.run({
      code,
      functionName: problem.function_name,
      tests: problem.tests,
      compare: problem.compare,
      harness: problem.harness,
    });
    setOutcome(result);
    if (result.kind !== "report" || result.report.error) return;

    const passed = result.report.results.filter((r) => r.passed).length;
    const total = problem.tests.length;
    if (passed === total && !solved) void celebrateMastery();
    try {
      const saved = await practiceService.submit(problem.slug, { code, passed, total });
      setSolved(saved.solved);
      setSaveError(null);
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : "Could not save your result.");
    }
  }, [code, problem, runner, solved]);

  if (loadError) {
    return (
      <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-12">
        <p role="alert" className="rounded-2xl bg-rose-500/10 px-4 py-3 text-rose-100 ring-1 ring-rose-400/25">
          {loadError}
        </p>
        <Link href="/practice" className="mt-4 inline-flex items-center gap-2 text-sm text-indigo-300 hover:text-indigo-200">
          <ArrowLeft className="h-4 w-4" aria-hidden="true" /> All problems
        </Link>
      </main>
    );
  }
  if (!problem) return <div className="mx-auto min-h-[60vh] w-full max-w-7xl animate-pulse px-4 py-12" aria-busy="true" />;

  const running = runner.status === "running";
  const runtimeNote =
    runner.status === "loading" ? "Starting Python in your browser…" : runner.status === "failed" ? "Python could not start in this browser." : "Python ready · Ctrl+Enter to run";

  return (
    <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6 sm:px-6 sm:py-10 lg:px-8">
      <Link href="/practice" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white">
        <ArrowLeft className="h-4 w-4" aria-hidden="true" /> All problems
      </Link>

      <div className="mt-4 grid gap-6 lg:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)]">
        <GlassPanel as="section" strong aria-labelledby="problem-title" className="h-fit p-6">
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className={cn("rounded-full px-2.5 py-1 ring-1", DIFFICULTY_TONE[problem.difficulty])}>{problem.difficulty}</span>
            {problem.tags.map((tag) => (
              <span key={tag} className="rounded-full bg-white/[0.04] px-2.5 py-1 text-slate-400">
                {tag}
              </span>
            ))}
            {solved && (
              <span className="inline-flex items-center gap-1 rounded-full bg-emerald-400/10 px-2.5 py-1 text-emerald-200 ring-1 ring-emerald-300/25">
                <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" /> Solved
              </span>
            )}
          </div>
          <h1 id="problem-title" className="mt-3 font-display text-3xl text-white sm:text-4xl">
            {problem.title}
          </h1>
          <LessonMarkdown markdown={problem.statement} compact className="mt-4" />

          {problem.related_topic && (
            <Link
              href={`/topics/${problem.related_topic.id}`}
              className="mt-5 flex items-center gap-2 rounded-xl bg-indigo-500/[0.08] px-4 py-3 text-sm text-indigo-100 ring-1 ring-indigo-400/20 hover:bg-indigo-500/[0.14]"
            >
              <BookOpen className="h-4 w-4 shrink-0" aria-hidden="true" />
              Review the lesson: {problem.related_topic.title}
            </Link>
          )}

          <section aria-labelledby="hints-heading" className="mt-6">
            <h2 id="hints-heading" className="flex items-center gap-2 text-sm font-semibold text-white">
              <Lightbulb className="h-4 w-4 text-amber-300" aria-hidden="true" /> Hint ladder
            </h2>
            <ol className="mt-3 space-y-2">
              {problem.hints.slice(0, hintsShown).map((hint, index) => (
                <li key={index} className="rounded-xl bg-amber-400/[0.05] px-4 py-3 ring-1 ring-amber-300/15">
                  <p className="text-[11px] font-semibold uppercase tracking-wider text-amber-200/80">
                    {index + 1}. {HINT_LABELS[index] ?? "Hint"}
                  </p>
                  <LessonMarkdown markdown={hint} compact className="mt-1" />
                </li>
              ))}
            </ol>
            {hintsShown < problem.hints.length ? (
              <button
                type="button"
                onClick={() => setHintsShown((n) => n + 1)}
                className="mt-3 rounded-xl bg-white/[0.04] px-3.5 py-2 text-sm text-slate-200 ring-1 ring-white/[0.08] hover:bg-white/[0.07]"
              >
                Show hint {hintsShown + 1} of {problem.hints.length}: {HINT_LABELS[hintsShown]}
              </button>
            ) : (
              <p className="mt-3 text-[13px] text-slate-500">All hints shown. Still stuck? Ask the tutor.</p>
            )}
          </section>
        </GlassPanel>

        <section aria-label="Code editor and tests" className="space-y-4">
          <CodeEditor value={code} onChange={onChange} onRun={() => void runTests()} label={`Python solution for ${problem.title}`} />

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={() => void runTests()}
              disabled={running || runner.status === "failed"}
              className="inline-flex items-center gap-2 rounded-xl bg-indigo-500 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 transition hover:bg-indigo-400 disabled:opacity-60"
            >
              {running || runner.status === "loading" ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <Play className="h-4 w-4" aria-hidden="true" />}
              {running ? "Running" : "Run tests"}
            </button>
            <button
              type="button"
              onClick={() => {
                setCode(problem.starter_code);
                writeDraft(slug, null);
                setOutcome(null);
              }}
              className="inline-flex items-center gap-2 rounded-xl bg-white/[0.04] px-4 py-2.5 text-sm text-slate-200 ring-1 ring-white/[0.08] hover:bg-white/[0.07]"
            >
              <RotateCcw className="h-4 w-4" aria-hidden="true" /> Reset code
            </button>
            <span className={cn("text-[13px]", runner.status === "failed" ? "text-rose-300" : "text-slate-500")}>{runtimeNote}</span>
          </div>
          {saveError && <p className="text-[13px] text-amber-200">Your result could not be saved: {saveError}</p>}

          <GlassPanel className="p-5">
            <h2 className="mb-3 text-sm font-semibold text-white">Tests</h2>
            <TestResults tests={problem.tests} functionName={problem.function_name} outcome={outcome} />
          </GlassPanel>

          <AskTutor problem={problem} code={code} outcome={outcome} />
        </section>
      </div>
    </main>
  );
}

export default function PracticeProblemPage({ params }: { params: { slug: string } }) {
  return (
    <ProtectedRoute>
      <Workspace slug={params.slug} />
    </ProtectedRoute>
  );
}
