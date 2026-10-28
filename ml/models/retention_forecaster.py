"""
LuminaLearn AI — Ebbinghaus Retention Forecaster.
Module: ml/models/retention_forecaster.py

Models how a mastered concept fades without review and how spaced retrieval practice
flattens the forgetting curve:

  Retention:    R(t) = exp(-t / S)
  Stability:    S0 = base_stability + mastery_gain * P(L)        (days)
  Review rule:  review when R falls to the target retention,  t* = -S * ln(target)
  After review: S <- S * review_multiplier  (expanding intervals)

The frontend mirrors these formulas in `frontend/src/utils/retention.ts` for live
what-if interaction; this module is the tested source of truth.
"""

import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RetentionForecaster:
    """Deterministic forgetting-curve model parameterized by BKT mastery."""

    base_stability_days: float = 1.5
    mastery_gain_days: float = 6.0
    review_multiplier: float = 2.2

    def __post_init__(self) -> None:
        if self.base_stability_days <= 0.0:
            raise ValueError("base_stability_days must be > 0.")
        if self.mastery_gain_days < 0.0:
            raise ValueError("mastery_gain_days must be >= 0.")
        if self.review_multiplier < 1.0:
            raise ValueError("review_multiplier must be >= 1.0 so reviews never weaken memory.")

    @staticmethod
    def _clamp_probability(value: float) -> float:
        if math.isnan(value) or math.isinf(value):
            raise ValueError("Probability cannot be NaN or Infinite.")
        return max(0.0, min(1.0, float(value)))

    def initial_stability(self, mastery: float) -> float:
        """Memory stability S0 (days) for a learner at BKT mastery P(L)."""
        return self.base_stability_days + self.mastery_gain_days * self._clamp_probability(mastery)

    @staticmethod
    def retention(days: float, stability: float) -> float:
        """Ebbinghaus retention R(t) = exp(-t / S)."""
        if stability <= 0.0:
            raise ValueError("stability must be > 0.")
        return math.exp(-max(0.0, days) / stability)

    def half_life_days(self, mastery: float) -> float:
        """Days until retention halves without review: S0 * ln 2."""
        return self.initial_stability(mastery) * math.log(2.0)

    def review_schedule(
        self,
        mastery: float,
        target_retention: float = 0.80,
        horizon_days: float = 30.0,
    ) -> list[float]:
        """Days on which a spaced retrieval review keeps retention above the target."""
        target = min(0.99, max(0.05, target_retention))
        stability = self.initial_stability(mastery)
        reviews: list[float] = []
        elapsed = 0.0
        while True:
            elapsed += -stability * math.log(target)
            if elapsed > horizon_days:
                return reviews
            reviews.append(round(elapsed, 2))
            stability *= self.review_multiplier

    def forecast(
        self,
        mastery: float,
        horizon_days: float = 30.0,
        points: int = 61,
        target_retention: float = 0.80,
    ) -> dict[str, Any]:
        """
        Samples both curves on an even grid over [0, horizon_days]:
          * `no_review`: a single study session left to decay.
          * `spaced`: retention reset at each scheduled review, with growing stability.
        """
        if points < 2:
            raise ValueError("points must be >= 2.")
        stability0 = self.initial_stability(mastery)
        reviews = self.review_schedule(mastery, target_retention, horizon_days)
        days = [round(horizon_days * i / (points - 1), 3) for i in range(points)]

        no_review = [round(self.retention(d, stability0), 4) for d in days]
        spaced: list[float] = []
        for d in days:
            stability = stability0
            last_review = 0.0
            for review_day in reviews:
                if review_day > d:
                    break
                stability *= self.review_multiplier
                last_review = review_day
            spaced.append(round(self.retention(d - last_review, stability), 4))

        return {
            "days": days,
            "no_review": no_review,
            "spaced": spaced,
            "review_days": reviews,
            "target_retention": target_retention,
            "half_life_days": round(self.half_life_days(mastery), 2),
            "initial_stability_days": round(stability0, 2),
        }
