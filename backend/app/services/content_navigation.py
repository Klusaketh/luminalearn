"""
LuminaLearn AI — Subjects module navigation.
Module: backend/app/services/content_navigation.py

Orders a subject's lessons and topics the way its syllabus reads (course, module, topic, lesson
display order) and answers "what comes before and after this one" for the lesson reader and the
topic page. Works on a subject loaded with its full course -> module -> topic -> lesson tree.
"""

import uuid
from dataclasses import dataclass

from app.models.content import Course, Lesson, Module, Subject, Topic
from app.schemas.content import (
    LessonNavigation,
    LessonNavLink,
    ModuleTopicLink,
    TopicNavigation,
    TopicNavLink,
)


@dataclass(frozen=True)
class SyllabusEntry:
    course: Course
    module: Module
    topic: Topic


def syllabus_topics(subject: Subject) -> list[SyllabusEntry]:
    """Every topic of the subject's active courses, in reading order."""
    return [
        SyllabusEntry(course, module, topic)
        for course in sorted(subject.courses, key=lambda c: c.display_order)
        if course.is_active
        for module in sorted(course.modules, key=lambda m: m.display_order)
        for topic in sorted(module.topics, key=lambda t: t.display_order)
    ]


def _ordered_lessons(topic: Topic) -> list[Lesson]:
    return sorted(topic.lessons, key=lambda les: les.display_order)


def lesson_navigation(subject: Subject, lesson_id: uuid.UUID) -> LessonNavigation | None:
    entries = syllabus_topics(subject)
    flat = [(entry, lesson) for entry in entries for lesson in _ordered_lessons(entry.topic)]
    index = next((i for i, (_, lesson) in enumerate(flat) if lesson.id == lesson_id), None)
    if index is None:
        return None

    def link(position: int) -> LessonNavLink | None:
        if not 0 <= position < len(flat):
            return None
        entry, lesson = flat[position]
        return LessonNavLink(
            lesson_id=lesson.id,
            lesson_title=lesson.title,
            topic_id=entry.topic.id,
            topic_title=entry.topic.title,
            module_title=entry.module.title,
        )

    current = flat[index][0]
    module_topics = [
        ModuleTopicLink(
            topic_id=entry.topic.id,
            title=entry.topic.title,
            lesson_id=lessons[0].id if (lessons := _ordered_lessons(entry.topic)) else None,
            is_current=entry.topic.id == current.topic.id,
        )
        for entry in entries
        if entry.module.id == current.module.id
    ]
    return LessonNavigation(
        previous=link(index - 1),
        next=link(index + 1),
        position=index + 1,
        total=len(flat),
        module_topics=module_topics,
    )


def topic_navigation(subject: Subject, topic_id: uuid.UUID) -> TopicNavigation | None:
    entries = syllabus_topics(subject)
    index = next((i for i, entry in enumerate(entries) if entry.topic.id == topic_id), None)
    if index is None:
        return None

    def link(position: int) -> TopicNavLink | None:
        if not 0 <= position < len(entries):
            return None
        entry = entries[position]
        lessons = _ordered_lessons(entry.topic)
        return TopicNavLink(
            topic_id=entry.topic.id,
            title=entry.topic.title,
            module_title=entry.module.title,
            lesson_id=lessons[0].id if lessons else None,
        )

    return TopicNavigation(previous=link(index - 1), next=link(index + 1), position=index + 1, total=len(entries))
