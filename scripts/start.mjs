#!/usr/bin/env node
/**
 * Runs the production container (see the Dockerfile): the Next.js server on the public $PORT and
 * the FastAPI backend on a private port behind it, the same arrangement `npm run dev` uses locally.
 * Only the web server is reachable from outside; it forwards /api/v1 to the backend.
 *
 * If either server exits, the other is stopped and the container exits, so the host restarts it.
 * Once the API answers, the curriculum is synced from content/ at low priority: the sync is
 * idempotent, and running it afterwards keeps it from delaying the site when it wakes up.
 */
import { spawn } from "node:child_process";
import { setPriority } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const backendDir = join(root, "backend");
const backendPort = "8001";
const backendUrl = `http://127.0.0.1:${backendPort}`;
// Both default to the image's layout; set them to run this script outside the container.
const python = process.env.PYTHON_BIN || "python";
const webDir = process.env.WEB_DIR || join(root, "frontend");

const children = new Set();
let shuttingDown = false;

function stopAll(exitCode) {
  shuttingDown = true;
  for (const child of children) child.kill("SIGTERM");
  process.exit(exitCode);
}

process.on("SIGINT", () => stopAll(0));
process.on("SIGTERM", () => stopAll(0));

function startServer(name, command, args, options) {
  const child = spawn(command, args, { ...options, stdio: "inherit" });
  children.add(child);
  const stopped = (reason) => {
    children.delete(child);
    if (!shuttingDown) {
      console.error(`The ${name} stopped (${reason}). Stopping the container.`);
      stopAll(1);
    }
  };
  child.on("error", (error) => stopped(error.message));
  child.on("exit", (code) => stopped(`exit code ${code ?? "none"}`));
}

async function waitForBackend() {
  while (!shuttingDown) {
    try {
      const response = await fetch(`${backendUrl}/api/v1/health`, { signal: AbortSignal.timeout(2000) });
      if (response.ok) return;
    } catch {
      // not up yet
    }
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
}

function syncCurriculum() {
  const sync = spawn(python, [join(root, "scripts", "seed_academic_content.py")], { cwd: backendDir, stdio: "inherit" });
  children.add(sync);
  sync.once("spawn", () => setPriority(sync.pid, 19));
  sync.on("error", (error) => console.error(`The curriculum sync could not start: ${error.message}`));
  sync.on("exit", (code) => {
    children.delete(sync);
    if (code) console.error(`The curriculum sync failed (exit code ${code}). The site keeps running with the lessons it has.`);
  });
}

startServer("backend", python, ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", backendPort], {
  cwd: backendDir,
  env: { ...process.env, PYTHONUNBUFFERED: "1" },
});
startServer("web server", process.execPath, ["server.js"], {
  cwd: webDir,
  env: { ...process.env, PORT: process.env.PORT || "3000", HOSTNAME: "0.0.0.0", BACKEND_URL: backendUrl },
});

await waitForBackend();
if (!shuttingDown) syncCurriculum();
