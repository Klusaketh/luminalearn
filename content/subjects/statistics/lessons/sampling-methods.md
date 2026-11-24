---
lesson: sampling-methods
title: Data Collection & Sampling Methods
summary: Populations, samples, parameters, and statistics; probability sampling designs (simple random, stratified, cluster, systematic); sources of bias; and the difference between observational studies and randomised experiments.
minutes: 40
type: theory
objectives:
  - Distinguish population from sample and parameter from statistic, and explain why random sampling matters
  - Choose between simple random, stratified, cluster, and systematic sampling for a given situation
  - Identify selection, non-response, and response bias, and explain why only randomised experiments support causal conclusions
review: ai-draft
---
## Introduction

Statistics is only as good as its data. A survey of a million people can be worse than one of a thousand if the million were chosen badly, as the 1936 *Literary Digest* poll famously showed when it predicted the wrong winner of a US presidential election from 2.4 million responses. How data is collected determines what conclusions are valid. This lesson covers the main ways of selecting samples, the biases that ruin them, and why a randomised experiment is the gold standard for establishing cause and effect.

**Before you start:** no special prerequisites; descriptive statistics and basic probability help.

## Core theory

### Populations, samples, parameters, and statistics

The **population** is the entire group of interest, such as all students at a university. A **sample** is the subset actually measured. A **parameter** is a number describing the population (the true mean height $\mu$, the true proportion $p$ who support a policy), usually unknown. A **statistic** is a number computed from the sample ($\bar{x}$, $\hat{p}$), used to estimate the parameter. Because samples vary, statistics vary from sample to sample: **sampling variability**, which later lessons quantify.

### Probability sampling designs

In a **probability sample**, every member of the population has a known, non-zero chance of selection, which allows valid inference.

- **Simple random sample (SRS):** every subset of size $n$ is equally likely, like drawing names from a hat. It is the basis of most statistical theory.
- **Stratified sampling:** divide the population into **strata** that are similar inside (such as year of study), and take an SRS within each. It guarantees representation of every group and often reduces variability.
- **Cluster sampling:** divide the population into **clusters** (such as classrooms or villages), randomly select some clusters, and measure everyone in them. It is cheaper when the population is spread out, but usually more variable than an SRS of the same size because members of a cluster tend to be alike.
- **Systematic sampling:** choose a random start and then every $k$-th item from a list. It is simple, but it can fail badly if the list has a periodic pattern that lines up with $k$.

**Convenience samples** (whoever is easiest to reach) and **voluntary response samples** (people who choose to reply, like online polls) are not probability samples; they systematically over-represent some groups and cannot support reliable inference.

### Bias

**Bias** is a systematic tendency to over- or under-estimate the parameter. A larger sample reduces random variability but does **not** reduce bias.

- **Selection (undercoverage) bias:** some groups are left out of the sampling frame, such as people without landlines in a phone survey.
- **Non-response bias:** the people who do not respond differ from those who do.
- **Response bias:** answers are inaccurate because of leading questions, social desirability, or poor memory.
- **Survivorship bias:** only "survivors" are observed, such as studying only successful startups.

### Observational studies and experiments

In an **observational study**, researchers measure variables without intervening. Such studies can reveal **associations**, but **confounding variables** may explain them: ice-cream sales and drownings rise together because of hot weather, not because one causes the other.

In an **experiment**, researchers assign **treatments** to subjects. A well-designed experiment uses a **control group**, **random assignment** (so that, on average, the groups are alike in every respect, including unmeasured confounders), **replication** on enough subjects, and, where possible, **blinding** (subjects and evaluators do not know who received which treatment) and a **placebo**. Only randomised experiments support strong **causal** conclusions. In technology this is the **A/B test**: users are randomly shown version A or B of a page.

## Worked examples

### Example 1: Simple random versus stratified sampling

A university has 6,000 students: 3,000 first-years, 2,000 second-years, and 1,000 final-years. We want a sample of 300 to estimate the average weekly study hours, which differ strongly by year.

- **SRS:** draw 300 students at random from all 6,000. Each sample's composition varies; by chance it may contain, say, 140 first-years and 70 final-years.
- **Proportional stratified sample:** draw $300 \times \frac{3000}{6000} = 150$ first-years, 100 second-years, and 50 final-years, each at random within its year.

```python
import random
from statistics import mean, pstdev

rng = random.Random(7)
hours = {"first": [rng.gauss(12, 2) for _ in range(3000)],
         "second": [rng.gauss(18, 2) for _ in range(2000)],
         "final": [rng.gauss(26, 2) for _ in range(1000)]}
population = [h for group in hours.values() for h in group]
true_mean = mean(population)

def srs():
    return mean(rng.sample(population, 300))

def stratified():
    picks = rng.sample(hours["first"], 150) + rng.sample(hours["second"], 100) + rng.sample(hours["final"], 50)
    return mean(picks)

srs_estimates = [srs() for _ in range(500)]
strat_estimates = [stratified() for _ in range(500)]
print(f"true mean {true_mean:.2f}")
print(f"SRS:        average estimate {mean(srs_estimates):.2f}, spread {pstdev(srs_estimates):.3f}")
print(f"stratified: average estimate {mean(strat_estimates):.2f}, spread {pstdev(strat_estimates):.3f}")
print("stratified spread is smaller:", pstdev(strat_estimates) < pstdev(srs_estimates))
```

The program simulates a population and repeats each design 500 times. Exact figures depend on the random numbers, but both designs average out to the true mean (neither is biased), while the stratified estimates vary far less from sample to sample, because the large differences **between** years no longer add randomness. Stratifying on a variable related to the outcome is a cheap way to gain precision.

### Example 2: Spotting the flaw

1. A news website asks readers to vote on whether a new law is good; 80% say no. **Flaw:** voluntary response. People with strong (often negative) opinions are far more likely to vote, and site readers are not representative of the population.
2. A study finds that people who take vitamin supplements have fewer heart attacks. **Flaw:** observational study with likely confounders (supplement users may exercise more, smoke less, or have higher incomes). Only a randomised trial can show that the vitamins cause the difference.
3. To estimate the average household size, a researcher picks random **people** and asks the size of their household. **Flaw:** large households are more likely to be selected, because they contain more people, so the estimate is biased upwards. Sample households, not people.
4. An app surveys its current users about satisfaction and reports 92% satisfied. **Flaw:** survivorship bias. Dissatisfied users have already uninstalled the app.

## Applications

- **Opinion polls:** stratified random samples of about 1,000 people estimate national opinion within a few percentage points.
- **A/B testing:** randomised experiments decide which product design performs better.
- **Clinical trials:** randomised, double-blind, placebo-controlled trials establish whether treatments work.
- **Quality control:** random samples from production lines estimate defect rates.

## Common mistakes

- **Believing large samples fix bias.** A huge biased sample is precisely wrong.
- **Drawing causal conclusions from observational data.** Association is not causation.
- **Using convenience or voluntary samples for inference.** They are not representative.
- **Confusing stratified and cluster sampling.** Stratified samples within every group; cluster sampling picks whole groups.
- **Ignoring non-response.** Low response rates can bias results even with a perfect sampling frame.

## Revision notes

- Population vs sample; parameter (unknown, about the population) vs statistic (computed from the sample).
- SRS: all subsets equally likely; stratified: SRS within each stratum; cluster: random whole clusters; systematic: every $k$-th.
- Convenience and voluntary response samples are biased.
- Biases: selection, non-response, response, survivorship; size does not cure bias.
- Observational studies show association; confounders threaten them.
- Randomised controlled experiments (with blinding and placebo where possible) support causation.

## Practice questions

:::question basic
A survey of 500 randomly chosen voters finds 54% support a candidate. Identify the population, sample, parameter, and statistic.
:::answer
The population is all voters; the sample is the 500 surveyed voters; the parameter is the true proportion of all voters who support the candidate; and the statistic is the sample proportion, 54%.
:::

:::question basic
Why does an online poll on a news website not give a reliable estimate of public opinion?
:::answer
It is a voluntary response sample: people choose whether to take part, and those with strong opinions are more likely to respond. The readers of one website are also not representative of the whole population, so the result is biased in unknown ways.
:::

:::question intermediate
A school district wants to survey parents. It randomly selects 10 of its 60 schools and surveys every parent at those schools. What kind of sample is this, and what is its main weakness?
:::answer
It is a cluster sample, with schools as clusters. It is convenient and cheap, but parents at the same school tend to be similar (same neighbourhood, same school policies), so the estimate is usually more variable than a simple random sample of the same number of parents.
:::

:::question intermediate
A study finds that students who sleep more get higher grades. Can we conclude that more sleep causes higher grades? What study would answer that?
:::answer
No. This is observational, and confounders such as stress, workload, part-time jobs, or health may affect both sleep and grades. A randomised experiment, assigning students at random to different sleep schedules, would balance such confounders on average and allow a causal conclusion, though it may be hard to run ethically or practically.
:::

:::question advanced
Explain why random assignment allows causal conclusions even when there are confounders nobody has thought of.
:::answer
Random assignment decides who gets each treatment by chance, independently of every characteristic of the subjects, measured or not. So, on average, the treatment and control groups have the same distribution of every potential confounder, known or unknown. Any systematic difference in outcomes larger than chance variation can therefore be attributed to the treatment itself, and significance tests quantify how likely the observed difference is under chance alone.
:::

## Further learning

- **Next:** *Central Limit Theorem & Sampling Error* quantifies how much a statistic varies from sample to sample.
- **Related:** *Conditional Probability & Bayes Theorem* in Probability helps reason about biased selection.
