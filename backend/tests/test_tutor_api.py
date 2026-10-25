"""Socratic tutor HTTP endpoints: sign-in enforcement, SSE contract, personalization, speech and rate limiting."""
import json
import uuid

import pytest
from httpx import AsyncClient

from app.core.database import AsyncSessionLocal
from app.core.rate_limit import SlidingWindowRateLimiter
from app.core.security import create_access_token
from app.models.quiz import StudentTopicMastery
from app.models.user import User, UserRole, VARKModality
from app.services.speech_text import speech_text


def parse_sse(body: str) -> list[tuple[str, dict]]:
    events = []
    for frame in body.strip().split("\n\n"):
        lines = dict(line.split(": ", 1) for line in frame.splitlines() if ": " in line)
        events.append((lines["event"], json.loads(lines["data"])))
    return events


async def create_student_with_mastery(topic: str, mastery: float) -> str:
    async with AsyncSessionLocal() as session:
        user = User(
            id=uuid.uuid4(),
            email=f"tutor_{uuid.uuid4().hex[:8]}@luminalearn.ai",
            password_hash="argon2id_mock_hash",
            full_name="Ada Lovelace",
            role=UserRole.STUDENT,
            preferred_modality=VARKModality.VISUAL,
            is_active=True,
            is_verified=True,
        )
        session.add(user)
        session.add(StudentTopicMastery(user_id=user.id, topic_title=topic, current_mastery=mastery))
        await session.commit()
        return create_access_token(subject=str(user.id))


@pytest.mark.asyncio
async def test_status_reports_offline_engines_and_agents(authed_client: AsyncClient):
    res = await authed_client.get("/api/v1/tutor/status")
    assert res.status_code == 200
    data = res.json()
    assert data["llm_enabled"] is False  # tests run hermetically
    assert data["voice_websocket_path"] == "/api/v1/voice/session"
    assert {a["name"] for a in data["agents"]} == {"socratic_tutor", "concept_explainer", "analogy_specialist", "code_diagnostic"}


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/api/v1/tutor/status", "/api/v1/tutor/agents"])
async def test_tutor_reads_require_sign_in(async_client: AsyncClient, path: str):
    assert (await async_client.get(path)).status_code == 401


@pytest.mark.asyncio
async def test_guests_cannot_chat_or_speak(async_client: AsyncClient):
    chat = await async_client.post("/api/v1/tutor/chat/stream", json={"message": "explain recursion"})
    speak = await async_client.post("/api/v1/tutor/speak", json={"text": "What is the base case?"})
    assert chat.status_code == 401
    assert speak.status_code == 401


@pytest.mark.asyncio
async def test_chat_stream_contract(authed_client: AsyncClient):
    res = await authed_client.post(
        "/api/v1/tutor/chat/stream",
        json={"message": "Find the derivative of $x^2 \\sin x$", "topic": "Calculus"},
    )
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/event-stream")
    events = parse_sse(res.text)
    names = [name for name, _ in events]
    assert names[0] == "route" and names[-1] == "done"
    assert "delta" in names and "hints" in names
    route, done = events[0][1], events[-1][1]
    assert route["agent"] == "socratic_tutor"
    assert done["engine"] == "offline"
    assert done["text"] == "".join(data["text"] for name, data in events if name == "delta")


@pytest.mark.asyncio
async def test_signed_in_learner_gets_mastery_and_vark_personalization(async_client: AsyncClient):
    token = await create_student_with_mastery("Calculus", 0.15)
    res = await async_client.post(
        "/api/v1/tutor/chat/stream",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Evaluate the integral of 2x from 0 to 3", "topic": "Calculus"},
    )
    route = parse_sse(res.text)[0][1]
    assert route["hint_tier"] == 2  # novice mastery starts on the scaffold rung
    assert "15%" in route["rationale"]
    assert route["modality"] == "visual"  # taken from the learner's VARK profile


@pytest.mark.asyncio
async def test_invalid_token_is_rejected(async_client: AsyncClient):
    res = await async_client.post(
        "/api/v1/tutor/chat/stream",
        headers={"Authorization": "Bearer not-a-real-token"},
        json={"message": "explain recursion"},
    )
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_chat_validation_rejects_empty_message(authed_client: AsyncClient):
    res = await authed_client.post("/api/v1/tutor/chat/stream", json={"message": ""})
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_speak_returns_503_when_server_voice_is_offline(authed_client: AsyncClient):
    res = await authed_client.post("/api/v1/tutor/speak", json={"text": "What is the base case?"})
    assert res.status_code == 503
    assert res.json()["detail"] == "SERVER_VOICE_UNAVAILABLE"


@pytest.mark.asyncio
async def test_rate_limit_returns_429_with_retry_after(authed_client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    import app.api.v1.tutor as tutor_api
    from app.core.config import settings

    monkeypatch.setattr(tutor_api, "tutor_rate_limiter", SlidingWindowRateLimiter(window_s=60))
    monkeypatch.setattr(settings, "TUTOR_RATE_LIMIT_AUTHENTICATED", 1)
    first = await authed_client.post("/api/v1/tutor/chat/stream", json={"message": "hi"})
    second = await authed_client.post("/api/v1/tutor/chat/stream", json={"message": "hi again"})
    assert first.status_code == 200
    assert second.status_code == 429
    assert int(second.headers["retry-after"]) >= 1


def test_speech_text_reads_math_and_strips_markdown():
    spoken = speech_text("**Nice.** Evaluate $\\int_0^2 x^2\\,dx$ [1].\n```python\nprint(1)\n```")
    assert "**" not in spoken and "$" not in spoken and "[1]" not in spoken
    assert "integral" in spoken and "squared" in spoken
    assert "code example on your screen" in spoken


def test_rate_limiter_window_and_zero_limit():
    limiter = SlidingWindowRateLimiter(window_s=60)
    assert limiter.hit("k", 2) is None
    assert limiter.hit("k", 2) is None
    assert limiter.hit("k", 2) is not None
    assert limiter.hit("other", 0) == 60.0
