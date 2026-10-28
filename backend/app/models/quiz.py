import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.user import Base, User


class QuizSession(Base):
    """
    Represents an adaptive quizzing session initiated by a student for a specific topic.
    Tracks session lifecycle, difficulty parameter, and mastery delta.
    """

    __tablename__ = "quiz_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    topic_title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    topic_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("topics.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    difficulty_level: Mapped[str] = mapped_column(
        String(50), nullable=False, default="intermediate"
    )
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="in_progress",  # in_progress, completed, abandoned
    )
    initial_mastery: Mapped[float] = mapped_column(Float, nullable=False, default=0.10)
    final_mastery: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped[User] = relationship("User", foreign_keys=[user_id])
    questions: Mapped[list["QuizQuestion"]] = relationship(
        "QuizQuestion",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="QuizQuestion.question_index",
    )
    attempts: Mapped[list["QuizAttempt"]] = relationship(
        "QuizAttempt", back_populates="session", cascade="all, delete-orphan"
    )


class QuizQuestion(Base):
    """
    Individual question generated for a quiz session.
    Encapsulates Bloom's Taxonomy category, IRT 2PL difficulty parameters, and misconception mapping.
    """

    __tablename__ = "quiz_questions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("quiz_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    correct_answer: Mapped[str] = mapped_column(String(500), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    blooms_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="understanding",  # remembering, understanding, applying, analyzing, evaluating
    )
    question_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="multiple_choice",  # multiple_choice, free_response, code_analysis
    )
    source_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    irt_difficulty: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,  # b parameter in IRT 2PL [-3.0 to +3.0]
    )
    irt_discrimination: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,  # a parameter in IRT 2PL [0.5 to 2.5]
    )
    misconception_map: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,  # Maps distractor option text -> diagnostic reason why student chose it
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    session: Mapped["QuizSession"] = relationship(
        "QuizSession", back_populates="questions"
    )
    attempts: Mapped[list["QuizAttempt"]] = relationship(
        "QuizAttempt", back_populates="question", cascade="all, delete-orphan"
    )


class QuizAttempt(Base):
    """
    Student submission for a specific quiz question.
    Records correctness, latency, posterior BKT mastery, and detected misconceptions.
    Enforces idempotency: exactly one attempt per question per session.
    """

    __tablename__ = "quiz_attempts"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "question_id",
            "user_id",
            name="uq_session_question_user_attempt",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("quiz_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("quiz_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    selected_answer: Mapped[str] = mapped_column(String(500), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bkt_prior_mastery: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.10
    )
    bkt_posterior_mastery: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.10
    )
    detected_misconception: Mapped[str | None] = mapped_column(Text, nullable=True)
    feedback: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    session: Mapped["QuizSession"] = relationship(
        "QuizSession", back_populates="attempts"
    )
    question: Mapped["QuizQuestion"] = relationship(
        "QuizQuestion", back_populates="attempts"
    )
    user: Mapped[User] = relationship("User", foreign_keys=[user_id])


class StudentTopicMastery(Base):
    """
    Persistent transactional mastery record per student per topic.
    Tracks Bayesian Knowledge Tracing (BKT) metrics, predictions, streaks, and calibration data.
    """

    __tablename__ = "student_topic_masteries"
    __table_args__ = (
        UniqueConstraint("user_id", "topic_title", name="uq_user_topic_mastery"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    topic_title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    topic_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("topics.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    current_mastery: Mapped[float] = mapped_column(Float, nullable=False, default=0.10)
    predicted_accuracy: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.28
    )
    total_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    correct_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    retention_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Novice",  # Novice, Developing, Competent, Mastered
    )
    last_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user: Mapped[User] = relationship("User", foreign_keys=[user_id])
