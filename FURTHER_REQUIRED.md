# LuminaLearn AI — Comprehensive Prerequisites, Required Items & Decisions Checklist

> **Document Name**: `FURTHER_REQUIRED.md`  
> **Target Audience**: Product Owner / Project Lead  
> **Purpose**: A complete, single-source checklist of all software, API keys, credentials, curriculum assets, and architectural decisions required from your side to bring LuminaLearn AI from its current foundation (~56%) to 100% full production completion without any roadblocks or backdrops.

---

## Quick Status Summary (What You Already Have Ready)

We ran an automated diagnostic scan on your local machine. **Good news!** You already have the foundational runtimes installed:
- ✅ **Python**: `v3.13.7` (Installed & operational)
- ✅ **Node.js**: `v22.18.0` (Installed & operational)
- ✅ **npm**: `v10.9.3` (Installed & operational)
- ✅ **Docker**: `v28.3.2` (Installed)
- ✅ **Git**: `v2.55.0` (Installed)
- ✅ **Gemini API Key**: `GEMINI_API_KEY` configured in `.env` and `backend/.env`
- ✅ **Backend Test Suite**: 35/35 tests passing cleanly (100% pass rate)

Below is the structured breakdown of everything that remains for you to install, configure, provide, or decide upon.

---

## 1. Software & Local Environment (What to Install / Run)

| Item | Requirement | Why It Is Needed | Your Action Required |
| :--- | :---: | :--- | :--- |
| **Docker Desktop** | **Optional for Dev, Required for Prod DB** | PostgreSQL, Redis, and Qdrant containers run via Docker Compose. *(Note: Our resilience engine already allows you to run locally with SQLite without Docker).* | If you want to run PostgreSQL and Redis locally, launch the **Docker Desktop** application on Windows. |
| **Browser Microphone Permission** | **Required for Voice Agent** | The upcoming Real-Time Voice Agent listens to your voice for conversational Socratic tutoring. | When prompted by your browser at `http://localhost:3000`, click **Allow** for microphone access. |
| **Python Virtual Environment** | **Recommended** | Isolates Python packages and prevents version conflicts. | Run `python -m venv .venv` inside `backend/` and activate it before installing dependencies. |

---

## 2. API Keys & Third-Party Service Credentials (What to Provide)

Please review each credential below. Fill in the values or check the boxes:

### A. AI & LLM Services
- [x] **Google Gemini API Key**:
  - **Status**: ✅ **ALREADY CONFIGURED**
  - **Configured Key**: `GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"`
  - **Purpose**: Powers dynamic topic quiz generation, pedagogical multi-agent reasoning, Bloom's difficulty adaptation, and Socratic hint ladders.

### B. Voice & Speech Synthesis (Choose One Option)
- [ ] **Option 1 (Recommended — Zero Cost / Zero Setup)**: **Browser Web Speech API**
  - *No API key required.* Uses the native speech synthesis and recognition engines built into Google Chrome / Microsoft Edge.
- [ ] **Option 2 (Studio Human Voices)**: **ElevenLabs API Key**
  - *Key*: `ELEVENLABS_API_KEY="your_api_key_here"`
  - *Where to get*: [elevenlabs.io](https://elevenlabs.io)
  - *Purpose*: Provides ultra-realistic, low-latency conversational voices with custom warmth and cadences.

### C. Real Google OAuth2 Sign-In (Optional for Dev, Required for Production)
*Note: The app currently includes a built-in development simulation modal that allows full testing without configuring Google Cloud.*
- [ ] **Google Cloud OAuth 2.0 Credentials**:
  - `GOOGLE_CLIENT_ID="your_google_client_id.apps.googleusercontent.com"`
  - `GOOGLE_CLIENT_SECRET="your_google_client_secret"`
  - *Where to get*: [Google Cloud Console](https://console.cloud.google.com/) $\rightarrow$ APIs & Services $\rightarrow$ Credentials $\rightarrow$ OAuth 2.0 Client IDs.
  - *Authorized Javascript Origins*: `http://localhost:3000`, `http://127.0.0.1:3000`
  - *Authorized Redirect URIs*: `http://localhost:3000/api/auth/callback/google`

### D. Email / SMTP Service (For Real Email Verification & Password Resets)
*Note: In development mode, OTP codes and password reset links are automatically displayed in the API response and terminal logs so you don't need real emails.*
- [ ] **SMTP Credentials (for production email dispatch)**:
  - `SMTP_HOST="smtp.sendgrid.net"` (or `smtp.resend.com`, `email-smtp.us-east-1.amazonaws.com`, or `smtp.gmail.com`)
  - `SMTP_PORT=587`
  - `SMTP_USER="apikey"` (or your SMTP username)
  - `SMTP_PASSWORD="your_smtp_password"`
  - `EMAILS_FROM_EMAIL="noreply@yourdomain.com"`
  - `EMAILS_FROM_NAME="LuminaLearn AI"`

### E. Vector Database (For Phase 5.7 Curriculum RAG)
- [ ] **Vector Database Preference**:
  - **Option 1 (Local Docker — Free)**: Run Qdrant locally (`docker run -p 6333:6333 qdrant/qdrant`). *No API key needed.*
  - **Option 2 (Cloud Managed)**: Qdrant Cloud API Key
    - `QDRANT_HOST="https://your-cluster-id.qdrant.tech"`
    - `QDRANT_API_KEY="your_qdrant_api_key"`
    - *Where to get*: [cloud.qdrant.io](https://cloud.qdrant.io)

---

## 3. Curriculum & Content Assets (What Materials to Provide)

To tailor the system to your exact curriculum, syllabus, or academic subjects:

1. **Priority Subject Domains for Initial Quizzing**:
   - What subjects do you want tested first? (e.g., Computer Science, Python, Data Structures & Algorithms, Artificial Intelligence, Discrete Mathematics, or another field?)
   - *Provide*: A short list of priority topics you want learners to be quizzed on.
2. **Textbook & Syllabus Documents (Optional, for Zero-Hallucination RAG)**:
   - If you want the AI to quote verified textbook chunks, syllabi, or school lecture notes, provide:
     - PDF textbooks, course handouts, or Markdown files.
     - We will place these into `ai/rag/documents/` to be automatically chunked and embedded into the vector database.

---

## 4. Production Cloud Deployment & Release (Phase 7)

When you are ready to deploy LuminaLearn AI live to the web for public users:

1. **Cloud Hosting Platform Preference**:
   - **Frontend**: Vercel (recommended for Next.js 14) or AWS Amplify / Cloudflare Pages.
   - **Backend**: Render, Railway, Fly.io, AWS ECS/EC2, or Google Cloud Run.
   - **Database**: Supabase / Neon / AWS RDS (PostgreSQL) + Upstash (Redis).
2. **Custom Domain Name**:
   - The domain you want the app hosted on (e.g., `luminalearn.ai`, `learn.yourdomain.com`).
   - Access to DNS records to point CNAME/A records and configure automated SSL certificates.

---

## 5. Architectural & Design Decisions (Questionnaire for You)

Please answer the following 4 quick questions so we build the remaining sprints to your exact preferences:

### Question 1: Voice Engine Selection
Which voice engine do you prefer to start with for the Live Socratic Voice Tutor?
- [ ] **Choice A (Recommended)**: Browser Web Speech API — Instant setup, completely free, zero API keys, works immediately in Chrome/Edge.
- [ ] **Choice B**: ElevenLabs — Studio-quality, natural human voices (requires free/paid ElevenLabs API key).
- [ ] **Choice C**: Google Cloud Text-to-Speech — High quality Google WaveNet/Journey voices.

### Question 2: Local Database Workflow
How do you prefer running the database during development?
- [ ] **Choice A (Recommended for simplicity)**: Embedded SQLite (`USE_SQLITE=true`) — Fast, zero setup, stores data in `luminalearn.db`, doesn't require Docker running.
- [ ] **Choice B**: Docker Compose PostgreSQL & Redis — Runs full production-grade database containers on your machine.

### Question 3: Initial Quiz Testing Topics
Which topic domain should we calibrate first for Sprint 1 adaptive quizzes?
- [ ] **Choice A**: Computer Science & Programming (Data Structures, Python, Algorithms, Object-Oriented Design).
- [ ] **Choice B**: Artificial Intelligence & Machine Learning (Neural Networks, Linear Regression, Backpropagation).
- [ ] **Choice C**: Mathematics (Calculus, Linear Algebra, Probability & Statistics).
- [ ] **Choice D**: Custom list of topics provided by you.

### Question 4: Math Notation in Quizzes
For STEM and mathematical questions, should we enable full KaTeX LaTeX notation rendering (e.g., $E = mc^2$, $\int_0^\infty x^2 dx$)?
- [ ] **Yes (Recommended)**: Enable KaTeX in the Next.js frontend quiz studio.
- [ ] **No**: Plain text / standard markdown only.

---

## 6. Selected User Preferences & Tailored Action Plan

Based on your configuration selections:

| Selection Item | Your Decision | What This Means & What Is Needed Next |
| :--- | :--- | :--- |
| **Voice Engine** | **Google Cloud Text-to-Speech** (Journey / WaveNet) | Uses Google Cloud's natural WaveNet / Journey neural voices. Provide either: <br>• A Google Cloud Service Account JSON file (`gcloud auth application-default login` or set `GOOGLE_APPLICATION_CREDENTIALS="path/to/key.json"`), or <br>• Ensure Cloud Text-to-Speech API is enabled on your Google Cloud Console project. |
| **Local Database** | **Docker Compose PostgreSQL & Redis** | Run full production database containers locally. <br>• **Action Needed**: Launch **Docker Desktop** on Windows (it is currently installed but stopped). Once opened, run: <br>`docker-compose -f docker/docker-compose.dev.yml up -d` |
| **Quiz Calibration Domain** | **Mathematics** (Calculus, Linear Algebra, Probability & Statistics) | The Sprint 1 Quiz Engine and Bayesian Knowledge Tracing skill graph will prioritize mathematics concepts, derivative/integral scaffolding, and matrix algebra. |
| **Math Notation** | **Yes, Enable KaTeX LaTeX Rendering** | We will install `katex` in `frontend` so formulas like $\int_{a}^{b} f(x)dx$ and $\det(A - \lambda I) = 0$ render with typography. |

---

## 7. Immediate Next Step: Sprint 1 Execution

Once you confirm your preferences above, we will immediately begin building **Sprint 1**:
1. **`backend/app/models/quiz.py`**: Create `QuizSession`, `QuizQuestion`, and `QuizAttempt` models.
2. **`backend/app/services/quiz_service.py`**: Build the dynamic topic quiz generator with Gemini 1.5 JSON schema and IRT 2PL difficulty calculation.
3. **`ml/models/knowledge_tracer.py`**: Implement the Bayesian Knowledge Tracing (BKT) predictive mastery engine.
4. **`backend/app/api/v1/quiz.py`**: Create `/api/v1/quiz/generate` and `/api/v1/quiz/submit` endpoints.
5. **`backend/tests/test_quiz_engine.py`**: Write automated Pytest validation tests.
