import os
import sys
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.core.database import AsyncSessionLocal
from app.core.security import create_access_token
from app.models.quiz import QuizAttempt, QuizQuestion
from app.models.user import User, UserRole


async def create_test_student(verified: bool = True) -> tuple[str, uuid.UUID]:
    """Helper to create a test student user and generate a valid access token."""
    async with AsyncSessionLocal() as session:
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            email=f"quiz_student_{uuid.uuid4().hex[:8]}@luminalearn.ai",
            password_hash="argon2id_mock_hash",
            full_name="Quiz Test Student",
            role=UserRole.STUDENT,
            is_active=True,
            is_verified=verified,
        )
        session.add(user)
        await session.commit()

        token = create_access_token(subject=str(user.id))
        return token, user.id


@pytest.mark.asyncio
async def test_unauthenticated_cannot_generate_quiz(async_client: AsyncClient):
    """POST /api/v1/quiz/generate requires authentication."""
    response = await async_client.post(
        "/api/v1/quiz/generate",
        json={"topic": "Calculus", "difficulty": "intermediate", "question_count": 5}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_generate_quiz_success(async_client: AsyncClient):
    """Verified student generates adaptive quiz and receives questions with withheld answers."""
    token, _ = await create_test_student(verified=True)
    response = await async_client.post(
        "/api/v1/quiz/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={"topic": "Linear Algebra", "difficulty": "intermediate", "question_count": 5}
    )
    assert response.status_code == 201
    data = response.json()

    assert data["topic_title"] == "Linear Algebra"
    assert data["difficulty_level"] == "intermediate"
    assert data["total_questions"] == 5
    assert data["status"] == "in_progress"
    assert data["initial_mastery"] == 0.10
    assert len(data["questions"]) == 5

    # Verify answers are withheld from student view
    for q in data["questions"]:
        assert "prompt" in q
        assert len(q["options"]) >= 2
        assert "blooms_level" in q
        assert "correct_answer" not in q
        assert "explanation" not in q


@pytest.mark.asyncio
async def test_submit_correct_answer_updates_bkt(async_client: AsyncClient):
    """Submitting correct answer increases mastery and returns educational explanation."""
    token, _ = await create_test_student(verified=True)

    # 1. Generate Session
    gen_res = await async_client.post(
        "/api/v1/quiz/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={"topic": "Mathematics", "difficulty": "intermediate", "question_count": 5}
    )
    assert gen_res.status_code == 201
    session_data = gen_res.json()
    session_id = session_data["id"]
    q1 = session_data["questions"][0]

    # Look up correct answer from DB for testing
    async with AsyncSessionLocal() as db:
        db_q = await db.get(QuizQuestion, uuid.UUID(q1["id"]))
        assert db_q is not None
        correct_ans = db_q.correct_answer

    # 2. Submit Correct Answer
    sub_res = await async_client.post(
        "/api/v1/quiz/submit-answer",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "session_id": session_id,
            "question_id": q1["id"],
            "selected_answer": correct_ans,
            "latency_ms": 3200
        }
    )
    assert sub_res.status_code == 200
    sub_data = sub_res.json()

    assert sub_data["is_correct"] is True
    assert sub_data["correct_answer"] == correct_ans
    assert sub_data["posterior_mastery"] > sub_data["prior_mastery"]
    assert sub_data["next_opportunity_mastery"] > sub_data["posterior_mastery"]
    assert sub_data["explanation"] != ""


@pytest.mark.asyncio
async def test_submit_incorrect_answer_records_misconception(async_client: AsyncClient):
    """Submitting wrong answer decreases posterior mastery and flags misconception."""
    token, _ = await create_test_student(verified=True)

    gen_res = await async_client.post(
        "/api/v1/quiz/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={"topic": "Mathematics", "difficulty": "intermediate", "question_count": 5}
    )
    session_data = gen_res.json()
    session_id = session_data["id"]
    q1 = session_data["questions"][0]

    # Select an incorrect option
    async with AsyncSessionLocal() as db:
        db_q = await db.get(QuizQuestion, uuid.UUID(q1["id"]))
        assert db_q is not None
        wrong_ans = next(opt for opt in db_q.options if opt != db_q.correct_answer)

    sub_res = await async_client.post(
        "/api/v1/quiz/submit-answer",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "session_id": session_id,
            "question_id": q1["id"],
            "selected_answer": wrong_ans,
            "latency_ms": 5400
        }
    )
    assert sub_res.status_code == 200
    sub_data = sub_res.json()

    assert sub_data["is_correct"] is False
    assert sub_data["posterior_mastery"] < sub_data["prior_mastery"]
    assert sub_data["detected_misconception"] is not None


@pytest.mark.asyncio
async def test_submission_idempotency_prevents_double_counting(async_client: AsyncClient):
    """Submitting duplicate answers to same question returns identical attempt without mutating BKT."""
    token, _ = await create_test_student(verified=True)

    gen_res = await async_client.post(
        "/api/v1/quiz/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={"topic": "Linear Algebra", "difficulty": "intermediate", "question_count": 3}
    )
    session_data = gen_res.json()
    session_id = session_data["id"]
    q1 = session_data["questions"][0]

    payload = {
        "session_id": session_id,
        "question_id": q1["id"],
        "selected_answer": q1["options"][0],
        "latency_ms": 2100
    }

    # First submission
    res1 = await async_client.post(
        "/api/v1/quiz/submit-answer",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )
    assert res1.status_code == 200
    data1 = res1.json()

    # Second identical submission
    res2 = await async_client.post(
        "/api/v1/quiz/submit-answer",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )
    assert res2.status_code == 200
    data2 = res2.json()

    # Must return identical attempt ID and unchanged score
    assert data1["attempt_id"] == data2["attempt_id"]
    assert data1["posterior_mastery"] == data2["posterior_mastery"]
    assert data1["session_score"] == data2["session_score"]

    # Verify only ONE attempt exists in database
    async with AsyncSessionLocal() as db:
        attempts = (
            await db.execute(
                select(QuizAttempt).where(
                    QuizAttempt.session_id == uuid.UUID(session_id),
                    QuizAttempt.question_id == uuid.UUID(q1["id"])
                )
            )
        ).scalars().all()
        assert len(attempts) == 1


@pytest.mark.asyncio
async def test_cross_student_authorization_guard(async_client: AsyncClient):
    """Student B cannot access or submit answers to Student A's quiz session."""
    token_a, _ = await create_test_student(verified=True)
    token_b, _ = await create_test_student(verified=True)

    # Student A creates session
    gen_res = await async_client.post(
        "/api/v1/quiz/generate",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"topic": "Probability", "difficulty": "intermediate", "question_count": 5}
    )
    session_id = gen_res.json()["id"]

    # Student B attempts to fetch Student A's session -> 403 Forbidden
    fetch_res = await async_client.get(
        f"/api/v1/quiz/session/{session_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert fetch_res.status_code == 403

    # Student B attempts to submit answer -> 403 Forbidden
    q_id = gen_res.json()["questions"][0]["id"]
    submit_res = await async_client.post(
        "/api/v1/quiz/submit-answer",
        headers={"Authorization": f"Bearer {token_b}"},
        json={
            "session_id": session_id,
            "question_id": q_id,
            "selected_answer": "Arbitrary Guess",
            "latency_ms": 1000
        }
    )
    assert submit_res.status_code == 403


@pytest.mark.asyncio
async def test_topic_mastery_report_endpoint(async_client: AsyncClient):
    """GET /api/v1/quiz/mastery/{topic} returns student's BKT retention curve and stats."""
    token, _ = await create_test_student(verified=True)

    # Check baseline mastery before attempts
    res = await async_client.get(
        "/api/v1/quiz/mastery/Mathematics",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    data = res.json()

    assert data["topic_title"] == "Mathematics"
    assert data["current_mastery"] == 0.10
    assert data["retention_level"] == "Novice"
    assert isinstance(data["history"], list)


@pytest.mark.asyncio
async def test_quiz_history_endpoint_with_pagination(async_client: AsyncClient):
    """GET /api/v1/quiz/history returns paginated sessions for authenticated student."""
    token, _user_id = await create_test_student(verified=True)

    # Initially empty
    empty_res = await async_client.get(
        "/api/v1/quiz/history?page=1&page_size=5",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert empty_res.status_code == 200
    empty_data = empty_res.json()
    assert empty_data["total"] == 0
    assert empty_data["items"] == []

    # Generate two sessions
    await async_client.post(
        "/api/v1/quiz/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={"topic": "Algorithms", "difficulty": "intermediate", "question_count": 3}
    )
    await async_client.post(
        "/api/v1/quiz/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={"topic": "Calculus", "difficulty": "intermediate", "question_count": 3}
    )

    # Check history with pagination
    res = await async_client.get(
        "/api/v1/quiz/history?page=1&page_size=1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    assert len(data["items"]) == 1
    assert data["page"] == 1
    assert data["page_size"] == 1


@pytest.mark.asyncio
async def test_submit_contract_alias_and_mastery_persistence(async_client: AsyncClient):
    """POST /api/v1/quiz/submit works identically to /submit-answer and persists StudentTopicMastery."""
    from app.models.quiz import StudentTopicMastery
    token, user_id = await create_test_student(verified=True)

    # Generate session
    gen_res = await async_client.post(
        "/api/v1/quiz/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={"topic": "Linear Algebra", "difficulty": "intermediate", "question_count": 3}
    )
    session_data = gen_res.json()
    session_id = session_data["id"]
    q1 = session_data["questions"][0]

    # Get answer
    async with AsyncSessionLocal() as db:
        db_q = await db.get(QuizQuestion, uuid.UUID(q1["id"]))
        assert db_q is not None
        ans = db_q.correct_answer

    # Call /api/v1/quiz/submit (alias)
    sub_res = await async_client.post(
        "/api/v1/quiz/submit",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "session_id": session_id,
            "question_id": q1["id"],
            "selected_answer": ans,
            "latency_ms": 2500
        }
    )
    assert sub_res.status_code == 200
    sub_data = sub_res.json()
    assert sub_data["is_correct"] is True

    # Verify StudentTopicMastery table has an entry
    async with AsyncSessionLocal() as db:
        m_record = (
            await db.execute(
                select(StudentTopicMastery).where(
                    StudentTopicMastery.user_id == user_id,
                    StudentTopicMastery.topic_title == "Linear Algebra"
                )
            )
        ).scalar_one_or_none()
        assert m_record is not None
        assert m_record.total_attempts == 1
        assert m_record.correct_attempts == 1
        assert m_record.streak == 1
        assert m_record.current_mastery == sub_data["next_opportunity_mastery"]

