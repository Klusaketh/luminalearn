"""Retention forecasting math, quiz mastery extensions, and the Redis/RAG resilience layers."""
import math
import os
import sys
import uuid
from itertools import pairwise
from typing import Any

import pytest
from httpx import AsyncClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import app.core.redis as redis_module
from ai.rag.curriculum_rag import CurriculumRAGService, tokenize
from app.core.database import AsyncSessionLocal
from app.core.security import create_access_token
from app.models.quiz import QuizQuestion
from app.models.user import User, UserRole
from ml.models.retention_forecaster import RetentionForecaster

# --------------------------------------------------------------------------- forecaster


def test_half_life_matches_stability_formula() -> None:
    forecaster = RetentionForecaster()
    stability = forecaster.initial_stability(0.5)
    assert stability == pytest.approx(1.5 + 6.0 * 0.5)
    assert forecaster.half_life_days(0.5) == pytest.approx(stability * math.log(2))
    assert forecaster.retention(forecaster.half_life_days(0.5), stability) == pytest.approx(0.5)


def test_spaced_reviews_expand_and_dominate_no_review_curve() -> None:
    forecaster = RetentionForecaster()
    data = forecaster.forecast(0.4, horizon_days=30, points=61)
    reviews = data["review_days"]
    gaps = [b - a for a, b in pairwise([0.0, *reviews])]
    assert all(later > earlier for earlier, later in pairwise(gaps))  # expanding intervals
    assert all(s >= n for s, n in zip(data["spaced"], data["no_review"], strict=True))
    assert data["no_review"] == sorted(data["no_review"], reverse=True)  # monotone forgetting
    assert min(data["spaced"]) >= data["target_retention"] - 1e-3


def test_higher_mastery_forgets_more_slowly() -> None:
    forecaster = RetentionForecaster()
    assert forecaster.half_life_days(0.9) > forecaster.half_life_days(0.1)


def test_forecaster_rejects_invalid_parameters() -> None:
    with pytest.raises(ValueError):
        RetentionForecaster(review_multiplier=0.5)
    with pytest.raises(ValueError):
        RetentionForecaster().forecast(0.5, points=1)


# --------------------------------------------------------------------------- quiz extensions


async def _student() -> tuple[str, uuid.UUID]:
    async with AsyncSessionLocal() as session:
        user = User(
            id=uuid.uuid4(),
            email=f"radar_{uuid.uuid4().hex[:8]}@luminalearn.ai",
            password_hash="argon2id_mock_hash",
            full_name="Radar Student",
            role=UserRole.STUDENT,
            is_active=True,
            is_verified=True,
        )
        session.add(user)
        await session.commit()
        return create_access_token(subject=str(user.id)), user.id


@pytest.mark.asyncio
async def test_submit_reports_level_up_and_mastery_report_has_forecast(async_client: AsyncClient) -> None:
    token, _ = await _student()
    headers = {"Authorization": f"Bearer {token}"}
    session = (await async_client.post(
        "/api/v1/quiz/generate", headers=headers,
        json={"topic": "Linear Algebra", "difficulty": "intermediate", "question_count": 3},
    )).json()

    level_ups = []
    for question in session["questions"]:
        async with AsyncSessionLocal() as db:
            db_question = await db.get(QuizQuestion, uuid.UUID(question["id"]))
            assert db_question is not None
            answer = db_question.correct_answer
        result = (await async_client.post(
            "/api/v1/quiz/submit-answer", headers=headers,
            json={"session_id": session["id"], "question_id": question["id"], "selected_answer": answer, "latency_ms": 900},
        )).json()
        assert result["retention_level"] in {"Novice", "Developing", "Competent", "Mastered"}
        level_ups.append(result["level_up"])
    assert any(level_ups)  # three correct answers from P(L)=0.10 climb at least one tier

    report = (await async_client.get("/api/v1/quiz/mastery/Linear Algebra", headers=headers)).json()
    forecast = report["retention_forecast"]
    assert len(forecast["days"]) == len(forecast["spaced"]) == len(forecast["no_review"]) == 61

    radar = (await async_client.get("/api/v1/quiz/masteries", headers=headers)).json()
    assert radar[0]["topic_title"] == "Linear Algebra"
    assert radar[0]["total_attempts"] == 3


@pytest.mark.asyncio
async def test_masteries_requires_authentication(async_client: AsyncClient) -> None:
    assert (await async_client.get("/api/v1/quiz/masteries")).status_code == 401


def test_curated_fallback_questions_are_copies_not_shared_state() -> None:
    from app.services.quiz_service import CURATED_BENCHMARKS, quiz_service

    questions = quiz_service._get_curated_fallback_questions("Calculus", 7)
    questions[0]["source_reference"] = "mutated"
    assert "source_reference" not in CURATED_BENCHMARKS["mathematics"][0]
    assert len(questions) == 7


def test_generated_question_validation_drops_inconsistent_items() -> None:
    from app.services.quiz_service import QuizService

    valid = QuizService._validate_generated_question({
        "prompt": "2 + 2?", "options": ["3", "4", "4", "5"], "correct_answer": "4",
        "irt_difficulty": 9, "blooms_level": "Remembering",
    })
    assert valid is not None
    assert valid["options"] == ["3", "4", "5"]  # duplicates removed
    assert valid["irt_difficulty"] == 3.0  # clamped into the IRT range
    assert valid["blooms_level"] == "remembering"
    assert QuizService._validate_generated_question({"prompt": "?", "options": ["a", "b"], "correct_answer": "c"}) is None
    assert QuizService._validate_generated_question("not a dict") is None


# --------------------------------------------------------------------------- resilience


class FlakyRedis:
    """Fake server that can be switched off and records what it stores."""

    def __init__(self) -> None:
        self.up = True
        self.store: dict[str, str] = {}

    def _check(self) -> None:
        if not self.up:
            raise ConnectionError("redis down")

    async def get(self, key: str) -> Any:
        self._check()
        return self.store.get(key)

    async def set(self, key: str, value: str, ex: int) -> None:
        self._check()
        self.store[key] = value

    async def delete(self, key: str) -> int:
        self._check()
        return 1 if self.store.pop(key, None) is not None else 0


@pytest.mark.asyncio
async def test_redis_outage_is_absorbed_and_reconciled(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FlakyRedis()
    monkeypatch.setattr(redis_module, "_real_redis", fake)
    client = redis_module.RedisClientWrapper()

    await client.setex("refresh_token:u1", 600, "old-token")
    assert fake.store["refresh_token:u1"] == "old-token"

    fake.up = False
    await client.delete("refresh_token:u1")  # e.g. logout while Redis is down
    await client.setex("otp:a@b.c", 600, "state-2")
    assert await client.get("otp:a@b.c") == "state-2"  # served from memory during the outage

    fake.up = True
    client._suspended_until = 0.0  # the 30 s breaker window has elapsed
    assert await client.get("refresh_token:u1") is None  # revoked token is NOT resurrected
    assert fake.store.get("otp:a@b.c") == "state-2"  # outage writes were replayed
    assert "refresh_token:u1" not in fake.store


def test_rag_retrieval_grounds_and_abstains() -> None:
    rag = CurriculumRAGService(documents_dir=None)
    top = rag.retrieve("How do I find eigenvalues of a 2x2 matrix?", top_k=1)
    assert top and "Eigen" in top[0].section
    assert rag.has_sufficient_grounding(top)
    assert rag.retrieve("best pizza recipe in naples") == []
    assert tokenize("Eigenvalues") == tokenize("eigenvalue")


def test_rag_ingests_markdown_course_notes(tmp_path: Any) -> None:
    (tmp_path / "notes.md").write_text(
        "---\ntopic: Graph Coloring\nsubject: Discrete Mathematics\nsource: Week 9 Notes\n---\n"
        "## Greedy coloring\nA greedy coloring assigns each vertex the smallest color not used by its neighbours, "
        "visiting vertices in a fixed order, and never uses more than max degree plus one colors.\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text("ignored", encoding="utf-8")
    rag = CurriculumRAGService(documents_dir=tmp_path)
    hit = rag.retrieve("greedy graph coloring of vertices", top_k=1)
    assert hit and hit[0].source_title == "Week 9 Notes" and hit[0].section == "Greedy coloring"
    assert all(chunk.content != "ignored" for chunk in rag.chunks)
