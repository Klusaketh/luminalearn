"use client";

import { useId, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ChevronDown, Eye, EyeOff } from "lucide-react";
import { LessonMarkdown } from "./LessonMarkdown";
import type { PracticeQuestion, QuestionLevel } from "./lessonFormat";

const LEVEL_STYLE: Record<QuestionLevel, string> = {
  basic: "bg-emerald-400/10 text-emerald-200 ring-emerald-300/20",
  intermediate: "bg-amber-400/10 text-amber-200 ring-amber-300/20",
  advanced: "bg-rose-400/10 text-rose-200 ring-rose-300/20",
};

function QuestionCard({ item, open, onToggle }: { item: PracticeQuestion; open: boolean; onToggle: () => void }) {
  const answerId = useId();
  return (
    <li className="rounded-2xl border border-white/[0.08] bg-white/[0.02] p-5 sm:p-6">
      <div className="flex items-start gap-3">
        <span className="tabular mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-indigo-500/15 text-xs font-semibold text-indigo-200">
          {item.number}
        </span>
        <div className="min-w-0 flex-1">
          {item.level && (
            <span className={`mb-2 inline-flex rounded-full px-2 py-0.5 text-[11px] font-medium capitalize ring-1 ${LEVEL_STYLE[item.level]}`}>
              {item.level}
            </span>
          )}
          <LessonMarkdown markdown={item.question} compact />
          <button
            type="button"
            onClick={onToggle}
            aria-expanded={open}
            aria-controls={answerId}
            className="mt-4 inline-flex items-center gap-1.5 rounded-xl border border-white/10 px-3 py-1.5 text-sm font-medium text-slate-200 outline-none transition-colors hover:border-indigo-300/40 hover:text-white focus-visible:ring-2 focus-visible:ring-indigo-300"
          >
            {open ? <EyeOff className="h-4 w-4" aria-hidden="true" /> : <Eye className="h-4 w-4" aria-hidden="true" />}
            {open ? "Hide answer" : "Show answer"}
            <ChevronDown className={`h-4 w-4 transition-transform ${open ? "rotate-180" : ""}`} aria-hidden="true" />
          </button>
          <AnimatePresence initial={false}>
            {open && (
              <motion.div
                id={answerId}
                key="answer"
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.22 }}
                className="overflow-hidden"
              >
                <div className="mt-4 rounded-xl border-l-2 border-emerald-300/50 bg-emerald-400/[0.04] px-4 py-3">
                  <p className="mb-1 text-xs font-semibold text-emerald-200">Answer and explanation</p>
                  <LessonMarkdown markdown={item.answer} compact />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </li>
  );
}

/** Self-study practice: try each question first, then reveal the worked answer. */
export function PracticeSet({ questions }: { questions: PracticeQuestion[] }) {
  const [open, setOpen] = useState<Set<number>>(new Set());
  const allOpen = open.size === questions.length;
  const toggle = (number: number) =>
    setOpen((current) => {
      const next = new Set(current);
      if (next.has(number)) next.delete(number);
      else next.add(number);
      return next;
    });

  return (
    <section aria-label="Practice questions" className="not-prose my-6">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm text-slate-400">Work each one out before opening the answer.</p>
        <button
          type="button"
          onClick={() => setOpen(allOpen ? new Set() : new Set(questions.map((q) => q.number)))}
          className="rounded-lg px-2 py-1 text-sm font-medium text-indigo-200 outline-none hover:text-white focus-visible:ring-2 focus-visible:ring-indigo-300"
        >
          {allOpen ? "Hide all answers" : "Show all answers"}
        </button>
      </div>
      <ol className="space-y-3">
        {questions.map((item) => (
          <QuestionCard key={item.number} item={item} open={open.has(item.number)} onToggle={() => toggle(item.number)} />
        ))}
      </ol>
    </section>
  );
}
