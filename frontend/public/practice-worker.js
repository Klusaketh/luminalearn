/*
 * LuminaLearn coding sandbox worker.
 *
 * Runs learner Python with Pyodide (Python compiled to WebAssembly) off the main thread, so a slow or
 * endless loop never freezes the page: the page simply terminates this worker after a time limit.
 * Code runs only in the learner's browser; nothing is executed on the server.
 *
 * Messages in:  { type: "init" }
 *               { type: "run", id, code, functionName, tests, compare, harness }
 * Messages out: { type: "ready" }
 *               { type: "result", id, report }
 *               { type: "error", id, message }
 */
/* global importScripts, loadPyodide */

let pyodidePromise = null;
let loadedHarness = null;

function pyodide() {
  if (!pyodidePromise) {
    importScripts("/pyodide/pyodide.js");
    pyodidePromise = loadPyodide({ indexURL: "/pyodide/" });
  }
  return pyodidePromise;
}

self.onmessage = async (event) => {
  const message = event.data || {};
  try {
    const py = await pyodide();
    if (message.type === "init") {
      self.postMessage({ type: "ready" });
      return;
    }
    if (message.type !== "run") return;

    if (loadedHarness !== message.harness) {
      py.runPython(message.harness); // defines run_tests() in the interpreter's globals
      loadedHarness = message.harness;
    }
    const runTests = py.globals.get("run_tests");
    try {
      const report = runTests(message.code, message.functionName, JSON.stringify(message.tests), message.compare);
      self.postMessage({ type: "result", id: message.id, report: JSON.parse(report) });
    } finally {
      runTests.destroy();
    }
  } catch (error) {
    self.postMessage({ type: "error", id: message.id, message: String((error && error.message) || error) });
  }
};
