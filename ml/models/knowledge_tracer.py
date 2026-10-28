"""
LuminaLearn AI — Bayesian Knowledge Tracing (BKT) & Item Response Theory (IRT) Engine.
Module: ml/models/knowledge_tracer.py

Deterministic mathematical models for tracking student concept mastery and calibrating
assessment item difficulties.
"""

import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BKTParameters:
    """
    Canonical Bayesian Knowledge Tracing (BKT) Parameters.

    Attributes:
        p_l0 (float): Prior probability of mastery before any observation. Default: 0.10.
        p_t (float): Probability of learning transition between opportunities. Default: 0.15.
        p_g (float): Probability of a lucky guess when skill is unmastered. Default: 0.20.
        p_s (float): Probability of an accidental slip when skill is mastered. Default: 0.05.
    """
    p_l0: float = 0.10
    p_t: float = 0.15
    p_g: float = 0.20
    p_s: float = 0.05

    def __post_init__(self) -> None:
        """Validate parameter boundaries and mathematical constraints."""
        for name, val in [("p_l0", self.p_l0), ("p_t", self.p_t), ("p_g", self.p_g), ("p_s", self.p_s)]:
            if not isinstance(val, (int, float)):
                raise TypeError(f"BKT parameter '{name}' must be numeric, got {type(val).__name__}.")
            if math.isnan(val) or math.isinf(val):
                raise ValueError(f"BKT parameter '{name}' cannot be NaN or Infinite.")
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"BKT parameter '{name}' must be within [0.0, 1.0], got {val}.")

        # Invariant: Guess and Slip sum must be strictly less than 1.0 to preserve monotonicity
        if self.p_g + self.p_s >= 1.0:
            raise ValueError(
                f"Degenerate parameter constraint: p_g ({self.p_g}) + p_s ({self.p_s}) "
                f"must be strictly < 1.0 to ensure correct response increases mastery."
            )


class BayesianKnowledgeTracer:
    """
    Deterministic Bayesian Knowledge Tracing (Corbett & Anderson standard BKT).

    Separates observation updating from the learning transition:
      1. Posterior given Correct:
         p_c = (p * (1 - S)) / (p * (1 - S) + (1 - p) * G)
      2. Posterior given Incorrect:
         p_i = (p * S) / (p * S + (1 - p) * (1 - G))
      3. Learning Transition:
         p_next = p_posterior + (1 - p_posterior) * T
    """

    EPSILON = 1e-12

    def __init__(self, params: BKTParameters | None = None) -> None:
        self.params = params if params is not None else BKTParameters()

    def validate_probability(self, p: float, name: str = "probability") -> float:
        """Ensure probability is numeric, finite, and strictly bounded within [0.0, 1.0]."""
        if not isinstance(p, (int, float)):
            raise TypeError(f"{name} must be numeric, got {type(p).__name__}.")
        if math.isnan(p) or math.isinf(p):
            raise ValueError(f"{name} cannot be NaN or Infinite.")
        if p < 0.0 or p > 1.0:
            raise ValueError(f"{name} must be in range [0.0, 1.0], got {p}.")
        return float(p)

    def calculate_observation_posterior(self, prior_mastery: float, is_correct: bool) -> float:
        """
        Calculates the posterior belief of mastery P(L_t | Observation).

        Args:
            prior_mastery: Prior belief P(L_{t-1}) in range [0.0, 1.0].
            is_correct: Whether the student's response was correct.

        Returns:
            Updated posterior probability of mastery before transition.
        """
        p = self.validate_probability(prior_mastery, "prior_mastery")
        s = self.params.p_s
        g = self.params.p_g

        if is_correct:
            numerator = p * (1.0 - s)
            denominator = numerator + (1.0 - p) * g
        else:
            numerator = p * s
            denominator = numerator + (1.0 - p) * (1.0 - g)

        # Numerical safety guard against zero denominator
        if denominator <= self.EPSILON:
            return 0.0 if not is_correct else 1.0

        posterior = numerator / denominator
        # Clip to [0.0, 1.0] for floating point rounding safety
        return max(0.0, min(1.0, posterior))

    def apply_learning_transition(self, posterior_mastery: float) -> float:
        """
        Applies the opportunity transition probability P(T).

        Args:
            posterior_mastery: The observation posterior probability.

        Returns:
            The transitioned prior mastery for the next learning opportunity P(L_{t+1}).
        """
        p_post = self.validate_probability(posterior_mastery, "posterior_mastery")
        t = self.params.p_t

        p_next = p_post + (1.0 - p_post) * t
        return max(0.0, min(1.0, p_next))

    def step(self, prior_mastery: float, is_correct: bool) -> tuple[float, float]:
        """
        Executes a complete BKT step: observation update followed by learning transition.

        Args:
            prior_mastery: Prior mastery belief.
            is_correct: Response correctness.

        Returns:
            Tuple of (posterior_mastery, next_opportunity_mastery).
        """
        posterior = self.calculate_observation_posterior(prior_mastery, is_correct)
        next_mastery = self.apply_learning_transition(posterior)
        return posterior, next_mastery

    def predict_performance(self, mastery: float) -> float:
        """
        Calculates the expected probability that a student will answer the next item correctly:
        P(Correct | L) = L * (1 - S) + (1 - L) * G

        Args:
            mastery: Current mastery probability.

        Returns:
            Predicted probability of correct response.
        """
        p = self.validate_probability(mastery, "mastery")
        s = self.params.p_s
        g = self.params.p_g
        prob_correct = p * (1.0 - s) + (1.0 - p) * g
        return max(0.0, min(1.0, prob_correct))

    def update_sequence(
        self,
        observations: list[bool],
        initial_mastery: float | None = None
    ) -> list[dict[str, float]]:
        """
        Evaluates a chronological sequence of student attempts.

        Args:
            observations: List of correctness booleans.
            initial_mastery: Optional custom initial mastery. Defaults to params.p_l0.

        Returns:
            List of diagnostic dictionaries recording prior, posterior, next mastery,
            and predicted performance for each step.
        """
        current_prior = (
            self.validate_probability(initial_mastery, "initial_mastery")
            if initial_mastery is not None
            else self.params.p_l0
        )
        trajectory: list[dict[str, float]] = []

        for i, is_correct in enumerate(observations):
            predicted_acc = self.predict_performance(current_prior)
            posterior, next_mastery = self.step(current_prior, is_correct)
            trajectory.append({
                "step": float(i + 1),
                "is_correct": 1.0 if is_correct else 0.0,
                "prior_mastery": current_prior,
                "predicted_accuracy": predicted_acc,
                "posterior_mastery": posterior,
                "next_mastery": next_mastery,
            })
            current_prior = next_mastery

        return trajectory


class ItemResponseTheory2PL:
    """
    Two-Parameter Logistic (2PL) Item Response Theory Model.

    Formula:
      P(Correct | theta) = 1 / (1 + exp(-a * (theta - b)))

    Where:
      theta: Learner latent ability (typically in [-3.0, +3.0]).
      b: Item difficulty parameter (typically in [-3.0, +3.0]).
      a: Item discrimination parameter (typically in [0.5, 2.5]).
    """

    EXP_BOUND = 35.0

    @classmethod
    def predict_probability(
        cls,
        theta: float,
        difficulty_b: float,
        discrimination_a: float = 1.0
    ) -> float:
        """
        Calculates probability of correct response under the 2PL model with
        numerical stability guards against overflow.
        """
        if discrimination_a <= 0.0:
            raise ValueError(f"Discrimination parameter 'a' must be > 0.0, got {discrimination_a}.")

        # Logit calculation: z = a * (theta - b)
        z = discrimination_a * (theta - difficulty_b)

        # Numerical overflow/underflow protection
        if z > cls.EXP_BOUND:
            return 1.0
        if z < -cls.EXP_BOUND:
            return 0.0

        return 1.0 / (1.0 + math.exp(-z))

    @classmethod
    def estimate_ability_step(
        cls,
        current_theta: float,
        is_correct: bool,
        difficulty_b: float,
        discrimination_a: float = 1.0,
        learning_rate: float = 0.4
    ) -> float:
        """
        Stochastic gradient step adjusting learner latent ability estimate (theta)
        based on the observed response vs. expected 2PL probability.
        """
        expected_p = cls.predict_probability(current_theta, difficulty_b, discrimination_a)
        actual = 1.0 if is_correct else 0.0
        residual = actual - expected_p

        # Gradient update for logistic loss
        updated_theta = current_theta + learning_rate * discrimination_a * residual
        # Bound theta to standard psychometric range [-4.0, +4.0]
        return max(-4.0, min(4.0, updated_theta))

    @classmethod
    def select_optimal_difficulty(
        cls,
        theta: float,
        target_success_prob: float = 0.65,
        discrimination_a: float = 1.0,
        min_b: float = -3.0,
        max_b: float = 3.0
    ) -> float:
        """
        Calculates calibrated item difficulty b that targets a specific expected probability
        of success for a student with latent ability theta.

        Formula:
          b = theta - (1 / a) * ln(P / (1 - P))

        For max Fisher information, set target_success_prob = 0.50 (b = theta).
        For pedagogically optimal challenge (Zone of Proximal Development), target ~0.65.
        """
        p = max(0.01, min(0.99, target_success_prob))
        a = max(0.1, discrimination_a)
        offset = (1.0 / a) * math.log(p / (1.0 - p))
        target_b = theta - offset
        return max(min_b, min(max_b, round(target_b, 3)))


class PrerequisiteSkillGraph:
    """
    Academic skill and prerequisite knowledge graph for identifying conceptual gaps.
    Enables backward gap diagnosis and targeted remedial suggestions.
    """

    DEFAULT_GRAPH: dict[str, list[str]] = {
        "derivatives": ["limits", "functions"],
        "integrals": ["derivatives", "algebra"],
        "definite integrals": ["integrals", "fundamental theorem of calculus"],
        "differential equations": ["integrals", "derivatives", "linear algebra"],
        "linear algebra": ["algebra", "vectors"],
        "eigenvalues": ["linear algebra", "determinants", "matrix multiplication"],
        "neural networks": ["linear algebra", "derivatives", "gradient descent"],
        "deep learning": ["neural networks", "optimization"],
        "graph algorithms": ["data structures", "recursion", "asymptotic notation"],
        "dynamic programming": ["recursion", "asymptotic notation"],
        "bayes theorem": ["conditional probability", "probability distributions"],
        "machine learning": ["linear algebra", "calculus", "probability & statistics"],
        "operating systems": ["computer architecture", "data structures", "concurrency"],
    }

    def __init__(self, custom_graph: dict[str, list[str]] | None = None) -> None:
        self.graph = {k.lower(): [p.lower() for p in v] for k, v in (custom_graph or self.DEFAULT_GRAPH).items()}

    def get_prerequisites(self, topic: str) -> list[str]:
        """Returns immediate prerequisites for a topic."""
        return self.graph.get(topic.strip().lower(), [])

    def detect_prerequisite_gaps(
        self,
        topic: str,
        student_masteries: dict[str, float],
        gap_threshold: float = 0.45
    ) -> list[dict[str, Any]]:
        """
        Identifies prerequisite topics where student's current mastery is below gap_threshold.
        """
        prereqs = self.get_prerequisites(topic)
        gaps: list[dict[str, Any]] = []
        for p in prereqs:
            current_m = student_masteries.get(p.lower(), 0.10)
            if current_m < gap_threshold:
                gaps.append({
                    "prerequisite_topic": p,
                    "current_mastery": current_m,
                    "gap_severity": "Critical" if current_m < 0.25 else "Moderate",
                    "recommendation": f"Review foundational concept '{p}' before proceeding."
                })
        return gaps

    def get_remedial_study_plan(
        self,
        topic: str,
        student_masteries: dict[str, float]
    ) -> dict[str, Any]:
        """Produces a structured remedial study roadmap addressing identified knowledge gaps."""
        gaps = self.detect_prerequisite_gaps(topic, student_masteries)
        has_critical = any(g["gap_severity"] == "Critical" for g in gaps)

        return {
            "target_topic": topic,
            "has_blocking_gaps": has_critical,
            "gaps": gaps,
            "recommended_next_topic": gaps[0]["prerequisite_topic"] if gaps else topic,
            "readiness_summary": (
                "Prerequisite gaps detected. Recommended to review prerequisites first."
                if gaps else "Prerequisites satisfied. Ready for advanced practice."
            )
        }


class BrierScoreEvaluator:
    """
    Calibration and forecast accuracy verification for Bayesian Knowledge Tracing.
    Computes Brier Score: (1/N) * sum((p_pred - y_true)^2)
    Brier Score ranges from 0.0 (perfect calibration) to 1.0 (worst).
    A score <= 0.25 beats random baseline (0.5 prediction).
    """

    @staticmethod
    def compute_brier_score(predictions: list[float], actuals: list[bool | int]) -> float:
        """Computes mean squared calibration error between predicted probability and observed outcome."""
        if not predictions or not actuals:
            raise ValueError("Predictions and actuals lists must not be empty.")
        if len(predictions) != len(actuals):
            raise ValueError("Predictions and actuals must have the same length.")

        squared_errors = []
        for p, y in zip(predictions, actuals, strict=True):
            act_num = 1.0 if y else 0.0
            p_val = max(0.0, min(1.0, float(p)))
            squared_errors.append((p_val - act_num) ** 2)

        return sum(squared_errors) / len(squared_errors)

    @staticmethod
    def compute_calibration_bins(
        predictions: list[float],
        actuals: list[bool | int],
        num_bins: int = 5
    ) -> list[dict[str, Any]]:
        """Splits predictions into probability intervals and computes observed accuracy per bin."""
        if len(predictions) != len(actuals):
            raise ValueError("Predictions and actuals must have the same length.")

        bins: list[dict[str, Any]] = []
        bin_width = 1.0 / num_bins

        for b in range(num_bins):
            low = b * bin_width
            high = (b + 1) * bin_width
            bin_preds = []
            bin_acts = []
            for p, y in zip(predictions, actuals, strict=True):
                if low <= p < high or (b == num_bins - 1 and p == 1.0):
                    bin_preds.append(p)
                    bin_acts.append(1.0 if y else 0.0)

            count = len(bin_preds)
            mean_pred = sum(bin_preds) / count if count > 0 else (low + high) / 2.0
            obs_acc = sum(bin_acts) / count if count > 0 else 0.0
            bins.append({
                "bin_range": f"{low:.1f}-{high:.1f}",
                "count": count,
                "mean_predicted": round(mean_pred, 3),
                "observed_accuracy": round(obs_acc, 3),
                "calibration_gap": round(abs(mean_pred - obs_acc), 3) if count > 0 else 0.0
            })

        return bins

