/**
 * The single door to the LuminaLearn API.
 *
 * Requests go to this site's own origin (`/api/v1/...`). The Next.js server forwards them to the
 * backend (src/app/api/v1/[...path]/route.ts), so the browser never needs the backend's port and
 * CORS never applies. On top of `fetch`, the client:
 *  - attaches the learner's access token, renewing it just before it expires (it lives 15 minutes),
 *  - refreshes and retries once if the server still rejects the token (e.g. it was revoked),
 *  - turns "the server is unreachable" into one clear error instead of the browser's "Failed to fetch",
 *  - reports reachability so the app can show one banner and recover when the server is back.
 */

export const API_BASE = "/api/v1";

const UNAVAILABLE_MESSAGE = "Can't reach the LuminaLearn server right now. It may be restarting; this page retries automatically.";

/** The backend could not be reached (not running, restarting, or the network dropped). */
export class BackendUnavailableError extends Error {
  constructor(message = UNAVAILABLE_MESSAGE) {
    super(message);
    this.name = "BackendUnavailableError";
  }
}

/** Connects the client to the auth store without an import cycle (the store registers itself). */
export interface SessionBridge {
  /** The token to send, renewed first when it is about to expire; null when signed out. Never throws. */
  accessToken(): Promise<string | null>;
  /** Renew after the server rejected the token; null when the session is over. Never throws. */
  refresh(): Promise<string | null>;
}

let session: SessionBridge | null = null;

export function connectSession(bridge: SessionBridge): void {
  session = bridge;
}

type ReachabilityListener = (reachable: boolean) => void;
const listeners = new Set<ReachabilityListener>();
let reachable = true;

/** Subscribe to backend reachability changes. Returns the unsubscribe function. */
export function onReachabilityChange(listener: ReachabilityListener): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

export function isBackendReachable(): boolean {
  return reachable;
}

function setReachable(next: boolean): void {
  if (next === reachable) return;
  reachable = next;
  listeners.forEach((listener) => listener(next));
}

export interface ApiRequestInit extends RequestInit {
  /** Attach the session token and refresh it on a 401. Auth endpoints pass false. Default true. */
  auth?: boolean;
  /** Abort and report a timeout when no response arrives in time. Off by default (streams). */
  timeoutMs?: number;
}

/** Marks the proxy's own "backend down" reply, so it is never mistaken for a backend error. */
const PROXY_STATUS_HEADER = "x-luminalearn-proxy";

async function send(input: string, init: RequestInit, timeoutMs?: number): Promise<Response> {
  const controller = new AbortController();
  const callerSignal = init.signal;
  const abortFromCaller = () => controller.abort(callerSignal?.reason);
  if (callerSignal?.aborted) controller.abort(callerSignal.reason);
  callerSignal?.addEventListener("abort", abortFromCaller, { once: true });
  let timedOut = false;
  const timer = timeoutMs
    ? setTimeout(() => {
        timedOut = true;
        controller.abort();
      }, timeoutMs)
    : undefined;

  try {
    const response = await fetch(input, { ...init, signal: controller.signal });
    if (response.status === 503 && response.headers.get(PROXY_STATUS_HEADER) === "backend-unavailable") {
      setReachable(false);
      throw new BackendUnavailableError();
    }
    setReachable(true);
    return response;
  } catch (error) {
    if (error instanceof BackendUnavailableError) throw error;
    if (timedOut) throw new Error("The server took too long to respond. Please try again.");
    if (callerSignal?.aborted) throw error; // the caller cancelled; not a connectivity problem
    setReachable(false);
    throw new BackendUnavailableError();
  } finally {
    if (timer) clearTimeout(timer);
    callerSignal?.removeEventListener("abort", abortFromCaller);
  }
}

/**
 * `fetch` for LuminaLearn API paths (`${API_BASE}/...`). Request bodies must be replayable
 * (strings, FormData, Blobs), since a request can be retried once after a token refresh.
 */
export async function apiFetch(input: string, init: ApiRequestInit = {}): Promise<Response> {
  const { auth = true, timeoutMs, ...requestInit } = init;
  const withToken = (token: string | null): RequestInit => {
    const headers = new Headers(requestInit.headers);
    if (token) headers.set("Authorization", `Bearer ${token}`);
    return { ...requestInit, headers };
  };

  const explicit = new Headers(requestInit.headers).get("Authorization")?.replace(/^Bearer\s+/i, "") || null;
  const token = auth ? explicit ?? (session ? await session.accessToken() : null) : null;
  const response = await send(input, auth ? withToken(token) : requestInit, timeoutMs);
  if (response.status !== 401 || !auth || !session) return response;

  const fresh = await session.refresh();
  if (!fresh || fresh === token) return response;
  return send(input, withToken(fresh), timeoutMs);
}

/** The most helpful message in an error response: FastAPI `detail` strings and validation lists. */
export async function readErrorDetail(response: Response, fallback: string): Promise<string> {
  const body = await response.json().catch(() => null);
  const detail = body && typeof body === "object" ? (body as { detail?: unknown }).detail : undefined;
  if (typeof detail === "string" && detail.trim()) return detail;
  if (Array.isArray(detail)) {
    const first = detail[0] as { msg?: unknown } | undefined;
    if (first && typeof first.msg === "string") return first.msg.replace(/^Value error, /, "");
  }
  return fallback;
}
