# LuminaLearn AI (Project Aurora) — Full Information & Sprint Master Document

> **Document Name**: `FULL_INFO.md`  
> **Project**: LuminaLearn AI (*Project Aurora*)  
> **Status**: Comprehensive Monorepo Specification, Completed Work Inventory, System Health, and Sprint Execution Roadmap  
> **Repository Location**: Root [`FULL_INFO.md`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/FULL_INFO.md)  
> **Audit Status**: 35/35 Pytest Tests Passing (100%) | Backend (:8000) & Frontend (:3000) Operational

---

## Table of Contents

1. [Executive Summary & Product Vision](#1-executive-summary--product-vision)
2. [Complete Technology Stack Specification](#2-complete-technology-stack-specification)
3. [Monorepo Directory Structure](#3-monorepo-directory-structure)
4. [Current System Health & Verification Status](#4-current-system-health--verification-status)
5. [Comprehensive Inventory of What Has Been Completed](#5-comprehensive-inventory-of-what-has-been-completed)
   - 5.1 Adaptive Zero-Downtime Resilience Engine
   - 5.2 Full-Stack Identity, Authentication & Security
   - 5.3 Diagnostic VARK Cognitive Onboarding Subsystem
   - 5.4 Academic Content Hierarchy Engine (Sprint 6.2A & 6.2B)
   - 5.5 Next.js 14 Frontend Web Client
   - 5.6 Automated Test Suite (35 Passing Tests)
6. [Audit of the 8 Formal SDLC Phases](#6-audit-of-the-8-formal-sdlc-phases)
7. [Sub-Phase Status of Phase 5 (Implementation & Build)](#7-sub-phase-status-of-phase-5-implementation--build)
8. [What Has To Be Done Next (Upcoming Sprints & Implementation Roadmap)](#8-what-has-to-be-done-next-upcoming-sprints--implementation-roadmap)
   - 8.1 Sprint 1: Topic-Based Adaptive Quizzing & Bayesian Knowledge Tracing (BKT)
   - 8.2 Sprint 2: LangGraph Multi-Agent Teaching Framework & Real-Time Voice Agent
   - 8.3 Sprint 3: Grounded Curriculum RAG & Educator Command Center
   - 8.4 Sprint 4: Automated E2E Testing, WCAG Audits & Cloud Production Release
9. [Agile Sprint Framework & 10-Point Definition of Done (DoD)](#9-agile-sprint-framework--10-point-definition-of-done-dod)
10. [Local Quickstart & Execution Guide](#10-local-quickstart--execution-guide)
11. [User Action Items to Kick Off Next Sprint](#11-user-action-items-to-kick-off-next-sprint)

---

## 1. Executive Summary & Product Vision

**LuminaLearn AI** is an enterprise-grade, AI-first adaptive learning ecosystem engineered to revolutionize online education. Conventional Learning Management Systems (LMS) enforce linear, one-size-fits-all curricula that treat all learners identically. LuminaLearn AI personalizes education dynamically based on each student's cognitive pace, knowledge gaps, and preferred **VARK learning style** (Visual, Auditory, Read/Write, Kinesthetic).

### Core Strategic Pillars

1. **Socratic AI Agent Framework**: Rather than spoon-feeding direct homework solutions, the system guides learners through inquisitive step-by-step scaffolding questions, hint ladders, and conceptual self-discovery.
2. **Cognitive Personalization (VARK Adapters)**: Dynamically calibrates content presentation (visual diagrams, audio summaries, text breakdowns, or interactive simulations) based on cognitive diagnostics.
3. **Resilient Hybrid Infrastructure**: Engineered with zero-downtime local fallback mechanisms (SQLite + In-Memory Caching) alongside enterprise PostgreSQL + Redis support.
4. **Universal Accessibility (WCAG 2.1 AAA)**: Native architecture designed for screen readers, high-contrast modes, dyslexia-friendly typography, and multi-modal speech interfaces.
5. **Explainable AI (XAI) & Learning Analytics**: Transparent student mastery mapping, decay curves (spacing effect), and retention forecasts for students, parents, and educators.

---

## 2. Complete Technology Stack Specification

| Subsystem | Technology | Version / Spec | Purpose & Architectural Role |
| :--- | :--- | :---: | :--- |
| **Frontend Framework** | **Next.js (App Router)** | `14.2+` | React 18, Server Components, SSR/CSR hybrid routing, layout nesting |
| **Frontend Language** | **TypeScript** | `5.4+` | Strict static type safety, interface contracts, zero runtime type errors |
| **Styling & Design System** | **Tailwind CSS + Lucide Icons** | `3.4+` | Apple/Linear-inspired dark glassmorphism, responsive CSS variables |
| **Client State Management** | **Zustand** | `4.5+` | Lightweight global reactive store for auth sessions & learner state |
| **Data Fetching Client** | **Axios & TanStack Query** | Latest | Automated Authorization bearer injection and response error interceptors |
| **Backend Microservices** | **FastAPI** | `0.110+` | High-throughput asynchronous ASGI REST API, automatic OpenAPI / Swagger specs |
| **Backend Language** | **Python** | `3.11+` | Asynchronous runtime, type hints, AI/ML execution runtime |
| **ORM & Database Layer** | **Async SQLAlchemy** | `2.0+` | Async ORM mapping, cross-database UUID compilation, repository pattern |
| **Primary Relational DB** | **PostgreSQL** | `16.2+` | Scalable enterprise storage for users, profiles, and academic content |
| **Zero-Downtime Fallback DB**| **SQLite (`aiosqlite`)** | `0.22+` | Embedded zero-config local database automatically activated when PostgreSQL is unavailable |
| **Primary Cache & Store** | **Redis** | `7.2+` | Refresh token revocation list, session cache, rate limiting |
| **Zero-Downtime Fallback Cache**| **In-Memory Dictionary Cache** | Thread-Safe Dict | Resilient fallback with TTL expiration for OTP codes and password reset tokens |
| **Security & Cryptography** | **Argon2id, Bcrypt, PyJWT** | Industry Standard | 15-min Access / 7-day Refresh tokens, keyed HMAC-SHA256 OTP hashes |
| **AI LLM Foundation** | **Google Gemini SDK** | `1.5 Pro / Flash` | Socratic tutoring, dynamic quiz generation, explanation synthesis |
| **Code Verification** | **Ruff, Mypy, ESLint, Pytest** | Latest | Automated static linting, strict Python type checking, and unit testing |
| **Containerization** | **Docker & Docker Compose** | `26.0+` | Multi-container local orchestration and production containerization |

---

## 3. Monorepo Directory Structure

```
LUMINALEARN_AI/
├── .github/                     # GitHub CI/CD workflows, issue & PR templates
├── .vscode/                     # Workspace linter, formatter & debugger settings
├── ai/                          # Pedagogical Socratic AI Agent framework & prompts
│   ├── agents/                  # Multi-agent collective (Socratic, Explainer, Analogy)
│   ├── prompts/                 # System prompt templates & guardrails
│   └── rag/                     # Vector retrieval & document chunking pipelines
├── backend/                     # FastAPI (Python 3.11+) microservices application
│   ├── app/
│   │   ├── api/                 # API routing layer
│   │   │   ├── deps.py          # FastAPI dependencies (auth, role checks, DB sessions)
│   │   │   └── v1/              # Version 1 endpoints (auth, onboarding, content)
│   │   ├── core/                # Core infrastructure (config, database, redis, security)
│   │   ├── models/              # SQLAlchemy 2.0 ORM database models
│   │   ├── repositories/        # Repository pattern database access layer
│   │   ├── schemas/             # Pydantic v2 validation models
│   │   ├── services/            # Domain business logic (AuthService, ContentService)
│   │   └── main.py              # ASGI application entrypoint with lifespan manager
│   ├── tests/                   # Pytest automated test suite (35 tests passing)
│   ├── Dockerfile               # Multi-stage production container specification
│   └── pyproject.toml           # Python dependencies, Ruff, and Mypy configurations
├── database/                    # Relational database initialization & schemas
│   ├── init/                    # Initial database bootstrap SQL scripts
│   └── schema.sql               # Master DDL schema definition
├── docker/                      # Multi-container orchestration configurations
│   └── docker-compose.dev.yml   # Local development multi-container stack
├── docs/                        # Single Source of Truth (SSOT) technical documentation
│   ├── PRODUCT_CHARTER.md       # Product vision, user personas, and 8-phase SDLC roadmap
│   ├── MARKET_RESEARCH.md       # EdTech industry analysis, competitor landscape, TAM/SAM/SOM
│   ├── STAKEHOLDER_ANALYSIS.md  # 20 user personas, regulatory guidelines (FERPA/COPPA)
│   ├── SYSTEM_ARCHITECTURE.md   # Architectural blueprints, data flow diagrams, security
│   ├── UX_ARCHITECTURE.md       # User journeys, wireframes, and VARK UI adaptation strategies
│   ├── DESIGN_SYSTEM.md         # Tailwind CSS design tokens and component specifications
│   ├── ENGINEERING_STANDARDS.md # Code standards, git branch policies, and sprint checklists
│   ├── PROJECT_MASTER_DOCUMENT.md # Developer handbook & 20+ interview/architecture QA sets
│   └── PROJECT_PHASES_AND_WORKFLOW_STATUS.md # Official workflow status report
├── frontend/                    # Next.js 14 App Router web client
│   ├── src/
│   │   ├── app/                 # Next.js App Router routes & pages
│   │   ├── components/          # Reusable UI component library (glassmorphic dark mode)
│   │   ├── hooks/               # Custom React lifecycle hooks
│   │   ├── services/            # Axios API communication services
│   │   ├── stores/              # Zustand global client state stores
│   │   └── styles/              # Global CSS variables, radiant glow tokens, and typography
│   ├── next.config.js           # Next.js server configuration
│   ├── tailwind.config.js       # Design tokens & color theme specifications
│   └── tsconfig.json            # Strict TypeScript compiler options
├── ml/                          # Machine Learning & Knowledge Tracing engine
│   └── models/                  # Bayesian Knowledge Tracing & Skill Graph models
├── scripts/                     # Developer automation & data seeding utilities
│   ├── seed_academic_content.py # Sprint 6.2B master content seeder (2,980 lines)
│   └── setup_dev.sh             # Linux/macOS automated environment bootstrap
├── .env.example                 # Centralized environment variable template
├── docker-compose.yml           # Root Docker Compose orchestration file
├── mypy.ini                     # Strict Python type checking configuration
├── ruff.toml                    # High-performance Python linter configuration
├── NEXT_IMPLEMENTATIONS.md      # Project Aurora v2.0 evolution blueprint (Adaptive Quiz & Voice)
└── FULL_INFO.md                 # THIS FILE (Comprehensive project master document)
```

---

## 4. Current System Health & Verification Status

| Health Check Metric | Status | Verification Details |
| :--- | :---: | :--- |
| **Backend API Server** | **ONLINE** | Running at `http://127.0.0.1:8000` via Uvicorn async lifespan. |
| **Swagger Interactive Docs**| **ONLINE** | Interactive API schema generated at `http://127.0.0.1:8000/docs`. |
| **Frontend Web App** | **ONLINE** | Running at `http://localhost:3000` via Next.js 14 App Router. |
| **Automated Pytest Suite** | **100% PASS** | **35 passed, 0 failed** in `backend/tests/` across 4 test suites. |
| **Static Type Verification**| **100% PASS** | `mypy app` passes with 0 type errors. |
| **Python Code Quality** | **100% PASS** | `ruff check .` passes with 0 linter violations. |
| **Frontend Build** | **100% PASS** | `npm run build` compiles with zero hydration or SSR errors. |
| **Database Resilience** | **VERIFIED** | Successfully tested seamless automatic fallback to SQLite (`luminalearn.db`). |
| **Cache Resilience** | **VERIFIED** | Successfully tested in-memory fallback for OTP codes & password resets without Redis. |

---

## 5. Comprehensive Inventory of What Has Been Completed

### 5.1 Adaptive Zero-Downtime Resilience Engine
- **Cross-Database ORM ([`backend/app/core/database.py`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/backend/app/core/database.py))**:
  - Connects to PostgreSQL 16 by default via `asyncpg`.
  - Automatically activates embedded SQLite mode (`sqlite+aiosqlite:///./luminalearn.db`) when PostgreSQL is unreachable or `USE_SQLITE=true`.
  - Employs `sqlalchemy.Uuid(as_uuid=True)` which dynamically compiles to native `UUID` on PostgreSQL and `CHAR(32)`/`VARCHAR(36)` on SQLite, preventing dialect runtime crashes.
  - Safe auto-creation of missing tables on ASGI startup lifespan.
- **Resilient Cache Client ([`backend/app/core/redis.py`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/backend/app/core/redis.py))**:
  - Primary connection to Redis 7.2+.
  - Automatically falls back to a thread-safe Python dictionary cache with microsecond TTL expiration handling if Redis is offline.
  - Guarantees OTP verification, password resets, and session revocations function flawlessly in local offline environments.

### 5.2 Full-Stack Identity, Authentication & Security
- **JWT Token Pair System ([`backend/app/api/v1/auth.py`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/backend/app/api/v1/auth.py))**:
  - Issues 15-minute Access Tokens and 7-day Refresh Tokens.
  - Passwords hashed using Argon2id / Bcrypt via Passlib.
  - HTTP-Only secure cookies and `Authorization: Bearer` header support.
- **Email OTP Verification System**:
  - 6-digit numeric OTP generation.
  - Stored securely using keyed HMAC-SHA256 hashing (raw OTP is never stored in plaintext).
  - 10-minute expiration TTL, 60-second resend cooldown timer, and 5-attempt brute-force threshold.
- **Google OAuth Integration ([`backend/app/api/v1/auth.py`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/backend/app/api/v1/auth.py))**:
  - Server-side cryptographic token validation using Google's public certificates (`google.oauth2.id_token.verify_oauth2_token`).
  - Validates token signature, expiration, issuer, audience, and `email_verified` claim.
  - Development mock modal allows instant testing without configuring a Google Cloud Console client ID.
  - Protected endpoints prevent mock tokens from being accepted in production mode (`ENVIRONMENT=production`).
- **Role-Based Access Control (RBAC)**:
  - User roles: `student`, `teacher`, `admin`.
  - Reusable dependency injection `require_role(...)` blocks unauthorized users with HTTP 403 Forbidden.

### 5.3 Diagnostic VARK Cognitive Onboarding Subsystem
- **Cognitive Diagnostic Assessment ([`backend/app/api/v1/onboarding.py`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/backend/app/api/v1/onboarding.py))**:
  - 16-question diagnostic questionnaire evaluating learner preferences.
  - Computes primary learning modality (Visual, Auditory, Read/Write, Kinesthetic).
  - Stores student pace preference, academic interests, and modality scores in `StudentProfile`.

### 5.4 Academic Content Hierarchy Engine (Sprint 6.2A & 6.2B)
- **Database Schema ([`backend/app/models/content.py`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/backend/app/models/content.py))**:
  - 5-tier relational structure: `ContentCategory` $\rightarrow$ `Subject` $\rightarrow$ `Course` $\rightarrow$ `Module` $\rightarrow$ `Topic` $\rightarrow$ `Lesson`.
  - Supports ordering indices, difficulty ratings, estimated minutes, and active publication flags.
- **Master Academic Content Seeder ([`scripts/seed_academic_content.py`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/scripts/seed_academic_content.py))**:
  - Over 2,980 lines of rich academic content.
  - **4 Top-Level Disciplines**: Computer Science, Programming, Artificial Intelligence, Mathematics.
  - **22 Subjects**: Data Structures, Operating Systems, Computer Networks, Python, JavaScript, Machine Learning, Deep Learning, Calculus, Linear Algebra, etc.
  - **22 Courses**, **146 Structured Modules**, **165 Topics**, and **12 Scaffolded Lessons**.
  - Idempotent execution (skips existing records safely on subsequent runs).
- **Academic API Endpoints ([`backend/app/api/v1/content.py`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/backend/app/api/v1/content.py))**:
  - Filter by category slug, difficulty, and search term.
  - Invariant security guard: Lesson content requires an active authenticated session and a verified email address.

### 5.5 Next.js 14 Frontend Web Client
- **Pages Implemented**:
  1. **Landing Page ([`page.tsx`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/frontend/src/app/page.tsx))**: Premium hero banner, interactive feature highlights, Socratic AI preview, and VARK callouts.
  2. **Login Screen ([`login/page.tsx`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/frontend/src/app/login/page.tsx))**: Validated form with Google login button and dev simulation modal.
  3. **Register Screen ([`register/page.tsx`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/frontend/src/app/register/page.tsx))**: Toggle role selection (Student vs. Teacher) and account creation.
  4. **Onboarding Quiz ([`onboarding/page.tsx`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/frontend/src/app/onboarding/page.tsx))**: Interactive multi-step diagnostic quiz assessing learning modalities.
  5. **Student Dashboard ([`dashboard/page.tsx`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/frontend/src/app/dashboard/page.tsx))**: Personal command center displaying VARK modality radar, learning streak tracker, and active courses.
  6. **Academic Subject Catalog ([`subjects/page.tsx`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/frontend/src/app/subjects/page.tsx))**: Filterable academic disciplines with difficulty tags.
  7. **Lesson Viewer ([`lessons/[lessonId]/page.tsx`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/frontend/src/app/lessons/[lessonId]/page.tsx))**: Clean reading workspace with email verification guard overlay.
  8. **AI Tutor Mockup HUD ([`tutor/page.tsx`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/frontend/src/app/tutor/page.tsx))**: Interactive preview of the upcoming live conversational tutor interface.
  9. **Password Recovery & Email Verification**: Dedicated pages with Next.js Suspense boundaries for static build compliance.
- **Global State Store ([`useAuthStore.ts`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/frontend/src/stores/useAuthStore.ts))**:
  - Auto-login session restoration (`initializeAuth`).
  - Seamless background token refresh and persistence in `localStorage`.

### 5.6 Automated Test Suite (35 Passing Tests)
- Located in [`backend/tests/`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/backend/tests):
  - `test_auth_security.py` (6 tests): Mock token rejection in production, invalid Google tokens, unverified email checks, password login blocks for OAuth accounts, cookie security flags.
  - `test_google_auth.py` (3 tests): Student OAuth signup, Teacher OAuth signup, login for existing accounts.
  - `test_otp_auth.py` (11 tests): OTP generation, keyed HMAC hashing, attempt limit locks, expiration, resend cooldowns, state cleanup on success, protected route token enforcement.
  - `test_content_engine.py` (15 tests): Seeder idempotency, category endpoints, subject filtering and 404 handling, course module traversal, topic lesson lists, unauthenticated and unverified lesson blocks, verified lesson access.

---

## 6. Audit of the 8 Formal SDLC Phases

The project follows an 8-Phase Software Development Lifecycle (SDLC) defined in [`docs/PRODUCT_CHARTER.md`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/docs/PRODUCT_CHARTER.md):

```
+-----------------------------------------------------------------------------------+
|                             SDLC PHASE DELIVERABLES                               |
|                                                                                   |
| Phase 1: Strategy  ► Phase 2: Reqs     ► Phase 3: Arch    ► Phase 4: UX/UI Design  |
| Phase 5: Build     ► Phase 6: QA/Audit ► Phase 7: Deploy  ► Phase 8: Operations  |
+-----------------------------------------------------------------------------------+
```

| Phase | Phase Name | Status | Completion % | Key Artifacts & Deliverables |
| :---: | :--- | :---: | :---: | :--- |
| **Phase 1** | **Product Strategy** | Complete | **100%** | [`PRODUCT_CHARTER.md`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/docs/PRODUCT_CHARTER.md), [`MARKET_RESEARCH.md`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/docs/MARKET_RESEARCH.md), TAM/SAM/SOM market sizing, competitive positioning matrix. |
| **Phase 2** | **Requirements Engineering** | Complete | **100%** | [`STAKEHOLDER_ANALYSIS.md`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/docs/STAKEHOLDER_ANALYSIS.md) (20 user personas), FERPA/COPPA compliance framework, WCAG 2.1 AAA accessibility rules. |
| **Phase 3** | **System Architecture & Design** | Complete | **100%** | [`SYSTEM_ARCHITECTURE.md`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/docs/SYSTEM_ARCHITECTURE.md), [`ENGINEERING_STANDARDS.md`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/docs/ENGINEERING_STANDARDS.md), master DDL schema, dual-engine fallback architecture. |
| **Phase 4** | **UX / UI Design Systems** | Complete | **100%** | [`DESIGN_SYSTEM.md`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/docs/DESIGN_SYSTEM.md), [`UX_ARCHITECTURE.md`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/docs/UX_ARCHITECTURE.md), Tailwind tokens, glassmorphic dark theme, micro-animations. |
| **Phase 5** | **Implementation & Build** | **In-Progress** | **50%** | Core backend, resilient DB/cache, auth, onboarding, and content hierarchy 100% complete; Socratic AI & voice agent upcoming. |
| **Phase 6** | **Quality Assurance & Audits** | Upcoming | **15%** | Ruff/Mypy verified, 35 Pytest tests clean; End-to-end browser tests and AI bias/hallucination audits scheduled. |
| **Phase 7** | **Deployment & Release** | Upcoming | **10%** | Multi-container Docker compose configured; CI/CD automation and production cloud deployment scheduled. |
| **Phase 8** | **Post-Launch & Operations** | Upcoming | **0%** | Telemetry pipelines, Prometheus/Grafana monitoring, and educator onboarding manuals scheduled. |

---

## 7. Sub-Phase Status of Phase 5 (Implementation & Build)

| Sub-Phase | Component / Module | Progress | Status | Deliverables |
| :--- | :--- | :---: | :---: | :--- |
| **5.1** | **Monorepo & Environment** | **100%** | Complete | Docker compose, `.env.example`, linter configs, Git hygiene. |
| **5.2** | **Resilient DB & Cache Core** | **100%** | Complete | `database.py`, `redis.py`, dual-engine automatic fallback. |
| **5.3** | **Auth & Identity Engine** | **100%** | Complete | JWT tokens, Argon2id hashing, Google OAuth, HMAC-SHA256 OTP. |
| **5.4** | **Diagnostic VARK Onboarding**| **100%** | Complete | 16-question diagnostic, scoring logic, DB persistence. |
| **5.5** | **Frontend Core & State** | **100%** | Complete | Next.js 14 App Router, Zustand, responsive glassmorphic UI. |
| **5.5b**| **Academic Content Engine** | **100%** | Complete | 5-tier relational hierarchy, seeder, content APIs. |
| **5.6** | **Socratic AI Agent Framework**| **15%** | **Next Up** | `ai/` folder initialized; Gemini SDK prompt orchestration scheduled. |
| **5.7** | **Vector DB & RAG Pipeline** | **0%** | Scheduled | Qdrant vector database integration for verified textbook search. |
| **5.8** | **Live Socratic Tutor & Voice**| **10%** | Scheduled | UI mockup exists; WebSocket audio streaming scheduled. |

---

## 8. What Has To Be Done Next (Upcoming Sprints & Implementation Roadmap)

The upcoming implementation roadmap is formally outlined in [`NEXT_IMPLEMENTATIONS.md`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/NEXT_IMPLEMENTATIONS.md) (*Project Aurora v2.0*), targeting a transformation from static course browsing into an **adaptive quizzing and voice-first personal tutor**.

```
                           UPCOMING SPRINT ROADMAP
┌─────────────────────────────────────────────────────────────────────────────┐
│ SPRINT 1: Adaptive Quizzing & Predictive Accuracy Engine                     │
│ ├── Topic-Based Dynamic Quiz Generator (Gemini 1.5 JSON Schema)             │
│ ├── Bloom's Taxonomy & Item Response Theory (IRT 2PL difficulty calibration) │
│ ├── Bayesian Knowledge Tracing (BKT) Engine (ml/models/knowledge_tracer.py) │
│ └── Quiz History, Misconception Detection & Prerequisite Skill Graph        │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ SPRINT 2: Multi-Agent Socratic Teaching & Real-Time Voice Agent             │
│ ├── LangGraph Multi-Agent Faculty (Supervisor, Socratic, Explainer, Analogy)│
│ ├── Full-Duplex Real-Time Voice Agent (FastAPI WebSocket + Audio Streaming) │
│ ├── Barge-in / Interruption Detection & Audio Buffer Cancellation           │
│ └── Next.js Voice & Quiz Studio (Canvas Waveform, KaTeX LaTeX, Radar Chart) │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ SPRINT 3: Curriculum RAG & Educator Command Center                          │
│ ├── Qdrant Vector Database Ingestion (Syllabus Chunking, Zero-Hallucination)│
│ ├── Teacher Analytics Dashboard (Classroom Bottlenecks & At-Risk Alerts)    │
│ └── Automated AI-Assisted Rubric Grading & Lesson Plan Generator            │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ SPRINT 4: QA Hardening, E2E Testing & Production Deployment                 │
│ ├── Playwright / Cypress E2E Suite & AI Bias / Hallucination Audits         │
│ ├── WCAG 2.1 AAA Automated Accessibility Validation (axe-core)              │
│ └── GitHub Actions CI/CD & Cloud Elastic Production Deployment              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.1 Sprint 1: Topic-Based Adaptive Quizzing & Bayesian Knowledge Tracing — [VERIFIED & COMPLETE ✅]

**Status:** Completed, Integrated, and 100% Tested (**54/54 Passing Backend Tests**).

#### 1. Dynamic Topic Quiz Generation & API Endpoints
- **Endpoints Implemented:**
  - `POST /api/v1/quiz/generate`: Generates calibrated questions using Gemini Pro/Flash SDK with fallback to deterministic math benchmarks.
  - `GET /api/v1/quiz/session/{session_id}`: Retrieves student session with answers withheld prior to submission.
  - `POST /api/v1/quiz/submit-answer`: Grades attempt, detects conceptual misconceptions, updates BKT mastery, and guarantees idempotency.
  - `GET /api/v1/quiz/mastery/{topic}`: Returns student retention curve, predicted future accuracy, and historical attempt timelines.
- Questions span Bloom's Taxonomy: *Remembering* $\rightarrow$ *Understanding* $\rightarrow$ *Applying* $\rightarrow$ *Analyzing* $\rightarrow$ *Evaluating*.

#### 2. Item Response Theory (IRT 2PL Model)
Calibrates question difficulty against learner ability:
$$P(\text{correct} \mid \theta) = \frac{1}{1 + e^{-a(\theta - b)}}$$
- Implemented in [`ml/models/knowledge_tracer.py`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/ml/models/knowledge_tracer.py) with numerical stability clipping guards to eliminate float overflow.

#### 3. Bayesian Knowledge Tracing (BKT) Engine (`ml/models/knowledge_tracer.py`)
Predicts with mathematical accuracy whether a student has truly mastered a skill:
1. **If student answered correctly:**
   $$p(L_t \mid \text{Correct}) = \frac{p(L_{t-1}) \cdot (1 - P(S))}{p(L_{t-1}) \cdot (1 - P(S)) + (1 - p(L_{t-1})) \cdot P(G)}$$
2. **If student answered incorrectly:**
   $$p(L_t \mid \text{Incorrect}) = \frac{p(L_{t-1}) \cdot P(S)}{p(L_{t-1}) \cdot P(S) + (1 - p(L_{t-1})) \cdot (1 - P(G))}$$
3. **Transition to next opportunity (Learning Rate):**
   $$p(L_{t+1}) = p(L_t) + (1 - p(L_t)) \cdot P(T)$$
- Unit tested via [`backend/tests/test_bkt_engine.py`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/backend/tests/test_bkt_engine.py) (**12/12 passing**).

#### 4. Database Schema Additions (`backend/app/models/quiz.py`)
- `QuizSession`: Tracks session ID, user ID, requested topic, difficulty level, start time, score, and mastery delta.
- `QuizQuestion`: Question text, options JSON, correct answer, explanation, Bloom's level, IRT difficulty $b$, discrimination $a$.
- `QuizAttempt`: Selected answer, correctness bool, latency seconds, feedback text, detected misconception.
- Unique constraint `uq_session_question_user_attempt` enforces strict idempotency.

#### 5. Frontend KaTeX & Adaptive Quiz Studio (`frontend/src/app/quiz/page.tsx`)
- High-performance KaTeX math formula rendering via [`frontend/src/components/common/MathRenderer.tsx`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/frontend/src/components/common/MathRenderer.tsx).
- Pre-calibrated mathematics domains (Calculus, Linear Algebra, Probability & Statistics, Algorithms).
- Live Bayesian mastery gauge, diagnosed misconception alerts, and retention curve history.
- Next.js production build: **22/22 routes successfully compiled**.

---

### 8.2 Sprint 2: LangGraph Multi-Agent Teaching Framework & Real-Time Voice Agent

#### 1. Multi-Agent Teaching Collective (`ai/agents/`)
Instead of a single monolithic prompt, LuminaLearn AI deploys a coordinated team of specialized AI agents:
1. **Supervisor Agent**: Inspects conversation state, student mastery score, and cognitive load; delegates to the appropriate agent.
2. **Socratic Tutor Agent**: Asks targeted scaffolding questions to guide students toward the answer without spoon-feeding solutions.
3. **Concept Explainer Agent**: Steps in when a student is stuck; breaks concepts down to first principles using the student's VARK modality (e.g., ASCII diagrams for Visual learners, physical metaphors for Kinesthetic learners).
4. **Analogy Specialist Agent**: Translates abstract academic concepts into relatable everyday analogies.
5. **Code & Lab Specialist**: Writes, analyzes, and executes student code in safe sandbox environments.

#### 2. Full-Duplex Real-Time Voice Agent (`backend/app/api/v1/voice.py`)
- FastAPI WebSocket endpoint at `/api/v1/voice/session`.
- Receives client audio chunks (WebM/PCM).
- Fast STT (Whisper / Web Speech API) passes tokens to Gemini streaming core.
- Low-latency TTS (Web Speech API / Edge-TTS / ElevenLabs) streams audio back to the frontend.
- **Barge-In / Interruption Detection**: If the student begins speaking while the AI is talking, audio playback is instantly silenced and the AI begins listening.

#### 3. Next.js Interactive Workspace (`frontend/src/app/quiz/`)
- Dynamic Question Studio with KaTeX LaTeX mathematical rendering and Prism syntax highlighting.
- Audio Waveform Visualizer (Canvas glowing orb reacting to voice frequencies).
- Knowledge Mastery Radar (interactive spider chart displaying skill retention).

---

### 8.3 Sprint 3: Grounded Curriculum RAG & Educator Command Center
- **Qdrant Vector Database**: Ingests textbook chapters, lecture notes, and syllabus documents with dense-sparse hybrid search to ensure zero-hallucination citations.
- **Educator Command Center**:
  - Class-wide conceptual bottleneck heatmaps.
  - Automated at-risk student intervention triggers.
  - AI-assisted rubric grading and lesson draft generators.

---

### 8.4 Sprint 4: Automated E2E Testing, WCAG Audits & Cloud Production Release
- **Playwright E2E Suite**: Full browser automation testing covering the student journey from registration to quiz completion.
- **WCAG 2.1 AAA Accessibility Audit**: Automated accessibility test runs using axe-core to ensure 100% compliance.
- **CI/CD & Cloud Deployment**: GitHub Actions pipeline for linting, testing, Docker image building, and deployment to AWS/GCP with automated SSL.

---

## 9. Agile Sprint Framework & 10-Point Definition of Done (DoD)

The team operates on a standard **2-Week Sprint Cycle** ([`docs/ENGINEERING_STANDARDS.md#L567-L604`](file:///c:/Users/Sudar/Downloads/luminalearn-main/luminalearn-main/docs/ENGINEERING_STANDARDS.md#L567-L604)):

```
+-----------------------------------------------------------------------------------+
|                            2-WEEK SPRINT CYCLE FLOW                               |
|                                                                                   |
|  [Day 1: Planning] ──► [Days 2-7: Dev & Testing] ──► [Days 8-9: Review & QA]     |
|                                                               │                   |
|  [Day 10: Retrospective & Release] ◄──────────────────────────┘                   |
+-----------------------------------------------------------------------------------+
```

### Master 10-Point Sprint Definition of Done (DoD) Checklist

| # | Checklist Domain | Requirement | Responsible Role | Status |
| :-: | :--- | :--- | :---: | :---: |
| **1** | **Architecture** | Code adheres to modular domain boundaries and repository patterns. | Tech Lead | Verified |
| **2** | **Clean Code** | 0 linter errors (`ruff` / `ESLint`), 100% strict type annotations. | Lead Developer | Verified |
| **3** | **Git Strategy** | Conventional commits used, feature branches reviewed before merge. | GitHub Maintainer | Verified |
| **4** | **API Standards** | Standardized response envelopes, OpenAPI docs generated, correct status codes. | Backend Lead | Verified |
| **5** | **Testing** | $\ge 85\%$ test coverage, all unit and integration tests passing. | QA Lead | 54/54 Passed |
| **6** | **Security** | Zero secrets in code, OWASP Top 10 validated, anti-enumeration in place. | Security Officer | Verified |
| **7** | **Accessibility** | 100% WCAG 2.1 AAA automated pass rate. | A11y Lead | Scheduled |
| **8** | **Infrastructure** | Multi-stage Docker builds pass without root privileges. | DevOps Lead | Verified |
| **9** | **Documentation** | Single Source of Truth docs in `docs/` updated. | Scrum Master | Verified |
| **10**| **Sign-off** | Double code-owner review completed before staging merge. | Engineering Manager| Verified |

---

## 10. Local Quickstart & Execution Guide

### Prerequisites
- **Node.js**: `v20.x` or higher
- **Python**: `3.11.x`
- **Docker & Docker Compose**: `v26.x` or higher

### Step 1: Clone & Configure Environment
```bash
cp .env.example .env
```

### Step 2: Launch Backend (FastAPI)
```bash
cd backend
python -m venv .venv

# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# On Linux/macOS:
source .venv/bin/activate

# Install dependencies:
pip install -r requirements.txt aiosqlite email-validator

# Run dev server:
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Endpoint: `http://127.0.0.1:8000`
- Swagger Documentation: `http://127.0.0.1:8000/docs`

### Step 3: Launch Frontend (Next.js 14)
```bash
cd frontend
npm install
npm run dev
```
- Frontend Web App: `http://localhost:3000`

### Step 4: Run Tests & Verification
```bash
# Backend Pytest (35 tests):
pytest backend/tests/ -v

# Python Linter & Typecheck:
cd backend
ruff check .
mypy app

# Frontend Build Verification:
cd frontend
npm run build
```

---

## 11. User Action Items to Kick Off Next Sprint

To begin **Sprint 1 (Adaptive Quizzing & BKT Predictive Engine)**:

1. **Provide Gemini API Key**: ✅ **Configured** (`GEMINI_API_KEY` set in `.env` and `backend/.env`).
2. **Choose Voice / TTS Engine**:
   - **Option A (Recommended for Day 1)**: Browser-native Web Speech API (Free, zero setup, built into Chrome/Edge).
   - **Option B**: Cloud TTS (ElevenLabs / Google Cloud TTS for studio-grade human voices).
3. **Select Priority Benchmark Topics**: Confirm preferred topics for initial quiz calibration (e.g., Computer Science, Python, Data Structures, or AI/ML).
4. **Approve Sprint 1 Kickoff**: Authorize creating the `QuizSession` and `QuizQuestion` database models and service layer.
