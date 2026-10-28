"""
LuminaLearn AI — Adaptive Quizzing & Predictive Mastery API Endpoints.
Module: backend/app/api/v1/quiz.py
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.quiz import (
    QuizGenerateRequest,
    QuizHistoryResponse,
    QuizMasteryResponse,
    QuizSessionDetail,
    QuizSubmitAnswerRequest,
    QuizSubmitAnswerResponse,
    TopicMasterySummary,
)
from app.services.quiz_service import quiz_service

router = APIRouter(prefix="/quiz", tags=["Adaptive Quizzing & Predictive Accuracy"])


@router.post(
    "/generate",
    response_model=QuizSessionDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Adaptive Topic Quiz Session"
)
async def generate_quiz(
    request: QuizGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Generates a personalized adaptive quiz session for any user-specified topic.
    Questions span Bloom's Taxonomy and include Item Response Theory (IRT 2PL) parameters.
    """
    return await quiz_service.generate_quiz_session(
        db=db,
        user_id=current_user.id,
        request=request
    )


@router.get(
    "/history",
    response_model=QuizHistoryResponse,
    summary="Get Paginated Quiz History for Current Student"
)
async def get_quiz_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retrieves paginated quiz attempt history and session scores for the authenticated student.
    Enforces user isolation at query level.
    """
    return await quiz_service.get_quiz_history(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size
    )


@router.get(
    "/session/{session_id}",
    response_model=QuizSessionDetail,
    summary="Get Quiz Session Details"
)
async def get_quiz_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retrieves the questions and state of an existing quiz session.
    Enforces user ownership.
    """
    return await quiz_service.get_quiz_session(
        db=db,
        session_id=session_id,
        user_id=current_user.id
    )


@router.post(
    "/submit-answer",
    response_model=QuizSubmitAnswerResponse,
    summary="Submit Answer for Real-Time BKT Grading & Misconception Analysis"
)
@router.post(
    "/submit",
    response_model=QuizSubmitAnswerResponse,
    summary="Submit Answer (Contract Alias)"
)
async def submit_answer(
    request: QuizSubmitAnswerRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Evaluates student response, applies Bayesian Knowledge Tracing (BKT) probability update,
    detects conceptual misconceptions, and returns pedagogical explanations.
    Submissions are strictly idempotent.
    """
    return await quiz_service.submit_question_answer(
        db=db,
        user_id=current_user.id,
        request=request
    )


@router.get(
    "/masteries",
    response_model=list[TopicMasterySummary],
    summary="Get Bayesian Mastery Across All Assessed Topics"
)
async def list_topic_masteries(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Every topic the student has been assessed on, strongest first (knowledge radar data)."""
    return await quiz_service.get_topic_masteries(db=db, user_id=current_user.id)


@router.get(
    "/mastery/{topic_title}",
    response_model=QuizMasteryResponse,
    summary="Get Student Bayesian Mastery Report for a Topic"
)
async def get_topic_mastery(
    topic_title: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retrieves student's current Bayesian mastery score, predicted accuracy,
    retention classification, and historical attempt trajectory.
    """
    return await quiz_service.get_topic_mastery_report(
        db=db,
        user_id=current_user.id,
        topic_title=topic_title
    )

