"""
LuminaLearn AI — Socratic Tutor Service.
Module: backend/app/services/tutor_service.py

Personalizes learner turns (BKT mastery, VARK modality) and renders the faculty's event
stream as Server-Sent Events.
"""

import json
import logging
import uuid
from collections.abc import AsyncIterator

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.agents import (
    DialogueTurn,
    Modality,
    SocraticOrchestrator,
    TutorEvent,
    TutorRequest,
)
from app.core.config import settings
from app.core.rate_limit import SlidingWindowRateLimiter
from app.models.quiz import StudentTopicMastery
from app.models.user import User, VARKModality
from app.schemas.tutor import TutorChatRequest

logger = logging.getLogger("luminalearn.tutor_service")

MODALITY_BY_ENUM: dict[VARKModality, Modality] = {
    VARKModality.VISUAL: "visual",
    VARKModality.AUDITORY: "auditory",
    VARKModality.READ_WRITE: "read_write",
    VARKModality.KINESTHETIC: "kinesthetic",
}


def encode_sse(event: TutorEvent) -> bytes:
    """One SSE frame. json.dumps escapes newlines, so `data:` always stays on one line."""
    return f"event: {event.type}\ndata: {json.dumps(event.data, ensure_ascii=False)}\n\n".encode()


def rate_limit_key(user: User) -> str:
    """HTTP turns and voice turns share one budget per learner."""
    return f"user:{user.id}"


def enforce_rate_limit(limiter: SlidingWindowRateLimiter, user: User) -> None:
    retry_after = limiter.hit(rate_limit_key(user), settings.TUTOR_RATE_LIMIT_AUTHENTICATED)
    if retry_after is not None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="You've reached the tutoring limit for now. Take a short break and try again.",
            headers={"Retry-After": str(int(retry_after))},
        )


class TutorService:
    """Bridges HTTP / WebSocket payloads and the multi-agent orchestrator."""

    async def lookup_mastery(self, db: AsyncSession, user_id: uuid.UUID, topic: str | None) -> float | None:
        """Latest BKT mastery for the topic, matched case-insensitively; None when never assessed."""
        if not topic or not topic.strip():
            return None
        stmt = (
            select(StudentTopicMastery.current_mastery)
            .where(
                StudentTopicMastery.user_id == user_id,
                func.lower(StudentTopicMastery.topic_title) == topic.strip().lower(),
            )
            .limit(1)
        )
        value = (await db.execute(stmt)).scalar_one_or_none()
        return float(value) if value is not None else None

    async def build_request(
        self,
        db: AsyncSession,
        payload: TutorChatRequest,
        user: User | None,
    ) -> TutorRequest:
        modality_enum = payload.modality or (user.preferred_modality if user else None)
        mastery = await self.lookup_mastery(db, user.id, payload.topic) if user else None
        return TutorRequest(
            message=payload.message.strip(),
            topic=payload.topic.strip() if payload.topic else None,
            modality=MODALITY_BY_ENUM[modality_enum] if modality_enum else "read_write",
            mastery=mastery,
            hint_level=payload.hint_level,
            history=[DialogueTurn(role=turn.role, text=turn.text) for turn in payload.history],
            channel="chat",
            requested_agent=payload.agent,
            learner_name=user.full_name.split(" ")[0] if user and user.full_name else None,
        )

    async def sse_stream(self, orchestrator: SocraticOrchestrator, tutor_request: TutorRequest) -> AsyncIterator[bytes]:
        try:
            async for event in orchestrator.stream(tutor_request):
                yield encode_sse(event)
        except Exception:
            # The stream has already started, so an HTTP error is impossible: end with a typed frame.
            logger.exception("Tutor stream failed.")
            yield encode_sse(TutorEvent("done", {
                "text": "",
                "agent": None,
                "engine": "error",
                "error": "The tutor hit an unexpected problem. Please send your message again.",
            }))


tutor_service = TutorService()
