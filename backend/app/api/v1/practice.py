"""
LuminaLearn AI — Coding practice (sandbox) API.
Module: backend/app/api/v1/practice.py

Problems and results only: learner code runs in the browser (Pyodide), never on this server.
"""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.practice import (
    PracticeProblemDetail,
    PracticeProblemList,
    PracticeSubmissionRequest,
    PracticeSubmissionResponse,
)
from app.services import practice_service

router = APIRouter(prefix="/practice", tags=["Coding Practice Sandbox"])


@router.get("/problems", response_model=PracticeProblemList, summary="List practice problems with the learner's progress")
async def list_problems(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    return await practice_service.list_problems(db, current_user.id)


@router.get("/problems/{slug}", response_model=PracticeProblemDetail, summary="Get a problem, its tests and the judging harness")
async def get_problem(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    return await practice_service.problem_detail(db, current_user.id, slug)


@router.post("/problems/{slug}/submissions", response_model=PracticeSubmissionResponse, summary="Record the result of a test run")
async def submit(
    slug: str,
    payload: PracticeSubmissionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    return await practice_service.record_submission(
        db, current_user.id, slug, payload.code, payload.passed, payload.total, payload.language
    )
