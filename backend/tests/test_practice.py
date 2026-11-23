"""Coding practice sandbox: problem content, the judging harness, and the API."""

import json
import runpy

import pytest
from httpx import AsyncClient
from scripts.subject_content import iter_topics, load_subject_catalog

from app.core.security import create_access_token
from app.services.practice_service import PRACTICE_ROOT, load_problems
from tests.conftest import create_verified_learner

HARNESS = runpy.run_path(str(PRACTICE_ROOT / "harness.py"))
PROBLEMS = list(load_problems().values())
DSA_TOPICS = {
    t["slug"] for s in load_subject_catalog() if s["slug"] == "data-structures-and-algorithms" for (_, _, t) in iter_topics(s)
}


def judge(code: str, problem) -> dict:
    return json.loads(HARNESS["run_tests"](code, problem.function_name, json.dumps(list(problem.tests)), problem.compare))


# ---------------------------------------------------------------------- content


def test_problem_set_is_present():
    assert len(PROBLEMS) >= 12
    assert len({p.order for p in PROBLEMS}) == len(PROBLEMS), "each problem needs its own display order"


@pytest.mark.parametrize("problem", PROBLEMS, ids=[p.slug for p in PROBLEMS])
def test_reference_solution_passes_every_test(problem):
    report = judge(problem.solution, problem)
    assert report["error"] is None, report["error"]
    failed = [r for r in report["results"] if not r["passed"]]
    assert not failed, failed


@pytest.mark.parametrize("problem", PROBLEMS, ids=[p.slug for p in PROBLEMS])
def test_starter_code_is_not_already_a_solution(problem):
    report = judge(problem.starter_code, problem)
    assert report["error"] is None, "the starter must define the function the tests call"
    assert not all(r["passed"] for r in report["results"])


@pytest.mark.parametrize("problem", PROBLEMS, ids=[p.slug for p in PROBLEMS])
def test_problem_is_complete(problem):
    assert problem.difficulty in {"Easy", "Medium", "Hard"}
    assert len(problem.tests) >= 5, "write at least five tests, including edge cases"
    assert len(problem.hints) == 3, "hints follow the tutor's ladder: nudge, scaffold, parallel example"
    assert problem.compare in {"exact", "unordered"}
    assert len(problem.statement.split()) >= 30
    assert problem.related_topic in DSA_TOPICS, f"unknown related_topic {problem.related_topic!r}"


# ---------------------------------------------------------------------- harness


def _run(code: str, tests: list, function: str = "f", compare: str = "exact") -> dict:
    return json.loads(HARNESS["run_tests"](code, function, json.dumps(tests), compare))


def test_harness_reports_syntax_errors_with_the_line():
    report = _run("def f(x):\n    return x +\n", [{"args": [1], "expected": 1}])
    assert report["results"] == []
    assert report["error"].startswith("SyntaxError") and "(line 2)" in report["error"]


def test_harness_requires_the_named_function():
    report = _run("def g(x):\n    return x\n", [{"args": [1], "expected": 1}])
    assert "Define a function named f(...)" in report["error"]


def test_harness_reports_runtime_errors_per_test():
    code = "def f(x):\n    return 10 // x\n"
    report = _run(code, [{"args": [2], "expected": 5}, {"args": [0], "expected": 0}])
    assert report["results"][0]["passed"] is True
    second = report["results"][1]
    assert second["passed"] is False and second["error"].startswith("ZeroDivisionError") and "(line 2)" in second["error"]


def test_harness_captures_prints_and_normalises_results():
    code = "def f(xs):\n    print('checking', len(xs))\n    return tuple(sorted(set(xs)))\n"
    report = _run(code, [{"args": [[3, 1, 3]], "expected": [1, 3]}])
    result = report["results"][0]
    assert result["passed"] is True and result["stdout"] == "checking 3\n" and result["got"] == "[1, 3]"


def test_harness_unordered_comparison_and_argument_isolation():
    code = "def f(xs):\n    xs.append(99)\n    return [2, 1]\n"
    tests = [{"args": [[1]], "expected": [1, 2]}, {"args": [[1]], "expected": [1, 2]}]
    assert all(r["passed"] for r in _run(code, tests, compare="unordered")["results"])
    assert not any(r["passed"] for r in _run(code, tests, compare="exact")["results"])


# ---------------------------------------------------------------------- API


@pytest.mark.asyncio
async def test_practice_requires_sign_in(async_client: AsyncClient):
    assert (await async_client.get("/api/v1/practice/problems")).status_code == 401


@pytest.mark.asyncio
async def test_list_and_detail_never_expose_solutions(authed_client: AsyncClient):
    listing = (await authed_client.get("/api/v1/practice/problems")).json()
    assert listing["total_count"] == len(PROBLEMS) and listing["solved_count"] == 0
    assert listing["problems"][0]["slug"] == "two-sum"

    detail = (await authed_client.get("/api/v1/practice/problems/two-sum")).json()
    assert detail["function_name"] == "two_sum" and len(detail["hints"]) == 3
    assert "def run_tests" in detail["harness"]
    assert detail["related_topic"]["title"] == "Hash Functions & Collision Handling"
    assert "solution" not in detail and "seen[target - x]" not in json.dumps(detail)


@pytest.mark.asyncio
async def test_unknown_problem_is_404(authed_client: AsyncClient):
    assert (await authed_client.get("/api/v1/practice/problems/nope")).status_code == 404


@pytest.mark.asyncio
async def test_submissions_track_progress_per_learner(authed_client: AsyncClient, async_client: AsyncClient):
    total = len(load_problems()["binary-search"].tests)
    url = "/api/v1/practice/problems/binary-search/submissions"

    first = (await authed_client.post(url, json={"code": "def search(n, t): pass", "passed": 2, "total": total})).json()
    assert first == {"solved": False, "attempts": 1, "best_passed": 2, "total": total}
    second = (await authed_client.post(url, json={"code": "def search(n, t): ...", "passed": total, "total": total})).json()
    assert second["solved"] is True and second["attempts"] == 2 and second["best_passed"] == total

    listing = (await authed_client.get("/api/v1/practice/problems")).json()
    entry = next(p for p in listing["problems"] if p["slug"] == "binary-search")
    assert entry["solved"] is True and listing["solved_count"] == 1

    other = await create_verified_learner()
    headers = {"Authorization": f"Bearer {create_access_token(subject=str(other.id))}"}
    theirs = (await async_client.get("/api/v1/practice/problems", headers=headers)).json()
    assert theirs["solved_count"] == 0, "progress belongs to each learner"


@pytest.mark.asyncio
async def test_submission_must_match_the_problem(authed_client: AsyncClient):
    url = "/api/v1/practice/problems/two-sum/submissions"
    wrong_total = await authed_client.post(url, json={"code": "x", "passed": 1, "total": 99})
    too_many = await authed_client.post(url, json={"code": "x", "passed": 9, "total": len(load_problems()["two-sum"].tests)})
    assert wrong_total.status_code == 422 and too_many.status_code == 422
