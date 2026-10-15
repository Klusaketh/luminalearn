"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  contentService,
  SubjectDetail,
  CourseDetail,
} from "@/services/contentService";
import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  Clock,
  Layers,
  GraduationCap,
  AlertCircle,
  RefreshCw,
  ChevronRight,
} from "lucide-react";

export default function SubjectDetailPage() {
  const params = useParams();
  const subjectSlug = params.subjectSlug as string;

  const [subject, setSubject] = useState<SubjectDetail | null>(null);
  const [courseDetails, setCourseDetails] = useState<Record<string, CourseDetail>>({});
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadSubjectData = async () => {
    if (!subjectSlug) return;
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const data = await contentService.getSubject(subjectSlug);
      setSubject(data);

      // Load full details for courses to show module outlines
      if (data.courses && data.courses.length > 0) {
        const detailsPromises = data.courses.map((c) =>
          contentService.getCourse(c.slug).catch(() => null)
        );
        const results = await Promise.all(detailsPromises);
        const map: Record<string, CourseDetail> = {};
        results.forEach((c) => {
          if (c) map[c.slug] = c;
        });
        setCourseDetails(map);
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to load subject details.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSubjectData();
  }, [subjectSlug]);

  return (
    <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-10 space-y-8 relative overflow-hidden">
      {/* Ambient Glow */}
        <div className="absolute top-1/6 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-indigo-600/10 blur-[150px] rounded-full pointer-events-none" />

        {/* Breadcrumb Navigation */}
        <div className="flex items-center gap-2 text-xs text-slate-400 relative z-10">
          <Link href="/subjects" className="hover:text-indigo-400 transition-colors flex items-center gap-1">
            <ArrowLeft className="w-3.5 h-3.5" />
            All Subjects
          </Link>
          <ChevronRight className="w-3.5 h-3.5 text-slate-600" />
          <span className="text-slate-300 font-semibold">{subject?.name || subjectSlug}</span>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="p-16 rounded-2xl bg-slate-900/40 border border-slate-800 flex flex-col items-center justify-center gap-4 text-center">
            <div className="w-10 h-10 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
            <p className="text-xs text-slate-400 font-mono animate-pulse">
              Loading syllabus and course structures...
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
              onClick={loadSubjectData}
              className="px-3.5 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-white font-semibold flex items-center gap-1.5 transition-colors shrink-0"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Retry
            </button>
          </div>
        )}

        {/* Subject Header Banner */}
        {!isLoading && subject && (
          <div className="space-y-8 relative z-10">
            <div className="p-6 sm:p-8 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-2xl space-y-4">
              <div className="flex flex-wrap items-center gap-2.5">
                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  {subject.category_name || "Academic Subject"}
                </span>
                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                  Difficulty: {subject.difficulty_level}
                </span>
              </div>

              <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
                {subject.name}
              </h1>

              <p className="text-sm sm:text-base text-slate-300 max-w-3xl leading-relaxed">
                {subject.description || subject.short_description}
              </p>
            </div>

            {/* Courses Section */}
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <GraduationCap className="w-5 h-5 text-indigo-400" />
                  Available Courses & Syllabus
                </h2>
                <span className="text-xs text-slate-500 font-mono">
                  {subject.courses.length} {subject.courses.length === 1 ? "Course" : "Courses"}
                </span>
              </div>

              {subject.courses.length === 0 ? (
                <div className="p-8 rounded-2xl bg-slate-900/40 border border-slate-800 text-center text-xs text-slate-400">
                  No courses currently authored for this subject.
                </div>
              ) : (
                <div className="space-y-6">
                  {subject.courses.map((course) => {
                    const detail = courseDetails[course.slug];
                    const modules = detail ? detail.modules : [];
                    const totalTopics = modules.reduce(
                      (acc, m) => acc + (m.topics ? m.topics.length : 0),
                      0
                    );

                    return (
                      <div
                        key={course.id}
                        className="rounded-2xl bg-slate-900/60 border border-slate-800/80 overflow-hidden shadow-lg space-y-6 p-6 sm:p-8"
                      >
                        {/* Course Card Header */}
                        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800/80">
                          <div className="space-y-2">
                            <div className="flex items-center gap-2 text-xs">
                              <span className="text-indigo-400 font-semibold uppercase tracking-wider">
                                Course Track
                              </span>
                              <span className="text-slate-600">•</span>
                              <span className="text-slate-400 flex items-center gap-1">
                                <Clock className="w-3.5 h-3.5" />
                                ~{course.estimated_hours} Hours
                              </span>
                              <span className="text-slate-600">•</span>
                              <span className="text-slate-400 flex items-center gap-1">
                                <Layers className="w-3.5 h-3.5" />
                                {modules.length} Modules ({totalTopics} Topics)
                              </span>
                            </div>
                            <h3 className="text-2xl font-bold text-white">
                              {course.title}
                            </h3>
                            <p className="text-xs sm:text-sm text-slate-400 max-w-2xl">
                              {course.description || "Structured learning module curriculum."}
                            </p>
                          </div>

                          <Link
                            href={`/courses/${course.slug}`}
                            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/30 transition-all flex items-center gap-2 shrink-0 group self-start md:self-auto"
                          >
                            Open Course
                            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                          </Link>
                        </div>

                        {/* Module Syllabus Breakdown */}
                        <div className="space-y-4">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                            <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
                            Curriculum Module Outline
                          </h4>

                          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                            {modules.map((mod, idx) => (
                              <div
                                key={mod.id}
                                className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-start gap-3"
                              >
                                <span className="w-6 h-6 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-mono font-bold flex items-center justify-center shrink-0">
                                  {String(idx + 1).padStart(2, "0")}
                                </span>
                                <div className="space-y-1 min-w-0">
                                  <h5 className="text-xs font-bold text-slate-200 truncate">
                                    {mod.title}
                                  </h5>
                                  <p className="text-[11px] text-slate-400">
                                    {mod.topics ? mod.topics.length : 0} Topics • ~{mod.estimated_minutes} mins
                                  </p>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        )}
      </main>
  );
}
