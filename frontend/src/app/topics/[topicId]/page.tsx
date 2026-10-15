"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { contentService, TopicDetail } from "@/services/contentService";
import {
  ArrowRight,
  BookOpen,
  Clock,
  Layers,
  AlertCircle,
  RefreshCw,
  ChevronRight,
  Calendar,
} from "lucide-react";

export default function TopicDetailPage() {
  const params = useParams();
  const topicId = params.topicId as string;

  const [topic, setTopic] = useState<TopicDetail | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadTopicData = async () => {
    if (!topicId) return;
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const data = await contentService.getTopic(topicId);
      setTopic(data);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to load topic details.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadTopicData();
  }, [topicId]);

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
          {topic?.subject_slug ? (
            <Link
              href={`/subjects/${topic.subject_slug}`}
              className="hover:text-indigo-400 transition-colors"
            >
              {topic.subject_name || "Subject"}
            </Link>
          ) : (
            <span>Subject</span>
          )}
          <ChevronRight className="w-3.5 h-3.5 text-slate-600" />
          {topic?.course_slug ? (
            <Link
              href={`/courses/${topic.course_slug}`}
              className="hover:text-indigo-400 transition-colors"
            >
              {topic.course_title || "Course"}
            </Link>
          ) : (
            <span>Course</span>
          )}
          <ChevronRight className="w-3.5 h-3.5 text-slate-600" />
          <span className="text-slate-300 font-semibold">{topic?.title || "Topic"}</span>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="p-16 rounded-2xl bg-slate-900/40 border border-slate-800 flex flex-col items-center justify-center gap-4 text-center">
            <div className="w-10 h-10 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
            <p className="text-xs text-slate-400 font-mono animate-pulse">
              Loading topic information and lessons...
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
              onClick={loadTopicData}
              className="px-3.5 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-white font-semibold flex items-center gap-1.5 transition-colors shrink-0"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Retry
            </button>
          </div>
        )}

        {/* Topic Content */}
        {!isLoading && topic && (
          <div className="space-y-8 relative z-10">
            {/* Topic Header Card */}
            <div className="p-6 sm:p-8 rounded-2xl bg-slate-900/80 border border-slate-800/80 shadow-2xl space-y-4">
              <div className="flex flex-wrap items-center gap-3 text-xs">
                {topic.module_title && (
                  <span className="px-3 py-1 rounded-full font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                    Module: {topic.module_title}
                  </span>
                )}
                <span className="text-slate-400 flex items-center gap-1.5">
                  <Clock className="w-4 h-4 text-indigo-400" />
                  Estimated Time: ~{topic.estimated_minutes} Minutes
                </span>
                <span className="text-slate-400 flex items-center gap-1.5">
                  <Layers className="w-4 h-4 text-purple-400" />
                  Level: {topic.difficulty}
                </span>
              </div>

              <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                {topic.title}
              </h1>

              <p className="text-sm text-slate-300 leading-relaxed">
                {topic.summary || "Core concept learning unit."}
              </p>
            </div>

            {/* Lessons Section */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-indigo-400" />
                  Learning Units & Lessons
                </h2>
                <span className="text-xs text-slate-500 font-mono">
                  {topic.lessons.length} {topic.lessons.length === 1 ? "Lesson" : "Lessons"}
                </span>
              </div>

              {topic.lessons.length > 0 ? (
                <div className="space-y-3">
                  {topic.lessons.map((lesson, lIdx) => (
                    <Link
                      key={lesson.id}
                      href={`/lessons/${lesson.id}`}
                      className="group p-5 rounded-2xl bg-slate-900/60 hover:bg-slate-900 border border-slate-800/80 hover:border-indigo-500/40 transition-all flex items-center justify-between gap-4 shadow-lg"
                    >
                      <div className="flex items-start gap-3.5 min-w-0">
                        <span className="w-8 h-8 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-mono font-bold flex items-center justify-center shrink-0 mt-0.5">
                          {String(lIdx + 1).padStart(2, "0")}
                        </span>
                        <div className="space-y-1 min-w-0">
                          <h3 className="text-sm font-bold text-white group-hover:text-indigo-300 transition-colors truncate">
                            {lesson.title}
                          </h3>
                          <p className="text-xs text-slate-400 line-clamp-1">
                            {lesson.summary || "Structured concept breakdown and worked examples."}
                          </p>
                          <div className="flex items-center gap-3 text-[11px] text-slate-500 pt-1 font-mono">
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              ~{lesson.estimated_minutes} mins
                            </span>
                            <span>•</span>
                            <span className="capitalize">{lesson.lesson_type}</span>
                          </div>
                        </div>
                      </div>

                      <div className="px-4 py-2 rounded-xl bg-indigo-600/20 group-hover:bg-indigo-600 text-indigo-300 group-hover:text-white font-semibold text-xs transition-all flex items-center gap-1.5 shrink-0">
                        <span>Read Lesson</span>
                        <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                /* Fallback: Lessons coming soon */
                <div className="p-8 rounded-2xl bg-slate-900/40 border border-slate-800/80 text-center space-y-3 max-w-md mx-auto">
                  <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center mx-auto">
                    <Calendar className="w-6 h-6" />
                  </div>
                  <h3 className="text-base font-bold text-white">Lessons Coming Soon</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Detailed educational text and interactive exercises for this topic are currently being authored by our academic curriculum team.
                  </p>
                  <div className="pt-2">
                    <span className="px-3 py-1 rounded-full text-[11px] font-semibold bg-slate-800 text-slate-400 border border-slate-700">
                      Curriculum Pipeline: In Authoring
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
  );
}
