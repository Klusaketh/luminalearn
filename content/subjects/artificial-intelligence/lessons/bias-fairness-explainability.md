---
lesson: bias-fairness-explainability
title: Bias, Fairness & Explainability in AI
summary: How bias enters AI systems, group fairness metrics (demographic parity, equal opportunity, equalised odds, predictive parity) and the trade-offs between them, mitigation techniques, explainability methods from interpretable models to SHAP and counterfactuals, and governance and regulation.
minutes: 35
type: theory
objectives:
  - Identify sources of bias across the machine-learning life cycle and explain why removing protected attributes is not enough
  - Compute and compare fairness metrics such as selection rate, disparate impact, true positive rate, and precision across groups
  - Explain global and local explanation methods, including feature attributions and counterfactuals, and the role of documentation and regulation
review: ai-draft
---
## Introduction

AI systems increasingly help decide who gets a loan, which job applicants are interviewed, how patients are prioritised, and what content people see. When they learn from historical data, they can reproduce and even amplify past discrimination, and when they are opaque, the people affected cannot understand or challenge decisions. Responsible AI requires measuring fairness, mitigating bias, explaining decisions, and governing systems throughout their life cycle. These are technical skills as much as ethical ones.

**Before you start:** you should know classification and confusion matrices; *Classification Metrics & ROC Curves* covers them in depth.

## Core theory

### Where bias comes from

- **Historical bias:** the data faithfully records an unfair world, such as past hiring decisions that favoured one group.
- **Representation bias:** some groups are under-represented in the training data, so the model performs worse for them. The 2018 Gender Shades study found commercial gender classifiers had error rates up to about 35% for darker-skinned women but under 1% for lighter-skinned men.
- **Measurement bias:** the label or a feature is a poor proxy. A widely used US health algorithm predicted health-care costs as a proxy for health needs; because less money had historically been spent on Black patients, it underestimated their needs.
- **Aggregation and evaluation bias:** one model for groups with different patterns, or benchmarks that do not represent the people affected.
- **Deployment bias and feedback loops:** a system used differently from its design, or predictions that shape future data (more patrols in an area produce more recorded incidents there).

Simply deleting protected attributes such as gender or caste ("fairness through unawareness") rarely works, because other features, such as postcode, school, or name, act as **proxies**.

### Group fairness metrics

For a binary classifier and groups $A$ and $B$:

- **Demographic parity:** equal selection rates $P(\hat{Y} = 1)$. The **disparate impact ratio** divides the lower selection rate by the higher; the US **four-fifths rule** flags ratios below 0.8.
- **Equal opportunity:** equal true positive rates $P(\hat{Y} = 1 \mid Y = 1)$: qualified people have the same chance of being selected.
- **Equalised odds:** equal true positive rates **and** equal false positive rates.
- **Predictive parity:** equal precision $P(Y = 1 \mid \hat{Y} = 1)$; a related property is **calibration** within each group.

These criteria conflict. When groups have different base rates, no imperfect classifier can be calibrated (or have equal precision) and also have equal false positive and false negative rates across groups. This impossibility result, shown in 2016–2017 during the debate about the COMPAS recidivism tool, means fairness requires choosing which criterion matters for the decision at hand.

### Mitigation

- **Pre-processing:** collect better data, rebalance or reweigh samples, fix labels.
- **In-processing:** add fairness constraints or penalties to the training objective.
- **Post-processing:** adjust decision thresholds per group, for example to equalise true positive rates. Whether group-specific thresholds are lawful depends on the jurisdiction and domain.

Every intervention should be evaluated on accuracy and on the fairness metrics, and with the affected communities in mind.

### Explainability

- **Interpretable models** such as linear models and small decision trees are understandable by design.
- **Global explanations** describe overall behaviour: feature importance (such as permutation importance) and partial dependence plots.
- **Local explanations** describe one decision: **LIME** fits a simple surrogate model around the input; **SHAP** assigns each feature a contribution based on Shapley values from cooperative game theory, and the contributions sum to the difference between the prediction and the average prediction; **counterfactual explanations** state the smallest change that would alter the decision.
- For images, **saliency maps** highlight influential pixels.

Post-hoc explanations are approximations and can be unfaithful to the model, so they should be validated.

### Governance

Good practice includes **datasheets for datasets** and **model cards** documenting intended use, performance across groups, and limitations; human oversight and appeal routes; and audits after deployment. Regulation is growing: the GDPR restricts solely automated decisions with significant effects, the **EU AI Act** (in force since August 2024) imposes risk-based obligations, and India's **Digital Personal Data Protection Act, 2023** governs personal data processing.

## Worked examples

### Example 1: Auditing a classifier and adjusting thresholds

Each group has ten applicants with model scores and true outcomes (1 = would repay). The program computes selection rate, true positive rate, false positive rate, and precision per group, then lowers group B's threshold until its true positive rate matches group A's.

```python
groups = {
    "A": ([0.90, 0.80, 0.75, 0.70, 0.60, 0.55, 0.40, 0.35, 0.20, 0.10], [1, 1, 1, 0, 1, 0, 1, 0, 0, 0]),
    "B": ([0.85, 0.65, 0.45, 0.42, 0.40, 0.38, 0.30, 0.25, 0.15, 0.05], [1, 1, 1, 1, 0, 1, 0, 0, 0, 0]),
}


def rates(scores, labels, threshold):
    pred = [s >= threshold for s in scores]
    tp = sum(p and y for p, y in zip(pred, labels))
    fp = sum(p and not y for p, y in zip(pred, labels))
    positives, negatives = sum(labels), len(labels) - sum(labels)
    return {"selection": sum(pred) / len(pred), "TPR": tp / positives, "FPR": fp / negatives,
            "precision": tp / sum(pred) if sum(pred) else 0.0}


print("one threshold (0.5) for everyone:")
results = {g: rates(s, y, 0.5) for g, (s, y) in groups.items()}
for g, r in results.items():
    print(f"  group {g}: " + ", ".join(f"{k} {v:.2f}" for k, v in r.items()))
ratio = results["B"]["selection"] / results["A"]["selection"]
print(f"  disparate impact ratio = {ratio:.2f} (four-fifths rule needs >= 0.80)")

# Post-processing: pick group B's threshold so its true positive rate matches group A's
target = results["A"]["TPR"]
scores_b, labels_b = groups["B"]
threshold_b = max(t for t in scores_b if rates(scores_b, labels_b, t)["TPR"] >= target)
r = rates(scores_b, labels_b, threshold_b)
print(f"equal opportunity: group B threshold {threshold_b} -> " + ", ".join(f"{k} {v:.2f}" for k, v in r.items()))
```

Output:

```text
one threshold (0.5) for everyone:
  group A: selection 0.60, TPR 0.80, FPR 0.40, precision 0.67
  group B: selection 0.20, TPR 0.40, FPR 0.00, precision 1.00
  disparate impact ratio = 0.33 (four-fifths rule needs >= 0.80)
equal opportunity: group B threshold 0.42 -> selection 0.40, TPR 0.80, FPR 0.00, precision 1.00
```

With one threshold, group B is selected at a third of group A's rate (ratio 0.33, failing the four-fifths rule), and qualified people in group B are selected only 40% of the time against 80% in group A: the model's scores are systematically lower for group B. Lowering group B's threshold to 0.42 achieves **equal opportunity** (both TPRs 0.80) without adding false positives. But other criteria still differ: false positive rates are 0.40 against 0.00, so equalised odds fails, and the selection-rate ratio is now 0.67. Fixing one fairness metric does not fix them all.

### Example 2: A local explanation and a counterfactual

A linear credit model scores applicants as $0.4 \times \text{income band} + 0.3 \times \text{history score}$ and approves scores of at least 4.0. The average applicant has income band 5 and history 4, giving an average score of $0.4 \times 5 + 0.3 \times 4 = 3.2$. Applicant Kiran has income band 3 and history 8: score $1.2 + 2.4 = 3.6$, rejected.

For a linear model with independent features, the SHAP value of each feature is its weight times its deviation from the average:

- Income: $0.4 \times (3 - 5) = -0.8$.
- History: $0.3 \times (8 - 4) = +1.2$.

The contributions sum to $0.4 = 3.6 - 3.2$, the gap between Kiran's score and the average. A **counterfactual explanation**: "If your income band were 4 instead of 3, your score would be 4.0 and the loan would be approved." This tells Kiran what mattered and what would change the decision.

## Applications

- **Hiring and lending:** fairness audits and adverse-action explanations.
- **Healthcare:** checking diagnostic models across age, sex, and ethnicity.
- **Criminal justice:** scrutiny of risk-assessment tools.
- **Content moderation and recommendation:** auditing disparate error rates and exposure.
- **Model governance:** model cards and documentation for regulators and users.

## Common mistakes

- **Assuming that removing protected attributes removes bias.** Proxies carry the same information.
- **Reporting only overall accuracy.** Always break performance down by group.
- **Treating one fairness metric as the definition of fairness.** Metrics conflict; choose with the context and stakeholders.
- **Trusting post-hoc explanations blindly.** They approximate the model and can mislead.
- **Treating fairness as a one-time check.** Data and populations drift; monitor after deployment.

## Revision notes

- Bias sources: historical, representation, measurement, aggregation, evaluation, deployment, feedback loops.
- Demographic parity (selection rates; four-fifths rule), equal opportunity (TPR), equalised odds (TPR and FPR), predictive parity (precision).
- With different base rates, calibration and equal error rates cannot all hold.
- Mitigation: pre-, in-, and post-processing.
- Explanations: interpretable models, global (importance, partial dependence), local (LIME, SHAP, counterfactuals).
- Governance: datasheets, model cards, oversight, GDPR, EU AI Act, India's DPDP Act 2023.

## Practice questions

:::question basic
Define demographic parity and equal opportunity.
:::answer
Demographic parity requires the same selection rate (the fraction predicted positive) in every group. Equal opportunity requires the same true positive rate: among people who truly qualify, each group must have the same chance of a positive prediction.
:::

:::question basic
A hiring model selects 45% of group X and 60% of group Y. Does it pass the four-fifths rule?
:::answer
The disparate impact ratio is $0.45 / 0.60 = 0.75$, which is below 0.8, so it fails the four-fifths rule and the disparity should be investigated.
:::

:::question intermediate
Why does removing a protected attribute from the training data not guarantee a fair model?
:::answer
Other features can be strongly correlated with the protected attribute, such as postcode, school, name, or shopping patterns, and the model can learn the same pattern through these proxies. Historical bias in the labels also remains. Fairness has to be measured on outcomes, which in fact requires knowing group membership for auditing.
:::

:::question intermediate
Explain the difference between a global and a local explanation, with one method for each.
:::answer
A global explanation describes the model's overall behaviour, for example permutation feature importance, which measures how much accuracy drops when each feature is shuffled. A local explanation describes a single prediction, for example SHAP values, which attribute that prediction's difference from the average to each feature, or a counterfactual stating the smallest change that would flip the decision.
:::

:::question advanced
State the impossibility result for fairness criteria and explain what it means in practice.
:::answer
When the base rate of the outcome differs between groups and the classifier is not perfect, it cannot simultaneously be calibrated (or have equal precision) in each group and have equal false positive and false negative rates across groups. In practice, designers must decide which errors matter most in the specific context, for example whether wrongly denying qualified people or wrongly approving unqualified ones causes more harm, document that choice, involve affected stakeholders, and consider whether an automated decision is appropriate at all.
:::

## Further learning

- **Next:** *The End-to-End ML Pipeline* in Machine Learning shows where data and evaluation choices are made.
- **Related:** *Classification Metrics & ROC Curves* in Machine Learning explains the error rates used in fairness metrics.
