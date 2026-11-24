---
lesson: foundations-of-ai
title: Foundations of Artificial Intelligence
summary: What artificial intelligence is, the four classic ways of defining it, the Turing test and its critics, the disciplines AI draws on, its history from the 1950s to large language models, and the difference between symbolic and statistical approaches.
minutes: 35
type: theory
objectives:
  - Compare the four approaches to defining AI and explain why the rational-agent view is the standard working definition
  - Describe the Turing test, the Chinese Room argument, and the main periods of AI history
  - Distinguish symbolic (rule-based) AI from statistical (learning-based) AI and narrow AI from general AI
review: ai-draft
---
## Introduction

Artificial intelligence (AI) is the study and construction of systems that perceive, reason, learn, and act in ways we would call intelligent. It already shapes daily life: route planning in map apps, spam filters, face unlock, recommendation feeds, machine translation, and chat assistants. Yet "intelligence" is hard to define, and the field has swung between very different ideas of how to achieve it. This lesson builds the vocabulary and historical context that every later AI topic relies on.

**Before you start:** no prior AI knowledge is needed; basic programming and probability help with the examples.

## Core theory

### Four ways to define AI

Definitions of AI differ along two dimensions: whether they concern **thinking** or **acting**, and whether success is measured against **human** performance or against an ideal standard of **rationality**.

| | Human-like | Rational |
| :--- | :--- | :--- |
| **Thinking** | Thinking humanly: model how people think (cognitive science) | Thinking rationally: reason correctly with logic ("laws of thought") |
| **Acting** | Acting humanly: behave indistinguishably from a person (Turing test) | Acting rationally: do the right thing to achieve the best expected outcome |

Modern AI mostly adopts the **rational agent** view: an agent should choose actions that maximise its expected performance, given what it has perceived and what it knows. This standard is mathematically precise, does not require copying human quirks, and includes correct reasoning as just one way of acting well. Rational does not mean all-knowing: it means making the best choice with the information available.

### The Turing test and its critics

In his 1950 paper *Computing Machinery and Intelligence*, Alan Turing replaced "Can machines think?" with the **imitation game**: a human judge holds text conversations with a person and a machine; if the judge cannot reliably tell which is which, the machine passes. Passing requires natural language processing, knowledge representation, automated reasoning, and machine learning. The **total Turing test** adds perception and physical manipulation, bringing in computer vision and robotics.

John Searle's **Chinese Room** argument (1980) challenges the idea that passing such a test proves understanding. A person who knows no Chinese follows a rule book to answer Chinese questions perfectly; the room behaves intelligently, yet nobody inside understands Chinese. Searle concluded that manipulating symbols (syntax) is not enough for meaning (semantics). Critics reply that the whole system, not the person alone, might understand. The debate remains open, which is one reason researchers focus on measurable behaviour rather than inner experience.

### The foundations of AI

AI draws on many fields: **philosophy** (logic, mind, ethics), **mathematics** (logic, computability, probability), **economics** (utility and decision theory), **neuroscience** and **psychology** (how brains and minds work), **computer engineering** (fast hardware), **control theory** (feedback and optimisation), and **linguistics** (structure of language).

### A short history

- **1943:** McCulloch and Pitts propose a mathematical model of the neuron.
- **1950:** Turing proposes the imitation game.
- **1956:** the Dartmouth workshop, organised by John McCarthy, Marvin Minsky, Nathaniel Rochester, and Claude Shannon, launches "artificial intelligence" as a field.
- **1958–1966:** early optimism: Rosenblatt's perceptron, general problem solvers, and ELIZA, a pattern-matching chatbot.
- **1970s:** the first **AI winter**: early systems failed to scale, and funding was cut after critical reviews such as the 1973 Lighthill report in the UK.
- **1980s:** **expert systems** encode specialists' rules (for example, R1/XCON configured computer orders); a second winter follows when they prove brittle and expensive to maintain.
- **1990s–2000s:** probability and machine learning take centre stage; IBM's Deep Blue defeats chess champion Garry Kasparov in 1997.
- **2012 onward:** **deep learning** wins the ImageNet image-recognition challenge; DeepMind's AlphaGo beats Go champion Lee Sedol in 2016; the Transformer architecture (2017) leads to large language models and, from 2022, widely used chat assistants.

### Symbolic versus statistical AI

- **Symbolic AI** (sometimes called "good old-fashioned AI") represents knowledge explicitly as symbols, rules, and logic. It is transparent and precise, but brittle: someone must write every rule, and real-world exceptions are endless.
- **Statistical (machine-learning) AI** learns patterns from data, often with neural networks. It handles noise and perception well, but needs lots of data and can be hard to interpret.
- **Neuro-symbolic** systems combine both, for example a language model that calls a calculator or queries a knowledge graph.

### Narrow and general AI

Every deployed system today is **narrow AI**: it performs specific tasks, sometimes superhumanly, but cannot transfer that competence to unrelated problems the way people do. **Artificial general intelligence** (AGI) refers to hypothetical systems with broad, human-level ability across domains. Searle also distinguished **weak AI** (machines can act as if intelligent) from **strong AI** (machines actually have minds).

## Worked examples

### Example 1: Hand-written rules versus a learned rule

The first half of this program is symbolic AI: pattern-matching rules in the style of ELIZA. The second half is statistical AI: it learns a pass/fail rule from labelled examples by trying candidate thresholds and keeping the one with the fewest mistakes.

```python
import re

# Symbolic AI: hand-written pattern rules, in the style of 1960s chatbots
RULES = [
    (r"i feel (.*)", "Why do you feel {0}?"),
    (r"i am (.*)", "How long have you been {0}?"),
    (r".*\bexam\b.*", "Exams can be stressful. Which subject is it?"),
    (r".*", "Please tell me more."),
]


def respond(sentence):
    text = sentence.lower().strip(".!? ")
    for pattern, template in RULES:
        match = re.fullmatch(pattern, text)
        if match:
            return template.format(*match.groups())


for line in ["I feel tired.", "I am worried about my exam", "The weather is nice"]:
    print(f"> {line}\n  {respond(line)}")

# Statistical AI: learn a rule from labelled examples instead of writing it
hours = [1, 2, 2.5, 3, 4, 4.5, 5, 6, 7, 8]
passed = [0, 0, 0, 0, 1, 0, 1, 1, 1, 1]


def errors(threshold):
    return sum((h >= threshold) != bool(p) for h, p in zip(hours, passed))


for t in [3, 4, 5, 6]:
    print(f"rule 'pass if hours >= {t}': mistakes = {errors(t)}")
best = min(sorted(set(hours)), key=errors)
print(f"learned rule: pass if hours >= {best}")
```

Output:

```text
> I feel tired.
  Why do you feel tired?
> I am worried about my exam
  How long have you been worried about my exam?
> The weather is nice
  Please tell me more.
rule 'pass if hours >= 3': mistakes = 2
rule 'pass if hours >= 4': mistakes = 1
rule 'pass if hours >= 5': mistakes = 1
rule 'pass if hours >= 6': mistakes = 2
learned rule: pass if hours >= 4
```

The chatbot looks clever on the first sentence, but the second response exposes it: it echoes "my exam" back without changing it to "your exam", and the exam rule never fired because the "i am" rule came first. The program shuffles symbols with no understanding, exactly the gap the Chinese Room argument points at. The learned rule, by contrast, was not written by a programmer: thresholds 4 and 5 both make one mistake on the data (the student who studied 4.5 hours but failed, or the student who studied 4 hours and passed), and the tie is broken towards the smaller threshold. Real machine learning works the same way at scale: choose the model that best fits the examples, then hope it generalises.

### Example 2: Classifying systems by approach

Decide which definition of AI each system best illustrates.

1. A chess engine that searches millions of positions and plays the move with the highest evaluation. **Acting rationally:** it chooses the action with the best expected outcome, without imitating how grandmasters think.
2. A computer model that reproduces human reaction times and typical memory errors in a recall experiment. **Thinking humanly:** its purpose is to mirror human cognition, mistakes included.
3. A theorem prover that derives new mathematical results from axioms with sound inference rules. **Thinking rationally:** correct logical reasoning is the goal.
4. A customer-service bot evaluated by whether customers believe they spoke to a person. **Acting humanly:** success is indistinguishability from a human.

Now classify the technique: a spam filter trained on millions of labelled emails is **statistical**; a tax-calculation engine that applies the published rules of the tax code is **symbolic**.

## Applications

- **Navigation and logistics:** route planning and delivery scheduling use search and optimisation.
- **Healthcare:** image-based screening and clinical decision support.
- **Finance:** fraud detection and credit-risk modelling.
- **Language:** translation, speech recognition, and conversational assistants.
- **Education:** adaptive tutoring systems that personalise practice and feedback.

## Common mistakes

- **Treating AI and machine learning as synonyms.** Machine learning is one part of AI, alongside search, planning, logic, and probabilistic reasoning.
- **Taking fluent conversation as proof of understanding.** Behaviour and understanding are different claims.
- **Assuming deployed AI is general.** Today's systems are narrow, even when they are very capable.
- **Thinking symbolic AI is obsolete.** Rules, logic, and knowledge graphs remain central in planning, verification, and hybrid systems.
- **Confusing "rational" with "never wrong".** A rational agent can make a decision that turns out badly; what matters is that it was the best choice given its information.

## Revision notes

- Four definitions: thinking humanly, thinking rationally, acting humanly, acting rationally; modern AI uses the rational agent.
- Turing test (1950): can a judge tell machine from human in conversation? Chinese Room (1980): symbol manipulation is not understanding.
- Foundations: philosophy, mathematics, economics, neuroscience, psychology, computer engineering, control theory, linguistics.
- History: Dartmouth 1956, early optimism, AI winters (1970s, late 1980s), expert systems, statistical ML, deep learning (2012), Transformers (2017), LLMs.
- Symbolic AI: explicit rules, transparent but brittle. Statistical AI: learned from data, robust but data-hungry and less interpretable.
- Narrow AI performs specific tasks; AGI is hypothetical broad intelligence.

## Practice questions

:::question basic
List the four approaches to defining AI and state which one modern AI mainly follows.
:::answer
Thinking humanly, thinking rationally, acting humanly, and acting rationally. Modern AI mainly follows acting rationally: building agents that choose actions maximising expected performance given their percepts and knowledge.
:::

:::question basic
What did Turing propose in place of the question "Can machines think?"
:::answer
He proposed the imitation game, now called the Turing test: a judge converses by text with a hidden human and a hidden machine; if the judge cannot reliably tell which is the machine, the machine is said to behave intelligently.
:::

:::question intermediate
Contrast symbolic and statistical AI, giving one strength and one weakness of each.
:::answer
Symbolic AI represents knowledge as explicit rules and logic: it is transparent and its reasoning can be checked, but it is brittle because every rule and exception must be written by hand. Statistical AI learns patterns from data: it copes well with noise and perception tasks, but it needs large datasets and its decisions can be hard to explain.
:::

:::question intermediate
Why is "acting rationally" a more useful working definition for engineers than "acting humanly"?
:::answer
Rationality is defined precisely by a performance measure, so it can be analysed and optimised mathematically. Acting humanly would require copying human errors and limitations that are irrelevant or harmful for most tasks; we want a self-driving car that drives safely, not one that drives like an average human.
:::

:::question advanced
Summarise the Chinese Room argument and one well-known reply to it.
:::answer
Searle imagines a person who does not know Chinese following a rule book to produce perfect answers to Chinese questions. The room passes a Turing test in Chinese, yet nobody in it understands Chinese, so Searle argues that running a program (symbol manipulation) cannot by itself produce understanding. The systems reply says that understanding belongs to the whole system of person, rule book, and room, not to the person alone; Searle answers that the person could memorise the rules and still understand nothing.
:::

## Further learning

- **Next:** *PEAS Model & Agent Taxonomies* formalises the rational agent.
- **Related:** *Problem Formulation & Uninformed Search* shows how agents plan sequences of actions.
