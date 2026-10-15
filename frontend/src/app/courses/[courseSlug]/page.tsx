"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { contentService, CourseDetail } from "@/services/contentService";
import {
  ArrowRight,
  BookOpen,
  Clock,
  Layers,
  AlertCircle,
  RefreshCw,
  ChevronRight,
} from "lucide-react";

export default function CourseDetailPage() {
  const params = useParams();
  const courseSlug = params.courseSlug as string;

  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadCourseData = async () => {
    if (!courseSlug) return;
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const data = await contentService.getCourse(courseSlug);
      setCourse(data);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to load course details.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadCourseData();
  }, [courseSlug]);

  return (
    <main className="flex-1 max-w-5xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-10 space-y-8 relative overflow-hidden">
      {/* Ambient Glow */}
        <div className="absolute top-1/6 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-indigo-600/10 blur-[150px] rounded-full pointer-events-none" />

        {/* Breadcrumb Navigation */}
        <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400 relative z-10">
          <Link href="/subjects" className="hover:text-indigo-400 transition-colors">
            Subjects
          </Link>
          <ChevronRight className="w-3.5 h-3.5 text-slate-600" />
          {course?.subject_slug ? (
            <Link
              href={`/subjects/${course.subject_slug}`}
              className="hover:text-indigo-400 transition-colors"
            >
              {course.subject_name || "Subject"}
            </Link>
          ) : (
            <span>Subject</span>
          )}
          <ChevronRight className="w-3.5 h-3.5 text-slate-600" />
          <span className="text-slate-300 font-semibold">{course?.title || courseSlug}</span>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="p-16 rounded-2xl bg-slate-900/40 border border-slate-800 flex flex-col items-center justify-center gap-4 text-center">
            <div className="w-10 h-10 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
            <p className="text-xs text-slate-400 font-mono animate-pulse">
              Loading course syllabus and topics...
            </p>
          </div>
        )}

        {/* Error State */}
        {!isLoading && errorMessage && (
          <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center justify-between gap-4 max-w-xl mx-auto">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={loadCourseData}
              className="px-3.5 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-white font-semibold flex items-center gap-1.5 transition-colors shrink-0"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Retry
            </button>
          </div>
        )}

        {/* Course Header Banner */}
        {!isLoading && course && (
          <div className="space-y-8 relative z-10">
            <div className="p-6 sm:p-8 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-2xl space-y-4">
              <div className="flex flex-wrap items-center gap-3 text-xs">
                <span className="px-3 py-1 rounded-full font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  Level: {course.difficulty}
                </span>
                <span className="text-slate-400 flex items-center gap-1.5">
                  <Clock className="w-4 h-4 text-indigo-400" />
                  Estimated: ~{course.estimated_hours} Hours
                </span>
                <span className="text-slate-400 flex items-center gap-1.5">
                  <Layers className="w-4 h-4 text-purple-400" />
                  {course.modules.length} Modules
                </span>
              </div>

              <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
                {course.title}
              </h1>

              <p className="text-sm sm:text-base text-slate-300 max-w-3xl leading-relaxed">
                {course.description || "In-depth structured curriculum designed for mastering core competencies."}
              </p>
            </div>

            {/* Modules & Topics Breakdown */}
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <BookOpen className="w-5 h-5 text-indigo-400" />
                  Course Modules & Units
                </h2>
                <span className="text-xs text-slate-500 font-mono">
                  {course.modules.reduce((acc, m) => acc + m.topics.length, 0)} Total Topics
                </span>
              </div>

              <div className="space-y-6">
                {course.modules.map((module, mIdx) => (
                  <div
                    key={module.id}
                    className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-4 shadow-lg"
                  >
                    {/* Module Title */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800/60">
                      <div className="flex items-center gap-3">
                        <span className="w-7 h-7 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-mono font-bold flex items-center justify-center shrink-0">
                          {String(mIdx + 1).padStart(2, "0")}
                        </span>
                        <div>
                          <h3 className="text-base font-bold text-white">
                            {module.title}
                          </h3>
                          {module.description && (
                            <p className="text-xs text-slate-400 mt-0.5">
                              {module.description}
                            </p>
                          )}
                        </div>
                      </div>
                      <span className="text-xs text-slate-500 font-mono flex items-center gap-1 self-start sm:self-auto">
                        <Clock className="w-3.5 h-3.5" />
                        ~{module.estimated_minutes} mins
                      </span>
                    </div>

                    {/* Topics List */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                      {module.topics.map((topic) => (
                        <Link
                          key={topic.id}
                          href={`/topics/${topic.id}`}
                          className="group p-4 rounded-xl bg-slate-950/60 hover:bg-slate-950 border border-slate-800/80 hover:border-indigo-500/40 transition-all flex items-center justify-between gap-3 shadow-sm"
                        >
                          <div className="space-y-1 min-w-0">
                            <h4 className="text-xs font-semibold text-slate-200 group-hover:text-indigo-300 transition-colors truncate">
                              {topic.title}
                            </h4>
                            <div className="flex items-center gap-2 text-[10px] text-slate-400">
                              <span>~{topic.estimated_minutes} mins</span>
                              <span>•</span>
                              <span>{topic.difficulty}</span>
                              {topic.lesson_count > 0 && (
                                <>
                                  <span>•</span>
                                  <span className="text-emerald-400 font-medium">
                                    {topic.lesson_count} {topic.lesson_count === 1 ? "Lesson" : "Lessons"}
                                  </span>
                                </>
                              )}
                            </div>
                          </div>

                          <div className="w-7 h-7 rounded-lg bg-slate-800 text-slate-400 group-hover:bg-indigo-600 group-hover:text-white flex items-center justify-center shrink-0 transition-colors">
                            <ArrowRight className="w-3.5 h-3.5" />
                          </div>
                        </Link>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
  );
}
