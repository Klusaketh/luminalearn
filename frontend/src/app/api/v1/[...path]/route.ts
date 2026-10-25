/**
 * Same-origin proxy: the browser calls /api/v1/* on this site and the Next.js server forwards it
 * to the FastAPI backend. The browser never needs the backend's address, so a port change or a
 * CORS setting can't break the app, and a stopped backend gets one clear JSON reply instead of
 * "Failed to fetch". The voice WebSocket is forwarded by a rewrite in next.config.js, because
 * route handlers cannot accept WebSocket upgrades.
 */
import type { NextRequest } from "next/server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

// next.config.js resolves the default and writes it back to process.env; the fallback mirrors it.
const BACKEND_URL = (process.env.BACKEND_URL || "http://127.0.0.1:8001").replace(/\/+$/, "");

// Connection-level headers describe one hop and must not be forwarded.
const HOP_BY_HOP = new Set([
  "connection",
  "keep-alive",
  "proxy-authenticate",
  "proxy-authorization",
  "te",
  "trailer",
  "transfer-encoding",
  "upgrade",
  "host",
  "content-length",
]);

let lastOutageLog = 0;

function forwardedRequestHeaders(req: NextRequest): Headers {
  const headers = new Headers();
  req.headers.forEach((value, key) => {
    if (!HOP_BY_HOP.has(key)) headers.set(key, value);
  });
  const clientIp = req.ip ?? req.headers.get("x-forwarded-for")?.split(",")[0]?.trim();
  if (clientIp) headers.set("x-forwarded-for", clientIp);
  headers.set("x-forwarded-host", req.headers.get("host") ?? "");
  headers.set("x-forwarded-proto", req.nextUrl.protocol.replace(":", ""));
  return headers;
}

function responseHeaders(upstream: Response): Headers {
  const headers = new Headers();
  upstream.headers.forEach((value, key) => {
    // fetch() already decoded the body, so the original encoding and length no longer apply.
    if (!HOP_BY_HOP.has(key) && key !== "content-encoding" && key !== "set-cookie") headers.set(key, value);
  });
  // Cookies must stay separate headers; joining them with commas corrupts their Expires dates.
  upstream.headers.getSetCookie().forEach((cookie) => headers.append("set-cookie", cookie));
  if (headers.get("content-type")?.startsWith("text/event-stream")) {
    // no-transform keeps compression from buffering the stream; it must reach the browser live.
    headers.set("cache-control", "no-cache, no-transform");
    headers.set("x-accel-buffering", "no");
  }
  return headers;
}

function backendUnavailable(cause: unknown): Response {
  const now = Date.now();
  if (now - lastOutageLog > 30_000) {
    lastOutageLog = now;
    const reason = cause instanceof Error ? (cause.cause instanceof Error ? cause.cause.message : cause.message) : String(cause);
    console.error(
      `[api proxy] The LuminaLearn backend is not reachable at ${BACKEND_URL} (${reason}). ` +
        "Start it with `npm run dev` from the project root, or `python -m app` in backend/. " +
        "If it runs elsewhere, set BACKEND_URL in frontend/.env.local."
    );
  }
  return Response.json(
    { detail: "BACKEND_UNAVAILABLE", message: "The LuminaLearn server is not running or is restarting." },
    { status: 503, headers: { "x-luminalearn-proxy": "backend-unavailable", "retry-after": "3", "cache-control": "no-store" } }
  );
}

async function proxy(req: NextRequest, { params }: { params: { path: string[] } }): Promise<Response> {
  // Keep the proxy scoped to the API: dot segments would let a path climb out of /api/v1.
  if (params.path.some((segment) => segment === "." || segment === "..")) {
    return Response.json({ detail: "Not Found" }, { status: 404 });
  }
  const target = `${BACKEND_URL}/api/v1/${params.path.map(encodeURIComponent).join("/")}${req.nextUrl.search}`;
  const hasBody = req.method !== "GET" && req.method !== "HEAD";

  let upstream: Response;
  try {
    upstream = await fetch(target, {
      method: req.method,
      headers: forwardedRequestHeaders(req),
      body: hasBody ? await req.arrayBuffer() : undefined,
      redirect: "manual",
      cache: "no-store",
      // Closing the tab or pressing stop cancels the backend's work (e.g. a streaming answer).
      signal: req.signal,
    });
  } catch (error) {
    if (req.signal.aborted) return new Response(null, { status: 499 });
    return backendUnavailable(error);
  }

  return new Response(upstream.body, {
    status: upstream.status,
    statusText: upstream.statusText,
    headers: responseHeaders(upstream),
  });
}

export const GET = proxy;
export const HEAD = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
