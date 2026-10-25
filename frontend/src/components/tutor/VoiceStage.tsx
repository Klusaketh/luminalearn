"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Hand, Mic, MicOff } from "lucide-react";
import type { VoiceSession } from "@/hooks/useVoiceSession";
import type { VoiceState } from "@/stores/useTutorStore";
import { VoiceOrb, type OrbMode } from "@/components/tutor/VoiceOrb";
import { GlassPanel } from "@/components/ui/GlassPanel";
import { SegmentedControl } from "@/components/ui/SegmentedControl";
import { cn } from "@/utils/cn";

const STATE_COPY: Record<VoiceState, { title: string; hint: string }> = {
  off: { title: "Talk it through", hint: "Tap the microphone and think out loud. The tutor answers with a question." },
  connecting: { title: "Connecting", hint: "Allow microphone access when your browser asks." },
  listening: { title: "Listening", hint: "Speak naturally and pause when you're done." },
  thinking: { title: "Thinking", hint: "The faculty is choosing who should answer." },
  speaking: { title: "Speaking", hint: "Start talking at any time to interrupt." },
};

const ORB_MODE: Record<VoiceState, OrbMode> = {
  off: "idle",
  connecting: "thinking",
  listening: "listening",
  thinking: "thinking",
  speaking: "speaking",
};

const VOICE_OPTIONS = [
  { value: "server", label: "Studio voice", description: "Gemini speech, streamed from the server" },
  { value: "browser", label: "Instant voice", description: "Your browser's built-in speech, no delay" },
] as const;

export function VoiceStage({ voice, compact = false }: { voice: VoiceSession; compact?: boolean }) {
  const copy = STATE_COPY[voice.state];
  const mode = ORB_MODE[voice.state];
  const analyser = voice.state === "listening" ? voice.micAnalyser : voice.state === "speaking" && voice.ttsMode === "server" ? voice.playbackAnalyser : null;
  const toggle = () => (voice.active ? voice.stop() : void voice.start());

  if (compact) {
    return (
      <GlassPanel className="flex items-center gap-3 rounded-[1.5rem] p-2.5 pr-3">
        <VoiceOrb mode={mode} analyser={analyser} className="h-16 w-16 shrink-0" />
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold text-white">{copy.title}</p>
          <p className="truncate text-xs text-slate-400">{voice.partial || voice.error || copy.hint}</p>
        </div>
        {voice.state === "speaking" && (
          <button type="button" onClick={voice.interrupt} className="rounded-xl px-2.5 py-2 text-xs text-slate-200 ring-1 ring-white/10" aria-label="Interrupt the tutor">
            <Hand className="h-4 w-4" aria-hidden="true" />
          </button>
        )}
        <button
          type="button"
          onClick={toggle}
          disabled={voice.state === "connecting"}
          aria-pressed={voice.active}
          aria-label={voice.active ? "End voice conversation" : "Start voice conversation"}
          className={cn(
            "flex h-11 w-11 items-center justify-center rounded-2xl outline-none focus-visible:ring-2 focus-visible:ring-indigo-300",
            voice.active ? "bg-rose-500/20 text-rose-100 ring-1 ring-rose-300/40" : "bg-[linear-gradient(135deg,#7C3AED,#0891B2)] text-white shadow-glow"
          )}
        >
          {voice.active ? <MicOff className="h-5 w-5" aria-hidden="true" /> : <Mic className="h-5 w-5" aria-hidden="true" />}
        </button>
      </GlassPanel>
    );
  }

  return (
    <GlassPanel as="section" aria-label="Voice tutor" className="flex h-full min-h-0 flex-col items-center overflow-y-auto p-5 text-center">
      <div className="relative aspect-square w-full max-w-[17rem]">
        <VoiceOrb mode={mode} analyser={analyser} className="h-full w-full" />
      </div>
      <AnimatePresence mode="wait">
        <motion.div key={voice.state} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }} transition={{ duration: 0.25 }}>
          <h2 className="font-display text-3xl text-white">{copy.title}</h2>
          <p className="mx-auto mt-1 max-w-[16rem] text-sm leading-relaxed text-slate-400">{copy.hint}</p>
        </motion.div>
      </AnimatePresence>
      <p className="mt-3 min-h-[2.5rem] max-w-[16rem] text-sm italic text-cyan-100/90">{voice.partial}</p>

      <div className="mt-2 flex items-center gap-3">
        <motion.button
          type="button"
          onClick={toggle}
          disabled={voice.state === "connecting"}
          aria-pressed={voice.active}
          aria-label={voice.active ? "End voice conversation" : "Start voice conversation"}
          whileTap={{ scale: 0.94 }}
          className={cn(
            "relative flex h-16 w-16 items-center justify-center rounded-full outline-none transition-colors focus-visible:ring-2 focus-visible:ring-indigo-300 focus-visible:ring-offset-2 focus-visible:ring-offset-space-950",
            voice.active ? "bg-rose-500/20 text-rose-100 ring-1 ring-rose-300/40" : "bg-[linear-gradient(135deg,#7C3AED,#0891B2)] text-white shadow-glow"
          )}
        >
          {!voice.active && (
            <motion.span
              aria-hidden="true"
              className="absolute inset-0 rounded-full ring-2 ring-indigo-300/50"
              animate={{ scale: [1, 1.25], opacity: [0.7, 0] }}
              transition={{ duration: 2.2, repeat: Infinity, ease: "easeOut" }}
            />
          )}
          {voice.active ? <MicOff className="h-6 w-6" aria-hidden="true" /> : <Mic className="h-6 w-6" aria-hidden="true" />}
        </motion.button>
        <AnimatePresence>
          {voice.state === "speaking" && (
            <motion.button
              type="button"
              onClick={voice.interrupt}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="flex items-center gap-1.5 rounded-full px-3.5 py-2 text-xs font-semibold text-slate-100 ring-1 ring-white/15 hover:bg-white/[0.06]"
            >
              <Hand className="h-3.5 w-3.5" aria-hidden="true" /> Interrupt
            </motion.button>
          )}
        </AnimatePresence>
      </div>

      {voice.capabilities?.server_tts && (
        <div className="mt-5">
          <SegmentedControl label="Tutor voice" size="sm" options={VOICE_OPTIONS} value={voice.ttsMode} onChange={voice.setTtsPreference} />
        </div>
      )}
      <div className="mt-auto pt-5 text-[11px] leading-relaxed text-slate-500">
        {voice.sttMode === "browser" && <p>Speech is recognized by your browser.</p>}
        {voice.sttMode === "server" && <p>Speech is transcribed on the server, one turn at a time.</p>}
        {voice.error && (
          <p role="alert" className="mt-2 rounded-xl bg-rose-500/10 px-3 py-2 text-xs text-rose-200 ring-1 ring-rose-400/25">
            {voice.error}
          </p>
        )}
      </div>
    </GlassPanel>
  );
}
