"use client";

import { memo, useState } from "react";
import { motion } from "framer-motion";
import { AlertCircle, Mic, Volume2, Lightbulb, StepForward, Square } from "lucide-react";
import type { TutorMessage } from "@/stores/useTutorStore";
import { useTypewriter } from "@/hooks/useTypewriter";
import { MarkdownMessage } from "@/components/tutor/MarkdownMessage";
import { AgentBadge } from "@/components/tutor/AgentBadge";
import { HintLadder } from "@/components/tutor/HintLadder";
import { CitationList } from "@/components/tutor/CitationList";
import dynamic from "next/dynamic";
import { DiagnosticsPanel } from "@/components/tutor/DiagnosticsPanel";

const KinestheticLab = dynamic(() => import("@/components/tutor/KinestheticLab").then((m) => m.KinestheticLab));

export interface MessageActions {
  onListen: (message: TutorMessage) => void;
  onStopListening: () => void;
  onAnalogy: (message: TutorMessage) => void;
  onNextHint: (message: TutorMessage) => void;
  onRevealHint: () => void;
  speakingId: string | null;
}

function ThinkingDots() {
  return (
    <span className="inline-flex items-center gap-1 py-2" aria-hidden="true">
      {[0, 1, 2].map((i) => (
        <motion.span
          key={i}
          className="h-1.5 w-1.5 rounded-full bg-indigo-300"
          animate={{ opacity: [0.25, 1, 0.25], y: [0, -3, 0] }}
          transition={{ duration: 1.1, repeat: Infinity, delay: i * 0.15 }}
        />
      ))}
    </span>
  );
}

function TutorCard({ message, actions }: { message: TutorMessage; actions: MessageActions }) {
  const streaming = message.status === "streaming";
  const shown = useTypewriter(message.text, streaming);
  const [highlight, setHighlight] = useState<number | null>(null);
  const done = message.status === "done" || message.status === "interrupted";
  const speaking = actions.speakingId === message.id;

  const onCite = (index: number) => {
    setHighlight(index);
    document.getElementById(`${message.id}-source-${index}`)?.scrollIntoView({ block: "nearest", behavior: "smooth" });
    window.setTimeout(() => setHighlight((current) => (current === index ? null : current)), 1800);
  };

  return (
    <motion.article
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 260, damping: 28 }}
      className="glass-strong max-w-[46rem] rounded-3xl rounded-tl-lg p-4 sm:p-5"
      aria-busy={streaming}
    >
      {message.route && <AgentBadge route={message.route} />}
      {message.diagnostics && <DiagnosticsPanel diagnostics={message.diagnostics} />}
      {message.text ? <MarkdownMessage text={shown} onCite={onCite} /> : streaming ? <ThinkingDots /> : null}
      {message.status === "error" && (
        <p className="mt-2 flex items-start gap-2 rounded-xl bg-rose-500/10 px-3 py-2 text-sm text-rose-200 ring-1 ring-rose-400/25">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
          {message.error}
        </p>
      )}
      {message.status === "interrupted" && (
        <p className="mt-2 inline-flex items-center gap-1.5 rounded-full bg-white/[0.05] px-2.5 py-1 text-[11px] text-slate-400">
          <Mic className="h-3 w-3" aria-hidden="true" /> You cut in, so the tutor stopped here.
        </p>
      )}
      {done && message.widget && <KinestheticLab widget={message.widget} />}
      {done && message.hints && message.hints.items.length > 0 && (
        <HintLadder startTier={message.hints.startTier} items={message.hints.items} onReveal={actions.onRevealHint} />
      )}
      {done && message.citations && <CitationList citations={message.citations} highlighted={highlight} idPrefix={message.id} />}
      {done && message.text && (
        <div className="mt-4 flex flex-wrap items-center gap-1.5">
          <button
            type="button"
            onClick={() => (speaking ? actions.onStopListening() : actions.onListen(message))}
            className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1.5 text-xs text-slate-300 ring-1 ring-white/10 transition-colors hover:bg-white/[0.05] hover:text-white"
            aria-pressed={speaking}
          >
            {speaking ? <Square className="h-3 w-3" aria-hidden="true" /> : <Volume2 className="h-3.5 w-3.5" aria-hidden="true" />}
            {speaking ? "Stop" : "Listen"}
          </button>
          {message.route?.agent === "socratic_tutor" && (
            <button
              type="button"
              onClick={() => actions.onNextHint(message)}
              className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1.5 text-xs text-slate-300 ring-1 ring-white/10 transition-colors hover:bg-white/[0.05] hover:text-white"
            >
              <StepForward className="h-3.5 w-3.5" aria-hidden="true" /> I'm still stuck
            </button>
          )}
          {message.route?.agent !== "analogy_specialist" && (
            <button
              type="button"
              onClick={() => actions.onAnalogy(message)}
              className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1.5 text-xs text-slate-300 ring-1 ring-white/10 transition-colors hover:bg-white/[0.05] hover:text-white"
            >
              <Lightbulb className="h-3.5 w-3.5" aria-hidden="true" /> Explain with an analogy
            </button>
          )}
          {message.engine && (
            <span className="ml-auto text-[11px] text-slate-500" title={message.latencyMs ? `${message.latencyMs} ms` : undefined}>
              {message.engine.startsWith("gemini") ? "Gemini" : "Offline engine"}
              {message.redactions ? `, ${message.redactions} answer leak held back` : ""}
            </span>
          )}
        </div>
      )}
    </motion.article>
  );
}

function StudentBubble({ message }: { message: TutorMessage }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: "spring", stiffness: 320, damping: 28 }}
      className="ml-auto max-w-[38rem] rounded-3xl rounded-tr-lg bg-[linear-gradient(135deg,rgba(124,58,237,0.42),rgba(8,145,178,0.28))] px-4 py-3 text-[15px] leading-7 text-white shadow-[0_0_0_1px_rgba(196,181,253,0.18)]"
    >
      {message.channel === "voice" && (
        <span className="mb-1 flex items-center gap-1 text-[11px] text-indigo-100/80">
          <Mic className="h-3 w-3" aria-hidden="true" /> Spoken
        </span>
      )}
      <p className="whitespace-pre-wrap break-words">{message.text}</p>
    </motion.div>
  );
}

export const MessageBubble = memo(function MessageBubble({ message, actions }: { message: TutorMessage; actions: MessageActions }) {
  return message.role === "student" ? <StudentBubble message={message} /> : <TutorCard message={message} actions={actions} />;
});
