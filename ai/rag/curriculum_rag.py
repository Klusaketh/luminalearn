"""
LuminaLearn AI — Curriculum Retrieval Augmented Generation (Curriculum RAG).
Module: ai/rag/curriculum_rag.py

Provides hybrid (dense + BM25), provenance-grounded curriculum retrieval.
Includes strict abstention thresholds to prevent AI hallucinations, verifiable citations,
and resilient offline embeddings that need no external service.

Course material can be added without code changes: drop Markdown or text files into
`ai/rag/documents/` (see ai/README.md for the front-matter format).
"""

import hashlib
import json
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

DOCUMENTS_DIR = Path(__file__).resolve().parent / "documents"
# The written curriculum (content/subjects/<slug>/overview.md and lessons/*.md). In the Docker image this
# resolves to /srv/content/subjects, which the backend Dockerfile copies.
CONTENT_SUBJECTS_DIR = Path(__file__).resolve().parents[2] / "content" / "subjects"
# Uploaded documents are small corpora with weak term statistics, so they use a lower relevance floor.
DOCUMENT_THRESHOLD = 0.15
WINDOW_WORDS = 110
WINDOW_OVERLAP = 15
_FRONT_MATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_QUESTION_MARKERS = re.compile(r"^:::\s*(?:question\s+\w+|answer)?\s*$", re.MULTILINE)
_MARKUP = re.compile(r"[#*`>|]")

_STOPWORDS = frozenset(
    "a an and are as at be by can do does for from has have how i if in into is it its me my "
    "of on or so that the their then there these this to was we what when where which why "
    "will with you your about please explain tell show give help even though sometimes everything also "
    "just really actually get got thing things lot want know mean".split()
)
_TOKEN_PATTERN = re.compile(r"[a-z][a-z0-9]+")


def _stem(token: str) -> str:
    """Harman S-stemmer: folds plurals so "eigenvalues" and "eigenvalue" share one term."""
    if len(token) <= 3:
        return token
    if token.endswith("ies") and not token.endswith(("eies", "aies")):
        return token[:-3] + "y"
    if token.endswith("es") and not token.endswith(("aes", "ees", "oes")):
        return token[:-1]
    if token.endswith("s") and not token.endswith(("us", "ss")):
        return token[:-1]
    # Light verb folding so "appending"/"append" and "visited"/"visit" share a term. A stem shorter than
    # four letters is kept whole ("string" stays "string", "need" stays "need").
    if token.endswith("ing") and len(token) - 3 >= 4:
        return token[:-3]
    if token.endswith("ed") and len(token) - 2 >= 4 and not token.endswith("eed"):
        return token[:-2]
    return token


def tokenize(text: str) -> list[str]:
    """Lowercased, stop-word filtered, stemmed terms."""
    return [_stem(t) for t in _TOKEN_PATTERN.findall(text.lower()) if t not in _STOPWORDS]


def _stable_hash(value: str) -> int:
    return int.from_bytes(hashlib.blake2b(value.encode("utf-8"), digest_size=8).digest(), "big")


@dataclass
class CurriculumChunk:
    """A vetted curriculum knowledge chunk with full source provenance."""
    id: str
    topic: str
    subject: str
    source_title: str
    section: str
    page: int | None
    content: str
    score: float = 0.0
    embedding: list[float] = field(default_factory=list)

    @property
    def citation(self) -> str:
        """Standardized academic citation format."""
        pg = f", p. {self.page}" if self.page else ""
        return f"[{self.source_title}, {self.section}{pg}]"


class CurriculumRAGService:
    """
    Curriculum-grounded retrieval engine.
    Combines signed feature-hashing dense vectors with Okapi BM25 term weighting,
    provenance citation, and threshold-based abstention policies.
    """

    RELEVANCE_THRESHOLD = 0.30
    DENSE_DIM = 512
    DENSE_WEIGHT = 0.55
    BM25_K1 = 1.5
    BM25_B = 0.75
    BM25_SATURATION = 4.0

    def __init__(
        self,
        documents_dir: Path | None = DOCUMENTS_DIR,
        lessons_dir: Path | None = CONTENT_SUBJECTS_DIR,
        include_seed: bool = True,
    ) -> None:
        self.chunks: list[CurriculumChunk] = []
        if include_seed:
            self._load_vetted_curriculum()
        if documents_dir is not None:
            self._load_documents(documents_dir)
        if lessons_dir is not None:
            self._load_lessons(lessons_dir)
        self._index_chunks()

    @classmethod
    def from_pages(cls, *, title: str, pages: list[tuple[int, str]], subject: str = "Your documents") -> "CurriculumRAGService":
        """An index over one uploaded document, one or more windows per page, citing the page number."""
        index = cls(documents_dir=None, lessons_dir=None, include_seed=False)
        for page, text in pages:
            index._add_windows(topic=title, subject=subject, source_title=title, section="Uploaded document", page=page, text=text)
        index._index_chunks()
        return index

    # ------------------------------------------------------------------ indexing

    def _generate_dense_vector(self, text: str, dim: int | None = None) -> list[float]:
        """
        Generates a deterministic L2-normalized dense vector via signed feature hashing
        of unigram and bigram terms (resilient offline embeddings).
        """
        size = dim or self.DENSE_DIM
        vec = [0.0] * size
        terms = tokenize(text)
        if not terms:
            return vec
        features = terms + [f"{a}_{b}" for a, b in zip(terms, terms[1:], strict=False)]
        for feature in features:
            h = _stable_hash(feature)
            vec[h % size] += 1.0 if (h >> 32) & 1 == 0 else -1.0
        norm = math.sqrt(sum(x * x for x in vec))
        return [x / norm for x in vec] if norm > 1e-12 else vec

    def _cosine_similarity(self, v1: list[float], v2: list[float]) -> float:
        """Computes cosine similarity between two unit vectors, clipped to [0, 1]."""
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2, strict=True))
        return max(0.0, min(1.0, dot))

    def _index_chunks(self) -> None:
        """Computes dense vectors and BM25 statistics for all loaded curriculum chunks."""
        self._chunk_terms: list[Counter[str]] = []
        self._title_terms: list[frozenset[str]] = []
        document_frequency: Counter[str] = Counter()
        for chunk in self.chunks:
            combined = f"{chunk.topic} {chunk.subject} {chunk.section} {chunk.content}"
            chunk.embedding = self._generate_dense_vector(combined)
            terms = Counter(tokenize(combined))
            self._chunk_terms.append(terms)
            self._title_terms.append(frozenset(tokenize(f"{chunk.topic} {chunk.section}")))
            document_frequency.update(terms.keys())
        total = len(self.chunks) or 1
        self._idf = {
            term: math.log(1.0 + (total - df + 0.5) / (df + 0.5)) for term, df in document_frequency.items()
        }
        lengths = [sum(t.values()) for t in self._chunk_terms]
        self._avg_length = (sum(lengths) / len(lengths)) if lengths else 1.0

    def _bm25(self, query_terms: list[str], index: int) -> float:
        terms = self._chunk_terms[index]
        length = sum(terms.values()) or 1
        score = 0.0
        for term in set(query_terms):
            tf = terms.get(term, 0)
            if not tf:
                continue
            idf = self._idf.get(term, 0.0)
            norm = tf + self.BM25_K1 * (1 - self.BM25_B + self.BM25_B * length / self._avg_length)
            score += idf * (tf * (self.BM25_K1 + 1)) / norm
        return score

    # ------------------------------------------------------------------ retrieval

    def retrieve(
        self,
        query: str,
        topic: str | None = None,
        top_k: int = 3,
        threshold: float | None = None
    ) -> list[CurriculumChunk]:
        """
        Retrieves top-k relevant curriculum chunks matching the student's query.
        Hybrid score = 0.55 * dense cosine + 0.45 * saturated BM25.
        When `topic` is given, only chunks whose topic overlaps it are considered.
        """
        min_thresh = threshold if threshold is not None else self.RELEVANCE_THRESHOLD
        query_vec = self._generate_dense_vector(query)
        query_terms = tokenize(query)
        unique_terms = set(query_terms)
        candidates: list[CurriculumChunk] = []

        norm_topic = topic.strip().lower() if topic else None

        for index, chunk in enumerate(self.chunks):
            if norm_topic and norm_topic not in chunk.topic.lower() and chunk.topic.lower() not in norm_topic:
                continue

            matched = [term for term in unique_terms if self._chunk_terms[index].get(term)]
            # One matching word only counts when the chunk is about it (the word is in its lesson title or
            # section): "semaphore" grounds the Semaphores lesson, "tie" in "tie a tie" grounds nothing.
            if len(matched) == 1 and matched[0] not in self._title_terms[index]:
                continue
            dense_sim = self._cosine_similarity(query_vec, chunk.embedding)
            bm25 = self._bm25(query_terms, index)
            # Weight keyword evidence by how much of the question the chunk covers: in a large corpus a
            # single rare word ("capital", "best") must not ground an unrelated question.
            coverage = len(matched) / len(unique_terms) if unique_terms else 0.0
            sparse_sim = bm25 / (bm25 + self.BM25_SATURATION) * coverage
            hybrid_score = round(self.DENSE_WEIGHT * dense_sim + (1 - self.DENSE_WEIGHT) * sparse_sim, 4)

            if hybrid_score >= min_thresh:
                candidates.append(
                    CurriculumChunk(
                        id=chunk.id,
                        topic=chunk.topic,
                        subject=chunk.subject,
                        source_title=chunk.source_title,
                        section=chunk.section,
                        page=chunk.page,
                        content=chunk.content,
                        score=hybrid_score,
                        embedding=chunk.embedding,
                    )
                )

        candidates.sort(key=lambda c: c.score, reverse=True)
        return candidates[:top_k]

    def has_sufficient_grounding(
        self,
        chunks: list[CurriculumChunk],
        threshold: float | None = None
    ) -> bool:
        """
        Abstention Gate: Checks whether retrieved evidence meets the grounding threshold.
        Returns False if chunks are empty or top score is below threshold.
        """
        thresh = threshold if threshold is not None else self.RELEVANCE_THRESHOLD
        if not chunks:
            return False
        return chunks[0].score >= thresh

    def format_grounded_context(self, chunks: list[CurriculumChunk]) -> str:
        """
        Formats retrieved curriculum chunks with explicit provenance markers for LLM prompts.
        """
        if not chunks:
            return "No verified curriculum material found for this specific query."

        lines = ["=== VERIFIED CURRICULUM CONTEXT ==="]
        for idx, chunk in enumerate(chunks, 1):
            lines.append(
                f"[Source {idx}] {chunk.citation} (Relevance: {int(chunk.score * 100)}%):\n"
                f"{chunk.content}\n"
            )
        lines.append("=== INSTRUCTION: Ground your answer strictly on the facts above with citations ===")
        return "\n".join(lines)

    # ------------------------------------------------------------------ corpus

    def _add_chunk(self, *, topic: str, subject: str, source_title: str, section: str, page: int | None, content: str) -> None:
        chunk_id = hashlib.blake2b(f"{source_title}_{section}_{content[:64]}".encode(), digest_size=6).hexdigest()
        self.chunks.append(
            CurriculumChunk(
                id=chunk_id,
                topic=topic,
                subject=subject,
                source_title=source_title,
                section=section,
                page=page,
                content=" ".join(content.split()),
            )
        )

    def _add_windows(self, *, topic: str, subject: str, source_title: str, section: str, page: int | None, text: str) -> None:
        """Adds overlapping ~110-word windows of `text` as chunks (short fragments are skipped)."""
        words = _MARKUP.sub(" ", _QUESTION_MARKERS.sub(" ", text)).split()
        for start in range(0, len(words), WINDOW_WORDS):
            window = words[max(0, start - WINDOW_OVERLAP): start + WINDOW_WORDS]
            if len(window) >= 12:
                self._add_chunk(topic=topic, subject=subject, source_title=source_title, section=section, page=page, content=" ".join(window))

    def _load_lessons(self, directory: Path) -> None:
        """
        Ingests the written curriculum: each subject's overview and every lesson, one chunk group per
        `## Section`, cited as the lesson title and section so learners can open the lesson.
        """
        if not directory.is_dir():
            return
        for subject_dir in sorted(p for p in directory.iterdir() if p.is_dir()):
            subject = subject_dir.name.replace("-", " ").title()
            syllabus = subject_dir / "syllabus.json"
            if syllabus.is_file():
                try:
                    subject = json.loads(syllabus.read_text(encoding="utf-8")).get("name", subject)
                except (ValueError, OSError):
                    pass
            files: list[tuple[Path, str | None]] = [(subject_dir / "overview.md", f"{subject} (subject overview)")]
            files += [(path, None) for path in sorted((subject_dir / "lessons").glob("*.md"))]
            for path, fixed_title in files:
                if not path.is_file():
                    continue
                raw = path.read_text(encoding="utf-8", errors="replace")
                body = raw
                title: str | None = fixed_title
                front = _FRONT_MATTER.match(raw)
                if front:
                    body = raw[front.end():]
                    match = re.search(r"^title:\s*(.+)$", front.group(1), re.MULTILINE)
                    title = title or (match.group(1).strip().strip("\"'") if match else None)
                lesson_title = title or path.stem.replace("-", " ").title()
                sections = re.split(r"^##\s+(.+)$", body, flags=re.MULTILINE)
                pairs = [("Introduction", sections[0])] + list(zip(sections[1::2], sections[2::2], strict=False))
                for heading, text in pairs:
                    self._add_windows(
                        topic=lesson_title, subject=subject, source_title=f"LuminaLearn lesson: {lesson_title}",
                        section=heading.strip(), page=None, text=text,
                    )

    def _load_documents(self, directory: Path) -> None:
        """
        Ingests `*.md` / `*.txt` course notes. Optional front matter sets `topic`, `subject`
        and `source`; each `## Heading` becomes a section, long sections are windowed.
        """
        if not directory.is_dir():
            return
        for path in sorted(directory.iterdir()):
            if path.suffix.lower() not in {".md", ".txt"} or path.name.lower().startswith(("readme", "_")):
                continue
            raw = path.read_text(encoding="utf-8", errors="replace")
            meta: dict[str, str] = {}
            body = raw
            front = re.match(r"^---\s*\n(.*?)\n---\s*\n", raw, re.DOTALL)
            if front:
                body = raw[front.end():]
                for line in front.group(1).splitlines():
                    key, _, value = line.partition(":")
                    if value.strip():
                        meta[key.strip().lower()] = value.strip()
            topic = meta.get("topic", path.stem.replace("_", " ").title())
            subject = meta.get("subject", "Course Notes")
            source = meta.get("source", f"LuminaLearn Course Notes: {topic}")

            sections = re.split(r"^##\s+(.+)$", body, flags=re.MULTILINE)
            # re.split yields [preamble, heading1, text1, heading2, text2, ...]
            pairs = [("Overview", sections[0])] + list(zip(sections[1::2], sections[2::2], strict=False))
            for heading, text in pairs:
                words = re.sub(r"[#*`>]", " ", text).split()
                for start in range(0, len(words), 110):
                    window = words[max(0, start - 15): start + 110]
                    if len(window) >= 12:
                        self._add_chunk(
                            topic=topic, subject=subject, source_title=source,
                            section=heading.strip(), page=None, content=" ".join(window),
                        )

    def _load_vetted_curriculum(self) -> None:
        """Seeds the internal store with peer-reviewed curriculum knowledge across core STEM subjects."""
        seeds: list[dict[str, str | int | None]] = [
            # Calculus
            {
                "topic": "Calculus",
                "subject": "Mathematics",
                "source_title": "Calculus: Early Transcendentals",
                "section": "Sec 4.3 - The Fundamental Theorem of Calculus",
                "page": 298,
                "content": (
                    "The Fundamental Theorem of Calculus (FTC) bridges differential and integral calculus. "
                    "Part 1 states that if f is continuous on [a, b], then g(x) = int_a^x f(t) dt is continuous on [a, b], "
                    "differentiable on (a, b), and g'(x) = f(x). "
                    "Part 2 states that int_a^b f(x) dx = F(b) - F(a), where F is any antiderivative of f such that F'(x) = f(x). "
                    "To evaluate a definite integral, find an antiderivative term by term, then subtract its value at the lower limit from its value at the upper limit."
                )
            },
            {
                "topic": "Calculus",
                "subject": "Mathematics",
                "source_title": "Calculus: Early Transcendentals",
                "section": "Sec 3.1 - Derivatives of Polynomials and Exponential Functions",
                "page": 174,
                "content": (
                    "The power rule states that d/dx [x^n] = n * x^(n-1) for any real number n. "
                    "The derivative of the natural exponential function f(x) = e^x satisfies d/dx [e^x] = e^x. "
                    "The product rule states that d/dx [u(x)v(x)] = u'(x)v(x) + u(x)v'(x). "
                    "The quotient rule states that d/dx [u(x)/v(x)] = (u'(x)v(x) - u(x)v'(x)) / [v(x)]^2."
                )
            },
            {
                "topic": "Calculus",
                "subject": "Mathematics",
                "source_title": "Calculus: Early Transcendentals",
                "section": "Sec 3.4 - The Chain Rule",
                "page": None,
                "content": (
                    "The chain rule differentiates a composition of functions. If y = f(g(x)), then dy/dx = f'(g(x)) * g'(x): "
                    "differentiate the outer function evaluated at the inner function, then multiply by the derivative of the inner function. "
                    "In Leibniz notation, if y = f(u) and u = g(x), then dy/dx = (dy/du)(du/dx)."
                )
            },
            # Linear Algebra
            {
                "topic": "Linear Algebra",
                "subject": "Mathematics",
                "source_title": "Linear Algebra and Its Applications",
                "section": "Sec 5.1 - Eigenvectors and Eigenvalues",
                "page": 269,
                "content": (
                    "An eigenvector of an n x n matrix A is a nonzero vector x such that Ax = lambda * x "
                    "for some scalar lambda called the eigenvalue. "
                    "To find eigenvalues, we solve the characteristic equation det(A - lambda * I) = 0. "
                    "The roots of this characteristic polynomial are the eigenvalues of matrix A. "
                    "The corresponding eigenspace is the null space of (A - lambda * I)."
                )
            },
            {
                "topic": "Linear Algebra",
                "subject": "Mathematics",
                "source_title": "Linear Algebra and Its Applications",
                "section": "Sec 6.2 - Orthogonal Sets and Gram-Schmidt",
                "page": 344,
                "content": (
                    "A set of vectors {u_1, ..., u_p} in R^n is said to be an orthogonal set if each pair of distinct vectors "
                    "is orthogonal, meaning u_i . u_j = 0 whenever i != j. "
                    "An orthonormal set is an orthogonal set of unit vectors where ||u_i|| = 1. "
                    "The Gram-Schmidt process algorithmically produces an orthogonal basis from any linearly independent set."
                )
            },
            {
                "topic": "Linear Algebra",
                "subject": "Mathematics",
                "source_title": "Linear Algebra and Its Applications",
                "section": "Sec 1.8 - Introduction to Linear Transformations",
                "page": None,
                "content": (
                    "A transformation T from R^n to R^m is linear if T(u + v) = T(u) + T(v) and T(cu) = cT(u) for all vectors u, v and scalars c. "
                    "Every linear transformation can be represented by a matrix A so that T(x) = Ax. "
                    "Linear transformations map lines to lines and keep the origin fixed; rotations, reflections, shears and scalings are examples."
                )
            },
            # Algorithms & Data Structures
            {
                "topic": "Algorithms",
                "subject": "Computer Science",
                "source_title": "Introduction to Algorithms (CLRS)",
                "section": "Ch 3 - Growth of Functions & Asymptotics",
                "page": 44,
                "content": (
                    "Asymptotic notation describes the limiting behavior of an algorithm's running time as input size n grows. "
                    "Big-O notation O(g(n)) denotes an asymptotic upper bound: f(n) <= c * g(n) for all n >= n_0. "
                    "Big-Omega notation Omega(g(n)) denotes an asymptotic lower bound: f(n) >= c * g(n). "
                    "Big-Theta notation Theta(g(n)) denotes an asymptotically tight bound, holding when f(n) is both O(g(n)) and Omega(g(n))."
                )
            },
            {
                "topic": "Algorithms",
                "subject": "Computer Science",
                "source_title": "Introduction to Algorithms (CLRS)",
                "section": "Ch 22 - Elementary Graph Algorithms (BFS and DFS)",
                "page": 594,
                "content": (
                    "Breadth-First Search (BFS) explores all vertices at distance k before exploring vertices at distance k+1. "
                    "BFS utilizes a FIFO queue and computes shortest path distances in unweighted graphs in O(V + E) time. "
                    "Depth-First Search (DFS) explores as deep as possible along each branch before backtracking, "
                    "using a LIFO stack or recursive call stack, producing discovery and finishing timestamps in O(V + E) time."
                )
            },
            {
                "topic": "Algorithms",
                "subject": "Computer Science",
                "source_title": "Introduction to Algorithms (CLRS)",
                "section": "Ch 24 - Single-Source Shortest Paths (Dijkstra's Algorithm)",
                "page": None,
                "content": (
                    "Dijkstra's algorithm solves the single-source shortest-paths problem on a weighted graph with nonnegative edge weights. "
                    "It maintains a set of vertices whose final shortest-path distance is known and repeatedly selects the unvisited vertex "
                    "with the minimum tentative distance, then relaxes each outgoing edge: if d[u] + w(u, v) < d[v], update d[v]. "
                    "With a binary min-priority queue it runs in O((V + E) log V) time."
                )
            },
            {
                "topic": "Algorithms",
                "subject": "Computer Science",
                "source_title": "Introduction to Algorithms (CLRS)",
                "section": "Ch 15 - Dynamic Programming",
                "page": None,
                "content": (
                    "Dynamic programming applies when a problem has optimal substructure and overlapping subproblems. "
                    "Instead of recomputing the same subproblem repeatedly, a dynamic program solves each subproblem once and stores the answer, "
                    "either top-down with memoization or bottom-up by filling a table in order of increasing subproblem size."
                )
            },
            {
                "topic": "Data Structures",
                "subject": "Computer Science",
                "source_title": "Introduction to Algorithms (CLRS)",
                "section": "Ch 11 - Hash Tables",
                "page": None,
                "content": (
                    "A hash table stores key-value pairs in an array indexed by a hash function h(k). "
                    "Collisions, where two keys hash to the same slot, are resolved by chaining or open addressing. "
                    "With a good hash function and a bounded load factor, search, insertion and deletion take O(1) expected time; "
                    "the worst case degrades to O(n) when many keys collide."
                )
            },
            {
                "topic": "Recursion",
                "subject": "Computer Science",
                "source_title": "Structure and Interpretation of Computer Programs",
                "section": "Sec 1.2 - Procedures and the Processes They Generate",
                "page": None,
                "content": (
                    "A recursive procedure is defined in terms of itself. Every correct recursion needs a base case that is answered directly "
                    "and a recursive case that reduces the problem toward the base case. A linear recursive process such as factorial builds "
                    "a chain of deferred operations on the call stack, which unwinds as each call returns. Tree recursion, as in a naive "
                    "Fibonacci, recomputes the same subproblems and grows exponentially in time."
                )
            },
            # Probability & Statistics
            {
                "topic": "Probability",
                "subject": "Statistics",
                "source_title": "Introduction to Probability (Bertsekas & Tsitsiklis)",
                "section": "Sec 1.4 - Total Probability Theorem and Bayes' Rule",
                "page": 32,
                "content": (
                    "Bayes' Rule relates conditional and marginal probabilities of stochastic events: "
                    "P(A|B) = [P(B|A) * P(A)] / P(B). "
                    "The Total Probability Theorem expands the denominator: P(B) = sum_i [P(B|A_i) * P(A_i)] for a partition {A_i}. "
                    "P(A) is termed the prior probability, P(B|A) the likelihood, P(B) the evidence, and P(A|B) the posterior probability."
                )
            },
            # Machine Learning
            {
                "topic": "Machine Learning",
                "subject": "Artificial Intelligence",
                "source_title": "Deep Learning (Goodfellow, Bengio, Courville)",
                "section": "Sec 4.3 - Gradient-Based Optimization",
                "page": 80,
                "content": (
                    "Gradient descent is an iterative optimization algorithm that minimizes an objective function f(x) "
                    "by taking steps proportional to the negative of the gradient: x_{t+1} = x_t - eta * grad f(x_t), "
                    "where eta is the positive scalar learning rate. "
                    "Stochastic Gradient Descent (SGD) approximates the full gradient using a randomly sampled mini-batch of examples, "
                    "drastically reducing per-step computational complexity from O(N) to O(B)."
                )
            },
            {
                "topic": "Machine Learning",
                "subject": "Artificial Intelligence",
                "source_title": "Deep Learning (Goodfellow, Bengio, Courville)",
                "section": "Sec 6.5 - Back-Propagation and Other Differentiation Algorithms",
                "page": None,
                "content": (
                    "Back-propagation computes the gradient of a scalar loss with respect to every parameter of a neural network by applying "
                    "the chain rule backward through the computational graph, reusing intermediate results so the cost is comparable to the "
                    "forward pass. The resulting gradients are then used by an optimizer such as stochastic gradient descent."
                )
            },
            {
                "topic": "Operating Systems",
                "subject": "Computer Science",
                "source_title": "Operating System Concepts (Silberschatz)",
                "section": "Ch 6 - Synchronization Tools & Deadlocks",
                "page": 260,
                "content": (
                    "A race condition occurs when several processes access and manipulate the same shared data concurrently "
                    "and the outcome of the execution depends on the particular order in which access takes place. "
                    "The Critical Section Problem requires Mutual Exclusion, Progress, and Bounded Waiting. "
                    "Deadlock occurs when four Coffman conditions hold simultaneously: Mutual Exclusion, Hold and Wait, "
                    "No Preemption, and Circular Wait."
                )
            },
            {
                "topic": "Operating Systems",
                "subject": "Computer Science",
                "source_title": "Operating System Concepts (Silberschatz)",
                "section": "Sec 6.5 - Mutex Locks",
                "page": None,
                "content": (
                    "A mutex lock protects a critical section: a process must acquire() the lock before entering and release() it on exit. "
                    "Only one process can hold the lock at a time, so other processes attempting to acquire it block or spin until it is released. "
                    "Holding locks for short periods and always acquiring multiple locks in a consistent order helps avoid contention and deadlock."
                )
            },
        ]

        for s in seeds:
            self._add_chunk(
                topic=str(s["topic"]),
                subject=str(s["subject"]),
                source_title=str(s["source_title"]),
                section=str(s["section"]),
                page=s["page"] if isinstance(s["page"], int) else None,
                content=str(s["content"]),
            )


# Global Instantiated Curriculum RAG Singleton
curriculum_rag = CurriculumRAGService()
