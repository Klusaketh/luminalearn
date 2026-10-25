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


class LessonNavLink(BaseModel):
    """A neighbouring lesson in syllabus order."""

    lesson_id: uuid.UUID
    lesson_title: str
    topic_id: uuid.UUID
    topic_title: str
    module_title: str


class ModuleTopicLink(BaseModel):
    """A topic in the current lesson's module, for the reader's sidebar."""

    topic_id: uuid.UUID
    title: str
    lesson_id: uuid.UUID | None = None
    is_current: bool = False


class LessonNavigation(BaseModel):
    previous: LessonNavLink | None = None
    next: LessonNavLink | None = None
    position: int
    total: int
    module_topics: list[ModuleTopicLink] = []


class LessonDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    topic_id: uuid.UUID
    topic_title: str | None = None
    topic_summary: str | None = None
    topic_difficulty: str | None = None
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
    navigation: LessonNavigation | None = None


class TopicNavLink(BaseModel):
    """A neighbouring topic in syllabus order, with its first lesson when it has one."""

    topic_id: uuid.UUID
    title: str
    module_title: str
    lesson_id: uuid.UUID | None = None


class TopicNavigation(BaseModel):
    previous: TopicNavLink | None = None
    next: TopicNavLink | None = None
    position: int
    total: int


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
    navigation: TopicNavigation | None = None


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
    module_count: int = 0
    topic_count: int = 0
    lesson_count: int = 0
    # Lets the catalog search topics as well as subject names.
    topic_titles: list[str] = []


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


class SyllabusLesson(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    estimated_minutes: int


class SyllabusTopic(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    summary: str | None = None
    difficulty: str
    estimated_minutes: int
    display_order: int
    lessons: list[SyllabusLesson] = []


class SyllabusModule(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    description: str | None = None
    estimated_minutes: int
    display_order: int
    topics: list[SyllabusTopic] = []


class SyllabusCourse(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    description: str | None = None
    difficulty: str
    estimated_hours: int
    display_order: int
    modules: list[SyllabusModule] = []


class SubjectSyllabus(BaseModel):
    """A subject with its whole course -> module -> topic -> lesson tree (lesson bodies excluded)."""

    id: uuid.UUID
    name: str
    slug: str
    category_name: str | None = None
    category_slug: str | None = None
    short_description: str | None = None
    description: str | None = None
    icon_key: str | None = None
    difficulty_level: str
    module_count: int = 0
    topic_count: int = 0
    lesson_count: int = 0
    estimated_hours: int = 0
    courses: list[SyllabusCourse] = []


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
