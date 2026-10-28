"use client";

import React, { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { AlertCircle, ArrowLeft, ArrowRight, BookOpenCheck, ChevronRight, Clock, RefreshCw } from "lucide-react";
import { useOnReconnect } from "@/hooks/useOnReconnect";
import { contentService, type TopicDetail } from "@/services/contentService";
import { DifficultyBadge } from "@/components/subjects/SubjectIcon";

export default function TopicDetailPage() {
  const params = useParams();
  const topicId = params.topicId as string;
  const [topic, setTopic] = useState<TopicDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadTopicData = useCallback(async () => {
    if (!topicId) return;
    setIsLoading(true);
    setErrorMessage(null);
    try {
      setTopic(await contentService.getTopic(topicId));
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Failed to load topic details.");
    } finally {
      setIsLoading(false);
    }
  }, [topicId]);

  useEffect(() => {
    void loadTopicData();
  }, [loadTopicData]);

  // After a server outage, reload by itself if this page is showing a load error.
  useOnReconnect(() => {
    if (errorMessage) void loadTopicData();
  });

  const nav = topic?.navigation ?? null;
  const neighbourHref = (link: { lesson_id: string | null; topic_id: string }) => (link.lesson_id ? `/lessons/${link.lesson_id}` : `/topics/${link.topic_id}`);

  return (
    <main className="mx-auto w-full max-w-4xl flex-1 px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
      <nav aria-label="Breadcrumb" className="flex flex-wrap items-center gap-1.5 text-sm text-slate-400">
        <Link href="/subjects" className="hover:text-white">
          Subjects
        </Link>
        {topic?.subject_slug && (
          <>
            <ChevronRight className="h-3.5 w-3.5 text-slate-600" aria-hidden="true" />
            <Link href={`/subjects/${topic.subject_slug}`} className="hover:text-white">
              {topic.subject_name}
            </Link>
          </>
        )}
        {topic?.module_title && (
          <>
            <ChevronRight className="h-3.5 w-3.5 text-slate-600" aria-hidden="true" />
            <span>{topic.module_title}</span>
          </>
        )}
      </nav>

      {isLoading && (
        <div className="mt-8 space-y-4" role="status" aria-live="polite">
          <span className="sr-only">Loading topic</span>
          <div className="h-10 w-2/3 animate-pulse rounded-xl bg-white/[0.05]" />
          <div className="h-32 animate-pulse rounded-3xl bg-white/[0.03]" />
        </div>
      )}

      {!isLoading && errorMessage && (
        <div role="alert" className="mt-10 flex items-center justify-between gap-4 rounded-2xl border border-rose-400/30 bg-rose-500/10 p-5 text-sm text-rose-100">
          <span className="flex items-center gap-3">
            <AlertCircle className="h-5 w-5 shrink-0" aria-hidden="true" />
            {errorMessage}
          </span>
          <button type="button" onClick={() => void loadTopicData()} className="inline-flex shrink-0 items-center gap-1.5 rounded-lg bg-rose-500/20 px-3 py-1.5 font-semibold text-white hover:bg-rose-500/30">
            <RefreshCw className="h-4 w-4" aria-hidden="true" />
            Retry
          </button>
        </div>
      )}

      {!isLoading && topic && (
        <>
          <header className="mt-6">
            <div className="flex flex-wrap items-center gap-2.5 text-sm text-slate-400">
              <DifficultyBadge level={topic.difficulty} />
              <span className="inline-flex items-center gap-1.5">
                <Clock className="h-4 w-4" aria-hidden="true" />
                About {topic.estimated_minutes} minutes
              </span>
              {nav && (
                <span className="tabular">
                  Topic {nav.position} of {nav.total}
                </span>
              )}
            </div>
            <h1 className="mt-3 font-display text-4xl leading-tight text-white sm:text-5xl">{topic.title}</h1>
            {topic.summary && <p className="mt-3 text-lg leading-relaxed text-slate-300">{topic.summary}</p>}
          </header>

          <section aria-labelledby="lessons-heading" className="mt-10">
            <h2 id="lessons-heading" className="text-sm font-semibold text-slate-300">
              {topic.lessons.length === 1 ? "Lesson" : "Lessons"}
            </h2>
            {topic.lessons.length === 0 ? (
              <p className="mt-3 rounded-2xl border border-white/[0.08] p-5 text-slate-400">This topic does not have a published lesson yet.</p>
            ) : (
              <ul className="mt-3 space-y-3">
                {topic.lessons.map((lesson) => (
                  <li key={lesson.id}>
                    <Link
                      href={`/lessons/${lesson.id}`}
                      className="group flex items-start gap-4 rounded-2xl border border-white/[0.08] bg-white/[0.02] p-5 outline-none transition-colors hover:border-indigo-300/35 focus-visible:ring-2 focus-visible:ring-indigo-300"
                    >
                      <BookOpenCheck className="mt-0.5 h-5 w-5 shrink-0 text-indigo-300" aria-hidden="true" />
                      <span className="min-w-0 flex-1">
                        <span className="block text-lg font-semibold text-white">{lesson.title}</span>
                        {lesson.summary && <span className="mt-1 block leading-relaxed text-slate-400">{lesson.summary}</span>}
                        <span className="mt-2 block text-sm text-slate-500">About {lesson.estimated_minutes} minutes</span>
                      </span>
                      <ArrowRight className="mt-1 h-5 w-5 shrink-0 text-slate-400 transition-transform group-hover:translate-x-0.5 group-hover:text-white" aria-hidden="true" />
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </section>

          {nav && (nav.previous || nav.next) && (
            <nav aria-label="Topic navigation" className="mt-12 grid gap-3 border-t border-white/[0.08] pt-8 sm:grid-cols-2">
              {nav.previous ? (
                <Link href={neighbourHref(nav.previous)} className="group rounded-2xl border border-white/[0.08] p-4 outline-none hover:border-indigo-300/40 focus-visible:ring-2 focus-visible:ring-indigo-300">
                  <span className="flex items-center gap-1.5 text-xs text-slate-400">
                    <ArrowLeft className="h-3.5 w-3.5" aria-hidden="true" /> Previous · {nav.previous.module_title}
                  </span>
                  <span className="mt-1 block font-medium text-slate-100 group-hover:text-white">{nav.previous.title}</span>
                </Link>
              ) : (
                <span aria-hidden="true" />
              )}
              {nav.next && (
                <Link href={neighbourHref(nav.next)} className="group rounded-2xl border border-white/[0.08] p-4 text-right outline-none hover:border-indigo-300/40 focus-visible:ring-2 focus-visible:ring-indigo-300">
                  <span className="flex items-center justify-end gap-1.5 text-xs text-slate-400">
                    Next · {nav.next.module_title} <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
                  </span>
                  <span className="mt-1 block font-medium text-slate-100 group-hover:text-white">{nav.next.title}</span>
                </Link>
              )}
            </nav>
          )}
        </>
      )}
    </main>
  );
}
