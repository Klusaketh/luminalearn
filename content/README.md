# LuminaLearn academic content

This folder is the source of truth for the Subjects module: every category, subject, syllabus, and lesson the catalog shows. The database holds a synced copy.

```
content/
  categories.json                          the four academic categories
  subjects/<subject-slug>/
    syllabus.json                          subject metadata and its course -> module -> topic tree
    overview.md                            the subject page: overview, objectives, prerequisites, glossary, reading
    lessons/<topic-slug>.md                one lesson per topic
```

## Applying changes

```bash
python scripts/seed_academic_content.py    # sync files -> database (safe to run any time)
python scripts/subjects_coverage.py        # rebuild docs/SUBJECTS_COVERAGE.md
cd backend && pytest tests/test_subject_content.py
```

The sync is non-destructive. It creates missing records and refreshes titles, descriptions, ordering, and lesson text. It never deletes a record and never changes an id or slug, because quiz history references topic ids.

Rules that keep it that way:

- Never rename a `slug` that has been published. Change the `title` instead.
- Never move a topic to another module, or a module to another course. The sync matches by parent and slug, so a moved item would be created again in its new place. Add a new topic instead.
- Removing an item from a file does not remove it from the database. Retire it deliberately.

## syllabus.json

```json
{
  "category_slug": "computer-science",
  "name": "Operating Systems",
  "slug": "operating-systems",
  "short_description": "One sentence for the catalog card.",
  "icon_key": "server",
  "difficulty_level": "Intermediate",
  "display_order": 2,
  "courses": [
    {
      "title": "...", "slug": "...", "description": "...", "difficulty": "Intermediate", "estimated_hours": 40,
      "modules": [
        {
          "title": "...", "slug": "...", "description": "...", "estimated_minutes": 120,
          "topics": [
            { "title": "...", "slug": "...", "summary": "...", "difficulty": "Beginner", "estimated_minutes": 45 }
          ]
        }
      ]
    }
  ]
}
```

Order in the file is the order learners see. `difficulty` is `Beginner`, `Intermediate`, or `Advanced`. Topic slugs must be unique within a subject, because lesson files are named after them.

## overview.md

Opening paragraphs describe the subject's scope and purpose (at least 80 words). Then these sections, in this order:

```markdown
## What you will learn
- One objective per line

## Prerequisites
- One prerequisite per line

## Glossary
- **Term**: definition

## Further reading
- Genuine, verifiable references only: author, title, publisher. No invented editions, chapters, or URLs.
```

## lessons/&lt;topic-slug&gt;.md

```markdown
---
lesson: lesson-slug
title: The lesson title
summary: One sentence shown under the title.
minutes: 45
type: theory
objectives:
  - What the learner can do afterwards
  - At least two objectives
---

## Introduction
## Core theory
## Worked examples
### Example 1: ...
## Applications
## Common mistakes
## Revision notes
## Practice questions
## Further learning
```

All eight sections are required, in this order. The page shows the title and objectives, so the body has no `# H1`.

- Math: `$inline$` and `$$display$$` (KaTeX).
- Code: fenced blocks with a language (`python`, `c`, `cpp`, `java`, `sql`, `bash`, `text`). Show expected output in a following `text` block. Code must be correct and runnable as shown.
- Diagrams: a ` ```mermaid ` block with `flowchart LR` or `flowchart TD`, nodes like `A[Label]`, edges `A --> B` or `A -->|label| B`. Use one only when it is accurate.
- Tables: GitHub-flavoured Markdown.

### Practice questions

At least five per lesson, mixing levels, each with a full answer and explanation:

```markdown
:::question basic
What is ...?
:::answer
The answer, and why.
:::
```

Levels are `basic`, `intermediate`, and `advanced`. The page hides answers until the learner opens them.

A lesson counts as complete only when it has every section, at least one `### Example`, five or more answered questions, two or more objectives, and 900 or more words. `docs/SUBJECTS_COVERAGE.md` shows the status of every topic.

## Accuracy

This is a foundational curriculum written for LuminaLearn, not the official syllabus of any institution. Do not add course codes, semester mappings, or exam regulations. Check every formula, algorithm trace, query result, and code output before publishing. Cite only references that really exist.
