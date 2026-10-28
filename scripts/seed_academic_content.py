"""
LuminaLearn AI — Academic Content Seeder (Subjects module).

Syncs the curriculum files in content/ (format: content/README.md) into the content tables:
Category -> Subject -> Course -> Module -> Topic -> Lesson.

Idempotent and non-destructive:
- creates whatever is missing, matching records by slug at every level;
- refreshes catalog-owned fields (titles, descriptions, ordering, lesson text) when the files change;
- never deletes a record and never changes an id or slug, so quiz history and saved links stay valid.
A second run over unchanged files creates and updates nothing.

Run: python scripts/seed_academic_content.py   (from the project root or anywhere else)
"""

import asyncio
import sys
import uuid
from pathlib import Path
from typing import Any

# Running as a script: make the backend package and this folder importable.
_ROOT = Path(__file__).resolve().parent.parent
for _path in (_ROOT / "backend", _ROOT):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: E402

from app.core.database import AsyncSessionLocal, init_db  # noqa: E402
from app.models.content import (  # noqa: E402
    ContentCategory,
    Course,
    Lesson,
    Module,
    Subject,
    Topic,
)
from scripts.subject_content import (  # noqa: E402
    load_categories,
    load_lessons,
    load_overview,
    load_subject_catalog,
)

LEVELS = ("categories", "subjects", "courses", "modules", "topics", "lessons")


def _sync(record: Any, desired: dict[str, Any]) -> bool:
    """Copy changed fields onto an existing record; True when anything changed."""
    changed = False
    for name, value in desired.items():
        if getattr(record, name) != value:
            setattr(record, name, value)
            changed = True
    return changed


async def _upsert(db: AsyncSession, stats: dict[str, int], level: str, model: Any, match: dict[str, Any], desired: dict[str, Any]) -> Any:
    """Find the record by its natural key; create it, refresh it, or leave it alone."""
    stmt = select(model).filter_by(**match)
    record = (await db.execute(stmt)).scalars().first()
    if record is None:
        record = model(id=uuid.uuid4(), **match, **desired)
        db.add(record)
        await db.flush()
        stats[f"{level}_created"] += 1
    elif _sync(record, desired):
        await db.flush()
        stats[f"{level}_updated"] += 1
    else:
        stats[f"{level}_skipped"] += 1
    return record


async def seed_academic_content(db: AsyncSession) -> dict[str, int]:
    """Sync every category, subject, course, module, topic, and lesson from content/ into the database."""
    stats = {f"{level}_{outcome}": 0 for level in LEVELS for outcome in ("created", "updated", "skipped")}
    stats["topics_without_lesson"] = 0

    categories: dict[str, ContentCategory] = {}
    for cat in load_categories():
        categories[cat["slug"]] = await _upsert(
            db, stats, "categories", ContentCategory, {"slug": cat["slug"]},
            {"name": cat["name"], "description": cat["description"], "display_order": cat["display_order"], "is_active": True},
        )

    for sub in load_subject_catalog():
        subject = await _upsert(
            db, stats, "subjects", Subject, {"slug": sub["slug"]},
            {
                "category_id": categories[sub["category_slug"]].id,
                "name": sub["name"],
                "short_description": sub["short_description"],
                "description": load_overview(sub["slug"]) or sub.get("description"),
                "icon_key": sub.get("icon_key", "book"),
                "difficulty_level": sub.get("difficulty_level", "All Levels"),
                "display_order": sub["display_order"],
                "is_active": True,
            },
        )
        lessons = load_lessons(sub["slug"])

        for c_order, course_data in enumerate(sub.get("courses", []), start=1):
            course = await _upsert(
                db, stats, "courses", Course, {"subject_id": subject.id, "slug": course_data["slug"]},
                {
                    "title": course_data["title"],
                    "description": course_data["description"],
                    "difficulty": course_data.get("difficulty", "Beginner"),
                    "estimated_hours": course_data.get("estimated_hours", 10),
                    "display_order": c_order,
                    "is_active": True,
                },
            )
            for m_order, mod_data in enumerate(course_data.get("modules", []), start=1):
                module = await _upsert(
                    db, stats, "modules", Module, {"course_id": course.id, "slug": mod_data["slug"]},
                    {
                        "title": mod_data["title"],
                        "description": mod_data["description"],
                        "estimated_minutes": mod_data.get("estimated_minutes", 60),
                        "display_order": m_order,
                    },
                )
                for t_order, top_data in enumerate(mod_data.get("topics", []), start=1):
                    topic = await _upsert(
                        db, stats, "topics", Topic, {"module_id": module.id, "slug": top_data["slug"]},
                        {
                            "title": top_data["title"],
                            "summary": top_data.get("summary", ""),
                            "estimated_minutes": top_data.get("estimated_minutes", 30),
                            "difficulty": top_data.get("difficulty", "Beginner"),
                            "display_order": t_order,
                        },
                    )
                    lesson = lessons.get(top_data["slug"])
                    if lesson is None:
                        stats["topics_without_lesson"] += 1
                        continue
                    await _upsert(
                        db, stats, "lessons", Lesson, {"topic_id": topic.id, "slug": lesson.slug},
                        {
                            "title": lesson.title,
                            "summary": lesson.summary,
                            "content": lesson.content,
                            "learning_objectives": lesson.learning_objectives,
                            "estimated_minutes": lesson.estimated_minutes,
                            "lesson_type": lesson.lesson_type,
                            "display_order": 1,
                        },
                    )

    await db.commit()
    return stats


async def main() -> None:
    print("[INIT] Syncing the LuminaLearn academic curriculum from content/ ...")
    await init_db()
    async with AsyncSessionLocal() as session:
        stats = await seed_academic_content(session)
    print("=" * 64)
    for level in LEVELS:
        print(
            f"{level.capitalize():<11} created {stats[f'{level}_created']:>4} | "
            f"updated {stats[f'{level}_updated']:>4} | unchanged {stats[f'{level}_skipped']:>4}"
        )
    if stats["topics_without_lesson"]:
        print(f"Topics still without a lesson file: {stats['topics_without_lesson']}")
    print("=" * 64)


if __name__ == "__main__":
    asyncio.run(main())
