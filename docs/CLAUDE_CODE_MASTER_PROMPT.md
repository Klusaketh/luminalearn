# 🌟 LuminaLearn AI — Claude Code Master Engineering & UI/UX Prompt

> **Instructions for Use**:  
> 1. Open your terminal in the root of this repository: `cd luminalearn-main`  
> 2. Run Claude Code: `claude`  
> 3. Paste the entire block below into Claude Code to execute the overhaul.

---

```markdown
### ROLE & OBJECTIVE
You are a Principal AI Systems Architect and Staff Design Technologist at a top-tier design-driven AI engineering lab (e.g., Linear, Apple, Vercel, OpenAI). You have been brought in to lead the end-to-end implementation and visual overhaul of **LuminaLearn AI** (Project Aurora).

Your mission is twofold:
1. **Complete all production AI capabilities**: Finalize the Multi-Agent Socratic Tutoring Collective, Full-Duplex Real-Time Voice HUD with Barge-in Interruption Detection, and Grounded Vector RAG.
2. **Elevate the Frontend to World-Class Luxury Polish**: Transform the web client into a breathtaking, fluid, visually stunning experience with heavy, silky-smooth 60fps animations, reactive audio visualizers, Apple VisionOS/Linear-grade glassmorphism, dynamic glowing gradients, and zero hydration/type errors.

---

### ARCHITECTURAL CONTEXT & ENVIRONMENT
- **Monorepo Structure**:
  - `backend/`: FastAPI (Python 3.11+), Async SQLAlchemy 2.0 (PostgreSQL + SQLite zero-downtime fallback), Redis + In-Memory fallback, Google Gemini 1.5 SDK, BKT Bayesian Knowledge Tracing Engine (`ml/models/knowledge_tracer.py`).
  - `frontend/`: Next.js 14 App Router (React 18), TypeScript 5.4+, Tailwind CSS 3.4+, Zustand global stores, KaTeX math renderer, Lucide icons.
- **Existing Health & Tests**:
  - 59/59 pytest unit/integration tests passing.
  - Zero linter violations (`ruff check .` passing).
  - Strict type checking clean (`mypy app` passing).
  - 22 Next.js routes operational.

---

### STEP 1: VISUAL OVERHAUL & HEAVY ANIMATION SYSTEM (FRONTEND)

Transform the UI into a luxury, state-of-the-art interactive experience. Install and leverage `framer-motion` (or existing Canvas/CSS primitives) with high visual fidelity:

#### 1.1. Design Aesthetics & Visual Tokens
- **Theme**: Ultra-dark luxury palette with deep space backgrounds (`#05050A`, `#0B0C15`), frosted glass (`backdrop-blur-2xl bg-white/[0.03] border border-white/[0.08]`), and radiant ambient glows (aurora gradients in violet `#8B5CF6`, cyan `#06B6D4`, and amber `#F59E0B`).
- **Typography**: Crisp tracking, tabular numerals for stats, KaTeX for LaTeX equations, and beautiful typography hierarchy.
- **Micro-Interactions**:
  - Magnetic button hover states with radial cursor glow tracking.
  - Smooth spring physics on modal entries, card hover elevation, and tabs.
  - Radiant border shimmer animations (`gradient-border-flow`).
  - Particle confetti triggers upon unlocking new skill mastery levels.

#### 1.2. The Socratic AI Tutor Workspace (`frontend/src/app/tutor/page.tsx`)
Upgrade the tutor interface from a static mockup into a jaw-dropping live experience:
- **Reactive Voice Orb HUD**:
  - Implement an HTML5 `<canvas>` glowing holographic orb visualizer that dynamically ripples, pulses, and responds to real-time audio frequencies (using the Web Audio API `AudioContext` and `AnalyserNode`).
  - Modes: *Idle* (slow breathing luminescence), *Listening* (reactive waveform frequency bars), *Thinking* (spinning quantum orbit rings), *Speaking* (flowing harmonic fluid mesh).
- **Streaming Socratic Dialogue Feed**:
  - Typewriter text streaming with smooth auto-scroll lock.
  - Code blocks with syntax highlighting, language badges, and animated "Copy" buttons.
  - Socratic "Hint Ladders" rendered as collapsible frosted glass accordion steps.
  - Inline KaTeX formula rendering for math equations.
- **Cognitive Load & VARK Switcher**:
  - Floating switcher allowing students to toggle explanations in real time: **Visual** (interactive SVG diagrams), **Auditory** (voice narration), **Read/Write** (structured markdown breakdowns), **Kinesthetic** (interactive parameter sliders).

#### 1.3. Adaptive Quizzing & Knowledge Radar (`frontend/src/app/quiz/page.tsx`)
- Dynamic animated SVG Bayesian Knowledge Mastery gauges that sweep smoothly from prior mastery to posterior mastery on question submission.
- Real-time Misconception Callout banner with glowing warning borders and instant remediation paths.
- Interactive Retention Forecast curve visualizer showing exponential forgetting decay vs. spaced retrieval repetition.

---

### STEP 2: IMPLEMENT CORE AI MULTI-AGENT FACULTY (BACKEND & AI)

Finalize the multi-agent orchestration under `ai/agents/` and `backend/app/api/v1/`:

#### 2.1. LangGraph / Socratic Multi-Agent Orchestration
Build a clean, modular agent collective using the Google Gemini 1.5 Flash/Pro SDK:
1. **Supervisor Agent**: Parses student queries, inspects current BKT skill mastery and VARK profile, and routes to the right specialist.
2. **Socratic Tutor Agent**: Enforces the golden rule: **NEVER give the final answer directly**. Formulates scaffolding questions, identifies false assumptions, and provides progressive hint tiers (Tiers 1-3).
3. **Concept Explainer (VARK Specialist)**: Generates modality-specific breakdowns:
   - *Visual*: Generates Mermaid.js diagrams or ASCII structural charts.
   - *Kinesthetic*: Frames explanations around physical intuition and step-by-step interactive experiments.
4. **Analogy Specialist**: Translates abstract concepts (e.g., Dijkstra's algorithm, mutex locks, linear transformations) into relatable everyday metaphors.
5. **Code Diagnostic Agent**: Evaluates student code snippets, pinpoints syntax/logical bugs, and highlights time/space complexity bottlenecks.

#### 2.2. Full-Duplex Real-Time Voice Agent & Barge-In Detection
- **WebSocket Endpoint**: Implement `/api/v1/voice/session` in `backend/app/api/v1/voice.py`.
- **Audio Pipeline**:
  - Accept incoming binary audio chunks (PCM / WebM) from the browser.
  - Fast Speech-to-Text (STT) parsing.
  - Stream conversational responses from Gemini.
  - Text-to-Speech (TTS) synthesis streamed back over the WebSocket.
- **Barge-In / Interruption Engine**:
  - When the client's microphone detects voice activity while the AI is speaking, the client immediately sends an `{"event": "interrupt"}` frame.
  - The backend instantly cancels any in-flight TTS generation and clears audio queues, returning immediately to the listening state with zero lag.

---

### STEP 3: STRICT QUALITY & ENGINEERING CONSTRAINTS
1. **Zero Breakage**: Do NOT break any of the 59 existing unit/integration tests in `backend/tests/`. Run `pytest backend/tests/` to verify continuously.
2. **Resilience Invariants**: Maintain the zero-downtime fallback mechanisms (`database.py` SQLite fallback and `redis.py` in-memory fallback).
3. **Frontend Compile Cleanliness**:
   - Zero TypeScript errors (`npm run build` in `frontend/` must compile with 0 errors).
   - Zero hydration mismatch warnings (`suppressHydrationWarning` or proper `useEffect` mounting guards).
   - 100% responsive design (flawless on mobile 375px through ultra-wide 4K monitors).
4. **Accessibility (WCAG 2.1 AAA)**:
   - Provide `prefers-reduced-motion` fallbacks for all heavy animations.
   - Proper `aria-live` regions for streaming AI text responses.
   - Screen-reader labels on all interactive icons and audio controls.

---

### EXECUTION WORKFLOW
1. Scan existing routes and code in `backend/app/` and `frontend/src/`.
2. Install required frontend packages (e.g. `npm install framer-motion canvas-confetti @types/canvas-confetti`).
3. Build the Canvas audio visualizer component and Socratic HUD in `frontend/src/components/tutor/`.
4. Implement the multi-agent orchestrator in `ai/agents/` and expose the live Socratic endpoints in `backend/app/api/v1/`.
5. Run full verification: `pytest backend/tests/`, `ruff check .`, `mypy app`, and `npm run build` in `frontend/`.
6. Present a concise summary of all transformed components and animated flows.
```

---

*Generated for LuminaLearn AI (Project Aurora)*
