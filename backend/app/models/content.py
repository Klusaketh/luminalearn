import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.user import Base


class ContentCategory(Base):
    """
    Top-level category grouping academic disciplines (e.g., Computer Science, Programming, AI, Mathematics).
    """
    __tablename__ = "content_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    subjects: Mapped[list["Subject"]] = relationship(
        "Subject",
        back_populates="category",
        cascade="all, delete-orphan",
        order_by="Subject.display_order"
    )


class Subject(Base):
    """
    Academic subject within a category (e.g., Operating Systems, Python, Machine Learning).
    """
    __tablename__ = "subjects"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("content_categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )
    slug: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )
    short_description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    icon_key: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    difficulty_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="All Levels"
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    category: Mapped["ContentCategory"] = relationship(
        "ContentCategory",
        back_populates="subjects"
    )
    courses: Mapped[list["Course"]] = relationship(
        "Course",
        back_populates="subject",
        cascade="all, delete-orphan",
        order_by="Course.display_order"
    )


class Course(Base):
    """
    Curated course belonging to a subject (e.g., Operating Systems Fundamentals).
    """
    __tablename__ = "courses"
    __table_args__ = (
        UniqueConstraint("subject_id", "slug", name="uq_course_subject_slug"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    slug: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    difficulty: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Beginner"
    )
    estimated_hours: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=10
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    subject: Mapped["Subject"] = relationship(
        "Subject",
        back_populates="courses"
    )
    modules: Mapped[list["Module"]] = relationship(
        "Module",
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="Module.display_order"
    )


class Module(Base):
    """
    Module chapter within a course (e.g., Processes & Threads).
    """
    __tablename__ = "modules"
    __table_args__ = (
        UniqueConstraint("course_id", "slug", name="uq_module_course_slug"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    slug: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    estimated_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=60
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="modules"
    )
    topics: Mapped[list["Topic"]] = relationship(
        "Topic",
        back_populates="module",
        cascade="all, delete-orphan",
        order_by="Topic.display_order"
    )


class Topic(Base):
    """
    Sub-topic unit within a module (e.g., CPU Scheduling Algorithms).
    """
    __tablename__ = "topics"
    __table_args__ = (
        UniqueConstraint("module_id", "slug", name="uq_topic_module_slug"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    module_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("modules.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    slug: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True
    )
    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    estimated_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=30
    )
    difficulty: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Beginner"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    module: Mapped["Module"] = relationship(
        "Module",
        back_populates="topics"
    )
    lessons: Mapped[list["Lesson"]] = relationship(
        "Lesson",
        back_populates="topic",
        cascade="all, delete-orphan",
        order_by="Lesson.display_order"
    )


class Lesson(Base):
    """
    Concrete learning unit containing structured Markdown educational content.
    """
    __tablename__ = "lessons"
    __table_args__ = (
        UniqueConstraint("topic_id", "slug", name="uq_lesson_topic_slug"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    slug: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True
    )
    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    learning_objectives: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list
    )
    estimated_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=15
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    lesson_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="theory"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    topic: Mapped["Topic"] = relationship(
        "Topic",
        back_populates="lessons"
    )
