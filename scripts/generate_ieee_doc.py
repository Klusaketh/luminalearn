import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def add_callout_box(doc, text_list, bg_color="F1F5F9", border_color="3B82F6"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="none"/>
            <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>
            <w:bottom w:val="none"/>
            <w:right w:val="none"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    for i, line in enumerate(text_list):
        if i > 0:
            p = cell.add_paragraph()
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
        run = p.add_run(line)
        run.font.name = 'Consolas'
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def format_table_header(row, col_widths, bg_color="1E293B"):
    for idx, cell in enumerate(row.cells):
        cell.width = col_widths[idx]
        set_cell_background(cell, bg_color)
        set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.name = 'Arial'
                run.font.size = Pt(9.5)
                run.font.bold = True
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

def format_table_row(row, col_widths, bg_color="FFFFFF", is_even=False):
    fill = "F8FAFC" if is_even else bg_color
    for idx, cell in enumerate(row.cells):
        cell.width = col_widths[idx]
        set_cell_background(cell, fill)
        set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.name = 'Arial'
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

def build_ieee_document():
    doc = Document()
    
    # Page setup - Standard Letter, 0.75 in margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Document Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(4)
    run_title = p_title.add_run("LuminaLearn AI: An Explainable, Cognitive-Adaptive Tutoring Ecosystem Leveraging Dual-Engine Fallback Architecture, VARK Diagnostics, and Socratic Generative Agents")
    run_title.font.name = 'Times New Roman'
    run_title.font.size = Pt(18)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    # Subtitle / Metadata
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(12)
    run_sub = p_sub.add_run("Project Aurora — Master Technical Paper & Complete System Blueprint")
    run_sub.font.name = 'Times New Roman'
    run_sub.font.size = Pt(11)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    # Authors Block
    p_auth = doc.add_paragraph()
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_auth.paragraph_format.space_after = Pt(18)
    r_auth = p_auth.add_run("LuminaLearn AI Research & Core Development Team\n")
    r_auth.font.bold = True
    r_auth.font.size = Pt(10.5)
    r_inst = p_auth.add_run("Department of Computer Science & Educational Technology | System Architecture Division\nOpenAPI Documentation: http://127.0.0.1:8000/docs | Client Engine: Next.js 14 App Router")
    r_inst.font.size = Pt(9.5)
    r_inst.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    # Abstract & Keywords Box
    p_abs = doc.add_paragraph()
    p_abs.paragraph_format.space_before = Pt(6)
    p_abs.paragraph_format.space_after = Pt(4)
    p_abs.paragraph_format.line_spacing = 1.15
    run_abs_title = p_abs.add_run("Abstract—")
    run_abs_title.font.name = 'Times New Roman'
    run_abs_title.font.size = Pt(10)
    run_abs_title.font.bold = True
    
    run_abs_body = p_abs.add_run(
        "Contemporary Learning Management Systems (LMS) predominantly employ static, linear instructional paths "
        "that fail to accommodate student cognitive diversity, resulting in divergent retention rates and low completion metrics. "
        "While generative Artificial Intelligence (GenAI) introduces opportunities for personalized education, standard Large Language "
        "Models (LLMs) suffer from unchecked hallucinations and provide immediate answers that impede critical reasoning. "
        "This paper presents LuminaLearn AI (Project Aurora), an enterprise-grade, cloud-native adaptive tutoring ecosystem designed "
        "to personalize learning trajectories through cognitive diagnostics, Socratic dialogue constraints, and zero-downtime infrastructure resilience. "
        "LuminaLearn AI integrates a 16-item diagnostic onboarding engine grounded in Fleming's VARK (Visual, Auditory, Read/Write, Kinesthetic) model, "
        "dynamic Bayesian Knowledge Tracing (BKT), and a hybrid multi-tier persistence layer. The system architecture pairs an asynchronous Python "
        "FastAPI backend with a Next.js 14 App Router frontend, featuring an automated resilience engine that seamlessly transitions between PostgreSQL/Redis "
        "and embedded SQLite (aiosqlite)/in-memory caching. We present the end-to-end mathematical model, the completed baseline infrastructure "
        "(accounting for ~56% of total lifecycle milestones), and the planned integration roadmap for Retrieval-Augmented Generation (RAG) using "
        "Qdrant vector indexing, Google Gemini 1.5 Flash/Pro Socratic agents, and longitudinal efficacy evaluation."
    )
    run_abs_body.font.name = 'Times New Roman'
    run_abs_body.font.size = Pt(10)

    # Keywords
    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_after = Pt(14)
    run_kw_title = p_kw.add_run("Index Terms—")
    run_kw_title.font.name = 'Times New Roman'
    run_kw_title.font.size = Pt(9.5)
    run_kw_title.font.bold = True
    run_kw_title.font.italic = True
    
    run_kw_body = p_kw.add_run("Adaptive Learning Systems, Intelligent Tutoring Systems (ITS), Socratic Dialogue, VARK Modality, Bayesian Knowledge Tracing (BKT), Large Language Models, FastAPI, Next.js, Explainable AI (XAI), High-Availability Fallback Architecture.")
    run_kw_body.font.name = 'Times New Roman'
    run_kw_body.font.size = Pt(9.5)
    run_kw_body.font.italic = True

    # Divider
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_after = Pt(10)
    r_div = p_div.add_run("―" * 58)
    r_div.font.color.rgb = RGBColor(0xCB, 0xD5, 0xE1)

    # SECTION I: INTRODUCTION
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(12)
    h1.paragraph_format.space_after = Pt(4)
    r_h1 = h1.add_run("I. INTRODUCTION & PROBLEM FORMULATION")
    r_h1.font.name = 'Times New Roman'
    r_h1.font.size = Pt(12)
    r_h1.font.bold = True
    r_h1.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p1 = doc.add_paragraph()
    p1.paragraph_format.space_after = Pt(6)
    p1.paragraph_format.line_spacing = 1.15
    p1.add_run(
        "In 1984, educational psychologist Benjamin Bloom identified the famous '2-Sigma Problem': students who received one-on-one "
        "mastery tutoring performed two standard deviations better than students in traditional classroom lectures. Despite billions invested "
        "in online EdTech over the subsequent four decades, mainstream platforms (e.g., Coursera, Udemy, standard Moodle LMS) remain static, "
        "one-size-fits-all content repositories. Every student, regardless of prior knowledge, learning style, or cognitive speed, is subjected "
        "to the exact same linear video sequences and static multiple-choice evaluations.\n\n"
        "Recent breakthroughs in Large Language Models (LLMs) provide the raw generative intelligence necessary to deliver personalized instruction. "
        "However, direct deployment of generic commercial LLMs (e.g., raw ChatGPT or Claude) introduces three critical educational hazards:\n"
        "1) Passive Solution Spoon-Feeding: LLMs immediately output final answers to homework problems, bypassing the student's cognitive struggle and eliminating deeper neural schema formation.\n"
        "2) Epistemic Inaccuracies & Hallucinations: Probabilistic token generators frequently output incorrect mathematical derivations or non-existent citations without warning.\n"
        "3) Infrastructure Rigidity & Service Fragility: Traditional enterprise architectures crash if Redis or PostgreSQL are unavailable, making edge or localized deployments fragile.\n\n"
        "LuminaLearn AI (Project Aurora) addresses these fundamental shortcomings by integrating cognitive profiling, guarded Socratic AI agents, "
        "and a resilient hybrid software architecture."
    )

    # Research Contributions Box
    add_callout_box(doc, [
        "MAJOR RESEARCH & ENGINEERING CONTRIBUTIONS:",
        "• Fleming VARK Diagnostic Engine: 16-point situational questionnaire quantifying cognitive sensory modalities.",
        "• Guarded Socratic Dialogue Pipeline: Rejects direct answer requests; employs 3-tier scaffolded hint ladders.",
        "• Dual-Engine Zero-Downtime Resilience: PostgreSQL 16 <-> SQLite (aiosqlite) ORM fallback and Redis <-> In-Memory TTL cache.",
        "• Fully Implemented Monorepo Foundation: FastAPI async backend + Next.js 14 App Router frontend (~56% completed)."
    ], bg_color="EFF6FF", border_color="2563EB")

    # SECTION II: THEORETICAL & PEDAGOGICAL FOUNDATION
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(4)
    r_h2 = h2.add_run("II. THEORETICAL & PEDAGOGICAL FOUNDATIONS")
    r_h2.font.name = 'Times New Roman'
    r_h2.font.size = Pt(12)
    r_h2.font.bold = True
    r_h2.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p2 = doc.add_paragraph()
    p2.paragraph_format.space_after = Pt(6)
    p2.paragraph_format.line_spacing = 1.15
    p2.add_run(
        "A. Fleming's VARK Modality Model\n"
        "Learners assimilate sensory information through four primary modalities: Visual (V), Auditory (A), Read/Write (R), and Kinesthetic (K). "
        "During onboarding, learners complete an assessment of N=16 questions. For each question i, weights w_(i,m) are assigned to modality m. "
        "The normalized preference score S_m is evaluated as:"
    )

    # VARK Equation Box
    add_callout_box(doc, [
        "VARK Normalized Modality Formulation:",
        "    S_m = ( SUM_{i=1 to N} w_{i,m} ) / ( SUM_{m' in M} SUM_{i=1 to N} w_{i,m'} )",
        "Primary Modality Assignment:",
        "    m_star = argmax_{m in {Visual, Auditory, Read/Write, Kinesthetic}} (S_m)"
    ], bg_color="F8FAFC", border_color="64748B")

    p2_b = doc.add_paragraph()
    p2_b.paragraph_format.space_after = Pt(6)
    p2_b.paragraph_format.line_spacing = 1.15
    p2_b.add_run(
        "B. Bayesian Knowledge Tracing (BKT) Engine\n"
        "Concept mastery across the curriculum knowledge graph is governed by Corbett and Anderson's Bayesian Knowledge Tracing model. "
        "For each concept node, the system models the probability P(L_t) that a learner has mastered the skill at step t upon observing correctness C_t in {0, 1}:"
    )

    add_callout_box(doc, [
        "Bayesian Knowledge Tracing (Corbett & Anderson):",
        "1. Probability update on correct response (C_t = 1):",
        "   P(L_t | C_t=1) = [ P(L_{t-1}) * (1 - P(S)) ] / [ P(L_{t-1}) * (1 - P(S)) + (1 - P(L_{t-1})) * P(G) ]",
        "",
        "2. Probability update on incorrect response (C_t = 0):",
        "   P(L_t | C_t=0) = [ P(L_{t-1}) * P(S) ] / [ P(L_{t-1}) * P(S) + (1 - P(L_{t-1})) * (1 - P(G)) ]",
        "",
        "3. Skill transition update:",
        "   P(L_t) = P(L_t | C_t) + (1 - P(L_t | C_t)) * P(T)",
        "",
        "Where: P(L_0) = Prior knowledge, P(T) = Transition rate, P(G) = Guess rate, P(S) = Slip rate."
    ], bg_color="F8FAFC", border_color="64748B")

    p2_c = doc.add_paragraph()
    p2_c.paragraph_format.space_after = Pt(6)
    p2_c.paragraph_format.line_spacing = 1.15
    p2_c.add_run(
        "C. Ebbinghaus Forgetting Curve & Spaced Repetition\n"
        "Human memory retention decays exponentially over time. LuminaLearn AI computes retention probability R(t) = exp(-t / S), "
        "where t is elapsed time and S is memory stability. When R(t) drops below the cognitive threshold tau = 0.65, the system automatically "
        "inserts proactive spaced-retrieval prompts into the student's daily study plan."
    )

    # SECTION III: SYSTEM ARCHITECTURE
    h3 = doc.add_paragraph()
    h3.paragraph_format.space_before = Pt(14)
    h3.paragraph_format.space_after = Pt(4)
    r_h3 = h3.add_run("III. END-TO-END SYSTEM ARCHITECTURE & ENGINEERING")
    r_h3.font.name = 'Times New Roman'
    r_h3.font.size = Pt(12)
    r_h3.font.bold = True
    r_h3.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p3 = doc.add_paragraph()
    p3.paragraph_format.space_after = Pt(6)
    p3.paragraph_format.line_spacing = 1.15
    p3.add_run(
        "LuminaLearn AI is structured as an enterprise monorepo with clean microservice boundaries, separating presentation, "
        "business domain logic, resilient persistence, and AI orchestration."
    )

    # Tech Stack Table
    t_stack = doc.add_table(rows=1, cols=4)
    t_stack.alignment = WD_TABLE_ALIGNMENT.CENTER
    widths = [Inches(1.5), Inches(1.8), Inches(1.2), Inches(2.5)]
    
    hdr = t_stack.rows[0]
    hdr.cells[0].paragraphs[0].text = "Domain Layer"
    hdr.cells[1].paragraphs[0].text = "Technology / Framework"
    hdr.cells[2].paragraphs[0].text = "Version"
    hdr.cells[3].paragraphs[0].text = "Architectural Purpose"
    format_table_header(hdr, widths)

    stack_data = [
        ("Frontend Web Client", "Next.js (App Router) + React", "14.2+ / 18.3", "Server Components, dynamic SSR/SSG, accessible layout"),
        ("Frontend Typing & State", "TypeScript + Zustand", "5.4+ / 4.5+", "Strict interface validation & persistent client auth store"),
        ("Styling & Design System", "Tailwind CSS + Lucide Icons", "3.4+", "Apple/Linear dark glassmorphic design, WCAG 2.1 AAA"),
        ("Backend Microservice", "FastAPI (Python)", "0.110+ / 3.11+", "Asynchronous REST microservice with native OpenAPI Swagger"),
        ("ORM & Schema Mapping", "Async SQLAlchemy", "2.0+", "Dual-engine database abstraction with cross-DB Uuid support"),
        ("Primary Database", "PostgreSQL", "16.2+", "Relational ACID storage for users, curriculum, mastery scores"),
        ("Fallback Database", "SQLite (aiosqlite)", "0.22+", "Zero-config embedded DB fallback for 100% offline resilience"),
        ("Cache & Session Store", "Redis + In-Memory Fallback", "7.2+", "Distributed session cache with automatic dictionary TTL fallback"),
        ("AI Generative Engine", "Google Gemini API (Planned)", "1.5 Pro / Flash", "Long-context (1M+ token) Socratic tutoring & hint generation"),
        ("Vector Knowledge DB", "Qdrant Vector DB (Planned)", "1.9+", "Hybrid sparse/dense search for RAG concept grounding")
    ]

    for idx, (dom, tech, ver, purp) in enumerate(stack_data):
        row = t_stack.add_row()
        row.cells[0].paragraphs[0].text = dom
        row.cells[1].paragraphs[0].text = tech
        row.cells[2].paragraphs[0].text = ver
        row.cells[3].paragraphs[0].text = purp
        format_table_row(row, widths, is_even=(idx % 2 == 1))

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # SECTION IV: COMPLETED SUBSYSTEMS (~56% COMPLETE)
    h4 = doc.add_paragraph()
    h4.paragraph_format.space_before = Pt(14)
    h4.paragraph_format.space_after = Pt(4)
    r_h4 = h4.add_run("IV. COMPLETED SUBSYSTEMS & VERIFICATION (~56% COMPLETED)")
    r_h4.font.name = 'Times New Roman'
    r_h4.font.size = Pt(12)
    r_h4.font.bold = True
    r_h4.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p4 = doc.add_paragraph()
    p4.paragraph_format.space_after = Pt(6)
    p4.paragraph_format.line_spacing = 1.15
    p4.add_run(
        "As audited in the project charter and workflow tracker, Phases 1 through 4 are 100% complete, and Phase 5 (Build) is 50% complete, "
        "yielding an overall project completion metric of approximately 56%.\n\n"
        "Key completed deliverables include:\n"
        "1. Adaptive Resilience Persistence Layer (backend/app/core/database.py & redis.py):\n"
        "   - Implemented async SQLAlchemy 2.0 dual-engine orchestration. When PostgreSQL is unreachable, the system activates "
        "sqlite+aiosqlite:///./luminalearn.db without service interruption. Uses sqlalchemy.Uuid(as_uuid=True) for seamless dialect compatibility.\n"
        "   - Redis fallback wrapper provides an in-memory dictionary cache with TTL eviction for password tokens and verification codes.\n"
        "2. Authentication & Authorization Subsystem (backend/app/api/v1/auth.py):\n"
        "   - Issues JWT token pairs (15-min access token, 7-day refresh token) encrypted with Argon2id.\n"
        "   - Endpoints operational: /register, /login, /me, /verify-email, /reset-password (anti-enumeration protected).\n"
        "3. Cognitive VARK Diagnostic Onboarding Engine (backend/app/api/v1/onboarding.py):\n"
        "   - GET /questions serves 16 cognitive assessment questions.\n"
        "   - POST /submit evaluates student responses, calculates normalized VARK weights, and updates the student profile.\n"
        "4. Academic Curriculum Graph (backend/app/api/v1/content.py):\n"
        "   - Implements full academic hierarchy: Categories -> Subjects -> Courses -> Modules -> Topics -> Lessons.\n"
        "5. Modern Accessible Frontend Client (frontend/src/app/):\n"
        "   - Next.js 14 App Router pages: Landing page, Login, Register, Diagnostic Onboarding, Student Dashboard, Topic Views, and Password Recovery.\n"
        "   - Integrated Zustand auth store (useAuthStore) with localStorage session restoration and automatic token refresh.\n"
        "6. Code Quality Verification:\n"
        "   - Python linter (ruff) and strict type checker (mypy) pass with 0 errors.\n"
        "   - Next.js production build (npm run build) compiles with 0 hydration or SSR errors."
    )

    # SECTION V: IN-PROGRESS & PLANNED ROADMAP
    h5 = doc.add_paragraph()
    h5.paragraph_format.space_before = Pt(14)
    h5.paragraph_format.space_after = Pt(4)
    r_h5 = h5.add_run("V. IN-PROGRESS & UNCOMPLETED MODULES (PHASES 5.6 - 8)")
    r_h5.font.name = 'Times New Roman'
    r_h5.font.size = Pt(12)
    r_h5.font.bold = True
    r_h5.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p5 = doc.add_paragraph()
    p5.paragraph_format.space_after = Pt(6)
    p5.paragraph_format.line_spacing = 1.15
    p5.add_run(
        "The remaining 44% of the project lifecycle encompasses the advanced AI pipeline, streaming interfaces, and production testing:\n\n"
        "A. Phase 5.6: Google Gemini Socratic AI Agent Framework (Active / Planned Next)\n"
        "   • Integration of google-generativeai SDK with Gemini 1.5 Pro and Gemini 1.5 Flash models.\n"
        "   • Guardrail Prompt Engineering: Versioned Jinja2 prompt envelopes enforcing strict 'zero-direct-answer' rules.\n"
        "   • 3-Tier Dynamic Hint Ladder: Provides conceptual guidance (Tier 1), structural breakdown (Tier 2), and operational syntax hints (Tier 3).\n\n"
        "B. Phase 5.7: Qdrant Vector Database & Curriculum RAG Pipeline (Planned)\n"
        "   • Setup of Qdrant vector database container for localized textbook embeddings.\n"
        "   • Hybrid semantic retrieval combining dense cosine similarity with BM25 sparse keyword matching.\n"
        "   • Dynamic context injection to eliminate LLM hallucinations on STEM formulas.\n\n"
        "C. Phase 5.8: Live Streaming Tutor Chat UI & Educator Portal (Planned)\n"
        "   • Next.js streaming component using Server-Sent Events (SSE) or WebSockets in frontend/src/app/tutor/.\n"
        "   • Real-time KaTeX LaTeX rendering and code syntax highlighting.\n"
        "   • Teacher / Parent Oversight Dashboard displaying real-time cognitive hesitation indices and knowledge state heatmaps.\n\n"
        "D. Phase 6: Automated Testing, Security & AI Audits (Planned)\n"
        "   • Comprehensive Pytest suite covering backend auth, onboarding, and content repositories.\n"
        "   • Playwright E2E browser test automation across student journeys.\n"
        "   • LLM-as-a-judge bias, safety, and hallucination regression audits.\n\n"
        "E. Phase 7 & 8: Cloud Deployment & Post-Launch Operations (Planned)\n"
        "   • Kubernetes (EKS/GKE) Helm chart orchestration, multi-stage Docker containerization, and GitHub Actions CI/CD.\n"
        "   • Prometheus and Grafana telemetry pipelines monitoring P99 latency (<800ms) and token consumption."
    )

    # Lifecycle Milestones Table
    t_phase = doc.add_table(rows=1, cols=4)
    t_phase.alignment = WD_TABLE_ALIGNMENT.CENTER
    w_phase = [Inches(1.2), Inches(2.3), Inches(1.2), Inches(2.3)]
    
    h_phase = t_phase.rows[0]
    h_phase.cells[0].paragraphs[0].text = "Phase"
    h_phase.cells[1].paragraphs[0].text = "Name & Scope"
    h_phase.cells[2].paragraphs[0].text = "Status"
    h_phase.cells[3].paragraphs[0].text = "Key Deliverables"
    format_table_header(h_phase, w_phase)

    phase_data = [
        ("Phase 1", "Product Strategy", "100% Done", "Charter, Market TAM/SAM/SOM, Competitive Matrix"),
        ("Phase 2", "Requirements Engineering", "100% Done", "20 Stakeholder Personas, FERPA/COPPA/WCAG specs"),
        ("Phase 3", "System Architecture", "100% Done", "Monorepo specs, Relational DDL, Resilience blueprints"),
        ("Phase 4", "UX / UI Design Systems", "100% Done", "Apple/Linear glassmorphic tokens, wireframes, Tailwind"),
        ("Phase 5", "Implementation & Build", "50% Active", "Auth, Onboarding, Dual-DB done; Gemini & RAG planned"),
        ("Phase 6", "QA & Security Audits", "15% Done", "Ruff/Mypy pass; Pytest suite & E2E tests pending"),
        ("Phase 7", "Deployment & CI/CD", "10% Done", "Docker Compose done; K8s & Cloud CI/CD pending"),
        ("Phase 8", "Operations & Telemetry", "0% Planned", "Prometheus/Grafana, Teacher manuals, Efficacy trials")
    ]

    for idx, (ph, nm, st, deliv) in enumerate(phase_data):
        row = t_phase.add_row()
        row.cells[0].paragraphs[0].text = ph
        row.cells[1].paragraphs[0].text = nm
        row.cells[2].paragraphs[0].text = st
        row.cells[3].paragraphs[0].text = deliv
        format_table_row(row, w_phase, is_even=(idx % 2 == 1))

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # SECTION VI: COMPARATIVE ANALYSIS
    h6 = doc.add_paragraph()
    h6.paragraph_format.space_before = Pt(14)
    h6.paragraph_format.space_after = Pt(4)
    r_h6 = h6.add_run("VI. COMPARATIVE SYSTEM ANALYSIS")
    r_h6.font.name = 'Times New Roman'
    r_h6.font.size = Pt(12)
    r_h6.font.bold = True
    r_h6.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    t_comp = doc.add_table(rows=1, cols=4)
    t_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
    w_comp = [Inches(1.6), Inches(1.6), Inches(1.6), Inches(2.2)]
    
    h_comp = t_comp.rows[0]
    h_comp.cells[0].paragraphs[0].text = "Dimension"
    h_comp.cells[1].paragraphs[0].text = "Traditional LMS"
    h_comp.cells[2].paragraphs[0].text = "Raw LLM (ChatGPT)"
    h_comp.cells[3].paragraphs[0].text = "LuminaLearn AI"
    format_table_header(h_comp, w_comp)

    comp_data = [
        ("Pedagogy", "Passive video streaming", "Direct answer generation", "Socratic inquiry & scaffolded hint ladders"),
        ("Cognitive Fit", "None (one-size-fits-all)", "Manual user prompt required", "Automated 16-point VARK profiling"),
        ("Knowledge Model", "Static quiz percentages", "Session-isolated memory", "Bayesian Knowledge Tracing (BKT)"),
        ("Factual Grounding", "Verified static text", "Prone to hallucinations", "Curriculum Qdrant Vector RAG"),
        ("System Resilience", "Single DB dependency", "Third-party cloud dependent", "Dual-engine (Postgres <-> SQLite fallback)"),
        ("Accessibility", "Standard WCAG AA", "Text-only", "WCAG 2.1 AAA glassmorphic design")
    ]

    for idx, (dim, lms, llm, lum) in enumerate(comp_data):
        row = t_comp.add_row()
        row.cells[0].paragraphs[0].text = dim
        row.cells[1].paragraphs[0].text = lms
        row.cells[2].paragraphs[0].text = llm
        row.cells[3].paragraphs[0].text = lum
        format_table_row(row, w_comp, is_even=(idx % 2 == 1))

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # SECTION VII: ETHICAL SAFEGUARDS & CONCLUSION
    h7 = doc.add_paragraph()
    h7.paragraph_format.space_before = Pt(14)
    h7.paragraph_format.space_after = Pt(4)
    r_h7 = h7.add_run("VII. ETHICAL SAFEGUARDS, PRIVACY & CONCLUSION")
    r_h7.font.name = 'Times New Roman'
    r_h7.font.size = Pt(12)
    r_h7.font.bold = True
    r_h7.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p7 = doc.add_paragraph()
    p7.paragraph_format.space_after = Pt(6)
    p7.paragraph_format.line_spacing = 1.15
    p7.add_run(
        "A. Privacy & FERPA/COPPA Compliance\n"
        "LuminaLearn AI enforces strict student privacy by sanitizing all PII prior to AI dispatch. Outgoing inference requests "
        "to Google Gemini utilize zero-data-retention headers (X-GOOG-DATA-POLICY: ZERO-RETENTION), preventing student queries "
        "from being retained for foundation model training.\n\n"
        "B. Conclusion\n"
        "LuminaLearn AI addresses Benjamin Bloom's 2-Sigma challenge through a scalable, resilient software ecosystem. "
        "By fusing Fleming's VARK cognitive diagnostics, Bayesian Knowledge Tracing, guarded Socratic LLM agents, and a dual-engine "
        "zero-downtime architecture, the system provides a robust blueprint for equitable, 1-on-1 intelligent tutoring. With the foundational "
        "~56% of infrastructure fully implemented and verified, ongoing execution of the Gemini Socratic dialogue and Qdrant RAG pipeline "
        "will establish LuminaLearn AI as a premier standard for applied AI in education."
    )

    # REFERENCES
    h_ref = doc.add_paragraph()
    h_ref.paragraph_format.space_before = Pt(14)
    h_ref.paragraph_format.space_after = Pt(4)
    r_href = h_ref.add_run("REFERENCES")
    r_href.font.name = 'Times New Roman'
    r_href.font.size = Pt(11)
    r_href.font.bold = True

    references = [
        "[1] B. S. Bloom, 'The 2 Sigma Problem: The Search for Methods of Group Instruction as Effective as One-to-One Tutoring,' Educational Researcher, vol. 13, no. 6, pp. 4–16, 1984.",
        "[2] D. H. Jonassen, 'Designing Constructivist Learning Environments,' Instructional-Design Theories and Models, vol. 2, pp. 215–239, 1999.",
        "[3] N. D. Fleming and C. Mills, 'Not Another Inventory, Rather a Catalyst for Reflection,' To Improve the Academy, vol. 11, no. 1, pp. 137–155, 1992.",
        "[4] A. T. Corbett and J. R. Anderson, 'Knowledge Tracing: Modeling the Acquisition of Procedural Knowledge,' User Modeling and User-Adapted Interaction, vol. 4, no. 4, pp. 253–278, 1994.",
        "[5] J. Sweller, 'Cognitive Load During Problem Solving: Effects on Learning,' Cognitive Science, vol. 12, no. 2, pp. 257–285, 1988.",
        "[6] A. Vaswani et al., 'Attention Is All You Need,' in Advances in Neural Information Processing Systems (NeurIPS), 2017, pp. 5998–6008.",
        "[7] S. M. Barnett and S. J. Ceci, 'When and Where Do We Apply What We Learn? A Taxonomy for Far Transfer,' Psychological Bulletin, vol. 128, no. 4, pp. 612–637, 2002.",
        "[8] World Wide Web Consortium (W3C), 'Web Content Accessibility Guidelines (WCAG) 2.1,' W3C Recommendation, Jun. 2018."
    ]

    for ref in references:
        p_r = doc.add_paragraph()
        p_r.paragraph_format.space_before = Pt(2)
        p_r.paragraph_format.space_after = Pt(2)
        p_r.paragraph_format.line_spacing = 1.1
        r = p_r.add_run(ref)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(8.5)

    # APPENDIX / MASTER PROMPT
    doc.add_page_break()
    h_app = doc.add_paragraph()
    h_app.paragraph_format.space_before = Pt(12)
    h_app.paragraph_format.space_after = Pt(4)
    r_happ = h_app.add_run("APPENDIX: MASTER IEEE GENERATIVE PROMPT")
    r_happ.font.name = 'Times New Roman'
    r_happ.font.size = Pt(13)
    r_happ.font.bold = True
    r_happ.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    p_app_intro = doc.add_paragraph()
    p_app_intro.paragraph_format.space_after = Pt(8)
    p_app_intro.add_run(
        "The following master prompt can be copied and supplied to advanced LLMs (e.g., Google Gemini 1.5 Pro, "
        "Claude 3.5 Sonnet, GPT-4o) or Overleaf LaTeX assistants to automatically produce camera-ready IEEE LaTeX code "
        "or academic thesis chapters for LuminaLearn AI."
    )

    prompt_lines = [
        "### MASTER PROMPT: IEEE RESEARCH PAPER GENERATOR FOR LUMINALEARN AI",
        "",
        "Act as a Principal Software Architect, Distinguished AI Researcher, and Senior IEEE Fellow in Computer Science and Educational Technology.",
        "Write a complete, highly technical, camera-ready IEEE Conference / Transactions Research Paper formatted in IEEE LaTeX (\\documentclass[conference]{IEEEtran}) based on the following specifications of 'LuminaLearn AI' (Project Aurora):",
        "",
        "1. PROJECT METADATA:",
        "   • Title: LuminaLearn AI: An Explainable, Cognitive-Adaptive Tutoring Ecosystem Leveraging Dual-Engine Fallback Architecture, VARK Diagnostics, and Socratic Generative Agents",
        "   • Core Paradigm: Socratic Intelligent Tutoring System (ITS), Bayesian Knowledge Tracing (BKT), Multimodal Personalization (VARK), and Resilient Microservices.",
        "   • Frontend: Next.js 14.2+ (App Router), TypeScript 5.4, Tailwind CSS, Zustand client store, TanStack Query, WCAG 2.1 AAA Accessibility.",
        "   • Backend: FastAPI 0.110+, Python 3.11+, Async SQLAlchemy 2.0, Pydantic v2, PyJWT, Argon2id encryption.",
        "   • Dual-Engine Resilience: PostgreSQL 16 <-> SQLite (aiosqlite) ORM fallback and Redis 7 <-> In-Memory Python Dict TTL fallback.",
        "   • AI Foundation (Planned): Google Gemini 1.5 Pro/Flash, Qdrant Vector DB for hybrid semantic search & RAG.",
        "",
        "2. REQUIRED MATHEMATICAL FORMULATIONS:",
        "   • Fleming's VARK Modality Normalization Formula: S_m = ( SUM w_{i,m} ) / ( SUM SUM w_{i,m'} )",
        "   • Bayesian Knowledge Tracing (Corbett & Anderson): P(L_t | C_t = 1), P(L_t | C_t = 0), and P(L_t) transition equation.",
        "   • Ebbinghaus Forgetting Curve: R(t) = exp(-t / S).",
        "",
        "3. REQUIRED PAPER SECTIONS (IEEE TRANSACTIONS SPECIFICATION):",
        "   • Section I: Introduction (Bloom's 2-Sigma problem, limitations of standard LMS and raw LLMs, key contributions).",
        "   • Section II: Theoretical & Pedagogical Foundations (VARK sensory model, Sweller Cognitive Load, BKT & Ebbinghaus math).",
        "   • Section III: System Architecture & Resilient Engineering (Data flow diagram, Dual-engine fallback mechanics, Relational DDL).",
        "   • Section IV: Completed Subsystems & Implementation Verification (Phase 1 to 5.5, Auth, Onboarding, Content, Zustand, Ruff/Mypy 0 errors).",
        "   • Section V: In-Progress & Uncompleted Modules (Phase 5.6 Gemini Socratic Guardrails, Phase 5.7 Qdrant RAG, Phase 5.8 Streaming chat).",
        "   • Section VI: Comparative System Analysis (LuminaLearn AI vs Coursera, Duolingo, Khan Academy, vanilla LLMs).",
        "   • Section VII: Ethical Safeguards, Privacy & FERPA/COPPA (Zero-data-retention headers).",
        "   • Section VIII: Conclusion & References (IEEE format citations).",
        "",
        "TONE: Extreme academic rigor, formal scholarly tone, precise computer science nomenclature, and mathematical equations."
    ]

    add_callout_box(doc, prompt_lines, bg_color="F8FAFC", border_color="3B82F6")

    output_path = r"c:\Users\Sudar\OneDrive\Desktop\LUMINALEARN AI\IEEE final document.docx"
    doc.save(output_path)
    print(f"Document successfully created at: {output_path}")

if __name__ == "__main__":
    build_ieee_document()
