"use client";

import React from "react";
import { AlertTriangle, CheckCircle2, Clock3, XCircle } from "lucide-react";
import type { RunOutcome } from "@/hooks/useCodeRunner";
import { RUN_TIME_LIMIT_MS } from "@/hooks/useCodeRunner";
import { LANGUAGE_LABELS, type PracticeLanguage, type PracticeTestCase } from "@/services/practiceService";
import { callRepr, gotRepr, valueRepr } from "@/components/practice/format";
import { cn } from "@/utils/cn";

interface TestResultsProps {
  tests: PracticeTestCase[];
  functionName: string;
  language: PracticeLanguage;
  outcome: RunOutcome | null;
}

function Output({ label, text }: { label: string; text: string }) {
  return (
    <div className="mt-2">
      <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">{label}</p>
      <pre className="mt-1 max-h-32 overflow-auto whitespace-pre-wrap rounded-lg bg-black/30 px-3 py-2 font-mono text-[12.5px] text-slate-300">{text}</pre>
    </div>
  );
}

/** Per-test outcome of the last run, or the list of tests before any run. */
export function TestResults({ tests, functionName, language, outcome }: TestResultsProps) {
  if (outcome?.kind === "timeout") {
    return (
      <p role="status" className="flex items-start gap-2.5 rounded-2xl bg-amber-500/10 px-4 py-3 text-sm text-amber-100 ring-1 ring-amber-400/25">
        <Clock3 className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
        Your code ran for more than {RUN_TIME_LIMIT_MS / 1000} seconds and was stopped. Check for a loop that never ends.
      </p>
    );
  }
  if (outcome?.kind === "error") {
    return (
      <p role="alert" className="flex items-start gap-2.5 rounded-2xl bg-rose-500/10 px-4 py-3 text-sm text-rose-100 ring-1 ring-rose-400/25">
        <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
        The {LANGUAGE_LABELS[language]} runtime failed: {outcome.message}
      </p>
    );
  }

  const report = outcome?.kind === "report" ? outcome.report : null;
  if (report?.error) {
    return (
      <div role="alert" className="rounded-2xl bg-rose-500/10 px-4 py-3 text-sm text-rose-100 ring-1 ring-rose-400/25">
        <p className="flex items-start gap-2.5 font-medium">
          <XCircle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
          Your code could not run: {report.error}
        </p>
        {report.stdout && <Output label="Printed output" text={report.stdout} />}
      </div>
    );
  }

  const passed = report ? report.results.filter((r) => r.passed).length : 0;
  return (
    <div>
      {report && (
        <p
          role="status"
          className={cn(
            "mb-3 flex items-center gap-2 text-sm font-semibold",
            passed === tests.length ? "text-emerald-300" : "text-slate-200",
          )}
        >
          {passed === tests.length ? <CheckCircle2 className="h-4 w-4" aria-hidden="true" /> : null}
          {passed} of {tests.length} tests passed
        </p>
      )}
      <ol className="space-y-2">
        {tests.map((test, index) => {
          const result = report?.results[index];
          return (
            <li
              key={index}
              className={cn(
                "rounded-xl px-4 py-3 ring-1",
                !result && "bg-white/[0.02] ring-white/[0.07]",
                result?.passed && "bg-emerald-500/[0.06] ring-emerald-400/20",
                result && !result.passed && "bg-rose-500/[0.06] ring-rose-400/20",
              )}
            >
              <div className="flex items-start gap-2.5">
                {result ? (
                  result.passed ? (
                    <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-300" aria-label="Passed" />
                  ) : (
                    <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-rose-300" aria-label="Failed" />
                  )
                ) : (
                  <span className="mt-1 h-2.5 w-2.5 shrink-0 rounded-full bg-slate-600" aria-hidden="true" />
                )}
                <div className="min-w-0 flex-1 font-mono text-[13px]">
                  <p className="break-all text-slate-200">{callRepr(functionName, test.args, language)}</p>
                  <p className="mt-1 text-slate-400">
                    expected <span className="text-slate-200">{valueRepr(test.expected, language)}</span>
                    {result && !result.passed && !result.error && (
                      <>
                        {" · "}got <span className="text-rose-200">{gotRepr(result.got, language)}</span>
                      </>
                    )}
                  </p>
                  {result?.error && <p className="mt-1 text-rose-200">{result.error}</p>}
                  {result?.stdout && <Output label="Printed output" text={result.stdout} />}
                </div>
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
