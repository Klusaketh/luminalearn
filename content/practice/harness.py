"""Runs a learner's solution against a practice problem's tests.

This one file is the single source of truth for judging solutions:
- the browser loads it into Pyodide (the API serves it with each problem), and
- the backend test suite runs it against every reference solution.

`run_tests` never raises. It returns a JSON string:
{"error": str | None, "stdout": str, "results": [{"index", "passed", "got", "stdout", "error"}]}
"""

import contextlib
import copy
import io
import json
import traceback

MAX_OUTPUT = 2000


def _normalise(value):
    """Turns a result into JSON data: tuples become lists, sets become sorted lists."""
    if isinstance(value, (set, frozenset)):
        return sorted((_normalise(v) for v in value), key=repr)
    if isinstance(value, (list, tuple)):
        return [_normalise(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _normalise(v) for k, v in value.items()}
    return value


def _equal(got, expected, compare):
    if compare == "unordered" and isinstance(got, list) and isinstance(expected, list):
        return sorted(got, key=repr) == sorted(expected, key=repr)
    return got == expected


def _describe(exc):
    """'ValueError: bad input (line 4)', pointing at the learner's own code where possible."""
    line = None
    for frame in traceback.extract_tb(exc.__traceback__):
        if frame.filename == "solution.py":
            line = frame.lineno
    if isinstance(exc, SyntaxError) and exc.filename == "solution.py":
        line = exc.lineno
    message = "".join(traceback.format_exception_only(type(exc), exc)).strip().splitlines()[-1]
    return f"{message} (line {line})" if line else message


def _show(value):
    try:
        return json.dumps(value)
    except (TypeError, ValueError):
        return repr(value)


def run_tests(user_code, function_name, tests_json, compare="exact"):
    tests = json.loads(tests_json)
    namespace = {"__name__": "solution"}
    top_out = io.StringIO()
    try:
        with contextlib.redirect_stdout(top_out):
            exec(compile(user_code, "solution.py", "exec"), namespace)
    except BaseException as exc:  # noqa: BLE001 - every failure is reported, never raised
        return json.dumps({"error": _describe(exc), "stdout": top_out.getvalue()[:MAX_OUTPUT], "results": []})

    function = namespace.get(function_name)
    if not callable(function):
        error = f"Define a function named {function_name}(...) so the tests can call it."
        return json.dumps({"error": error, "stdout": top_out.getvalue()[:MAX_OUTPUT], "results": []})

    results = []
    for index, case in enumerate(tests):
        out = io.StringIO()
        entry = {"index": index, "passed": False, "got": None, "stdout": "", "error": None}
        try:
            with contextlib.redirect_stdout(out):
                got = _normalise(function(*copy.deepcopy(case["args"])))
            entry["got"] = _show(got)
            entry["passed"] = _equal(got, case["expected"], compare)
        except BaseException as exc:  # noqa: BLE001
            entry["error"] = _describe(exc)
        entry["stdout"] = out.getvalue()[:MAX_OUTPUT]
        results.append(entry)
    return json.dumps({"error": None, "stdout": top_out.getvalue()[:MAX_OUTPUT], "results": results})
