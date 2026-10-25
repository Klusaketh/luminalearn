"""
LuminaLearn AI — Multi-Agent Socratic Tutor API Endpoints.
Module: backend/app/api/v1/tutor.py
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ai.agents import AGENT_NAMES, AGENT_PROFILES
from ai.llm import LLMUnavailableError, pcm_to_wav
from ai.prompts import PROMPT_VERSION
from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.tutor import (
    AgentProfileResponse,
    TutorChatRequest,
    TutorSpeakRequest,
    TutorStatusResponse,
)
from app.services.ai_runtime import (
    gemini_gateway,
    tutor_orchestrator,
    tutor_rate_limiter,
)
from app.services.speech_text import speech_text
from app.services.tutor_service import (
    enforce_rate_limit,
    tutor_service,
)

# Tutoring is part of the signed-in workspace: every route requires a verified session.
router = APIRouter(
    prefix="/tutor",
    tags=["Multi-Agent Socratic Tutor"],
    dependencies=[Depends(get_current_active_user)],
)


def _agent_profiles() -> list[AgentProfileResponse]:
    return [
        AgentProfileResponse(name=name, display_name=AGENT_PROFILES[name]["display_name"], summary=AGENT_PROFILES[name]["summary"])
        for name in AGENT_NAMES
    ]


@router.get(
    "/status",
    response_model=TutorStatusResponse,
    summary="AI Tutor Capabilities & Gateway Health"
)
async def tutor_status() -> Any:
    """Reports whether live Gemini generation and server speech are available, plus per-model health."""
    return TutorStatusResponse(
        llm_enabled=gemini_gateway.enabled,
        speech_enabled=gemini_gateway.speech_enabled,
        prompt_version=PROMPT_VERSION,
        gateway=gemini_gateway.status(),
        agents=_agent_profiles(),
        voice_websocket_path="/api/v1/voice/session",
    )


@router.get(
    "/agents",
    response_model=list[AgentProfileResponse],
    summary="List the Socratic Faculty Specialists"
)
async def list_agents() -> Any:
    """The specialists the Supervisor can route a learner turn to."""
    return _agent_profiles()


@router.post(
    "/chat/stream",
    summary="Stream a Socratic Tutoring Turn (Server-Sent Events)",
    response_class=StreamingResponse,
)
async def stream_chat(
    payload: TutorChatRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
) -> StreamingResponse:
    """
    Routes the turn through the Supervisor to one specialist and streams events:
    `route`, `citations`, optional `diagnostics`, many `delta`, optional `hints` / `interactive`, then `done`.
    Every turn is personalized with the learner's BKT mastery and VARK modality.
    """
    enforce_rate_limit(tutor_rate_limiter, user)
    # Resolve personalization before streaming begins: the DB session is released when this handler returns.
    tutor_request = await tutor_service.build_request(db, payload, user)
    return StreamingResponse(
        tutor_service.sse_stream(tutor_orchestrator, tutor_request),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post(
    "/speak",
    summary="Synthesize Tutor Speech (Gemini TTS)",
    responses={200: {"content": {"audio/wav": {}}}, 503: {"description": "Server voice unavailable"}},
)
async def speak(
    payload: TutorSpeakRequest,
    user: User = Depends(get_current_active_user),
) -> Response:
    """Returns WAV audio for a tutor message. Clients fall back to browser speech on 503."""
    enforce_rate_limit(tutor_rate_limiter, user)
    spoken = speech_text(payload.text)
    if not spoken or not gemini_gateway.speech_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="SERVER_VOICE_UNAVAILABLE")
    try:
        audio = await gemini_gateway.synthesize_speech(spoken)
    except LLMUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="SERVER_VOICE_UNAVAILABLE") from exc
    return Response(
        content=pcm_to_wav(audio.pcm, audio.sample_rate),
        media_type="audio/wav",
        headers={"X-TTS-Model": audio.model, "Cache-Control": "no-store"},
    )
