"""
LuminaLearn AI — Adaptive Quizzing Service.
Module: backend/app/services/quiz_service.py

Orchestrates dynamic question generation, Item Response Theory (IRT 2PL) parameter calibration,
Bayesian Knowledge Tracing (BKT) mastery tracking, and idempotent submission grading.
"""

import json
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ai.llm import LLMUnavailableError
from ai.rag.curriculum_rag import curriculum_rag
from app.core.config import settings
from app.models.content import Topic
from app.models.quiz import QuizAttempt, QuizQuestion, QuizSession, StudentTopicMastery
from app.schemas.quiz import (
    QuizGenerateRequest,
    QuizHistoryItem,
    QuizHistoryResponse,
    QuizMasteryResponse,
    QuizQuestionStudentView,
    QuizSessionDetail,
    QuizSubmitAnswerRequest,
    QuizSubmitAnswerResponse,
    RetentionForecastResponse,
    TopicMasterySummary,
)
from app.services.ai_runtime import gemini_gateway
from ml.models.knowledge_tracer import BayesianKnowledgeTracer, BKTParameters
from ml.models.retention_forecaster import RetentionForecaster

logger = logging.getLogger("luminalearn.quiz_service")

_BLOOMS_LEVELS = {"remembering", "understanding", "applying", "analyzing", "evaluating", "creating"}


# ------------------------------------------------------------------------------
# CURATED MATH & STEM FALLBACK BENCHMARKS (Deterministic Offline Resilience)
# ------------------------------------------------------------------------------
CURATED_BENCHMARKS: dict[str, list[dict[str, Any]]] = {
    "mathematics": [
        {
            "prompt": "Evaluate the definite integral: $\\int_{0}^{2} (3x^2 - 2x + 1)\\,dx$.",
            "options": ["$4$", "$6$", "$8$", "$10$"],
            "correct_answer": "$6$",
            "explanation": "Integrating term-by-term: $\\int 3x^2\\,dx = x^3$, $\\int -2x\\,dx = -x^2$, and $\\int 1\\,dx = x$. Evaluating $F(2) = 2^3 - 2^2 + 2 = 8 - 4 + 2 = 6$. $F(0) = 0$. Result is $6 - 0 = 6$.",
            "blooms_level": "applying",
            "irt_difficulty": 0.2,
            "irt_discrimination": 1.1,
            "misconception_map": {
                "$4$": "Subtracted linear term incorrectly or dropped constant term integration.",
                "$8$": "Computed only $2^3 = 8$ and omitted subsequent polynomial terms.",
                "$10$": "Added all values without subtracting $-x^2$."
            }
        },
        {
            "prompt": "Let matrix $A = \\begin{pmatrix} 2 & 1 \\\\ 1 & 2 \\end{pmatrix}$. What are the eigenvalues $\\lambda$ of matrix $A$?",
            "options": ["$\\lambda = 1, 3$", "$\\lambda = 0, 4$", "$\\lambda = -1, 3$", "$\\lambda = 2, 2$"],
            "correct_answer": "$\\lambda = 1, 3$",
            "explanation": "Characteristic equation is $\\det(A - \\lambda I) = (2-\\lambda)^2 - 1 = \\lambda^2 - 4\\lambda + 3 = 0$. Factoring gives $(\\lambda - 1)(\\lambda - 3) = 0$, so $\\lambda = 1, 3$.",
            "blooms_level": "analyzing",
            "irt_difficulty": 0.5,
            "irt_discrimination": 1.3,
            "misconception_map": {
                "$\\lambda = 2, 2$": "Assumed diagonal entries are eigenvalues without computing the determinant for non-diagonal matrix.",
                "$\\lambda = 0, 4$": "Miscalculated the constant determinant term.",
                "$\\lambda = -1, 3$": "Sign error when factoring the quadratic polynomial."
            }
        },
        {
            "prompt": "According to Bayes' Theorem, if event $A$ has prior $P(A) = 0.2$, $P(B|A) = 0.8$, and $P(B|\\neg A) = 0.1$, what is the posterior $P(A|B)$?",
            "options": ["$0.50$", "$0.67$", "$0.80$", "$0.33$"],
            "correct_answer": "$0.67$",
            "explanation": "$P(B) = P(B|A)P(A) + P(B|\\neg A)P(\\neg A) = (0.8)(0.2) + (0.1)(0.8) = 0.16 + 0.08 = 0.24$. Then $P(A|B) = \\frac{0.16}{0.24} = \\frac{2}{3} \\approx 0.67$.",
            "blooms_level": "evaluating",
            "irt_difficulty": 0.7,
            "irt_discrimination": 1.4,
            "misconception_map": {
                "$0.50$": "Averaged conditional likelihoods without accounting for prior weighting.",
                "$0.80$": "Confused $P(A|B)$ with $P(B|A)$ (base-rate fallacy).",
                "$0.33$": "Omitted prior probability $P(A)$ from the numerator."
            }
        },
        {
            "prompt": "What is the derivative of $f(x) = e^{x} \\sin(x)$ with respect to $x$?",
            "options": [
                "$e^x \\cos(x)$",
                "$e^x (\\sin(x) + \\cos(x))$",
                "$e^x (\\sin(x) - \\cos(x))$",
                "$e^x \\sin(x) \\cos(x)$"
            ],
            "correct_answer": "$e^x (\\sin(x) + \\cos(x))$",
            "explanation": "Applying the Product Rule $\\frac{d}{dx}[uv] = u'v + uv'$: $\\frac{d}{dx}[e^x] = e^x$ and $\\frac{d}{dx}[\\sin(x)] = \\cos(x)$. Factoring $e^x$ yields $e^x(\\sin(x) + \\cos(x))$.",
            "blooms_level": "understanding",
            "irt_difficulty": -0.2,
            "irt_discrimination": 1.0,
            "misconception_map": {
                "$e^x \\cos(x)$": "Differentiated only the trigonometric term, violating the Product Rule.",
                "$e^x (\\sin(x) - \\cos(x))$": "Sign error on derivative of sine (confusing with cosine derivative).",
                "$e^x \\sin(x) \\cos(x)$": "Multiplied derivatives instead of applying additive product rule."
            }
        },
        {
            "prompt": "In linear algebra, a set of vectors $\\{\\mathbf{v}_1, \\mathbf{v}_2, \\dots, \\mathbf{v}_k\\}$ is linearly independent if and only if:",
            "options": [
                "$c_1\\mathbf{v}_1 + \\dots + c_k\\mathbf{v}_k = \\mathbf{0}$ has only the trivial solution $c_1 = \\dots = c_k = 0$.",
                "At least one vector is a scalar multiple of another.",
                "The determinant of any matrix formed by these vectors is always zero.",
                "The dot product between every pair of vectors is zero."
            ],
            "correct_answer": "$c_1\\mathbf{v}_1 + \\dots + c_k\\mathbf{v}_k = \\mathbf{0}$ has only the trivial solution $c_1 = \\dots = c_k = 0$.",
            "explanation": "By definition, vectors are linearly independent if no vector in the set can be represented as a linear combination of the others, meaning the zero vector can only be formed by all zero scalars.",
            "blooms_level": "remembering",
            "irt_difficulty": -0.5,
            "irt_discrimination": 0.9,
            "misconception_map": {
                "The dot product between every pair of vectors is zero.": "Confused linear independence with orthogonality.",
                "At least one vector is a scalar multiple of another.": "This describes linear dependence, the exact opposite.",
                "The determinant of any matrix formed by these vectors is always zero.": "A zero determinant signifies linear dependence in square matrices."
            }
        }
    ]
}


class QuizService:
    """Service handling adaptive quiz session generation, grading, and Bayesian mastery tracking."""

    def __init__(self) -> None:
        self.tracer = BayesianKnowledgeTracer(BKTParameters())
        self.forecaster = RetentionForecaster()

    async def generate_quiz_session(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        request: QuizGenerateRequest
    ) -> QuizSessionDetail:
        """
        Generates an adaptive quiz session for the given topic.
        Attempts Gemini structured generation, falling back gracefully to validated benchmark items.
        """
        # Validate or resolve topic
        topic_title = request.topic.strip()
        topic_id = request.topic_id

        if topic_id:
            db_topic = await db.get(Topic, topic_id)
            if db_topic:
                topic_title = db_topic.title

        # Determine current student mastery on this topic
        initial_mastery = await self.get_latest_mastery(db, user_id, topic_title)

        # Generate calibrated questions
        generated_raw = await self._generate_questions_with_gemini_or_fallback(
            topic=topic_title,
            difficulty=request.difficulty,
            count=request.question_count,
            current_mastery=initial_mastery
        )

        # Create QuizSession entity
        session = QuizSession(
            user_id=user_id,
            topic_title=topic_title,
            topic_id=topic_id,
            difficulty_level=request.difficulty,
            total_questions=len(generated_raw),
            score=0.0,
            status="in_progress",
            initial_mastery=initial_mastery
        )
        db.add(session)
        await db.flush()  # obtain session.id

        # Create QuizQuestion entities
        questions: list[QuizQuestion] = []
        for idx, q_data in enumerate(generated_raw):
            q_entity = QuizQuestion(
                session_id=session.id,
                question_index=idx,
                prompt=q_data["prompt"],
                options=q_data["options"],
                correct_answer=q_data["correct_answer"],
                explanation=q_data["explanation"],
                blooms_level=q_data.get("blooms_level", "understanding"),
                question_type=q_data.get("question_type", "multiple_choice"),
                source_reference=q_data.get("source_reference"),
                irt_difficulty=float(q_data.get("irt_difficulty", 0.0)),
                irt_discrimination=float(q_data.get("irt_discrimination", 1.0)),
                misconception_map=q_data.get("misconception_map", {})
            )
            db.add(q_entity)
            questions.append(q_entity)

        await db.commit()

        # Re-query session with questions loaded
        stmt = (
            select(QuizSession)
            .where(QuizSession.id == session.id)
            .options(selectinload(QuizSession.questions))
        )
        result = await db.execute(stmt)
        full_session = result.scalar_one()

        student_questions = [
            QuizQuestionStudentView(
                id=q.id,
                question_index=q.question_index,
                prompt=q.prompt,
                options=q.options,
                blooms_level=q.blooms_level,
                question_type=getattr(q, "question_type", "multiple_choice"),
                source_reference=getattr(q, "source_reference", None),
                irt_difficulty=q.irt_difficulty
            )
            for q in full_session.questions
        ]

        return QuizSessionDetail(
            id=full_session.id,
            topic_title=full_session.topic_title,
            difficulty_level=full_session.difficulty_level,
            total_questions=full_session.total_questions,
            score=full_session.score,
            status=full_session.status,
            initial_mastery=full_session.initial_mastery,
            final_mastery=full_session.final_mastery,
            created_at=full_session.created_at,
            completed_at=full_session.completed_at,
            questions=student_questions
        )

    async def get_quiz_session(
        self,
        db: AsyncSession,
        session_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> QuizSessionDetail:
        """Retrieves an active or completed quiz session, validating ownership."""
        stmt = (
            select(QuizSession)
            .where(QuizSession.id == session_id)
            .options(selectinload(QuizSession.questions))
        )
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz session not found."
            )
        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this quiz session."
            )

        student_questions = [
            QuizQuestionStudentView(
                id=q.id,
                question_index=q.question_index,
                prompt=q.prompt,
                options=q.options,
                blooms_level=q.blooms_level,
                question_type=getattr(q, "question_type", "multiple_choice"),
                source_reference=getattr(q, "source_reference", None),
                irt_difficulty=q.irt_difficulty
            )
            for q in session.questions
        ]

        return QuizSessionDetail(
            id=session.id,
            topic_title=session.topic_title,
            difficulty_level=session.difficulty_level,
            total_questions=session.total_questions,
            score=session.score,
            status=session.status,
            initial_mastery=session.initial_mastery,
            final_mastery=session.final_mastery,
            created_at=session.created_at,
            completed_at=session.completed_at,
            questions=student_questions
        )

    async def submit_question_answer(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        request: QuizSubmitAnswerRequest
    ) -> QuizSubmitAnswerResponse:
        """
        Grades an answer submission, computes BKT posterior mastery,
        detects conceptual misconceptions, and records the attempt idempotently.
        """
        # Fetch session
        session = await db.get(QuizSession, request.session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz session not found."
            )
        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this quiz session."
            )

        # Fetch question
        question = await db.get(QuizQuestion, request.question_id)
        if not question or question.session_id != session.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question does not belong to this quiz session."
            )

        # Check for existing attempt (Idempotency Invariant)
        stmt = (
            select(QuizAttempt)
            .where(
                QuizAttempt.session_id == session.id,
                QuizAttempt.question_id == question.id,
                QuizAttempt.user_id == user_id
            )
        )
        existing_attempt = (await db.execute(stmt)).scalar_one_or_none()

        if existing_attempt:
            # Idempotently return the existing result without double-counting BKT
            pred_acc = self.tracer.predict_performance(existing_attempt.bkt_posterior_mastery)
            next_mastery = self.tracer.apply_learning_transition(existing_attempt.bkt_posterior_mastery)
            previous_level = self._calculate_retention_level(existing_attempt.bkt_prior_mastery)
            current_level = self._calculate_retention_level(next_mastery)
            return QuizSubmitAnswerResponse(
                attempt_id=existing_attempt.id,
                is_correct=existing_attempt.is_correct,
                selected_answer=existing_attempt.selected_answer,
                correct_answer=question.correct_answer,
                explanation=question.explanation,
                detected_misconception=existing_attempt.detected_misconception,
                feedback=existing_attempt.feedback,
                prior_mastery=existing_attempt.bkt_prior_mastery,
                posterior_mastery=existing_attempt.bkt_posterior_mastery,
                next_opportunity_mastery=next_mastery,
                predicted_accuracy=pred_acc,
                session_completed=session.status == "completed",
                session_score=session.score,
                session_final_mastery=session.final_mastery,
                previous_retention_level=previous_level,
                retention_level=current_level,
                level_up=self._is_level_up(previous_level, current_level),
            )

        # Determine correctness and confidence
        selected = request.selected_answer.strip()
        correct = question.correct_answer.strip()
        confidence: float | None = 1.0
        is_free_response = getattr(question, "question_type", "multiple_choice") == "free_response"
        feedback = ""

        if is_free_response:
            is_correct, detected_misconception, confidence, feedback = self._evaluate_free_response(
                student_answer=selected,
                reference_answer=correct,
                explanation=question.explanation,
                misconception_map=question.misconception_map
            )
        else:
            is_correct = (selected.lower() == correct.lower())
            detected_misconception = None
            if not is_correct and question.misconception_map:
                for opt_key, reason in question.misconception_map.items():
                    if selected.lower() == opt_key.lower():
                        detected_misconception = reason
                        break
                if not detected_misconception:
                    detected_misconception = "Conceptual error: review prerequisite definitions."

        # Determine prior mastery for this topic
        prior_mastery = await self.get_latest_mastery(db, user_id, session.topic_title)

        # Compute BKT Bayesian update
        posterior_mastery, next_opportunity_mastery = self.tracer.step(prior_mastery, is_correct)
        predicted_accuracy = self.tracer.predict_performance(posterior_mastery)

        # Multiple-choice feedback quotes the updated posterior, so it is built after the BKT step
        if not is_free_response:
            if is_correct:
                feedback = f"Excellent! Your reasoning is correct. Concept mastery increased to {int(posterior_mastery * 100)}%."
            else:
                feedback = f"Incorrect. {detected_misconception or 'Review the underlying steps.'} Explanation: {question.explanation}"

        previous_level = self._calculate_retention_level(prior_mastery)
        current_level = self._calculate_retention_level(next_opportunity_mastery)

        # Create Attempt record
        attempt = QuizAttempt(
            session_id=session.id,
            question_id=question.id,
            user_id=user_id,
            selected_answer=selected,
            is_correct=is_correct,
            latency_ms=request.latency_ms,
            bkt_prior_mastery=prior_mastery,
            bkt_posterior_mastery=posterior_mastery,
            detected_misconception=detected_misconception,
            feedback=feedback
        )
        db.add(attempt)

        # Update Session Score
        total_attempts_stmt = (
            select(func.count(QuizAttempt.id), func.count(QuizAttempt.id).filter(QuizAttempt.is_correct))
            .where(QuizAttempt.session_id == session.id)
        )
        attempt_counts = (await db.execute(total_attempts_stmt)).one()
        new_total_attempts = attempt_counts[0] + 1
        new_correct_attempts = attempt_counts[1] + (1 if is_correct else 0)

        session.score = round((new_correct_attempts / session.total_questions) * 100.0, 1)

        # Check if session is completed
        session_completed = (new_total_attempts >= session.total_questions)
        if session_completed:
            session.status = "completed"
            session.completed_at = datetime.now(timezone.utc)
            session.final_mastery = next_opportunity_mastery

        # Transactional update of StudentTopicMastery
        mastery_stmt = select(StudentTopicMastery).where(
            StudentTopicMastery.user_id == user_id,
            func.lower(StudentTopicMastery.topic_title) == func.lower(session.topic_title)
        )
        topic_mastery = (await db.execute(mastery_stmt)).scalar_one_or_none()
        retention_lvl = self._calculate_retention_level(next_opportunity_mastery)

        if not topic_mastery:
            topic_mastery = StudentTopicMastery(
                user_id=user_id,
                topic_title=session.topic_title,
                topic_id=session.topic_id,
                current_mastery=next_opportunity_mastery,
                predicted_accuracy=predicted_accuracy,
                total_attempts=1,
                correct_attempts=1 if is_correct else 0,
                streak=1 if is_correct else 0,
                retention_level=retention_lvl,
                last_attempt_at=datetime.now(timezone.utc)
            )
            db.add(topic_mastery)
        else:
            topic_mastery.current_mastery = next_opportunity_mastery
            topic_mastery.predicted_accuracy = predicted_accuracy
            topic_mastery.total_attempts += 1
            if is_correct:
                topic_mastery.correct_attempts += 1
                topic_mastery.streak += 1
            else:
                topic_mastery.streak = 0
            topic_mastery.retention_level = retention_lvl
            topic_mastery.last_attempt_at = datetime.now(timezone.utc)
            if session.topic_id and not topic_mastery.topic_id:
                topic_mastery.topic_id = session.topic_id

        await db.commit()
        await db.refresh(attempt)

        return QuizSubmitAnswerResponse(
            attempt_id=attempt.id,
            is_correct=is_correct,
            selected_answer=selected,
            correct_answer=correct,
            explanation=question.explanation,
            detected_misconception=detected_misconception,
            feedback=feedback,
            prior_mastery=prior_mastery,
            posterior_mastery=posterior_mastery,
            next_opportunity_mastery=next_opportunity_mastery,
            predicted_accuracy=predicted_accuracy,
            confidence=confidence,
            session_completed=session_completed,
            session_score=session.score,
            session_final_mastery=session.final_mastery,
            previous_retention_level=previous_level,
            retention_level=current_level,
            level_up=self._is_level_up(previous_level, current_level),
        )

    async def get_latest_mastery(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        topic_title: str
    ) -> float:
        """Retrieves the latest posterior BKT mastery score for a user on a given topic."""
        stmt = (
            select(QuizAttempt.bkt_posterior_mastery)
            .join(QuizSession, QuizAttempt.session_id == QuizSession.id)
            .where(
                QuizAttempt.user_id == user_id,
                func.lower(QuizSession.topic_title) == func.lower(topic_title)
            )
            .order_by(desc(QuizAttempt.created_at))
            .limit(1)
        )
        latest = (await db.execute(stmt)).scalar_one_or_none()
        if latest is not None:
            # Apply transition for current opportunity
            return self.tracer.apply_learning_transition(float(latest))
        return self.tracer.params.p_l0

    async def get_topic_mastery_report(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        topic_title: str
    ) -> QuizMasteryResponse:
        """Generates comprehensive mastery analytics and attempt history for a topic."""
        current_mastery = await self.get_latest_mastery(db, user_id, topic_title)
        predicted_acc = self.tracer.predict_performance(current_mastery)

        # Fetch attempt history
        stmt = (
            select(QuizAttempt)
            .join(QuizSession, QuizAttempt.session_id == QuizSession.id)
            .where(
                QuizAttempt.user_id == user_id,
                func.lower(QuizSession.topic_title) == func.lower(topic_title)
            )
            .order_by(QuizAttempt.created_at)
        )
        attempts = (await db.execute(stmt)).scalars().all()

        total = len(attempts)
        correct = sum(1 for a in attempts if a.is_correct)

        # Retention classification
        if current_mastery >= 0.85:
            retention_level = "Mastered"
        elif current_mastery >= 0.60:
            retention_level = "Competent"
        elif current_mastery >= 0.30:
            retention_level = "Developing"
        else:
            retention_level = "Novice"

        history_items = [
            {
                "attempt_id": str(a.id),
                "is_correct": a.is_correct,
                "latency_ms": a.latency_ms,
                "posterior_mastery": a.bkt_posterior_mastery,
                "created_at": a.created_at.isoformat()
            }
            for a in attempts
        ]

        return QuizMasteryResponse(
            topic_title=topic_title,
            topic_id=None,
            current_mastery=round(current_mastery, 4),
            predicted_accuracy=round(predicted_acc, 4),
            total_attempts=total,
            correct_attempts=correct,
            retention_level=retention_level,
            history=history_items,
            retention_forecast=RetentionForecastResponse(**self.forecaster.forecast(current_mastery)),
        )

    async def get_topic_masteries(self, db: AsyncSession, user_id: uuid.UUID) -> list[TopicMasterySummary]:
        """Every topic the learner has been assessed on, strongest first (feeds the knowledge radar)."""
        stmt = (
            select(StudentTopicMastery)
            .where(StudentTopicMastery.user_id == user_id)
            .order_by(desc(StudentTopicMastery.current_mastery))
        )
        records = (await db.execute(stmt)).scalars().all()
        return [
            TopicMasterySummary(
                topic_title=r.topic_title,
                current_mastery=round(r.current_mastery, 4),
                predicted_accuracy=round(r.predicted_accuracy, 4),
                retention_level=r.retention_level,
                total_attempts=r.total_attempts,
                correct_attempts=r.correct_attempts,
                streak=r.streak,
                last_attempt_at=r.last_attempt_at,
            )
            for r in records
        ]

    _LEVEL_ORDER = ("Novice", "Developing", "Competent", "Mastered")

    def _calculate_retention_level(self, mastery: float) -> str:
        """Categorizes BKT mastery into human-interpretable competency tiers."""
        if mastery >= 0.85:
            return "Mastered"
        elif mastery >= 0.60:
            return "Competent"
        elif mastery >= 0.30:
            return "Developing"
        return "Novice"

    def _is_level_up(self, previous_level: str, current_level: str) -> bool:
        """True when an answer lifted the learner into a higher competency tier."""
        return self._LEVEL_ORDER.index(current_level) > self._LEVEL_ORDER.index(previous_level)

    def _evaluate_free_response(
        self,
        student_answer: str,
        reference_answer: str,
        explanation: str,
        misconception_map: dict[str, Any] | None = None
    ) -> tuple[bool, str | None, float, str]:
        """
        Evaluates conceptual free-response submission using rubric-based keyword and conceptual density matching.
        Returns: (is_correct, detected_misconception, confidence, feedback)
        """
        norm_student = student_answer.strip().lower()
        norm_ref = reference_answer.strip().lower()

        stopwords = {"with", "that", "this", "from", "they", "were", "been", "have", "more", "when", "what", "which", "will"}
        ref_tokens = {
            w for w in re.findall(r"\b[a-z]{4,}\b", norm_ref)
            if w not in stopwords
        }
        student_tokens = set(re.findall(r"\b[a-z]{3,}\b", norm_student))

        if not ref_tokens:
            is_correct = (norm_student == norm_ref)
            confidence = 1.0 if is_correct else 0.80
            misconception = None if is_correct else "Answer did not match expected concept."
            feedback = "Correct." if is_correct else f"Review key principles: {explanation}"
            return is_correct, misconception, confidence, feedback

        overlap = len(ref_tokens.intersection(student_tokens))
        match_ratio = overlap / len(ref_tokens)

        detected_misconception = None
        if misconception_map:
            for mis_trigger, mis_desc in misconception_map.items():
                if mis_trigger.lower() in norm_student:
                    detected_misconception = str(mis_desc)
                    break

        if match_ratio >= 0.60:
            is_correct = True
            confidence = round(min(0.95, 0.70 + 0.3 * match_ratio), 2)
            feedback = f"Conceptual understanding demonstrated (coverage: {int(match_ratio * 100)}%). Evaluated against rubric."
        elif match_ratio >= 0.30:
            is_correct = False
            confidence = 0.65
            if not detected_misconception:
                detected_misconception = "Partial concept coverage; key foundational steps omitted."
            feedback = f"Partially addressing the prompt, but missed essential concepts. Rubric guidance: {explanation}"
        else:
            is_correct = False
            confidence = 0.85
            if not detected_misconception:
                detected_misconception = "Incomplete or inaccurate explanation of the core phenomenon."
            feedback = f"Concept not clearly demonstrated. Educational explanation: {explanation}"

        return is_correct, detected_misconception, confidence, feedback

    async def get_quiz_history(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 10
    ) -> QuizHistoryResponse:
        """Retrieves paginated historical quiz sessions for the authenticated student."""
        offset = (max(1, page) - 1) * page_size

        count_stmt = (
            select(func.count(QuizSession.id))
            .where(QuizSession.user_id == user_id)
        )
        total = (await db.execute(count_stmt)).scalar() or 0

        stmt = (
            select(QuizSession)
            .where(QuizSession.user_id == user_id)
            .order_by(desc(QuizSession.created_at))
            .offset(offset)
            .limit(page_size)
        )
        sessions = (await db.execute(stmt)).scalars().all()

        items = [
            QuizHistoryItem(
                id=s.id,
                topic_title=s.topic_title,
                difficulty_level=s.difficulty_level,
                total_questions=s.total_questions,
                score=s.score,
                status=s.status,
                initial_mastery=s.initial_mastery,
                final_mastery=s.final_mastery,
                created_at=s.created_at,
                completed_at=s.completed_at
            )
            for s in sessions
        ]

        return QuizHistoryResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=items
        )

    async def _generate_questions_with_gemini_or_fallback(
        self,
        topic: str,
        difficulty: str,
        count: int,
        current_mastery: float
    ) -> list[dict[str, Any]]:
        """
        Attempts to call the Google Gemini API for structured generation grounded in curriculum context.
        On any failure or missing key, falls back to deterministic curated benchmarks.
        """
        curriculum_chunks = curriculum_rag.retrieve(query=topic, top_k=2)
        grounded_context = curriculum_rag.format_grounded_context(curriculum_chunks) if curriculum_chunks else ""
        source_ref = curriculum_chunks[0].citation if curriculum_chunks else None

        if gemini_gateway.enabled:
            try:
                generated = await self._call_gemini_api(topic, difficulty, count, current_mastery, grounded_context)
                if len(generated) >= count:
                    for item in generated:
                        if not item.get("source_reference"):
                            item["source_reference"] = source_ref
                    return generated[:count]
                logger.warning("Gemini returned %s valid questions (needed %s); using curated benchmarks.", len(generated), count)
            except (LLMUnavailableError, ValueError, TypeError) as exc:
                logger.warning("Gemini generation unavailable (%s). Activating resilient benchmark fallback.", exc)

        # Offline / Curated Benchmark Fallback
        fallback_questions = self._get_curated_fallback_questions(topic, count)
        for q in fallback_questions:
            if not q.get("source_reference"):
                q["source_reference"] = source_ref
        return fallback_questions

    async def _call_gemini_api(
        self,
        topic: str,
        difficulty: str,
        count: int,
        current_mastery: float,
        grounded_context: str = ""
    ) -> list[dict[str, Any]]:
        """Asks Gemini (JSON mode, bounded by the gateway's deadlines) for calibrated questions."""
        grounding = (
            f"\nGround the questions in this verified material where relevant:\n{grounded_context}\n"
            if grounded_context
            else ""
        )
        prompt = f"""
You are the LuminaLearn AI Assessment Engine.
Generate exactly {count} distinct multiple-choice questions for the academic topic: "{topic}".
Target Difficulty: {difficulty}. The learner's current Bayesian mastery is {round(current_mastery * 100)}%.
{grounding}
Follow Bloom's Taxonomy progression:
1. Remembering (Definitions / Core rules)
2. Understanding (Principles / Interpretations)
3. Applying (Calculations / Formula applications)
4. Analyzing (Decomposition / Identifying bugs or pitfalls)
5. Evaluating (Comparing approaches / Boundary condition validation)

Rules:
- Exactly 4 options per question; "correct_answer" must be copied verbatim from "options".
- Vary the position of the correct option across questions.
- "irt_difficulty" is the IRT b parameter in [-3, 3]; "irt_discrimination" is the IRT a parameter in [0.5, 2.5].
- For mathematical or scientific equations, use KaTeX LaTeX notation (e.g. $\\int_{{0}}^{{1}} x^2 dx$ or $\\mathbf{{A}}x = \\lambda x$).

Return a JSON array only, matching this exact schema:
[
  {{
    "prompt": "Question text...",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option A",
    "explanation": "Educational derivation of why Option A is correct...",
    "blooms_level": "applying",
    "irt_difficulty": 0.2,
    "irt_discrimination": 1.1,
    "misconception_map": {{
      "Option B": "Reason student chose this distractor...",
      "Option C": "Reason student chose this distractor...",
      "Option D": "Reason student chose this distractor..."
    }}
  }}
]
"""
        result = await gemini_gateway.generate_text(
            prompt,
            temperature=settings.GEMINI_TEMPERATURE,
            max_output_tokens=max(settings.GEMINI_MAX_TOKENS, 900 * count),
            thinking="low",
            json_mode=True,
            timeout_s=25.0,
        )
        raw_text = result.text
        json_match = re.search(r"\[\s*\{.*\}\s*\]", raw_text, re.DOTALL)
        if not json_match:
            raise ValueError("Could not extract valid JSON array of questions from Gemini response.")
        try:
            data = json.loads(json_match.group(0))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Gemini returned malformed JSON: {exc}") from exc
        if not isinstance(data, list):
            raise TypeError("Gemini JSON payload is not a list of questions.")
        return [question for item in data if (question := self._validate_generated_question(item)) is not None]

    @staticmethod
    def _validate_generated_question(item: Any) -> dict[str, Any] | None:
        """Accepts a generated question only if it is internally consistent; otherwise drops it."""
        if not isinstance(item, dict):
            return None
        prompt, options, answer = item.get("prompt"), item.get("options"), item.get("correct_answer")
        if not isinstance(prompt, str) or not prompt.strip() or not isinstance(answer, str):
            return None
        if not isinstance(options, list) or not all(isinstance(o, str) and o.strip() for o in options):
            return None
        unique_options = list(dict.fromkeys(o.strip() for o in options))
        if len(unique_options) < 2 or answer.strip() not in unique_options:
            return None
        explanation = item.get("explanation")
        blooms = str(item.get("blooms_level", "understanding")).strip().lower()
        try:
            difficulty = max(-3.0, min(3.0, float(item.get("irt_difficulty", 0.0))))
            discrimination = max(0.5, min(2.5, float(item.get("irt_discrimination", 1.0))))
        except (TypeError, ValueError):
            difficulty, discrimination = 0.0, 1.0
        misconceptions = item.get("misconception_map")
        return {
            "prompt": prompt.strip(),
            "options": unique_options,
            "correct_answer": answer.strip(),
            "explanation": explanation.strip() if isinstance(explanation, str) and explanation.strip() else "Review the underlying definition and try again.",
            "blooms_level": blooms if blooms in _BLOOMS_LEVELS else "understanding",
            "irt_difficulty": difficulty,
            "irt_discrimination": discrimination,
            "misconception_map": {str(k): str(v) for k, v in misconceptions.items()} if isinstance(misconceptions, dict) else {},
        }

    def _get_curated_fallback_questions(self, topic: str, count: int) -> list[dict[str, Any]]:
        """Returns deterministic, pedagogically sound questions when offline or API is unavailable."""
        topic_lower = topic.lower()

        # Check if topic aligns with mathematics benchmarks
        if any(kw in topic_lower for kw in ["math", "calculus", "algebra", "integral", "matrix", "bayes", "probability"]):
            pool = CURATED_BENCHMARKS["mathematics"]
        else:
            # Universal STEM / Computer Science benchmark fallback
            pool = [
                {
                    "prompt": f"In the study of {topic}, which of the following best characterizes the primary foundational principle?",
                    "options": [
                        "Decomposition of complex structures into verifiable sub-components.",
                        "Random heuristic search without deterministic guarantees.",
                        "Direct manipulation of binary registers without abstractions.",
                        "Elimination of all time-complexity trade-offs."
                    ],
                    "correct_answer": "Decomposition of complex structures into verifiable sub-components.",
                    "explanation": f"Foundational mastery of {topic} relies on systematic abstraction and formal decomposition into testable, modular components.",
                    "blooms_level": "understanding",
                    "irt_difficulty": -0.1,
                    "irt_discrimination": 1.0,
                    "misconception_map": {
                        "Random heuristic search without deterministic guarantees.": "Confuses empirical trial-and-error with formal principles.",
                        "Direct manipulation of binary registers without abstractions.": "Overly focuses on low-level implementation rather than core models."
                    }
                },
                {
                    "prompt": f"When analyzing the efficiency bounds in {topic}, what metric is typically utilized to evaluate worst-case algorithmic complexity?",
                    "options": [
                        "Big-O notation $\\mathcal{O}(f(n))$ asymptotic upper bound.",
                        "Wall-clock runtime on a specific physical processor in milliseconds.",
                        "Lines of source code required to implement the algorithm.",
                        "Total number of floating-point operations divided by clock speed."
                    ],
                    "correct_answer": "Big-O notation $\\mathcal{O}(f(n))$ asymptotic upper bound.",
                    "explanation": "Asymptotic Big-O notation measures the mathematical growth rate of resource requirements independent of specific hardware.",
                    "blooms_level": "remembering",
                    "irt_difficulty": -0.3,
                    "irt_discrimination": 1.1,
                    "misconception_map": {
                        "Wall-clock runtime on a specific physical processor in milliseconds.": "Wall-clock time is hardware-dependent and non-deterministic."
                    }
                },
                {
                    "prompt": f"Which design pattern or methodology is most effective in {topic} for preventing unintended side-effects across asynchronous execution boundaries?",
                    "options": [
                        "Immutable data structures and stateless functional transformations.",
                        "Global shared mutable memory without lock contention boundaries.",
                        "Unbounded polling loops checking boolean flags.",
                        "Catching all exceptions and suppressing diagnostic logging."
                    ],
                    "correct_answer": "Immutable data structures and stateless functional transformations.",
                    "explanation": "Immutability guarantees thread safety and prevents race conditions across asynchronous boundaries.",
                    "blooms_level": "analyzing",
                    "irt_difficulty": 0.4,
                    "irt_discrimination": 1.2,
                    "misconception_map": {
                        "Global shared mutable memory without lock contention boundaries.": "Causes severe concurrency race conditions.",
                        "Catching all exceptions and suppressing diagnostic logging.": "Anti-pattern that hides catastrophic failures."
                    }
                },
                {
                    "prompt": f"Given a system modeled under {topic}, what is the consequence of violating the invariant boundary conditions?",
                    "options": [
                        "State corruption leading to non-deterministic failure modes.",
                        "Automatic self-healing with zero computational overhead.",
                        "Guaranteed constant-time performance improvement.",
                        "Elimination of all network latency."
                    ],
                    "correct_answer": "State corruption leading to non-deterministic failure modes.",
                    "explanation": "Invariants maintain integrity; violating them leads to undefined behavior and corrupted states.",
                    "blooms_level": "evaluating",
                    "irt_difficulty": 0.6,
                    "irt_discrimination": 1.3,
                    "misconception_map": {
                        "Automatic self-healing with zero computational overhead.": "Self-healing requires explicit supervisory architecture."
                    }
                },
                {
                    "prompt": f"What is the mathematical definition of convergence in iterative algorithms for {topic}?",
                    "options": [
                        "The sequence of estimates satisfies $\\lim_{k \\to \\infty} \\|x^{(k+1)} - x^{(k)}\\| < \\epsilon$ for a given tolerance $\\epsilon$.",
                        "The algorithm terminates after a fixed number of loop steps regardless of error residual.",
                        "The parameter values oscillate indefinitely between positive and negative bounds.",
                        "The computational complexity increases exponentially at each step."
                    ],
                    "correct_answer": "The sequence of estimates satisfies $\\lim_{k \\to \\infty} \\|x^{(k+1)} - x^{(k)}\\| < \\epsilon$ for a given tolerance $\\epsilon$.",
                    "explanation": "Convergence means successive approximations grow arbitrarily close to the exact solution within a bounded tolerance.",
                    "blooms_level": "applying",
                    "irt_difficulty": 0.3,
                    "irt_discrimination": 1.1,
                    "misconception_map": {
                        "The algorithm terminates after a fixed number of loop steps regardless of error residual.": "A step limit is an iteration cap, not mathematical convergence."
                    }
                }
            ]

        # Duplicate or slice to meet exact count
        result: list[dict[str, Any]] = []
        while len(result) < count:
            result.extend(dict(item) for item in pool)
        return result[:count]


# Global Instantiated Quiz Service Singleton
quiz_service = QuizService()
