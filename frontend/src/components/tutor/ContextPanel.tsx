"use client";

import { useEffect, useId, useState } from "react";
import Link from "next/link";
import { BrainCircuit, Radio, X } from "lucide-react";
import type { AgentName, TutorStatus } from "@/services/tutorService";
import { quizService } from "@/services/quizService";
import { AGENT_STYLE } from "@/components/tutor/agents";
import { MasteryGauge } from "@/components/quiz/MasteryGauge";
import { GlassPanel } from "@/components/ui/GlassPanel";
import { cn } from "@/utils/cn";

const AGENT_ORDER: AgentName[] = ["socratic_tutor", "concept_explainer", "analogy_specialist", "code_diagnostic"];
const FALLBACK_SUMMARIES: Record<AgentName, string> = {
  socratic_tutor: "Guides you to the answer with questions and a three-tier hint ladder.",
  concept_explainer: "Explains ideas as diagrams, narration, notes or hands-on labs.",
  analogy_specialist: "Maps abstract ideas onto everyday experience.",
  code_diagnostic: "Finds bugs and complexity hot-spots, then asks the leading question.",
};

interface ContextPanelProps {
  topic: string;
  onTopicChange: (topic: string) => void;
  activeAgent?: AgentName;
  status: TutorStatus | null;
  statusLoaded: boolean;
  onClose?: () => void;
}

export function ContextPanel({ topic, onTopicChange, activeAgent, status, statusLoaded, onClose }: ContextPanelProps) {
  const inputId = useId();
  const [draft, setDraft] = useState(topic);
  const [mastery, setMastery] = useState<number | null>(null);

  useEffect(() => setDraft(topic), [topic]);
  useEffect(() => {
    if (draft.trim() === topic.trim()) return;
    const timer = window.setTimeout(() => onTopicChange(draft.trim()), 500);
    return () => window.clearTimeout(timer);
  }, [draft, topic, onTopicChange]);

  useEffect(() => {
    if (!topic.trim()) {
      setMastery(null);
      return;
    }
    let cancelled = false;
    quizService
      .getMastery(topic.trim())
      .then((report) => !cancelled && setMastery(report.total_attempts > 0 ? report.current_mastery : null))
      .catch(() => !cancelled && setMastery(null));
    return () => {
      cancelled = true;
    };
  }, [topic]);

  const summaries = new Map(status?.agents.map((a) => [a.name, a.summary]));

  return (
    <GlassPanel as="aside" aria-label="Learning context" className="flex h-full min-h-0 flex-col gap-5 overflow-y-auto p-5">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-white">Your learning context</h2>
        {onClose && (
          <button type="button" onClick={onClose} aria-label="Close learning context" className="rounded-lg p-1.5 text-slate-400 hover:bg-white/[0.06] hover:text-white">
            <X className="h-4 w-4" aria-hidden="true" />
          </button>
        )}
      </div>

      <div>
        <label htmlFor={inputId} className="text-xs font-medium text-slate-300">
          Topic in focus
        </label>
        <input
          id={inputId}
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onBlur={() => onTopicChange(draft.trim())}
          maxLength={150}
          placeholder="e.g. Calculus, recursion, Bayes' theorem"
          className="mt-1.5 w-full rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-white outline-none placeholder:text-slate-500 focus:border-indigo-400/60 focus:ring-2 focus:ring-indigo-400/20"
        />
        <p className="mt-1.5 text-[11px] leading-relaxed text-slate-500">Grounds answers in your curriculum and sets how much scaffolding you get.</p>
      </div>

      <div className="flex flex-col items-center rounded-2xl border border-white/[0.06] bg-white/[0.02] p-4">
        {mastery !== null ? (
          <>
            <MasteryGauge value={mastery} size={150} label={`Mastery of ${topic}`} />
            <Link href={`/quiz?topic=${encodeURIComponent(topic)}`} className="mt-3 text-xs font-medium text-indigo-300 hover:text-indigo-200">
              Recalibrate with a quiz
            </Link>
          </>
        ) : (
          <div className="flex items-start gap-3 text-left">
            <BrainCircuit className="mt-0.5 h-4 w-4 shrink-0 text-indigo-300" aria-hidden="true" />
            <p className="text-xs leading-relaxed text-slate-300">
              No mastery data for this topic yet.{" "}
              <Link href={topic ? `/quiz?topic=${encodeURIComponent(topic)}` : "/quiz"} className="font-medium text-indigo-300 hover:text-indigo-200">
                Take a calibrated quiz
              </Link>{" "}
              so hints match your level.
            </p>
          </div>
        )}
      </div>

      <div>
        <h3 className="mb-2 text-xs font-semibold text-slate-200">The faculty</h3>
        <ul className="space-y-1.5">
          {AGENT_ORDER.map((name) => {
            const style = AGENT_STYLE[name];
            const Icon = style.icon;
            const active = name === activeAgent;
            return (
              <li
                key={name}
                className={cn(
                  "flex items-start gap-2.5 rounded-xl px-2.5 py-2 transition-colors duration-300",
                  active ? "bg-white/[0.06] ring-1 ring-white/10" : ""
                )}
              >
                <span className={cn("mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-lg ring-1", style.tone)}>
                  <Icon className="h-3.5 w-3.5" aria-hidden="true" />
                </span>
                <span className="min-w-0">
                  <span className="flex items-center gap-2 text-xs font-semibold text-slate-100">
                    {style.label}
                    {active && <span className="rounded-full bg-emerald-400/15 px-1.5 py-0.5 text-[10px] font-medium text-emerald-300">Answered last</span>}
                  </span>
                  <span className="block text-[11px] leading-snug text-slate-400">{summaries.get(name) ?? FALLBACK_SUMMARIES[name]}</span>
                </span>
              </li>
            );
          })}
        </ul>
      </div>

      <div className="mt-auto flex items-start gap-2 rounded-xl bg-white/[0.02] px-3 py-2.5 text-[11px] leading-relaxed text-slate-400">
        <Radio className={cn("mt-0.5 h-3.5 w-3.5 shrink-0", status?.llm_enabled ? "text-emerald-300" : "text-amber-300")} aria-hidden="true" />
        {!statusLoaded
          ? "Checking the tutor service."
          : status === null
            ? "The tutor service is offline. Start the backend to chat."
            : status.llm_enabled
              ? "Live answers from Gemini, with deterministic engines as a safety net."
              : "Running on the built-in Socratic engines (no Gemini key configured)."}
      </div>
    </GlassPanel>
  );
}
