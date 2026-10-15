import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.onboarding import StudentOnboarding


class OnboardingRepository:
    """Async OnboardingRepository handling database operations for StudentOnboarding profile entity."""

    async def get_by_user_id(self, db: AsyncSession, user_id: uuid.UUID) -> StudentOnboarding | None:
        """Fetch onboarding profile for a specific user."""
        result = await db.execute(select(StudentOnboarding).where(StudentOnboarding.user_id == user_id))
        return result.scalars().first()

    async def create_or_update(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        goals: list[str],
        interests: list[str],
        selected_subjects: list[str],
        assessment_score: float,
        strengths: list[str],
        weak_areas: list[str],
        recommended_weekly_hours: int,
        suggested_starting_topic: str
    ) -> StudentOnboarding:
        """Create or update student onboarding profile record."""
        existing = await self.get_by_user_id(db, user_id)
        if existing:
            existing.goals = goals
            existing.interests = interests
            existing.selected_subjects = selected_subjects
            existing.assessment_score = assessment_score
            existing.strengths = strengths
            existing.weak_areas = weak_areas
            existing.recommended_weekly_hours = recommended_weekly_hours
            existing.suggested_starting_topic = suggested_starting_topic
            existing.is_completed = True
            db.add(existing)
            await db.commit()
            await db.refresh(existing)
            return existing

        profile = StudentOnboarding(
            user_id=user_id,
            goals=goals,
            interests=interests,
            selected_subjects=selected_subjects,
            assessment_score=assessment_score,
            strengths=strengths,
            weak_areas=weak_areas,
            recommended_weekly_hours=recommended_weekly_hours,
            suggested_starting_topic=suggested_starting_topic,
            is_completed=True
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        return profile


onboarding_repository = OnboardingRepository()
