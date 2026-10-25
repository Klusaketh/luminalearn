import { AlertOctagon, AlertTriangle, Gauge, Info } from "lucide-react";
import type { DiagnosticsInfo } from "@/services/tutorService";

const SEVERITY = {
  error: { icon: AlertOctagon, tone: "text-rose-300", ring: "ring-rose-400/25 bg-rose-500/[0.07]" },
  warning: { icon: AlertTriangle, tone: "text-amber-300", ring: "ring-amber-400/25 bg-amber-500/[0.07]" },
  info: { icon: Info, tone: "text-cyan-300", ring: "ring-cyan-400/20 bg-cyan-500/[0.06]" },
} as const;

/** Static-analysis findings and the Big-O estimate from the Code Diagnostic agent. */
export function DiagnosticsPanel({ diagnostics }: { diagnostics: DiagnosticsInfo }) {
  return (
    <section aria-label="Code diagnostics" className="mb-4 rounded-2xl border border-white/[0.07] bg-white/[0.02] p-3">
      <div className="mb-2 flex flex-wrap items-center gap-2 text-xs">
        <Gauge className="h-3.5 w-3.5 text-indigo-300" aria-hidden="true" />
        <span className="font-semibold text-slate-100">Static analysis</span>
        <span className="rounded-md bg-white/[0.06] px-1.5 py-0.5 font-mono text-[11px] text-slate-300">{diagnostics.language}</span>
        <span className="tabular ml-auto font-mono text-[11px] text-slate-300">
          time {diagnostics.time_complexity} · space {diagnostics.space_complexity}
        </span>
      </div>
      {diagnostics.findings.length === 0 ? (
        <p className="text-xs text-slate-400">No syntax errors or classic logic traps found.</p>
      ) : (
        <ul className="space-y-1.5">
          {diagnostics.findings.slice(0, 6).map((finding, index) => {
            const style = SEVERITY[finding.severity];
            const Icon = style.icon;
            return (
              <li key={`${finding.title}-${index}`} className={`flex items-start gap-2 rounded-xl px-2.5 py-2 text-xs ring-1 ${style.ring}`}>
                <Icon className={`mt-0.5 h-3.5 w-3.5 shrink-0 ${style.tone}`} aria-hidden="true" />
                <span className="text-slate-200">
                  {finding.line !== null && <span className="tabular mr-1.5 font-mono text-slate-400">L{finding.line}</span>}
                  <span className="font-semibold">{finding.title}</span>
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
