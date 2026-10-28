# LUMINALEARN AI — ENGINEERING STANDARDS & ARCHITECTURAL HANDBOOK

> **Project Aurora | Phase 1: Product Strategy — Step 4**  
> **Document Version:** 1.0.0  
> **Classification:** Master Engineering Standards & Architectural Handbook (SSOT)  
> **Status:** Approved / Technical Baseline  
> **Target Audience:** Software Architects, Engineering Managers, Tech Leads, Frontend & Backend Engineers, DevOps / SRE, QA Lead, Security & Compliance Officers  

---

## 1. Executive Summary & Document Governance

### 1.1 Engineering Vision & North Star
**LuminaLearn AI** (*Project Aurora*) is an enterprise-grade, AI-first adaptive learning ecosystem designed to revolutionize global education. Delivering dynamic Bayesian knowledge graph tracking, sub-second Socratic AI tutoring, real-time cognitive load adjustment, native universal accessibility (WCAG 2.1 AAA), and Explainable AI (XAI) telemetry requires an unshakeable engineering foundation.

This **Engineering Standards Document** serves as the official technical handbook for LuminaLearn AI. It defines the foundational engineering principles, repository architecture, coding conventions, Git workflow, API specifications, environment strategies, quality gates, and sprint workflows that every developer, team, and automated pipeline must adhere to.

```
+-----------------------------------------------------------------------------------+
|                        ENGINEERING FOUNDATION ARCHITECTURE                        |
|                                                                                   |
|  [FOUNDATIONAL PRINCIPLES] ──► Clean Code, SOLID, Zero-Trust, Shift-Left Testing  |
|            │                                                                      |
|            ▼                                                                      |
|  [STANDARDIZED WORKFLOWS] ──► Conventional Commits, GitFlow, SemVer, Quality Gates |
|            │                                                                      |
|            ▼                                                                      |
|  [UNIFIED ARCHITECTURE]   ──► Modular Monolith / Microservices, OpenAPI, Docker   |
|            │                                                                      |
|            ▼                                                                      |
|  [EXCELLENCE & COMPLIANCE]──► WCAG 2.1 AAA, FERPA/COPPA/GDPR-K, 99.99% Uptime    |
+-----------------------------------------------------------------------------------+
```

### 1.2 Document Information & Ownership

| Attribute | Specification |
| :--- | :--- |
| **Document Title** | Engineering Standards & Architectural Handbook |
| **Project Codename** | Project Aurora |
| **Product Name** | LuminaLearn AI |
| **Document Owner** | Chief Software Architect & Principal Staff Engineer |
| **Approved By** | Technical Lead, Engineering Manager, DevOps Lead |
| **Baseline Dependencies** | `PRODUCT_CHARTER.md` (v1.0.0), `MARKET_RESEARCH.md` (v1.0.0), `STAKEHOLDER_ANALYSIS.md` (v1.0.0) |
| **Lifecycle Phase** | SDLC Phase 1 (Product Strategy & Technical Blueprint) |

### 1.3 Systemic Alignment
This engineering handbook operationalizes the strategic vision set forth in the baseline documents:
* **Product Charter Alignment:** Translates the 7 core values (Human-Centered AI, Hyper-Personalization, Universal Accessibility, XAI, Privacy-First, Continuous Innovation, Continuous Learning) into strict engineering standards.
* **Stakeholder Framework Alignment:** Enforces quality gates that satisfy all 20 stakeholder profiles—guaranteeing developer velocity (SH-10), QA rigour (SH-11), SRE stability (SH-17), privacy compliance (SH-20), and accessibility standards (SH-16).

---

## 2. Foundational Engineering Principles

LuminaLearn AI operates under seven non-negotiable technical philosophies designed by enterprise software architects.

```
+-----------------------------------------------------------------------------------+
|                         SEVEN ENGINEERING PHILOSOPHIES                            |
|                                                                                   |
|  1. Coding Philosophy       ──► Clean Code, KISS, DRY, SOLID, Defensive           |
|  2. Architecture Philosophy ──► Domain-Driven Design, Async Event Telemetry       |
|  3. Scalability Philosophy  ──► Stateless Services, Layered Caching, Auto-scaling |
|  4. Maintainability Philosophy► Explicit Interfaces, Strict Typing, Zero Debt     |
|  5. Documentation Philosophy► Docs-as-Code, Living ADRs, OpenAPI SSOT             |
|  6. Security Philosophy     ──► Zero-Trust, Shift-Left, Zero-Data-Retention AI    |
|  7. Testing Philosophy      ──► Test Pyramid, Contract Testing, Non-Deterministic QA|
+-----------------------------------------------------------------------------------+
```

### 2.1 Coding Philosophy
* **Keep It Simple, Stupid (KISS):** Avoid over-engineering. Write code for clarity first, cleverness never. Simple, readable code beats hyper-complex abstractions.
* **Don't Repeat Yourself (DRY):** Abstract duplicate domain logic into centralized utility modules or shared domain libraries. However, prefer duplication over wrong abstraction.
* **SOLID Principles:** Enforce Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion across all module boundaries.
* **Clean Code & Self-Documentation:** Code must read like plain English. Variable and function names must express intent clearly, eliminating the need for comments explaining *what* code does (comments should explain *why* non-obvious trade-offs were made).
* **Defensive Programming:** Never trust external input. Validate all data payloads at API boundaries using strict schema validation (Pydantic / TypeScript types) and fail fast with meaningful error states.

### 2.2 Architecture Philosophy
* **Domain-Driven Design (DDD):** Organize code strictly by domain contexts (e.g., `knowledge_graph`, `socratic_tutor`, `assessment`, `analytics`, `user_identity`) rather than generic technical layers (`controllers`, `services`, `helpers`).
* **Modular Monolith to Microservices Evolution:** Start with a cleanly decoupled Modular Monolith with strict boundary enforcement, allowing seamless extraction into isolated microservices as domain scaling mandates require.
* **Decoupled AI Pipeline:** Isolate heavy LLM and vector search orchestration behind async interfaces and broker queues (Celery/Redis/Kafka), ensuring AI latency never blocks core HTTP request threads.
* **Event-Driven Async Telemetry:** Capture clickstream, cognitive load signals, and interaction logs asynchronously via event pipelines, decoupling real-time learning analytics from user-facing transactions.

### 2.3 Scalability Philosophy
* **Stateless API Services:** Every web application backend service must be 100% stateless, delegating session management to distributed Redis stores and JWT tokens to allow infinite horizontal scaling.
* **Multi-Layered Caching Hierarchy:** Implement a 3-tier caching model: Browser/CDN edge caching $\rightarrow$ Application Redis cache $\rightarrow$ Database query/read replicas.
* **Database Read/Write Separation:** Isolate heavy transactional writes (PostgreSQL primary) from high-throughput read traffic (PostgreSQL read-replicas, Redis vector indices).
* **Graceful Degradation & Circuit Breakers:** If third-party AI APIs (e.g., OpenAI, Vertex AI) experience latency or downtime, circuit breakers must automatically fall back to cached local models or static diagnostic hint paths without crashing the user interface.

### 2.4 Maintainability Philosophy
* **Strict Static Typing:** Python code MUST use type annotations enforced by `mypy` in strict mode. Frontend JavaScript MUST be 100% TypeScript with `noImplicitAny` enabled.
* **Explicit Interfaces:** Define strict interface contracts between frontend components, backend services, and external APIs. Implicit data shapes are strictly prohibited.
* **Low Coupling, High Cohesion:** Modules must depend only on abstractions, never internal implementations of other modules.
* **Continuous Refactoring Culture:** Technical debt must be tracked in the sprint backlog and allocated a mandatory 15% effort quota in every sprint cycle.

### 2.5 Documentation Philosophy
* **Documentation-as-Code (Docs-as-Code):** All documentation lives alongside the codebase in Markdown format within the `docs/` folder, subject to code review and version control.
* **Architecture Decision Records (ADR):** Any significant technical design, library choice, or architectural trade-off MUST be documented in an ADR before implementation begins.
* **Self-Documenting APIs:** REST APIs MUST generate interactive OpenAPI 3.0 (Swagger) documentation automatically from code schemas (FastAPI/Pydantic). Manual API documentation is forbidden.

### 2.6 Security Philosophy
* **Zero-Trust Architecture:** Authenticate and authorize every internal and external request. Trust no network boundary.
* **Shift-Left Security:** Integrate automated static application security testing (SAST), software bill of materials (SBOM) scanning, and dependency vulnerability checks directly into CI pipelines.
* **OWASP Top 10 Mitigation:** Enforce strict protections against SQL injection, XSS, CSRF, broken authentication, and unauthorized direct object references (IDOR).
* **Zero-Data-Retention AI Compliance:** All integrations with external AI service providers MUST enforce zero-data-retention headers, ensuring student input payloads are never stored or used to retrain foundation models (FERPA/COPPA/GDPR-K).

### 2.7 Testing Philosophy
* **The Testing Pyramid:** Enforce a balanced test distribution: 60% Unit Tests, 25% Integration Tests, 10% End-to-End (E2E) Tests, and 5% Load/Contract Tests.
* **Contract Testing:** Verify API contracts between frontend, backend, and microservices using consumer-driven contract tests (Pact framework).
* **Non-Deterministic AI Testing:** Validate AI Socratic tutor outputs using deterministic evaluation harnesses, semantic similarity scoring, and LLM-as-a-judge regression suites.
* **Accessibility Quality Gates:** Every frontend release must execute automated WCAG 2.1 AAA accessibility audits (axe-core/Playwright) prior to production deployment.

---

## 3. Repository Architecture & Directory Blueprint

LuminaLearn AI utilizes an enterprise monorepo directory layout designed for modular clarity, separation of concerns, and team scalability.

### 3.1 Complete Root-to-Leaf Directory Tree

```
LUMINALEARN_AI/
├── .github/                        # GitHub Actions CI/CD workflows, templates & governance
│   ├── ISSUE_TEMPLATE/             # Standardized GitHub Issue templates
│   │   ├── bug_report.md           # Defect report template
│   │   ├── feature_request.md      # New feature specification template
│   │   └── refactor_spec.md        # Technical debt refactoring template
│   ├── PULL_REQUEST_TEMPLATE.md    # Pull Request description and DoD checklist
│   └── workflows/                  # CI/CD Pipeline Automation
│       ├── ci_backend.yml          # Backend linting, mypy, pytest, security scan
│       ├── ci_frontend.yml         # Frontend ESLint, TypeScript check, Vitest, Playwright
│       ├── ci_ai_eval.yml          # AI model safety & Socratic regression eval suite
│       ├── ci_accessibility.yml    # Automated WCAG 2.1 AAA accessibility audit
│       └── cd_deploy.yml           # Multi-stage continuous deployment pipeline
├── ai/                             # Artificial Intelligence & Socratic Agent Framework
│   ├── agents/                     # Specialized AI Agent implementations
│   │   ├── socratic_tutor.py       # LuminaTutor Socratic dialogue manager
│   │   ├── load_adjuster.py        # Real-time cognitive load balancer agent
│   │   └── resource_synthesizer.py # VARK multi-modal resource generator agent
│   ├── prompts/                    # Versioned Prompt Engineering registry
│   │   ├── socratic_guardrails.py  # Zero-direct-answer prompt templates
│   │   └── assessment_rubrics.py   # Automated rubric evaluation prompts
│   ├── rag/                        # Retrieval-Augmented Generation (RAG) module
│   │   ├── embeddings.py           # Vector embedding pipeline
│   │   ├── retriever.py            # Vector search & hybrid retrieval logic
│   │   └── vector_store.py         # Pinecone/Qdrant vector DB connector
│   └── evaluation/                 # AI Model Evaluation & Regression Testing
│       ├── eval_harness.py         # Deterministic LLM evaluation runner
│       └── benchmarks/             # Test datasets for Socratic accuracy & safety
├── ml/                             # Machine Learning & Adaptive Engine
│   ├── models/                     # Trained ML model definitions & serialized weights
│   │   ├── bayesian_graph.py       # Dynamic Bayesian Knowledge Graph engine
│   │   └── decay_curve.py          # Ebbinghaus cognitive memory decay model
│   ├── pipelines/                  # ML Data Engineering & Training Pipelines
│   │   ├── feature_store.py        # Telemetry feature extractor
│   │   └── train_knowledge_graph.py# Offline Bayesian network weight recalibration
│   └── notebooks/                  # Experimental research Jupyter notebooks
├── backend/                        # Backend FastAPI Microservices Application
│   ├── app/                        # Main Application Package
│   │   ├── api/                    # API Routing Layer (FastAPI Routers)
│   │   │   ├── v1/                 # API Version 1 Routers
│   │   │   │   ├── auth.py         # OAuth2 / JWT Authentication endpoints
│   │   │   │   ├── knowledge.py    # Knowledge Graph & Mastery endpoints
│   │   │   │   ├── tutor.py        # Socratic AI Tutor interaction endpoints
│   │   │   │   ├── analytics.py    # Learning Telemetry & XAI endpoints
│   │   │   │   └── educator.py     # Educator Command Center endpoints
│   │   │   └── router.py           # Master API V1 Router aggregation
│   │   ├── core/                   # System Infrastructure & Core Configuration
│   │   │   ├── config.py           # Pydantic BaseSettings environment loader
│   │   │   ├── security.py         # Cryptography, password hashing, JWT tools
│   │   │   ├── database.py         # Async SQLAlchemy engine & session factory
│   │   │   ├── redis.py            # Async Redis connection pool & cache helper
│   │   │   └── logging.py          # Structured JSON log formatter (structlog)
│   │   ├── domain/                 # Domain-Driven Core Modules
│   │   │   ├── user/               # User & Profile Domain
│   │   │   ├── knowledge/          # Knowledge Graph Domain logic
│   │   │   ├── tutoring/           # Socratic Dialogue Domain logic
│   │   │   └── assessment/         # Diagnostic & Rubric Domain logic
│   │   ├── schemas/                # Pydantic Data Transfer Objects (DTOs)
│   │   │   ├── user.py             # User request/response schemas
│   │   │   ├── knowledge.py        # Knowledge node & edge schemas
│   │   │   └── tutor.py            # AI Tutor chat request/response schemas
│   │   ├── db/                     # Data Access Layer & Models
│   │   │   ├── models/             # SQLAlchemy ORM Database Models
│   │   │   └── migrations/         # Alembic database migration scripts
│   │   └── main.py                 # FastAPI Application Factory & Lifecycle hooks
│   ├── pyproject.toml              # Python dependencies (Poetry / UV config)
│   └── Dockerfile                  # Production backend container build spec
├── frontend/                       # Frontend Web Application (React + TypeScript)
│   ├── src/                        # Source Directory
│   │   ├── assets/                 # SVGs, static icons, brand imagery
│   │   ├── components/             # Reusable UI Component Library
│   │   │   ├── common/             # Buttons, Inputs, Modals, Cards (WCAG AAA)
│   │   │   ├── layout/             # Navigation bars, Sidebars, App Shell
│   │   │   ├── tutor/              # Socratic Tutor chat interface components
│   │   │   ├── graph/              # Interactive Knowledge Graph visualizer
│   │   │   └── dashboard/          # Analytics charts & educator command cards
│   │   ├── features/               # Feature-Based Modules (Redux/Zustand slices)
│   │   │   ├── auth/               # Authentication state & hooks
│   │   │   ├── learning/           # Adaptive learning session state
│   │   │   └── educator/           # Educator management state
│   │   ├── hooks/                  # Custom React Hooks (a11y, telemetry, API)
│   │   ├── pages/                  # Page-Level Routing Components
│   │   ├── services/               # API Client Services (Axios/TanStack Query)
│   │   ├── styles/                 # Global CSS Variables & Theme tokens
│   │   ├── types/                  # Global TypeScript Interfaces & Type definitions
│   │   ├── utils/                  # Pure utility functions & formatters
│   │   └── App.tsx                 # Main Application Root & Router Provider
│   ├── package.json                # NPM Dependencies & Scripts
│   ├── tsconfig.json               # Strict TypeScript Compiler Options
│   ├── vite.config.ts              # Vite Bundler & Dev Server Configuration
│   └── Dockerfile                  # Multi-stage production Nginx static container
├── database/                       # Database Governance & Schemas
│   ├── init/                       # Initial PostgreSQL setup scripts
│   ├── seeds/                      # Development & Staging seed datasets
│   └── schema.sql                  # Master relational schema definition reference
├── deployment/                     # Infrastructure-as-Code (IaC) & Cloud Deploy
│   ├── kubernetes/                 # Production Helm Charts & K8s Manifests
│   │   ├── base/                   # Core deployment, service, ingress templates
│   │   └── overlays/               # Environment specific overlays (staging/prod)
│   └── terraform/                  # Cloud Provisioning Scripts (AWS/GCP)
│       ├── main.tf                 # Primary cloud infrastructure resources
│       └── variables.tf            # Infrastructure environment variables
├── docker/                         # Docker Compose Multi-Container Orchestration
│   ├── docker-compose.dev.yml      # Local development environment stack
│   ├── docker-compose.test.yml     # CI testing orchestration stack
│   └── docker-compose.prod.yml     # Local production mirror stack
├── docs/                           # Master Project Documentation (SSOT)
│   ├── PRODUCT_CHARTER.md          # Step 1: Startup Product Charter
│   ├── MARKET_RESEARCH.md          # Step 2: Market Research Report
│   ├── STAKEHOLDER_ANALYSIS.md     # Step 3: Stakeholder Analysis Report
│   ├── ENGINEERING_STANDARDS.md    # Step 4: Engineering Standards Handbook
│   ├── adr/                        # Architecture Decision Records
│   │   ├── 0001-modular-monolith.md# ADR: Modular Monolith vs Microservices
│   │   └── 0002-fastapi-backend.md # ADR: FastAPI & Async SQLAlchemy choice
│   └── api/                        # Exported OpenAPI Specs & Postman Collections
├── tests/                          # Cross-System Integration & E2E Tests
│   ├── e2e/                        # Playwright End-to-End User Journey Tests
│   ├── integration/                # Service API contract & DB integration tests
│   └── load/                       # Locust performance & stress testing scripts
├── assets/                         # Global Media Assets & Branding Source Files
├── scripts/                        # Automation & Developer Utility Tooling
│   ├── setup_dev.sh                # Single-command local developer environment bootstrap
│   ├── run_tests.sh                # Unified local test suite executor
│   └── seed_db.py                  # Database seeding automation script
└── configs/                        # Tooling & Linter Configurations
    ├── .eslintrc.js                # Frontend ESLint rule definitions
    ├── .prettierrc                 # Code formatting standards definition
    ├── ruff.toml                   # Python high-performance linter config
    └── mypy.ini                    # Strict type checking configuration
```

### 3.2 Module Responsibility Breakdown

| Directory Node | Primary Technical Responsibility | Domain Owner |
| :--- | :--- | :--- |
| `/.github/` | CI/CD automation, quality gate enforcement, issue/PR templates. | DevOps Lead |
| `/ai/` | Socratic agent orchestration, prompt engineering, RAG, AI evaluation. | Lead AI Engineer |
| `/ml/` | Bayesian Knowledge Graph engine, memory decay algorithms, ML pipelines. | ML Architect |
| `/backend/` | RESTful API microservices, domain business logic, authentication, DB ORM. | Lead Backend Engineer |
| `/frontend/` | React UI, TypeScript state management, WCAG 2.1 AAA accessible views. | Lead Frontend Engineer |
| `/database/` | SQL schema baselines, migrations, seed datasets, query optimizations. | Database Administrator |
| `/deployment/` | Kubernetes Helm charts, Terraform cloud infrastructure definitions. | Infrastructure Lead |
| `/docker/` | Docker Compose orchestration for dev, test, and prod environments. | SRE / DevOps |
| `/docs/` | Single Source of Truth (SSOT) project markdown documentation & ADRs. | Chief Architect |
| `/tests/` | System-wide Playwright E2E tests, contract tests, load testing scripts. | QA Lead |

---

## 4. Git Strategy & Repository Governance

LuminaLearn AI follows a modified **GitFlow / GitHub Flow Hybrid** model optimized for high velocity, stability, and automated quality gate enforcement.

```
+-----------------------------------------------------------------------------------+
|                            GIT BRANCHING ARCHITECTURE                             |
|                                                                                   |
|  [main] ───────────────────────────● (v1.0.0 Release Tag)                        |
|                                    ▲                                              |
|                                    │ (Pull Request + All Quality Gates Pass)     |
|  [release/v1.0.0] ─────────────────┴───────────────┐                              |
|                                                    ▲                              |
|                                                    │ (PR Merge)                   |
|  [develop] ──────────●─────────────────────────────┴──────────●                   |
|                      ▲                                        ▲                   |
|                      │ (PR Merge)                             │ (PR Merge)        |
|  [feature/*] ────────┴─ (feature/SH-02-educator-dashboard)     │                   |
|                                                               │                   |
|  [bugfix/*] ──────────────────────────────────────────────────┴ (bugfix/auth-jwt) |
+-----------------------------------------------------------------------------------+
```

### 4.1 Branch Naming Conventions
All branch names MUST follow strict prefix protocols incorporating ticket IDs:
* `main`: Production-ready code ONLY. Protected branch requiring 2 approvals.
* `develop`: Integration branch for active sprint development. Protected branch.
* `feature/<ticket-id>-<short-description>`: New feature implementations.  
  * *Example:* `feature/AUR-102-socratic-hint-escalation`
* `bugfix/<ticket-id>-<short-description>`: Non-critical bug fixes.  
  * *Example:* `bugfix/AUR-204-jwt-token-refresh`
* `hotfix/<ticket-id>-<short-description>`: Critical production emergency fixes branching from `main`.  
  * *Example:* `hotfix/AUR-911-openai-api-timeout`
* `release/v<major>.<minor>.<patch>`: Staging release candidate branches.  
  * *Example:* `release/v1.1.0`

### 4.2 Commit Naming Conventions (Conventional Commits v1.0.0)
All commit messages MUST adhere to the Conventional Commits specification:

$$\text{Format: } \langle\text{type}\rangle(\langle\text{scope}\rangle): \langle\text{description}\rangle$$

```
feat(tutor): implement 4-stage adaptive Socratic hint escalation
fix(auth): resolve race condition in JWT token refresh mechanism
docs(api): update OpenAPI spec for educator mastery endpoints
style(frontend): adjust WCAG contrast ratio on primary buttons to 7:1
refactor(graph): optimize Bayesian node traversal algorithm speed
perf(backend): add Redis caching layer for student profile queries
test(e2e): add Playwright test suite for Socratic chat workflow
ci(github): integrate axe-core automated accessibility audit action
chore(deps): bump FastAPI from 0.109.0 to 0.110.0
```

### 4.3 Semantic Versioning (SemVer 2.0.0)
Releases are versioned according to $\text{MAJOR}.\text{MINOR}.\text{PATCH}$:
* **MAJOR (x.0.0):** Incompatible API changes or breaking architectural updates.
* **MINOR (0.x.0):** Backward-compatible new functionality or major feature additions.
* **PATCH (0.0.x):** Backward-compatible bug fixes and security hotfixes.

### 4.4 Release Lifecycle & Tagging Strategy
1. Code merged into `release/vX.Y.Z` undergoes full staging validation and QA sign-off.
2. Upon approval, `release/vX.Y.Z` is merged into `main` via PR.
3. An official immutable Git tag is created: `git tag -a vX.Y.Z -m "Release vX.Y.Z - LuminaLearn AI"`.
4. Automated GitHub Actions release pipeline builds container artifacts, publishes release notes, and deploys to production environments.

### 4.5 GitHub Projects, Issues & Milestones
* **Milestones:** Mapped directly to 2-week Agile Sprint cycles (e.g., `Sprint 14: Educator Command Center`).
* **Issues:** Every work item MUST have a GitHub Issue created using official templates (`bug_report.md`, `feature_request.md`). Issues must specify labels (e.g., `domain:ai`, `type:bug`, `priority:critical`).
* **GitHub Projects:** Kanban boards tracking issue status across: `Backlog` $\rightarrow$ `Ready for Sprint` $\rightarrow$ `In Progress` $\rightarrow$ `In Review / QA` $\rightarrow$ `Done`.

### 4.6 Pull Request (PR) Governance & Merge Strategy
* **PR Requirements:**
  * Title MUST follow Conventional Commits format.
  * Description MUST complete the standard PR template (Linking Issue ID, detailing changes, and checking off the DoD checklist).
  * Minimum **2 Code Owner Approvals** required.
  * 100% of automated CI Pipeline checks MUST pass (Lint, Typecheck, Tests, SAST, A11y).
* **Merge Strategy:** **Squash and Merge** ONLY for feature/bugfix branches to maintain a clean linear commit history on `develop` and `main`. Merge commits are prohibited.

---

## 5. Coding Standards & Naming Conventions

### 5.1 Universal Naming Conventions

| Language / Context | Case Style | Example | Operational Context |
| :--- | :--- | :--- | :--- |
| **Folders & Directories** | `snake_case` or `kebab-case` | `knowledge_graph/` or `socratic-tutor/` | Repository directory nodes |
| **File Names (Python)** | `snake_case.py` | `bayesian_engine.py` | All Python backend modules |
| **File Names (React/TS)** | `PascalCase.tsx` | `SocraticChat.tsx` | React UI components |
| **File Names (TS Utils)** | `camelCase.ts` | `formatDate.ts` | Non-component TS helpers |
| **Classes (All)** | `PascalCase` | `KnowledgeGraphEngine` | Python & TypeScript classes |
| **Variables (All)** | `snake_case` (Py) / `camelCase` (TS) | `mastery_score` / `masteryScore` | Instance variables |
| **Functions (All)** | `snake_case` (Py) / `camelCase` (TS) | `calculate_decay()` / `calculateDecay()` | Functions and methods |
| **Constants (All)** | `UPPER_SNAKE_CASE` | `MAX_RETRY_LIMIT` | Global immutable constants |
| **Interfaces (TS)** | `PascalCase` (No `I` prefix) | `UserSessionProps` | TypeScript type declarations |

### 5.2 React & Frontend Engineering Standards
* **Component Architecture:** Functional components ONLY with React Hooks. Class components are forbidden.
* **TypeScript Strictness:** Enable `"strict": true` in `tsconfig.json`. Use explicit prop interfaces for every component. `any` type is strictly banned (`unknown` must be used if type is uncertain).
* **Styling Standard:** Use Vanilla CSS modules or CSS-in-JS with predefined CSS Variables (`styles/tokens.css`). Ad-hoc inline styles or utility clutter are prohibited.
* **Accessibility (WCAG 2.1 AAA):** Every interactive element MUST have unique descriptive `id` attributes, proper `aria-*` labels, visible focus indicators, and full keyboard navigation support (`tabIndex`).
* **State Management:** Keep local UI state in `useState`/`useReducer`. Global application state must use `Zustand` or `TanStack Query` for server state.

### 5.3 Python & Backend Engineering Standards
* **PEP 8 Compliance:** Enforced via `ruff` linter with a maximum line length of **88 characters** (Black standard).
* **Strict Type Hints:** 100% function signature coverage required. All functions MUST specify return type annotations: `def get_user(user_id: UUID) -> UserResponse:`.
* **Async/Await Standard:** Native asynchronous I/O (`async def`) for all network requests, database queries, and Redis calls. Synchronous blocking calls on main event loops are banned.
* **Logging Standard:** Use structured JSON logging (`structlog`). Never use `print()` statements. Log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

### 5.4 FastAPI Framework Standards
* **Dependency Injection:** Utilize FastAPI's `Depends()` for database sessions, current authenticated user extraction, and service class instantiation.
* **Schema Validation:** Use `Pydantic v2` for all request/response payload validation. Define explicit `ConfigDict` and field descriptions.
* **APIRouter Modularization:** Route files must be grouped logically under `/backend/app/api/v1/` and included in the main app router with explicit tags and response models.

---

## 6. Documentation Standards & Knowledge Management

### 6.1 Documentation-as-Code Methodology
All technical documentation is maintained in Markdown within the repository. Documentation updates MUST occur in the same Pull Request as the code changes they describe.

### 6.2 Architecture Decision Records (ADR)
Any major technical decision (e.g., database choice, framework selection, paradigm shift) requires creating an ADR in `docs/adr/` using the following standardized format:

```markdown
# ADR-0001: Adoption of FastAPI for Backend Microservices

## Status
Approved

## Context
LuminaLearn AI requires a high-performance, asynchronous Python backend framework capable of serving low-latency REST endpoints, executing async AI pipelines, and generating automatic OpenAPI documentation.

## Decision
We will adopt FastAPI (v0.110+) running on Uvicorn with async SQLAlchemy 2.0 as our backend foundation.

## Consequences
### Positive
* Sub-millisecond routing overhead with native async performance.
* Automatic OpenAPI / Swagger generation via Pydantic schemas.
* Built-in dependency injection simplifying security and testing.
### Negative
* Engineering team must maintain strict async coding discipline to avoid thread blocking.
```

---

## 7. API Design & Integration Standards

LuminaLearn AI enforces strict **RESTful API Design Standards** across all microservices.

### 7.1 RESTful Architectural Conventions
* **Base URL Pattern:** `https://api.luminalearn.ai/v1/<domain>/<resource>`
* **HTTP Verbs:**
  * `GET`: Retrieve resource or collection (Safe, Idempotent).
  * `POST`: Create a new resource or execute an RPC-style action (Unsafe, Non-Idempotent).
  * `PUT`: Replace an existing resource completely (Unsafe, Idempotent).
  * `PATCH`: Partially update an existing resource (Unsafe, Non-Idempotent).
  * `DELETE`: Remove a resource (Unsafe, Idempotent).

### 7.2 HTTP Status Code Matrix

| Status Code | Code Name | Usage Scenario |
| :---: | :--- | :--- |
| **200** | `OK` | Standard successful GET, PUT, or PATCH request. |
| **201** | `Created` | Successful POST request resulting in resource creation. |
| **204** | `No Content` | Successful DELETE or action with no response body. |
| **400** | `Bad Request` | Validation failure or malformed request payload. |
| **401** | `Unauthorized` | Missing or invalid authentication token. |
| **403** | `Forbidden` | Authenticated user lacks permission for the resource. |
| **404** | `Not Found` | Target resource or endpoint does not exist. |
| **422** | `Unprocessable Entity` | Pydantic schema validation error. |
| **429** | `Too Many Requests` | Rate limit threshold exceeded. |
| **500** | `Internal Server Error` | Unhandled backend exception (triggers SRE alert). |
| **503** | `Service Unavailable` | Circuit breaker tripped for downstream dependency. |

### 7.3 Standardized Response & Error Envelopes

#### Standard Success Envelope

```json
{
  "success": true,
  "data": {
    "node_id": "kn_math_101",
    "title": "Quadratic Equations",
    "mastery_score": 0.85
  },
  "meta": {
    "timestamp": "2026-07-30T08:30:00Z",
    "request_id": "req_8f9a2b1c"
  }
}
```

#### Standard Error Envelope

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Knowledge node with ID 'kn_math_999' was not found.",
    "details": [
      {
        "field": "node_id",
        "issue": "Invalid node identifier provided."
      }
    ]
  },
  "meta": {
    "timestamp": "2026-07-30T08:30:00Z",
    "request_id": "req_8f9a2b1c"
  }
}
```

### 7.4 Pagination, Filtering & Sorting Standards
* **Pagination (Cursor-based):** `GET /v1/knowledge/nodes?limit=20&cursor=eyJpZCI6IDEwfQ==`
* **Filtering:** `GET /v1/analytics/cohorts?subject=mathematics&status=at_risk`
* **Sorting:** `GET /v1/educator/students?sort=-mastery_score,+last_active` (`-` = Descending, `+` = Ascending)

---

## 8. Multi-Environment & Infrastructure Strategy

```
+-----------------------------------------------------------------------------------+
|                           MULTI-ENVIRONMENT SPECTRUM                              |
|                                                                                   |
|  [DEVELOPMENT] ────────► [TESTING / STAGING] ──────► [PRODUCTION]                 |
|  • Local Docker Compose   • Kubernetes Staging Cluster• Multi-Region AWS / GCP    |
|  • Mocked AI APIs         • Staging DB & Vector Store  • Production Database    |
|  • Hot Reloading Enabled  • Real AI APIs (Sandboxed)   • Auto-scaling & Redundancy|
+-----------------------------------------------------------------------------------+
```

### 8.1 Multi-Environment Spectrum

| Feature | Development (Local) | Testing / Staging | Production |
| :--- | :--- | :--- | :--- |
| **Host Environment** | Developer Workstation | Cloud K8s (Staging Namespace) | Cloud K8s (Prod Multi-Region) |
| **Orchestration** | Docker Compose (`docker/`) | Helm / Kubernetes | Helm / Terraform / K8s |
| **Database** | Local Postgres Container | Isolated Staging RDS Instance | Multi-AZ RDS Primary + Replicas |
| **AI Integration** | Mocked AI Responses / Ollama | Real AI APIs (Test Keys) | Production Zero-Retention APIs |
| **Log Level** | `DEBUG` | `INFO` | `WARNING` / `ERROR` |
| **Security Audit** | Local Linter Checks | Automated SAST / DAST | Continuous Security Guardrails |

### 8.2 Docker Containerization Standards
* **Multi-Stage Builds:** All Dockerfiles MUST use multi-stage builds to minimize image size (Final production images MUST be <150MB for Python/Nginx).
* **Rootless Containers:** Containers MUST run as a non-privileged `appuser` (UID 10001). Running containers as `root` is strictly banned.
* **Image Tagging:** Production images MUST be tagged with Git commit SHA and SemVer version tag (`luminalearn/backend:1.1.0-sha-8f9a2b1`). Using `:latest` in production is forbidden.

### 8.3 Secrets Management & Configuration
* **12-Factor App Compliance:** Configuration MUST be stored in environment variables, loaded via Pydantic `BaseSettings`.
* **Zero Secrets in Code:** Hardcoding API keys, database passwords, or JWT secrets in source code is an immediate firing offense.
* **Secrets Vault:** Secrets in Staging and Production MUST be injected dynamically via HashiCorp Vault or AWS Secrets Manager. Local dev secrets use `.env.local` (gitignored).

---

## 9. Quality Gates & Definition of Done (DoD)

### 9.1 Definition of Done (DoD) Framework
A user story or feature issue is considered **DONE** only when all of the following criteria are met:

```
  [1. Code Complete] ──► [2. Tests Pass] ──► [3. Code Reviewed] ──► [4. A11y / Security] ──► [5. Deployed]
```

### 9.2 Quality Gate Checklists

#### Code Review Checklist
- [ ] Code adheres strictly to clean code, SOLID, and KISS principles.
- [ ] 100% static type annotations present (No `any` in TS; explicit return types in Python).
- [ ] Zero linting errors (`ruff` for Python, `ESLint` for React).
- [ ] No hardcoded secrets, credentials, or magic numbers.

#### Testing Checklist
- [ ] Unit test coverage exceeds **85%** for modified domain files.
- [ ] Integration tests pass for all modified API endpoints.
- [ ] Non-deterministic AI outputs evaluated against Socratic safety harness.
- [ ] Automated regression suite passes 100%.

#### Documentation Checklist
- [ ] API changes automatically updated in OpenAPI / Swagger schema.
- [ ] Corresponding markdown documentation updated in `docs/`.
- [ ] Architecture Decision Record (ADR) created for major architectural choices.

#### Security & Accessibility Checklist
- [ ] Automated SAST (Bandit/Semgrep) clean of high/critical vulnerabilities.
- [ ] OWASP Top 10 mitigation verified for new endpoints.
- [ ] Automated WCAG 2.1 AAA accessibility audit passes with 0 violations.
- [ ] Zero-data-retention API headers verified for external AI calls.

---

## 10. Agile Sprint Workflow & Release Cycle

LuminaLearn AI operates on a **2-Week Sprint Cycle**.

```
+-----------------------------------------------------------------------------------+
|                            2-WEEK SPRINT CYCLE FLOW                               |
|                                                                                   |
|  [Day 1: Planning] ──► [Days 2-7: Dev & Testing] ──► [Days 8-9: Review & QA]     |
|                                                               │                   |
|  [Day 10: Retrospective & Release] ◄──────────────────────────┘                   |
+-----------------------------------------------------------------------------------+
```

1. **Sprint Planning (Day 1):** Product Manager and Tech Lead review refined backlog, verify user stories meet Definition of Ready (DoR), and commit to sprint goals.
2. **Development & TDD (Days 2–7):** Developers build features using feature branches (`feature/*`), writing unit/integration tests alongside code.
3. **Continuous Review & QA (Days 8–9):** Code reviews performed asynchronously. PRs trigger automated CI pipelines. QA verifies features in the Staging environment.
4. **Sprint Demo & Retrospective (Day 10):** Completed features demonstrated to stakeholders. Team conducts Sprint Retrospective to continuous process improvement. Staging release merged to `main` for production deployment.

---

## 11. Master Reusable Sprint Engineering Checklist

Every future engineering sprint MUST verify compliance against this master checklist prior to release sign-off.

| Checklist Domain | Verification Requirement | Responsible Role | Status |
| :--- | :--- | :---: | :---: |
| **Architecture** | Code follows Domain-Driven Design layout and modular monolith boundaries. | Tech Lead | [ ] |
| **Clean Code** | Zero linting errors (`ruff` / `ESLint`), 100% strict type annotations. | Lead Developer | [ ] |
| **Git Strategy** | Conventional commits used, feature branches squashed into `develop`. | GitHub Maintainer | [ ] |
| **API Standards** | RESTful response envelopes, OpenAPI spec generated, status codes verified. | Backend Lead | [ ] |
| **Testing** | Unit test coverage $\ge 85\%$, Playwright E2E tests pass, AI eval suite clean. | QA Lead | [ ] |
| **Security** | SAST scan clean, OWASP Top 10 checked, zero secrets in code, DPIA verified. | Security Officer | [ ] |
| **Accessibility** | 100% WCAG 2.1 AAA automated audit pass rate (axe-core), screen-reader verified. | A11y Lead | [ ] |
| **Infrastructure** | Multi-stage Docker containers non-root, Helm charts updated, zero downtime. | DevOps Lead | [ ] |
| **Documentation** | Markdown docs in `docs/` updated, ADR logged if architecture altered. | Scrum Master | [ ] |
| **Sprint DoD** | Definition of Done 100% satisfied, double code-owner PR sign-off complete. | Engineering Manager| [ ] |

---
