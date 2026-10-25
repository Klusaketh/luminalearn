import { BookMarked } from "lucide-react";
import type { Citation } from "@/services/tutorService";
import { cn } from "@/utils/cn";

/** Verified curriculum sources behind an answer (grounded RAG provenance). */
export function CitationList({ citations, highlighted, idPrefix }: { citations: Citation[]; highlighted?: number | null; idPrefix: string }) {
  if (citations.length === 0) return null;
  return (
    <section aria-label="Sources" className="mt-4 border-t border-white/[0.06] pt-3">
      <p className="mb-2 flex items-center gap-1.5 text-[11px] font-semibold text-slate-300">
        <BookMarked className="h-3.5 w-3.5 text-indigo-300" aria-hidden="true" />
        Sources from your curriculum
      </p>
      <ol className="space-y-1.5">
        {citations.map((citation) => (
          <li
            key={citation.index}
            id={`${idPrefix}-source-${citation.index}`}
            className={cn(
              "rounded-xl px-2.5 py-2 text-xs transition-colors duration-500",
              highlighted === citation.index ? "bg-indigo-500/15 ring-1 ring-indigo-400/40" : "bg-white/[0.02]"
            )}
          >
            <span className="tabular mr-2 font-semibold text-indigo-200">{citation.index}</span>
            <span className="text-slate-200">{citation.source}</span>
            <span className="text-slate-400">, {citation.section}</span>
            {citation.page ? <span className="text-slate-400">, p. {citation.page}</span> : null}
          </li>
        ))}
      </ol>
    </section>
  );
}
