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
| **Coding practice** | 12 interview-style Python problems with a real code editor. Code runs **in the learner's browser** (Pyodide/WebAssembly), never on the server, with a time limit for endless loops. Each problem has tests, a three-step hint ladder and an "Ask the tutor" button that sends the code and first failing test to the Socratic tutor. Progress is saved per learner. See [`content/practice/README.md`](content/practice/README.md). |
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
├── content/     # Curriculum (subjects, syllabi, lessons) and coding-practice problems
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

In development without SMTP settings, sign-up and password-reset codes are printed in the API console, so no email account is needed. To send real emails, see **Email (OTP) setup** below.

Or run the whole stack (PostgreSQL, Redis, API and web app) with Docker:

```bash
docker compose -f docker/docker-compose.dev.yml up --build
```

---

## ✉️ Email (OTP) setup

Sign-up, **Resend code** and **Forgot password** each send a 6-digit code by email. The page then says what actually happened: *sent to your address*, *email isn't set up (the code is in the API terminal)*, or *couldn't send, try Resend in a minute*.

| Situation | What happens |
| :--- | :--- |
| SMTP set | The code is emailed. On startup the API logs `Email: SMTP configured (host:port, from address)`. |
| No SMTP, development | The code is printed in the terminal running the API. |
| No SMTP, `ENVIRONMENT=production` | The API refuses to start. |
| SMTP set but sending fails | The real SMTP error is logged (never the password or the code). Development reports it on the page; production answers `503 EMAIL_DELIVERY_FAILED` and the account stays unverified, so the user can resend later. |

**With Gmail:**

1. Turn on 2-Step Verification: Google Account > Security > 2-Step Verification.
2. Create an App Password: Google Account > Security > 2-Step Verification > App passwords. Copy the 16-character password (it is shown once).
3. Add these lines to `backend/.env` (never commit this file):

   ```bash
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=you@gmail.com
   SMTP_PASSWORD=<the 16-character app password>
   EMAILS_FROM_EMAIL=you@gmail.com
   ```

4. Check it, then restart the API:

   ```bash
   cd backend
   python scripts/send_test_email.py you@gmail.com   # prints "sent", or the exact SMTP error
   ```

Gmail allows about **500 emails a day**. For many users, use a transactional email provider such as [Brevo](https://www.brevo.com), [Resend](https://resend.com) or [SendGrid](https://sendgrid.com): only the `SMTP_*` values change (each provider shows its host, port, login and SMTP key; you'll also verify a sender address or domain with them). Port 465 uses SSL; 587 and 2525 use STARTTLS.

---

## ✅ Tests & Code Quality

```bash
cd backend
pytest -q          # 451 tests; runs on offline AI engines and a throwaway database
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

Production needs `GEMINI_API_KEY` for live AI, and SMTP settings so sign-up and password-reset codes are delivered (the API won't start without them; see **Email (OTP) setup** above).

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
