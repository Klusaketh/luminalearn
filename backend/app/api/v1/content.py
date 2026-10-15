import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.repositories.content_repository import content_repository
from app.schemas.content import (
    ContentCategorySummary,
    CourseDetail,
    CourseSummary,
    LessonDetail,
    LessonSummary,
    ModuleDetail,
    SubjectDetail,
    SubjectSummary,
    TopicDetail,
    TopicSummary,
)

router = APIRouter(prefix="/content", tags=["Academic Content Engine"])


@router.get(
    "/categories",
    response_model=list[ContentCategorySummary],
    summary="Get All Content Categories"
)
async def list_categories(
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve top-level academic disciplines (Computer Science, Programming, AI, Mathematics)."""
    categories = await content_repository.get_categories(db)
    return [
        ContentCategorySummary(
            id=cat.id,
            name=cat.name,
            slug=cat.slug,
            description=cat.description,
            display_order=cat.display_order,
            subject_count=len(cat.subjects) if cat.subjects else 0
        )
        for cat in categories
    ]


@router.get(
    "/subjects",
    response_model=list[SubjectSummary],
    summary="Get All Academic Subjects"
)
async def list_subjects(
    category_slug: str | None = Query(None, description="Filter by category slug"),
    difficulty: str | None = Query(None, description="Filter by difficulty level"),
    search: str | None = Query(None, description="Search term across name and description"),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve academic subjects with optional category, difficulty, or search filters."""
    subjects = await content_repository.get_subjects(
        db,
        category_slug=category_slug,
        difficulty=difficulty,
        search=search
    )
    return [
        SubjectSummary(
            id=s.id,
            category_id=s.category_id,
            category_name=s.category.name if s.category else None,
            category_slug=s.category.slug if s.category else None,
            name=s.name,
            slug=s.slug,
            short_description=s.short_description,
            icon_key=s.icon_key,
            difficulty_level=s.difficulty_level,
            display_order=s.display_order,
            course_count=len(s.courses) if s.courses else 0
        )
        for s in subjects
    ]


@router.get(
    "/subjects/{subject_slug}",
    response_model=SubjectDetail,
    summary="Get Subject Detail by Slug"
)
async def get_subject(
    subject_slug: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve detailed subject information including available courses."""
    subject = await content_repository.get_subject_by_slug(db, slug=subject_slug)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject '{subject_slug}' not found."
        )

    return SubjectDetail(
        id=subject.id,
        category_id=subject.category_id,
        category_name=subject.category.name if subject.category else None,
        category_slug=subject.category.slug if subject.category else None,
        name=subject.name,
        slug=subject.slug,
        short_description=subject.short_description,
        description=subject.description,
        icon_key=subject.icon_key,
        difficulty_level=subject.difficulty_level,
        display_order=subject.display_order,
        courses=[
            CourseSummary(
                id=c.id,
                subject_id=c.subject_id,
                title=c.title,
                slug=c.slug,
                description=c.description,
                difficulty=c.difficulty,
                estimated_hours=c.estimated_hours,
                display_order=c.display_order,
                module_count=len(c.modules) if c.modules else 0
            )
            for c in (subject.courses or [])
        ]
    )


@router.get(
    "/subjects/{subject_slug}/courses",
    response_model=list[CourseSummary],
    summary="Get Courses for a Subject"
)
async def list_subject_courses(
    subject_slug: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve all courses belonging to a specific subject."""
    subject = await content_repository.get_subject_by_slug(db, slug=subject_slug)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject '{subject_slug}' not found."
        )

    courses = await content_repository.get_courses_by_subject_slug(db, subject_slug=subject_slug)
    return [
        CourseSummary(
            id=c.id,
            subject_id=c.subject_id,
            title=c.title,
            slug=c.slug,
            description=c.description,
            difficulty=c.difficulty,
            estimated_hours=c.estimated_hours,
            display_order=c.display_order,
            module_count=len(c.modules) if c.modules else 0
        )
        for c in courses
    ]


@router.get(
    "/courses/{course_slug}",
    response_model=CourseDetail,
    summary="Get Course Detail with Modules and Topics"
)
async def get_course(
    course_slug: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve course by slug with its complete syllabus module and topic breakdown."""
    course = await content_repository.get_course_by_slug(db, course_slug=course_slug)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course '{course_slug}' not found."
        )

    return CourseDetail(
        id=course.id,
        subject_id=course.subject_id,
        subject_name=course.subject.name if course.subject else None,
        subject_slug=course.subject.slug if course.subject else None,
        title=course.title,
        slug=course.slug,
        description=course.description,
        difficulty=course.difficulty,
        estimated_hours=course.estimated_hours,
        display_order=course.display_order,
        modules=[
            ModuleDetail(
                id=m.id,
                course_id=m.course_id,
                title=m.title,
                slug=m.slug,
                description=m.description,
                estimated_minutes=m.estimated_minutes,
                display_order=m.display_order,
                topics=[
                    TopicSummary(
                        id=t.id,
                        module_id=t.module_id,
                        title=t.title,
                        slug=t.slug,
                        summary=t.summary,
                        estimated_minutes=t.estimated_minutes,
                        difficulty=t.difficulty,
                        display_order=t.display_order,
                        lesson_count=len(t.lessons) if t.lessons else 0
                    )
                    for t in (m.topics or [])
                ]
            )
            for m in (course.modules or [])
        ]
    )


@router.get(
    "/courses/{course_slug}/modules",
    response_model=list[ModuleDetail],
    summary="Get Modules for a Course"
)
async def list_course_modules(
    course_slug: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve module outline for a specific course."""
    course = await content_repository.get_course_by_slug(db, course_slug=course_slug)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course '{course_slug}' not found."
        )

    modules = await content_repository.get_modules_by_course_slug(db, course_slug=course_slug)
    return [
        ModuleDetail(
            id=m.id,
            course_id=m.course_id,
            title=m.title,
            slug=m.slug,
            description=m.description,
            estimated_minutes=m.estimated_minutes,
            display_order=m.display_order,
            topics=[
                TopicSummary(
                    id=t.id,
                    module_id=t.module_id,
                    title=t.title,
                    slug=t.slug,
                    summary=t.summary,
                    estimated_minutes=t.estimated_minutes,
                    difficulty=t.difficulty,
                    display_order=t.display_order,
                    lesson_count=len(t.lessons) if t.lessons else 0
                )
                for t in (m.topics or [])
            ]
        )
        for m in modules
    ]


@router.get(
    "/modules/{module_id}/topics",
    response_model=list[TopicSummary],
    summary="Get Topics for a Module"
)
async def list_module_topics(
    module_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve all topics under a specific module."""
    module = await content_repository.get_module_by_id(db, module_id=module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module '{module_id}' not found."
        )

    topics = await content_repository.get_topics_by_module_id(db, module_id=module_id)
    return [
        TopicSummary(
            id=t.id,
            module_id=t.module_id,
            title=t.title,
            slug=t.slug,
            summary=t.summary,
            estimated_minutes=t.estimated_minutes,
            difficulty=t.difficulty,
            display_order=t.display_order,
            lesson_count=len(t.lessons) if t.lessons else 0
        )
        for t in topics
    ]


@router.get(
    "/topics/{topic_id}",
    response_model=TopicDetail,
    summary="Get Topic Detail with Lessons"
)
async def get_topic(
    topic_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve topic information including available lesson units."""
    topic = await content_repository.get_topic_by_id(db, topic_id=topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic '{topic_id}' not found."
        )

    return TopicDetail(
        id=topic.id,
        module_id=topic.module_id,
        module_title=topic.module.title if topic.module else None,
        course_id=topic.module.course.id if (topic.module and topic.module.course) else None,
        course_title=topic.module.course.title if (topic.module and topic.module.course) else None,
        course_slug=topic.module.course.slug if (topic.module and topic.module.course) else None,
        subject_name=topic.module.course.subject.name if (topic.module and topic.module.course and topic.module.course.subject) else None,
        subject_slug=topic.module.course.subject.slug if (topic.module and topic.module.course and topic.module.course.subject) else None,
        title=topic.title,
        slug=topic.slug,
        summary=topic.summary,
        estimated_minutes=topic.estimated_minutes,
        difficulty=topic.difficulty,
        display_order=topic.display_order,
        lessons=[
            LessonSummary(
                id=les.id,
                topic_id=les.topic_id,
                title=les.title,
                slug=les.slug,
                summary=les.summary,
                estimated_minutes=les.estimated_minutes,
                display_order=les.display_order,
                lesson_type=les.lesson_type
            )
            for les in (topic.lessons or [])
        ]
    )


@router.get(
    "/topics/{topic_id}/lessons",
    response_model=list[LessonSummary],
    summary="Get Lessons for a Topic"
)
async def list_topic_lessons(
    topic_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve list of lessons under a topic."""
    topic = await content_repository.get_topic_by_id(db, topic_id=topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic '{topic_id}' not found."
        )

    lessons = await content_repository.get_lessons_by_topic_id(db, topic_id=topic_id)
    return [
        LessonSummary(
            id=les.id,
            topic_id=les.topic_id,
            title=les.title,
            slug=les.slug,
            summary=les.summary,
            estimated_minutes=les.estimated_minutes,
            display_order=les.display_order,
            lesson_type=les.lesson_type
        )
        for les in lessons
    ]


@router.get(
    "/lessons/{lesson_id}",
    response_model=LessonDetail,
    summary="Get Lesson Viewer Content (Protected: Active & Verified Learner Required)"
)
async def get_lesson(
    lesson_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retrieve concrete educational lesson content.
    Enforces active authentication and email verification (Sprint 6.2A invariant).
    """
    lesson = await content_repository.get_lesson_by_id(db, lesson_id=lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson '{lesson_id}' not found."
        )

    topic = lesson.topic
    module = topic.module if topic else None
    course = module.course if module else None
    subject = course.subject if course else None

    return LessonDetail(
        id=lesson.id,
        topic_id=lesson.topic_id,
        topic_title=topic.title if topic else None,
        module_id=module.id if module else None,
        module_title=module.title if module else None,
        course_id=course.id if course else None,
        course_title=course.title if course else None,
        course_slug=course.slug if course else None,
        subject_name=subject.name if subject else None,
        subject_slug=subject.slug if subject else None,
        title=lesson.title,
        slug=lesson.slug,
        summary=lesson.summary,
        content=lesson.content,
        learning_objectives=lesson.learning_objectives or [],
        estimated_minutes=lesson.estimated_minutes,
        display_order=lesson.display_order,
        lesson_type=lesson.lesson_type
    )
