"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  contentService,
  ContentCategorySummary,
  SubjectSummary,
} from "@/services/contentService";
import {
  Sparkles,
  Search,
  BookOpen,
  ArrowRight,
  Layers,
  GraduationCap,
  Code2,
  Database,
  Cpu,
  Network,
  Binary,
  Server,
  Terminal,
  Code,
  Coffee,
  FileCode,
  Brain,
  Wand2,
  MessageSquare,
  Eye,
  Sigma,
  Dice5,
  BarChart3,
  Grid3X3,
  Calculator,
  AlertCircle,
  RefreshCw,
} from "lucide-react";

// Icon resolution helper for dynamic icon_key
function getSubjectIcon(iconKey: string | null) {
  const className = "w-6 h-6";
  switch (iconKey) {
    case "code-2":
      return <Code2 className={className} />;
    case "cpu":
      return <Cpu className={className} />;
    case "database":
      return <Database className={className} />;
    case "network":
      return <Network className={className} />;
    case "binary":
      return <Binary className={className} />;
    case "server":
      return <Server className={className} />;
    case "terminal":
      return <Terminal className={className} />;
    case "code":
      return <Code className={className} />;
    case "coffee":
      return <Coffee className={className} />;
    case "file-code":
      return <FileCode className={className} />;
    case "brain":
      return <Brain className={className} />;
    case "sparkles":
      return <Sparkles className={className} />;
    case "wand-2":
      return <Wand2 className={className} />;
    case "message-square":
      return <MessageSquare className={className} />;
    case "eye":
      return <Eye className={className} />;
    case "sigma":
      return <Sigma className={className} />;
    case "dice-5":
      return <Dice5 className={className} />;
    case "bar-chart":
      return <BarChart3 className={className} />;
    case "grid":
      return <Grid3X3 className={className} />;
    case "calculator":
      return <Calculator className={className} />;
    default:
      return <BookOpen className={className} />;
  }
}

export default function SubjectsCatalogPage() {
  const [categories, setCategories] = useState<ContentCategorySummary[]>([]);
  const [subjects, setSubjects] = useState<SubjectSummary[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadCatalog = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const [cats, subs] = await Promise.all([
        contentService.getCategories(),
        contentService.getSubjects(),
      ]);
      setCategories(cats);
      setSubjects(subs);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to load academic catalog.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadCatalog();
  }, []);

  // Filter subjects based on active category & search query
  const filteredSubjects = subjects.filter((subject) => {
    const matchesCategory =
      selectedCategory === "all" || subject.category_slug === selectedCategory;
    const matchesSearch =
      searchQuery.trim() === "" ||
      subject.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (subject.short_description &&
        subject.short_description.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  return (
    <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-10 space-y-8 relative overflow-hidden">
      {/* Ambient Glow */}
      <div className="absolute top-1/6 left-1/2 -translate-x-1/2 w-[700px] h-[350px] bg-indigo-600/10 blur-[160px] rounded-full pointer-events-none" />

      {/* Catalog Header */}
      <div className="text-center space-y-4 max-w-3xl mx-auto relative z-10">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold uppercase tracking-wider">
          <GraduationCap className="w-4 h-4" />
          Academic Knowledge Graph
        </div>
        <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-300 bg-clip-text text-transparent">
          Explore Academic Subjects
        </h1>
        <p className="text-sm sm:text-base text-slate-400 leading-relaxed">
          Browse our structured curriculum across Computer Science, Programming, Artificial Intelligence, and Mathematics. Built to power personalized Socratic learning.
        </p>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="space-y-8 relative z-10 py-6">
          <div className="p-12 rounded-2xl bg-slate-900/40 border border-slate-800/80 flex flex-col items-center justify-center gap-4 text-center max-w-md mx-auto">
            <div className="w-10 h-10 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
            <p className="text-xs text-slate-400 font-mono animate-pulse">
              Retrieving dynamic academic catalog...
            </p>
          </div>

          {/* Skeleton Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div
                key={i}
                className="p-6 rounded-2xl bg-slate-900/30 border border-slate-800/50 space-y-4 animate-pulse"
              >
                <div className="flex justify-between items-start">
                  <div className="w-12 h-12 rounded-xl bg-slate-800/60" />
                  <div className="w-16 h-5 rounded-full bg-slate-800/60" />
                </div>
                <div className="space-y-2">
                  <div className="h-5 w-3/4 bg-slate-800/60 rounded" />
                  <div className="h-4 w-full bg-slate-800/40 rounded" />
                  <div className="h-4 w-2/3 bg-slate-800/40 rounded" />
                </div>
                <div className="pt-4 border-t border-slate-800/40 flex justify-between">
                  <div className="h-4 w-20 bg-slate-800/40 rounded" />
                  <div className="h-4 w-12 bg-slate-800/40 rounded" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Error State */}
      {!isLoading && errorMessage && (
        <div className="p-8 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex flex-col sm:flex-row items-center justify-between gap-6 max-w-2xl mx-auto relative z-10 shadow-lg shadow-rose-950/20">
          <div className="flex items-center gap-4 text-center sm:text-left">
            <div className="w-10 h-10 rounded-xl bg-rose-500/20 border border-rose-500/30 flex items-center justify-center shrink-0">
              <AlertCircle className="w-5 h-5 text-rose-400" />
            </div>
            <div>
              <h3 className="font-semibold text-white">Unable to load the academic catalog</h3>
              <p className="text-xs text-rose-300/80 mt-1">{errorMessage}</p>
            </div>
          </div>
          <button
            onClick={loadCatalog}
            className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-2 transition-all shadow-md shadow-indigo-600/30 shrink-0"
          >
            <RefreshCw className="w-4 h-4" />
            Retry
          </button>
        </div>
      )}

      {/* Loaded Content */}
      {!isLoading && !errorMessage && (
        <>
          {/* Filter Controls Bar */}
          <div className="space-y-4 relative z-10">
            {/* Search Input */}
            <div className="max-w-md mx-auto relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="text"
                id="subject-search-input"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search subjects by name or keyword..."
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/80 border border-slate-800 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
              />
            </div>

            {/* Category Filter Pills */}
            <div className="flex flex-wrap items-center justify-center gap-2 pt-2">
              <button
                onClick={() => setSelectedCategory("all")}
                className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all flex items-center gap-1.5 ${
                  selectedCategory === "all"
                    ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30"
                    : "bg-slate-900/60 border border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
                }`}
              >
                <Layers className="w-3.5 h-3.5" />
                All Categories ({subjects.length})
              </button>
              {categories.map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.slug)}
                  className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                    selectedCategory === cat.slug
                      ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30"
                      : "bg-slate-900/60 border border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
                  }`}
                >
                  {cat.name} ({cat.subject_count})
                </button>
              ))}
            </div>
          </div>

          {/* Empty State */}
          {filteredSubjects.length === 0 && (
            <div className="p-12 rounded-2xl bg-slate-900/60 border border-slate-800 text-center space-y-3 max-w-md mx-auto">
              <div className="w-12 h-12 rounded-xl bg-slate-800 text-slate-400 flex items-center justify-center mx-auto">
                <Search className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-white">No Subjects Found</h3>
              <p className="text-xs text-slate-400">
                No academic subjects matched &ldquo;{searchQuery}&rdquo;. Try another search term or switch categories.
              </p>
              <button
                onClick={() => {
                  setSearchQuery("");
                  setSelectedCategory("all");
                }}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition-colors"
              >
                Clear Filters
              </button>
            </div>
          )}

          {/* Subject Cards Grid */}
          {filteredSubjects.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 relative z-10">
              {filteredSubjects.map((subject) => (
                <Link
                  key={subject.id}
                  href={`/subjects/${subject.slug}`}
                  className="group p-6 rounded-2xl bg-slate-900/60 hover:bg-slate-900/90 border border-slate-800/80 hover:border-indigo-500/40 transition-all duration-300 flex flex-col justify-between shadow-lg hover:shadow-xl hover:shadow-indigo-500/5 hover:-translate-y-0.5"
                >
                  <div className="space-y-4">
                    {/* Top Header */}
                    <div className="flex items-start justify-between gap-3">
                      <div className="w-12 h-12 rounded-xl bg-indigo-600/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center group-hover:scale-105 group-hover:bg-indigo-600/20 transition-all">
                        {getSubjectIcon(subject.icon_key)}
                      </div>
                      <div className="flex flex-col items-end gap-1.5">
                        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                          {subject.category_name || "Academic"}
                        </span>
                        <span className="px-2 py-0.5 rounded-full text-[9px] font-medium bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 capitalize">
                          {subject.difficulty_level}
                        </span>
                      </div>
                    </div>

                    {/* Subject Details */}
                    <div>
                      <h3 className="text-lg font-bold text-white group-hover:text-indigo-400 transition-colors">
                        {subject.name}
                      </h3>
                      <p className="text-xs text-slate-400 mt-2 line-clamp-2 leading-relaxed">
                        {subject.short_description || "Comprehensive academic syllabus and learning modules."}
                      </p>
                    </div>
                  </div>

                  {/* Card Footer */}
                  <div className="pt-4 mt-6 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-400">
                    <span className="flex items-center gap-1.5 font-mono">
                      <BookOpen className="w-3.5 h-3.5 text-slate-500" />
                      {subject.course_count} {subject.course_count === 1 ? "Course" : "Courses"}
                    </span>
                    <span className="text-indigo-400 flex items-center gap-1 font-semibold group-hover:translate-x-0.5 transition-transform">
                      Explore
                      <ArrowRight className="w-3.5 h-3.5" />
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </>
      )}
    </main>
  );
}
