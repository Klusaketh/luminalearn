"use client";

import React from "react";
import CodeMirror from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import { oneDark } from "@codemirror/theme-one-dark";

const EXTENSIONS = [python()];

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  /** Called on Ctrl+Enter / Cmd+Enter. */
  onRun: () => void;
  label: string;
}

/** Python editor (CodeMirror 6). Client-only: import it with next/dynamic and `ssr: false`. */
export default function CodeEditor({ value, onChange, onRun, label }: CodeEditorProps) {
  return (
    <div
      className="overflow-hidden rounded-2xl ring-1 ring-white/[0.08] [&_.cm-editor]:bg-[#0b0b14] [&_.cm-gutters]:bg-[#0b0b14] [&_.cm-scroller]:font-mono [&_.cm-scroller]:text-[14px]"
      onKeyDownCapture={(event) => {
        if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
          event.preventDefault();
          onRun();
        }
      }}
    >
      <CodeMirror
        value={value}
        onChange={onChange}
        theme={oneDark}
        extensions={EXTENSIONS}
        height="420px"
        aria-label={label}
        basicSetup={{ foldGutter: false, highlightActiveLine: true, autocompletion: true, tabSize: 4 }}
        indentWithTab
      />
    </div>
  );
}
