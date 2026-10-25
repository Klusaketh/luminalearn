"use client";

import React, { useMemo } from "react";
import katex from "katex";

interface MathRendererProps {
  content: string;
  className?: string;
  block?: boolean;
}

const escapeHtml = (text: string) =>
  text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

/**
 * MathRenderer component for LuminaLearn AI
 * Renders mixed text and LaTeX mathematical expressions ($...$ inline or $$...$$ block)
 * utilizing KaTeX with zero hydration mismatches and full error fallback resilience.
 */
export const MathRenderer: React.FC<MathRendererProps> = ({
  content,
  className = "",
  block = false,
}) => {
  const renderedContent = useMemo(() => {
    if (!content) return "";

    // If whole string is requested as a block or wrapped in $$...$$
    if (block) {
      const cleanBlock = content.replace(/^\$\$/, "").replace(/\$\$$/, "").trim();
      try {
        return katex.renderToString(cleanBlock, {
          displayMode: true,
          throwOnError: false,
          strict: false,
        });
      } catch {
        return `<pre class="text-rose-400 text-xs font-mono">${escapeHtml(cleanBlock)}</pre>`;
      }
    }

    // Split content by $$ (block math) and $ (inline math)
    // Regex splits keeping delimiters:
    // Group 1: $$...$$
    // Group 2: $...$
    const mathRegex = /(\$\$[\s\S]+?\$\$|\$[^\$]+?\$)/g;
    const parts = content.split(mathRegex);

    return parts
      .map((part) => {
        if (!part) return "";

        // Block math ($$...$$)
        if (part.startsWith("$$") && part.endsWith("$$") && part.length >= 4) {
          const formula = part.slice(2, -2).trim();
          try {
            return katex.renderToString(formula, {
              displayMode: true,
              throwOnError: false,
              strict: false,
            });
          } catch {
            return `<span class="text-rose-400 font-mono text-xs">${escapeHtml(formula)}</span>`;
          }
        }

        // Inline math ($...$)
        if (part.startsWith("$") && part.endsWith("$") && part.length >= 2) {
          const formula = part.slice(1, -1).trim();
          try {
            return katex.renderToString(formula, {
              displayMode: false,
              throwOnError: false,
              strict: false,
            });
          } catch {
            return `<span class="text-rose-400 font-mono text-xs">${escapeHtml(formula)}</span>`;
          }
        }

        // Standard text: safely escape HTML entities to prevent XSS
        return part
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;")
          .replace(/\n/g, "<br/>");
      })
      .join("");
  }, [content, block]);

  return (
    <span
      className={`inline-block math-rendered ${className}`}
      dangerouslySetInnerHTML={{ __html: renderedContent }}
    />
  );
};

export default MathRenderer;
