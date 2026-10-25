"use client";

import React, { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { AlertCircle, ArrowRight, BookMarked, CheckCircle2, ChevronRight, Clock, GraduationCap, Layers, Library, ListTree, RefreshCw } from "lucide-react";
import { useOnReconnect } from "@/hooks/useOnReconnect";
import { contentService, type SubjectSyllabus } from "@/services/contentService";
import { SyllabusTree } from "@/components/subjects/SyllabusTree";
import { DifficultyBadge, SubjectIcon } from "@/components/subjects/SubjectIcon";
import { LessonMarkdown } from "@/components/subjects/LessonMarkdown";
import { glossaryEntries, listItems, overviewSections } from "@/components/subjects/lessonFormat";

function Stat({ icon: Icon, value, label }: { icon: typeof Layers; value: string | number; label: string }) {
  return (
    <div className="flex items-center gap-2.5">
      <Icon className="h-4 w-4 text-indigo-300" aria-hidden="true" />
      <span className="tabular text-sm text-slate-300">
        <span className="font-semibold text-white">{value}</span> {label}
      </span>
    </div>
  );
}

function SidePanel({ title, icon: Icon, children }: { title: string; icon: typeof Layers; children: React.ReactNode }) {
  return (
    <section className="rounded-2xl border border-white/[0.08] bg-white/[0.02] p-5">
      <h2 className="flex items-center gap-2 text-sm font-semibold text-white">
        <Icon className="h-4 w-4 text-indigo-300" aria-hidden="true" />
        {title}
      </h2>
      <div className="mt-3">{children}</div>
    </section>
  );
}

export default function SubjectDetailPage() {
  const params = useParams();
  const subjectSlug = params.subjectSlug as string;
  const [subject, setSubject] = useState<SubjectSyllabus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadSubjectData = useCallback(async () => {
    if (!subjectSlug) return;
    setIsLoading(true);
    setErrorMessage(null);
    try {
      setSubject(await contentService.getSyllabus(subjectSlug));
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Failed to load subject details.");
    } finally {
      setIsLoading(false);
    }
  }, [subjectSlug]);

  useEffect(() => {
    void loadSubjectData();
  }, [loadSubjectData]);

  // After a server outage, reload by itself if this page is showing a load error.
  useOnReconnect(() => {
    if (errorMessage) void loadSubjectData();
  });

  useEffect(() => {
    if (subject) document.title = `${subject.name} · Subjects · LuminaLearn AI`;
  }, [subject]);

  const overview = useMemo(() => overviewSections(subject?.description ?? ""), [subject]);
  const objectives = listItems(overview.sections["What you will learn"] ?? "");
  const prerequisites = listItems(overview.sections["Prerequisites"] ?? "");
  const glossary = glossaryEntries(overview.sections["Glossary"] ?? "");
  const reading = overview.sections["Further reading"];
  const firstLesson = subject?.courses.flatMap((c) => c.modules.flatMap((m) => m.topics.flatMap((t) => t.lessons)))[0];

  return (
    <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
      <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-sm text-slate-400">
        <Link href="/subjects" className="hover:text-white">
          Subjects
        </Link>
        <ChevronRight className="h-3.5 w-3.5 text-slate-600" aria-hidden="true" />
        <span className="text-slate-300" aria-current="page">
          {subject?.name ?? "Subject"}
        </span>
      </nav>

      {isLoading && (
        <div className="mt-8 space-y-4" role="status" aria-live="polite">
          <span className="sr-only">Loading subject</span>
          <div className="h-12 w-1/2 animate-pulse rounded-xl bg-white/[0.05]" />
          <div className="h-4 w-2/3 animate-pulse rounded bg-white/[0.04]" />
          <div className="mt-8 grid gap-6 lg:grid-cols-[minmax(0,1fr)_20rem]">
            <div className="h-80 animate-pulse rounded-3xl bg-white/[0.03]" />
            <div className="h-80 animate-pulse rounded-3xl bg-white/[0.03]" />
          </div>
        </div>
      )}

      {!isLoading && errorMessage && (
        <div role="alert" className="mx-auto mt-10 flex max-w-xl items-center justify-between gap-4 rounded-2xl border border-rose-400/30 bg-rose-500/10 p-5 text-sm text-rose-100">
          <span className="flex items-center gap-3">
            <AlertCircle className="h-5 w-5 shrink-0" aria-hidden="true" />
            {errorMessage}
          </span>
          <button
            type="button"
            onClick={() => void loadSubjectData()}
            className="inline-flex shrink-0 items-center gap-1.5 rounded-lg bg-rose-500/20 px-3 py-1.5 font-semibold text-white hover:bg-rose-500/30"
          >
            <RefreshCw className="h-4 w-4" aria-hidden="true" />
            Retry
          </button>
        </div>
      )}

      {!isLoading && subject && (
        <>
          <header className="mt-6 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl">
              <div className="flex flex-wrap items-center gap-2.5">
                <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-indigo-500/10 text-indigo-200">
                  <SubjectIcon iconKey={subject.icon_key} />
                </span>
                {subject.category_name && <span className="text-sm text-slate-400">{subject.category_name}</span>}
                <DifficultyBadge level={subject.difficulty_level} />
              </div>
              <h1 className="mt-4 font-display text-4xl leading-tight text-white sm:text-6xl">{subject.name}</h1>
              {subject.short_description && <p className="mt-3 text-lg leading-relaxed text-slate-300">{subject.short_description}</p>}
              <div className="mt-5 flex flex-wrap gap-x-6 gap-y-2">
                <Stat icon={Layers} value={subject.module_count} label="modules" />
                <Stat icon={ListTree} value={subject.topic_count} label="topics" />
                <Stat icon={BookMarked} value={subject.lesson_count} label="lessons" />
                <Stat icon={Clock} value={`~${subject.estimated_hours}`} label="hours" />
              </div>
            </div>
            <div className="flex flex-wrap gap-3">
              {firstLesson && (
                <Link
                  href={`/lessons/${firstLesson.id}`}
                  className="inline-flex items-center gap-2 rounded-xl bg-white px-5 py-3 text-sm font-semibold text-space-950 outline-none transition-transform hover:-translate-y-px focus-visible:ring-2 focus-visible:ring-indigo-300"
                >
                  Start with the first lesson <ArrowRight className="h-4 w-4" aria-hidden="true" />
                </Link>
              )}
              <a href="#syllabus" className="inline-flex items-center rounded-xl border border-white/15 px-5 py-3 text-sm font-semibold text-slate-100 outline-none hover:border-white/30 focus-visible:ring-2 focus-visible:ring-indigo-300">
                View syllabus
              </a>
            </div>
          </header>

          <div className="mt-10 grid gap-10 lg:grid-cols-[minmax(0,1fr)_20rem]">
            <div className="min-w-0 space-y-12">
              {overview.intro && (
                <section aria-labelledby="overview-heading" className="max-w-3xl">
                  <h2 id="overview-heading" className="font-display text-3xl text-white">
                    About this subject
                  </h2>
                  <LessonMarkdown markdown={overview.intro} className="mt-4" />
                </section>
              )}

              <section id="syllabus" aria-labelledby="syllabus-heading" className="scroll-mt-24">
                <h2 id="syllabus-heading" className="font-display text-3xl text-white">
                  Syllabus
                </h2>
                {subject.courses.length === 0 ? (
                  <p className="mt-4 text-slate-400">No course has been published for this subject yet.</p>
                ) : (
                  subject.courses.map((course) => (
                    <div key={course.id} className="mt-5">
                      <div className="mb-4 flex flex-wrap items-baseline justify-between gap-2">
                        <h3 className="text-lg font-semibold text-white">{course.title}</h3>
                        <span className="text-sm text-slate-400">
                          {course.difficulty} · ~{course.estimated_hours} hours
                        </span>
                      </div>
                      {course.description && <p className="-mt-2 mb-4 max-w-3xl text-[15px] leading-relaxed text-slate-400">{course.description}</p>}
                      <SyllabusTree modules={course.modules} />
                    </div>
                  ))
                )}
              </section>

              {glossary.length > 0 && (
                <section aria-labelledby="glossary-heading">
                  <h2 id="glossary-heading" className="font-display text-3xl text-white">
                    Glossary
                  </h2>
                  <dl className="mt-5 grid gap-3 sm:grid-cols-2">
                    {glossary.map((entry) => (
                      <div key={entry.term} className="rounded-2xl border border-white/[0.07] bg-white/[0.015] p-4">
                        <dt className="font-semibold text-white">{entry.term}</dt>
                        <dd className="mt-1 text-[15px] leading-relaxed text-slate-300">{entry.definition}</dd>
                      </div>
                    ))}
                  </dl>
                </section>
              )}
            </div>

            <aside className="space-y-4 lg:sticky lg:top-24 lg:self-start">
              {objectives.length > 0 && (
                <SidePanel title="What you will learn" icon={GraduationCap}>
                  <ul className="space-y-2.5">
                    {objectives.map((item) => (
                      <li key={item} className="flex gap-2.5 text-sm leading-relaxed text-slate-300">
                        <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-300" aria-hidden="true" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </SidePanel>
              )}
              {prerequisites.length > 0 && (
                <SidePanel title="Before you start" icon={ListTree}>
                  <ul className="list-disc space-y-1.5 pl-5 text-sm leading-relaxed text-slate-300 marker:text-indigo-300">
                    {prerequisites.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </SidePanel>
              )}
              {reading && (
                <SidePanel title="Further reading" icon={Library}>
                  <LessonMarkdown markdown={reading} compact />
                </SidePanel>
              )}
            </aside>
          </div>
        </>
      )}
    </main>
  );
}
