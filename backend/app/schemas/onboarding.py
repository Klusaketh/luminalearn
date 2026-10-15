import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DiagnosticOption(BaseModel):
    id: int
    text: str


class DiagnosticQuestion(BaseModel):
    id: int
    subject: str
    topic: str
    difficulty: str  # Easy, Medium, Hard
    question: str
    options: list[str]


class QuestionAnswer(BaseModel):
    question_id: int
    selected_option_index: int
    time_taken_ms: int | None = 0


class OnboardingSubmitRequest(BaseModel):
    goals: list[str] = Field(..., min_items=1, description="List of selected learning goals")
    interests: list[str] = Field(..., min_items=1, description="List of selected interests")
    selected_subjects: list[str] = Field(..., min_items=1, description="List of subjects to learn first")
    answers: list[QuestionAnswer] = Field(..., min_items=1, description="List of diagnostic quiz answers")


class LearnerProfileResponse(BaseModel):
    user_id: uuid.UUID
    goals: list[str]
    interests: list[str]
    selected_subjects: list[str]
    assessment_score: float
    strengths: list[str]
    weak_areas: list[str]
    recommended_weekly_hours: int
    suggested_starting_topic: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoadmapModule(BaseModel):
    id: int
    title: str
    description: str
    estimated_hours: int
    difficulty: str
    is_key_focus: bool


class PersonalizedRoadmapResponse(BaseModel):
    profile: LearnerProfileResponse
    recommended_course: str
    weekly_goal_hours: int
    daily_target_minutes: int
    starting_module: str
    roadmap_modules: list[RoadmapModule]
