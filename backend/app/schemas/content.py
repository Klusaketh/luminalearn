import uuid

from pydantic import BaseModel, ConfigDict


class LessonSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    topic_id: uuid.UUID
    title: str
    slug: str
    summary: str | None = None
    estimated_minutes: int
    display_order: int
    lesson_type: str


class LessonDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    topic_id: uuid.UUID
    topic_title: str | None = None
    module_id: uuid.UUID | None = None
    module_title: str | None = None
    course_id: uuid.UUID | None = None
    course_title: str | None = None
    course_slug: str | None = None
    subject_name: str | None = None
    subject_slug: str | None = None
    title: str
    slug: str
    summary: str | None = None
    content: str
    learning_objectives: list[str] = []
    estimated_minutes: int
    display_order: int
    lesson_type: str


class TopicSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    module_id: uuid.UUID
    title: str
    slug: str
    summary: str | None = None
    estimated_minutes: int
    difficulty: str
    display_order: int
    lesson_count: int = 0


class TopicDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    module_id: uuid.UUID
    module_title: str | None = None
    course_id: uuid.UUID | None = None
    course_title: str | None = None
    course_slug: str | None = None
    subject_name: str | None = None
    subject_slug: str | None = None
    title: str
    slug: str
    summary: str | None = None
    estimated_minutes: int
    difficulty: str
    display_order: int
    lessons: list[LessonSummary] = []


class ModuleSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    slug: str
    description: str | None = None
    estimated_minutes: int
    display_order: int
    topic_count: int = 0


class ModuleDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    slug: str
    description: str | None = None
    estimated_minutes: int
    display_order: int
    topics: list[TopicSummary] = []


class CourseSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject_id: uuid.UUID
    title: str
    slug: str
    description: str | None = None
    difficulty: str
    estimated_hours: int
    display_order: int
    module_count: int = 0


class CourseDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject_id: uuid.UUID
    subject_name: str | None = None
    subject_slug: str | None = None
    title: str
    slug: str
    description: str | None = None
    difficulty: str
    estimated_hours: int
    display_order: int
    modules: list[ModuleDetail] = []


class SubjectSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category_id: uuid.UUID
    category_name: str | None = None
    category_slug: str | None = None
    name: str
    slug: str
    short_description: str | None = None
    icon_key: str | None = None
    difficulty_level: str
    display_order: int
    course_count: int = 0


class SubjectDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category_id: uuid.UUID
    category_name: str | None = None
    category_slug: str | None = None
    name: str
    slug: str
    short_description: str | None = None
    description: str | None = None
    icon_key: str | None = None
    difficulty_level: str
    display_order: int
    courses: list[CourseSummary] = []


class ContentCategorySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    description: str | None = None
    display_order: int
    subject_count: int = 0


class ContentCategoryDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    description: str | None = None
    display_order: int
    subjects: list[SubjectSummary] = []
