"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { BackendUnavailableError } from "@/services/apiClient";
import { tutorService, TutorRequestError, type AgentName, type Modality } from "@/services/tutorService";
import { historyForRequest, newMessageId, useTutorStore } from "@/stores/useTutorStore";

export interface SendOptions {
  agent?: AgentName;
  modality?: Modality;
}

/** Streams Socratic tutoring turns into the shared dialogue store. */
export function useTutorChat() {
  const abortRef = useRef<AbortController | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);

  useEffect(() => () => abortRef.current?.abort(), []);

  const send = useCallback(async (text: string, options: SendOptions = {}) => {
    const message = text.trim();
    if (!message) return;
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    const store = useTutorStore.getState();
    const history = historyForRequest(store.messages);
    const modality = options.modality ?? store.modality;
    store.addMessage({ id: newMessageId(), role: "student", text: message, status: "done", channel: "chat" });
    const replyId = newMessageId();
    store.addMessage({ id: replyId, role: "tutor", text: "", status: "streaming", channel: "chat" });
    setIsStreaming(true);

    const { patchMessage, appendText } = useTutorStore.getState();
    try {
      const events = tutorService.streamChat(
        {
          message,
          topic: store.topic.trim() || null,
          modality,
          hint_level: store.hintLevel,
          agent: options.agent ?? null,
          history,
        },
        controller.signal
      );
      for await (const event of events) {
        switch (event.type) {
          case "route":
            patchMessage(replyId, { route: event.data });
            break;
          case "citations":
            patchMessage(replyId, { citations: event.data.items, grounded: event.data.grounded });
            break;
          case "diagnostics":
            patchMessage(replyId, { diagnostics: event.data });
            break;
          case "delta":
            appendText(replyId, event.data.text);
            break;
          case "hints":
            patchMessage(replyId, { hints: { startTier: event.data.start_tier, items: event.data.items } });
            break;
          case "interactive":
            patchMessage(replyId, { widget: event.data.widget });
            break;
          case "done":
            patchMessage(replyId, {
              status: event.data.error ? "error" : "done",
              error: event.data.error,
              engine: event.data.engine,
              latencyMs: event.data.latency_ms,
              redactions: event.data.guardrail_redactions,
            });
            break;
        }
      }
      const final = useTutorStore.getState().messages.find((m) => m.id === replyId);
      if (final?.status === "streaming") patchMessage(replyId, { status: "done" });
    } catch (error) {
      if (controller.signal.aborted) {
        patchMessage(replyId, { status: "interrupted" });
      } else if (error instanceof TutorRequestError && error.status === 429) {
        patchMessage(replyId, {
          status: "error",
          error: `You've reached the tutoring limit for now. Try again in about ${Math.ceil((error.retryAfterSeconds ?? 60) / 60)} minute(s).`,
        });
      } else if (error instanceof TutorRequestError || error instanceof BackendUnavailableError) {
        patchMessage(replyId, { status: "error", error: error.message });
      } else {
        patchMessage(replyId, {
          status: "error",
          error: "The connection to the tutor dropped mid-answer. Send your message again.",
        });
      }
    } finally {
      if (abortRef.current === controller) {
        abortRef.current = null;
        setIsStreaming(false);
      }
    }
  }, []);

  const stop = useCallback(() => abortRef.current?.abort(), []);

  return useMemo(() => ({ send, stop, isStreaming }), [send, stop, isStreaming]);
}
