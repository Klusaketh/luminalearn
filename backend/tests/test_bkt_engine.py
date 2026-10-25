import math
import os
import sys

import pytest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ml.models.knowledge_tracer import (
    BayesianKnowledgeTracer,
    BKTParameters,
    ItemResponseTheory2PL,
)


def test_bkt_canonical_defaults():
    """Verify that default BKT parameters strictly match the Project Aurora specification."""
    params = BKTParameters()
    assert params.p_l0 == 0.10
    assert params.p_t == 0.15
    assert params.p_g == 0.20
    assert params.p_s == 0.05


def test_bkt_parameter_validation_bounds():
    """Verify validation enforces probabilities in [0.0, 1.0] and rejects non-finite values."""
    with pytest.raises(ValueError, match="must be within"):
        BKTParameters(p_l0=-0.1)

    with pytest.raises(ValueError, match="must be within"):
        BKTParameters(p_t=1.2)

    with pytest.raises(ValueError, match="cannot be NaN or Infinite"):
        BKTParameters(p_g=float("nan"))

    with pytest.raises(ValueError, match="cannot be NaN or Infinite"):
        BKTParameters(p_s=float("inf"))

    with pytest.raises(ValueError, match="Degenerate parameter constraint"):
        # p_g + p_s >= 1.0 violates monotonicity
        BKTParameters(p_g=0.6, p_s=0.5)


def test_bkt_correct_observation_update_math():
    """
    Verify exact analytical calculation for correct observation.
    p=0.10, S=0.05, G=0.20, T=0.15
    Numerator: 0.10 * 0.95 = 0.095
    Denominator: 0.095 + (0.90 * 0.20) = 0.095 + 0.180 = 0.275
    Posterior = 0.095 / 0.275 = 19 / 55 ~ 0.3454545...
    Transition = 19/55 + (1 - 19/55) * 0.15 = 19/55 + (36/55) * 0.15 = (19 + 5.4)/55 = 24.4 / 55 ~ 0.4436363...
    """
    tracer = BayesianKnowledgeTracer()
    prior = 0.10

    posterior = tracer.calculate_observation_posterior(prior, is_correct=True)
    expected_posterior = 0.095 / 0.275
    assert math.isclose(posterior, expected_posterior, rel_tol=1e-9)

    next_mastery = tracer.apply_learning_transition(posterior)
    expected_next = expected_posterior + (1.0 - expected_posterior) * 0.15
    assert math.isclose(next_mastery, expected_next, rel_tol=1e-9)

    # Combined step matches sequential updates
    step_post, step_next = tracer.step(prior, is_correct=True)
    assert math.isclose(step_post, posterior, rel_tol=1e-9)
    assert math.isclose(step_next, next_mastery, rel_tol=1e-9)


def test_bkt_incorrect_observation_update_math():
    """
    Verify exact analytical calculation for incorrect observation.
    p=0.10, S=0.05, G=0.20, T=0.15
    Numerator: 0.10 * 0.05 = 0.005
    Denominator: 0.005 + (0.90 * 0.80) = 0.005 + 0.720 = 0.725
    Posterior = 0.005 / 0.725 = 1 / 145 ~ 0.00689655...
    Transition = 1/145 + (144/145) * 0.15 = (1 + 21.6) / 145 = 22.6 / 145 ~ 0.155862...
    """
    tracer = BayesianKnowledgeTracer()
    prior = 0.10

    posterior = tracer.calculate_observation_posterior(prior, is_correct=False)
    expected_posterior = 0.005 / 0.725
    assert math.isclose(posterior, expected_posterior, rel_tol=1e-9)

    next_mastery = tracer.apply_learning_transition(posterior)
    expected_next = expected_posterior + (1.0 - expected_posterior) * 0.15
    assert math.isclose(next_mastery, expected_next, rel_tol=1e-9)


def test_bkt_boundary_conditions():
    """Verify BKT behavior at prior = 0.0 and prior = 1.0."""
    tracer = BayesianKnowledgeTracer()

    # Boundary: Absolute zero knowledge
    post_zero_c = tracer.calculate_observation_posterior(0.0, is_correct=True)
    assert post_zero_c == 0.0  # Lucky guess means belief remains 0 before transition
    next_zero_c = tracer.apply_learning_transition(post_zero_c)
    assert math.isclose(next_zero_c, 0.15, rel_tol=1e-9)  # Transition T kicks in

    post_zero_i = tracer.calculate_observation_posterior(0.0, is_correct=False)
    assert post_zero_i == 0.0
    next_zero_i = tracer.apply_learning_transition(post_zero_i)
    assert math.isclose(next_zero_i, 0.15, rel_tol=1e-9)

    # Boundary: Absolute mastery
    post_one_c = tracer.calculate_observation_posterior(1.0, is_correct=True)
    assert post_one_c == 1.0
    assert tracer.apply_learning_transition(post_one_c) == 1.0

    # Even with an accidental slip, prior 1.0 can only drop to slip posterior
    post_one_i = tracer.calculate_observation_posterior(1.0, is_correct=False)
    # Numerator: 1.0 * S = 0.05; Denominator: 0.05 + 0 = 0.05 -> 1.0
    assert post_one_i == 1.0


def test_bkt_monotonicity_repeated_success():
    """Verify that consecutive correct answers monotonically increase mastery toward 1.0."""
    tracer = BayesianKnowledgeTracer()
    current_p = 0.10

    for _ in range(8):
        _, next_p = tracer.step(current_p, is_correct=True)
        assert next_p > current_p
        current_p = next_p

    assert current_p > 0.95
    assert current_p <= 1.0


def test_bkt_predict_performance():
    """Verify performance prediction formula: P(Correct | L) = L*(1-S) + (1-L)*G."""
    tracer = BayesianKnowledgeTracer()

    # When L = 0: P(Correct) = G = 0.20
    assert math.isclose(tracer.predict_performance(0.0), 0.20, rel_tol=1e-9)

    # When L = 1: P(Correct) = 1 - S = 0.95
    assert math.isclose(tracer.predict_performance(1.0), 0.95, rel_tol=1e-9)

    # When L = 0.5: 0.5*0.95 + 0.5*0.20 = 0.475 + 0.10 = 0.575
    assert math.isclose(tracer.predict_performance(0.5), 0.575, rel_tol=1e-9)


def test_bkt_sequence_tracer():
    """Verify sequence trajectory produces deterministic step diagnostics."""
    tracer = BayesianKnowledgeTracer()
    observations = [True, False, True, True]
    trajectory = tracer.update_sequence(observations, initial_mastery=0.10)

    assert len(trajectory) == 4
    assert trajectory[0]["step"] == 1.0
    assert trajectory[0]["is_correct"] == 1.0
    assert math.isclose(trajectory[0]["prior_mastery"], 0.10, rel_tol=1e-9)

    # Ensure continuity: step t+1 prior == step t next_mastery
    for i in range(len(trajectory) - 1):
        assert math.isclose(
            trajectory[i]["next_mastery"],
            trajectory[i + 1]["prior_mastery"],
            rel_tol=1e-9
        )


def test_irt_2pl_probability_at_difficulty_equality():
    """When ability theta equals item difficulty b, P(correct) must equal exactly 0.5."""
    p = ItemResponseTheory2PL.predict_probability(theta=1.5, difficulty_b=1.5, discrimination_a=1.2)
    assert math.isclose(p, 0.5, rel_tol=1e-9)


def test_irt_2pl_monotonicity():
    """Higher ability theta must strictly produce higher probability of success."""
    p_low = ItemResponseTheory2PL.predict_probability(theta=-1.0, difficulty_b=0.0, discrimination_a=1.0)
    p_mid = ItemResponseTheory2PL.predict_probability(theta=0.0, difficulty_b=0.0, discrimination_a=1.0)
    p_high = ItemResponseTheory2PL.predict_probability(theta=1.0, difficulty_b=0.0, discrimination_a=1.0)

    assert p_low < p_mid < p_high


def test_irt_2pl_numerical_stability_extremes():
    """Ensure extreme ability values do not cause overflow exceptions."""
    p_inf_high = ItemResponseTheory2PL.predict_probability(theta=100.0, difficulty_b=0.0)
    p_inf_low = ItemResponseTheory2PL.predict_probability(theta=-100.0, difficulty_b=0.0)

    assert p_inf_high == 1.0
    assert p_inf_low == 0.0


def test_irt_2pl_ability_update_step():
    """Verify stochastic ability updating moves in the correct direction."""
    theta_initial = 0.0

    # Correct response on difficult question (b=1.0) should increase ability
    theta_updated = ItemResponseTheory2PL.estimate_ability_step(
        current_theta=theta_initial,
        is_correct=True,
        difficulty_b=1.0,
        discrimination_a=1.0
    )
    assert theta_updated > theta_initial

    # Incorrect response on easy question (b=-1.0) should decrease ability
    theta_down = ItemResponseTheory2PL.estimate_ability_step(
        current_theta=theta_initial,
        is_correct=False,
        difficulty_b=-1.0,
        discrimination_a=1.0
    )
    assert theta_down < theta_initial


def test_irt_select_optimal_difficulty():
    """Verify adaptive item selector generates difficulty matching target challenge probability."""
    # When ability is 1.0 and target prob is 0.50 (max Fisher info), b should equal theta
    b_half = ItemResponseTheory2PL.select_optimal_difficulty(theta=1.0, target_success_prob=0.50, discrimination_a=1.0)
    assert math.isclose(b_half, 1.0, abs_tol=1e-3)

    # When target prob is 0.65 (Zone of Proximal Development), b should be slightly easier than theta
    b_zpd = ItemResponseTheory2PL.select_optimal_difficulty(theta=1.0, target_success_prob=0.65, discrimination_a=1.0)
    assert b_zpd < 1.0
    # Expected prob at this b should match 0.65
    p_actual = ItemResponseTheory2PL.predict_probability(theta=1.0, difficulty_b=b_zpd, discrimination_a=1.0)
    assert math.isclose(p_actual, 0.65, abs_tol=1e-2)


def test_prerequisite_skill_graph_gap_detection():
    """Verify prerequisite graph detects gaps and builds remedial recommendations."""
    from ml.models.knowledge_tracer import PrerequisiteSkillGraph

    graph = PrerequisiteSkillGraph()
    # Topic 'derivatives' requires 'limits' and 'functions'
    prereqs = graph.get_prerequisites("derivatives")
    assert "limits" in prereqs
    assert "functions" in prereqs

    # Student has low mastery in 'limits'
    student_scores = {"limits": 0.20, "functions": 0.80}
    gaps = graph.detect_prerequisite_gaps("derivatives", student_scores)
    assert len(gaps) == 1
    assert gaps[0]["prerequisite_topic"] == "limits"
    assert gaps[0]["gap_severity"] == "Critical"

    # Remedial plan recommends limits
    plan = graph.get_remedial_study_plan("derivatives", student_scores)
    assert plan["has_blocking_gaps"] is True
    assert plan["recommended_next_topic"] == "limits"


def test_brier_score_evaluator_calibration():
    """Verify Brier Score calculations against expected analytical values."""
    from ml.models.knowledge_tracer import BrierScoreEvaluator

    # Perfect forecast
    assert BrierScoreEvaluator.compute_brier_score([1.0, 0.0], [1, 0]) == 0.0
    # Worst possible forecast
    assert BrierScoreEvaluator.compute_brier_score([1.0, 0.0], [0, 1]) == 1.0
    # Consistent 0.5 coin-flip guess on 2 items (one correct, one incorrect)
    # (0.5 - 1)^2 = 0.25, (0.5 - 0)^2 = 0.25 -> mean = 0.25
    assert BrierScoreEvaluator.compute_brier_score([0.5, 0.5], [1, 0]) == 0.25

    # Calibration bins
    bins = BrierScoreEvaluator.compute_calibration_bins(
        predictions=[0.1, 0.2, 0.8, 0.9],
        actuals=[0, 0, 1, 1],
        num_bins=2
    )
    assert len(bins) == 2
    assert bins[0]["observed_accuracy"] == 0.0
    assert bins[1]["observed_accuracy"] == 1.0

