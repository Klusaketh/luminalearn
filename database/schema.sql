-- ==============================================================================
-- LUMINALEARN AI — MASTER DATABASE RELATIONAL SCHEMA (POSTGRESQL 16)
-- ==============================================================================
-- Classification: Master DDL Specification Baseline
-- Document Version: 1.0.0

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Custom Domain Enums
CREATE TYPE user_role AS ENUM ('student', 'teacher', 'admin', 'parent');
CREATE TYPE vark_modality AS ENUM ('visual', 'auditory', 'read_write', 'kinesthetic');
CREATE TYPE interaction_type AS ENUM ('question_attempt', 'socratic_hint', 'concept_view', 'assessment');

-- ------------------------------------------------------------------------------
-- 1. USERS TABLE
-- Stores core authentication identity and pedagogical preference profiles.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'student',
    preferred_modality vark_modality DEFAULT 'visual',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- ------------------------------------------------------------------------------
-- 2. KNOWLEDGE NODES TABLE (BAYESIAN KNOWLEDGE GRAPH)
-- Represents micro-concept nodes and prerequisite dependency links.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS knowledge_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    concept_code VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    subject VARCHAR(100) NOT NULL,
    parent_node_id UUID REFERENCES knowledge_nodes(id) ON DELETE SET NULL,
    difficulty_level FLOAT DEFAULT 0.5,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_nodes_concept_code ON knowledge_nodes(concept_code);
CREATE INDEX idx_nodes_subject ON knowledge_nodes(subject);

-- ------------------------------------------------------------------------------
-- 3. MASTERY SCORES TABLE
-- Traces real-time Bayesian probability of mastery P(L) per student per concept.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mastery_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    node_id UUID NOT NULL REFERENCES knowledge_nodes(id) ON DELETE CASCADE,
    mastery_probability FLOAT DEFAULT 0.1, -- P(L) between 0.0 and 1.0
    last_assessed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_node_mastery UNIQUE(user_id, node_id)
);

CREATE INDEX idx_mastery_user_node ON mastery_scores(user_id, node_id);

-- ------------------------------------------------------------------------------
-- 4. LEARNING SESSIONS TABLE
-- Groups interactions into structured temporal learning sessions.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    started_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMPTZ,
    total_interactions INT DEFAULT 0
);

CREATE INDEX idx_sessions_user ON learning_sessions(user_id);

-- ------------------------------------------------------------------------------
-- 5. TELEMETRY LOGS TABLE
-- High-throughput diagnostic logs capturing hesitation velocity and accuracy.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS telemetry_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    node_id UUID REFERENCES knowledge_nodes(id) ON DELETE SET NULL,
    interaction_type interaction_type NOT NULL DEFAULT 'question_attempt',
    hesitation_time_ms INT NOT NULL DEFAULT 0,
    is_correct BOOLEAN NOT NULL DEFAULT FALSE,
    cognitive_load_index FLOAT DEFAULT 0.5,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_telemetry_session ON telemetry_logs(session_id);
CREATE INDEX idx_telemetry_created_at ON telemetry_logs(created_at);

-- ------------------------------------------------------------------------------
-- 6. ONBOARDING PROFILES TABLE
-- Stores student goals, domain interests, diagnostic scores, and learner profiles.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS onboarding_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    goals JSONB NOT NULL DEFAULT '[]'::jsonb,
    interests JSONB NOT NULL DEFAULT '[]'::jsonb,
    selected_subjects JSONB NOT NULL DEFAULT '[]'::jsonb,
    assessment_score FLOAT NOT NULL DEFAULT 0.0,
    strengths JSONB NOT NULL DEFAULT '[]'::jsonb,
    weak_areas JSONB NOT NULL DEFAULT '[]'::jsonb,
    recommended_weekly_hours INT NOT NULL DEFAULT 10,
    suggested_starting_topic VARCHAR(255) NOT NULL DEFAULT 'Foundations of Computer Science',
    is_completed BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_onboarding_user_id ON onboarding_profiles(user_id);

-- ------------------------------------------------------------------------------
-- 7. CONTENT CATEGORIES TABLE (ACADEMIC CONTENT ENGINE)
-- High-level disciplinary grouping (e.g., Computer Science, Programming, AI, Mathematics).
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS content_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    display_order INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_categories_slug ON content_categories(slug);
CREATE INDEX idx_categories_order ON content_categories(display_order);

-- ------------------------------------------------------------------------------
-- 8. SUBJECTS TABLE
-- Canonical academic subjects mapped to categories.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS subjects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID NOT NULL REFERENCES content_categories(id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,
    slug VARCHAR(150) UNIQUE NOT NULL,
    short_description VARCHAR(255),
    description TEXT,
    icon_key VARCHAR(50),
    difficulty_level VARCHAR(50) NOT NULL DEFAULT 'All Levels',
    display_order INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_subjects_category_id ON subjects(category_id);
CREATE INDEX idx_subjects_slug ON subjects(slug);
CREATE INDEX idx_subjects_order ON subjects(display_order);

-- ------------------------------------------------------------------------------
-- 9. COURSES TABLE
-- Structured courses within an academic subject.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) NOT NULL,
    description TEXT,
    difficulty VARCHAR(50) NOT NULL DEFAULT 'Beginner',
    estimated_hours INT NOT NULL DEFAULT 10,
    display_order INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_course_subject_slug UNIQUE(subject_id, slug)
);

CREATE INDEX idx_courses_subject_id ON courses(subject_id);
CREATE INDEX idx_courses_slug ON courses(slug);

-- ------------------------------------------------------------------------------
-- 10. MODULES TABLE
-- Curricular modules/chapters belonging to a course.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) NOT NULL,
    description TEXT,
    display_order INT NOT NULL DEFAULT 0,
    estimated_minutes INT NOT NULL DEFAULT 60,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_module_course_slug UNIQUE(course_id, slug)
);

CREATE INDEX idx_modules_course_id ON modules(course_id);
CREATE INDEX idx_modules_slug ON modules(slug);

-- ------------------------------------------------------------------------------
-- 11. TOPICS TABLE
-- Micro-topics within a course module.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_id UUID NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) NOT NULL,
    summary TEXT,
    display_order INT NOT NULL DEFAULT 0,
    estimated_minutes INT NOT NULL DEFAULT 30,
    difficulty VARCHAR(50) NOT NULL DEFAULT 'Beginner',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_topic_module_slug UNIQUE(module_id, slug)
);

CREATE INDEX idx_topics_module_id ON topics(module_id);
CREATE INDEX idx_topics_slug ON topics(slug);

-- ------------------------------------------------------------------------------
-- 12. LESSONS TABLE
-- Concrete learning units with structured educational markdown content.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lessons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) NOT NULL,
    summary TEXT,
    content TEXT NOT NULL,
    learning_objectives JSONB NOT NULL DEFAULT '[]'::jsonb,
    estimated_minutes INT NOT NULL DEFAULT 15,
    display_order INT NOT NULL DEFAULT 0,
    lesson_type VARCHAR(50) NOT NULL DEFAULT 'theory',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_lesson_topic_slug UNIQUE(topic_id, slug)
);

CREATE INDEX idx_lessons_topic_id ON lessons(topic_id);
CREATE INDEX idx_lessons_slug ON lessons(slug);

-- ------------------------------------------------------------------------------
-- 13. QUIZ SESSIONS TABLE (SPRINT 1 ADAPTIVE QUIZZING)
-- Tracks active adaptive test sessions, student topic, and final mastery scores.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS quiz_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    topic_title VARCHAR(255) NOT NULL,
    topic_id UUID REFERENCES topics(id) ON DELETE SET NULL,
    difficulty_level VARCHAR(50) NOT NULL DEFAULT 'intermediate',
    total_questions INT NOT NULL DEFAULT 5,
    score FLOAT NOT NULL DEFAULT 0.0,
    status VARCHAR(50) NOT NULL DEFAULT 'in_progress',
    initial_mastery FLOAT NOT NULL DEFAULT 0.10,
    final_mastery FLOAT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_quiz_sessions_user_id ON quiz_sessions(user_id);
CREATE INDEX idx_quiz_sessions_topic_id ON quiz_sessions(topic_id);

-- ------------------------------------------------------------------------------
-- 14. QUIZ QUESTIONS TABLE
-- Stores generated assessment items with Bloom's level and IRT 2PL difficulty parameters.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS quiz_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES quiz_sessions(id) ON DELETE CASCADE,
    question_index INT NOT NULL DEFAULT 0,
    prompt TEXT NOT NULL,
    options JSONB NOT NULL DEFAULT '[]'::jsonb,
    correct_answer VARCHAR(500) NOT NULL,
    explanation TEXT NOT NULL,
    blooms_level VARCHAR(50) NOT NULL DEFAULT 'understanding',
    irt_difficulty FLOAT NOT NULL DEFAULT 0.0,
    irt_discrimination FLOAT NOT NULL DEFAULT 1.0,
    misconception_map JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_quiz_questions_session_id ON quiz_questions(session_id);

-- ------------------------------------------------------------------------------
-- 15. QUIZ ATTEMPTS TABLE
-- Idempotent student submissions with posterior BKT mastery updates.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES quiz_sessions(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES quiz_questions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    selected_answer VARCHAR(500) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    latency_ms INT NOT NULL DEFAULT 0,
    bkt_prior_mastery FLOAT NOT NULL DEFAULT 0.10,
    bkt_posterior_mastery FLOAT NOT NULL DEFAULT 0.10,
    detected_misconception TEXT,
    feedback TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_session_question_user_attempt UNIQUE(session_id, question_id, user_id)
);

CREATE INDEX idx_quiz_attempts_session_id ON quiz_attempts(session_id);
CREATE INDEX idx_quiz_attempts_question_id ON quiz_attempts(question_id);
CREATE INDEX idx_quiz_attempts_user_id ON quiz_attempts(user_id);

