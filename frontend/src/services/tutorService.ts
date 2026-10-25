import { API_BASE, apiFetch, readErrorDetail } from "./apiClient";

export type AgentName = "socratic_tutor" | "concept_explainer" | "analogy_specialist" | "code_diagnostic";
export type Modality = "visual" | "auditory" | "read_write" | "kinesthetic";
export type LabWidget = "recursion" | "gradient_descent" | "bayes";

export interface RouteInfo {
  agent: AgentName;
  display_name: string;
  summary: string;
  confidence: number;
  rationale: string;
  signals: string[];
  hint_tier: number;
  modality: Modality;
}

export interface Citation {
  index: number;
  label: string;
  source: string;
  section: string;
  page: number | null;
  relevance: number;
  excerpt: string;
}

export interface HintItem {
  tier: number;
  title: string;
  text: string;
}

export interface CodeFindingInfo {
  severity: "error" | "warning" | "info";
  line: number | null;
  title: string;
  detail: string;
  question: string;
}

export interface DiagnosticsInfo {
  language: string;
  time_complexity: string;
  space_complexity: string;
  rationale: string;
  findings: CodeFindingInfo[];
}

export interface DoneInfo {
  text: string;
  agent: AgentName | null;
  engine: string;
  grounded?: boolean;
  hint_tier?: number;
  guardrail_redactions?: number;
  prompt_version?: string;
  latency_ms?: number;
  error?: string;
}

export type TutorStreamEvent =
  | { type: "route"; data: RouteInfo }
  | { type: "citations"; data: { items: Citation[]; grounded: boolean } }
  | { type: "diagnostics"; data: DiagnosticsInfo }
  | { type: "delta"; data: { text: string } }
  | { type: "hints"; data: { start_tier: number; items: HintItem[] } }
  | { type: "interactive"; data: { widget: LabWidget } }
  | { type: "done"; data: DoneInfo };

export interface AgentProfile {
  name: AgentName;
  display_name: string;
  summary: string;
}

export interface TutorStatus {
  llm_enabled: boolean;
  speech_enabled: boolean;
  prompt_version: string;
  agents: AgentProfile[];
  voice_websocket_path: string;
}

export interface TutorChatPayload {
  message: string;
  topic?: string | null;
  modality?: Modality;
  hint_level?: number;
  agent?: AgentName | null;
  history?: Array<{ role: "student" | "tutor"; text: string }>;
}

export class TutorRequestError extends Error {
  constructor(message: string, public readonly status: number, public readonly retryAfterSeconds?: number) {
    super(message);
    this.name = "TutorRequestError";
  }
}

const EVENT_TYPES = new Set(["route", "citations", "diagnostics", "delta", "hints", "interactive", "done"]);

/** Parses one `event: ...\ndata: ...` SSE frame. */
function parseFrame(frame: string): TutorStreamEvent | null {
  let type = "";
  const data: string[] = [];
  for (const line of frame.split("\n")) {
    if (line.startsWith("event:")) type = line.slice(6).trim();
    else if (line.startsWith("data:")) data.push(line.slice(5).trimStart());
  }
  if (!EVENT_TYPES.has(type) || data.length === 0) return null;
  try {
    return { type, data: JSON.parse(data.join("\n")) } as TutorStreamEvent;
  } catch {
    return null;
  }
}

const JSON_HEADERS = { "Content-Type": "application/json" };

class TutorService {
  /** ws(s):// URL of the voice endpoint on this site; next.config.js forwards it to the backend. */
  voiceSocketUrl(): string {
    const scheme = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${scheme}//${window.location.host}${API_BASE}/voice/session`;
  }

  async status(signal?: AbortSignal): Promise<TutorStatus> {
    const res = await apiFetch(`${API_BASE}/tutor/status`, { signal });
    if (!res.ok) throw new TutorRequestError("Tutor status unavailable.", res.status);
    return res.json();
  }

  /** Streams one tutoring turn as typed events (POST + Server-Sent Events over fetch). */
  async *streamChat(payload: TutorChatPayload, signal?: AbortSignal): AsyncGenerator<TutorStreamEvent> {
    const res = await apiFetch(`${API_BASE}/tutor/chat/stream`, {
      method: "POST",
      headers: { ...JSON_HEADERS, Accept: "text/event-stream" },
      body: JSON.stringify(payload),
      signal,
    });
    if (!res.ok || !res.body) {
      const retryAfter = Number(res.headers.get("Retry-After")) || undefined;
      const detail = await readErrorDetail(res, "The tutor could not answer that request.");
      throw new TutorRequestError(detail, res.status, retryAfter);
    }
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    try {
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, "\n");
        let boundary = buffer.indexOf("\n\n");
        while (boundary !== -1) {
          const event = parseFrame(buffer.slice(0, boundary));
          buffer = buffer.slice(boundary + 2);
          if (event) yield event;
          boundary = buffer.indexOf("\n\n");
        }
      }
      const last = parseFrame(buffer);
      if (last) yield last;
    } finally {
      reader.releaseLock();
    }
  }

  /** Server voice (Gemini TTS) as a WAV blob. Throws when the server voice is unavailable. */
  async speak(text: string, signal?: AbortSignal): Promise<Blob> {
    const res = await apiFetch(`${API_BASE}/tutor/speak`, {
      method: "POST",
      headers: JSON_HEADERS,
      body: JSON.stringify({ text: text.slice(0, 1500) }),
      signal,
    });
    if (!res.ok) throw new TutorRequestError("Server voice unavailable.", res.status);
    return res.blob();
  }
}

export const tutorService = new TutorService();
