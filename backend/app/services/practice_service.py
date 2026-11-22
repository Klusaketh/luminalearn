"""
LuminaLearn AI — Coding practice (sandbox) service.

Problems live in content/practice/problems/<slug>/ (see content/practice/README.md). Learner code runs
in the browser with Pyodide; this service serves problems and records learners' results.
"""

import json
import uuid
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import Integer, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Course, Module, Subject, Topic
from app.models.practice import PracticeSubmission

# backend/app/services -> repository root (also /srv in the Docker image, where content/ is copied).
PRACTICE_ROOT = Path(__file__).resolve().parents[3] / "content" / "practice"
PROBLEMS_ROOT = PRACTICE_ROOT / "problems"
RELATED_SUBJECT = "data-structures-and-algorithms"


@dataclass(frozen=True)
class PracticeProblem:
    slug: str
    title: str
    difficulty: str
    order: int
    tags: tuple[str, ...]
    related_topic: str | None
    function_name: str
    compare: str
    hints: tuple[str, ...]
    tests: tuple[dict[str, Any], ...]
    statement: str
    starter_code: str
    solution: str


def _load_problem(folder: Path) -> PracticeProblem:
    meta = json.loads((folder / "problem.json").read_text(encoding="utf-8"))
    return PracticeProblem(
        slug=folder.name,
        title=meta["title"],
        difficulty=meta["difficulty"],
        order=int(meta["order"]),
        tags=tuple(meta.get("tags", [])),
        related_topic=meta.get("related_topic"),
        function_name=meta["function"],
        compare=meta.get("compare", "exact"),
        hints=tuple(meta["hints"]),
        tests=tuple(meta["tests"]),
        statement=(folder / "statement.md").read_text(encoding="utf-8"),
        starter_code=(folder / "starter.py").read_text(encoding="utf-8"),
        solution=(folder / "solution.py").read_text(encoding="utf-8"),
    )


@lru_cache(maxsize=1)
def load_problems() -> dict[str, PracticeProblem]:
    """All problems by slug, in display order. Read once per process."""
    folders = sorted(p for p in PROBLEMS_ROOT.iterdir() if (p / "problem.json").is_file()) if PROBLEMS_ROOT.is_dir() else []
    problems = sorted((_load_problem(f) for f in folders), key=lambda p: (p.order, p.slug))
    return {p.slug: p for p in problems}


@lru_cache(maxsize=1)
def harness_source() -> str:
    return (PRACTICE_ROOT / "harness.py").read_text(encoding="utf-8")


def get_problem(slug: str) -> PracticeProblem:
    problem = load_problems().get(slug)
    if problem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PROBLEM_NOT_FOUND")
    return problem


async def _progress(db: AsyncSession, user_id: uuid.UUID) -> dict[str, dict[str, Any]]:
    """Per problem: attempts, best passed count, and whether any run passed every test."""
    rows = await db.execute(
        select(
            PracticeSubmission.problem_slug,
            func.count(PracticeSubmission.id),
            func.max(PracticeSubmission.passed),
            func.max(cast(PracticeSubmission.solved, Integer)),
        )
        .where(PracticeSubmission.user_id == user_id)
        .group_by(PracticeSubmission.problem_slug)
    )
    return {slug: {"attempts": n, "best_passed": best or 0, "solved": bool(solved)} for slug, n, best, solved in rows.all()}


def _summary(problem: PracticeProblem, progress: dict[str, Any] | None) -> dict[str, Any]:
    progress = progress or {}
    return {
        "slug": problem.slug,
        "title": problem.title,
        "difficulty": problem.difficulty,
        "tags": list(problem.tags),
        "order": problem.order,
        "solved": progress.get("solved", False),
        "attempts": progress.get("attempts", 0),
    }


async def list_problems(db: AsyncSession, user_id: uuid.UUID) -> dict[str, Any]:
    progress = await _progress(db, user_id)
    problems = [_summary(p, progress.get(p.slug)) for p in load_problems().values()]
    return {"problems": problems, "solved_count": sum(p["solved"] for p in problems), "total_count": len(problems)}


async def _related_topic(db: AsyncSession, slug: str | None) -> dict[str, Any] | None:
    if not slug:
        return None
    row = await db.execute(
        select(Topic.id, Topic.title)
        .join(Module, Topic.module_id == Module.id)
        .join(Course, Module.course_id == Course.id)
        .join(Subject, Course.subject_id == Subject.id)
        .where(Subject.slug == RELATED_SUBJECT, Topic.slug == slug)
        .limit(1)
    )
    found = row.first()
    return {"id": found.id, "title": found.title} if found else None


async def problem_detail(db: AsyncSession, user_id: uuid.UUID, slug: str) -> dict[str, Any]:
    problem = get_problem(slug)
    progress = (await _progress(db, user_id)).get(slug, {})
    return {
        **_summary(problem, progress),
        "statement": problem.statement,
        "starter_code": problem.starter_code,
        "function_name": problem.function_name,
        "compare": problem.compare,
        "hints": list(problem.hints),
        "tests": list(problem.tests),
        "harness": harness_source(),
        "related_topic": await _related_topic(db, problem.related_topic),
        "best_passed": progress.get("best_passed", 0),
    }


async def record_submission(db: AsyncSession, user_id: uuid.UUID, slug: str, code: str, passed: int, total: int) -> dict[str, Any]:
    problem = get_problem(slug)
    if total != len(problem.tests) or passed > total:
        raise HTTPException(status_code=422, detail="RESULT_DOES_NOT_MATCH_PROBLEM")
    db.add(PracticeSubmission(user_id=user_id, problem_slug=slug, code=code, passed=passed, total=total, solved=passed == total))
    await db.commit()
    progress = (await _progress(db, user_id))[slug]
    return {"solved": progress["solved"], "attempts": progress["attempts"], "best_passed": progress["best_passed"], "total": total}
