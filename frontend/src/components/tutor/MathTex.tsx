"use client";

import { useMemo } from "react";
import katex from "katex";

/** KaTeX renderer; KaTeX escapes its input and `trust` stays off, so model output is safe here. */
export function MathTex({ value, display = false }: { value: string; display?: boolean }) {
  const html = useMemo(
    () => katex.renderToString(value, { displayMode: display, throwOnError: false, strict: "ignore", output: "htmlAndMathml" }),
    [value, display]
  );
  if (display) {
    return <div className="my-3 overflow-x-auto rounded-2xl bg-white/[0.025] px-3 py-1" dangerouslySetInnerHTML={{ __html: html }} />;
  }
  return <span dangerouslySetInnerHTML={{ __html: html }} />;
}
