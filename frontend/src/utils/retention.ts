/**
 * Ebbinghaus retention forecast with spaced retrieval practice.
 * Mirrors ml/models/retention_forecaster.py (the tested source of truth) so the quiz can
 * recompute the review schedule instantly while the learner drags the target slider.
 *
 *   R(t) = exp(-t / S),   S0 = 1.5 + 6.0 * P(L) days,   S <- S * 2.2 after each review.
 */
const BASE_STABILITY_DAYS = 1.5;
const MASTERY_GAIN_DAYS = 6.0;
const REVIEW_MULTIPLIER = 2.2;

const clamp01 = (value: number) => Math.max(0, Math.min(1, value));

export function initialStability(mastery: number): number {
  return BASE_STABILITY_DAYS + MASTERY_GAIN_DAYS * clamp01(mastery);
}

export function retention(days: number, stability: number): number {
  return Math.exp(-Math.max(0, days) / stability);
}

export function halfLifeDays(mastery: number): number {
  return initialStability(mastery) * Math.LN2;
}

export function reviewSchedule(mastery: number, target = 0.8, horizonDays = 30): number[] {
  const goal = Math.min(0.99, Math.max(0.05, target));
  let stability = initialStability(mastery);
  const reviews: number[] = [];
  let elapsed = 0;
  for (;;) {
    elapsed += -stability * Math.log(goal);
    if (elapsed > horizonDays) return reviews;
    reviews.push(Math.round(elapsed * 100) / 100);
    stability *= REVIEW_MULTIPLIER;
  }
}

export interface RetentionForecastData {
  days: number[];
  noReview: number[];
  spaced: number[];
  reviewDays: number[];
  halfLife: number;
}

export function forecastRetention(mastery: number, target = 0.8, horizonDays = 30, points = 121): RetentionForecastData {
  const s0 = initialStability(mastery);
  const reviewDays = reviewSchedule(mastery, target, horizonDays);
  const days = Array.from({ length: points }, (_, i) => (horizonDays * i) / (points - 1));
  const noReview = days.map((d) => retention(d, s0));
  const spaced = days.map((d) => {
    let stability = s0;
    let lastReview = 0;
    for (const review of reviewDays) {
      if (review > d) break;
      stability *= REVIEW_MULTIPLIER;
      lastReview = review;
    }
    return retention(d - lastReview, stability);
  });
  return { days, noReview, spaced, reviewDays, halfLife: halfLifeDays(mastery) };
}
