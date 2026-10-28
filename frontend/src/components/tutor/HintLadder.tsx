"use client";

import { useId, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ChevronDown, Lock, Lightbulb } from "lucide-react";
import type { HintItem } from "@/services/tutorService";
import { MarkdownMessage } from "@/components/tutor/MarkdownMessage";
import { cn } from "@/utils/cn";

interface HintLadderProps {
  startTier: number;
  items: HintItem[];
  /** Called when the learner unlocks a rung above the starting tier (climbs the ladder). */
  onReveal?: (tier: number) => void;
}

const TIER_ACCENT = ["", "from-indigo-400/70 to-indigo-400/0", "from-cyan-400/70 to-cyan-400/0", "from-amber-400/70 to-amber-400/0"];

/**
 * Socratic hint ladder as a frosted accordion. Rungs up to the supervisor's starting tier
 * are open to read; higher rungs stay locked until the learner chooses to climb.
 */
export function HintLadder({ startTier, items, onReveal }: HintLadderProps) {
  const baseId = useId();
  const [unlocked, setUnlocked] = useState(Math.max(1, Math.min(3, startTier)));
  const [open, setOpen] = useState<number | null>(null);

  const toggle = (tier: number) => {
    if (tier > unlocked) {
      setUnlocked(tier);
      onReveal?.(tier);
    }
    setOpen((current) => (current === tier ? null : tier));
  };

  return (
    <div className="mt-4 overflow-hidden rounded-2xl border border-white/[0.07] bg-white/[0.02]">
      <div className="flex items-start gap-2 border-b border-white/[0.06] px-4 py-2.5">
        <Lightbulb className="mt-0.5 h-3.5 w-3.5 text-amber-300" aria-hidden="true" />
        <div>
          <p className="text-xs font-semibold text-slate-200">Hint ladder</p>
          <p className="text-[11px] text-slate-400">Open a rung only when you're stuck.</p>
        </div>
      </div>
      <ol>
        {items.map((hint) => {
          const locked = hint.tier > unlocked;
          const expanded = open === hint.tier;
          const panelId = `${baseId}-panel-${hint.tier}`;
          const headerId = `${baseId}-header-${hint.tier}`;
          return (
            <li key={hint.tier} className="relative border-b border-white/[0.05] last:border-b-0">
              <span aria-hidden="true" className={cn("absolute inset-y-0 left-0 w-0.5 bg-gradient-to-b", TIER_ACCENT[hint.tier])} />
              <button
                id={headerId}
                type="button"
                aria-expanded={expanded}
                aria-controls={panelId}
                onClick={() => toggle(hint.tier)}
                className="flex w-full items-center gap-3 px-4 py-3 text-left outline-none transition-colors hover:bg-white/[0.03] focus-visible:bg-white/[0.04] focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-indigo-300/70"
              >
                <span className="tabular flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-white/[0.06] text-[11px] font-semibold text-slate-200">{hint.tier}</span>
                <span className="flex-1 text-[13px] font-medium text-slate-100">
                  {hint.title}
                  {locked && <span className="ml-2 text-xs font-normal text-slate-400">Reveal when you're ready</span>}
                </span>
                {locked ? (
                  <Lock className="h-3.5 w-3.5 text-slate-500" aria-hidden="true" />
                ) : (
                  <motion.span animate={{ rotate: expanded ? 180 : 0 }} transition={{ type: "spring", stiffness: 400, damping: 30 }}>
                    <ChevronDown className="h-4 w-4 text-slate-400" aria-hidden="true" />
                  </motion.span>
                )}
              </button>
              <AnimatePresence initial={false}>
                {expanded && (
                  <motion.div
                    id={panelId}
                    role="region"
                    aria-labelledby={headerId}
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ type: "spring", stiffness: 300, damping: 32 }}
                    className="overflow-hidden"
                  >
                    <div className="px-4 pb-4 pl-[3.25rem] text-[14px]">
                      <MarkdownMessage text={hint.text} />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
