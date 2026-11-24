"""
Tutor accuracy suite.

Measures the deterministic parts that decide whether the tutor gives correct, grounded answers:
1. Retrieval: does a learner's question find the lesson that answers it? (top-3 hit rate)
2. Abstention: are off-topic questions refused instead of grounded on an unrelated lesson?
3. Routing: does each question reach the right specialist?

The thresholds are floors that a change must not fall below. Raise them as the tutor improves.
"""

import pytest

from ai.agents.schema import TutorRequest
from ai.agents.supervisor import SupervisorAgent
from ai.rag.curriculum_rag import DOCUMENT_THRESHOLD, CurriculumRAGService

RAG = CurriculumRAGService(documents_dir=None)

# (learner question, words that identify the lesson that should be retrieved)
GROUNDED_QUESTIONS = [
    # Data structures and algorithms
    ("why is appending to a python list O(1) on average even though it sometimes copies everything", ("Amortized Analysis", "Static and Dynamic Arrays")),
    ("what does big O notation actually measure", "Big-O"),
    ("how do I find the middle of a linked list in one pass", "Fast and Slow Pointer"),
    ("check whether brackets in a string are balanced", "Monotonic Stacks and Bracket Matching"),
    ("how does a hash table resolve collisions with chaining or open addressing", "Hash Functions and Collision Handling"),
    ("inorder preorder postorder traversal of a binary tree", "Binary Tree Traversals"),
    ("how do AVL rotations keep a tree balanced", "Balanced Search Trees"),
    ("autocomplete words by prefix using a trie", "Tries and Prefix Search"),
    ("how does heapify build a min heap", "Min and Max Heap"),
    ("adjacency list versus adjacency matrix", "Graph Representations"),
    ("breadth first search visits nodes level by level", ("Breadth-First Search", "Binary Tree Traversals")),  # level order is BFS on a tree
    ("why does dijkstra fail with negative edge weights", "Dijkstra and Bellman-Ford"),
    ("kruskal algorithm with union find for minimum spanning tree", "Minimum Spanning Trees"),
    ("loop invariant for binary search on a sorted array", "Binary Search and Loop Invariants"),
    ("how does quicksort choose a pivot and partition", "Merge Sort and QuickSort"),
    ("solve n queens with backtracking", "Backtracking"),
    ("top down memoization versus bottom up tabulation", "Memoization vs Tabulation"),
    ("0/1 knapsack dynamic programming table", "Knapsack"),
    ("longest substring using a sliding window", "Sliding Window"),
    ("recursion tree for the time of a recursive function", "Call Stack and Recurrence Trees"),
    # Operating systems
    ("what are the four coffman conditions for deadlock", "Deadlock"),
    ("banker's algorithm safe state", "Banker's Algorithm"),
    ("difference between a mutex and a semaphore", "Semaphores"),
    ("round robin versus shortest job first scheduling", "CPU Scheduling"),
    ("what happens on a page fault with demand paging", "Demand Paging"),
    ("LRU versus FIFO page replacement and belady's anomaly", "Page Replacement"),
    ("how does a page table translate a virtual address", "Paging and Page Tables"),
    ("what is stored in a process control block", "Process Control Block"),
    ("how does a system call switch from user mode to kernel mode", "System Calls and Dual-Mode"),
    ("SCAN and C-SCAN disk scheduling", "Disk Scheduling"),
    ("what is an inode", "Inodes"),
    # Databases
    ("what is a functional dependency and third normal form", "Functional Dependencies and Normal Forms"),
    ("left outer join versus inner join", "Joins"),
    ("primary key foreign key referential integrity", "Referential Integrity"),
    ("GROUP BY with HAVING to filter groups", "Grouping"),
    ("map a many to many relationship from an ER diagram to tables", "ER-to-Relational Mapping"),
    # Python
    ("why does a mutable default argument keep its value between calls", "Defining Functions"),
    ("difference between == and is in python", "Python Variables & Data Types"),
    ("what does the else block on a for loop do", "Conditional Branching & Loops"),
    ("LEGB rule for variable scope", "Defining Functions"),
]

OFF_TOPIC_QUESTIONS = [
    "best pizza recipe in naples",
    "who won the football world cup",
    "how to cook rice",
    "what is the capital of france",
    "tell me a joke about cats",
    "recommend a good movie for tonight",
    "what is the weather tomorrow",
    "how do I tie a tie",
]

# (message, expected specialist)
ROUTING_CASES = [
    ("```python\ndef fact(n):\n    return n * fact(n - 1)\n```\nwhy does this crash", "code_diagnostic"),
    ("my code throws IndexError: list index out of range, can you debug it?", "code_diagnostic"),
    ("def search(a, x):\n    for i in range(len(a)):\n        if a[i] == x:\n            return i\nwhy is this slow", "code_diagnostic"),
    ("explain it with an analogy please, recursion confuses me", "analogy_specialist"),
    ("can you give me a real world example or metaphor for a hash table", "analogy_specialist"),
    ("explain what a semaphore is", "concept_explainer"),
    ("what is the difference between a process and a thread", "concept_explainer"),
    ("I'm stuck solving this problem: find two numbers that add up to a target", "socratic_tutor"),
    ("how do I solve 2x + 3 = 11", "socratic_tutor"),
    ("just give me the answer to this question", "socratic_tutor"),
    ("Which enzyme fixes carbon dioxide in the Calvin cycle?", "concept_explainer"),
    ("who proposed the relational model of data", "concept_explainer"),
    ("when should I use a linked list instead of an array", "concept_explainer"),
    ("what is the value of x if 2x + 3 = 11", "socratic_tutor"),
    ("which answer is correct for my homework question 3", "socratic_tutor"),
]


def _hit(question: str, expected: str | tuple[str, ...]) -> bool:
    accepted = (expected,) if isinstance(expected, str) else expected
    titles = [chunk.source_title.lower() for chunk in RAG.retrieve(question, top_k=3, threshold=0.2)]
    return any(want.lower() in title for want in accepted for title in titles)


def test_retrieval_finds_the_right_lesson():
    misses = [(q, expected) for q, expected in GROUNDED_QUESTIONS if not _hit(q, expected)]
    hit_rate = 1 - len(misses) / len(GROUNDED_QUESTIONS)
    assert hit_rate >= 0.95, f"top-3 hit rate {hit_rate:.0%}; misses: {misses}"


@pytest.mark.parametrize("question", OFF_TOPIC_QUESTIONS)
def test_off_topic_questions_are_not_grounded(question):
    assert RAG.retrieve(question) == [], "an unrelated lesson must not be cited as evidence"


def test_routing_accuracy():
    supervisor = SupervisorAgent()
    wrong = [
        (message.splitlines()[-1][:60], expected, decision.agent)
        for message, expected in ROUTING_CASES
        if (decision := supervisor.route(TutorRequest(message=message))).agent != expected
    ]
    accuracy = 1 - len(wrong) / len(ROUTING_CASES)
    assert accuracy >= 0.93, f"routing accuracy {accuracy:.0%}; wrong: {wrong}"


def test_uploaded_document_index_cites_pages():
    index = CurriculumRAGService.from_pages(
        title="lecture-notes.pdf",
        pages=[
            (1, "Photosynthesis converts light energy into chemical energy stored in glucose inside the chloroplast. " * 3),
            (2, "The Krebs cycle runs in the mitochondrial matrix and produces NADH and FADH2 for the electron transport chain. " * 3),
        ],
    )
    top = index.retrieve("where does the krebs cycle happen", top_k=1, threshold=DOCUMENT_THRESHOLD)
    assert top and top[0].page == 2 and top[0].source_title == "lecture-notes.pdf"
    assert "p. 2" in top[0].citation


# (language, code, expected time complexity from loop nesting)
COMPLEXITY_CASES = [
    ("javascript", "function f(a, t) {\n  for (let i = 0; i < a.length; i++)\n    for (let j = 0; j < a.length; j++)\n      if (a[i] + a[j] === t) return [i, j];\n}", "O(n^2)"),
    ("c", "int f(int n) {\n  int s = 0;\n  for (int i = 0; i < n; i++) {\n    for (int j = 0; j < n; j++) {\n      s += i * j;\n    }\n  }\n  return s;\n}", "O(n^2)"),
    ("java", "int f(int[] a) { int s = 0; for (int x : a) s += x; for (int x : a) s -= x; return s; }", "O(n)"),
    ("javascript", "function f(a) { if (a) { return 1; } return a[0]; }", "O(1)"),
    ("javascript", "function f(m) { let s = 0; m.forEach((row) => { row.forEach((x) => { s += x; }); }); return s; }", "O(n^2)"),
    ("javascript", "function f(a) { const b = a.map((x) => x * 2); if (b) { return b; } }", "O(n)"),
    ("c", "int f(int n) { int c = 0; do { c++; } while (c < n); return c; }", "O(n)"),
    ("java", "void f(int n) { for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) for (int k = 0; k < n; k++) g(); }", "O(n^3)"),
    ("python", "def f(a):\n    for x in a:\n        for y in a:\n            print(x, y)", "O(n^2)"),
]


@pytest.mark.parametrize(("language", "code", "expected"), COMPLEXITY_CASES)
def test_code_analysis_estimates_loop_complexity(language, code, expected):
    from ai.agents.code_diagnostic import analyze_code

    analysis = analyze_code(f"```{language}\n{code}\n```")
    assert analysis.time_complexity == expected
    assert not any(f.title == "Unbalanced brackets" for f in analysis.findings)
