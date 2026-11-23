"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import { Loader2, MessagesSquare } from "lucide-react";
import { AgentBadge } from "@/components/tutor/AgentBadge";
import { MarkdownMessage } from "@/components/tutor/MarkdownMessage";
import { callRepr, gotRepr, pyRepr } from "@/components/practice/format";
import type { RunOutcome } from "@/hooks/usePythonRunner";
import type { PracticeProblemDetail } from "@/services/practiceService";
import { tutorService, type RouteInfo } from "@/services/tutorService";

/** Describes what went wrong in the last run, in words the tutor (and the learner) can use. */
function describeOutcome(problem: PracticeProblemDetail, outcome: RunOutcome | null): string {
  if (!outcome) return "I have not run the tests yet.";
  if (outcome.kind === "timeout") return "When I run the tests, my code never finishes; it seems to loop forever.";
  if (outcome.kind === "error") return "The Python runtime failed to run my code.";
  const { report } = outcome;
  if (report.error) return `My code does not run. Python says: ${report.error}`;
  const failed = report.results.find((r) => !r.passed);
  if (!failed) return "All the tests pass. Can my solution be simpler or faster?";
  const test = problem.tests[failed.index];
  const call = callRepr(problem.function_name, test.args);
  return failed.error
    ? `This test raises an error: ${call} gives ${failed.error}`
    : `This test fails: ${call} should return ${pyRepr(test.expected)} but my code returns ${gotRepr(failed.got)}.`;
}

interface AskTutorProps {
  problem: PracticeProblemDetail;
  code: string;
  outcome: RunOutcome | null;
}

/** Sends the learner's code and the first failing test to the Socratic tutor, which guides without solving. */
export function AskTutor({ problem, code, outcome }: AskTutorProps) {
  const [reply, setReply] = useState("");
  const [route, setRoute] = useState<RouteInfo | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => () => abortRef.current?.abort(), []);

  const ask = useCallback(async () => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setBusy(true);
    setError(null);
    setReply("");
    setRoute(null);

    const message = [
      `I'm practising the coding problem "${problem.title}".`,
      describeOutcome(problem, outcome),
      "Here is my code:",
      "```python",
      code.trimEnd(),
      "```",
      "Please guide me towards the fix with a question or a hint. Don't give me the full solution.",
    ].join("\n");

    try {
      for await (const event of tutorService.streamChat(
        { message, topic: problem.related_topic?.title ?? problem.title },
        controller.signal,
      )) {
        if (event.type === "route") setRoute(event.data);
        else if (event.type === "delta") setReply((text) => text + event.data.text);
      }
    } catch (err) {
      if (!controller.signal.aborted) setError(err instanceof Error ? err.message : "The tutor could not answer.");
    } finally {
      if (abortRef.current === controller) setBusy(false);
    }
  }, [code, outcome, problem]);

  return (
    <section aria-labelledby="ask-tutor-heading" className="rounded-2xl bg-white/[0.02] p-4 ring-1 ring-white/[0.07]">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 id="ask-tutor-heading" className="text-sm font-semibold text-white">
          Stuck? Ask the tutor
        </h3>
        <button
          type="button"
          onClick={() => void ask()}
          disabled={busy}
          className="inline-flex items-center gap-2 rounded-xl bg-indigo-500/15 px-3.5 py-2 text-sm font-medium text-indigo-100 ring-1 ring-indigo-400/30 transition hover:bg-indigo-500/25 disabled:opacity-60"
        >
          {busy ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <MessagesSquare className="h-4 w-4" aria-hidden="true" />}
          {busy ? "Thinking" : reply ? "Ask again" : "Ask the tutor"}
        </button>
      </div>
      <p className="mt-1 text-[13px] text-slate-400">
        Sends your code and the first failing test. The tutor answers with a question or a hint, never the full solution.
      </p>
      {error && (
        <p role="alert" className="mt-3 text-sm text-rose-200">
          {error}
        </p>
      )}
      {(route || reply) && (
        <div className="mt-4 space-y-3" aria-live="polite">
          {route && <AgentBadge route={route} />}
          {reply && (
            <div className="text-[15px] leading-relaxed text-slate-200">
              <MarkdownMessage text={reply} />
            </div>
          )}
        </div>
      )}
    </section>
  );
}
