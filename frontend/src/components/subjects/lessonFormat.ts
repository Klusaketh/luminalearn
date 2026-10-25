/**
 * Parsing helpers for Subjects lesson content (format: content/README.md).
 *
 * Lessons are Markdown with one extension, the practice question block:
 *
 *   :::question basic
 *   Question text (Markdown)
 *   :::answer
 *   Answer and explanation (Markdown)
 *   :::
 */

export type QuestionLevel = "basic" | "intermediate" | "advanced";

export interface PracticeQuestion {
  number: number;
  level: QuestionLevel | null;
  question: string;
  answer: string;
}

export type LessonBlock = { kind: "markdown"; text: string } | { kind: "practice"; questions: PracticeQuestion[] };

export interface Heading {
  id: string;
  text: string;
}

const QUESTION = /^:::question(?:[ \t]+([a-z]+))?[ \t]*\n([\s\S]*?)\n:::answer[ \t]*\n([\s\S]*?)\n:::[ \t]*$/gm;
const LEVELS: QuestionLevel[] = ["basic", "intermediate", "advanced"];

/** Splits a lesson into Markdown runs and groups of consecutive practice questions. */
export function splitLesson(content: string): LessonBlock[] {
  const text = content.replace(/\r\n/g, "\n");
  const blocks: LessonBlock[] = [];
  let cursor = 0;
  let number = 0;
  for (const match of text.matchAll(QUESTION)) {
    const start = match.index ?? 0;
    const between = text.slice(cursor, start);
    const level = LEVELS.includes(match[1] as QuestionLevel) ? (match[1] as QuestionLevel) : null;
    const question: PracticeQuestion = { number: ++number, level, question: match[2].trim(), answer: match[3].trim() };
    const last = blocks[blocks.length - 1];
    if (last?.kind === "practice" && between.trim() === "") {
      last.questions.push(question);
    } else {
      if (between.trim()) blocks.push({ kind: "markdown", text: between });
      blocks.push({ kind: "practice", questions: [question] });
    }
    cursor = start + match[0].length;
  }
  const rest = text.slice(cursor);
  if (rest.trim()) blocks.push({ kind: "markdown", text: rest });
  return blocks;
}

/** Stable anchor id for a heading; the renderer and the table of contents must agree. */
export function headingId(text: string): string {
  return text
    .toLowerCase()
    .replace(/[`*_$\\]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

/** H2 headings outside fenced code, for the lesson's table of contents. */
export function extractHeadings(markdown: string): Heading[] {
  const headings: Heading[] = [];
  let fence: string | null = null;
  for (const line of markdown.replace(/\r\n/g, "\n").split("\n")) {
    const marker = line.trimStart().slice(0, 3);
    if (marker === "```" || marker === "~~~") {
      fence = fence === marker ? null : fence ?? marker;
      continue;
    }
    if (!fence && line.startsWith("## ")) {
      const text = line.slice(3).trim();
      headings.push({ id: headingId(text), text });
    }
  }
  return headings;
}

/** A subject overview: the opening text plus its named `## ` sections. */
export function overviewSections(markdown: string): { intro: string; sections: Record<string, string> } {
  const parts = markdown.replace(/\r\n/g, "\n").split(/^## /m);
  const sections: Record<string, string> = {};
  for (const part of parts.slice(1)) {
    const newline = part.indexOf("\n");
    const title = (newline === -1 ? part : part.slice(0, newline)).trim();
    sections[title] = newline === -1 ? "" : part.slice(newline + 1).trim();
  }
  return { intro: parts[0].trim(), sections };
}

/** `- **Term**: definition` list items from a glossary section. */
export function glossaryEntries(markdown: string): { term: string; definition: string }[] {
  const entries: { term: string; definition: string }[] = [];
  for (const line of markdown.split("\n")) {
    const match = /^\s*[-*]\s+\*\*(.+?)\*\*\s*[:—-]\s*(.+)$/.exec(line);
    if (match) entries.push({ term: match[1].trim(), definition: match[2].trim() });
  }
  return entries;
}

/** Plain-text list items of a Markdown section (objectives, prerequisites). */
export function listItems(markdown: string): string[] {
  return markdown
    .split("\n")
    .map((line) => /^\s*(?:[-*]|\d+\.)\s+(.+)$/.exec(line)?.[1]?.trim())
    .filter((item): item is string => Boolean(item));
}
