"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useAuthStore } from "@/stores/useAuthStore";
import { contentService, LessonDetail } from "@/services/contentService";
import {
  ArrowLeft,
  Clock,
  AlertCircle,
  RefreshCw,
  ChevronRight,
  Target,
  Lock,
  MailCheck,
} from "lucide-react";

export default function LessonViewerPage() {
  const params = useParams();
  const lessonId = params.lessonId as string;
  const { user, accessToken, isAuthenticated } = useAuthStore();

  const [lesson, setLesson] = useState<LessonDetail | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [accessState, setAccessState] = useState<"ok" | "unauthenticated" | "unverified">("ok");

  const loadLesson = async () => {
    if (!lessonId) return;
    setIsLoading(true);
    setErrorMessage(null);
    setAccessState("ok");

    if (!isAuthenticated || !accessToken) {
      setIsLoading(false);
      setAccessState("unauthenticated");
      return;
    }

    if (user && !user.is_verified) {
      setIsLoading(false);
      setAccessState("unverified");
      return;
    }

    try {
      const data = await contentService.getLesson(lessonId, accessToken);
      setLesson(data);
    } catch (err: any) {
      if (err.message === "AUTHENTICATION_REQUIRED") {
        setAccessState("unauthenticated");
      } else if (err.message === "EMAIL_VERIFICATION_REQUIRED") {
        setAccessState("unverified");
      } else {
        setErrorMessage(err.message || "Failed to load lesson content.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadLesson();
  }, [lessonId, accessToken, isAuthenticated, user]);

  return (
    <main className="flex-1 max-w-4xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-10 space-y-8 relative overflow-hidden">
      {/* Ambient Glow */}
        <div className="absolute top-1/6 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-indigo-600/10 blur-[150px] rounded-full pointer-events-none" />

        {/* Breadcrumb Navigation */}
        <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400 relative z-10">
          <Link href="/subjects" className="hover:text-indigo-400 transition-colors">
            Subjects
          </Link>
          <ChevronRight className="w-3.5 h-3.5 text-slate-600" />
          {lesson?.subject_slug ? (
            <Link
              href={`/subjects/${lesson.subject_slug}`}
              className="hover:text-indigo-400 transition-colors"
            >
              {lesson.subject_name || "Subject"}
            </Link>
          ) : (
            <span>Subject</span>
          )}
          <ChevronRight className="w-3.5 h-3.5 text-slate-600" />
          {lesson?.course_slug ? (
            <Link
              href={`/courses/${lesson.course_slug}`}
              className="hover:text-indigo-400 transition-colors"
            >
              {lesson.course_title || "Course"}
            </Link>
          ) : (
            <span>Course</span>
          )}
          <ChevronRight className="w-3.5 h-3.5 text-slate-600" />
          {lesson?.topic_id ? (
            <Link
              href={`/topics/${lesson.topic_id}`}
              className="hover:text-indigo-400 transition-colors"
            >
              {lesson.topic_title || "Topic"}
            </Link>
          ) : (
            <span>Topic</span>
          )}
          <ChevronRight className="w-3.5 h-3.5 text-slate-600" />
          <span className="text-slate-300 font-semibold">{lesson?.title || "Lesson"}</span>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="p-16 rounded-2xl bg-slate-900/40 border border-slate-800 flex flex-col items-center justify-center gap-4 text-center">
            <div className="w-10 h-10 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
            <p className="text-xs text-slate-400 font-mono animate-pulse">
              Retrieving lesson content...
            </p>
          </div>
        )}

        {/* Unauthenticated Access Guard */}
        {!isLoading && accessState === "unauthenticated" && (
          <div className="p-8 sm:p-12 rounded-2xl bg-slate-900/80 border border-indigo-500/30 text-center space-y-5 max-w-lg mx-auto shadow-2xl relative z-10">
            <div className="w-14 h-14 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mx-auto">
              <Lock className="w-7 h-7" />
            </div>
            <div className="space-y-2">
              <h2 className="text-xl font-bold text-white">Student Sign-In Required</h2>
              <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
                Academic lessons and interactive concept materials require an active LuminaLearn student account.
              </p>
            </div>
            <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link
                href="/login"
                className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-all shadow-lg shadow-indigo-600/30"
              >
                Sign In to Read
              </Link>
              <Link
                href="/register"
                className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs transition-all border border-slate-700"
              >
                Create Account
              </Link>
            </div>
          </div>
        )}

        {/* Unverified Email Guard (Sprint 6.2A invariant) */}
        {!isLoading && accessState === "unverified" && (
          <div className="p-8 sm:p-12 rounded-2xl bg-slate-900/80 border border-amber-500/30 text-center space-y-5 max-w-lg mx-auto shadow-2xl relative z-10">
            <div className="w-14 h-14 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center mx-auto">
              <MailCheck className="w-7 h-7" />
            </div>
            <div className="space-y-2">
              <h2 className="text-xl font-bold text-white">Email Verification Required</h2>
              <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
                Under Sprint 6.2A security requirements, your account must be email OTP verified before accessing academic curriculum lessons.
              </p>
            </div>
            <div className="pt-2">
              <Link
                href="/verify-email"
                className="inline-flex px-6 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-semibold text-xs transition-all shadow-lg shadow-amber-600/30"
              >
                Verify Email with OTP
              </Link>
            </div>
          </div>
        )}

        {/* General Error State */}
        {!isLoading && accessState === "ok" && errorMessage && (
          <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center justify-between gap-4 max-w-xl mx-auto">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={loadLesson}
              className="px-3.5 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-white font-semibold flex items-center gap-1.5 transition-colors shrink-0"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Retry
            </button>
          </div>
        )}

        {/* Active Lesson Content Viewer */}
        {!isLoading && accessState === "ok" && lesson && (
          <article className="space-y-8 relative z-10">
            {/* Lesson Title Header */}
            <header className="p-6 sm:p-8 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-2xl space-y-4">
              <div className="flex flex-wrap items-center gap-3 text-xs">
                {lesson.topic_title && (
                  <span className="px-3 py-1 rounded-full font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                    Topic: {lesson.topic_title}
                  </span>
                )}
                <span className="text-slate-400 flex items-center gap-1.5">
                  <Clock className="w-4 h-4 text-indigo-400" />
                  Estimated Study Time: ~{lesson.estimated_minutes} Minutes
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono uppercase bg-slate-800 text-slate-300 border border-slate-700">
                  {lesson.lesson_type}
                </span>
              </div>

              <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
                {lesson.title}
              </h1>

              {lesson.summary && (
                <p className="text-sm sm:text-base text-slate-300 leading-relaxed max-w-3xl">
                  {lesson.summary}
                </p>
              )}
            </header>

            {/* Learning Objectives Checklist */}
            {lesson.learning_objectives && lesson.learning_objectives.length > 0 && (
              <div className="p-6 rounded-2xl bg-indigo-950/20 border border-indigo-500/30 space-y-3 shadow-lg">
                <div className="flex items-center gap-2 text-indigo-300 text-xs font-bold uppercase tracking-wider">
                  <Target className="w-4 h-4 text-indigo-400" />
                  Learning Objectives
                </div>
                <ul className="space-y-2">
                  {lesson.learning_objectives.map((obj, oIdx) => (
                    <li key={oIdx} className="flex items-start gap-2.5 text-xs text-slate-300">
                      <span className="w-4 h-4 rounded-full bg-indigo-500/20 border border-indigo-500/30 text-indigo-400 text-[10px] flex items-center justify-center shrink-0 mt-0.5 font-bold">
                        ✓
                      </span>
                      <span>{obj}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Markdown Body Viewer */}
            <div className="p-6 sm:p-10 rounded-2xl bg-slate-900/60 border border-slate-800/80 shadow-2xl">
              <div className="prose prose-invert max-w-none space-y-6 text-slate-300 text-sm sm:text-base leading-relaxed whitespace-pre-line font-sans">
                {lesson.content}
              </div>
            </div>

            {/* Navigation Footnotes */}
            <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-500">
              <Link
                href={lesson.topic_id ? `/topics/${lesson.topic_id}` : "/subjects"}
                className="flex items-center gap-1.5 hover:text-indigo-400 transition-colors"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                Return to Topic
              </Link>
              <span className="font-mono text-[11px]">
                LuminaLearn AI Academic Content Layer V1
              </span>
            </div>
          </article>
        )}
      </main>
  );
}
