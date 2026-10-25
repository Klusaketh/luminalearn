"use client";

import React, { memo } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import { MathTex } from "@/components/tutor/MathTex";
import { headingId } from "./lessonFormat";
import styles from "./lesson.module.css";

// Highlighting and diagram layout load only for lessons that contain code or a flowchart.
const blockPlaceholder = () => <div className="my-4 h-28 animate-pulse rounded-2xl bg-white/[0.03]" aria-hidden="true" />;
const CodeBlock = dynamic(() => import("@/components/tutor/CodeBlock").then((m) => m.CodeBlock), { loading: blockPlaceholder });
const FlowDiagram = dynamic(() => import("@/components/tutor/FlowDiagram").then((m) => m.FlowDiagram), { loading: blockPlaceholder });

interface HastNode {
  type: string;
  tagName?: string;
  value?: string;
  properties?: { className?: unknown };
  children?: HastNode[];
}

function textOf(node: HastNode | undefined): string {
  if (!node) return "";
  if (node.type === "text") return node.value ?? "";
  return (node.children ?? []).map(textOf).join("");
}

function classList(node: HastNode | undefined): string[] {
  const value = node?.properties?.className;
  return Array.isArray(value) ? value.map(String) : typeof value === "string" ? value.split(" ") : [];
}

const components: Components = {
  h2: ({ node, children }) => <h2 id={headingId(textOf(node as HastNode))}>{children}</h2>,
  h3: ({ node, children }) => <h3 id={headingId(textOf(node as HastNode))}>{children}</h3>,
  pre({ node }) {
    const code = (node as HastNode | undefined)?.children?.find((c) => c.type === "element" && c.tagName === "code");
    const classes = classList(code);
    const text = textOf(code).replace(/\n$/, "");
    if (classes.includes("math-display")) return <MathTex value={text} display />;
    const language = classes.find((c) => c.startsWith("language-"))?.slice("language-".length);
    if (language === "mermaid") return <FlowDiagram source={text} />;
    return <CodeBlock code={text} language={language} />;
  },
  code({ className, children }) {
    if (className?.includes("math-inline")) return <MathTex value={String(children ?? "")} />;
    return <code className={className}>{children}</code>;
  },
  a: ({ href = "", children }) =>
    href.startsWith("/") ? (
      <Link href={href}>{children}</Link>
    ) : (
      <a href={href} target="_blank" rel="noopener noreferrer">
        {children}
      </a>
    ),
  table: ({ children }) => (
    <div className={styles.tableWrap}>
      <table>{children}</table>
    </div>
  ),
};

interface LessonMarkdownProps {
  markdown: string;
  /** Smaller type for answers and side panels. */
  compact?: boolean;
  className?: string;
}

/** Lesson Markdown: GFM tables, KaTeX math, highlighted code, simple flowcharts, anchored headings. */
export const LessonMarkdown = memo(function LessonMarkdown({ markdown, compact = false, className = "" }: LessonMarkdownProps) {
  return (
    <div className={`${styles.prose} ${compact ? styles.compact : ""} ${className}`}>
      <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} components={components} skipHtml>
        {markdown}
      </ReactMarkdown>
    </div>
  );
});
