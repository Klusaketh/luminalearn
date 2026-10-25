import uuid
from typing import ClassVar

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.onboarding_repository import onboarding_repository
from app.schemas.onboarding import (
    DiagnosticQuestion,
    LearnerProfileResponse,
    OnboardingSubmitRequest,
    PersonalizedRoadmapResponse,
    RoadmapModule,
)

# Canonical 10-Question Diagnostic Assessment Item Pool
DIAGNOSTIC_QUESTIONS: list[dict] = [
    {
        "id": 1,
        "subject": "Data Structures",
        "topic": "Arrays & Hashing",
        "difficulty": "Easy",
        "question": "What is the average-case time complexity of searching for a value in a hash table?",
        "options": ["O(1)", "O(n)", "O(log n)", "O(n^2)"],
        "correct_index": 0
    },
    {
        "id": 2,
        "subject": "Data Structures",
        "topic": "Trees & Graphs",
        "difficulty": "Medium",
        "question": "Which tree traversal strategy visits nodes in ascending key order for a Binary Search Tree (BST)?",
        "options": ["Pre-order", "In-order", "Post-order", "Level-order"],
        "correct_index": 1
    },
    {
        "id": 3,
        "subject": "Algorithms",
        "topic": "Sorting & Searching",
        "difficulty": "Easy",
        "question": "What is the worst-case time complexity of standard Merge Sort?",
        "options": ["O(n)", "O(n log n)", "O(n^2)", "O(2^n)"],
        "correct_index": 1
    },
    {
        "id": 4,
        "subject": "Algorithms",
        "topic": "Dynamic Programming",
        "difficulty": "Hard",
        "question": "Which algorithmic property must a problem possess to be solvable via Dynamic Programming?",
        "options": ["Greedy Choice Property", "Overlapping Subproblems & Optimal Substructure", "Divide and Conquer only", "Amortized Constant Time"],
        "correct_index": 1
    },
    {
        "id": 5,
        "subject": "Programming Fundamentals",
        "topic": "Python Core",
        "difficulty": "Easy",
        "question": "Which of the following Python data types is IMMUTABLE?",
        "options": ["List", "Dictionary", "Tuple", "Set"],
        "correct_index": 2
    },
    {
        "id": 6,
        "subject": "Programming Fundamentals",
        "topic": "Object-Oriented Programming",
        "difficulty": "Medium",
        "question": "What OOP principle allows a subclass to provide a specific implementation of a method defined in its superclass?",
        "options": ["Encapsulation", "Polymorphism / Method Overriding", "Abstraction", "Composition"],
        "correct_index": 1
    },
    {
        "id": 7,
        "subject": "Mathematics & Logic",
        "topic": "Linear Algebra",
        "difficulty": "Medium",
        "question": "What is the determinant of a $2 \\times 2$ identity matrix?",
        "options": ["0", "1", "2", "-1"],
        "correct_index": 1
    },
    {
        "id": 8,
        "subject": "Mathematics & Logic",
        "topic": "Probability & Statistics",
        "difficulty": "Medium",
        "question": "If events A and B are independent, what is P(A and B)?",
        "options": ["P(A) + P(B)", "P(A) * P(B)", "P(A) / P(B)", "P(A) + P(B) - P(A and B)"],
        "correct_index": 1
    },
    {
        "id": 9,
        "subject": "Databases & AI",
        "topic": "SQL & Relational DB",
        "difficulty": "Easy",
        "question": "Which SQL clause is used to filter records resulting from a GROUP BY clause?",
        "options": ["WHERE", "HAVING", "ORDER BY", "SELECT"],
        "correct_index": 1
    },
    {
        "id": 10,
        "subject": "Databases & AI",
        "topic": "AI & Machine Learning",
        "difficulty": "Medium",
        "question": "Which evaluation metric measures the ratio of true positive predictions to total predicted positives?",
        "options": ["Accuracy", "Recall", "Precision", "F1 Score"],
        "correct_index": 2
    }
]


class OnboardingService:
    """Service managing student onboarding and rule-based diagnostic profile evaluation."""

    CANONICAL_SUBJECT_MAP: ClassVar[dict[str, str]] = {
        "Data Structures": "Data Structures & Algorithms",
        "Algorithms": "Data Structures & Algorithms",
        "Data Structures & Algorithms": "Data Structures & Algorithms",
        "Python & AI Foundations": "Python",
        "Linear Algebra & Calculus": "Linear Algebra",
        "Database Systems & SQL": "Database Management Systems",
        "Full-Stack Web Engineering": "Computer Networks",
        "Machine Learning & Data Science": "Machine Learning",
        "Programming Fundamentals": "Python",
        "Mathematics & Logic": "Discrete Mathematics",
        "Databases & AI": "Database Management Systems",
    }

    def resolve_canonical_subject(self, raw_subject: str) -> str:
        """Safely translate onboarding subject selections into canonical academic catalog subject names."""
        return self.CANONICAL_SUBJECT_MAP.get(raw_subject.strip(), raw_subject.strip())

    def get_diagnostic_questions(self) -> list[DiagnosticQuestion]:

        """Return the 10 diagnostic questions without correct answers."""
        return [
            DiagnosticQuestion(
                id=q["id"],
                subject=q["subject"],
                topic=q["topic"],
                difficulty=q["difficulty"],
                question=q["question"],
                options=q["options"]
            )
            for q in DIAGNOSTIC_QUESTIONS
        ]

    async def process_onboarding_submission(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        payload: OnboardingSubmitRequest
    ) -> LearnerProfileResponse:
        """
        Evaluate diagnostic quiz answers, calculate strengths & weak areas,
        generate rule-based learner profile recommendations, and persist record.
        """
        # Map user answers by question id
        user_answer_map = {ans.question_id: ans.selected_option_index for ans in payload.answers}

        correct_count = 0
        topic_scores: dict[str, tuple[int, int]] = {}  # topic -> (correct, total)

        for q in DIAGNOSTIC_QUESTIONS:
            qid = q["id"]
            topic = q["topic"]
            correct_idx = q["correct_index"]

            user_selected = user_answer_map.get(qid)
            is_correct = (user_selected == correct_idx)

            if is_correct:
                correct_count += 1

            prev_correct, prev_total = topic_scores.get(topic, (0, 0))
            topic_scores[topic] = (prev_correct + (1 if is_correct else 0), prev_total + 1)

        total_questions = len(DIAGNOSTIC_QUESTIONS)
        score_percentage = round((correct_count / total_questions) * 100.0, 1)

        # Rule-based calculation of strengths and weak areas
        strengths: list[str] = []
        weak_areas: list[str] = []

        for topic, (c, t) in topic_scores.items():
            topic_acc = c / t
            if topic_acc >= 0.8:
                strengths.append(topic)
            elif topic_acc < 0.6:
                weak_areas.append(topic)

        # Default fallbacks if none categorized
        if not strengths and score_percentage >= 50:
            strengths.append("General Logical Reasoning")
        if not weak_areas and score_percentage < 100:
            weak_areas.append("Advanced Algorithm Optimization")

        # Rule-based calculation of recommended weekly study hours
        if score_percentage >= 75.0:
            recommended_hours = 7  # Advanced pace
        elif score_percentage >= 50.0:
            recommended_hours = 10  # Balanced pace
        else:
            recommended_hours = 14  # Foundational pace

        # Rule-based suggested starting topic
        if weak_areas:
            suggested_starting_topic = f"Remediation: {weak_areas[0]}"
        elif payload.selected_subjects:
            suggested_starting_topic = f"Foundations of {payload.selected_subjects[0]}"
        else:
            suggested_starting_topic = "Foundations of Computer Science & Programming"

        # Persist onboarding record in DB
        onboarding_record = await onboarding_repository.create_or_update(
            db,
            user_id=user_id,
            goals=payload.goals,
            interests=payload.interests,
            selected_subjects=payload.selected_subjects,
            assessment_score=score_percentage,
            strengths=strengths,
            weak_areas=weak_areas,
            recommended_weekly_hours=recommended_hours,
            suggested_starting_topic=suggested_starting_topic
        )

        return LearnerProfileResponse.model_validate(onboarding_record)

    async def get_user_roadmap(
        self,
        db: AsyncSession,
        user_id: uuid.UUID
    ) -> PersonalizedRoadmapResponse:
        """Fetch or generate personalized study roadmap for user."""
        profile = await onboarding_repository.get_by_user_id(db, user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Onboarding profile not found. Please complete the onboarding wizard first."
            )

        daily_target_mins = round((profile.recommended_weekly_hours * 60) / 7)
        raw_subject = profile.selected_subjects[0] if profile.selected_subjects else "Computer Science"
        primary_subject = self.resolve_canonical_subject(raw_subject)

        modules = [
          RoadmapModule(
              id=1,
              title=f"Module 1: {profile.suggested_starting_topic}",

              description="Master fundamental concepts and bridge identified diagnostic gaps.",
              estimated_hours=3,
              difficulty="Foundational",
              is_key_focus=True
          ),
          RoadmapModule(
              id=2,
              title=f"Module 2: Core {primary_subject} Mastery",
              description="Deep dive into key principles, problem-solving techniques, and worked examples.",
              estimated_hours=4,
              difficulty="Intermediate",
              is_key_focus=False
          ),
          RoadmapModule(
              id=3,
              title="Module 3: Socratic Practice & Exam Alignment",
              description="Interactive Socratic exercises tuned to your target goals.",
              estimated_hours=3,
              difficulty="Advanced",
              is_key_focus=False
          )
        ]

        return PersonalizedRoadmapResponse(
            profile=LearnerProfileResponse.model_validate(profile),
            recommended_course=f"Adaptive {primary_subject} Masterclass",
            weekly_goal_hours=profile.recommended_weekly_hours,
            daily_target_minutes=daily_target_mins,
            starting_module=profile.suggested_starting_topic,
            roadmap_modules=modules
        )


onboarding_service = OnboardingService()
