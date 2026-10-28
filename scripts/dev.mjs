#!/usr/bin/env node
/**
 * One command for local development: `npm run dev` from the project root.
 *
 * Starts the FastAPI backend (`python -m app`, which reads BACKEND_PORT from backend/.env and
 * refuses a port another program already holds) and the Next.js frontend, pointing the
 * frontend's API proxy at that same port. The two can never disagree about where the API is.
 * Ctrl+C stops both; if either one exits, the other is stopped too.
 */
import { spawn, spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { connect } from "node:net";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const backendDir = join(root, "backend");
const frontendDir = join(root, "frontend");
const isWindows = process.platform === "win32";

function envValue(file, key) {
  if (!existsSync(file)) return undefined;
  const match = readFileSync(file, "utf8").match(new RegExp(`^${key}\\s*=\\s*"?([^"\\r\\n#]+)"?`, "m"));
  return match?.[1].trim();
}

const port = Number(envValue(join(backendDir, ".env"), "BACKEND_PORT") ?? 8001);
const backendUrl = `http://127.0.0.1:${port}`;

const venvPython = isWindows ? join(backendDir, ".venv", "Scripts", "python.exe") : join(backendDir, ".venv", "bin", "python");
const python = existsSync(venvPython) ? venvPython : isWindows ? "python" : "python3";
const nextBin = join(frontendDir, "node_modules", "next", "dist", "bin", "next");

if (!existsSync(nextBin)) {
  console.error("Frontend dependencies are missing. Run `npm install` in frontend/ first.");
  process.exit(1);
}

/** True when something already accepts connections on the port (works even where two programs share one). */
function portTaken(candidate) {
  return new Promise((resolve) => {
    const socket = connect({ host: "127.0.0.1", port: candidate });
    socket.setTimeout(500);
    socket.once("connect", () => {
      socket.destroy();
      resolve(true);
    });
    socket.once("timeout", () => {
      socket.destroy();
      resolve(false);
    });
    socket.once("error", () => resolve(false));
  });
}

async function freeWebPort(first = 3000) {
  for (let candidate = first; candidate < first + 20; candidate += 1) {
    if (!(await portTaken(candidate))) return candidate;
  }
  throw new Error(`No free port between ${first} and ${first + 19} for the web app.`);
}

const colors = { api: "\x1b[36m", web: "\x1b[35m", reset: "\x1b[0m" };
const children = new Map();
let shuttingDown = false;

function prefixed(name, stream, target) {
  let pending = "";
  stream.on("data", (chunk) => {
    pending += chunk.toString();
    const lines = pending.split(/\r?\n/);
    pending = lines.pop() ?? "";
    for (const line of lines) target.write(`${colors[name]}[${name}]${colors.reset} ${line}\n`);
  });
}

function start(name, command, args, options) {
  const child = spawn(command, args, { ...options, stdio: ["ignore", "pipe", "pipe"] });
  children.set(name, child);
  prefixed(name, child.stdout, process.stdout);
  prefixed(name, child.stderr, process.stderr);
  child.on("exit", (code) => {
    children.delete(name);
    if (!shuttingDown) {
      console.error(`\n${name === "api" ? "The backend" : "The frontend"} stopped (exit code ${code ?? "none"}). Stopping the other server.`);
      stopAll(code ?? 1);
    }
  });
  return child;
}

function stopAll(exitCode = 0) {
  shuttingDown = true;
  for (const child of children.values()) {
    if (isWindows) {
      // Kill the whole tree: uvicorn's reloader and Next.js both spawn worker processes.
      spawnSync("taskkill", ["/pid", String(child.pid), "/T", "/F"], { stdio: "ignore" });
    } else {
      child.kill("SIGTERM");
    }
  }
  process.exit(exitCode);
}

process.on("SIGINT", () => stopAll(0));
process.on("SIGTERM", () => stopAll(0));

async function waitForBackend(timeoutMs = 90_000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline && !shuttingDown) {
    try {
      const response = await fetch(`${backendUrl}/api/v1/health`, { signal: AbortSignal.timeout(2000) });
      const body = await response.json();
      if (body?.service?.includes("LuminaLearn")) return true;
    } catch {
      // not up yet
    }
    await new Promise((resolve) => setTimeout(resolve, 750));
  }
  return false;
}

const webPort = await freeWebPort();
const webUrl = `http://localhost:${webPort}`;
console.log(`Starting LuminaLearn: API on ${backendUrl}, web app on ${webUrl}\n`);
start("api", python, ["-m", "app"], { cwd: backendDir, env: { ...process.env, PYTHONUNBUFFERED: "1" } });
start("web", process.execPath, [nextBin, "dev", "-p", String(webPort)], { cwd: frontendDir, env: { ...process.env, BACKEND_URL: backendUrl } });

if (await waitForBackend()) {
  console.log(`\n${colors.api}[api]${colors.reset} Ready. Open ${webUrl} (Ctrl+C stops both servers).\n`);
} else if (!shuttingDown) {
  console.error(`\nThe backend did not answer on ${backendUrl} within 90 seconds. Check the [api] lines above.`);
}
