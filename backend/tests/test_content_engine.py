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
from app.models.content import ContentCategory, Course, Lesson, Module, Subject, Topic
from app.models.user import User, UserRole
from scripts.seed_academic_content import seed_academic_content



@pytest.mark.asyncio
async def test_content_seeder_idempotency():
    """Verify seeder creates entities and second run skips existing records."""
    async with AsyncSessionLocal() as session:
        stats = await seed_academic_content(session)
        assert stats["categories_created"] == 0
        assert stats["categories_skipped"] == 4
        assert stats["subjects_skipped"] == 22
        assert stats["courses_skipped"] == 22
        assert stats["modules_skipped"] == 146
        assert stats["topics_skipped"] == 165
        assert stats["lessons_skipped"] == 12


@pytest.mark.asyncio
async def test_categories_endpoint(async_client: AsyncClient):
    """GET /api/v1/content/categories returns 4 top-level academic disciplines."""
    response = await async_client.get("/api/v1/content/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    slugs = [cat["slug"] for cat in data]
    assert "computer-science" in slugs
    assert "programming" in slugs
    assert "artificial-intelligence" in slugs
    assert "mathematics" in slugs


@pytest.mark.asyncio
async def test_subjects_list_and_filtering(async_client: AsyncClient):
    """GET /api/v1/content/subjects with optional filtering by category and search."""
    # List all 22 subjects
    response = await async_client.get("/api/v1/content/subjects")
    assert response.status_code == 200
    all_subjects = response.json()
    assert len(all_subjects) == 22

    # Filter by category
    cs_response = await async_client.get("/api/v1/content/subjects?category_slug=computer-science")
    assert cs_response.status_code == 200
    cs_subjects = cs_response.json()
    assert len(cs_subjects) == 6

    # Search filter
    search_response = await async_client.get("/api/v1/content/subjects?search=operating")
    assert search_response.status_code == 200
    search_results = search_response.json()
    assert len(search_results) == 1
    assert search_results[0]["slug"] == "operating-systems"


@pytest.mark.asyncio
async def test_subject_lookup_by_slug(async_client: AsyncClient):
    """GET /api/v1/content/subjects/{slug} returns detail and course outlines."""
    response = await async_client.get("/api/v1/content/subjects/operating-systems")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Operating Systems"
    assert data["slug"] == "operating-systems"
    assert len(data["courses"]) >= 1
    assert data["courses"][0]["slug"] == "operating-systems-fundamentals"


@pytest.mark.asyncio
async def test_invalid_subject_returns_404(async_client: AsyncClient):
    """GET /api/v1/content/subjects/{non_existent} returns 404."""
    response = await async_client.get("/api/v1/content/subjects/quantum-teleportation")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_course_retrieval(async_client: AsyncClient):
    """GET /api/v1/content/courses/{slug} returns course with modules and topics."""
    response = await async_client.get("/api/v1/content/courses/operating-systems-fundamentals")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "operating-systems-fundamentals"
    assert data["subject_slug"] == "operating-systems"
    assert len(data["modules"]) >= 9
    module_slugs = [m["slug"] for m in data["modules"]]
    assert "os-introduction" in module_slugs
    assert "os-processes-and-threads" in module_slugs


@pytest.mark.asyncio
async def test_invalid_course_returns_404(async_client: AsyncClient):
    """GET /api/v1/content/courses/{non_existent} returns 404."""
    response = await async_client.get("/api/v1/content/courses/unknown-course-12345")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_course_modules_endpoint(async_client: AsyncClient):
    """GET /api/v1/content/courses/{slug}/modules returns module list."""
    response = await async_client.get("/api/v1/content/courses/dbms-fundamentals/modules")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 10
    assert any(m["slug"] == "dbms-relational-model" for m in data)


@pytest.mark.asyncio
async def test_module_topics_endpoint(async_client: AsyncClient):
    """GET /api/v1/content/modules/{id}/topics returns topic list."""
    async with AsyncSessionLocal() as session:
        stmt = select(Module).where(Module.slug == "os-processes-and-threads")
        module = (await session.execute(stmt)).scalars().first()
        assert module is not None
        module_id = module.id

    response = await async_client.get(f"/api/v1/content/modules/{module_id}/topics")
    assert response.status_code == 200
    topics = response.json()
    assert len(topics) >= 2
    topic_slugs = [t["slug"] for t in topics]
    assert "process-control-block-lifecycle" in topic_slugs


@pytest.mark.asyncio
async def test_topic_retrieval(async_client: AsyncClient):
    """GET /api/v1/content/topics/{id} returns topic details with lessons."""
    async with AsyncSessionLocal() as session:
        stmt = select(Topic).where(Topic.slug == "process-control-block-lifecycle")
        topic = (await session.execute(stmt)).scalars().first()
        assert topic is not None
        topic_id = topic.id

    response = await async_client.get(f"/api/v1/content/topics/{topic_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "process-control-block-lifecycle"
    assert len(data["lessons"]) >= 1
    assert data["lessons"][0]["slug"] == "process-control-block-and-lifecycle"


@pytest.mark.asyncio
async def test_topic_lessons_endpoint(async_client: AsyncClient):
    """GET /api/v1/content/topics/{id}/lessons returns lesson summaries."""
    async with AsyncSessionLocal() as session:
        stmt = select(Topic).where(Topic.slug == "asymptotic-notations")
        topic = (await session.execute(stmt)).scalars().first()
        assert topic is not None
        topic_id = topic.id

    response = await async_client.get(f"/api/v1/content/topics/{topic_id}/lessons")
    assert response.status_code == 200
    lessons = response.json()
    assert len(lessons) >= 1
    assert lessons[0]["slug"] == "foundations-of-big-o-complexity"


@pytest.mark.asyncio
async def test_unauthenticated_user_cannot_access_lesson(async_client: AsyncClient):
    """GET /api/v1/content/lessons/{id} without token returns 401 Unauthorized."""
    fake_id = uuid.uuid4()
    response = await async_client.get(f"/api/v1/content/lessons/{fake_id}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_unverified_user_cannot_access_lesson(async_client: AsyncClient):
    """GET /api/v1/content/lessons/{id} with unverified account returns 403 Forbidden."""
    async with AsyncSessionLocal() as session:
        # Create unverified user
        unverified_user = User(
            id=uuid.uuid4(),
            email=f"unverified_{uuid.uuid4().hex[:8]}@example.com",
            password_hash="fakehash",
            full_name="Unverified Learner",
            role=UserRole.STUDENT,
            is_active=True,
            is_verified=False,
        )
        session.add(unverified_user)

        # Get existing seeded lesson
        stmt = select(Lesson).limit(1)
        lesson = (await session.execute(stmt)).scalars().first()
        assert lesson is not None
        lesson_id = lesson.id
        await session.commit()

    token = create_access_token(subject=str(unverified_user.id))
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.get(f"/api/v1/content/lessons/{lesson_id}", headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "EMAIL_VERIFICATION_REQUIRED"


@pytest.mark.asyncio
async def test_verified_user_can_access_lesson(async_client: AsyncClient):
    """GET /api/v1/content/lessons/{id} with verified account returns 200 and full content."""
    async with AsyncSessionLocal() as session:
        # Create verified user
        verified_user = User(
            id=uuid.uuid4(),
            email=f"verified_{uuid.uuid4().hex[:8]}@example.com",
            password_hash="fakehash",
            full_name="Verified Learner",
            role=UserRole.STUDENT,
            is_active=True,
            is_verified=True,
        )
        session.add(verified_user)

        # Get existing seeded lesson
        stmt = select(Lesson).where(Lesson.slug == "foundations-of-big-o-complexity")
        lesson = (await session.execute(stmt)).scalars().first()
        assert lesson is not None
        lesson_id = lesson.id
        await session.commit()

    token = create_access_token(subject=str(verified_user.id))
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.get(f"/api/v1/content/lessons/{lesson_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "foundations-of-big-o-complexity"
    assert data["title"] == "Foundations of Big-O Complexity"
    assert len(data["learning_objectives"]) >= 2
    assert "# Foundations of Big-O Complexity" in data["content"]
    assert data["subject_slug"] == "data-structures-and-algorithms"


@pytest.mark.asyncio
async def test_invalid_lesson_returns_404_for_verified_user(async_client: AsyncClient):
    """GET /api/v1/content/lessons/{non_existent} returns 404 for verified user."""
    async with AsyncSessionLocal() as session:
        verified_user = User(
            id=uuid.uuid4(),
            email=f"verified_{uuid.uuid4().hex[:8]}@example.com",
            password_hash="fakehash",
            full_name="Verified Learner",
            role=UserRole.STUDENT,
            is_active=True,
            is_verified=True,
        )
        session.add(verified_user)
        await session.commit()

    token = create_access_token(subject=str(verified_user.id))
    headers = {"Authorization": f"Bearer {token}"}

    random_lesson_id = uuid.uuid4()
    response = await async_client.get(f"/api/v1/content/lessons/{random_lesson_id}", headers=headers)
    assert response.status_code == 404
