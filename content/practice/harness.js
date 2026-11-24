/*
 * Runs a learner's JavaScript solution against a practice problem's tests.
 *
 * The JavaScript twin of harness.py, with the same report so the page shows both languages alike:
 * - the browser runs it in a Web Worker (the API serves it with each problem), and
 * - the backend test suite runs it with Node against every reference solution.
 *
 * runTests never throws. It returns a JSON string:
 * {"error": string | null, "stdout": string, "results": [{"index", "passed", "got", "stdout", "error"}]}
 */
function runTests(userCode, functionName, testsJson, compare) {
  "use strict";
  var MAX_OUTPUT = 2000;
  // `new Function(params, body)` puts the body two lines down, and the "use strict" line adds one more.
  var LINE_OFFSET = 3;
  var tests = JSON.parse(testsJson);

  function show(value) {
    if (typeof value === "string") return value;
    try {
      var text = JSON.stringify(normalise(value));
      return text === undefined ? String(value) : text;
    } catch (e) {
      return String(value);
    }
  }

  // Results are compared as JSON data: Sets become sorted arrays, Maps become objects, undefined becomes null.
  function normalise(value) {
    if (value === undefined || (typeof value === "number" && !isFinite(value))) return value === undefined ? null : String(value);
    if (value instanceof Set) return Array.from(value, normalise).sort(byJson);
    if (value instanceof Map) {
      var object = {};
      value.forEach(function (v, k) { object[String(k)] = normalise(v); });
      return object;
    }
    if (Array.isArray(value) || ArrayBuffer.isView(value)) return Array.from(value, normalise);
    if (value !== null && typeof value === "object") {
      var copy = {};
      Object.keys(value).forEach(function (k) { copy[k] = normalise(value[k]); });
      return copy;
    }
    return value;
  }

  function byJson(a, b) {
    var x = JSON.stringify(a), y = JSON.stringify(b);
    return x < y ? -1 : x > y ? 1 : 0;
  }

  function equal(a, b) {
    if (a === b) return true;
    if (Array.isArray(a) && Array.isArray(b)) {
      if (a.length !== b.length) return false;
      for (var i = 0; i < a.length; i++) if (!equal(a[i], b[i])) return false;
      return true;
    }
    if (a && b && typeof a === "object" && typeof b === "object" && !Array.isArray(a) && !Array.isArray(b)) {
      var ka = Object.keys(a), kb = Object.keys(b);
      if (ka.length !== kb.length) return false;
      for (var j = 0; j < ka.length; j++) if (!Object.prototype.hasOwnProperty.call(b, ka[j]) || !equal(a[ka[j]], b[ka[j]])) return false;
      return true;
    }
    return false;
  }

  function matches(got, expected) {
    if (compare === "unordered" && Array.isArray(got) && Array.isArray(expected)) {
      return equal(got.slice().sort(byJson), expected.slice().sort(byJson));
    }
    return equal(got, expected);
  }

  // "TypeError: x is not a function (line 4)", pointing at the learner's own code where possible.
  function describe(error) {
    var name = (error && error.name) || "Error";
    var message = error && error.message !== undefined ? error.message : String(error);
    var stack = (error && error.stack) || "";
    // A SyntaxError's stack points at the harness, not the learner's code, so it gets no line number.
    var found = name === "SyntaxError" ? null : /<anonymous>:(\d+):\d+/.exec(stack) || /Function:(\d+):\d+/.exec(stack);
    var line = found ? Number(found[1]) - LINE_OFFSET : 0;
    return name + ": " + message + (line > 0 ? " (line " + line + ")" : "");
  }

  var sink = [];
  function capture() {
    var write = function () {
      var parts = [];
      for (var i = 0; i < arguments.length; i++) parts.push(show(arguments[i]));
      sink.push(parts.join(" "));
    };
    return { log: write, info: write, warn: write, error: write, debug: write };
  }
  function drain() {
    var text = sink.length ? sink.join("\n") + "\n" : "";
    sink = [];
    return text.slice(0, MAX_OUTPUT);
  }

  var fn;
  var console = capture();
  try {
    var factory = new Function(
      "console",
      '"use strict";\n' + userCode + "\n;return typeof " + functionName + ' === "function" ? ' + functionName + " : undefined;"
    );
    fn = factory(console);
  } catch (error) {
    return JSON.stringify({ error: describe(error), stdout: drain(), results: [] });
  }
  var topOut = drain();
  if (typeof fn !== "function") {
    return JSON.stringify({
      error: "Define a function named " + functionName + "(...) so the tests can call it.",
      stdout: topOut,
      results: [],
    });
  }

  var results = tests.map(function (test, index) {
    var entry = { index: index, passed: false, got: null, stdout: "", error: null };
    try {
      var value = fn.apply(null, JSON.parse(JSON.stringify(test.args)));
      if (value && typeof value.then === "function") {
        entry.error = "Return the answer directly: the tests do not wait for async functions or Promises.";
      } else {
        var got = normalise(value);
        entry.got = show(got);
        entry.passed = matches(got, test.expected);
      }
    } catch (error) {
      entry.error = describe(error);
    }
    entry.stdout = drain();
    return entry;
  });
  return JSON.stringify({ error: null, stdout: topOut, results: results });
}

if (typeof module !== "undefined" && module.exports) module.exports = { runTests: runTests };
