# LuminaLearn AI

> **Illuminate Every Learning Journey**
> *Project Aurora*

[![CI](https://github.com/Klusaketh/luminalearn/actions/workflows/ci.yml/badge.svg)](https://github.com/Klusaketh/luminalearn/actions/workflows/ci.yml)

LuminaLearn AI is an adaptive learning platform built around a **Socratic AI tutor**: instead of handing over answers, it asks the next right question, explains why it chose that approach, and offers hints one step at a time. It diagnoses each learner's learning style, tracks mastery with **Bayesian Knowledge Tracing**, calibrates quizzes with **Item Response Theory**, and forecasts forgetting so reviews come at the right time.

---

## ✨ Features

| Area | What it does |
| :--- | :--- |
| **Socratic tutor** | A supervisor routes every question to one of four specialists (Socratic Tutor, Concept Explainer, Analogy Specialist, Code Diagnostic). A guardrail screens replies so the final answer is never leaked. "Why this tutor?" shows the routing decision and its confidence. |
| **Learning styles (VARK)** | An onboarding diagnostic finds whether a learner prefers visual, auditory, read/write or hands-on explanations, and the tutor adapts, for example answering with a flowchart for a visual learner. |
| **Grounded answers** | Replies cite the course material they used, retrieved with hybrid search (dense vectors + BM25) over the curriculum. |
| **Code diagnostics** | Pasted Python code is analysed with the `ast` module (missing base cases, repeated subproblems, complexity) and the tutor responds with guiding questions. |
| **Adaptive quizzes** | Questions are calibrated with IRT (2PL). Wrong answers are diagnosed as specific misconceptions, mastery updates live with BKT, and a retention forecast schedules spaced reviews. |
| **Voice** | Talk to the tutor and hear replies (Gemini speech-to-text and text-to-speech over a WebSocket). |
| **Curriculum** | 4 disciplines, 22 subjects, 279 topics, with fully written lessons (theory, worked examples, common mistakes, practice questions). Coverage is tracked in [`docs/SUBJECTS_COVERAGE.md`](docs/SUBJECTS_COVERAGE.md). |
| **Accounts & security** | Email OTP verification, Google sign-in, Argon2id password hashing, short-lived JWT sessions, role-based access, per-learner rate limits. |
| **Keeps working offline** | Every AI specialist has a deterministic offline engine, so tutoring continues with no API key or when every Gemini model is unavailable. |

---

## 🧱 Tech Stack

| Layer | Technology |
| :--- | :--- |
| Frontend | Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, Zustand, TanStack Query, Framer Motion, KaTeX |
| Backend | FastAPI, Python 3.11+, async SQLAlchemy 2 |
| Database | PostgreSQL 16 in production; SQLite for local development |
| Cache | Redis 7, with an in-memory fallback |
| AI | Google Gemini (with a model fallback chain), multi-agent orchestration in [`ai/`](ai/README.md) |
| Learning science | Bayesian Knowledge Tracing, IRT 2PL and retention forecasting in [`ml/`](ml/) |
| Deployment | Docker, Render ([`render.yaml`](render.yaml)), Netlify ([`netlify.toml`](netlify.toml)) |
| Quality | pytest, Ruff, mypy, ESLint, TypeScript strict mode, GitHub Actions |

---

## 🗂️ Repository Layout

```
luminalearn/
├── ai/          # Gemini gateway, Socratic agents, prompts, curriculum RAG
├── backend/     # FastAPI app (app/), tests (tests/), Dockerfile
├── content/     # Curriculum source: subjects, syllabi, overviews and lessons (Markdown)
├── database/    # PostgreSQL schema reference
├── docker/      # Docker Compose stack for local development
├── docs/        # Architecture, standards, research, deployment guide, notes and IEEE paper
├── frontend/    # Next.js web app (src/app pages, components, services, stores)
├── ml/          # Knowledge tracing and retention forecasting models
├── scripts/     # Curriculum seeder, coverage report, dev launcher
├── render.yaml  # Render blueprint: PostgreSQL + backend + frontend
└── netlify.toml # Netlify build for the frontend
```

---

## 🚀 Run It Locally

**Prerequisites:** Node.js 20+, Python 3.11+.

```bash
cp .env.example backend/.env          # then add GEMINI_API_KEY (optional: the tutor runs offline without it)
python -m venv backend/.venv
backend/.venv/bin/pip install -r backend/requirements.txt
(cd frontend && npm ci)
backend/.venv/bin/python scripts/seed_academic_content.py   # load the curriculum into the local database
npm run dev
```

On Windows, use `backend\.venv\Scripts\pip` and `backend\.venv\Scripts\python` in place of the `bin/` paths.

This starts the API on `http://127.0.0.1:8001` and the web app on `http://localhost:3000`. The browser only calls the web app's own `/api/v1`, which the Next.js server forwards to the API, so there is no CORS setup.

In development, sign-up verification codes are printed in the API console, so no email account is needed.

Or run the whole stack (PostgreSQL, Redis, API and web app) with Docker:

```bash
docker compose -f docker/docker-compose.dev.yml up --build
```

---

## ✅ Tests & Code Quality

```bash
cd backend
pytest -q          # 404 tests; runs on offline AI engines and a throwaway database
ruff check .
mypy app

cd ../frontend
npm run lint
npm run typecheck
```

GitHub Actions runs the backend tests and lint, and the frontend lint, type check and build, on every push and pull request.

The lesson tests also run every code example in the curriculum and compare its real output with the output printed in the lesson.

---

## ☁️ Deploy

- **Render (full stack):** New → Blueprint → this repository. Render reads [`render.yaml`](render.yaml) and creates PostgreSQL, the API and the web app. Step-by-step guide: [`docs/DEPLOY_RENDER.md`](docs/DEPLOY_RENDER.md).
- **Netlify (web app only):** import the repository; [`netlify.toml`](netlify.toml) builds the frontend. Set `BACKEND_URL` to the Render API's URL. The live voice session needs WebSockets, which Netlify cannot proxy.

Production needs `GEMINI_API_KEY` for live AI, and SMTP settings so sign-up emails are delivered.

---

## 📚 Documentation

| Document | Contents |
| :--- | :--- |
| [`docs/SYSTEM_ARCHITECTURE.md`](docs/SYSTEM_ARCHITECTURE.md) | Architecture and data flow |
| [`docs/PRODUCT_CHARTER.md`](docs/PRODUCT_CHARTER.md) | Vision, personas and success metrics |
| [`docs/ENGINEERING_STANDARDS.md`](docs/ENGINEERING_STANDARDS.md) | Coding standards |
| [`ai/README.md`](ai/README.md) | The tutor's agents, prompts and retrieval |
| [`content/README.md`](content/README.md) | How to write and publish lessons |
| [`docs/paper/`](docs/paper/) | IEEE technical paper |

---

## 📄 License

Proprietary. © LuminaLearn AI Development Team. All rights reserved.
