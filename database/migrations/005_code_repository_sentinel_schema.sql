-- ============================================================================
-- Code Repository Sentinel - Database Schema
-- ============================================================================
-- Purpose: Track and analyze all code repositories across the organization
-- Created: 2025-11-18
-- Version: 1.0
-- ============================================================================

-- ============================================================================
-- TABLE: repositories
-- ============================================================================
-- Stores metadata about each code repository
CREATE TABLE IF NOT EXISTS repositories (
    -- Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id VARCHAR(255) UNIQUE NOT NULL, -- Unique identifier (e.g., github-owner-repo)
    repository_name VARCHAR(255) NOT NULL,
    repository_url TEXT, -- GitHub, GitLab, Bitbucket URL

    -- Location
    local_path TEXT, -- Local file system path if cloned
    remote_origin TEXT, -- Git remote origin URL

    -- Classification
    repository_type VARCHAR(50), -- github, gitlab, bitbucket, local
    primary_language VARCHAR(50), -- Python, JavaScript, TypeScript, etc.
    framework VARCHAR(100), -- Django, React, Next.js, Streamlit, etc.
    project_category VARCHAR(100), -- web-app, cli-tool, library, dashboard, etc.

    -- Metadata
    description TEXT, -- What the repository is for
    purpose TEXT, -- Detailed purpose and use case
    current_status VARCHAR(50) DEFAULT 'active', -- active, archived, deprecated, experimental, production

    -- Versioning
    version_number VARCHAR(50), -- Semantic version (e.g., 1.2.3)
    version_tag VARCHAR(100), -- Git tag (e.g., v1.2.3)
    latest_commit_hash VARCHAR(255),
    latest_commit_date TIMESTAMP,
    latest_commit_message TEXT,

    -- Statistics
    total_files INTEGER DEFAULT 0,
    total_lines_of_code INTEGER DEFAULT 0,
    total_commits INTEGER DEFAULT 0,
    total_contributors INTEGER DEFAULT 0,

    -- Language breakdown (JSON)
    language_breakdown JSONB, -- {"Python": 5000, "JavaScript": 2000, "CSS": 500}

    -- Dependencies
    dependencies JSONB, -- {"react": "^18.0.0", "streamlit": "1.31.0"}
    dev_dependencies JSONB,

    -- Dates
    created_date TIMESTAMP, -- When repository was first created
    first_commit_date TIMESTAMP, -- Date of first commit
    last_modified_date TIMESTAMP, -- Last modification date
    last_scanned_at TIMESTAMP DEFAULT NOW(), -- When sentinel last scanned this repo

    -- Health & Quality
    has_readme BOOLEAN DEFAULT false,
    has_tests BOOLEAN DEFAULT false,
    has_ci_cd BOOLEAN DEFAULT false,
    has_documentation BOOLEAN DEFAULT false,
    test_coverage_percentage DECIMAL(5,2),
    code_quality_score INTEGER, -- 0-100 score

    -- Security
    has_vulnerabilities BOOLEAN DEFAULT false,
    vulnerability_count INTEGER DEFAULT 0,
    last_security_scan_date TIMESTAMP,

    -- Git Info
    default_branch VARCHAR(100) DEFAULT 'main',
    total_branches INTEGER DEFAULT 0,
    open_pull_requests INTEGER DEFAULT 0,

    -- Ownership
    owner_name VARCHAR(255),
    maintainers TEXT[], -- Array of maintainer names
    organization VARCHAR(255),

    -- Notes
    notes TEXT,
    tags TEXT[], -- Array of tags for categorization

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- TABLE: repository_files
-- ============================================================================
-- Stores information about important files in each repository
CREATE TABLE IF NOT EXISTS repository_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id VARCHAR(255) REFERENCES repositories(repository_id) ON DELETE CASCADE,

    file_path TEXT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50), -- python, javascript, markdown, config, etc.
    file_size_bytes BIGINT,
    lines_of_code INTEGER,

    -- Classification
    is_source_code BOOLEAN DEFAULT false,
    is_test_file BOOLEAN DEFAULT false,
    is_config_file BOOLEAN DEFAULT false,
    is_documentation BOOLEAN DEFAULT false,

    -- Content analysis
    complexity_score INTEGER, -- McCabe complexity or similar
    has_todos BOOLEAN DEFAULT false,
    has_fixmes BOOLEAN DEFAULT false,

    -- Dates
    created_date TIMESTAMP,
    last_modified_date TIMESTAMP,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(repository_id, file_path)
);

-- ============================================================================
-- TABLE: repository_scan_history
-- ============================================================================
-- Tracks all scans performed by the sentinel
CREATE TABLE IF NOT EXISTS repository_scan_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id VARCHAR(255) REFERENCES repositories(repository_id) ON DELETE CASCADE,

    scan_date TIMESTAMP DEFAULT NOW(),
    scan_duration_seconds DECIMAL(10,2),
    scan_type VARCHAR(50), -- full, incremental, quick

    -- Results
    files_scanned INTEGER,
    changes_detected BOOLEAN DEFAULT false,
    changes_summary JSONB, -- {"files_added": 5, "files_modified": 10, "files_deleted": 2}

    -- Errors
    scan_successful BOOLEAN DEFAULT true,
    errors TEXT,

    -- Version at scan time
    version_at_scan VARCHAR(50),
    commit_hash_at_scan VARCHAR(255),

    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- TABLE: repository_dependencies
-- ============================================================================
-- Tracks dependencies across all repositories
CREATE TABLE IF NOT EXISTS repository_dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id VARCHAR(255) REFERENCES repositories(repository_id) ON DELETE CASCADE,

    dependency_name VARCHAR(255) NOT NULL,
    dependency_version VARCHAR(100),
    dependency_type VARCHAR(50), -- runtime, dev, peer

    -- Package manager
    package_manager VARCHAR(50), -- npm, pip, cargo, composer, etc.

    -- Security
    has_known_vulnerabilities BOOLEAN DEFAULT false,
    vulnerability_severity VARCHAR(50), -- low, medium, high, critical

    -- Usage
    is_direct_dependency BOOLEAN DEFAULT true,
    is_transitive BOOLEAN DEFAULT false,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(repository_id, dependency_name, dependency_version)
);

-- ============================================================================
-- TABLE: repository_tags
-- ============================================================================
-- Flexible tagging system for repositories
CREATE TABLE IF NOT EXISTS repository_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id VARCHAR(255) REFERENCES repositories(repository_id) ON DELETE CASCADE,

    tag_name VARCHAR(100) NOT NULL,
    tag_category VARCHAR(100), -- tech-stack, use-case, status, priority
    tag_value TEXT,

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(repository_id, tag_name)
);

-- ============================================================================
-- TABLE: code_analysis_metrics
-- ============================================================================
-- Stores code quality and analysis metrics
CREATE TABLE IF NOT EXISTS code_analysis_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id VARCHAR(255) REFERENCES repositories(repository_id) ON DELETE CASCADE,

    analysis_date TIMESTAMP DEFAULT NOW(),

    -- Code Quality Metrics
    cyclomatic_complexity_avg DECIMAL(10,2),
    maintainability_index DECIMAL(10,2),
    technical_debt_ratio DECIMAL(10,2),

    -- Size Metrics
    total_functions INTEGER,
    total_classes INTEGER,
    total_modules INTEGER,

    -- Documentation
    documented_functions_percentage DECIMAL(5,2),
    comment_density DECIMAL(5,2),

    -- Testing
    total_test_files INTEGER,
    total_test_cases INTEGER,
    test_coverage DECIMAL(5,2),

    -- Duplication
    duplicate_code_percentage DECIMAL(5,2),

    -- Issues
    total_code_smells INTEGER,
    total_bugs INTEGER,
    total_security_hotspots INTEGER,

    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- INDEXES for Performance
-- ============================================================================

-- repositories table
CREATE INDEX IF NOT EXISTS idx_repositories_status ON repositories(current_status);
CREATE INDEX IF NOT EXISTS idx_repositories_language ON repositories(primary_language);
CREATE INDEX IF NOT EXISTS idx_repositories_category ON repositories(project_category);
CREATE INDEX IF NOT EXISTS idx_repositories_last_modified ON repositories(last_modified_date DESC);
CREATE INDEX IF NOT EXISTS idx_repositories_created ON repositories(created_date DESC);
CREATE INDEX IF NOT EXISTS idx_repositories_tags ON repositories USING GIN(tags);

-- repository_files table
CREATE INDEX IF NOT EXISTS idx_files_repository_id ON repository_files(repository_id);
CREATE INDEX IF NOT EXISTS idx_files_type ON repository_files(file_type);
CREATE INDEX IF NOT EXISTS idx_files_is_source ON repository_files(is_source_code);

-- repository_scan_history table
CREATE INDEX IF NOT EXISTS idx_scan_history_repo_id ON repository_scan_history(repository_id);
CREATE INDEX IF NOT EXISTS idx_scan_history_date ON repository_scan_history(scan_date DESC);

-- repository_dependencies table
CREATE INDEX IF NOT EXISTS idx_dependencies_repo_id ON repository_dependencies(repository_id);
CREATE INDEX IF NOT EXISTS idx_dependencies_name ON repository_dependencies(dependency_name);
CREATE INDEX IF NOT EXISTS idx_dependencies_vulnerabilities ON repository_dependencies(has_known_vulnerabilities);

-- repository_tags table
CREATE INDEX IF NOT EXISTS idx_tags_repo_id ON repository_tags(repository_id);
CREATE INDEX IF NOT EXISTS idx_tags_name ON repository_tags(tag_name);
CREATE INDEX IF NOT EXISTS idx_tags_category ON repository_tags(tag_category);

-- code_analysis_metrics table
CREATE INDEX IF NOT EXISTS idx_metrics_repo_id ON code_analysis_metrics(repository_id);
CREATE INDEX IF NOT EXISTS idx_metrics_date ON code_analysis_metrics(analysis_date DESC);

-- ============================================================================
-- VIEWS for Common Queries
-- ============================================================================

-- Active repositories summary
CREATE OR REPLACE VIEW v_active_repositories AS
SELECT
    repository_id,
    repository_name,
    primary_language,
    framework,
    current_status,
    version_number,
    total_lines_of_code,
    last_modified_date,
    code_quality_score
FROM repositories
WHERE current_status = 'active'
ORDER BY last_modified_date DESC;

-- Repository health dashboard
CREATE OR REPLACE VIEW v_repository_health AS
SELECT
    r.repository_id,
    r.repository_name,
    r.current_status,
    r.has_readme,
    r.has_tests,
    r.has_ci_cd,
    r.has_documentation,
    r.test_coverage_percentage,
    r.code_quality_score,
    r.has_vulnerabilities,
    r.vulnerability_count,
    CASE
        WHEN r.has_readme AND r.has_tests AND r.has_ci_cd AND r.has_documentation
            AND r.test_coverage_percentage >= 80 AND r.code_quality_score >= 80
            AND NOT r.has_vulnerabilities
        THEN 'excellent'
        WHEN r.has_readme AND r.has_tests AND r.code_quality_score >= 60
        THEN 'good'
        WHEN r.has_readme OR r.has_tests
        THEN 'fair'
        ELSE 'poor'
    END as health_status
FROM repositories r
ORDER BY r.code_quality_score DESC NULLS LAST;

-- Dependencies across repositories
CREATE OR REPLACE VIEW v_dependency_usage AS
SELECT
    d.dependency_name,
    d.dependency_version,
    COUNT(DISTINCT d.repository_id) as used_in_count,
    ARRAY_AGG(DISTINCT r.repository_name) as used_in_repos,
    MAX(d.has_known_vulnerabilities) as has_vulnerabilities
FROM repository_dependencies d
JOIN repositories r ON d.repository_id = r.repository_id
GROUP BY d.dependency_name, d.dependency_version
ORDER BY used_in_count DESC;

-- Recent activity summary
CREATE OR REPLACE VIEW v_recent_activity AS
SELECT
    r.repository_id,
    r.repository_name,
    r.latest_commit_date,
    r.latest_commit_message,
    r.last_scanned_at,
    DATE_PART('day', NOW() - r.latest_commit_date) as days_since_last_commit,
    DATE_PART('day', NOW() - r.last_scanned_at) as days_since_last_scan
FROM repositories r
WHERE r.current_status = 'active'
ORDER BY r.latest_commit_date DESC;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
DROP TRIGGER IF EXISTS update_repositories_updated_at ON repositories;
CREATE TRIGGER update_repositories_updated_at
    BEFORE UPDATE ON repositories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_repository_files_updated_at ON repository_files;
CREATE TRIGGER update_repository_files_updated_at
    BEFORE UPDATE ON repository_files
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_repository_dependencies_updated_at ON repository_dependencies;
CREATE TRIGGER update_repository_dependencies_updated_at
    BEFORE UPDATE ON repository_dependencies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW LEVEL SECURITY (Optional - enable if needed)
-- ============================================================================

-- Enable RLS on all tables (commented out by default)
-- ALTER TABLE repositories ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE repository_files ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE repository_scan_history ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE repository_dependencies ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE repository_tags ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE code_analysis_metrics ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================================================

-- Insert ASEAGI repository as example
INSERT INTO repositories (
    repository_id,
    repository_name,
    repository_url,
    repository_type,
    primary_language,
    framework,
    project_category,
    description,
    purpose,
    current_status,
    version_number,
    default_branch,
    owner_name,
    organization,
    has_readme,
    has_documentation,
    tags
) VALUES (
    'github-dondada876-ASEAGI',
    'ASEAGI',
    'https://github.com/dondada876/ASEAGI',
    'github',
    'Python',
    'Streamlit',
    'legal-intelligence-dashboard',
    'AI-powered legal document intelligence system for child protection cases',
    'Assist protective parents and legal teams in analyzing legal documents with AI-powered scoring to identify smoking gun evidence, detect perjury, and track constitutional violations',
    'production',
    '1.0.0',
    'main',
    'Don Bucknor',
    'Ashe Sanctuary of Empowerment Foundation',
    true,
    true,
    ARRAY['legal-tech', 'ai-analysis', 'streamlit', 'child-protection']
) ON CONFLICT (repository_id) DO NOTHING;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE repositories IS 'Stores metadata about all code repositories in the organization';
COMMENT ON TABLE repository_files IS 'Tracks important files within each repository';
COMMENT ON TABLE repository_scan_history IS 'Audit log of all repository scans performed by the sentinel';
COMMENT ON TABLE repository_dependencies IS 'Tracks all dependencies used across repositories';
COMMENT ON TABLE repository_tags IS 'Flexible tagging system for categorizing repositories';
COMMENT ON TABLE code_analysis_metrics IS 'Code quality and analysis metrics for each repository';

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
