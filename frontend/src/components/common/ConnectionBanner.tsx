"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, Loader2 } from "lucide-react";
import { API_BASE, apiFetch, onReachabilityChange } from "@/services/apiClient";

const FIRST_RETRY_MS = 2000;
const MAX_RETRY_MS = 10000;

/**
 * Appears while the LuminaLearn server is unreachable and probes it with growing intervals.
 * The first successful probe marks the server reachable again, which wakes every page and
 * session check waiting on it (see useOnReconnect).
 */
export function ConnectionBanner() {
  const [status, setStatus] = useState<"online" | "offline" | "restored">("online");

  useEffect(
    () =>
      onReachabilityChange((reachable) => {
        setStatus(reachable ? "restored" : "offline");
      }),
    []
  );

  useEffect(() => {
    if (status === "restored") {
      const timer = window.setTimeout(() => setStatus("online"), 2500);
      return () => window.clearTimeout(timer);
    }
    if (status !== "offline") return;
    let cancelled = false;
    let delay = FIRST_RETRY_MS;
    let timer = 0;
    const probe = async () => {
      try {
        await apiFetch(`${API_BASE}/health`, { auth: false, timeoutMs: 4000 }); // marks the server reachable
      } catch {
        if (cancelled) return;
        delay = Math.min(delay * 1.5, MAX_RETRY_MS);
        timer = window.setTimeout(probe, delay);
      }
    };
    timer = window.setTimeout(probe, delay);
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [status]);

  return (
    <div aria-live="polite" className="pointer-events-none fixed inset-x-0 top-[4.5rem] z-[60] flex justify-center px-4">
      <AnimatePresence>
        {status !== "online" && (
          <motion.div
            key={status}
            initial={{ opacity: 0, y: -8, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ type: "spring", stiffness: 380, damping: 30 }}
            className="glass-strong pointer-events-auto flex items-center gap-2.5 rounded-full px-4 py-2 text-sm shadow-glass"
          >
            {status === "offline" ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin text-amber-200" aria-hidden="true" />
                <span className="text-slate-100">Reconnecting to the LuminaLearn server…</span>
              </>
            ) : (
              <>
                <CheckCircle2 className="h-4 w-4 text-emerald-300" aria-hidden="true" />
                <span className="text-slate-100">Back online</span>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
