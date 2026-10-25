"use client";

import React, { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { AlertCircle, ChevronRight, RefreshCw } from "lucide-react";
import { useOnReconnect } from "@/hooks/useOnReconnect";
import { contentService, type SubjectSyllabus, type SyllabusCourse } from "@/services/contentService";
import { SyllabusTree } from "@/components/subjects/SyllabusTree";
import { DifficultyBadge } from "@/components/subjects/SubjectIcon";

export default function CourseDetailPage() {
  const params = useParams();
  const courseSlug = params.courseSlug as string;
  const [subject, setSubject] = useState<SubjectSyllabus | null>(null);
  const [course, setCourse] = useState<SyllabusCourse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadCourseData = useCallback(async () => {
    if (!courseSlug) return;
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const detail = await contentService.getCourse(courseSlug);
      if (!detail.subject_slug) throw new Error("This course is not linked to a subject.");
      const syllabus = await contentService.getSyllabus(detail.subject_slug);
      setSubject(syllabus);
      setCourse(syllabus.courses.find((c) => c.slug === courseSlug) ?? null);
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Failed to load course details.");
    } finally {
      setIsLoading(false);
    }
  }, [courseSlug]);

  useEffect(() => {
    void loadCourseData();
  }, [loadCourseData]);

  // After a server outage, reload by itself if this page is showing a load error.
  useOnReconnect(() => {
    if (errorMessage) void loadCourseData();
  });

  const topicCount = course?.modules.reduce((n, m) => n + m.topics.length, 0) ?? 0;

  return (
    <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
      <nav aria-label="Breadcrumb" className="flex flex-wrap items-center gap-1.5 text-sm text-slate-400">
        <Link href="/subjects" className="hover:text-white">
          Subjects
        </Link>
        {subject && (
          <>
            <ChevronRight className="h-3.5 w-3.5 text-slate-600" aria-hidden="true" />
            <Link href={`/subjects/${subject.slug}`} className="hover:text-white">
              {subject.name}
            </Link>
          </>
        )}
        <ChevronRight className="h-3.5 w-3.5 text-slate-600" aria-hidden="true" />
        <span className="text-slate-300" aria-current="page">
          {course?.title ?? "Course"}
        </span>
      </nav>

      {isLoading && (
        <div className="mt-8 space-y-4" role="status" aria-live="polite">
          <span className="sr-only">Loading course</span>
          <div className="h-10 w-2/3 animate-pulse rounded-xl bg-white/[0.05]" />
          <div className="h-72 animate-pulse rounded-3xl bg-white/[0.03]" />
        </div>
      )}

      {!isLoading && errorMessage && (
        <div role="alert" className="mt-10 flex items-center justify-between gap-4 rounded-2xl border border-rose-400/30 bg-rose-500/10 p-5 text-sm text-rose-100">
          <span className="flex items-center gap-3">
            <AlertCircle className="h-5 w-5 shrink-0" aria-hidden="true" />
            {errorMessage}
          </span>
          <button type="button" onClick={() => void loadCourseData()} className="inline-flex shrink-0 items-center gap-1.5 rounded-lg bg-rose-500/20 px-3 py-1.5 font-semibold text-white hover:bg-rose-500/30">
            <RefreshCw className="h-4 w-4" aria-hidden="true" />
            Retry
          </button>
        </div>
      )}

      {!isLoading && !errorMessage && course && (
        <>
          <header className="mt-6">
            <div className="flex flex-wrap items-center gap-2.5 text-sm text-slate-400">
              <DifficultyBadge level={course.difficulty} />
              <span className="tabular">
                {course.modules.length} modules · {topicCount} topics · ~{course.estimated_hours} hours
              </span>
            </div>
            <h1 className="mt-3 font-display text-4xl leading-tight text-white sm:text-5xl">{course.title}</h1>
            {course.description && <p className="mt-3 max-w-3xl text-lg leading-relaxed text-slate-300">{course.description}</p>}
          </header>
          <section aria-label="Course syllabus" className="mt-10">
            <SyllabusTree modules={course.modules} />
          </section>
        </>
      )}
    </main>
  );
}
