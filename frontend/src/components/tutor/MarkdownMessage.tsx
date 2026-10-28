"use client";

import React, { memo } from "react";
import dynamic from "next/dynamic";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import { MathTex } from "@/components/tutor/MathTex";

// Highlighting and diagram layout load only when a reply actually contains code or a flowchart.
const blockPlaceholder = () => <div className="my-3 h-24 animate-pulse rounded-2xl bg-white/[0.03]" aria-hidden="true" />;
const CodeBlock = dynamic(() => import("@/components/tutor/CodeBlock").then((m) => m.CodeBlock), { loading: blockPlaceholder });
const FlowDiagram = dynamic(() => import("@/components/tutor/FlowDiagram").then((m) => m.FlowDiagram), { loading: blockPlaceholder });

const CITATION = /\[(\d+(?:\s*,\s*\d+)*)\]/g;

/** Turns `[1]` / `[1, 2]` markers in plain text into source chips. */
function withCitations(children: React.ReactNode, onCite?: (index: number) => void): React.ReactNode {
  return React.Children.map(children, (child) => {
    if (typeof child !== "string" || !CITATION.test(child)) return child;
    CITATION.lastIndex = 0;
    const parts: React.ReactNode[] = [];
    let last = 0;
    for (const match of child.matchAll(CITATION)) {
      const start = match.index ?? 0;
      if (start > last) parts.push(child.slice(last, start));
      match[1].split(",").forEach((n, i) => {
        const index = Number(n.trim());
        parts.push(
          <button
            key={`${start}-${i}`}
            type="button"
            onClick={() => onCite?.(index)}
            className="mx-0.5 inline-flex h-[1.15rem] min-w-[1.15rem] -translate-y-1 items-center justify-center rounded-md bg-indigo-500/20 px-1 align-baseline text-[10px] font-semibold text-indigo-200 outline-none transition-colors hover:bg-indigo-500/35 focus-visible:ring-2 focus-visible:ring-indigo-300"
            aria-label={`Source ${index}`}
          >
            {index}
          </button>
        );
      });
      last = start + match[0].length;
    }
    if (last < child.length) parts.push(child.slice(last));
    return parts;
  });
}

interface HastLike {
  type: string;
  tagName?: string;
  value?: string;
  properties?: { className?: unknown };
  children?: HastLike[];
}

function textOf(node: HastLike | undefined): string {
  if (!node) return "";
  if (node.type === "text") return node.value ?? "";
  return (node.children ?? []).map(textOf).join("");
}

function classList(node: HastLike | undefined): string[] {
  const value = node?.properties?.className;
  return Array.isArray(value) ? value.map(String) : typeof value === "string" ? value.split(" ") : [];
}

function buildComponents(onCite?: (index: number) => void): Components {
  const cite = (children: React.ReactNode) => withCitations(children, onCite);
  return {
    pre({ node }) {
      const code = (node as HastLike | undefined)?.children?.find((c) => c.type === "element" && c.tagName === "code");
      const classes = classList(code);
      const text = textOf(code).replace(/\n$/, "");
      if (classes.includes("math-display")) return <MathTex value={text} display />;
      const language = classes.find((c) => c.startsWith("language-"))?.slice("language-".length);
      if (language === "mermaid") return <FlowDiagram source={text} />;
      return <CodeBlock code={text} language={language} />;
    },
    code({ className, children }) {
      const value = String(children ?? "");
      if (className?.includes("math-inline")) return <MathTex value={value} />;
      return <code className={className}>{children}</code>;
    },
    p: ({ children }) => <p>{cite(children)}</p>,
    li: ({ children }) => <li>{cite(children)}</li>,
    strong: ({ children }) => <strong>{cite(children)}</strong>,
    em: ({ children }) => <em>{cite(children)}</em>,
    td: ({ children }) => <td>{cite(children)}</td>,
    a: ({ href, children }) => (
      <a href={href} target="_blank" rel="noopener noreferrer">
        {children}
      </a>
    ),
    table: ({ children }) => (
      <div className="overflow-x-auto">
        <table>{children}</table>
      </div>
    ),
  };
}

interface MarkdownMessageProps {
  text: string;
  onCite?: (index: number) => void;
}

/** Markdown + GFM + KaTeX math + Mermaid flowcharts + highlighted code, with citation chips. */
export const MarkdownMessage = memo(function MarkdownMessage({ text, onCite }: MarkdownMessageProps) {
  return (
    <div className="tutor-prose">
      <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} components={buildComponents(onCite)} skipHtml>
        {text}
      </ReactMarkdown>
    </div>
  );
});
