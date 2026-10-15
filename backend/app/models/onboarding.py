import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.user import Base


class StudentOnboarding(Base):
    """
    SQLAlchemy ORM model mapping student onboarding choices,
    diagnostic assessment scores, and rule-based learner profiles.
    """
    __tablename__ = "onboarding_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    goals: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list
    )
    interests: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list
    )
    selected_subjects: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list
    )
    assessment_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0
    )
    strengths: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list
    )
    weak_areas: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list
    )
    recommended_weekly_hours: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=10
    )
    suggested_starting_topic: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="Foundations of Computer Science"
    )
    is_completed: Mapped[bool] = mapped_column(
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

    user = relationship("User", backref="onboarding_profile")
