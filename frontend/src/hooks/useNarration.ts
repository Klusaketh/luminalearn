"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { tutorService } from "@/services/tutorService";

/** Strips markdown, code and math so narration reads naturally. */
export function plainSpeech(markdown: string): string {
  return markdown
    .replace(/```[\s\S]*?(```|$)/g, " There's a code example on screen. ")
    .replace(/\$\$?[^$]+\$\$?/g, " the expression on screen ")
    .replace(/`([^`]*)`/g, "$1")
    .replace(/\[(\d+(?:\s*,\s*\d+)*)\]/g, "")
    .replace(/[*_#>|~]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

/**
 * Speaks tutor messages: studio-quality server speech when available, the browser's speech
 * synthesis otherwise. One narration plays at a time.
 */
export function useNarration() {
  const [speakingId, setSpeakingId] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const urlRef = useRef<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const serverVoiceRef = useRef(true);

  const stop = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    audioRef.current?.pause();
    if (urlRef.current) URL.revokeObjectURL(urlRef.current);
    urlRef.current = null;
    if (typeof window !== "undefined") window.speechSynthesis?.cancel();
    setSpeakingId(null);
  }, []);

  const speakWithBrowser = useCallback((id: string, text: string) => {
    const synth = window.speechSynthesis;
    if (!synth) {
      setSpeakingId(null);
      return;
    }
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.02;
    utterance.onend = () => setSpeakingId((current) => (current === id ? null : current));
    utterance.onerror = utterance.onend;
    synth.cancel();
    synth.speak(utterance);
  }, []);

  const speak = useCallback(
    async (id: string, markdown: string) => {
      stop();
      const text = plainSpeech(markdown);
      if (!text) return;
      setSpeakingId(id);
      if (serverVoiceRef.current) {
        const controller = new AbortController();
        abortRef.current = controller;
        try {
          const blob = await tutorService.speak(text, controller.signal);
          const url = URL.createObjectURL(blob);
          urlRef.current = url;
          const audio = audioRef.current ?? new Audio();
          audioRef.current = audio;
          audio.src = url;
          audio.onended = () => setSpeakingId((current) => (current === id ? null : current));
          await audio.play();
          return;
        } catch {
          if (controller.signal.aborted) return;
          serverVoiceRef.current = false; // server voice is offline: stop asking for this session
        }
      }
      speakWithBrowser(id, text);
    },
    [speakWithBrowser, stop]
  );

  useEffect(() => stop, [stop]);

  return useMemo(() => ({ speak, stop, speakingId }), [speak, stop, speakingId]);
}
