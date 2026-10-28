"use client";

import { Suspense, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { PanelRight, RotateCcw } from "lucide-react";
import { useTutorStore, type TutorMessage } from "@/stores/useTutorStore";
import { tutorService, type Modality, type TutorStatus } from "@/services/tutorService";
import { useTutorChat } from "@/hooks/useTutorChat";
import { useVoiceSession } from "@/hooks/useVoiceSession";
import { useNarration } from "@/hooks/useNarration";
import { DialogueFeed } from "@/components/tutor/DialogueFeed";
import { Composer } from "@/components/tutor/Composer";
import { VarkSwitcher } from "@/components/tutor/VarkSwitcher";
import { VoiceStage } from "@/components/tutor/VoiceStage";
import { ContextPanel } from "@/components/tutor/ContextPanel";
import type { MessageActions } from "@/components/tutor/MessageBubble";

const MODALITY_KEY = "lumina_tutor_modality";
const MODALITIES: Modality[] = ["visual", "auditory", "read_write", "kinesthetic"];

const REEXPLAIN: Record<Modality, string> = {
  visual: "Show me that as a diagram",
  auditory: "Talk me through that out loud",
  read_write: "Write that up as structured notes",
  kinesthetic: "Let me learn that hands-on",
};

const STARTERS = [
  { label: "Work through an integral", prompt: "Evaluate $\\int_0^2 (3x^2 - 2x + 1)\\,dx$. I'm not sure where to start." },
  { label: "See recursion as a diagram", prompt: "Explain how recursion works, with a diagram of the call stack." },
  { label: "Debug a slow function", prompt: "Why is this so slow?\n```python\ndef fib(n):\n    if n < 2:\n        return n\n    return fib(n - 1) + fib(n - 2)\n```" },
  { label: "An analogy for Dijkstra", prompt: "Give me an everyday analogy for Dijkstra's shortest path algorithm." },
];

function lastStudentText(messages: TutorMessage[]): string | null {
  for (let i = messages.length - 1; i >= 0; i -= 1) if (messages[i].role === "student") return messages[i].text;
  return null;
}

function TutorWorkspace() {
  const params = useSearchParams();
  const messages = useTutorStore((s) => s.messages);
  const topic = useTutorStore((s) => s.topic);
  const modality = useTutorStore((s) => s.modality);
  const { setTopic, setModality, bumpHintLevel, clear } = useTutorStore.getState();

  const chat = useTutorChat();
  const voice = useVoiceSession();
  const narration = useNarration();
  const [status, setStatus] = useState<TutorStatus | null>(null);
  const [statusLoaded, setStatusLoaded] = useState(false);
  const [draft, setDraft] = useState("");
  const [contextOpen, setContextOpen] = useState(false);
  const narratedRef = useRef<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    tutorService
      .status(controller.signal)
      .then(setStatus)
      .catch(() => setStatus(null))
      .finally(() => !controller.signal.aborted && setStatusLoaded(true));
    return () => controller.abort();
  }, []);

  // Deep links from the quiz ("work through this misconception") and saved style preference.
  useEffect(() => {
    const paramTopic = params.get("topic");
    const question = params.get("q");
    if (paramTopic) useTutorStore.getState().setTopic(paramTopic.slice(0, 150));
    if (question) setDraft(question.slice(0, 2000));
    try {
      const saved = localStorage.getItem(MODALITY_KEY) as Modality | null;
      if (saved && MODALITIES.includes(saved)) useTutorStore.getState().setModality(saved);
    } catch {
      /* storage unavailable (private mode): keep the default */
    }
  }, [params]);

  const persistModality = (next: Modality) => {
    setModality(next);
    try {
      localStorage.setItem(MODALITY_KEY, next);
    } catch {
      /* storage unavailable */
    }
  };

  // Auditory learners hear each finished reply (unless a live voice session is already speaking).
  const last = messages[messages.length - 1];
  useEffect(() => {
    if (modality !== "auditory" || voice.active || !last || last.role !== "tutor" || last.status !== "done") return;
    if (narratedRef.current === last.id) return;
    narratedRef.current = last.id;
    void narration.speak(last.id, last.text);
  }, [last, modality, narration, voice.active]);

  const send = useCallback(
    (text: string) => {
      narration.stop();
      if (voice.active) voice.sendText(text);
      else void chat.send(text);
    },
    [chat, narration, voice]
  );

  const onModalityChange = (next: Modality) => {
    if (next === modality) return;
    persistModality(next);
    const question = lastStudentText(useTutorStore.getState().messages);
    if (question && !chat.isStreaming && !voice.active) {
      void chat.send(`${REEXPLAIN[next]}: ${question}`, { agent: "concept_explainer", modality: next });
    }
  };

  const { send: sendChat } = chat;
  const { speak, stop: stopNarration, speakingId } = narration;
  const actions: MessageActions = useMemo(
    () => ({
      onListen: (message) => void speak(message.id, message.text),
      onStopListening: stopNarration,
      onAnalogy: () => {
        const question = lastStudentText(useTutorStore.getState().messages) ?? topic;
        void sendChat(`Give me an everyday analogy for this: ${question}`, { agent: "analogy_specialist" });
      },
      onNextHint: () => {
        bumpHintLevel();
        void sendChat("I'm still stuck. Can I have the next hint?", { agent: "socratic_tutor" });
      },
      onRevealHint: bumpHintLevel,
      speakingId,
    }),
    [bumpHintLevel, sendChat, speak, stopNarration, speakingId, topic]
  );

  const activeAgent = [...messages].reverse().find((m) => m.role === "tutor" && m.route)?.route?.agent;
  const context = (onClose?: () => void) => (
    <ContextPanel
      topic={topic}
      onTopicChange={setTopic}
      activeAgent={activeAgent}
      status={status}
      statusLoaded={statusLoaded}
      onClose={onClose}
    />
  );

  const empty = (
    <div className="flex flex-col items-center px-2 pb-6 pt-2 text-center sm:pt-14">
      <h2 className="font-display text-3xl leading-tight text-white sm:text-5xl">What are you working on?</h2>
      <p className="mt-3 max-w-md text-[15px] leading-relaxed text-slate-400">
        Ask anything. The faculty answers with the question that gets you unstuck, never with the answer itself.
      </p>
      <div className="mt-8 grid w-full max-w-xl grid-cols-1 gap-2.5 sm:grid-cols-2">
        {STARTERS.map((starter, index) => (
          <motion.button
            key={starter.label}
            type="button"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + index * 0.06, type: "spring", stiffness: 260, damping: 26 }}
            onClick={() => send(starter.prompt)}
            className="glass group rounded-2xl px-4 py-3.5 text-left outline-none transition-colors hover:border-white/20 focus-visible:ring-2 focus-visible:ring-indigo-300"
          >
            <span className="text-sm font-semibold text-slate-100 group-hover:text-white">{starter.label}</span>
          </motion.button>
        ))}
      </div>
    </div>
  );

  return (
    <main className="mx-auto grid h-[calc(100vh-4rem)] w-full max-w-[1680px] grid-cols-1 gap-3 p-3 supports-[height:100dvh]:h-[calc(100dvh-4rem)] sm:gap-4 sm:p-4 lg:grid-cols-[19rem_minmax(0,1fr)] 2xl:grid-cols-[20rem_minmax(0,1fr)_21rem]">
      <h1 className="sr-only">Socratic AI tutor</h1>
      <div className="hidden min-h-0 lg:block">
        <VoiceStage voice={voice} />
      </div>

      <section aria-label="Tutoring dialogue" className="glass relative flex min-h-0 flex-col overflow-hidden rounded-3xl shadow-glass">
        <div className="flex items-center gap-2 border-b border-white/[0.06] px-3 py-2.5 sm:px-4">
          <div className="min-w-0 flex-1 lg:hidden">
            <VoiceStage voice={voice} compact />
          </div>
          <div className="ml-auto flex items-center gap-1.5">
            {messages.length > 0 && (
              <button
                type="button"
                onClick={() => {
                  chat.stop();
                  narration.stop();
                  clear();
                }}
                className="flex items-center gap-1.5 rounded-xl px-2.5 py-2 text-xs text-slate-300 ring-1 ring-white/10 hover:bg-white/[0.05] hover:text-white"
              >
                <RotateCcw className="h-3.5 w-3.5" aria-hidden="true" />
                <span className="hidden sm:inline">New conversation</span>
              </button>
            )}
            <button
              type="button"
              onClick={() => setContextOpen(true)}
              className="flex items-center gap-1.5 rounded-xl px-2.5 py-2 text-xs text-slate-300 ring-1 ring-white/10 hover:bg-white/[0.05] hover:text-white 2xl:hidden"
              aria-label="Show learning context"
            >
              <PanelRight className="h-3.5 w-3.5" aria-hidden="true" />
              <span className="hidden sm:inline">Context</span>
            </button>
          </div>
        </div>

        <DialogueFeed messages={messages} actions={actions} empty={empty} />

        <div className="space-y-2.5 border-t border-white/[0.06] p-3 sm:p-4">
          <div className="flex justify-center">
            <VarkSwitcher value={modality} onChange={onModalityChange} />
          </div>
          <div className="mx-auto max-w-3xl">
            <Composer
              value={draft}
              onChange={setDraft}
              onSend={send}
              onStop={chat.stop}
              streaming={chat.isStreaming}
              voiceActive={voice.active}
              voiceConnecting={voice.state === "connecting"}
              onToggleVoice={() => (voice.active ? voice.stop() : void voice.start())}
            />
          </div>
        </div>
      </section>

      <div className="hidden min-h-0 2xl:block">{context()}</div>

      <AnimatePresence>
        {contextOpen && (
          <motion.div className="fixed inset-0 z-[60] 2xl:hidden" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <button type="button" aria-label="Close learning context" className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setContextOpen(false)} />
            <motion.div
              role="dialog"
              aria-modal="true"
              aria-label="Learning context"
              className="absolute inset-y-0 right-0 w-full max-w-sm p-3"
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", stiffness: 320, damping: 34 }}
            >
              {context(() => setContextOpen(false))}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
}

export default function TutorPage() {
  return (
    <Suspense fallback={<div className="h-[calc(100vh-4rem)]" aria-busy="true" />}>
      <TutorWorkspace />
    </Suspense>
  );
}
