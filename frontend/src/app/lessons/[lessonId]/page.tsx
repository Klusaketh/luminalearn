"use client";

import React, { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { AlertCircle, ArrowLeft, ArrowRight, ChevronRight, Clock, ListChecks, Lock, MailCheck, RefreshCw, Target } from "lucide-react";
import { useOnReconnect } from "@/hooks/useOnReconnect";
import { useAuthStore } from "@/stores/useAuthStore";
import { contentService, type LessonDetail } from "@/services/contentService";
import { LessonMarkdown } from "@/components/subjects/LessonMarkdown";
import { PracticeSet } from "@/components/subjects/PracticeSet";
import { LessonToc } from "@/components/subjects/LessonToc";
import { DifficultyBadge } from "@/components/subjects/SubjectIcon";
import { extractHeadings, splitLesson } from "@/components/subjects/lessonFormat";

type AccessState = "ok" | "unauthenticated" | "unverified";

function Breadcrumbs({ lesson }: { lesson: LessonDetail | null }) {
  return (
    <nav aria-label="Breadcrumb" className="flex flex-wrap items-center gap-1.5 text-sm text-slate-400">
      <Link href="/subjects" className="hover:text-white">
        Subjects
      </Link>
      {lesson?.subject_slug && (
        <>
          <ChevronRight className="h-3.5 w-3.5 text-slate-600" aria-hidden="true" />
          <Link href={`/subjects/${lesson.subject_slug}`} className="hover:text-white">
            {lesson.subject_name}
          </Link>
        </>
      )}
      {lesson?.module_title && (
        <>
          <ChevronRight className="h-3.5 w-3.5 text-slate-600" aria-hidden="true" />
          <span>{lesson.module_title}</span>
        </>
      )}
      {lesson?.topic_title && (
        <>
          <ChevronRight className="h-3.5 w-3.5 text-slate-600" aria-hidden="true" />
          <Link href={`/topics/${lesson.topic_id}`} className="text-slate-300 hover:text-white" aria-current="page">
            {lesson.topic_title}
          </Link>
        </>
      )}
    </nav>
  );
}

function AccessNotice({ state }: { state: Exclude<AccessState, "ok"> }) {
  const unverified = state === "unverified";
  return (
    <div className="glass mx-auto max-w-lg rounded-3xl p-8 text-center">
      <span className={`mx-auto flex h-12 w-12 items-center justify-center rounded-2xl ${unverified ? "bg-amber-400/10 text-amber-200" : "bg-indigo-500/10 text-indigo-200"}`}>
        {unverified ? <MailCheck className="h-6 w-6" aria-hidden="true" /> : <Lock className="h-6 w-6" aria-hidden="true" />}
      </span>
      <h1 className="mt-4 font-display text-3xl text-white">{unverified ? "Verify your email to read lessons" : "Sign in to read lessons"}</h1>
      <p className="mt-2 text-sm leading-relaxed text-slate-300">
        {unverified ? "Confirm the 6-digit code we emailed you, then come back to this lesson." : "Lessons are part of your LuminaLearn workspace."}
      </p>
      <Link
        href={unverified ? "/verify-email" : "/login"}
        className="mt-6 inline-flex rounded-xl bg-white px-5 py-2.5 text-sm font-semibold text-space-950 outline-none focus-visible:ring-2 focus-visible:ring-indigo-300"
      >
        {unverified ? "Verify email" : "Sign in"}
      </Link>
    </div>
  );
}

export default function LessonViewerPage() {
  const params = useParams();
  const lessonId = params.lessonId as string;
  const { user, accessToken, isAuthenticated } = useAuthStore();
  const [lesson, setLesson] = useState<LessonDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [accessState, setAccessState] = useState<AccessState>("ok");

  const loadLesson = useCallback(async () => {
    if (!lessonId) return;
    setIsLoading(true);
    setErrorMessage(null);
    setAccessState("ok");
    if (!isAuthenticated || !accessToken) {
      setIsLoading(false);
      setAccessState("unauthenticated");
      return;
    }
    if (user && user.is_verified === false) {
      setIsLoading(false);
      setAccessState("unverified");
      return;
    }
    try {
      setLesson(await contentService.getLesson(lessonId, accessToken));
    } catch (err) {
      const message = err instanceof Error ? err.message : "";
      if (message === "AUTHENTICATION_REQUIRED") setAccessState("unauthenticated");
      else if (message === "EMAIL_VERIFICATION_REQUIRED") setAccessState("unverified");
      else setErrorMessage(message || "Failed to load lesson content.");
    } finally {
      setIsLoading(false);
    }
  }, [lessonId, accessToken, isAuthenticated, user]);

  useEffect(() => {
    void loadLesson();
  }, [loadLesson]);

  // After a server outage, reload by itself if this page is showing a load error.
  useOnReconnect(() => {
    if (errorMessage) void loadLesson();
  });

  const blocks = useMemo(() => (lesson ? splitLesson(lesson.content) : []), [lesson]);
  const headings = useMemo(() => (lesson ? extractHeadings(lesson.content) : []), [lesson]);
  const nav = lesson?.navigation ?? null;

  useEffect(() => {
    if (lesson) document.title = `${lesson.title} · ${lesson.subject_name ?? "Subjects"} · LuminaLearn AI`;
  }, [lesson]);

  return (
    <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
      <Breadcrumbs lesson={lesson} />

      {isLoading && (
        <div className="mt-8 space-y-4" role="status" aria-live="polite">
          <span className="sr-only">Loading lesson</span>
          <div className="h-10 w-2/3 animate-pulse rounded-xl bg-white/[0.05]" />
          <div className="h-4 w-1/2 animate-pulse rounded bg-white/[0.04]" />
          <div className="mt-8 h-64 animate-pulse rounded-3xl bg-white/[0.03]" />
        </div>
      )}

      {!isLoading && accessState !== "ok" && (
        <div className="mt-10">
          <AccessNotice state={accessState} />
        </div>
      )}

      {!isLoading && accessState === "ok" && errorMessage && (
        <div role="alert" className="mx-auto mt-10 flex max-w-xl items-center justify-between gap-4 rounded-2xl border border-rose-400/30 bg-rose-500/10 p-5 text-sm text-rose-100">
          <span className="flex items-center gap-3">
            <AlertCircle className="h-5 w-5 shrink-0" aria-hidden="true" />
            {errorMessage}
          </span>
          <button
            type="button"
            onClick={() => void loadLesson()}
            className="inline-flex shrink-0 items-center gap-1.5 rounded-lg bg-rose-500/20 px-3 py-1.5 font-semibold text-white hover:bg-rose-500/30"
          >
            <RefreshCw className="h-4 w-4" aria-hidden="true" />
            Retry
          </button>
        </div>
      )}

      {!isLoading && accessState === "ok" && lesson && (
        <div className="mt-6 grid gap-10 lg:grid-cols-[minmax(0,1fr)_17rem]">
          <article className="min-w-0">
            <header className="max-w-3xl">
              <div className="flex flex-wrap items-center gap-2.5 text-sm text-slate-400">
                {lesson.topic_difficulty && <DifficultyBadge level={lesson.topic_difficulty} />}
                <span className="inline-flex items-center gap-1.5">
                  <Clock className="h-4 w-4" aria-hidden="true" />
                  About {lesson.estimated_minutes} minutes
                </span>
                {nav && (
                  <span className="tabular">
                    Lesson {nav.position} of {nav.total}
                  </span>
                )}
              </div>
              <h1 className="mt-3 font-display text-4xl leading-tight text-white sm:text-5xl">{lesson.title}</h1>
              {lesson.summary && <p className="mt-3 text-lg leading-relaxed text-slate-300">{lesson.summary}</p>}
            </header>

            {lesson.learning_objectives.length > 0 && (
              <section aria-labelledby="objectives-heading" className="mt-8 max-w-3xl rounded-2xl border border-indigo-400/20 bg-indigo-500/[0.06] p-5 sm:p-6">
                <h2 id="objectives-heading" className="flex items-center gap-2 text-sm font-semibold text-indigo-100">
                  <Target className="h-4 w-4" aria-hidden="true" />
                  By the end of this lesson you can
                </h2>
                <ul className="mt-3 space-y-2">
                  {lesson.learning_objectives.map((objective) => (
                    <li key={objective} className="flex gap-2.5 text-[15px] leading-relaxed text-slate-200">
                      <ListChecks className="mt-1 h-4 w-4 shrink-0 text-indigo-300" aria-hidden="true" />
                      {objective}
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {headings.length > 0 && (
              <details className="mt-6 max-w-3xl rounded-2xl border border-white/[0.08] p-4 lg:hidden">
                <summary className="cursor-pointer text-sm font-semibold text-slate-200">On this page</summary>
                <div className="mt-3">
                  <LessonToc headings={headings} />
                </div>
              </details>
            )}

            <div className="mt-10 max-w-3xl">
              {blocks.map((block, index) =>
                block.kind === "markdown" ? (
                  <LessonMarkdown key={index} markdown={block.text} />
                ) : (
                  <PracticeSet key={index} questions={block.questions} />
                )
              )}
            </div>

            {nav && (nav.previous || nav.next) && (
              <nav aria-label="Lesson navigation" className="mt-14 grid max-w-3xl gap-3 border-t border-white/[0.08] pt-8 sm:grid-cols-2">
                {nav.previous ? (
                  <Link
                    href={`/lessons/${nav.previous.lesson_id}`}
                    className="group rounded-2xl border border-white/[0.08] p-4 outline-none transition-colors hover:border-indigo-300/40 focus-visible:ring-2 focus-visible:ring-indigo-300"
                  >
                    <span className="flex items-center gap-1.5 text-xs text-slate-400">
                      <ArrowLeft className="h-3.5 w-3.5" aria-hidden="true" /> Previous · {nav.previous.module_title}
                    </span>
                    <span className="mt-1 block font-medium text-slate-100 group-hover:text-white">{nav.previous.topic_title}</span>
                  </Link>
                ) : (
                  <span aria-hidden="true" />
                )}
                {nav.next && (
                  <Link
                    href={`/lessons/${nav.next.lesson_id}`}
                    className="group rounded-2xl border border-white/[0.08] p-4 text-right outline-none transition-colors hover:border-indigo-300/40 focus-visible:ring-2 focus-visible:ring-indigo-300"
                  >
                    <span className="flex items-center justify-end gap-1.5 text-xs text-slate-400">
                      Next · {nav.next.module_title} <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
                    </span>
                    <span className="mt-1 block font-medium text-slate-100 group-hover:text-white">{nav.next.topic_title}</span>
                  </Link>
                )}
              </nav>
            )}
          </article>

          <aside className="hidden lg:block">
            <div className="sticky top-24 space-y-8">
              <LessonToc headings={headings} />
              {nav && nav.module_topics.length > 1 && (
                <nav aria-label={`Topics in ${lesson.module_title ?? "this module"}`} className="text-sm">
                  <p className="mb-2 text-xs font-semibold text-slate-400">In {lesson.module_title}</p>
                  <ul className="space-y-1">
                    {nav.module_topics.map((topic) => (
                      <li key={topic.topic_id}>
                        {topic.lesson_id && !topic.is_current ? (
                          <Link href={`/lessons/${topic.lesson_id}`} className="block rounded-lg px-2 py-1.5 text-slate-300 hover:bg-white/[0.04] hover:text-white">
                            {topic.title}
                          </Link>
                        ) : (
                          <span
                            aria-current={topic.is_current ? "page" : undefined}
                            className={`block rounded-lg px-2 py-1.5 ${topic.is_current ? "bg-indigo-500/10 font-medium text-white" : "text-slate-500"}`}
                          >
                            {topic.title}
                          </span>
                        )}
                      </li>
                    ))}
                  </ul>
                </nav>
              )}
            </div>
          </aside>
        </div>
      )}
    </main>
  );
}
