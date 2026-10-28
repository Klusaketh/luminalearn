"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { AlertTriangle, ArrowDownToLine, MessagesSquare } from "lucide-react";

interface MisconceptionCalloutProps {
  misconception: string;
  topic: string;
  question: string;
  chosenAnswer: string;
  onReviewExplanation: () => void;
}

/** Diagnosed misconception with a glowing warning border and two remediation paths. */
export function MisconceptionCallout({ misconception, topic, question, chosenAnswer, onReviewExplanation }: MisconceptionCalloutProps) {
  const tutorPrompt = `I answered "${chosenAnswer}" to this question: ${question}\nThe quiz said: ${misconception}\nHelp me find where my reasoning went wrong.`;
  const tutorHref = `/tutor?topic=${encodeURIComponent(topic)}&q=${encodeURIComponent(tutorPrompt.slice(0, 1800))}`;
  return (
    <motion.section
      role="status"
      aria-label="Likely misconception"
      initial={{ opacity: 0, y: 8, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: "spring", stiffness: 260, damping: 24 }}
      className="relative overflow-hidden rounded-3xl bg-amber-500/[0.06] p-5 shadow-glow-amber ring-1 ring-amber-400/35"
    >
      <motion.span
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 rounded-3xl ring-2 ring-amber-300/40"
        animate={{ opacity: [0.2, 0.75, 0.2] }}
        transition={{ duration: 2.6, repeat: Infinity, ease: "easeInOut" }}
      />
      <div className="relative flex items-start gap-3">
        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl bg-amber-400/15 text-amber-300">
          <AlertTriangle className="h-[18px] w-[18px]" aria-hidden="true" />
        </span>
        <div className="min-w-0 flex-1">
          <h3 className="text-sm font-semibold text-amber-100">Likely misconception</h3>
          <p className="mt-1 text-sm leading-relaxed text-amber-50/90">{misconception}</p>
          <div className="mt-4 flex flex-wrap gap-2">
            <Link
              href={tutorHref}
              className="inline-flex items-center gap-1.5 rounded-xl bg-amber-400/20 px-3 py-2 text-xs font-semibold text-amber-50 ring-1 ring-amber-300/40 transition-colors hover:bg-amber-400/30"
            >
              <MessagesSquare className="h-3.5 w-3.5" aria-hidden="true" /> Work through it with the tutor
            </Link>
            <button
              type="button"
              onClick={onReviewExplanation}
              className="inline-flex items-center gap-1.5 rounded-xl px-3 py-2 text-xs font-medium text-amber-100 ring-1 ring-amber-300/25 transition-colors hover:bg-amber-400/10"
            >
              <ArrowDownToLine className="h-3.5 w-3.5" aria-hidden="true" /> Review the derivation
            </button>
          </div>
        </div>
      </div>
    </motion.section>
  );
}
