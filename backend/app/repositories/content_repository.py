import uuid
from collections.abc import Sequence

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.content import (
    ContentCategory,
    Course,
    Lesson,
    Module,
    Subject,
    Topic,
)


class ContentRepository:
    """Async repository for querying academic content hierarchy entities."""

    async def get_categories(
        self,
        db: AsyncSession,
        active_only: bool = True
    ) -> Sequence[ContentCategory]:
        """Fetch all content categories ordered by display_order."""
        stmt = (
            select(ContentCategory)
            .options(selectinload(ContentCategory.subjects))
            .order_by(ContentCategory.display_order.asc(), ContentCategory.name.asc())
        )
        if active_only:
            stmt = stmt.where(ContentCategory.is_active.is_(True))
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_category_by_slug(
        self,
        db: AsyncSession,
        slug: str
    ) -> ContentCategory | None:
        """Fetch single category by slug with its subjects."""
        stmt = (
            select(ContentCategory)
            .options(selectinload(ContentCategory.subjects))
            .where(ContentCategory.slug == slug)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_subjects(
        self,
        db: AsyncSession,
        category_slug: str | None = None,
        difficulty: str | None = None,
        search: str | None = None,
        active_only: bool = True
    ) -> Sequence[Subject]:
        """Fetch subjects with optional filtering by category, difficulty, or search term."""
        stmt = (
            select(Subject)
            .options(
                selectinload(Subject.category),
                selectinload(Subject.courses)
            )
            .order_by(Subject.display_order.asc(), Subject.name.asc())
        )

        if active_only:
            stmt = stmt.where(Subject.is_active.is_(True))

        if category_slug:
            stmt = stmt.join(ContentCategory).where(ContentCategory.slug == category_slug)

        if difficulty:
            stmt = stmt.where(Subject.difficulty_level.ilike(f"%{difficulty}%"))

        if search:
            search_pattern = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Subject.name.ilike(search_pattern),
                    Subject.short_description.ilike(search_pattern),
                    Subject.description.ilike(search_pattern),
                )
            )

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_subject_by_slug(
        self,
        db: AsyncSession,
        slug: str
    ) -> Subject | None:
        """Fetch subject by unique slug with category and courses."""
        stmt = (
            select(Subject)
            .options(
                selectinload(Subject.category),
                selectinload(Subject.courses).selectinload(Course.modules)
            )
            .where(Subject.slug == slug)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_courses_by_subject_slug(
        self,
        db: AsyncSession,
        subject_slug: str,
        active_only: bool = True
    ) -> Sequence[Course]:
        """Fetch all courses for a given subject slug."""
        stmt = (
            select(Course)
            .join(Subject)
            .options(
                selectinload(Course.subject),
                selectinload(Course.modules)
                .selectinload(Module.topics)
                .selectinload(Topic.lessons)
            )
            .where(Subject.slug == subject_slug)
            .order_by(Course.display_order.asc())
        )
        if active_only:
            stmt = stmt.where(Course.is_active.is_(True))
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_course_by_slug(
        self,
        db: AsyncSession,
        course_slug: str
    ) -> Course | None:
        """Fetch course by slug including full module and topic breakdown."""
        stmt = (
            select(Course)
            .options(
                selectinload(Course.subject),
                selectinload(Course.modules)
                .selectinload(Module.topics)
                .selectinload(Topic.lessons)
            )
            .where(Course.slug == course_slug)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_modules_by_course_slug(
        self,
        db: AsyncSession,
        course_slug: str
    ) -> Sequence[Module]:
        """Fetch all modules for a course with topics."""
        stmt = (
            select(Module)
            .join(Course)
            .options(selectinload(Module.topics).selectinload(Topic.lessons))
            .where(Course.slug == course_slug)
            .order_by(Module.display_order.asc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_module_by_id(
        self,
        db: AsyncSession,
        module_id: uuid.UUID
    ) -> Module | None:
        """Fetch module by UUID with course and topics."""
        stmt = (
            select(Module)
            .options(
                selectinload(Module.course),
                selectinload(Module.topics).selectinload(Topic.lessons)
            )
            .where(Module.id == module_id)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_topics_by_module_id(
        self,
        db: AsyncSession,
        module_id: uuid.UUID
    ) -> Sequence[Topic]:
        """Fetch all topics for a module."""
        stmt = (
            select(Topic)
            .options(selectinload(Topic.lessons))
            .where(Topic.module_id == module_id)
            .order_by(Topic.display_order.asc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_topic_by_id(
        self,
        db: AsyncSession,
        topic_id: uuid.UUID
    ) -> Topic | None:
        """Fetch topic by UUID with its lessons and parent module/course/subject hierarchy."""
        stmt = (
            select(Topic)
            .options(
                selectinload(Topic.module).selectinload(Module.course).selectinload(Course.subject),
                selectinload(Topic.lessons)
            )
            .where(Topic.id == topic_id)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_lessons_by_topic_id(
        self,
        db: AsyncSession,
        topic_id: uuid.UUID
    ) -> Sequence[Lesson]:
        """Fetch all lessons for a topic."""
        stmt = (
            select(Lesson)
            .where(Lesson.topic_id == topic_id)
            .order_by(Lesson.display_order.asc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_lesson_by_id(
        self,
        db: AsyncSession,
        lesson_id: uuid.UUID
    ) -> Lesson | None:
        """Fetch lesson by UUID with full ancestor hierarchy."""
        stmt = (
            select(Lesson)
            .options(
                selectinload(Lesson.topic)
                .selectinload(Topic.module)
                .selectinload(Module.course)
                .selectinload(Course.subject)
            )
            .where(Lesson.id == lesson_id)
        )
        result = await db.execute(stmt)
        return result.scalars().first()


content_repository = ContentRepository()
