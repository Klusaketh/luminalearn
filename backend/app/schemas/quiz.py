import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class QuizGenerateRequest(BaseModel):
    """Payload for initiating an adaptive quiz generation."""
    topic: str = Field(..., min_length=2, max_length=150, description="Academic topic to quiz")
    difficulty: str = Field(
        default="intermediate",
        description="Target difficulty: beginner, intermediate, advanced"
    )
    question_count: int = Field(
        default=5,
        ge=3,
        le=10,
        description="Number of questions to generate (3 to 10)"
    )
    topic_id: uuid.UUID | None = Field(
        default=None,
        description="Optional foreign key to catalog topic"
    )


class QuizQuestionStudentView(BaseModel):
    """Student-safe view of a quiz question (correct answer withheld)."""
    id: uuid.UUID
    question_index: int
    prompt: str
    options: list[str]
    blooms_level: str
    question_type: str = "multiple_choice"
    source_reference: str | None = None
    irt_difficulty: float

    model_config = ConfigDict(from_attributes=True)


class QuizSessionDetail(BaseModel):
    """Full quiz session envelope containing questions."""
    id: uuid.UUID
    topic_title: str
    difficulty_level: str
    total_questions: int
    score: float
    status: str
    initial_mastery: float
    final_mastery: float | None
    created_at: datetime
    completed_at: datetime | None
    questions: list[QuizQuestionStudentView]

    model_config = ConfigDict(from_attributes=True)


class QuizSubmitAnswerRequest(BaseModel):
    """Payload for submitting a single question answer."""
    session_id: uuid.UUID
    question_id: uuid.UUID
    selected_answer: str = Field(..., min_length=1, max_length=1000)
    latency_ms: int = Field(default=0, ge=0, description="Response time in milliseconds")


class QuizSubmitAnswerResponse(BaseModel):
    """Formative assessment feedback and BKT Bayesian state update."""
    attempt_id: uuid.UUID
    is_correct: bool
    selected_answer: str
    correct_answer: str
    explanation: str
    detected_misconception: str | None
    feedback: str
    prior_mastery: float
    posterior_mastery: float
    next_opportunity_mastery: float
    predicted_accuracy: float
    confidence: float | None = None
    session_completed: bool
    session_score: float
    session_final_mastery: float | None
    previous_retention_level: str | None = Field(default=None, description="Competency tier before this answer")
    retention_level: str | None = Field(default=None, description="Competency tier after this answer")
    level_up: bool = Field(default=False, description="True when this answer crossed into a higher tier")


class RetentionForecastResponse(BaseModel):
    """Ebbinghaus forgetting curve with and without spaced retrieval practice."""
    days: list[float]
    no_review: list[float]
    spaced: list[float]
    review_days: list[float]
    target_retention: float
    half_life_days: float
    initial_stability_days: float


class QuizMasteryResponse(BaseModel):
    """Learner's current Bayesian mastery and historical progress for a topic."""
    topic_title: str
    topic_id: uuid.UUID | None
    current_mastery: float
    predicted_accuracy: float
    total_attempts: int
    correct_attempts: int
    retention_level: str
    history: list[dict[str, Any]]
    retention_forecast: RetentionForecastResponse | None = None


class TopicMasterySummary(BaseModel):
    """One assessed topic in the learner's knowledge radar."""
    topic_title: str
    current_mastery: float
    predicted_accuracy: float
    retention_level: str
    total_attempts: int
    correct_attempts: int
    streak: int
    last_attempt_at: datetime | None


class QuizHistoryItem(BaseModel):
    """Summarized historical quiz session item."""
    id: uuid.UUID
    topic_title: str
    difficulty_level: str
    total_questions: int
    score: float
    status: str
    initial_mastery: float
    final_mastery: float | None
    created_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class QuizHistoryResponse(BaseModel):
    """Paginated list of historical quiz sessions."""
    total: int
    page: int
    page_size: int
    items: list[QuizHistoryItem]

