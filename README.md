# LuminaLearn AI — Enterprise Monorepo

> **Illuminate Every Learning Journey**  
> *Project Aurora | Monorepo Engineering Foundation*

LuminaLearn AI is an AI-powered adaptive learning platform designed to personalize education through Artificial Intelligence, Learning Analytics, Universal Accessibility (WCAG 2.1 AAA), and Explainable AI (XAI).

---

## 🏛️ Monorepo Directory Architecture

```
LUMINALEARN_AI/
├── .github/                 # GitHub CI/CD workflows, issue & PR templates
├── .vscode/                 # Workspace linter, formatter & debugger settings
├── ai/                      # Socratic AI Agent framework & prompt engineering
├── backend/                 # FastAPI (Python 3.11+) microservices app
│   ├── app/                 # FastAPI application package (core, api, domain)
│   ├── tests/               # Pytest backend test suite
│   ├── Dockerfile           # Multi-stage production container spec
│   └── pyproject.toml       # Python dependencies (Ruff, Mypy, FastAPI)
├── database/                # PostgreSQL schema definitions & migrations
│   ├── init/                # SQL initialization scripts
│   └── schema.sql           # Master DDL schema definition
├── docker/                  # Docker Compose orchestration configurations
│   └── docker-compose.dev.yml # Local development multi-container stack
├── docs/                    # Single Source of Truth (SSOT) documentation
│   ├── PRODUCT_CHARTER.md   # Product Vision & Strategic Pillars
│   ├── MARKET_RESEARCH.md   # Industry Analysis & TAM/SAM/SOM
│   ├── STAKEHOLDER_ANALYSIS.md # 20 Stakeholder Profiles & Matrices
│   ├── ENGINEERING_STANDARDS.md # Coding & Architectural Handbook
│   └── SYSTEM_ARCHITECTURE.md   # Tech Stack Lock & Data Flow Specs
├── frontend/                # Next.js 14+ (React 18 / TypeScript) web app
│   ├── src/
│   │   ├── app/             # App Router pages & layouts
│   │   ├── components/      # UI Component Library (Apple/Linear inspired)
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # TanStack Query API services
│   │   ├── stores/          # Zustand state stores
│   │   ├── styles/          # Tailwind directives & CSS design tokens
│   │   └── utils/           # Shared utility functions & constants
│   ├── next.config.js       # Next.js configuration
│   ├── tailwind.config.js   # Custom design tokens & theme specs
│   ├── tsconfig.json        # Strict TypeScript compiler options
│   └── package.json         # Frontend dependencies
├── ml/                      # Machine Learning & Bayesian Knowledge Graph engine
├── scripts/                 # Developer setup & utility scripts
├── .env.example             # Centralized environment variable template
├── .gitignore               # Version control exclusion definitions
├── mypy.ini                 # Strict Python type checking configuration
├── ruff.toml                # High-performance Python linter configuration
└── docker-compose.yml       # Primary Docker Compose orchestration file
```

---

## ⚡ Tech Stack Lock

| Domain | Technology | Version | Purpose |
| :--- | :--- | :---: | :--- |
| **Frontend** | **Next.js (App Router)** | `14.2+` | React 18 Web Client, Server Components, SSR |
| **Styling** | **Tailwind CSS & CSS Tokens** | `3.4+` | Custom Design System (Apple/Linear inspired) |
| **State** | **Zustand & TanStack Query** | `v4 / v5` | Client UI State + Server Async Caching |
| **Backend** | **FastAPI** | `0.110+` | High-performance Async REST Microservices |
| **Language** | **Python** | `3.11+` | Backend & AI/ML Execution Engine |
| **Database** | **PostgreSQL** | `16.2+` | Primary Relational Database |
| **Cache & Queue** | **Redis** | `7.2+` | Session Cache & Async Task Queue |
| **Vector DB** | **Qdrant** | `1.9+` | Vector Search for RAG Concept Embeddings |
| **AI Foundation** | **Google Gemini** | `1.5 Pro / Flash` | Socratic AI Tutoring & Resource Generation |
| **Containers** | **Docker & Docker Compose** | `26.0+` | Multi-Container Local & Cloud Deployment |

---

## 🚀 Quickstart Development Setup

### 1. Prerequisites
- **Node.js**: `v20.x` or higher
- **Python**: `3.11.x`
- **Docker & Docker Compose**: `v26.x` or higher

### 2. Environment Configuration
Copy `.env.example` to create your local environment configuration:
```bash
cp .env.example .env
```

### 3. Run Locally (one command)
From the project root, after installing backend (`backend/.venv`) and frontend (`frontend/node_modules`) dependencies:
```bash
npm run dev
```
This starts the API on `http://127.0.0.1:8001` and the web app on `http://localhost:3000` (or the next free port), and Ctrl+C stops both. The browser only ever calls the web app's own `/api/v1`, which the Next.js server forwards to the API. There is no CORS setup, and no API address in the browser that can drift.

### 4. Or Launch the Stack via Docker Compose
To launch PostgreSQL, Redis, FastAPI Backend, and Next.js Frontend concurrently:
```bash
docker-compose -f docker/docker-compose.dev.yml up --build
```

Access local instances:
- **Frontend App**: `http://localhost:3000`
- **Backend API**: `http://localhost:8001`
- **API Interactive Docs (Swagger)**: `http://localhost:8001/docs`
- **Health Check Endpoint**: `http://localhost:8001/api/v1/health`

The workspace (subjects, tutor, quiz, dashboards) requires signing in, and the API enforces it on every request.

---

## 🛠️ Code Quality & Formatting Rules

### Frontend (TypeScript / React)
```bash
cd frontend
npm run lint      # ESLint check
npm run typecheck # TypeScript strict type check
npm run format    # Prettier auto-format
```

### Backend (Python / FastAPI)
```bash
cd backend
ruff check .      # High-performance linting
ruff format .     # Code formatting (Black compliant)
mypy app          # Strict type checking
```

---

## 📄 License & Governance
Proprietary & Confidential — LuminaLearn AI Development Team. All rights reserved.
