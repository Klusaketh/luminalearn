import { API_BASE, apiFetch, readErrorDetail } from "./apiClient";

export type Difficulty = "Easy" | "Medium" | "Hard";

export interface PracticeProblemSummary {
  slug: string;
  title: string;
  difficulty: Difficulty;
  tags: string[];
  order: number;
  solved: boolean;
  attempts: number;
}

export interface PracticeTestCase {
  args: unknown[];
  expected: unknown;
}

export interface PracticeProblemDetail extends PracticeProblemSummary {
  statement: string;
  starter_code: string;
  function_name: string;
  compare: "exact" | "unordered";
  hints: string[];
  tests: PracticeTestCase[];
  harness: string;
  related_topic: { id: string; title: string } | null;
  best_passed: number;
}

export interface PracticeProblemList {
  problems: PracticeProblemSummary[];
  solved_count: number;
  total_count: number;
}

export interface PracticeSubmissionResult {
  solved: boolean;
  attempts: number;
  best_passed: number;
  total: number;
}

/** One test's outcome, as reported by content/practice/harness.py running in the browser. */
export interface TestOutcome {
  index: number;
  passed: boolean;
  got: string | null;
  stdout: string;
  error: string | null;
}

export interface RunReport {
  error: string | null;
  stdout: string;
  results: TestOutcome[];
}

async function getJson<T>(path: string, fallback: string, init?: RequestInit): Promise<T> {
  const res = await apiFetch(`${API_BASE}${path}`, init);
  if (!res.ok) throw new Error(await readErrorDetail(res, fallback));
  return res.json() as Promise<T>;
}

export const practiceService = {
  list(signal?: AbortSignal): Promise<PracticeProblemList> {
    return getJson("/practice/problems", "Could not load the practice problems.", { signal });
  },

  get(slug: string, signal?: AbortSignal): Promise<PracticeProblemDetail> {
    return getJson(`/practice/problems/${encodeURIComponent(slug)}`, "Could not load this problem.", { signal });
  },

  submit(slug: string, body: { code: string; passed: number; total: number }): Promise<PracticeSubmissionResult> {
    return getJson(`/practice/problems/${encodeURIComponent(slug)}/submissions`, "Could not save your result.", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  },
};
