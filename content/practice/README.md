# LuminaLearn coding practice

This folder holds the problems for the coding sandbox (`/practice` in the web app). Learners write **Python or JavaScript** in the browser, run it against each problem's tests, climb a hint ladder, and ask the Socratic tutor for help.

## How solutions are run

Code runs **in the learner's browser**, inside a Web Worker: Python with [Pyodide](https://pyodide.org) (Python compiled to WebAssembly), JavaScript directly. The server never executes learner code, so a malicious or buggy submission cannot affect it. The page stops the worker after a time limit, so an infinite loop cannot freeze the tab.

[`harness.py`](harness.py) and [`harness.js`](harness.js) judge a solution and produce the same report. The API sends the harness for the chosen language with each problem, and the backend test suite runs both against every reference solution (JavaScript with Node), so the browser and the tests always agree.

## Layout

```
content/practice/
  harness.py, harness.js           run a solution against tests (browser and test suite)
  problems/<slug>/
    problem.json                   metadata, hints and tests
    statement.md                   the problem statement shown to learners (Markdown, KaTeX math)
    starter.py, starter.js         the code the editor starts with, per language
    solution.py, solution.js       reference solutions; never sent to the browser
```

## problem.json

```json
{
  "title": "Two Sum",
  "difficulty": "Easy",
  "order": 1,
  "tags": ["Arrays", "Hashing"],
  "related_topic": "hash-functions-collisions",
  "function": "two_sum",
  "compare": "exact",
  "hints": ["nudge", "scaffold", "parallel example"],
  "tests": [{ "args": [[2, 7, 11, 15], 9], "expected": [0, 1] }]
}
```

- `difficulty` is `Easy`, `Medium` or `Hard`. `order` sets the position in the list.
- `related_topic` is a topic slug from `content/subjects/data-structures-and-algorithms/syllabus.json`; the problem page links to that lesson.
- `function` is the name the tests call with `*args`. JavaScript uses the camelCase form (`two_sum` becomes `twoSum`). Results are compared as JSON data: tuples become lists and sets become sorted lists (in JavaScript, Sets become sorted arrays and Maps become objects).
- A language is offered for a problem when both its starter and solution files exist. Every problem currently has Python and JavaScript.
- `compare` is `exact`, or `unordered` when the order of a returned list does not matter.
- `hints` are exactly three, matching the tutor's hint ladder: a nudge, a scaffold, and a parallel example from a different problem. A hint never contains the full solution.
- Write at least five tests, including edge cases such as empty input, a single element, duplicates and negative numbers.

## Checks

```bash
cd backend && pytest tests/test_practice.py
```

The tests require every reference solution to pass all of its tests, every starter to fail at least one, every `related_topic` to exist, and every problem to have a statement and three hints.
