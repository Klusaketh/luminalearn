import os
import sys
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from scripts.seed_academic_content import LEVELS, seed_academic_content
from scripts.subject_content import iter_topics, load_lessons, load_subject_catalog

from app.core.database import AsyncSessionLocal
from app.core.security import create_access_token
from app.models.content import Lesson, Module, Topic
from app.models.user import User, UserRole


@pytest.mark.asyncio
async def test_content_seeder_idempotency():
    """A sync brings the database up to date; a second sync over the same files changes nothing."""
    catalog = load_subject_catalog()
    topics = [topic for subject in catalog for (_, _, topic) in iter_topics(subject)]
    lesson_files = sum(len(load_lessons(subject["slug"])) for subject in catalog)
    async with AsyncSessionLocal() as session:
        await seed_academic_content(session)
    async with AsyncSessionLocal() as session:
        stats = await seed_academic_content(session)
    assert all(stats[f"{level}_created"] == 0 for level in LEVELS), stats
    assert all(stats[f"{level}_updated"] == 0 for level in LEVELS), stats
    assert stats["categories_skipped"] == 4
    assert stats["subjects_skipped"] == len(catalog) == 22
    assert stats["courses_skipped"] == sum(len(s["courses"]) for s in catalog)
    assert stats["modules_skipped"] == sum(len(c["modules"]) for s in catalog for c in s["courses"])
    assert stats["topics_skipped"] == len(topics)
    assert stats["lessons_skipped"] == lesson_files
    assert stats["topics_without_lesson"] == len(topics) - lesson_files


@pytest.mark.asyncio
async def test_categories_endpoint(authed_client: AsyncClient):
    """GET /api/v1/content/categories returns 4 top-level academic disciplines."""
    response = await authed_client.get("/api/v1/content/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    slugs = [cat["slug"] for cat in data]
    assert "computer-science" in slugs
    assert "programming" in slugs
    assert "artificial-intelligence" in slugs
    assert "mathematics" in slugs


@pytest.mark.asyncio
async def test_subjects_list_and_filtering(authed_client: AsyncClient):
    """GET /api/v1/content/subjects with optional filtering by category and search."""
    # List all 22 subjects
    response = await authed_client.get("/api/v1/content/subjects")
    assert response.status_code == 200
    all_subjects = response.json()
    assert len(all_subjects) == 22

    # Filter by category
    cs_response = await authed_client.get("/api/v1/content/subjects?category_slug=computer-science")
    assert cs_response.status_code == 200
    cs_subjects = cs_response.json()
    assert len(cs_subjects) == 6

    # Search filter
    search_response = await authed_client.get("/api/v1/content/subjects?search=operating")
    assert search_response.status_code == 200
    search_results = search_response.json()
    assert len(search_results) == 1
    assert search_results[0]["slug"] == "operating-systems"


@pytest.mark.asyncio
async def test_subject_lookup_by_slug(authed_client: AsyncClient):
    """GET /api/v1/content/subjects/{slug} returns detail and course outlines."""
    response = await authed_client.get("/api/v1/content/subjects/operating-systems")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Operating Systems"
    assert data["slug"] == "operating-systems"
    assert len(data["courses"]) >= 1
    assert data["courses"][0]["slug"] == "operating-systems-fundamentals"


@pytest.mark.asyncio
async def test_invalid_subject_returns_404(authed_client: AsyncClient):
    """GET /api/v1/content/subjects/{non_existent} returns 404."""
    response = await authed_client.get("/api/v1/content/subjects/quantum-teleportation")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_course_retrieval(authed_client: AsyncClient):
    """GET /api/v1/content/courses/{slug} returns course with modules and topics."""
    response = await authed_client.get("/api/v1/content/courses/operating-systems-fundamentals")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "operating-systems-fundamentals"
    assert data["subject_slug"] == "operating-systems"
    assert len(data["modules"]) >= 9
    module_slugs = [m["slug"] for m in data["modules"]]
    assert "os-introduction" in module_slugs
    assert "os-processes-and-threads" in module_slugs


@pytest.mark.asyncio
async def test_invalid_course_returns_404(authed_client: AsyncClient):
    """GET /api/v1/content/courses/{non_existent} returns 404."""
    response = await authed_client.get("/api/v1/content/courses/unknown-course-12345")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_course_modules_endpoint(authed_client: AsyncClient):
    """GET /api/v1/content/courses/{slug}/modules returns module list."""
    response = await authed_client.get("/api/v1/content/courses/dbms-fundamentals/modules")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 10
    assert any(m["slug"] == "dbms-relational-model" for m in data)


@pytest.mark.asyncio
async def test_module_topics_endpoint(authed_client: AsyncClient):
    """GET /api/v1/content/modules/{id}/topics returns topic list."""
    async with AsyncSessionLocal() as session:
        stmt = select(Module).where(Module.slug == "os-processes-and-threads")
        module = (await session.execute(stmt)).scalars().first()
        assert module is not None
        module_id = module.id

    response = await authed_client.get(f"/api/v1/content/modules/{module_id}/topics")
    assert response.status_code == 200
    topics = response.json()
    assert len(topics) >= 2
    topic_slugs = [t["slug"] for t in topics]
    assert "process-control-block-lifecycle" in topic_slugs


@pytest.mark.asyncio
async def test_topic_retrieval(authed_client: AsyncClient):
    """GET /api/v1/content/topics/{id} returns topic details with lessons."""
    async with AsyncSessionLocal() as session:
        stmt = select(Topic).where(Topic.slug == "process-control-block-lifecycle")
        topic = (await session.execute(stmt)).scalars().first()
        assert topic is not None
        topic_id = topic.id

    response = await authed_client.get(f"/api/v1/content/topics/{topic_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "process-control-block-lifecycle"
    assert len(data["lessons"]) >= 1
    assert data["lessons"][0]["slug"] == "process-control-block-and-lifecycle"


@pytest.mark.asyncio
async def test_topic_lessons_endpoint(authed_client: AsyncClient):
    """GET /api/v1/content/topics/{id}/lessons returns lesson summaries."""
    async with AsyncSessionLocal() as session:
        stmt = select(Topic).where(Topic.slug == "asymptotic-notations")
        topic = (await session.execute(stmt)).scalars().first()
        assert topic is not None
        topic_id = topic.id

    response = await authed_client.get(f"/api/v1/content/topics/{topic_id}/lessons")
    assert response.status_code == 200
    lessons = response.json()
    assert len(lessons) >= 1
    assert lessons[0]["slug"] == "foundations-of-big-o-complexity"


@pytest.mark.asyncio
@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/api/v1/content/categories", "/api/v1/content/subjects", "/api/v1/content/subjects/operating-systems"])
async def test_catalog_requires_sign_in(async_client: AsyncClient, path: str):
    """The academic catalog belongs to the signed-in workspace."""
    response = await async_client.get(path)
    assert response.status_code == 401


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


@pytest.mark.asyncio
async def test_subject_summaries_report_real_counts(authed_client: AsyncClient):
    """Catalog counts come from the database, and every topic title is searchable."""
    subjects = (await authed_client.get("/api/v1/content/subjects")).json()
    os_summary = next(s for s in subjects if s["slug"] == "operating-systems")
    syllabus = (await authed_client.get("/api/v1/content/subjects/operating-systems/syllabus")).json()
    topics = [t for c in syllabus["courses"] for m in c["modules"] for t in m["topics"]]
    assert os_summary["module_count"] == syllabus["module_count"] == sum(len(c["modules"]) for c in syllabus["courses"])
    assert os_summary["topic_count"] == syllabus["topic_count"] == len(topics)
    assert os_summary["lesson_count"] == syllabus["lesson_count"] == sum(len(t["lessons"]) for t in topics)
    assert os_summary["topic_titles"] == [t["title"] for t in topics]


@pytest.mark.asyncio
async def test_search_matches_topics_not_just_subject_names(authed_client: AsyncClient):
    results = (await authed_client.get("/api/v1/content/subjects?search=page replacement")).json()
    assert [s["slug"] for s in results] == ["operating-systems"]
    results = (await authed_client.get("/api/v1/content/subjects?search=backpropagation")).json()
    assert "deep-learning" in [s["slug"] for s in results]


@pytest.mark.asyncio
async def test_syllabus_lists_the_tree_without_lesson_bodies(authed_client: AsyncClient):
    response = await authed_client.get("/api/v1/content/subjects/data-structures-and-algorithms/syllabus")
    assert response.status_code == 200
    data = response.json()
    module_slugs = [m["slug"] for c in data["courses"] for m in c["modules"]]
    assert module_slugs[0] == "dsa-complexity-analysis"
    first_topic = data["courses"][0]["modules"][0]["topics"][0]
    assert first_topic["slug"] == "asymptotic-notations"
    assert first_topic["lessons"][0]["slug"] == "foundations-of-big-o-complexity"
    assert "content" not in first_topic["lessons"][0]
    assert (await authed_client.get("/api/v1/content/subjects/nope/syllabus")).status_code == 404


@pytest.mark.asyncio
async def test_lesson_navigation_follows_syllabus_order(authed_client: AsyncClient):
    syllabus = (await authed_client.get("/api/v1/content/subjects/operating-systems/syllabus")).json()
    ordered = [les["id"] for c in syllabus["courses"] for m in c["modules"] for t in m["topics"] for les in t["lessons"]]
    assert len(ordered) >= 3
    middle = (await authed_client.get(f"/api/v1/content/lessons/{ordered[1]}")).json()["navigation"]
    assert middle["previous"]["lesson_id"] == ordered[0]
    assert middle["next"]["lesson_id"] == ordered[2]
    assert middle["position"] == 2 and middle["total"] == len(ordered)
    assert any(t["is_current"] for t in middle["module_topics"])
    first = (await authed_client.get(f"/api/v1/content/lessons/{ordered[0]}")).json()["navigation"]
    assert first["previous"] is None


@pytest.mark.asyncio
async def test_topic_navigation_links_neighbouring_topics(authed_client: AsyncClient):
    syllabus = (await authed_client.get("/api/v1/content/subjects/operating-systems/syllabus")).json()
    topics = [t for c in syllabus["courses"] for m in c["modules"] for t in m["topics"]]
    nav = (await authed_client.get(f"/api/v1/content/topics/{topics[1]['id']}")).json()["navigation"]
    assert nav["previous"]["topic_id"] == topics[0]["id"]
    assert nav["next"]["topic_id"] == topics[2]["id"]
    assert nav["position"] == 2 and nav["total"] == len(topics)
