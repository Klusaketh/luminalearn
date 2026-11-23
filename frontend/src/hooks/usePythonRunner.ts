"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { PracticeTestCase, RunReport } from "@/services/practiceService";

/** How long one run may take before the worker is stopped (an endless loop, for example). */
export const RUN_TIME_LIMIT_MS = 6000;

export type RunnerStatus = "loading" | "ready" | "running" | "failed";

export type RunOutcome =
  | { kind: "report"; report: RunReport }
  | { kind: "timeout" }
  | { kind: "error"; message: string };

interface RunRequest {
  code: string;
  functionName: string;
  tests: PracticeTestCase[];
  compare: string;
  harness: string;
}

type WorkerMessage =
  | { type: "ready" }
  | { type: "result"; id: number; report: RunReport }
  | { type: "error"; id?: number; message: string };

/**
 * Runs learner Python in a Web Worker with Pyodide. The worker is replaced after a timeout, so a
 * `while True:` loop costs the learner a few seconds, never a frozen tab.
 */
export function usePythonRunner() {
  const [status, setStatus] = useState<RunnerStatus>("loading");
  const workerRef = useRef<Worker | null>(null);
  const readyRef = useRef<Promise<void> | null>(null);
  const nextId = useRef(1);

  const startWorker = useCallback(() => {
    workerRef.current?.terminate();
    const worker = new Worker("/practice-worker.js");
    workerRef.current = worker;
    setStatus("loading");
    readyRef.current = new Promise<void>((resolve, reject) => {
      const onMessage = (event: MessageEvent<WorkerMessage>) => {
        if (event.data.type === "ready") {
          worker.removeEventListener("message", onMessage);
          setStatus("ready");
          resolve();
        } else if (event.data.type === "error" && event.data.id === undefined) {
          worker.removeEventListener("message", onMessage);
          setStatus("failed");
          reject(new Error(event.data.message));
        }
      };
      worker.addEventListener("message", onMessage);
      worker.addEventListener("error", () => {
        setStatus("failed");
        reject(new Error("The Python runtime could not start."));
      });
      worker.postMessage({ type: "init" });
    });
    readyRef.current.catch(() => {});
  }, []);

  useEffect(() => {
    startWorker();
    return () => workerRef.current?.terminate();
  }, [startWorker]);

  const run = useCallback(
    async (request: RunRequest): Promise<RunOutcome> => {
      try {
        await readyRef.current;
      } catch (error) {
        return { kind: "error", message: error instanceof Error ? error.message : String(error) };
      }
      const current = workerRef.current;
      if (!current) return { kind: "error", message: "The Python runtime is not available." };
      const worker: Worker = current;

      const id = nextId.current++;
      setStatus("running");
      const outcome = await new Promise<RunOutcome>((resolve) => {
        const timer = window.setTimeout(() => {
          worker.removeEventListener("message", onMessage);
          resolve({ kind: "timeout" });
        }, RUN_TIME_LIMIT_MS);
        function onMessage(event: MessageEvent<WorkerMessage>) {
          const data = event.data;
          if ((data.type === "result" || data.type === "error") && data.id === id) {
            window.clearTimeout(timer);
            worker.removeEventListener("message", onMessage);
            resolve(data.type === "result" ? { kind: "report", report: data.report } : { kind: "error", message: data.message });
          }
        }
        worker.addEventListener("message", onMessage);
        worker.postMessage({ type: "run", id, ...request });
      });

      if (outcome.kind === "timeout") startWorker(); // the old worker is stuck: replace it
      else setStatus("ready");
      return outcome;
    },
    [startWorker],
  );

  return { status, run };
}
