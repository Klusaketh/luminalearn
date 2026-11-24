import type { PracticeLanguage } from "@/services/practiceService";

/** Python-style rendering of JSON test data, so learners see `True` and `None`, not `true` and `null`. */
export function pyRepr(value: unknown): string {
  if (value === null || value === undefined) return "None";
  if (value === true) return "True";
  if (value === false) return "False";
  if (typeof value === "string") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(pyRepr).join(", ")}]`;
  if (typeof value === "object") {
    return `{${Object.entries(value as Record<string, unknown>)
      .map(([k, v]) => `${JSON.stringify(k)}: ${pyRepr(v)}`)
      .join(", ")}}`;
  }
  return String(value);
}

/** JavaScript-style rendering: `true`, `null`, and arrays with spaces. */
export function jsRepr(value: unknown): string {
  if (value === null || value === undefined) return "null";
  if (typeof value === "string") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(jsRepr).join(", ")}]`;
  if (typeof value === "object") {
    return `{${Object.entries(value as Record<string, unknown>)
      .map(([k, v]) => `${JSON.stringify(k)}: ${jsRepr(v)}`)
      .join(", ")}}`;
  }
  return String(value);
}

export function valueRepr(value: unknown, language: PracticeLanguage = "python"): string {
  return language === "javascript" ? jsRepr(value) : pyRepr(value);
}

/** `two_sum([2, 7], 9)` or `twoSum([2, 7], 9)` */
export function callRepr(functionName: string, args: unknown[], language: PracticeLanguage = "python"): string {
  return `${functionName}(${args.map((arg) => valueRepr(arg, language)).join(", ")})`;
}

/** The harness reports results as JSON text; show them the same way as expected values. */
export function gotRepr(got: string | null, language: PracticeLanguage = "python"): string {
  if (got === null) return language === "javascript" ? "undefined" : "None";
  try {
    return valueRepr(JSON.parse(got), language);
  } catch {
    return got;
  }
}

export const DIFFICULTY_TONE: Record<string, string> = {
  Easy: "bg-emerald-400/10 text-emerald-200 ring-emerald-300/25",
  Medium: "bg-amber-400/10 text-amber-200 ring-amber-300/25",
  Hard: "bg-rose-400/10 text-rose-200 ring-rose-300/25",
};
