# LuminaLearn AI — Project Master Guide & Team Execution Handbook

> **Project Aurora | LuminaLearn AI Core Documentation**
> _A Comprehensive Guide for Developers, Team Leads, Interviewers, and Technical Reviewers_

## 📌 1. Executive Project Overview

**LuminaLearn AI** is an enterprise-grade, AI-powered adaptive learning ecosystem designed to personalize education through Artificial Intelligence, Learning Analytics, Universal Accessibility (WCAG 2.1 AAA), and Explainable AI (XAI). Traditional Learning Management Systems (LMS) enforce rigid, linear curricula that treat all students identically. LuminaLearn AI dynamically diagnoses each learner's cognitive pace, knowledge gaps, and preferred VARK learning modality (Visual, Auditory, Read/Write, Kinesthetic) to construct a **100% personalized learning trajectory**.

### Core Pillars

1. **Socratic AI Agent Framework**: Guides learners using inquisitive, step-by-step Socratic questioning rather than handing out raw answers.
2. **Cognitive Personalization & VARK Adapters**: Adjusts explanations, UI themes, and content delivery based on cognitive diagnostics.
3. **Enterprise Monorepo Architecture**: High-performance FastAPI microservices coupled with a Next.js 14 App Router web client.
4. **Resilient Hybrid Infrastructure**: Engineered with zero-downtime local fallback mechanisms (SQLite + In-Memory Caching) alongside enterprise PostgreSQL + Redis support.

---

## ⚡ 2. Complete Tech Stack Specification

| Subsystem                 | Technology                      | Version / Spec     | Purpose & Architectural Role                                               |
| :------------------------ | :------------------------------ | :----------------- | :------------------------------------------------------------------------- |
| **Frontend Framework**    | **Next.js (App Router)**        | `14.2+` (React 18) | Server Components, Client CSR/SSR routing, SEO optimization                |
| **Frontend Language**     | **TypeScript**                  | `5.4+`             | Strict type safety, interface contracts, zero runtime type errors          |
| **Styling & System**      | **Tailwind CSS + Lucide Icons** | `3.4+`             | Glassmorphic dark theme, responsive design system, accessibility           |
| **Client State**          | **Zustand**                     | `4.5+`             | Light, reactive global state for auth session & learner profile            |
| **Backend Microservices** | **FastAPI**                     | `0.110+`           | High-performance Python async REST API, OpenAPI docs generation            |
| **Backend Language**      | **Python**                      | `3.11+`            | Async runtime, AI/ML execution, typing annotations                         |
| **ORM & Database Layer**  | **Async SQLAlchemy**            | `2.0+`             | Async ORM mapping, model schema management, cross-DB support               |
| **Primary Database**      | **PostgreSQL**                  | `16.2+`            | Enterprise relational storage for users, onboarding & learning data        |
| **Fallback Database**     | **SQLite (`aiosqlite`)**        | `0.22+`            | Embedded zero-config DB fallback when PostgreSQL is offline                |
| **Cache & Session**       | **Redis**                       | `7.2+`             | Refresh token revocation list, rate limiting & session cache               |
| **Fallback Cache**        | **In-Memory Token Store**       | Python Dict        | Resilient fallback for password reset & email tokens when Redis is offline |
| **Authentication**        | **JWT (PyJWT + Passlib)**       | `HS256` / Argon2id | Secure token pairs, HTTP-Only cookie & Authorization header support        |
| **AI LLM Engine**         | **Google Gemini API**           | `1.5 Pro / Flash`  | Socratic AI tutoring, diagnostic evaluation & content generation           |
| **Code Quality**          | **Ruff / Mypy / ESLint**        | Latest             | Automated Python linting/formatting and TypeScript static verification     |
| **Orchestration**         | **Docker & Docker Compose**     | `26.0+`            | Multi-container environment orchestration for dev & production             |

---

## 🚀 3. Team Implementation & Execution Guide

### Prerequisites

- **Node.js**: `v20.x` or higher
- **Python**: `3.11.x`
- **npm**: `v10.x`

### Step-by-Step Execution Workflow

#### Step 1: Environment Setup

Clone the monorepo and copy the environment template:

```bash
cp .env.example .env
```

#### Step 2: Backend Setup & Launch

```bash
cd backend
python -m venv .venv
# On Windows PowerShell:

.\.venv\Scripts\Activate.ps1
# Install dependencies:
pip install -r requirements.txt aiosqlite email-validator
# Launch backend development server:
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Backend API**: `http://127.0.0.1:8000`
- **Swagger Documentation**: `http://127.0.0.1:8000/docs`

> **Note on Resilient Mode**: If PostgreSQL and Redis are not running locally, the backend automatically uses **SQLite (`aiosqlite`)** and the **In-Memory Cache**. All authentication, signup, login, and onboarding features work out-of-the-box!

#### Step 3: Frontend Setup & Launch

In a separate terminal window:

```bash
cd frontend
npm install
npm run dev
```

- **Frontend App**: `http://localhost:3000`

#### Step 4: Verification & Building

To run a full production build and type-check verification:

```bash
# Frontend Build Verification
cd frontend
npm run build

# Backend Lint & Typecheck
cd backend
ruff check .
mypy app
```

---

## 🎯 4. Interviewer Questions & Answers (Comprehensive QA Pack)

### Q1: What problem does LuminaLearn AI solve compared to standard online learning platforms?

**Answer**: Standard LMS platforms (like Udemy or Coursera) deliver static, linear video courses that assume every student learns at the same rate and through the same modality. LuminaLearn AI uses diagnostic cognitive profiling (VARK model) and Socratic AI agents to personalize subject sequences, adapt content representations (visual vs. text vs. interactive), and actively guide students through inquiry rather than passive content consumption.

### Q2: Why did you choose Next.js 14 App Router over a SPA framework like Vite or standard React CRA?

**Answer**: Next.js 14 App Router provides hybrid rendering (Server Components + Client Components), automatic route pre-rendering, built-in layout nesting, and superior SEO performance out of the box. Server components reduce client-side bundle size, while client components manage interactive states (such as onboarding quizzes and live AI tutoring chats).

### Q3: Why did you select FastAPI for the backend microservice architecture instead of Node.js/Express or Django?

**Answer**: FastAPI built on Starlette and Pydantic provides asynchronous `async/await` execution, high throughput comparable to Go/Node.js, automatic Pydantic input validation, and instant OpenAPI (Swagger) document generation. Furthermore, Python is the native language for AI/ML libraries (Google Gemini SDK, LangChain, Qdrant), allowing seamless integration between API routes and AI pipelines.

### Q4: How does the Socratic AI agent differ from standard ChatGPT-style direct Q&A?

**Answer**: Direct AI prompt responses give students immediate answers, which leads to passive memorization rather than deep comprehension. LuminaLearn AI prompts the LLM with Socratic system constraints: the AI asks probing questions, breaks down complex problems into sub-steps, provides hint ladders, and validates student reasoning before revealing final answers.

### Q5: How is user authentication implemented, and how are security risks mitigated?

**Answer**: Authentication uses JSON Web Tokens (JWT) with an Access Token (15 min expiry) and Refresh Token (7 days expiry). Passwords are encrypted using standard hashing (Argon2id/Bcrypt). Tokens are returned via JSON response and HTTP-Only cookies to protect against Cross-Site Scripting (XSS). User roles (`student`, `teacher`, `admin`) are embedded in token claims and verified by FastAPI dependency injection (`require_role`).

### Q6: How does the system handle infrastructure unavailability (e.g., PostgreSQL or Redis being down)?

**Answer**: The system implements an **Adaptive Resilience Layer**:

- **Database**: If PostgreSQL is unreachable or `USE_SQLITE=true` is set, `app/core/database.py` dynamically selects `sqlite+aiosqlite:///./luminalearn.db`, auto-creating missing tables on startup via SQLAlchemy 2.0.
- **Cache**: If Redis is offline, `RedisClientWrapper` in `app/core/redis.py` falls back to an in-memory dictionary cache with TTL handling, ensuring login, password resets, and email verifications never crash.

### Q7: What is the VARK model and how is it integrated into the system?

**Answer**: VARK stands for Visual, Auditory, Read/Write, and Kinesthetic learning styles. During onboarding, students complete a diagnostic assessment. The preferred modality is stored in their profile (`preferred_modality`). The frontend adapts layout views (e.g., displaying interactive diagrams for Visual, text summaries for Read/Write), and AI prompts inject style constraints so explanations match the student's cognitive preference.

### Q8: How are user sessions maintained across page reloads in Next.js?

**Answer**: The frontend uses a Zustand store (`useAuthStore`) combined with `localStorage` persistence and token verification (`initializeAuth`). On initial app mount, `initializeAuth` retrieves stored tokens, calls `/api/v1/auth/me` to fetch current user state, and seamlessly attempts token refresh if the access token has expired.

### Q9: How do you prevent AI hallucinations and keep the AI responses accurate?

**Answer**: We use structured system prompts, temperature controls (low temperature ~0.2 for factual concepts), and RAG (Retrieval-Augmented Generation) context injection from curated educational content stored in Qdrant vector database.

### Q10: How is the monorepo structured for scalability across multiple engineering teams?

**Answer**: The repository follows clear domain separation:

- `/frontend`: Web application code, components, and pages.
- `/backend`: API microservice with clean layer separation (`app/core`, `app/api`, `app/models`, `app/services`, `app/repositories`).
- `/ai` & `/ml`: AI prompt frameworks and learning analytics.
- `/database`: Master DDL schemas and migration scripts.
- `/docs`: SSOT documentation.

---

## 🔍 5. Reviewer & Lead Architect Questions & Answers (Code Review QA)

### Q1: In `backend/app/api/deps.py`, how is authorization enforced across endpoint routes?

**Answer**: FastAPI dependencies provide declarative authorization. `get_current_user` extracts the JWT from either the `Authorization: Bearer` header or HTTP-only cookies, decodes the payload, validates expiration, and fetches the `User` ORM instance. `get_current_active_user` enforces account active status. `require_role([UserRole.TEACHER, UserRole.ADMIN])` creates a reusable dependency that blocks unauthorized access with HTTP 403 Forbidden.

### Q2: Why did you update SQLAlchemy model column definitions from `postgresql.UUID` to `sqlalchemy.Uuid`?

**Answer**: `sqlalchemy.dialects.postgresql.UUID` is postgres-specific and throws dialect errors when executed against SQLite. Using `sqlalchemy.Uuid(as_uuid=True)` introduced in SQLAlchemy 2.0 provides native cross-database compatibility: it compiles to `UUID` in PostgreSQL and `CHAR(32)`/`VARCHAR(36)` in SQLite while preserving native Python `uuid.UUID` objects in the application layer.

### Q3: Why is `asynccontextmanager` lifespan used in `backend/app/main.py` instead of `@app.on_event("startup")`?

**Answer**: FastAPI and Starlette have deprecated `@app.on_event("startup")` and `"shutdown"` in favor of standard ASGI `lifespan` context managers. Using `asynccontextmanager` cleanly handles startup operations (like `await init_db()`) and shutdown cleanups in a single, standard pythonic block.

### Q4: How are CORS headers configured and why is credentials support required?

**Answer**: `CORSMiddleware` in `main.py` explicitly allows trusted origins (`http://localhost:3000`, `http://127.0.0.1:3000`). `allow_credentials=True` is enabled so HTTP-only authentication cookies can be transmitted securely between the Next.js frontend and FastAPI backend during cross-origin AJAX/fetch requests.

### Q5: How do you handle password reset tokens securely without risking email enumeration attacks?

**Answer**: In `AuthService.request_password_reset`, if a non-existent email is submitted, the API still returns a generic success response ("If an account exists with this email, a reset token has been issued"). This prevents malicious actors from checking which emails exist in the database. In development, the token is returned in `detail` for convenience.

### Q6: What design pattern is used in `backend/app/repositories`?

**Answer**: The **Repository Pattern**. Database access logic (CRUD operations, query filtering, session management) is isolated in repository classes (e.g., `UserRepository`). Domain services (`AuthService`, `OnboardingService`) depend on repositories rather than writing raw SQL or inline ORM queries, making the code testable and easy to maintain.

### Q7: How does `useAuthStore` handle error handling during asynchronous auth actions?

**Answer**: Zustand store methods (`login`, `registerStudent`) set `isLoading: true` and `error: null` before making API calls via `authService`. If an HTTP exception or network error occurs, the catch block updates `error: err.message` and resets `isLoading: false`, re-throwing the error so page components can display targeted field alerts.

### Q8: In `reset-password/page.tsx` and `verify-email/page.tsx`, why are search params wrapped in Next.js `<Suspense>`?

**Answer**: Next.js 14 requires client components reading URL query parameters via `useSearchParams()` to be wrapped inside a `<Suspense>` boundary. Without `<Suspense>`, Next.js throws a static generation build error because query params cannot be determined during static HTML pre-rendering.

### Q9: How are Pydantic schemas separated from SQLAlchemy ORM models?

**Answer**:

- **ORM Models (`app/models`)**: Define database table structures, foreign key constraints, indexes, and relationship mappings.
- **Pydantic Schemas (`app/schemas`)**: Define API request payloads (`LoginRequest`, `StudentRegisterRequest`) and response contracts (`UserResponse`, `TokenResponse`) with runtime validation (e.g., `EmailStr`, min length rules). `model_config = ConfigDict(from_attributes=True)` enables seamless conversion from ORM models to Pydantic responses.

### Q10: What is the testing strategy for the backend microservices?

**Answer**: The test suite uses **Pytest** with `pytest-asyncio` and `httpx.AsyncClient`. Tests use an isolated test database (SQLite in-memory or PostgreSQL test schema) to test auth routes, onboarding submission, and role authorization without modifying production/development data.

---

## 📌 6. Summary Checklist for Team Onboarding

- [x] Monorepo cloned and `.env` configured.
- [x] Python virtual environment created and packages installed.
- [x] Backend running cleanly at `http://127.0.0.1:8000` with Swagger docs available.
- [x] Next.js frontend running cleanly at `http://localhost:3000`.
- [x] Verification tests passed for student registration, login, and password recovery.
- [x] Code standard check (`ruff`, `mypy`, `npm run build`) passing with zero errors.
