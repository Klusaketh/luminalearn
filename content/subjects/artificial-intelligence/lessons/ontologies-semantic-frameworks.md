---
lesson: ontologies-semantic-frameworks
title: Ontologies & Semantic Frameworks
summary: Representing knowledge with categories, semantic networks, frames, and ontologies; inheritance and default reasoning with exceptions; description logics; and the Semantic Web stack of RDF triples, RDFS, OWL, SPARQL, and knowledge graphs.
minutes: 40
type: theory
objectives:
  - Model a domain with classes, instances, properties, and subclass and instance relationships
  - Explain inheritance in semantic networks and frames, including defaults, exceptions, and multiple-inheritance conflicts
  - Write RDF-style triples, apply RDFS domain and range inferences, and contrast the open-world and closed-world assumptions
review: ai-draft
---
## Introduction

To answer "Can this patient take this drug?" or "Which courses does this lecturer teach?", a program needs knowledge about the world organised so it can reason with it. **Ontologies** provide that organisation: they define the kinds of things in a domain, how the kinds relate, and which facts follow automatically. They power the knowledge panels in search engines, medical terminologies used by hospitals, product catalogues, and the knowledge graphs that ground modern AI assistants.

**Before you start:** you should know sets and basic logic; *Propositional Logic & Inference* complements this lesson.

## Core theory

### Categories, objects, and relations

Most reasoning happens at the level of **categories** (classes): knowing that something is a bird tells you it probably flies and lays eggs. An **ontology** is an explicit specification of a domain's concepts: its **classes**, **individuals** (instances), **properties** (relations and attributes), and **axioms** (rules that constrain them). Key relations:

- **subclass of** (is-a between classes): every Penguin is a Bird.
- **instance of** (membership): penguin_17 is a Penguin.
- **part of**: a wing is part of a bird.

Classes can be declared **disjoint** (nothing is both a Mammal and a Bird) or form an **exhaustive decomposition** (every Animal is in at least one subclass); a disjoint exhaustive decomposition is a **partition**. An **upper ontology** defines very general concepts (objects, events, time) that domain ontologies specialise.

### Semantic networks and frames

A **semantic network** draws classes and individuals as nodes and relations as labelled links. Properties attached to a class are **inherited** by its subclasses and instances, which stores each fact once. **Frames** represent the same idea as records: a frame for Bird has slots such as `can_fly: true` and `covering: feathers`, and more specific frames inherit or override slot values.

Inheritance usually treats class properties as **defaults** that more specific classes can override: birds fly, but penguins do not. This makes reasoning **nonmonotonic**: learning a new fact (that Pip is a penguin) can withdraw a conclusion (Pip flies). With **multiple inheritance**, defaults can conflict. In the classic **Nixon diamond**, Quakers are typically pacifists and Republicans are typically not; for someone who is both, inheritance alone cannot decide.

### Description logics

**Description logics** give ontologies a precise logical meaning. They describe classes with constructors such as intersection, union, and restrictions ("a Parent is a Person with at least one child") and support automated reasoning tasks: **subsumption** (is one class necessarily a subclass of another?), **classification** (placing a class in the hierarchy), and **consistency checking**. They are designed so these tasks remain decidable.

### The Semantic Web stack

- **RDF** represents knowledge as **triples** (subject, predicate, object), with globally unique identifiers (IRIs): `(hyderabad, locatedIn, telangana)`. A set of triples forms a directed, labelled graph: a **knowledge graph**.
- **RDFS** adds vocabulary such as `subClassOf`, `subPropertyOf`, `domain`, and `range`, with simple inference rules. If a property's domain is Lecturer, anything that has that property is inferred to be a Lecturer.
- **OWL** (Web Ontology Language), based on description logics, adds equivalence, disjointness, cardinality restrictions, and transitive or inverse properties.
- **SPARQL** queries triple stores by matching graph patterns.

Semantic Web reasoning uses the **open-world assumption**: if a fact is not stated, it is unknown, not false. Databases use the **closed-world assumption**: anything not recorded is false. Large public knowledge graphs such as Wikidata contain billions of triples.

## Worked examples

### Example 1: A small triple store with inheritance

The program stores facts as triples, follows `subclass_of` links transitively, and looks up properties from the most specific class that mentions them.

```python
triples = {
    ("Animal", "subclass_of", "LivingThing"),
    ("Bird", "subclass_of", "Animal"),
    ("Penguin", "subclass_of", "Bird"),
    ("Sparrow", "subclass_of", "Bird"),
    ("penguin_17", "instance_of", "Penguin"),
    ("sparrow_3", "instance_of", "Sparrow"),
    ("Animal", "breathes", True),
    ("Bird", "can_fly", True),
    ("Bird", "has_part", "wings"),
    ("Penguin", "can_fly", False),      # exception overrides the default
    ("Penguin", "lives_in", "Antarctica"),
}


def query(s=None, p=None, o=None):
    return sorted((a, b, c) for a, b, c in triples
                  if (s is None or a == s) and (p is None or b == p) and (o is None or c == o))


def ancestors(cls):
    """Classes from most specific to most general (transitive subclass_of)."""
    chain = [cls]
    while True:
        parents = query(chain[-1], "subclass_of")
        if not parents:
            return chain
        chain.append(parents[0][2])


def lookup(individual, prop):
    cls = query(individual, "instance_of")[0][2]
    for c in ancestors(cls):  # the most specific class that says something wins
        found = query(c, prop)
        if found:
            return found[0][2], c
    return None, None


print("classes of penguin_17:", " -> ".join(ancestors("Penguin")))
for individual in ["sparrow_3", "penguin_17"]:
    for prop in ["can_fly", "breathes", "has_part"]:
        value, source = lookup(individual, prop)
        print(f"{individual}.{prop} = {value!s:5} (from class {source})")
birds = [s for s, _, c in query(p="instance_of") if "Bird" in ancestors(c)]
print("all instances of Bird:", birds)
```

Output:

```text
classes of penguin_17: Penguin -> Bird -> Animal -> LivingThing
sparrow_3.can_fly = True  (from class Bird)
sparrow_3.breathes = True  (from class Animal)
sparrow_3.has_part = wings (from class Bird)
penguin_17.can_fly = False (from class Penguin)
penguin_17.breathes = True  (from class Animal)
penguin_17.has_part = wings (from class Bird)
all instances of Bird: ['penguin_17', 'sparrow_3']
```

The sparrow inherits `can_fly = True` from Bird and `breathes = True` from Animal, two levels up. The penguin inherits the same facts except flying: the Penguin class overrides the Bird default because the lookup walks from the most specific class upward and stops at the first match. The final query finds every instance of Bird through the transitive closure of `subclass_of`, even though neither individual is directly an instance of Bird. Each fact was stated once yet applies to every relevant individual, which is the main benefit of an ontology.

### Example 2: Modelling a university with RDFS inference

Triples:

```text
(Lecturer, subClassOf, Person)
(Student, subClassOf, Person)
(Course, subClassOf, LearningResource)
(teaches, domain, Lecturer)
(teaches, range, Course)
(dr_rao, teaches, ai_101)
```

From the single fact `(dr_rao, teaches, ai_101)`, RDFS rules infer:

1. The domain of `teaches` is Lecturer, so `(dr_rao, type, Lecturer)`.
2. The range is Course, so `(ai_101, type, Course)`.
3. By `subClassOf`, `(dr_rao, type, Person)` and `(ai_101, type, LearningResource)`.

A SPARQL query for all courses taught by lecturers is

```text
SELECT ?course WHERE { ?person a :Lecturer . ?person :teaches ?course . }
```

which returns `ai_101`. Under the open-world assumption, the lack of a triple stating a prerequisite for ai_101 does not mean it has none: the information is simply unknown.

## Applications

- **Search engines:** knowledge panels draw on knowledge graphs of entities and relations.
- **Healthcare:** SNOMED CT and the Gene Ontology standardise medical and biological terms.
- **E-commerce:** product taxonomies and attributes power filters and recommendations.
- **Data integration:** shared ontologies let systems with different schemas exchange data.
- **AI assistants:** knowledge graphs ground answers and complement retrieval-augmented generation.

## Common mistakes

- **Confusing subclass with instance.** Penguin is a subclass of Bird; penguin_17 is an instance of Penguin.
- **Using is-a for part-of.** A wheel is part of a car, not a kind of car.
- **Applying closed-world reasoning to open-world data.** A missing triple does not make a statement false.
- **Treating defaults as strict rules.** Exceptions must be able to override inherited properties.
- **Over-deep or tangled hierarchies.** Keep classes meaningful and avoid unnecessary multiple inheritance.

## Revision notes

- Ontology: classes, individuals, properties, axioms; upper vs domain ontologies.
- Relations: subclass of (is-a), instance of, part of; disjointness and partitions.
- Semantic networks and frames inherit properties; defaults can be overridden (nonmonotonic).
- Description logics: precise semantics, decidable subsumption and classification.
- RDF triples, RDFS (subClassOf, domain, range), OWL, SPARQL; knowledge graphs.
- Open-world (unknown if unstated) vs closed-world (false if unstated).

## Practice questions

:::question basic
Write triples for "Hyderabad is a city, and it is located in Telangana."
:::answer
`(hyderabad, instance_of, City)` and `(hyderabad, located_in, telangana)`. In RDF, the first is usually written with the `type` predicate: `(hyderabad, rdf:type, City)`.
:::

:::question basic
What is the difference between subclass_of and instance_of?
:::answer
`subclass_of` relates two classes: every member of the first class is a member of the second (Penguin subclass_of Bird). `instance_of` relates an individual to a class it belongs to (penguin_17 instance_of Penguin).
:::

:::question intermediate
Given `(enrolled_in, domain, Student)`, `(enrolled_in, range, Course)`, and `(Student, subClassOf, Person)`, what can be inferred from `(ravi, enrolled_in, cs201)`?
:::answer
From the domain, ravi is a Student; from the subclass link, ravi is a Person; from the range, cs201 is a Course.
:::

:::question intermediate
Why does the rule "birds fly, but penguins do not" make reasoning nonmonotonic?
:::answer
In monotonic logic, adding facts never removes conclusions. Here, knowing only that Pip is a bird lets us conclude that Pip flies; adding the fact that Pip is a penguin withdraws that conclusion. Default reasoning with exceptions therefore needs nonmonotonic inference, such as preferring the most specific class.
:::

:::question advanced
Explain the Nixon diamond and two ways a reasoning system might respond to it.
:::answer
Nixon is both a Quaker (Quakers are typically pacifists) and a Republican (Republicans are typically not pacifists). Neither class is more specific than the other, so specificity cannot resolve the conflict. A skeptical reasoner draws no conclusion about whether Nixon is a pacifist; a credulous reasoner accepts one consistent conclusion (or reports both alternatives). Alternatively, the designer can add explicit priorities between the defaults.
:::

## Further learning

- **Next:** *Propositional Logic & Inference* introduces formal logical reasoning.
- **Related:** *Embeddings & Retrieval-Augmented Generation* in Natural Language Processing shows how retrieved knowledge grounds language models.
