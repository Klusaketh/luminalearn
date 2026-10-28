# LUMINALEARN AI — USER EXPERIENCE ARCHITECTURE & PRODUCT DESIGN SPECIFICATION

> **Project Aurora | Phase 1: Product Strategy — Step 6**  
> **Document Version:** 1.0.0  
> **Classification:** Master UX Architecture & Human-Centered Design Specification (SSOT)  
> **Status:** Approved / Design Baseline  
> **Target Audience:** Principal Designers, Product Managers, Frontend Engineers, Accessibility Auditors, QA Lead  

---

## 1. Executive Summary & Design Vision

### 1.1 Design Vision & North Star
**LuminaLearn AI** (*Project Aurora*) is built on the philosophy that software should adapt dynamically to the human learner, eliminating the cognitive friction, anxiety, and passivity of legacy EdTech interfaces.

Inspired by the design aesthetics of **Apple** (typography, visual restraint, physical rhythm), **Notion** (modular spatial hierarchy), **Linear** (high-speed keyboard-driven workflows), **Spotify** (personalized progression & fluid transitions), **Stripe** (flawless data visual clarity), and **Duolingo** (frictionless micro-motivations & milestone celebrations), LuminaLearn AI presents a clean, modern, student-first, and teacher-friendly user experience.

```
+-----------------------------------------------------------------------------------+
|                           DESIGN AESTHETIC & PHILOSOPHY                           |
|                                                                                   |
|  [APPLE]      ──► Refined Typography, Visual Restraint, Spatial Balance           |
|  [NOTION]     ──► Modular Cards, Minimal Spatial Hierarchy, Focused Content      |
|  [LINEAR]     ──► High-Density Keyboard Workflows, Sub-100ms Micro-Interactions     |
|  [SPOTIFY]    ──► Dynamic Personalized Discovery & Continuous Context Flow        |
|  [STRIPE]     ──► Precision Data Visualization, Accessible Contrast               |
|  [DUOLINGO]   ──► Non-Intrusive Gamification, Streaks & Visual Progression        |
+-----------------------------------------------------------------------------------+
```

### 1.2 Core Design Principles
1. **Quality over Quantity:** Provide fewer, highly impactful UI elements per screen to maximize learner focus.
2. **Clarity over Complexity:** Present complex Bayesian mastery data through intuitive visual indicators rather than overwhelming statistical tables.
3. **Learning over Decoration:** Every visual accent, micro-animation, and typography scale choice must serve a clear pedagogical function.
4. **Accessibility over Fancy Effects:** Enforce native **WCAG 2.1 AAA** compliance across contrast, keyboard focus, and screen-reader tree structures.
5. **Consistency over Creativity:** Maintain unified spatial grids, card surfaces, button states, and form feedback patterns across all user journeys.
6. **Focus over Clutter:** Eliminate unnecessary navigation sidebars during active learning sessions to preserve student flow state.
7. **Performance over Heavy Animations:** Utilize lightweight CSS transitions ($\le 200\text{ms}$) that never cause UI thread stutter or battery drain.

---

## 2. Part 1: User Roles & Behavioral Personas

```
+-----------------------------------------------------------------------------------+
|                               USER ROLE TAXONOMY                                  |
|                                                                                   |
|  1. STUDENT        ──► Primary Learner (K-12, Higher Ed, Competitive Exams)      |
|  2. TEACHER        ──► Pedagogical Co-Pilot & Cohort Orchestrator                 |
|  3. ADMINISTRATOR  ──► System Operator, Identity & Compliance Manager             |
|  4. PARENT (FUTURE)──► Home Advocate, Progress Observer & B2C Subscriber          |
+-----------------------------------------------------------------------------------+
```

### 2.1 Role 1: Student (Primary Learner)
* **Demographic Profile:** K-12 students (ages 10–18), university undergraduates, and adult competitive exam candidates.
* **UX Goal:** Achieve concept mastery without cognitive overload or exam anxiety.
* **Core Behavioral Traits:** Mobile-first or laptop user, sensitive to slow loading times, easily distracted by complex layouts, requires immediate positive feedback when stuck.
* **Key UX Requirements:** Non-judgmental Socratic AI tutor interface, 1-click continuation of previous study sessions, visual progress rings, WCAG AAA screen reader and high-contrast toggles.

### 2.2 Role 2: Teacher & Instructor (Pedagogical Co-Pilot)
* **Demographic Profile:** K-12 educators, department heads, and university professors.
* **UX Goal:** Identify struggling students instantly and reclaim 15+ hours per week from routine administrative grading.
* **Core Behavioral Traits:** Time-poor, overwhelmed by multi-tab browser clutter, hesitant toward complex software training, values clear actionable data summaries over raw logs.
* **Key UX Requirements:** Educator Command Center dashboard with cohort mastery heatmaps, 1-click AI-assisted rubric grading approval, zero-click at-risk student intervention alerts.

### 2.3 Role 3: Administrator (System & Operations Manager)
* **Demographic Profile:** School district IT administrators, university CIO staff, enterprise L&D managers.
* **UX Goal:** Manage user provisioning, maintain system security, monitor cloud API throughput, and verify data privacy compliance.
* **Core Behavioral Traits:** Data-driven, keyboard-shortcut power user, relies on high-density data tables and audit logs.
* **Key UX Requirements:** High-density administrative tables with batch actions, real-time telemetry metrics, role-based permission toggles (RBAC), exportable compliance reports (FERPA/COPPA).

### 2.4 Role 4: Parent & Guardian (Future Phase)
* **Demographic Profile:** Parents of K-12 students monitoring home learning.
* **UX Goal:** Gain transparent, encouraging visibility into their child's learning velocity without invading their study independence.
* **Core Behavioral Traits:** Accesses platform via mobile app digests or weekly email summaries, non-technical, values clear progress highlights over complex academic jargon.
* **Key UX Requirements:** 1-minute visual progress cards, time-spent metrics, milestone celebration alerts, subscription billing management.

---

## 3. Part 2: Complete Navigation Flows & Maps

### 3.1 Student User Journey Navigation Map

```
[Public Landing Page] ──► [About] ──► [Features] ──► [Pricing (Future)]
        │
        ▼
   [Login Page] ──► [Registration] ──► [Email Verification]
                                                │
                                                ▼
                                    [Welcome / Onboarding Screen]
                                                │
                                                ▼
                                    [Goal & Subject Selection]
                                                │
                                                ▼
                                    [Learning Modality (VARK) Test]
                                                │
                                                ▼
                                    [Adaptive Diagnostic Assessment]
                                                │
                                                ▼
                                    [AI Learner Profile Generation]
                                                │
                                                ▼
                                  +-----------------------------+
                                  |     PERSONAL DASHBOARD      |
                                  +-----------------------------+
                                     │         │             │
                    ┌────────────────┘         │             └────────────────┐
                    ▼                          ▼                              ▼
          [Continue Learning]          [Socratic AI Tutor]             [Progress & Graph]
                    │                          │                              │
                    ▼                          ▼                              ▼
           [Active Lesson UI]          [Interactive Chat]             [Mastery Analytics]
                    │                          │                              │
                    ▼                          ▼                              ▼
          [Adaptive Practice]          [Step Scaffolding]             [Achievement Badges]
                    │                          │                              │
                    └──────────────────────────┼──────────────────────────────┘
                                               │
                                               ▼
                                     [Account Settings / A11y]
```

### 3.2 Teacher User Journey Navigation Map

```
[Public Landing Page] ──► [Teacher Login] ──► [Institutional Verification]
                                                      │
                                                      ▼
                                       +-----------------------------+
                                       |     TEACHER COMMAND CENTER  |
                                       +-----------------------------+
                                          │          │             │
                 ┌────────────────────────┘          │             └────────────────────────┐
                 ▼                                   ▼                                      ▼
     [Course & Class Management]            [Cohort Analytics]                      [Automated Rubrics]
                 │                                   │                                      │
                 ▼                                   ▼                                      ▼
     [Curriculum Module Config]             [At-Risk Student Alerts]               [AI Grade Approvals]
                 │                                   │                                      │
                 └───────────────────────────────────┼──────────────────────────────────────┘
                                                     │
                                                     ▼
                                          [Export Reports & Settings]
```

### 3.3 Administrator User Journey Navigation Map

```
[Admin Login] ──► [2FA Security Check]
                        │
                        ▼
         +-----------------------------+
         |    ADMINISTRATOR DASHBOARD  |
         +-----------------------------+
            │          │             │
   ┌────────┘          │             └────────┐
   ▼                   ▼                      ▼
[User Mgmt]      [Course Mgmt]         [System Telemetry]
   │                   │                      │
   ▼                   ▼                      ▼
[RBAC Config]    [Node Graph Editor]   [Security Audit Logs]
```

---

## 4. Part 3: Version 1 Screen Inventory

The Version 1 release requires **28 unique screen layouts** organized across 8 operational categories.

```
+-----------------------------------------------------------------------------------+
|                              VERSION 1 SCREEN INVENTORY                           |
|                                                                                   |
|  1. AUTHENTICATION (4) ──► Login, Register, Verify Email, Password Reset          |
|  2. ONBOARDING (4)     ──► Welcome, Goal Select, VARK Quiz, Diagnostic Eval      |
|  3. LEARNING (4)       ──► Dashboard, Lesson View, Practice Arena, Graph View     |
|  4. ASSESSMENT (3)     ──► Quiz Mode, Diagnostic Results, Performance Review      |
|  5. AI INTERACTION (3) ──► Socratic Tutor Chat, Hint Drawer, Explainable XAI Modal|
|  6. ANALYTICS (3)      ──► Mastery Heatmap, Streak & Badges, Study Time Reports   |
|  7. SETTINGS (3)       ──► User Profile, Accessibility Config, Notifications      |
|  8. ADMIN & TEACHER(4) ──► Educator Hub, Class Management, Admin Table, Logs      |
+-----------------------------------------------------------------------------------+
```

---

## 5. Part 4: Detailed Screen Specifications

This section defines the precise functional requirements for core screens in Version 1.

---

### 5.1 SCR-01: Authentication — Student & Teacher Login

```
+-----------------------------------------------------------------------------------+
| SCREEN SPECIFICATION: SCR-01 (LOGIN)                                              |
| Category: Authentication                                                          |
| Target User: Students, Teachers, Administrators                                   |
+-----------------------------------------------------------------------------------+
```

1. **Purpose:** Authenticate returning users securely into their respective role-based dashboards.
2. **Primary Goal:** Enable 1-click or credentials login in under 5 seconds with zero visual clutter.
3. **Secondary Goal:** Provide clear navigation for registration, password recovery, and SSO integration.
4. **Target User:** All registered LuminaLearn AI users.
5. **Actions Available:** Email/Password input, "Remember Me" toggle, "Forgot Password" link, "Login with Google/Institutional SSO" button, "Create Account" link.
6. **Navigation:** On success $\rightarrow$ Role Dashboard (`SCR-09` or `SCR-25`). On click Register $\rightarrow$ `SCR-02`.
7. **Expected Behaviour:** Input focus on Email field upon page load. Real-time client-side validation of email format.
8. **Empty State:** Clean card container centered over subtle gradient background, placeholder text in inputs (`name@institution.edu`).
9. **Loading State:** Login button displays inline spinner, inputs disabled, ARIA live region announces "Authenticating...".
10. **Error State:** Red border on input fields (`hsl(var(--destructive))`), inline error message: *"Invalid email or password. Please try again."*
11. **Success State:** Instant smooth fade-out transition, redirecting to personalized dashboard.

---

### 5.2 SCR-05: Onboarding — Adaptive Diagnostic Assessment

```
+-----------------------------------------------------------------------------------+
| SCREEN SPECIFICATION: SCR-05 (DIAGNOSTIC ASSESSMENT)                              |
| Category: Onboarding & Diagnostic                                                 |
| Target User: Newly registered students                                            |
+-----------------------------------------------------------------------------------+
```

1. **Purpose:** Benchmark student's baseline knowledge across target subject concepts.
2. **Primary Goal:** Accurately seed the student's Bayesian Knowledge Graph mastery probabilities without causing test anxiety.
3. **Secondary Goal:** Establish student's baseline hesitation speed and confidence levels.
4. **Target User:** Onboarding students.
5. **Actions Available:** Answer choice selection, "Unsure / Skip" button, "Explain Question (Accessibility)" button, Progress indicator bar.
6. **Navigation:** On completion $\rightarrow$ AI Profile Generation (`SCR-08`) $\rightarrow$ Student Dashboard (`SCR-09`).
7. **Expected Behaviour:** Adaptive question selection (difficulty recalibrates dynamically based on previous answer accuracy). Zero high-stakes timers displayed.
8. **Empty State:** N/A (Questions stream dynamically).
9. **Loading State:** Skeleton loader placeholders for question text and choices while next adaptive question is retrieved (<300ms).
10. **Error State:** If network connection fails, current question is cached locally in `localStorage`, banner displays *"Connection lost. Retrying..."*.
11. **Success State:** On final question, celebratory confetti animation (optional, high-contrast accessible fallback), transition to profile generator.

---

### 5.3 SCR-09: Learning — Student Personal Dashboard

```
+-----------------------------------------------------------------------------------+
| SCREEN SPECIFICATION: SCR-09 (STUDENT DASHBOARD)                                  |
| Category: Learning Core                                                           |
| Target User: Active Students                                                      |
+-----------------------------------------------------------------------------------+
```

1. **Purpose:** Central command center for the student's daily learning journey.
2. **Primary Goal:** Prompt student to click "Continue Learning" on their next recommended micro-concept in 1 click.
3. **Secondary Goal:** Display current streak, daily goal progress ring, recent mastery gains, and quick access to LuminaTutor.
4. **Target User:** Enrolled students.
5. **Actions Available:** "Continue Study Session" primary CTA button, Concept node navigation, Socratic AI Tutor quick-launch floating button, Mastery Heatmap toggle, Profile settings link.
6. **Navigation:** Click Continue $\rightarrow$ Active Lesson UI (`SCR-10`). Click LuminaTutor $\rightarrow$ AI Tutor Chat (`SCR-17`).
7. **Expected Behaviour:** Hero section dynamically displays student's name, current streak count, and next recommended concept based on spacing decay algorithms.
8. **Empty State:** New student view displays "Welcome to LuminaLearn AI! Let's start your first concept." with a prominent Start button.
9. **Loading State:** Shimmer skeleton UI for dashboard cards and progress rings.
10. **Error State:** Soft banner at top if background analytics fail to sync, with cached offline data displayed.
11. **Success State:** Smooth micro-interactions on hover across concept cards; progress ring animates on load.

---

### 5.4 SCR-17: AI Interaction — LuminaTutor Socratic Chat Interface

```
+-----------------------------------------------------------------------------------+
| SCREEN SPECIFICATION: SCR-17 (LUMINATUTOR SOCRATIC CHAT)                          |
| Category: AI Interaction                                                          |
| Target User: Students seeking conceptual help or problem guidance                 |
+-----------------------------------------------------------------------------------+
```

1. **Purpose:** Interactive 1-on-1 Socratic AI tutoring chat interface that guides students through problem-solving step-by-step.
2. **Primary Goal:** Scaffold student understanding through Socratic questioning *without* revealing direct final answers.
3. **Secondary Goal:** Capture student hesitation, confidence, and misconception telemetry.
4. **Target User:** Students working through practice sets or stuck on homework concepts.
5. **Actions Available:** Text chat input, Voice input toggle, Math LaTeX symbol picker, "I'm Stuck / Give Hint" button, "Explain Differently (VARK)" toggle, Clear Chat context button.
6. **Navigation:** Docked side panel within Active Lesson (`SCR-10`) or expandable full-screen chat modal.
7. **Expected Behaviour:** AI streams responses token-by-token (<1.5s first token latency). Responses contain scaffolded questions, LaTeX math formulas, and progressive hints.
8. **Empty State:** Chat displays friendly LuminaTutor avatar, prompt suggestions: *"Stuck on step 2?", "Explain this quadratic formula using a visual analogy", "Give me a practice problem."*
9. **Loading State:** Animated 3-dot pulsing indicator during initial AI inference; streaming text state.
10. **Error State:** Inline chat alert: *"LuminaTutor is taking longer than expected. Click here to retry or request a visual hint."*
11. **Success State:** Student self-discovers correct solution $\rightarrow$ LuminaTutor displays celebratory micro-badge and updates mastery score.

---

### 5.5 SCR-25: Administration & Educator Hub — Teacher Command Center

```
+-----------------------------------------------------------------------------------+
| SCREEN SPECIFICATION: SCR-25 (TEACHER COMMAND CENTER)                             |
| Category: Educator & Administration                                               |
| Target User: Teachers and Course Instructors                                      |
+-----------------------------------------------------------------------------------+
```

1. **Purpose:** High-density overview dashboard for educators to monitor class cohort mastery, review automated rubrics, and intervene with at-risk students.
2. **Primary Goal:** Surface at-risk student intervention alerts and automated rubric approvals in 1 click.
3. **Secondary Goal:** Provide exportable student progress summaries for parent-teacher conferences and institutional compliance.
4. **Target User:** K-12 Teachers, College Professors.
5. **Actions Available:** Filter by class cohort, Approve/Edit AI-graded essay rubrics, Trigger group intervention notification, Export CSV progress report, Manage syllabus nodes.
6. **Navigation:** Click At-Risk Student $\rightarrow$ Student Deep-Dive Analytics (`SCR-26`). Click Rubrics $\rightarrow$ Automated Rubric Grading (`SCR-27`).
7. **Expected Behaviour:** Master table renders 50+ student rows with color-coded mastery status badges (Green = Mastered, Yellow = Learning, Red = At-Risk).
8. **Empty State:** "No classes assigned yet. Click 'Create Class' or contact your school administrator."
9. **Loading State:** Table skeleton rows with shimmer loading effect.
10. **Error State:** Error banner: *"Unable to load real-time telemetry. Showing cached class data from 10 minutes ago."*
11. **Success State:** Batch approval of AI rubrics executes instantly with smooth checkmark animations.

---

## 6. Part 5: User Experience Guidelines & Design System

### 6.1 Visual Hierarchy & Spatial Grid
* **Base Grid System:** 8px Spatial Grid Standard ($8\text{px}, 16\text{px}, 24\text{px}, 32\text{px}, 48\text{px}, 64\text{px}$). All padding, margins, and component dimensions MUST align to multiples of 8px (4px allowed for micro-spacing).
* **Surface Elevation Layers:**
  1. `Layer 0 (Background):` Dark Mode `hsl(224, 71%, 4%)` / Light Mode `hsl(0, 0%, 100%)`.
  2. `Layer 1 (Card Surfaces):` Dark Mode `hsl(222, 47%, 11%)` / Light Mode `hsl(0, 0%, 98%)` with subtle border `hsl(var(--border))`.
  3. `Layer 2 (Modals & Glass Overlays):` Backdrop blur `12px` with 70% opacity surface glass.

```
+-----------------------------------------------------------------------------------+
|                           SPATIAL ELEVATION STACK                                 |
|                                                                                   |
|  [LAYER 2: MODALS & FLOATING TOWERS]  ──► Glassmorphism / Backdrop Blur 12px      |
|            ▲                                                                      |
|  [LAYER 1: CARDS & CONTAINERS]        ──► Surface Color + 1px Subtle Border       |
|            ▲                                                                      |
|  [LAYER 0: CANVAS BACKGROUND]         ──► Base Theme Background Color             |
+-----------------------------------------------------------------------------------+
```

### 6.2 Typography Hierarchy

LuminaLearn AI utilizes system sans-serif font stacks (**Inter**, **SF Pro**, **-apple-system**) for maximum legibility and zero web-font loading latency.

| Typography Token | Font Weight | Line Height | Purpose & Usage |
| :--- | :---: | :---: | :--- |
| **Display Heading** | 700 (Bold) | 1.1 | Hero marketing pages, milestone achievements. |
| **Heading 1 (H1)** | 700 (Bold) | 1.2 | Main page titles (Dashboard, Active Lesson). |
| **Heading 2 (H2)** | 600 (SemiBold) | 1.25 | Section headers, card group titles. |
| **Heading 3 (H3)** | 600 (SemiBold) | 1.3 | Card titles, modal headers. |
| **Body Large** | 400 (Regular) | 1.5 | Primary instructional text, Socratic chat messages. |
| **Body Default** | 400 (Regular) | 1.5 | Standard interface labels, button text. |
| **Caption / Small** | 500 (Medium) | 1.4 | Helper text, metadata badges, timestamps. |
| **Code / Math** | 400 (Monospace)| 1.4 | LaTeX equations, code snippets (`JetBrains Mono`). |

### 6.3 Button & Form Behavior Standards
* **Button States:** Every button MUST implement 5 distinct visual states: *Default*, *Hover* (brightened background + subtle scale 1.01), *Active/Pressed* (scale 0.98), *Focus* (2px primary ring with offset), and *Disabled* (50% opacity, `cursor: not-allowed`).
* **Form Inputs:** Input fields MUST display explicit floating labels or permanent header labels. Never rely solely on placeholder text. Inputs display green checkmarks on valid input and red border + inline text on error.

```
+-----------------------------------------------------------------------------------+
|                             BUTTON STATE TRANSITIONS                              |
|                                                                                   |
|  [DEFAULT] ──► [HOVER: Scale 1.01] ──► [PRESSED: Scale 0.98] ──► [DISABLED: 50%]  |
+-----------------------------------------------------------------------------------+
```

### 6.4 Micro-Interactions & Transitions
* **Duration Standard:** All UI transitions MUST complete within **150ms to 200ms** using cubic-bezier easing (`cubic-bezier(0.16, 1, 0.3, 1)`).
* **Feedback Rules:** Every click, toggle, or score gain MUST produce immediate visual feedback within 16ms (1 frame at 60fps) to eliminate perceived latency.

---

## 7. Part 6: Dashboard Strategy

### 7.1 Student Dashboard Layout Strategy

```
+-----------------------------------------------------------------------------------+
|                            STUDENT DASHBOARD LAYOUT                               |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  | HERO CARD: "Welcome back, Alex!"                                           |  |
|  | Primary Action: [CONTINUE LESSON: Quadratic Equations - Step 3]              |  |
|  +-----------------------------------------------------------------------------+  |
|  | LEFT (65% Width):                    | RIGHT (35% Width):                  |  |
|  | • Active Knowledge Graph Pathway     | • Daily Goal Progress Ring (75%)    |  |
|  | • Recommended Next Micro-Concepts    | • Current Streak: 12 Days 🔥        |  |
|  | • Recent Practice Accuracy Curve     | • LuminaTutor Quick Help Widget     |  |
|  +--------------------------------------+--------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

#### Learner Priorities:
1. **Primary Focus:** Eliminate friction to start studying. The top hero card prominently features a 1-click "Continue Learning" button pointing to the student's exact Zone of Proximal Development (ZPD) topic.
2. **Motivation Signals:** Right column displays streak counter and progress ring prominently to reinforce habit loops.
3. **Cognitive Safety:** Avoid displaying large lists of failed past quizzes; frame historical data as "Mastery Opportunities."

---

### 7.2 Teacher Command Center Layout Strategy

```
+-----------------------------------------------------------------------------------+
|                            TEACHER DASHBOARD LAYOUT                               |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  | TOP METRICS BAR: Active Students: 142 | Avg Mastery: 78% | At-Risk Alerts: 3 |  |
|  +-----------------------------------------------------------------------------+  |
|  | LEFT (70% Width):                    | RIGHT (30% Width):                  |  |
|  | • Class Cohort Mastery Heatmap Table  | • At-Risk Student Intervention Cards |  |
|  | • Automated Rubric Approval Queue    | • Common Class Bottlenecks Widget   |  |
|  | • Bulk Student Management Actions    | • Quick Assignment Creator          |  |
|  +--------------------------------------+--------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

#### Educator Priorities:
1. **Primary Focus:** Instant identification of struggling students (surfaced in top metric bar and right-column intervention cards).
2. **Workflow Efficiency:** Main table area provides 1-click review and approval for AI-graded essay rubrics.
3. **Density & Speed:** High-density data table supporting multi-column sorting, filtering, and instant search.

---

### 7.3 Administrator Dashboard Layout Strategy

```
+-----------------------------------------------------------------------------------+
|                          ADMINISTRATOR DASHBOARD LAYOUT                           |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  | SYSTEM HEALTH: Uptime: 99.99% | API Latency: 320ms | Active Seats: 4,500/5,000|  |
|  +-----------------------------------------------------------------------------+  |
|  | • User Identity & RBAC Management Table (Students, Teachers, Admins)       |  |
|  | • Knowledge Graph Concept Node Editor & Taxonomy Manager                    |  |
|  | • Security Audit Logs, FERPA/COPPA Privacy Compliance Exporter               |  |
+-----------------------------------------------------------------------------------+
```

---

## 8. Part 7: Accessibility & Inclusivity Standards (WCAG 2.1 AAA)

LuminaLearn AI is engineered from day zero to fulfill **WCAG 2.1 AAA** compliance across all user interfaces.

```
+-----------------------------------------------------------------------------------+
|                        ACCESSIBILITY COMPLIANCE PILLARS                           |
|                                                                                   |
|  1. CONTRAST:          Minimum 7:1 ratio for normal text (AAA standard)           |
|  2. KEYBOARD:          100% full keyboard navigation (No focus traps)             |
|  3. SCREEN READERS:    Semantic HTML5 + ARIA Live Regions for dynamic content    |
|  4. NEURODIVERSITY:    Dyslexie font overlay, Motion reduction toggle             |
+-----------------------------------------------------------------------------------+
```

### 8.1 Keyboard Navigation Specifications
* **Focus Indicator:** All focusable components MUST display an explicit, high-contrast 2px primary outline with a 2px offset (`ring-2 ring-primary ring-offset-2`).
* **Tab Order:** Logical left-to-right, top-to-bottom DOM tab order. Modal dialogs MUST enforce focus traps, locking keyboard navigation inside the modal until closed.
* **Shortcut Keys:**
  * `Cmd/Ctrl + K`: Universal search & quick command palette.
  * `Space / Enter`: Activate selected button or toggle.
  * `Esc`: Close current modal, drawer, or active Socratic chat panel.
  * `Alt + A`: Open Universal Accessibility Settings menu.

### 8.2 Screen Reader Compatibility (NVDA, JAWS, VoiceOver)
* **Semantic Structure:** Native HTML5 semantic tags (`<header>`, `<nav>`, `<main>`, `<article>`, `<aside>`, `<footer>`) exclusively.
* **ARIA Live Regions:** Dynamic AI chat responses and notification popups MUST utilize `aria-live="polite"` to ensure screen readers announce new hints without interrupting user reading.
* **Alt Text Standard:** All mathematical diagrams, knowledge graph nodes, and icons MUST include descriptive text alternatives (`alt="Bar chart showing 85% mastery in Quadratic Equations"`).

### 8.3 Color Contrast & Visual Adaptations
* **Contrast Ratios:** Text and interactive elements enforce a **7:1 contrast ratio** against backgrounds (WCAG AAA) for body text, and **4.5:1** for large headings.
* **Dyslexie Font Mode:** Includes an in-app toggle to switch all UI typography to open-source Dyslexie / OpenDyslexic typeface with increased letter spacing.
* **Reduced Motion Mode:** Respects `prefers-reduced-motion: reduce` OS settings, automatically disabling all non-essential CSS transforms and background particle animations.

---

## 9. Part 8: Gamification Framework

Gamification in LuminaLearn AI is designed to foster **intrinsic mastery** rather than superficial distraction.

```
+-----------------------------------------------------------------------------------+
|                              GAMIFICATION ENGINE                                  |
|                                                                                   |
|  • XP (EXPERIENCE POINTS) ──► Awarded for conceptual understanding & effort       |
|  • LEARNING STREAKS       ──► Daily study habit reinforcement (with streak freeze) |
|  • PROGRESS RINGS        ──► Visual daily goal completion indicators              |
|  • MASTERY BADGES         ──► Awarded upon verified Bayesian concept node mastery  |
+-----------------------------------------------------------------------------------+
```

### 8.1 Gamification Mechanics Matrix

| Gamification Component | Trigger Condition | Visual Representation | Pedagogical Purpose |
| :--- | :--- | :--- | :--- |
| **Experience Points (XP)**| Completing practice questions, engaging in Socratic chat. | Floating `+25 XP` micro-toast notification. | Rewards effort and active problem-solving time. |
| **Learning Streaks** | Completing at least 10 minutes of study daily. | Flame icon 🔥 with counter badge on header. | Builds long-term daily learning habits. |
| **Streak Freeze** | Granted automatically once per month for consistent learners. | Shield icon 🛡️ in student profile. | Prevents demoralization from accidental missed days. |
| **Daily Progress Ring** | Progressing toward custom daily learning goal (e.g., 30 mins). | Circular SVG progress ring on student dashboard. | Clear visual goal completion metric. |
| **Mastery Badges** | Achieving $\ge 85\%$ Bayesian probability score on a concept graph. | 3D-styled enamel badge icon in Achievement gallery.| Honors verified conceptual mastery over guesswork. |
| **Leaderboards (Future)**| Opt-in friendly cohort study challenges. | Anonymized class progress ranking cards. | Fosters collaborative social learning motivation. |

---

## 10. Part 9: AI Interaction Strategy & Socratic Experience

### 10.1 AI Persona & Behavioral Identity
LuminaTutor MUST NEVER behave like a generic conversational AI chatbot (e.g., ChatGPT). It is an **AI Socratic Mentor**.

```
+-----------------------------------------------------------------------------------+
|                        SOCRATIC AI INTERACTION PRINCIPLES                         |
|                                                                                   |
|  1. NEVER GIVE DIRECT ANSWERS  ──► Guide through progressive Socratic questioning |
|  2. CONTEXT-AWARE INTELLIGENCE ──► Knows student's history, weak nodes, VARK style|
|  3. SOCRATIC HINT ESCALATION   ──► Concept Hint ──► Diagram ──► Worked Example    |
|  4. EMPATHETIC SCAFFOLDING     ──► Encourages effort, normalizes mistake making   |
+-----------------------------------------------------------------------------------+
```

### 10.2 Context-Aware AI Intelligence
LuminaTutor receives a dynamic contextual payload prior to every response generation:

```json
{
  "student_context": {
    "current_concept": "kn_quadratic_formula",
    "bayesian_mastery": 0.42,
    "recent_mistakes": ["forgot_square_root_sign", "sign_error_b_term"],
    "preferred_modality": "visual",
    "hesitation_velocity": "high_hesitation",
    "current_streak_days": 12
  }
}
```

### 10.3 4-Stage Adaptive Hint Escalation Protocol
When a student triggers the "I'm Stuck / Request Hint" action, LuminaTutor follows a strict 4-stage hint escalation path:

```
  [Stage 1: Socratic Question] ──► "What is the coefficient of the x^2 term in this equation?"
               │
               ▼ (If still stuck)
  [Stage 2: Conceptual Analogy] ──► Visual diagram or real-world physical analogy.
               │
               ▼ (If still stuck)
  [Stage 3: Worked Similar Example] ──► Fully solved problem with DIFFERENT numbers.
               │
               ▼ (If still stuck)
  [Stage 4: Step-by-Step Breakdown] ──► Guiding through step 1 of the specific problem.
```

---

## 11. Part 10: Deliverables & Future UX Roadmap

### 11.1 Immediate Implementation Deliverables Checklist
- [x] **User Role Taxonomy & Personas:** (Student, Teacher, Admin, Parent).
- [x] **Navigation Maps:** Complete flow diagrams for all user types.
- [x] **Screen Inventory:** 28 Version 1 screen layouts defined.
- [x] **Detailed Screen Specifications:** Functional specs for core screens (`SCR-01`, `SCR-05`, `SCR-09`, `SCR-17`, `SCR-25`).
- [x] **Design System Guidelines:** Spatial grid, typography hierarchy, button states, micro-interactions.
- [x] **Dashboard Strategy:** Layout blueprints for Student, Teacher, and Admin views.
- [x] **Accessibility Framework:** WCAG 2.1 AAA compliance specs, screen reader rules, keyboard shortcuts.
- [x] **Gamification Strategy:** XP, Streaks, Progress Rings, Mastery Badges.
- [x] **Socratic AI Strategy:** 4-stage hint escalation protocol and contextual payload specs.

### 11.2 Multi-Phase UX Roadmap

```
+-----------------------------------------------------------------------------------+
|                                 MULTI-PHASE UX ROADMAP                            |
|                                                                                   |
|  PHASE 1 (MVP) ──────► Socratic LuminaTutor, Learner Dashboard, Educator Hub,     |
|                        WCAG 2.1 AAA Accessibility, Core Knowledge Graph UI       |
|                                                                                   |
|  PHASE 2 (POST-MVP) ─► Multi-Lingual Vernacular UI (20+ Regional Languages),      |
|                        Parent Progress Portal, Opt-In Social Study Leaderboards   |
|                                                                                   |
|  PHASE 3 (FUTURE) ───► WebXR 3D Socratic Learning Environments, Voice-Native UI,  |
|                        Verifiable Micro-Credential Skill Wallet                    |
+-----------------------------------------------------------------------------------+
```

---
