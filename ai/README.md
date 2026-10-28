# LuminaLearn AI — Socratic Agent & AI Framework

The `ai/` package holds everything the platform needs to tutor: the Gemini gateway, the
multi-agent Socratic faculty, versioned prompts, and curriculum retrieval. The backend imports it
directly (`app/services/ai_runtime.py` is the composition root).

## Layout

| Path | What it does |
| :--- | :--- |
| `llm/gemini_gateway.py` | Every Gemini call (chat streams, quiz JSON, speech-to-text, text-to-speech). Ordered model fallback, per-model circuit breaker, hard deadlines, offline switch. |
| `agents/supervisor.py` | Routes each learner turn to one specialist using intent signals, BKT mastery and VARK modality, and explains why. |
| `agents/socratic_tutor.py` | Never gives the final answer. Three-tier hint ladder: nudge, scaffold, parallel worked example. |
| `agents/concept_explainer.py` | Explains in the learner's modality: Mermaid diagram, narration, structured notes, or a hands-on lab. |
| `agents/analogy_specialist.py` | Everyday analogies with an explicit "where it breaks" note. |
| `agents/code_diagnostic.py` | `ast`-based static analysis (bugs, base cases, Big-O) framed as guiding questions. |
| `agents/guardrails.py` | Streaming answer-leak screen and the `[[HINTS]]` splitter. |
| `agents/orchestrator.py` | The graph: ground → route → specialist → guardrail → finalize, emitted as typed events. |
| `prompts/templates.py` | Versioned system prompts. Bump `PROMPT_VERSION` whenever one changes. |
| `rag/curriculum_rag.py` | Hybrid retrieval (hashed dense vectors + BM25) with citations and an abstention threshold. |

Every specialist has two engines: a Gemini prompt and a deterministic `offline()` answer. The
faculty therefore keeps teaching when there is no API key, the key is rejected, or every model is
overloaded. The test suite runs entirely on the offline engines (`LLM_OFFLINE_MODE=true`).

## Adding course material for grounded answers

Drop Markdown (`.md`) or text (`.txt`) files into `ai/rag/documents/`. They are chunked and
indexed when the backend starts; restart it after adding files. Files whose names start with
`README` or `_` are ignored.

Optional front matter sets provenance for the citations the tutor shows:

```markdown
---
topic: Recursion
subject: Computer Science
source: CS101 Lecture Notes, Week 4
---

## Base cases
Every recursive function needs ...

## The call stack
Each pending call ...
```

- `topic` scopes retrieval and appears in the tutor's context.
- `source` is the citation title learners see. Without it, the file name is used.
- Each `## Heading` becomes the citation section. Long sections are split into overlapping
  windows of about 110 words.

Write material you are allowed to redistribute to learners: retrieved passages are quoted to the
model and cited in replies.
