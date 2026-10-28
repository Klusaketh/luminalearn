from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.repositories.onboarding_repository import onboarding_repository
from app.schemas.onboarding import (
    DiagnosticQuestion,
    LearnerProfileResponse,
    OnboardingSubmitRequest,
    PersonalizedRoadmapResponse,
)
from app.services.onboarding_service import onboarding_service

router = APIRouter(prefix="/onboarding", tags=["Student Onboarding & Diagnostics"])


@router.get(
    "/questions",
    response_model=list[DiagnosticQuestion],
    summary="Get Diagnostic Assessment Questions",
    dependencies=[Depends(get_current_active_user)],
)
async def get_diagnostic_questions() -> Any:
    """Fetch the 10 diagnostic assessment questions."""
    return onboarding_service.get_diagnostic_questions()


@router.post(
    "/submit",
    response_model=LearnerProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Onboarding Choices & Diagnostic Quiz Answers"
)
async def submit_onboarding(
    payload: OnboardingSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Submit student goals, interests, selected subjects, and diagnostic assessment answers.
    Evaluates profile, computes score/strengths/weaknesses, and returns initial LearnerProfile.
    """
    profile = await onboarding_service.process_onboarding_submission(
        db,
        user_id=current_user.id,
        payload=payload
    )
    return profile


@router.get(
    "/profile",
    response_model=LearnerProfileResponse,
    summary="Get Authenticated Student Learner Profile"
)
async def get_learner_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Fetch onboarding profile of authenticated student."""
    profile = await onboarding_repository.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Onboarding profile not found. Please complete the onboarding wizard."
        )
    return profile


@router.get(
    "/roadmap",
    response_model=PersonalizedRoadmapResponse,
    summary="Get Personalized Study Roadmap"
)
async def get_personalized_roadmap(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Fetch personalized study roadmap based on onboarding diagnostic evaluation."""
    roadmap = await onboarding_service.get_user_roadmap(db, current_user.id)
    return roadmap
