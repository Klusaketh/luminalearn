# 📘 LuminaLearn AI (Project Aurora) — Master Project Information & Status Report

> **Generated**: October 2026  
> **Status**: Production Monorepo Active | 59/59 Passing Automated Tests (100%)  
> **Architecture**: FastAPI Microservices + Next.js 14 App Router + Resilient Dual-Engine Fallback  

---

## 1. Executive Summary & Vision

**LuminaLearn AI** (*Project Aurora*) is an enterprise-grade, AI-first adaptive learning ecosystem designed to revolutionize online education. 

### The Problem
Traditional Learning Management Systems (LMS) such as Coursera or Udemy deliver static, linear video courses. They treat all learners identically, regardless of aptitude, pace, or background. Students get stuck, experience cognitive overload, or lose engagement.

### The Solution
LuminaLearn AI continuously diagnoses each learner's cognitive pace, conceptual gaps, and preferred **VARK learning modality** (Visual, Auditory, Read/Write, Kinesthetic) to construct a **100% personalized learning trajectory**.

### Core Pillars
1. **Socratic AI Agent Framework**: Never gives away direct answers. Guides learners through scaffolded step-by-step questioning, hint ladders, and conceptual self-discovery.
2. **Cognitive Personalization (VARK Adapters)**: Dynamically calibrates content presentation (visual diagrams, audio summaries, structured text breakdowns, or interactive simulations).
3. **Resilient Hybrid Infrastructure**: Engineered with zero-downtime local fallback mechanisms (SQLite + In-Memory Caching) alongside enterprise PostgreSQL + Redis.
4. **Universal Accessibility (WCAG 2.1 AAA)**: Native architecture designed for screen readers, high-contrast modes, dyslexia-friendly typography, and multi-modal speech interfaces.
5. **Explainable AI (XAI) & Learning Analytics**: Transparent student mastery mapping, decay curves (Ebbinghaus spacing effect), and retention forecasts for students, parents, and educators.

---

## 2. Complete Technology Stack Specification

| Subsystem | Technology | Version / Spec | Purpose & Architectural Role |
| :--- | :--- | :---: | :--- |
| **Frontend Framework** | **Next.js (App Router)** | `14.2+` (React 18) | Server Components, hybrid SSR/CSR routing, layout nesting |
| **Frontend Language** | **TypeScript** | `5.4+` | Strict static typing, zero runtime type errors |
| **Styling & System** | **Tailwind CSS + Lucide** | `3.4+` | Apple/Linear-inspired dark glassmorphism, responsive CSS variables |
| **Client State** | **Zustand** | `4.5+` | Lightweight global reactive store for auth sessions & learner profile |
| **Math & Code Rendering** | **KaTeX & Prism** | Latest | Mathematical formula rendering and code syntax highlighting |
| **Backend Microservices** | **FastAPI** | `0.110+` | High-throughput asynchronous ASGI REST API, automatic OpenAPI / Swagger specs |
| **Backend Language** | **Python** | `3.11+` | Asynchronous runtime, type hints, AI/ML execution runtime |
| **ORM & Database Layer** | **Async SQLAlchemy** | `2.0+` | Async ORM mapping, dynamic UUID compilation (`CHAR(32)` vs native `UUID`) |
| **Primary Relational DB** | **PostgreSQL** | `16.2+` | Enterprise relational storage for users, profiles, and academic content |
| **Zero-Downtime Fallback DB** | **SQLite (`aiosqlite`)** | `0.22+` | Embedded zero-config local database (`luminalearn.db`) automatically activated when PostgreSQL is unavailable |
| **Primary Cache & Store** | **Redis** | `7.2+` | Refresh token revocation list, session cache, rate limiting |
| **Zero-Downtime Fallback Cache** | **In-Memory Store** | Thread-Safe Dict | Resilient fallback with microsecond TTL expiration for OTP codes and password reset tokens |
| **Security & Cryptography** | **Argon2id, Bcrypt, PyJWT** | Standards | 15-min Access / 7-day Refresh tokens, keyed HMAC-SHA256 OTP hashes |
| **AI LLM Foundation** | **Google Gemini SDK** | `1.5 Pro / Flash` | Socratic tutoring, dynamic quiz generation, misconception detection |
| **Automated Verification** | **Ruff, Mypy, Pytest** | Latest | Automated static linting, strict Python type checking, and unit testing |
| **Containerization** | **Docker & Compose** | `26.0+` | Multi-container local orchestration and production containerization |

---

## 3. Comprehensive Inventory of Completed Work

### 3.1. Adaptive Zero-Downtime Resilience Engine
- **Cross-Database ORM (`backend/app/core/database.py`)**:
  - Connects to PostgreSQL 16 by default via `asyncpg`.
  - Automatically falls back to embedded SQLite (`sqlite+aiosqlite:///./luminalearn.db`) when PostgreSQL is unreachable or `USE_SQLITE=true`.
  - Uses `sqlalchemy.Uuid(as_uuid=True)` which dynamically compiles to native `UUID` on PostgreSQL and `CHAR(32)`/`VARCHAR(36)` on SQLite, preventing dialect runtime crashes.
  - Safe auto-creation of missing tables on ASGI startup lifespan.
- **Resilient Cache Client (`backend/app/core/redis.py`)**:
  - Primary connection to Redis 7.2+.
  - Automatically falls back to a thread-safe Python dictionary cache with microsecond TTL expiration handling if Redis is offline.
  - Guarantees OTP verification, password resets, and session revocations function in local offline environments.

### 3.2. Full-Stack Identity, Authentication & Security
- **JWT Token Pair System (`backend/app/api/v1/auth.py`)**:
  - Issues 15-minute Access Tokens and 7-day Refresh Tokens.
  - Passwords hashed using Argon2id / Bcrypt via Passlib.
  - HTTP-Only secure cookies and `Authorization: Bearer` header support.
- **Email OTP Verification System**:
  - 6-digit numeric OTP generation.
  - Stored securely using keyed HMAC-SHA256 hashing (raw OTP is never stored in plaintext).
  - 10-minute expiration TTL, 60-second resend cooldown timer, and 5-attempt brute-force threshold.
- **Google OAuth Integration (`backend/app/api/v1/auth.py`)**:
  - Server-side cryptographic token validation using Google's public certificates (`google.oauth2.id_token.verify_oauth2_token`).
  - Validates token signature, expiration, issuer, audience, and `email_verified` claim.
  - Development mock modal allows instant testing without configuring a Google Cloud Console client ID.
  - Protected endpoints reject mock tokens in production mode (`ENVIRONMENT=production`).
- **Role-Based Access Control (RBAC)**:
  - User roles: `student`, `teacher`, `admin`.
  - Reusable dependency injection `require_role(...)` blocks unauthorized users with HTTP 403 Forbidden.

### 3.3. Diagnostic VARK Cognitive Onboarding Subsystem
- **Cognitive Diagnostic Assessment (`backend/app/api/v1/onboarding.py`, `backend/app/models/onboarding.py`)**:
  - 16-question diagnostic questionnaire evaluating learner preferences.
  - Computes primary learning modality (Visual, Auditory, Read/Write, Kinesthetic).
  - Stores student pace preference, academic interests, and modality scores in `StudentProfile`.

### 3.4. Academic Content Hierarchy Engine
- **Database Schema (`backend/app/models/content.py`)**:
  - 5-tier relational structure: `ContentCategory` $\rightarrow$ `Subject` $\rightarrow$ `Course` $\rightarrow$ `Module` $\rightarrow$ `Topic` $\rightarrow$ `Lesson`.
  - Supports ordering indices, difficulty ratings, estimated minutes, and active publication flags.
- **Master Academic Content Seeder (`scripts/seed_academic_content.py`)**:
  - Over 2,980 lines of rich academic content.
  - **4 Top-Level Disciplines**: Computer Science, Programming, Artificial Intelligence, Mathematics.
  - **22 Subjects**: Data Structures, Operating Systems, Computer Networks, Python, JavaScript, Machine Learning, Deep Learning, Calculus, Linear Algebra, etc.
  - **22 Courses**, **146 Structured Modules**, **165 Topics**, and **12 Scaffolded Lessons**.
  - Idempotent execution (skips existing records safely on subsequent runs).
- **Academic API Endpoints (`backend/app/api/v1/content.py`)**:
  - Filter by category slug, difficulty, and search term.
  - Invariant security guard: Lesson content requires an active authenticated session and a verified email address.

### 3.5. Adaptive Quizzing & Bayesian Knowledge Tracing (Sprint 1)
- **Database Schema (`backend/app/models/quiz.py`)**:
  - `QuizSession`: Tracks session ID, user ID, requested topic, difficulty level, start time, score, and mastery delta.
  - `QuizQuestion`: Question text, options JSON, correct answer, explanation, Bloom's level, IRT difficulty $b$, discrimination $a$.
  - `QuizAttempt`: Selected answer, correctness bool, latency seconds, feedback text, detected misconception.
  - Unique constraint `uq_session_question_user_attempt` enforces strict idempotency.
- **Bayesian Knowledge Tracing (BKT) Engine (`ml/models/knowledge_tracer.py`)**:
  - Mathematical mastery probability update on every answer:
    $$p(L_t \mid \text{Correct}) = \frac{p(L_{t-1}) \cdot (1 - P(S))}{p(L_{t-1}) \cdot (1 - P(S)) + (1 - p(L_{t-1})) \cdot P(G)}$$
    $$p(L_t \mid \text{Incorrect}) = \frac{p(L_{t-1}) \cdot P(S)}{p(L_{t-1}) \cdot P(S) + (1 - p(L_{t-1})) \cdot (1 - P(G))}$$
    $$p(L_{t+1}) = p(L_t) + (1 - p(L_t)) \cdot P(T)$$
  - Where $P(L)$ = Mastery, $P(T)$ = Transit rate, $P(G)$ = Guess probability, $P(S)$ = Slip probability.
- **Item Response Theory (IRT 2PL Model)**:
  - Calibrates probability of correctness based on question difficulty ($b$) and discrimination ($a$):
    $$P(\text{correct} \mid \theta) = \frac{1}{1 + e^{-a(\theta - b)}}$$
  - Guarded against numerical overflow via extreme float clipping.

### 3.6. Next.js 14 Frontend Web Client
- **Pages Implemented**:
  1. **Landing Page (`page.tsx`)**: Premium hero banner, interactive feature highlights, Socratic AI preview, and VARK callouts.
  2. **Login Screen (`login/page.tsx`)**: Validated form with Google login button and dev simulation modal.
  3. **Register Screen (`register/page.tsx`)**: Toggle role selection (Student vs. Teacher) and account creation.
  4. **Onboarding Quiz (`onboarding/page.tsx`)**: Interactive multi-step diagnostic quiz assessing learning modalities.
  5. **Student Dashboard (`dashboard/page.tsx`)**: Personal command center displaying VARK modality radar, learning streak tracker, and active courses.
  6. **Academic Subject Catalog (`subjects/page.tsx`)**: Filterable academic disciplines with difficulty tags.
  7. **Lesson Viewer (`lessons/[lessonId]/page.tsx`)**: Clean reading workspace with email verification guard overlay.
  8. **AI Tutor HUD Mockup (`tutor/page.tsx`)**: Interactive preview of the live conversational tutor interface.
  9. **Adaptive Quiz Studio (`quiz/page.tsx`)**: Dynamic math formula rendering (KaTeX), question answering, misconception alerts, and real-time mastery gauges.
  10. **Password Recovery & Email Verification**: Dedicated pages with Next.js Suspense boundaries for static build compliance.
- **Global State Store (`useAuthStore.ts`)**:
  - Auto-login session restoration (`initializeAuth`).
  - Seamless background token refresh and persistence in `localStorage`.

---

## 4. Current Workings & System Health

| Health Check Metric | Status | Details |
| :--- | :---: | :--- |
| **Backend API Server** | **ONLINE** | Running at `http://127.0.0.1:8001` via Uvicorn async lifespan (`python -m app`). |
| **Swagger Interactive Docs** | **ONLINE** | Interactive schema generated at `http://127.0.0.1:8001/docs`. |
| **Frontend Web App** | **ONLINE** | Running at `http://localhost:3000` with 22 routes compiled cleanly. |
| **Automated Test Suite** | **100% PASS** | **59 passed, 0 failed in 17.05s** across 5 test suites. |
| **Static Type Verification** | **100% PASS** | `mypy app` passes with 0 type errors. |
| **Python Code Quality** | **100% PASS** | `ruff check .` passes with 0 linter violations. |
| **Database Resilience** | **VERIFIED** | Automatic fallback to SQLite (`luminalearn.db`) works out of the box. |
| **Cache Resilience** | **VERIFIED** | Automatic fallback to in-memory TTL dictionary works out of the box. |

---

## 5. Automated Test Suite Breakdown (59/59 Passing)

```
tests/test_auth_security.py    (6 tests)  --> PASSED [100%]
tests/test_google_auth.py      (3 tests)  --> PASSED [100%]
tests/test_otp_auth.py         (11 tests) --> PASSED [100%]
tests/test_content_engine.py   (15 tests) --> PASSED [100%]
tests/test_bkt_engine.py       (15 tests) --> PASSED [100%]
tests/test_quiz_engine.py      (9 tests)  --> PASSED [100%]
====================== 59 passed in 17.05s (100% Pass Rate) ======================
```

---

## 6. How the Key Subsystems Work Under the Hood

### 6.1. Authentication & Email OTP Workflow
1. User registers at `POST /api/v1/auth/register`. An unverified user row is created.
2. An 6-digit numeric OTP is generated.
3. The server computes `HMAC_SHA256(otp, secret_key)` and stores the hash in Redis (or in-memory cache) with a 600-second TTL.
4. When the user submits the code at `POST /api/v1/auth/verify-email`, the submitted code is hashed with the same key and compared using constant-time comparison `compare_digest`.
5. On match: `is_verified` is flipped to `True`, the OTP cache is evicted, and a JWT pair is issued.

### 6.2. Dual-Engine Resilience Workflow
1. At application startup (`lifespan`), the backend initiates an async probe to PostgreSQL (`asyncpg`).
2. If the connection fails or timeout occurs, it catches `OperationalError`, logs a warning, and switches `database_url` to `sqlite+aiosqlite:///./luminalearn.db`.
3. SQLAlchemy models use `Uuid(as_uuid=True)`, dynamically compiling to `UUID` on PostgreSQL and `CHAR(32)` on SQLite.
4. Redis follows the same pattern: if `redis.ping()` fails, cache methods seamlessly redirect to an internal thread-safe Python dictionary with TTL expiration checks.

### 6.3. Adaptive Quizzing & BKT Mastery Flow
1. Student requests a quiz for a topic via `POST /api/v1/quiz/generate`.
2. Gemini 1.5 generates questions adhering to Bloom's taxonomy and distractor misconception mapping.
3. Student submits an answer at `POST /api/v1/quiz/submit-answer`.
4. Idempotency check: queries `uq_session_question_user_attempt`. If already graded, returns cached result without recalculating.
5. The submission is evaluated: BKT posterior mastery $p(L_t)$ is updated using prior mastery, Slip ($0.10$), Guess ($0.20$), and Learning Transition ($0.15$).
6. If the selected answer is a distractor, the detected misconception diagnosis is logged and returned with corrective feedback.

---

## 7. Upcoming Sprint Roadmap

### Sprint 2: Multi-Agent Socratic Faculty & Real-Time Voice Agent
- **LangGraph Multi-Agent Team**:
  - Supervisor Agent (routing by cognitive state).
  - Socratic Tutor Agent (scaffolding questions, 3-tier hint ladders).
  - Concept Explainer (VARK modality adapter).
  - Analogy Specialist (real-world metaphors).
  - Code/Lab Diagnostic Specialist.
- **Full-Duplex Voice Agent**:
  - FastAPI WebSocket endpoint at `/api/v1/voice/session`.
  - Barge-in interruption detection (clears audio buffer when user begins speaking).
  - Reactive HTML5 Canvas audio orb visualizer.

### Sprint 3: Grounded Curriculum RAG & Educator Command Center
- **Vector Database (Qdrant)**: Ingestion of textbooks and syllabus chunks with hybrid dense-sparse search to guarantee zero hallucinations.
- **Educator Command Center**: Heatmap of classroom conceptual bottlenecks, automated at-risk alerts, and AI rubric grading.

### Sprint 4: QA Hardening & Cloud Production Release
- Playwright E2E browser automation suite.
- Automated WCAG 2.1 AAA accessibility validation (`axe-core`).
- GitHub Actions CI/CD with automated Docker image build and deploy to AWS/GCP.

---

## 8. Quickstart Commands

```bash
# 1. Start everything (backend + frontend) from the project root:
npm run dev
#    API on http://127.0.0.1:8001, web app on http://localhost:3000 (or the next free port).
#    Ctrl+C stops both. Workspace pages require signing in.

# 2. Or start them separately:
cd backend
.\.venv\Scripts\Activate.ps1
python -m app            # uses BACKEND_PORT from backend/.env (8001); refuses a port already in use
cd ../frontend
npm run dev              # its /api/v1 proxy forwards to BACKEND_URL in frontend/.env.local
#    Don't start uvicorn on port 8000 on this machine: Splunk answers there.

# 3. Run All Backend Tests:
cd backend
pytest -v

# 4. Run Linter & Typecheck:
cd backend
ruff check .
mypy app
```

---
*Document Location: `docs/PROJECT_MASTER_OVERVIEW.md` and `PROJECT_MASTER_OVERVIEW.txt`*
