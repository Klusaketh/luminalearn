"use client";

import { useEffect, useId, useRef } from "react";
import { motion } from "framer-motion";
import { ArrowUp, Mic, MicOff, Square } from "lucide-react";
import { cn } from "@/utils/cn";

const MAX_CHARS = 8000;

interface ComposerProps {
  value: string;
  onChange: (value: string) => void;
  onSend: (text: string) => void;
  onStop: () => void;
  streaming: boolean;
  voiceActive: boolean;
  voiceConnecting: boolean;
  onToggleVoice: () => void;
}

/** Message box: Enter sends, Shift+Enter adds a line, the mic starts a live voice conversation. */
export function Composer({ value, onChange, onSend, onStop, streaming, voiceActive, voiceConnecting, onToggleVoice }: ComposerProps) {
  const ref = useRef<HTMLTextAreaElement>(null);
  const hintId = useId();

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  }, [value]);

  const submit = () => {
    const text = value.trim();
    if (!text || text.length > MAX_CHARS) return;
    onSend(text);
    onChange("");
  };

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        submit();
      }}
      className="glass-strong gradient-border-flow flex items-end gap-2 rounded-[1.5rem] p-2"
    >
      <button
        type="button"
        onClick={onToggleVoice}
        aria-pressed={voiceActive}
        aria-label={voiceActive ? "End voice conversation" : "Start voice conversation"}
        disabled={voiceConnecting}
        className={cn(
          "relative flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl outline-none transition-colors focus-visible:ring-2 focus-visible:ring-indigo-300",
          voiceActive ? "bg-cyan-400/20 text-cyan-100 ring-1 ring-cyan-300/40" : "bg-white/[0.05] text-slate-200 hover:bg-white/[0.09]"
        )}
      >
        {voiceActive && (
          <motion.span
            aria-hidden="true"
            className="absolute inset-0 rounded-2xl ring-2 ring-cyan-300/50"
            animate={{ scale: [1, 1.18, 1], opacity: [0.6, 0, 0.6] }}
            transition={{ duration: 1.8, repeat: Infinity }}
          />
        )}
        {voiceActive ? <MicOff className="h-5 w-5" aria-hidden="true" /> : <Mic className="h-5 w-5" aria-hidden="true" />}
      </button>
      <label htmlFor={`${hintId}-input`} className="sr-only">
        Message the tutor
      </label>
      <textarea
        id={`${hintId}-input`}
        ref={ref}
        rows={1}
        value={value}
        maxLength={MAX_CHARS}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
            event.preventDefault();
            submit();
          }
        }}
        aria-describedby={hintId}
        placeholder={voiceActive ? "Talk, or type here and the tutor will answer out loud" : "Ask a question, paste code, or describe where you're stuck"}
        className="max-h-[200px] min-h-[44px] flex-1 resize-none bg-transparent px-1 py-2.5 text-[15px] leading-6 text-white outline-none placeholder:text-slate-500"
      />
      <span id={hintId} className="sr-only">
        Press Enter to send and Shift plus Enter for a new line.
      </span>
      {streaming ? (
        <button
          type="button"
          onClick={onStop}
          aria-label="Stop the reply"
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-white/[0.08] text-white outline-none hover:bg-white/[0.14] focus-visible:ring-2 focus-visible:ring-indigo-300"
        >
          <Square className="h-4 w-4" aria-hidden="true" />
        </button>
      ) : (
        <button
          type="submit"
          aria-label="Send message"
          disabled={!value.trim()}
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,#7C3AED,#0891B2)] text-white shadow-glow outline-none transition-opacity disabled:opacity-40 focus-visible:ring-2 focus-visible:ring-indigo-300"
        >
          <ArrowUp className="h-5 w-5" aria-hidden="true" />
        </button>
      )}
    </form>
  );
}
