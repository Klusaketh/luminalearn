"use client";

import { useId, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Info } from "lucide-react";
import type { RouteInfo } from "@/services/tutorService";
import { AGENT_STYLE } from "@/components/tutor/agents";
import { cn } from "@/utils/cn";

/** Which specialist answered, with an explainable "why this tutor" disclosure. */
export function AgentBadge({ route }: { route: RouteInfo }) {
  const [open, setOpen] = useState(false);
  const panelId = useId();
  const style = AGENT_STYLE[route.agent];
  const Icon = style.icon;
  return (
    <div className="mb-3">
      <div className="flex flex-wrap items-center gap-2">
        <span className={cn("inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ring-1", style.tone)}>
          <Icon className="h-3.5 w-3.5" aria-hidden="true" />
          {route.display_name}
        </span>
        {route.agent === "socratic_tutor" && (
          <span className="tabular rounded-full bg-white/[0.05] px-2 py-1 text-[11px] text-slate-300">Hint tier {route.hint_tier} of 3</span>
        )}
        <button
          type="button"
          aria-expanded={open}
          aria-controls={panelId}
          onClick={() => setOpen((value) => !value)}
          className="inline-flex items-center gap-1 rounded-full px-2 py-1 text-[11px] text-slate-400 outline-none transition-colors hover:text-slate-100 focus-visible:ring-2 focus-visible:ring-indigo-300"
        >
          <Info className="h-3 w-3" aria-hidden="true" />
          Why this tutor?
        </button>
      </div>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            id={panelId}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ type: "spring", stiffness: 320, damping: 32 }}
            className="overflow-hidden"
          >
            <p className="mt-2 rounded-xl border border-white/[0.06] bg-white/[0.02] px-3 py-2 text-xs leading-relaxed text-slate-300">
              {route.rationale}{" "}
              <span className="tabular text-slate-400">Routing confidence {Math.round(route.confidence * 100)}%.</span>
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
