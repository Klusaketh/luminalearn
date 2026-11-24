"use client";

import { useEffect, useId, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Check, FileText, Loader2, Paperclip, X } from "lucide-react";
import { MAX_DOCUMENT_BYTES, tutorService } from "@/services/tutorService";
import { MAX_ACTIVE_DOCUMENTS, useTutorStore } from "@/stores/useTutorStore";
import { cn } from "@/utils/cn";

function isPdf(file: File): boolean {
  return file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");
}

/**
 * Attach PDFs (lecture notes, a textbook chapter, an assignment) and choose which ones the tutor
 * answers from. Answers cite the file and page they used.
 */
export function DocumentTray({ disabled = false }: { disabled?: boolean }) {
  const documents = useTutorStore((s) => s.documents);
  const activeIds = useTutorStore((s) => s.activeDocumentIds);
  const { setDocuments, addDocument, removeDocument, toggleDocument } = useTutorStore.getState();
  const inputRef = useRef<HTMLInputElement>(null);
  const statusId = useId();
  const [uploading, setUploading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    tutorService
      .listDocuments(controller.signal)
      .then(setDocuments)
      .catch(() => {}); // the tray still works for new uploads
    return () => controller.abort();
  }, [setDocuments]);

  const upload = async (file: File) => {
    setError(null);
    if (!isPdf(file)) {
      setError("Choose a PDF file.");
      return;
    }
    if (file.size > MAX_DOCUMENT_BYTES) {
      setError("That PDF is larger than 15 MB. Upload the chapter you need.");
      return;
    }
    setUploading(file.name);
    try {
      addDocument(await tutorService.uploadDocument(file));
    } catch (err) {
      setError(err instanceof Error ? err.message : "That PDF could not be uploaded.");
    } finally {
      setUploading(null);
      if (inputRef.current) inputRef.current.value = "";
    }
  };

  const remove = async (id: string) => {
    setError(null);
    try {
      await tutorService.deleteDocument(id);
      removeDocument(id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "That document could not be deleted.");
    }
  };

  const activeCount = activeIds.length;

  return (
    <div className="space-y-1.5">
      <div className="flex items-center gap-2 overflow-x-auto pb-0.5 [scrollbar-width:none]">
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          disabled={disabled || uploading !== null}
          aria-describedby={statusId}
          className="flex shrink-0 items-center gap-1.5 rounded-xl px-2.5 py-1.5 text-xs font-medium text-slate-200 ring-1 ring-white/10 transition-colors hover:bg-white/[0.06] hover:text-white disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-300"
        >
          {uploading ? <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden="true" /> : <Paperclip className="h-3.5 w-3.5" aria-hidden="true" />}
          {uploading ? "Reading PDF…" : "Attach PDF"}
        </button>
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf,.pdf"
          className="sr-only"
          tabIndex={-1}
          aria-hidden="true"
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) void upload(file);
          }}
        />
        <AnimatePresence initial={false}>
          {documents.map((doc) => {
            const active = activeIds.includes(doc.id);
            return (
              <motion.div
                key={doc.id}
                layout
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className={cn(
                  "flex shrink-0 items-center rounded-xl text-xs ring-1 transition-colors",
                  active ? "bg-cyan-400/10 text-cyan-50 ring-cyan-300/40" : "bg-white/[0.03] text-slate-400 ring-white/10"
                )}
              >
                <button
                  type="button"
                  role="switch"
                  aria-checked={active}
                  onClick={() => toggleDocument(doc.id)}
                  title={active ? "The tutor answers from this document. Click to stop." : "Click so the tutor answers from this document."}
                  className="flex max-w-[15rem] items-center gap-1.5 rounded-l-xl py-1.5 pl-2.5 pr-1.5 outline-none focus-visible:ring-2 focus-visible:ring-indigo-300"
                >
                  {active ? <Check className="h-3.5 w-3.5 shrink-0" aria-hidden="true" /> : <FileText className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />}
                  <span className="truncate">{doc.filename}</span>
                  <span className="shrink-0 text-[11px] opacity-70">· {doc.page_count} p.</span>
                </button>
                <button
                  type="button"
                  onClick={() => void remove(doc.id)}
                  aria-label={`Delete ${doc.filename}`}
                  className="rounded-r-xl py-1.5 pl-1 pr-2 opacity-70 outline-none hover:opacity-100 focus-visible:ring-2 focus-visible:ring-indigo-300"
                >
                  <X className="h-3.5 w-3.5" aria-hidden="true" />
                </button>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
      <p id={statusId} role={error ? "alert" : "status"} className={cn("px-1 text-[11px]", error ? "text-rose-300" : "text-slate-500")}>
        {error ??
          (activeCount > 0
            ? `Answering from ${activeCount === 1 ? "your document" : `${activeCount} documents`}; replies cite the page they used.`
            : documents.length > 0
              ? `Tap a document to ask about it (up to ${MAX_ACTIVE_DOCUMENTS} at once).`
              : "Attach lecture notes or a chapter (PDF with selectable text, up to 15 MB) and ask your doubts about it.")}
      </p>
    </div>
  );
}
