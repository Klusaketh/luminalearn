"use client";

import { useId, useState } from "react";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import { BookOpenCheck, ChevronDown, Clock, FileText } from "lucide-react";
import type { SyllabusModule } from "@/services/contentService";
import { DifficultyBadge } from "./SubjectIcon";

function minutesLabel(minutes: number): string {
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.floor(minutes / 60);
  const rest = minutes % 60;
  return rest ? `${hours} h ${rest} min` : `${hours} h`;
}

function ModuleSection({ module, index, defaultOpen }: { module: SyllabusModule; index: number; defaultOpen: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  const panelId = useId();
  const lessons = module.topics.reduce((n, t) => n + t.lessons.length, 0);
  return (
    <li className="rounded-2xl border border-white/[0.07] bg-white/[0.015]">
      <h3>
        <button
          type="button"
          onClick={() => setOpen((o) => !o)}
          aria-expanded={open}
          aria-controls={panelId}
          className="flex w-full items-start gap-4 rounded-2xl p-4 text-left outline-none transition-colors hover:bg-white/[0.02] focus-visible:ring-2 focus-visible:ring-indigo-300 sm:p-5"
        >
          <span className="tabular mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-indigo-500/10 text-sm font-semibold text-indigo-200">
            {index + 1}
          </span>
          <span className="min-w-0 flex-1">
            <span className="block text-base font-semibold text-white">{module.title}</span>
            {module.description && <span className="mt-0.5 block text-sm leading-relaxed text-slate-400">{module.description}</span>}
            <span className="mt-1.5 block text-xs text-slate-500">
              {module.topics.length} {module.topics.length === 1 ? "topic" : "topics"} · {lessons} {lessons === 1 ? "lesson" : "lessons"} · {minutesLabel(module.estimated_minutes)}
            </span>
          </span>
          <ChevronDown className={`mt-1.5 h-5 w-5 shrink-0 text-slate-400 transition-transform ${open ? "rotate-180" : ""}`} aria-hidden="true" />
        </button>
      </h3>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            id={panelId}
            key="topics"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <ul className="space-y-1 px-3 pb-3 sm:px-4 sm:pb-4">
              {module.topics.map((topic) => {
                const lesson = topic.lessons[0];
                return (
                  <li key={topic.id}>
                    <Link
                      href={lesson ? `/lessons/${lesson.id}` : `/topics/${topic.id}`}
                      className="group flex items-start gap-3 rounded-xl px-3 py-2.5 outline-none transition-colors hover:bg-white/[0.04] focus-visible:ring-2 focus-visible:ring-indigo-300"
                    >
                      {lesson ? (
                        <BookOpenCheck className="mt-0.5 h-4 w-4 shrink-0 text-indigo-300" aria-hidden="true" />
                      ) : (
                        <FileText className="mt-0.5 h-4 w-4 shrink-0 text-slate-500" aria-hidden="true" />
                      )}
                      <span className="min-w-0 flex-1">
                        <span className="block text-[15px] font-medium text-slate-100 group-hover:text-white">{topic.title}</span>
                        {topic.summary && <span className="mt-0.5 block text-sm leading-relaxed text-slate-400">{topic.summary}</span>}
                      </span>
                      <span className="hidden shrink-0 items-center gap-2 sm:flex">
                        <DifficultyBadge level={topic.difficulty} />
                        <span className="tabular flex items-center gap-1 text-xs text-slate-500">
                          <Clock className="h-3.5 w-3.5" aria-hidden="true" />
                          {topic.estimated_minutes} min
                        </span>
                      </span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>
    </li>
  );
}

/** A course's modules as an accordion; each topic opens its lesson. */
export function SyllabusTree({ modules }: { modules: SyllabusModule[] }) {
  return (
    <ol className="space-y-3">
      {modules.map((module, index) => (
        <ModuleSection key={module.id} module={module} index={index} defaultOpen={index === 0} />
      ))}
    </ol>
  );
}
