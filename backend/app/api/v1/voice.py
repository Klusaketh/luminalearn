"""
LuminaLearn AI — Full-Duplex Real-Time Voice Endpoint.
Module: backend/app/api/v1/voice.py

The wire protocol and barge-in semantics are documented in app/services/voice_session.py.
"""

import re

from fastapi import APIRouter, WebSocket, status

from app.core.config import settings
from app.services.ai_runtime import (
    gemini_gateway,
    tutor_orchestrator,
    tutor_rate_limiter,
)
from app.services.voice_session import VoiceSession

router = APIRouter(prefix="/voice", tags=["Real-Time Voice Tutor"])

_LOCAL_ORIGIN = re.compile(r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$")


def origin_allowed(origin: str | None) -> bool:
    """CORS does not cover WebSockets, so browser origins are checked explicitly."""
    if origin is None:
        return True  # non-browser clients (CLI tools, tests) send no Origin header
    return bool(_LOCAL_ORIGIN.match(origin)) or origin in settings.BACKEND_CORS_ORIGINS


@router.websocket("/session")
async def voice_session(websocket: WebSocket) -> None:
    """Live Socratic voice tutoring with streaming speech and barge-in interruption."""
    if not origin_allowed(websocket.headers.get("origin")):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await websocket.accept()
    session = VoiceSession(websocket, orchestrator=tutor_orchestrator, gateway=gemini_gateway, limiter=tutor_rate_limiter)
    await session.run()
