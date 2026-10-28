import { create } from "zustand";
import type {
  Citation,
  DiagnosticsInfo,
  HintItem,
  LabWidget,
  Modality,
  RouteInfo,
} from "@/services/tutorService";

export type MessageStatus = "streaming" | "done" | "error" | "interrupted";
export type VoiceState = "off" | "connecting" | "listening" | "thinking" | "speaking";

export interface TutorMessage {
  id: string;
  role: "student" | "tutor";
  text: string;
  status: MessageStatus;
  channel: "chat" | "voice";
  route?: RouteInfo;
  citations?: Citation[];
  grounded?: boolean;
  diagnostics?: DiagnosticsInfo;
  hints?: { startTier: number; items: HintItem[] };
  widget?: LabWidget;
  engine?: string;
  latencyMs?: number;
  redactions?: number;
  error?: string;
}

interface TutorState {
  messages: TutorMessage[];
  topic: string;
  modality: Modality;
  /** Extra hints requested in the current thread; climbs the Socratic hint ladder. */
  hintLevel: number;
  voiceState: VoiceState;
  addMessage: (message: TutorMessage) => void;
  patchMessage: (id: string, patch: Partial<TutorMessage>) => void;
  appendText: (id: string, text: string) => void;
  setTopic: (topic: string) => void;
  setModality: (modality: Modality) => void;
  bumpHintLevel: () => void;
  setVoiceState: (state: VoiceState) => void;
  clear: () => void;
}

let counter = 0;
export function newMessageId(): string {
  counter += 1;
  const random = typeof crypto !== "undefined" && "randomUUID" in crypto ? crypto.randomUUID() : Math.random().toString(36).slice(2);
  return `${counter}-${random}`;
}

export const useTutorStore = create<TutorState>((set) => ({
  messages: [],
  topic: "",
  modality: "read_write",
  hintLevel: 0,
  voiceState: "off",

  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  patchMessage: (id, patch) =>
    set((state) => ({ messages: state.messages.map((m) => (m.id === id ? { ...m, ...patch } : m)) })),
  appendText: (id, text) =>
    set((state) => ({ messages: state.messages.map((m) => (m.id === id ? { ...m, text: m.text + text } : m)) })),
  setTopic: (topic) => set({ topic, hintLevel: 0 }),
  setModality: (modality) => set({ modality }),
  bumpHintLevel: () => set((state) => ({ hintLevel: Math.min(3, state.hintLevel + 1) })),
  setVoiceState: (voiceState) => set({ voiceState }),
  clear: () => set({ messages: [], hintLevel: 0 }),
}));

/** Recent completed turns, replayed to the faculty for conversational context. */
export function historyForRequest(messages: TutorMessage[], limit = 10): Array<{ role: "student" | "tutor"; text: string }> {
  return messages
    .filter((m) => m.text.trim() && m.status !== "error")
    .slice(-limit)
    .map((m) => ({ role: m.role, text: m.text.slice(0, 6000) }));
}
