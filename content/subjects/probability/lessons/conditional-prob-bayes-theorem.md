---
lesson: conditional-prob-bayes-theorem
title: Conditional Probability & Bayes Theorem
summary: Conditional probability, the multiplication rule, independence, the law of total probability, and Bayes' theorem for updating beliefs, with medical-test and spam-filter examples.
minutes: 45
type: theory
objectives:
  - Compute conditional probabilities and apply the multiplication rule to sequences of events
  - Test events for independence and use the law of total probability to combine cases
  - Apply Bayes' theorem to update a prior into a posterior and explain the base-rate fallacy
review: ai-draft
---
## Introduction

New information changes probabilities. The chance that a patient has a disease changes once a test comes back positive; the chance that an email is spam changes once you see the word "lottery". **Conditional probability** describes probabilities given that something is known, and **Bayes' theorem** turns the probability of the evidence given a hypothesis into the probability of the hypothesis given the evidence. It is the engine behind spam filters, medical diagnosis, and much of machine learning.

**Before you start:** you should know sample spaces, events, and the probability axioms.

## Core theory

### Conditional probability

The probability of A **given** B, for $P(B) > 0$, is

$$P(A \mid B) = \frac{P(A \cap B)}{P(B)}$$

Knowing that B occurred shrinks the sample space to B, and we ask what fraction of it also lies in A. Note that $P(A \mid B)$ and $P(B \mid A)$ are generally different: most people who play the lottery lose, but most losers did not play.

### The multiplication rule

Rearranging gives $P(A \cap B) = P(B)\,P(A \mid B) = P(A)\,P(B \mid A)$, and for several events

$$P(A_1 \cap A_2 \cap A_3) = P(A_1)\,P(A_2 \mid A_1)\,P(A_3 \mid A_1 \cap A_2)$$

This is how to compute probabilities of sequences, such as drawing cards without replacement.

### Independence

A and B are **independent** if $P(A \cap B) = P(A)P(B)$, equivalently $P(A \mid B) = P(A)$: knowing B does not change the probability of A. Successive fair coin tosses are independent; draws without replacement are not. Several events are **mutually independent** if the product rule holds for every subcollection. Do not confuse independence with disjointness: disjoint events with positive probabilities are always **dependent**, since one occurring rules out the other.

### The law of total probability

If $B_1, \dots, B_n$ partition the sample space (disjoint, covering every outcome), then

$$P(A) = \sum_{i=1}^{n} P(A \mid B_i)\,P(B_i)$$

Split into cases, compute the probability within each, and weight by how likely each case is. A **probability tree** draws this: the branches out of each node sum to 1, and the probability of a path is the product along it.

### Bayes' theorem

Combining the definitions:

$$P(B_j \mid A) = \frac{P(A \mid B_j)\,P(B_j)}{\sum_i P(A \mid B_i)\,P(B_i)}$$

In the language of inference: $P(B_j)$ is the **prior** (belief before the evidence), $P(A \mid B_j)$ the **likelihood** (how well hypothesis $B_j$ predicts the evidence), and $P(B_j \mid A)$ the **posterior** (belief after the evidence). The denominator is the total probability of the evidence.

### The base-rate fallacy

People often ignore the prior. A test that is 99% accurate seems to mean a positive result is 99% likely to be correct, but if the condition is rare, most positives can be **false positives**, because the healthy population is so much larger. Bayes' theorem accounts for this.

## Worked examples

### Example 1: A medical test

A disease affects 1% of a population. A test detects it in 99% of people who have it (sensitivity) and gives a false positive for 5% of healthy people (so its specificity is 95%). A person tests positive. How likely is it that they have the disease?

Let D be "has disease" and + be "tests positive".

- Prior: $P(D) = 0.01$, $P(D^c) = 0.99$.
- Likelihoods: $P(+ \mid D) = 0.99$, $P(+ \mid D^c) = 0.05$.
- Total probability: $P(+) = 0.99 \times 0.01 + 0.05 \times 0.99 = 0.0099 + 0.0495 = 0.0594$.
- Posterior: $P(D \mid +) = 0.0099 / 0.0594 \approx 0.1667$.

Only about one in six people who test positive actually has the disease. A second, independent positive test changes the picture, using the first posterior as the new prior:

```python
def posterior(prior, sensitivity=0.99, false_positive=0.05):
    evidence = sensitivity * prior + false_positive * (1 - prior)
    return sensitivity * prior / evidence

p1 = posterior(0.01)
p2 = posterior(p1)
print(f"after one positive test:  {p1:.4f}")
print(f"after two positive tests: {p2:.4f}")
population = 100_000
sick = population // 100
print("true positives:", round(0.99 * sick), "false positives:", round(0.05 * (population - sick)))
```

Output:

```text
after one positive test:  0.1667
after two positive tests: 0.7984
true positives: 990 false positives: 4950
```

Counting real people makes the result intuitive: out of 100,000, about 990 true positives are swamped by 4,950 false positives.

### Example 2: Cards without replacement and a simple spam filter

**(a)** Two cards are drawn without replacement. $P(\text{both aces}) = \frac{4}{52} \cdot \frac{3}{51} = \frac{1}{221}$ by the multiplication rule. The draws are dependent: $P(\text{second ace} \mid \text{first ace}) = 3/51$, but $P(\text{second ace}) = 4/52$ by symmetry.

**(b)** 40% of emails are spam. The word "free" appears in 30% of spam and 2% of genuine emails. Given that an email contains "free":

$$P(\text{spam} \mid \text{free}) = \frac{0.3 \times 0.4}{0.3 \times 0.4 + 0.02 \times 0.6} = \frac{0.12}{0.132} \approx 0.909$$

```python
from fractions import Fraction
print(Fraction(4, 52) * Fraction(3, 51))
spam, free_given_spam, free_given_ham = 0.4, 0.30, 0.02
p_free = free_given_spam * spam + free_given_ham * (1 - spam)
print(round(free_given_spam * spam / p_free, 3), round(p_free, 3))
```

Output:

```text
1/221
0.909 0.132
```

A naive Bayes spam filter repeats this update for every word, assuming the words are independent given the class.

## Applications

- **Medicine:** interpreting test results with prevalence (priors) and accuracy (likelihoods).
- **Machine learning:** naive Bayes classifiers and Bayesian inference update beliefs from data.
- **Reliability:** components in series and parallel combine with independence.
- **Search and rescue:** Bayesian search updates where to look after each unsuccessful search.

## Common mistakes

- **Confusing $P(A \mid B)$ with $P(B \mid A)$.** The "prosecutor's fallacy" swaps them.
- **Ignoring base rates.** A rare condition makes most positive results false.
- **Assuming independence without justification.** Draws without replacement are dependent.
- **Treating disjoint events as independent.** If one excludes the other, they are dependent.
- **Forgetting to normalise.** The posterior's denominator is the total probability of the evidence.

## Revision notes

- $P(A \mid B) = P(A \cap B)/P(B)$.
- Multiplication: $P(A \cap B) = P(B)P(A \mid B)$; chain it for sequences.
- Independent: $P(A \cap B) = P(A)P(B)$.
- Total probability: $P(A) = \sum_i P(A \mid B_i)P(B_i)$.
- Bayes: posterior = likelihood × prior / evidence.
- Base-rate fallacy: rare conditions produce many false positives.

## Practice questions

:::question basic
A die is rolled. Given that the result is even, what is the probability that it is a 6?
:::answer
Given "even", the sample space shrinks to {2, 4, 6}, so $P(6 \mid \text{even}) = (1/6)/(3/6) = 1/3$.
:::

:::question basic
Two fair coins are tossed. Are "the first is heads" and "the two coins match" independent?
:::answer
Yes. $P(\text{first H}) = 1/2$, $P(\text{match}) = P(HH) + P(TT) = 1/2$, and $P(\text{first H and match}) = P(HH) = 1/4 = (1/2)(1/2)$, so the product rule holds.
:::

:::question intermediate
Factory A makes 60% of a product with a 2% defect rate; factory B makes 40% with a 5% defect rate. What fraction of all products are defective?
:::answer
By the law of total probability, $P(\text{defect}) = 0.02 \times 0.6 + 0.05 \times 0.4 = 0.012 + 0.020 = 0.032$, so 3.2% are defective.
:::

:::question intermediate
Using the previous question, if a product is defective, what is the probability it came from factory B?
:::answer
By Bayes' theorem, $P(B \mid \text{defect}) = \frac{0.05 \times 0.4}{0.032} = 0.020/0.032 = 0.625$. Although B makes fewer products, it accounts for 62.5% of defective ones because its defect rate is higher.
:::

:::question advanced
A test for a condition with prevalence 0.1% has sensitivity 99.9% and specificity 99.9%. What is the probability that a person who tests positive has the condition, and what does this teach about screening rare conditions?
:::answer
$P(+) = 0.999 \times 0.001 + 0.001 \times 0.999 = 0.001998$, and $P(D \mid +) = 0.000999/0.001998 = 0.5$. Even with a 99.9% accurate test, a positive result is only a coin flip, because healthy people outnumber sick people 999 to 1. Screening for rare conditions therefore needs confirmatory tests or must target higher-risk groups where the prior is larger.
:::

## Further learning

- **Next:** *Random Variables & Distributions* attaches numbers to outcomes.
- **Related:** *k-NN, Naive Bayes & Support Vector Machines* in Machine Learning applies Bayes' theorem to data.
