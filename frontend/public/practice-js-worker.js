/*
 * LuminaLearn coding sandbox worker for JavaScript.
 *
 * Runs learner JavaScript off the main thread with content/practice/harness.js (sent with each run),
 * so an endless loop never freezes the page: the page terminates this worker after a time limit.
 * Code runs only in the learner's browser; nothing is executed on the server.
 *
 * Messages in:  { type: "init" }
 *               { type: "run", id, code, functionName, tests, compare, harness }
 * Messages out: { type: "ready" }
 *               { type: "result", id, report }
 *               { type: "error", id, message }
 */

let loadedHarness = null;
let runTests = null;

self.onmessage = (event) => {
  const message = event.data || {};
  if (message.type === "init") {
    self.postMessage({ type: "ready" });
    return;
  }
  if (message.type !== "run") return;
  try {
    if (loadedHarness !== message.harness) {
      runTests = new Function(`${message.harness}\nreturn runTests;`)();
      loadedHarness = message.harness;
    }
    const report = runTests(message.code, message.functionName, JSON.stringify(message.tests), message.compare);
    self.postMessage({ type: "result", id: message.id, report: JSON.parse(report) });
  } catch (error) {
    self.postMessage({ type: "error", id: message.id, message: String((error && error.message) || error) });
  }
};
