"use client";

import React, { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { AlertCircle, ArrowRight, RefreshCw, Search, X } from "lucide-react";
import { useOnReconnect } from "@/hooks/useOnReconnect";
import { contentService, type ContentCategorySummary, type SubjectSummary } from "@/services/contentService";
import { DifficultyBadge, SubjectIcon } from "@/components/subjects/SubjectIcon";

type SortKey = "syllabus" | "name" | "topics" | "difficulty";

const SORTS: { key: SortKey; label: string }[] = [
  { key: "syllabus", label: "Catalog order" },
  { key: "name", label: "Name (A to Z)" },
  { key: "topics", label: "Most topics" },
  { key: "difficulty", label: "Beginner first" },
];
const DIFFICULTY_RANK: Record<string, number> = { beginner: 0, intermediate: 1, advanced: 2 };

interface Match {
  subject: SubjectSummary;
  /** Topic titles that matched when the subject itself did not. */
  topics: string[];
}

function matchSubject(subject: SubjectSummary, query: string): Match | null {
  if (!query) return { subject, topics: [] };
  const haystack = [subject.name, subject.short_description ?? "", subject.category_name ?? ""].join(" ").toLowerCase();
  if (haystack.includes(query)) return { subject, topics: [] };
  const topics = subject.topic_titles.filter((title) => title.toLowerCase().includes(query));
  return topics.length > 0 ? { subject, topics } : null;
}

function SubjectCard({ match }: { match: Match }) {
  const { subject, topics } = match;
  return (
    <Link
      href={`/subjects/${subject.slug}`}
      className="group flex h-full flex-col rounded-2xl border border-white/[0.08] bg-white/[0.02] p-6 outline-none transition-colors hover:border-indigo-300/35 hover:bg-white/[0.035] focus-visible:ring-2 focus-visible:ring-indigo-300"
    >
      <div className="flex items-start justify-between gap-3">
        <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-500/10 text-indigo-200 transition-colors group-hover:bg-indigo-500/15">
          <SubjectIcon iconKey={subject.icon_key} />
        </span>
        <DifficultyBadge level={subject.difficulty_level} />
      </div>
      <p className="mt-5 text-xs font-medium text-slate-500">{subject.category_name}</p>
      <h2 className="mt-1 text-xl font-semibold leading-snug text-white">{subject.name}</h2>
      <p className="mt-2 line-clamp-3 text-[15px] leading-relaxed text-slate-400">{subject.short_description}</p>
      {topics.length > 0 && (
        <p className="mt-3 text-sm text-indigo-200">
          Matches {topics.length === 1 ? "topic" : "topics"}: {topics.slice(0, 2).join(", ")}
          {topics.length > 2 ? ` and ${topics.length - 2} more` : ""}
        </p>
      )}
      <div className="mt-auto flex items-center justify-between gap-3 border-t border-white/[0.06] pt-4 text-sm">
        <span className="tabular text-slate-400">
          {subject.module_count} modules · {subject.topic_count} topics · {subject.lesson_count} lessons
        </span>
        <span className="flex items-center gap-1 font-medium text-indigo-200 group-hover:text-white">
          Explore <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
        </span>
      </div>
    </Link>
  );
}

export default function SubjectsCatalogPage() {
  const [categories, setCategories] = useState<ContentCategorySummary[]>([]);
  const [subjects, setSubjects] = useState<SubjectSummary[]>([]);
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [sort, setSort] = useState<SortKey>("syllabus");
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadCatalog = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const [cats, subs] = await Promise.all([contentService.getCategories(), contentService.getSubjects()]);
      setCategories(cats);
      setSubjects(subs);
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Failed to load the academic catalog.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadCatalog();
  }, [loadCatalog]);

  // After a server outage, reload by itself if this page is showing a load error.
  useOnReconnect(() => {
    if (errorMessage) void loadCatalog();
  });

  const query = searchQuery.trim().toLowerCase();
  const searched = useMemo(() => subjects.map((s) => matchSubject(s, query)).filter((m): m is Match => m !== null), [subjects, query]);
  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const m of searched) counts[m.subject.category_slug ?? ""] = (counts[m.subject.category_slug ?? ""] ?? 0) + 1;
    return counts;
  }, [searched]);
  const visible = useMemo(() => {
    const filtered = searched.filter((m) => selectedCategory === "all" || m.subject.category_slug === selectedCategory);
    const categoryOrder = new Map(categories.map((c) => [c.slug, c.display_order]));
    const bySyllabus = (a: Match, b: Match) =>
      (categoryOrder.get(a.subject.category_slug ?? "") ?? 0) - (categoryOrder.get(b.subject.category_slug ?? "") ?? 0) ||
      a.subject.display_order - b.subject.display_order;
    const comparators: Record<SortKey, (a: Match, b: Match) => number> = {
      syllabus: bySyllabus,
      name: (a, b) => a.subject.name.localeCompare(b.subject.name),
      topics: (a, b) => b.subject.topic_count - a.subject.topic_count || bySyllabus(a, b),
      difficulty: (a, b) =>
        (DIFFICULTY_RANK[a.subject.difficulty_level.toLowerCase()] ?? 1) - (DIFFICULTY_RANK[b.subject.difficulty_level.toLowerCase()] ?? 1) ||
        bySyllabus(a, b),
    };
    return [...filtered].sort(comparators[sort]);
  }, [searched, selectedCategory, sort, categories]);

  const clearFilters = () => {
    setSearchQuery("");
    setSelectedCategory("all");
  };

  const pill = (active: boolean) =>
    `rounded-xl px-3.5 py-2 text-sm font-medium outline-none transition-colors focus-visible:ring-2 focus-visible:ring-indigo-300 ${
      active ? "bg-white text-space-950" : "border border-white/[0.08] text-slate-300 hover:border-white/20 hover:text-white"
    }`;

  return (
    <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-10 sm:px-6 lg:px-8">
      <header className="max-w-3xl">
        <p className="text-sm font-medium text-indigo-300">Subjects</p>
        <h1 className="mt-2 font-display text-4xl leading-tight text-white sm:text-6xl">The academic catalog</h1>
        <p className="mt-4 text-lg leading-relaxed text-slate-300">
          Twenty-two subjects across computer science, programming, artificial intelligence, and mathematics. Each one is a full syllabus of lessons with theory, worked examples, and practice questions.
        </p>
      </header>

      {isLoading && (
        <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3" role="status" aria-live="polite">
          <span className="sr-only">Loading the catalog</span>
          {Array.from({ length: 6 }, (_, i) => (
            <div key={i} className="h-64 animate-pulse rounded-2xl border border-white/[0.05] bg-white/[0.02]" />
          ))}
        </div>
      )}

      {!isLoading && errorMessage && (
        <div role="alert" className="mt-10 flex max-w-2xl flex-col items-start justify-between gap-4 rounded-2xl border border-rose-400/30 bg-rose-500/10 p-6 sm:flex-row sm:items-center">
          <div className="flex items-center gap-3">
            <AlertCircle className="h-5 w-5 shrink-0 text-rose-300" aria-hidden="true" />
            <div>
              <p className="font-semibold text-white">The catalog could not be loaded</p>
              <p className="mt-0.5 text-sm text-rose-100/80">{errorMessage}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => void loadCatalog()}
            className="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2 text-sm font-semibold text-space-950 outline-none focus-visible:ring-2 focus-visible:ring-indigo-300"
          >
            <RefreshCw className="h-4 w-4" aria-hidden="true" />
            Retry
          </button>
        </div>
      )}

      {!isLoading && !errorMessage && (
        <>
          <div className="mt-10 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div className="relative w-full lg:max-w-md">
              <label htmlFor="subject-search-input" className="sr-only">
                Search subjects and topics
              </label>
              <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
              <input
                id="subject-search-input"
                type="search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search subjects or topics, e.g. paging, recursion, eigenvalues"
                className="w-full rounded-xl border border-white/10 bg-white/[0.03] py-3 pl-10 pr-10 text-[15px] text-white placeholder:text-slate-500 outline-none transition-colors focus:border-indigo-300/50 focus:ring-2 focus:ring-indigo-300/30"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery("")}
                  aria-label="Clear search"
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 rounded-lg p-1 text-slate-400 outline-none hover:text-white focus-visible:ring-2 focus-visible:ring-indigo-300"
                >
                  <X className="h-4 w-4" aria-hidden="true" />
                </button>
              )}
            </div>
            <label className="flex items-center gap-2 text-sm text-slate-400">
              Sort by
              <select
                value={sort}
                onChange={(e) => setSort(e.target.value as SortKey)}
                className="rounded-xl border border-white/10 bg-space-900 px-3 py-2 text-sm text-white outline-none focus:ring-2 focus:ring-indigo-300/40"
              >
                {SORTS.map((option) => (
                  <option key={option.key} value={option.key}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div role="group" aria-label="Filter by category" className="mt-4 flex flex-wrap gap-2">
            <button type="button" aria-pressed={selectedCategory === "all"} onClick={() => setSelectedCategory("all")} className={pill(selectedCategory === "all")}>
              All categories <span className="tabular opacity-70">({searched.length})</span>
            </button>
            {categories.map((cat) => (
              <button
                key={cat.id}
                type="button"
                aria-pressed={selectedCategory === cat.slug}
                onClick={() => setSelectedCategory(cat.slug)}
                className={pill(selectedCategory === cat.slug)}
              >
                {cat.name} <span className="tabular opacity-70">({categoryCounts[cat.slug] ?? 0})</span>
              </button>
            ))}
          </div>

          <p className="mt-6 text-sm text-slate-400" aria-live="polite">
            Showing {visible.length} of {subjects.length} subjects
            {query ? ` matching "${searchQuery.trim()}"` : ""}
          </p>

          {visible.length === 0 ? (
            <div className="mt-6 max-w-lg rounded-2xl border border-white/[0.08] bg-white/[0.02] p-8">
              <p className="font-semibold text-white">No subject or topic matches that search</p>
              <p className="mt-1 text-sm leading-relaxed text-slate-400">
                Try a broader term, check the spelling, or search for a topic name such as &ldquo;sorting&rdquo; or &ldquo;probability&rdquo;.
              </p>
              <button type="button" onClick={clearFilters} className="mt-4 rounded-xl border border-white/15 px-4 py-2 text-sm font-semibold text-white outline-none hover:border-white/30 focus-visible:ring-2 focus-visible:ring-indigo-300">
                Clear search and filters
              </button>
            </div>
          ) : (
            <ul className="mt-4 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {visible.map((match) => (
                <li key={match.subject.id}>
                  <SubjectCard match={match} />
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </main>
  );
}
