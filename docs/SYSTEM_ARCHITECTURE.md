# LUMINALEARN AI — SYSTEM ARCHITECTURE & TECH STACK LOCK

> **Project Aurora | Phase 1: Product Strategy — Step 5**  
> **Document Version:** 1.0.0  
> **Classification:** Master System Architecture & Technical Specifications (SSOT)  
> **Status:** Approved / Technical Baseline Locked  
> **Target Audience:** Software Architects, Lead Engineers, DevOps / SRE, Frontend & Backend Developers, AI/ML Engineers  

---

## 1. Executive Summary & Architecture Overview

### 1.1 Architectural Vision
**LuminaLearn AI** (*Project Aurora*) is built on a modern, decoupled, microservices-ready architecture engineered to process real-time cognitive learning telemetry, deliver sub-second Socratic AI guidance, and maintain 100% universal accessibility (WCAG 2.1 AAA).

This **System Architecture & Tech Stack Lock Document** formalizes the end-to-end technical blueprint for LuminaLearn AI. It locks down the technology stack, defines data flow pipelines from the Student UI to the Gemini AI/RAG engine, specifies the database schema architecture, and details authentication and infrastructure setup.

```
+---------------------------------------------------------------------------------------------------+
|                                 END-TO-END SYSTEM DATA FLOW                                       |
|                                                                                                   |
|  [STUDENT]                                                                                        |
|     │                                                                                             |
|     ▼                                                                                             |
|  [NEXT.JS 14+ FRONTEND] (React 18 / TypeScript / Zustand / TanStack Query / Tailwind CSS)         |
|     │                                                                                             |
|     ▼  (HTTPS / REST APIs / WebSockets / OAuth2 JWT)                                             |
|  [FASTAPI BACKEND] (Python 3.11+ / Async SQLAlchemy / Pydantic v2 / Redis Cache)                  |
|     │                                                                                             |
|     ├───────────────────────────────┐                                                             |
|     ▼                               ▼                                                             |
|  [POSTGRESQL 16 DB]          [AI SERVICE & SOCRATIC AGENT]                                        |
|  (Users, Graphs, Mastery)    (Socratic Guardrails, Cognitive Load Balancer)                       |
|                                     │                                                             |
|                                     ├───────────────────────────────┐                             |
|                                     ▼                               ▼                             |
|                              [GEMINI AI API]                [RAG ENGINE & VECTOR DB]              |
|                              (Gemini 1.5 Pro/Flash)         (Qdrant Vector DB / Embeddings)     |
|                                     │                               │                             |
|                                     └───────────────┬───────────────┘                             |
|                                                     ▼                                             |
|                                            [RESPONSE ENGINE]                                      |
|                                            (XAI Hints / Telemetry)                                |
+---------------------------------------------------------------------------------------------------+
```

### 1.2 Document Information & Governance

| Attribute | Specification |
| :--- | :--- |
| **Document Title** | System Architecture & Tech Stack Lock |
| **Project Codename** | Project Aurora |
| **Product Name** | LuminaLearn AI |
| **Document Owner** | Chief Software Architect & Principal Staff Engineer |
| **Approved By** | Technical Lead, Backend Lead, Frontend Lead, AI/ML Lead |
| **Baseline Dependencies** | `PRODUCT_CHARTER.md`, `MARKET_RESEARCH.md`, `STAKEHOLDER_ANALYSIS.md`, `ENGINEERING_STANDARDS.md` |
| **Lifecycle Phase** | SDLC Phase 1 (System Architecture & Stack Freeze) |

---

## 2. Definitive Tech Stack Lock

All technologies, frameworks, and tools are **LOCKED** for Project Aurora. Modifications require a formal Architecture Decision Record (ADR) sign-off.

```
+-----------------------------------------------------------------------------------+
|                             DEFINITIVE TECH STACK LOCK                            |
|                                                                                   |
|  FRONTEND:   Next.js 14+ (App Router) | React 18 | TypeScript 5+ | Zustand        |
|  BACKEND:    FastAPI 0.110+ | Python 3.11+ | Async SQLAlchemy 2.0 | Pydantic v2   |
|  DATABASE:   PostgreSQL 16 | Redis 7 (Caching & Sessions)                     |
|  AI & RAG:   Google Gemini 1.5 Pro / Flash | Qdrant Vector DB | LangChain       |
|  DEPOYMENT:  Docker | Kubernetes | Helm | AWS / GCP Hyperscale                    |
+-----------------------------------------------------------------------------------+
```

### 2.1 Tech Stack Matrix

| Tier | Component / Tool | Version | Selection Justification |
| :--- | :--- | :---: | :--- |
| **Frontend Framework** | **Next.js** | `14.2+` | React 18 App Router, Server Components, SSR/SSG for SEO, optimized bundle splitting. |
| **UI Library** | **React** | `18.3+` | Concurrent mode, transitions, stable web ecosystem. |
| **Language (Frontend)** | **TypeScript** | `5.4+` | Strict static typing, eliminates runtime type errors across components and API models. |
| **State Management** | **Zustand & TanStack Query** | `v4 / v5` | Lightweight client state (Zustand) + async server state caching (TanStack Query v5). |
| **Styling & Theme** | **Tailwind CSS & CSS Tokens** | `3.4+` | Rapid accessible UI component styling, WCAG 2.1 AAA contrast tokens. |
| **Backend Framework** | **FastAPI** | `0.110+` | Asynchronous Python REST microservices, native OpenAPI spec generation, sub-ms routing. |
| **Language (Backend)** | **Python** | `3.11+` | Native async performance, deep ecosystem for AI/ML and Bayesian network algorithms. |
| **ORM / Data Access** | **Async SQLAlchemy** | `2.0+` | Async PostgreSQL ORM with Alembic migration governance. |
| **Schema Validation** | **Pydantic** | `v2.7+` | High-performance Rust-backed data validation envelope for APIs and environment config. |
| **Primary Database** | **PostgreSQL** | `16.2+` | Relational ACID database for users, knowledge graphs, and mastery telemetry. |
| **Cache & Event Broker** | **Redis** | `7.2+` | Distributed in-memory session store, API response caching, Celery task queue broker. |
| **Vector Database** | **Qdrant** | `1.9+` | Ultra-fast Rust vector database for RAG concept embeddings and hybrid search. |
| **AI LLM Foundation** | **Google Gemini** | `1.5 Pro / Flash` | Long-context window (1M+ tokens), sub-second inference speed, native multi-modal capabilities. |
| **AI Orchestration** | **LangChain / LlamaIndex** | `0.1+` | Socratic agent prompt chaining, RAG retrieval management, memory state retention. |
| **Containerization** | **Docker & Docker Compose**| `26.0+` | Multi-stage rootless container builds, local developer stack orchestration. |
| **Orchestration** | **Kubernetes & Helm** | `1.29+` | Multi-region auto-scaling container orchestration. |

---

## 3. End-to-End Data Flow Architecture

The data pipeline traces a student's interaction from the UI through to the Gemini AI engine and vector search.

```
+-----------------------------------------------------------------------------------+
|                        STUDENT INTERACTION DATA FLOW PIPELINE                     |
|                                                                                   |
|  [1. STUDENT] ──► [2. NEXT.JS UI] ──► [3. FASTAPI API] ──► [4. REDIS CACHE]       |
|                                                                 │                 |
|                                                                 ▼                 |
|  [8. RESPONSE] ◄── [7. GEMINI AI] ◄── [6. RAG ENGINE] ◄── [5. POSTGRES / QDRANT]  |
+-----------------------------------------------------------------------------------+
```

### 3.1 Step-by-Step Data Journey

1. **Student Initiation:** Student submits a query or attempts a math problem on the Next.js frontend (e.g., "How do I solve $x^2 - 5x + 6 = 0$?").
2. **Next.js Client Processing:** Client validates input locally, injects telemetry headers (session ID, VARK preference), and dispatches an authenticated HTTPS POST payload to FastAPI.
3. **FastAPI Ingress & Auth:** FastAPI receives request, validates Bearer JWT token via OAuth2 middleware, and checks Redis cache for existing session state.
4. **Knowledge Graph & Telemetry Lookup:** Backend queries PostgreSQL for student's current Bayesian mastery score for the concept (`kn_quadratics_101`).
5. **RAG & Vector Retrieval:** AI Service embeds query, executes hybrid search against Qdrant vector database to retrieve verified textbook concepts and worked hint scaffolds.
6. **Socratic AI Prompt Assembly:** Socratic Agent constructs prompt with:
   - System Guardrails (Never provide direct answers).
   - Concept Context (Qdrant RAG retrieval).
   - Learner Profile (Postgres Bayesian mastery score + VARK preference).
7. **Gemini 1.5 Inference Execution:** Payload dispatched to Gemini 1.5 API with zero-data-retention headers (`X-GOOG-DATA-POLICY: ZERO-RETENTION`).
8. **Response Streaming & Telemetry Logging:** Gemini streams Socratic hint response back to FastAPI. FastAPI logs hesitation time and interaction telemetry asynchronously to Redis stream and returns clean JSON envelope to Next.js.
9. **UI Render:** Next.js renders interactive step-by-step hint card with LaTeX math support (`KaTeX`) and screen-reader accessibility attributes.

---

## 4. Repository Structure & Workspace Blueprint

Preparing for the GitHub repository and VS Code environment setup.

### 4.1 Monorepo Directory Architecture

```
LUMINALEARN_AI/
├── .github/                        # CI/CD Workflows & Issue/PR Templates
├── .vscode/                        # Workspace Editor & Debugger Settings
│   ├── extensions.json             # Recommended VS Code Extensions
│   ├── launch.json                 # Fast Debugger configurations for Next.js & FastAPI
│   └── settings.json               # Workspace Linter/Formatter Auto-Save Settings
├── ai/                             # Socratic AI Agents, Prompts, RAG Pipelines
├── backend/                        # FastAPI Python Microservices App
│   ├── app/
│   │   ├── api/v1/                 # API Endpoints (auth, tutor, knowledge, analytics)
│   │   ├── core/                   # Security, DB, Redis, Logging configs
│   │   ├── domain/                 # Business Domain Logic
│   │   ├── models/                 # SQLAlchemy DB Models
│   │   └── schemas/                # Pydantic DTO schemas
│   ├── tests/                      # Pytest unit & integration tests
│   └── pyproject.toml              # Dependencies (Poetry / UV)
├── frontend/                       # Next.js 14+ React App
│   ├── src/
│   │   ├── app/                    # App Router Pages & Layouts
│   │   ├── components/             # UI Component Library (WCAG AAA)
│   │   ├── hooks/                  # Custom React Hooks
│   │   ├── services/               # API Service Clients (TanStack Query)
│   │   ├── stores/                 # Zustand State Stores
│   │   └── styles/                 # Tailwind & CSS Tokens
│   ├── package.json
│   └── tsconfig.json
├── database/                       # SQL Schemas & Alembic Migrations
├── deployment/                     # Helm Charts & Terraform Specs
├── docker/                         # Docker Compose Dev/Test/Prod Stacks
├── docs/                           # Markdown Documentation SSOT
└── scripts/                        # Dev Automation Scripts
```

### 4.2 Workspace VS Code Configuration

#### `.vscode/settings.json`
```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": "explicit",
    "source.fixAll.eslint": "explicit"
  },
  "python.defaultInterpreterPath": "./backend/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "typescript.tsdk": "frontend/node_modules/typescript/lib"
}
```

#### `.vscode/extensions.json`
```json
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "charliermarsh.ruff",
    "ms-python.python",
    "ms-python.vscode-pylance",
    "bradlc.vscode-tailwindcss",
    "eamodio.gitlens"
  ]
}
```

---

## 5. Database Schema & Data Models

PostgreSQL 16 relational database schema powering LuminaLearn AI.

```
+-----------------------------------------------------------------------------------+
|                           DATABASE ENTITY-RELATIONSHIP MODEL                      |
|                                                                                   |
|   +-------------------+          +-------------------+          +--------------+  |
|   |       USERS       | 1      N |   LEARNING_SESSIONS| 1      N | TELEMETRY_LOGS|  |
|   +-------------------+          +-------------------+          +--------------+  |
|   | id (PK)           |          | id (PK)           |          | id (PK)      |  |
|   | email             |<-------->| user_id (FK)      |<-------->| session_id(FK|  |
|   | password_hash     |          | started_at        |          | cognitive_load|  |
|   | role              |          +-------------------+          +--------------+  |
|   +-------------------+                                                           |
|             │                                                                     |
|             │ 1                                                                   |
|             ▼ N                                                                   |
|   +-------------------+          +-------------------+                            |
|   |  MASTERY_SCORES   | N      1 |  KNOWLEDGE_NODES  |                            |
|   +-------------------+          +-------------------+                            |
|   | user_id (FK)      |<-------->| id (PK)           |                            |
|   | node_id (FK)      |          | concept_code      |                            |
|   | mastery_probability|         | parent_node_id    |                            |
|   +-------------------+          +-------------------+                            |
+-----------------------------------------------------------------------------------+
```

### 5.1 Relational Schema Definitions (DDL)

```sql
-- Enums
CREATE TYPE user_role AS ENUM ('student', 'teacher', 'admin', 'parent');
CREATE TYPE vark_modality AS ENUM ('visual', 'auditory', 'read_write', 'kinesthetic');

-- 1. Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'student',
    preferred_modality vark_modality DEFAULT 'visual',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2. Knowledge Nodes Table (Bayesian Graph Nodes)
CREATE TABLE knowledge_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    concept_code VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    subject VARCHAR(100) NOT NULL,
    parent_node_id UUID REFERENCES knowledge_nodes(id),
    difficulty_level FLOAT DEFAULT 0.5,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. Student Mastery Scores Table
CREATE TABLE mastery_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    node_id UUID REFERENCES knowledge_nodes(id) ON DELETE CASCADE,
    mastery_probability FLOAT DEFAULT 0.1, -- Bayesian P(L)
    last_assessed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, node_id)
);

-- 4. Learning Sessions Table
CREATE TABLE learning_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    started_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMPTZ,
    total_interactions INT DEFAULT 0
);

-- 5. Telemetry Logs Table
CREATE TABLE telemetry_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES learning_sessions(id) ON DELETE CASCADE,
    node_id UUID REFERENCES knowledge_nodes(id),
    hesitation_time_ms INT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    cognitive_load_index FLOAT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

---

## 6. Authentication & Security Architecture

LuminaLearn AI utilizes an enterprise-grade **OAuth2 with JWT (JSON Web Tokens)** authentication architecture.

```
+-----------------------------------------------------------------------------------+
|                        AUTHENTICATION & JWT AUTHORIZATION FLOW                    |
|                                                                                   |
|  [CLIENT] ──► 1. POST /api/v1/auth/login ──────────► [FASTAPI AUTH ROUTER]       |
|    │                                                        │                     |
|    │                                                        ▼                     |
|    │                                               2. Verify Pass Hash (Argon2)   |
|    │                                                        │                     |
|    │                                                        ▼                     |
|    │ ◄── 3. Return { access_token, refresh_token } ─────────┘                     |
|    │                                                                              |
|    ▼                                                                              |
|  4. GET /api/v1/tutor/chat (Header: Bearer <access_token>)                        |
|    │                                                                              |
|    ▼                                                                              |
|  [FASTAPI AUTH MIDDLEWARE] ──► 5. Validate Signature & Extract User ID & Role     |
+-----------------------------------------------------------------------------------+
```

### 6.1 Security Protocol Specifications
* **Password Hashing:** Argon2id hashing via Passlib.
* **Token Standard:** JWT with RS256 signing (Public/Private key pair).
* **Token Expiration:** Access Token = 15 minutes; Refresh Token = 7 days (Stored in HttpOnly SameSite=Strict cookies).
* **Role-Based Access Control (RBAC):** Middleware checks scopes (`student`, `teacher`, `admin`) on every endpoint.

---

## 7. Execution Roadmap to Phase 2 (Code Implementation)

With the System Architecture & Tech Stack locked, the project transitions into execution across five immediate milestones:

```
  [1. GitHub Repo Setup] ──► [2. VS Code Setup] ──► [3. Database Init] ──► [4. First API] ──► [5. First Frontend & AI Integration]
```

1. **Milestone 1: GitHub Repository Initialization:** Push directory layout, CI/CD workflows, `.gitignore`, and issue templates to GitHub.
2. **Milestone 2: VS Code Workspace Configuration:** Apply workspace `.vscode/` settings, linters (`ruff`, `eslint`), and debuggers.
3. **Milestone 3: Database & Migration Engine Setup:** Initialize PostgreSQL 16 container, apply SQL DDL schema, configure Alembic migrations.
4. **Milestone 4: First FastAPI Microservice API:** Implement `/health` and `/api/v1/auth/login` endpoints with unit tests.
5. **Milestone 5: First Next.js Frontend & Gemini AI Integration:** Implement student dashboard UI and connect Socratic LuminaTutor to Gemini 1.5 API.

---
