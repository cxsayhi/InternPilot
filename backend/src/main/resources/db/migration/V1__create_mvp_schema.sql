CREATE DATABASE IF NOT EXISTS internpilot
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE internpilot;

SET NAMES utf8mb4;
SET time_zone = '+00:00';

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(64) PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    display_name VARCHAR(120),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS resumes (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    title VARCHAR(160) NOT NULL,
    raw_text MEDIUMTEXT NOT NULL,
    source_type VARCHAR(32) NOT NULL DEFAULT 'PASTED_TEXT',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_resumes_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE,
    CONSTRAINT ck_resumes_source_type
        CHECK (source_type IN ('PASTED_TEXT', 'UPLOAD')),
    KEY idx_resumes_user_id (user_id),
    KEY idx_resumes_user_active (user_id, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS projects (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    resume_id VARCHAR(64),
    name VARCHAR(160) NOT NULL,
    description TEXT,
    tech_stack JSON,
    evidence_text MEDIUMTEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_projects_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_projects_resume
        FOREIGN KEY (resume_id) REFERENCES resumes (id)
        ON DELETE SET NULL,
    KEY idx_projects_user_id (user_id),
    KEY idx_projects_resume_id (resume_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS applications (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    resume_id VARCHAR(64),
    company VARCHAR(160),
    role VARCHAR(160),
    job_text MEDIUMTEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'DRAFT',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_applications_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_applications_resume
        FOREIGN KEY (resume_id) REFERENCES resumes (id)
        ON DELETE SET NULL,
    CONSTRAINT ck_applications_status
        CHECK (status IN ('DRAFT', 'ANALYZING', 'ANALYZED', 'FAILED', 'APPLIED', 'REJECTED')),
    KEY idx_applications_user_id (user_id),
    KEY idx_applications_user_status (user_id, status),
    KEY idx_applications_resume_id (resume_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS application_analysis (
    id VARCHAR(64) PRIMARY KEY,
    application_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    agent_run_id VARCHAR(96),
    match_score INT NOT NULL,
    score_breakdown JSON NOT NULL,
    strong_matches JSON NOT NULL,
    weak_matches JSON NOT NULL,
    missing_skills JSON NOT NULL,
    learning_plan JSON NOT NULL,
    warnings JSON,
    model_metadata JSON,
    graph_version VARCHAR(80),
    prompt_versions JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_application_analysis_application
        FOREIGN KEY (application_id) REFERENCES applications (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_application_analysis_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE,
    CONSTRAINT ck_application_analysis_match_score
        CHECK (match_score BETWEEN 0 AND 100),
    UNIQUE KEY uk_application_analysis_application (application_id),
    KEY idx_application_analysis_user_id (user_id),
    KEY idx_application_analysis_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS resume_rewrite_suggestions (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    application_id VARCHAR(64) NOT NULL,
    analysis_id VARCHAR(64) NOT NULL,
    resume_id VARCHAR(64),
    original_bullet TEXT NOT NULL,
    suggested_bullet TEXT NOT NULL,
    targeted_skills JSON NOT NULL,
    evidence_sources JSON NOT NULL,
    unsupported_claims JSON NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    needs_user_confirmation BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING_REVIEW',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_rewrite_suggestions_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_rewrite_suggestions_application
        FOREIGN KEY (application_id) REFERENCES applications (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_rewrite_suggestions_analysis
        FOREIGN KEY (analysis_id) REFERENCES application_analysis (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_rewrite_suggestions_resume
        FOREIGN KEY (resume_id) REFERENCES resumes (id)
        ON DELETE SET NULL,
    CONSTRAINT ck_rewrite_suggestions_confidence
        CHECK (confidence BETWEEN 0 AND 1),
    CONSTRAINT ck_rewrite_suggestions_status
        CHECK (status IN ('PENDING_REVIEW', 'ACCEPTED', 'REJECTED')),
    KEY idx_rewrite_suggestions_user_id (user_id),
    KEY idx_rewrite_suggestions_application_id (application_id),
    KEY idx_rewrite_suggestions_analysis_id (analysis_id),
    KEY idx_rewrite_suggestions_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
