"use client";

import { useCallback, useEffect, useLayoutEffect, useRef, useState, type ReactNode } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { ArrowDown } from "lucide-react";
import type { TutorMessage } from "@/stores/useTutorStore";
import { MessageBubble, type MessageActions } from "@/components/tutor/MessageBubble";
import { plainSpeech } from "@/hooks/useNarration";

const PIN_THRESHOLD_PX = 96;
// Layout effects only exist in the browser; avoid React's SSR warning.
const useIsomorphicLayoutEffect = typeof window !== "undefined" ? useLayoutEffect : useEffect;

interface DialogueFeedProps {
  messages: TutorMessage[];
  actions: MessageActions;
  empty: ReactNode;
}

/**
 * The conversation log. Auto-scroll is locked to the bottom only while the learner is
 * already there; scrolling up to re-read pauses it and offers a "jump to latest" pill.
 * Completed replies are announced through a polite live region, never token by token.
 */
export function DialogueFeed({ messages, actions, empty }: DialogueFeedProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const pinnedRef = useRef(true);
  const [showJump, setShowJump] = useState(false);
  const [announcement, setAnnouncement] = useState("");
  const reduceMotion = useReducedMotion();
  const last = messages[messages.length - 1];
  const contentKey = `${messages.length}:${last?.text.length ?? 0}:${last?.status ?? ""}`;

  const onScroll = () => {
    const el = scrollRef.current;
    if (!el) return;
    const pinned = el.scrollHeight - el.scrollTop - el.clientHeight < PIN_THRESHOLD_PX;
    pinnedRef.current = pinned;
    if (pinned) setShowJump(false);
  };

  const scrollToBottom = useCallback(
    (smooth: boolean) => {
      const el = scrollRef.current;
      if (!el) return;
      el.scrollTo({ top: el.scrollHeight, behavior: smooth && !reduceMotion ? "smooth" : "auto" });
    },
    [reduceMotion]
  );

  const hasMessages = messages.length > 0;
  useIsomorphicLayoutEffect(() => {
    if (!hasMessages) return; // the empty state reads from the top
    if (pinnedRef.current) scrollToBottom(false);
    else setShowJump(true);
  }, [contentKey, hasMessages, scrollToBottom]);

  // Typewriter reveals keep growing the content after the store settles: follow while pinned.
  useEffect(() => {
    const content = scrollRef.current?.firstElementChild;
    if (!content) return;
    const observer = new ResizeObserver(() => {
      if (pinnedRef.current && (scrollRef.current?.querySelector("article, p.whitespace-pre-wrap") ?? null)) scrollToBottom(false);
    });
    observer.observe(content);
    return () => observer.disconnect();
  }, [scrollToBottom]);

  useEffect(() => {
    if (last?.role === "tutor" && last.status === "done" && last.text) {
      const who = last.route?.display_name ?? "The tutor";
      setAnnouncement(`${who} replied: ${plainSpeech(last.text).slice(0, 600)}`);
    } else if (last?.role === "tutor" && last.status === "streaming" && !last.text) {
      setAnnouncement("The tutor is thinking.");
    }
  }, [last?.id, last?.status, last?.role, last?.text, last?.route?.display_name]);

  return (
    <div className="relative min-h-0 flex-1">
      <div
        ref={scrollRef}
        onScroll={onScroll}
        role="log"
        aria-label="Conversation with the tutor"
        aria-live="off"
        className="h-full overflow-y-auto overscroll-contain px-3 pb-6 pt-4 sm:px-6"
      >
        <div className="mx-auto flex max-w-3xl flex-col gap-4">
          {messages.length === 0 ? empty : messages.map((message) => <MessageBubble key={message.id} message={message} actions={actions} />)}
        </div>
      </div>
      <div className="sr-only" aria-live="polite" aria-atomic="true">
        {announcement}
      </div>
      <AnimatePresence>
        {showJump && (
          <motion.button
            type="button"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            onClick={() => {
              pinnedRef.current = true;
              setShowJump(false);
              scrollToBottom(true);
            }}
            className="glass-strong absolute bottom-3 left-1/2 flex -translate-x-1/2 items-center gap-1.5 rounded-full px-3.5 py-2 text-xs font-medium text-slate-100 shadow-glow"
          >
            <ArrowDown className="h-3.5 w-3.5" aria-hidden="true" /> Jump to latest
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  );
}
