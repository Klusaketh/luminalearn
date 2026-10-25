"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Highlight, type PrismTheme } from "prism-react-renderer";
import { Check, Copy } from "lucide-react";

const AURORA_THEME: PrismTheme = {
  plain: { color: "#E4E6F2", backgroundColor: "transparent" },
  styles: [
    { types: ["comment", "prolog", "doctype", "cdata"], style: { color: "#8A91B0", fontStyle: "italic" } },
    { types: ["punctuation"], style: { color: "#A9AFCA" } },
    { types: ["keyword", "builtin", "important", "atrule"], style: { color: "#C4B5FD" } },
    { types: ["function", "class-name"], style: { color: "#67E8F9" } },
    { types: ["string", "char", "attr-value", "regex", "inserted"], style: { color: "#86EFAC" } },
    { types: ["number", "boolean", "constant", "symbol"], style: { color: "#FCD34D" } },
    { types: ["operator", "entity", "url"], style: { color: "#F9A8D4" } },
    { types: ["variable", "parameter"], style: { color: "#F5F3FF" } },
    { types: ["tag", "selector", "property"], style: { color: "#93C5FD" } },
    { types: ["deleted"], style: { color: "#FDA4AF" } },
  ],
};

const LANGUAGE_ALIASES: Record<string, string> = {
  py: "python",
  js: "javascript",
  ts: "typescript",
  sh: "bash",
  shell: "bash",
  "c++": "cpp",
  java: "clike",
  csharp: "clike",
  cs: "clike",
};

const LANGUAGE_LABELS: Record<string, string> = {
  python: "Python",
  javascript: "JavaScript",
  typescript: "TypeScript",
  jsx: "JSX",
  tsx: "TSX",
  cpp: "C++",
  c: "C",
  clike: "Java",
  rust: "Rust",
  go: "Go",
  sql: "SQL",
  json: "JSON",
  css: "CSS",
  bash: "Shell",
  markup: "HTML",
  yaml: "YAML",
};

async function copyText(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch {
    /* fall through to the legacy path */
  }
  const area = document.createElement("textarea");
  area.value = text;
  area.setAttribute("readonly", "");
  area.style.position = "fixed";
  area.style.opacity = "0";
  document.body.appendChild(area);
  area.select();
  const ok = document.execCommand("copy");
  document.body.removeChild(area);
  return ok;
}

export function CodeBlock({ code, language }: { code: string; language?: string }) {
  const [copied, setCopied] = useState(false);
  const raw = (language || "").toLowerCase();
  const lang = LANGUAGE_ALIASES[raw] ?? (raw || "plain");
  const label = LANGUAGE_LABELS[raw === "java" ? "clike" : lang] ?? (raw ? raw.toUpperCase() : "Code");

  const onCopy = async () => {
    if (await copyText(code)) {
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    }
  };

  return (
    <figure className="my-3 overflow-hidden rounded-2xl border border-white/[0.08] bg-[#080912]/90 shadow-card">
      <figcaption className="flex items-center justify-between border-b border-white/[0.06] px-4 py-2">
        <span className="rounded-md bg-indigo-500/15 px-2 py-0.5 font-mono text-[11px] font-medium text-indigo-200">{label}</span>
        <button
          type="button"
          onClick={onCopy}
          className="flex items-center gap-1.5 rounded-lg px-2 py-1 text-xs text-slate-300 outline-none transition-colors hover:bg-white/[0.06] hover:text-white focus-visible:ring-2 focus-visible:ring-indigo-300"
          aria-label={copied ? "Code copied" : "Copy code"}
        >
          <AnimatePresence mode="wait" initial={false}>
            {copied ? (
              <motion.span key="done" initial={{ scale: 0.4, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.4, opacity: 0 }} className="flex items-center gap-1.5 text-emerald-300">
                <Check className="h-3.5 w-3.5" aria-hidden="true" /> Copied
              </motion.span>
            ) : (
              <motion.span key="copy" initial={{ scale: 0.4, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.4, opacity: 0 }} className="flex items-center gap-1.5">
                <Copy className="h-3.5 w-3.5" aria-hidden="true" /> Copy
              </motion.span>
            )}
          </AnimatePresence>
        </button>
        <span className="sr-only" aria-live="polite">
          {copied ? "Copied to clipboard" : ""}
        </span>
      </figcaption>
      <Highlight code={code} language={lang} theme={AURORA_THEME}>
        {({ className, style, tokens, getLineProps, getTokenProps }) => (
          <pre className={`${className} overflow-x-auto py-3 font-mono text-[13px] leading-6`} style={style}>
            <code>
              {tokens.map((line, i) => {
                const lineProps = getLineProps({ line });
                return (
                  <div key={i} {...lineProps} className={`${lineProps.className} grid grid-cols-[2.75rem_1fr] pr-4`}>
                    <span aria-hidden="true" className="select-none pr-3 text-right text-slate-600">
                      {i + 1}
                    </span>
                    <span>
                      {line.map((token, key) => (
                        <span key={key} {...getTokenProps({ token })} />
                      ))}
                    </span>
                  </div>
                );
              })}
            </code>
          </pre>
        )}
      </Highlight>
    </figure>
  );
}
