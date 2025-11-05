-- ============================================================================
-- CONTEXT PRESERVATION & PROCESSING CACHE SCHEMA
-- ============================================================================
-- Purpose: Save all dashboard processing results, AI analysis, and system state
--          to Supabase for efficient querying and context preservation
-- Created: 2025-11-05
-- ============================================================================

-- ============================================================================
-- 1. SYSTEM PROCESSING CACHE
-- ============================================================================
-- Store expensive AI processing results to avoid recomputation

CREATE TABLE IF NOT EXISTS system_processing_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cache_key VARCHAR(500) UNIQUE NOT NULL,  -- Unique identifier for cached item
    cache_type VARCHAR(100) NOT NULL,         -- 'document_analysis', 'timeline_build', 'truth_score', etc.
    input_hash VARCHAR(64) NOT NULL,          -- SHA256 hash of input parameters
    result_data JSONB NOT NULL,               -- The cached result data
    metadata JSONB,                           -- Additional metadata about the cache
    expires_at TIMESTAMPTZ,                   -- Optional expiration time
    hit_count INTEGER DEFAULT 0,              -- How many times this cache was used
    last_hit_at TIMESTAMPTZ,                  -- Last time cache was accessed
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast lookup
CREATE INDEX IF NOT EXISTS idx_cache_key ON system_processing_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_cache_type ON system_processing_cache(cache_type);
CREATE INDEX IF NOT EXISTS idx_cache_expires ON system_processing_cache(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_cache_created ON system_processing_cache(created_at DESC);

-- ============================================================================
-- 2. DASHBOARD SNAPSHOTS
-- ============================================================================
-- Store complete dashboard states for quick restore

CREATE TABLE IF NOT EXISTS dashboard_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dashboard_name VARCHAR(200) NOT NULL,     -- 'truth_justice_timeline', 'proj344_master', etc.
    snapshot_name VARCHAR(200),               -- User-friendly name for snapshot
    snapshot_data JSONB NOT NULL,             -- Complete dashboard state
    filters_applied JSONB,                    -- Filters that were active
    metrics JSONB,                            -- Summary metrics at snapshot time
    data_sources JSONB,                       -- Which tables/data were used
    row_count INTEGER,                        -- Number of records in snapshot
    snapshot_date TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(200),                  -- User or system that created snapshot
    is_auto_snapshot BOOLEAN DEFAULT FALSE,   -- Auto-generated vs manual
    notes TEXT,                               -- User notes about this snapshot
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_dashboard_name ON dashboard_snapshots(dashboard_name);
CREATE INDEX IF NOT EXISTS idx_snapshot_date ON dashboard_snapshots(snapshot_date DESC);
CREATE INDEX IF NOT EXISTS idx_auto_snapshot ON dashboard_snapshots(is_auto_snapshot);

-- ============================================================================
-- 3. AI ANALYSIS RESULTS
-- ============================================================================
-- Store all AI model outputs (Claude, etc.) for reference

CREATE TABLE IF NOT EXISTS ai_analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_type VARCHAR(100) NOT NULL,      -- 'document_scan', 'truth_scoring', 'violation_detection', etc.
    source_id UUID,                           -- Reference to source document/event
    source_table VARCHAR(100),                -- Which table the source came from
    model_name VARCHAR(100),                  -- 'claude-sonnet-4.5', etc.
    prompt_text TEXT,                         -- The prompt sent to AI
    response_text TEXT,                       -- The AI response
    structured_output JSONB,                  -- Parsed/structured response
    confidence_score DECIMAL(5,2),            -- 0-100 confidence in result
    tokens_used INTEGER,                      -- Token count for cost tracking
    processing_time_ms INTEGER,               -- Processing time in milliseconds
    api_cost_usd DECIMAL(10,4),              -- Cost of this API call
    metadata JSONB,                           -- Additional context
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_analysis_type ON ai_analysis_results(analysis_type);
CREATE INDEX IF NOT EXISTS idx_source_ref ON ai_analysis_results(source_table, source_id);
CREATE INDEX IF NOT EXISTS idx_analysis_created ON ai_analysis_results(created_at DESC);

-- ============================================================================
-- 4. QUERY RESULTS CACHE
-- ============================================================================
-- Cache expensive Supabase query results

CREATE TABLE IF NOT EXISTS query_results_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_hash VARCHAR(64) UNIQUE NOT NULL,   -- SHA256 of query + parameters
    query_sql TEXT NOT NULL,                  -- The SQL query (for reference)
    query_params JSONB,                       -- Parameters used in query
    result_data JSONB NOT NULL,               -- Query result as JSON
    result_count INTEGER,                     -- Number of rows returned
    execution_time_ms INTEGER,                -- Query execution time
    tables_accessed TEXT[],                   -- Which tables were queried
    expires_at TIMESTAMPTZ,                   -- Cache expiration
    hit_count INTEGER DEFAULT 0,
    last_hit_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_query_hash ON query_results_cache(query_hash);
CREATE INDEX IF NOT EXISTS idx_query_expires ON query_results_cache(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_query_tables ON query_results_cache USING GIN(tables_accessed);

-- ============================================================================
-- 5. TRUTH SCORE HISTORY
-- ============================================================================
-- Track all truth score calculations over time

CREATE TABLE IF NOT EXISTS truth_score_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id UUID NOT NULL,                    -- ID of the item being scored
    item_type VARCHAR(100) NOT NULL,          -- 'STATEMENT', 'EVENT', 'ACTION', 'MOTION', 'FILING'
    item_title TEXT NOT NULL,
    truth_score DECIMAL(5,2) NOT NULL,        -- 0-100 truth score
    calculation_method VARCHAR(200),          -- How score was calculated
    evidence_count INTEGER,                   -- Number of evidence items used
    supporting_evidence JSONB,                -- Evidence supporting the score
    contradicting_evidence JSONB,             -- Evidence contradicting
    when_happened TIMESTAMPTZ,                -- When did this event occur
    where_happened TEXT,                      -- Where did it happen
    who_involved TEXT[],                      -- Who was involved
    what_occurred TEXT,                       -- What happened
    why_occurred TEXT,                        -- Why it happened
    how_occurred TEXT,                        -- How it happened
    importance_level VARCHAR(20),             -- CRITICAL, HIGH, MEDIUM, LOW
    category VARCHAR(100),                    -- DOCUMENT, EVENT, STATEMENT, etc.
    metadata JSONB,
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_truth_item_id ON truth_score_history(item_id);
CREATE INDEX IF NOT EXISTS idx_truth_item_type ON truth_score_history(item_type);
CREATE INDEX IF NOT EXISTS idx_truth_score ON truth_score_history(truth_score);
CREATE INDEX IF NOT EXISTS idx_truth_when ON truth_score_history(when_happened);
CREATE INDEX IF NOT EXISTS idx_truth_importance ON truth_score_history(importance_level);

-- ============================================================================
-- 6. JUSTICE SCORE ROLLUPS
-- ============================================================================
-- Store calculated justice scores and their breakdowns

CREATE TABLE IF NOT EXISTS justice_score_rollups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rollup_name VARCHAR(200) NOT NULL,        -- 'Full Case', 'August 2024 Incident', etc.
    rollup_date TIMESTAMPTZ NOT NULL,
    justice_score DECIMAL(5,2) NOT NULL,      -- Overall justice score 0-100
    total_items INTEGER NOT NULL,             -- Number of items in rollup
    critical_items INTEGER,                   -- Number of critical items
    high_items INTEGER,
    medium_items INTEGER,
    low_items INTEGER,
    avg_truth_score DECIMAL(5,2),            -- Average truth score
    truthful_items INTEGER,                   -- Score >= 75
    neutral_items INTEGER,                    -- Score 25-75
    false_items INTEGER,                      -- Score < 25
    score_breakdown JSONB,                    -- Detailed breakdown by category
    items_included UUID[],                    -- IDs of items in rollup
    date_range_start DATE,
    date_range_end DATE,
    filters_applied JSONB,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_justice_rollup_name ON justice_score_rollups(rollup_name);
CREATE INDEX IF NOT EXISTS idx_justice_rollup_date ON justice_score_rollups(rollup_date DESC);
CREATE INDEX IF NOT EXISTS idx_justice_score ON justice_score_rollups(justice_score);

-- ============================================================================
-- 7. PROCESSING JOBS LOG
-- ============================================================================
-- Track all long-running processing jobs

CREATE TABLE IF NOT EXISTS processing_jobs_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type VARCHAR(100) NOT NULL,           -- 'document_scan', 'timeline_build', etc.
    job_name VARCHAR(200),
    status VARCHAR(50) NOT NULL,              -- 'pending', 'running', 'completed', 'failed'
    progress_percentage INTEGER DEFAULT 0,
    items_total INTEGER,
    items_processed INTEGER DEFAULT 0,
    items_failed INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    error_details JSONB,
    result_summary JSONB,                     -- Summary of job results
    api_calls_made INTEGER DEFAULT 0,
    total_cost_usd DECIMAL(10,4) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_job_type ON processing_jobs_log(job_type);
CREATE INDEX IF NOT EXISTS idx_job_status ON processing_jobs_log(status);
CREATE INDEX IF NOT EXISTS idx_job_started ON processing_jobs_log(started_at DESC);

-- ============================================================================
-- 8. CONTEXT PRESERVATION METADATA
-- ============================================================================
-- Store conversation context and system state for AI continuity

CREATE TABLE IF NOT EXISTS context_preservation_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    context_type VARCHAR(100) NOT NULL,       -- 'conversation', 'dashboard_state', 'analysis_session'
    context_name VARCHAR(200),
    context_data JSONB NOT NULL,              -- The actual context data
    parent_context_id UUID,                   -- Reference to parent context
    tokens_estimated INTEGER,                 -- Estimated token count
    expires_at TIMESTAMPTZ,
    is_archived BOOLEAN DEFAULT FALSE,
    tags TEXT[],                              -- Tags for organization
    created_by VARCHAR(200),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_context_type ON context_preservation_metadata(context_type);
CREATE INDEX IF NOT EXISTS idx_context_name ON context_preservation_metadata(context_name);
CREATE INDEX IF NOT EXISTS idx_context_parent ON context_preservation_metadata(parent_context_id);
CREATE INDEX IF NOT EXISTS idx_context_tags ON context_preservation_metadata USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_context_archived ON context_preservation_metadata(is_archived);

-- ============================================================================
-- VIEWS FOR QUICK ACCESS
-- ============================================================================

-- Active cache entries (not expired)
CREATE OR REPLACE VIEW active_cache_entries AS
SELECT
    cache_key,
    cache_type,
    result_data,
    hit_count,
    last_hit_at,
    created_at,
    expires_at
FROM system_processing_cache
WHERE expires_at IS NULL OR expires_at > NOW()
ORDER BY hit_count DESC, created_at DESC;

-- Recent dashboard snapshots
CREATE OR REPLACE VIEW recent_dashboard_snapshots AS
SELECT
    dashboard_name,
    snapshot_name,
    snapshot_date,
    row_count,
    metrics,
    is_auto_snapshot,
    created_at
FROM dashboard_snapshots
ORDER BY snapshot_date DESC
LIMIT 100;

-- Truth score summary by category
CREATE OR REPLACE VIEW truth_score_summary AS
SELECT
    category,
    item_type,
    COUNT(*) as total_items,
    ROUND(AVG(truth_score), 2) as avg_truth_score,
    COUNT(*) FILTER (WHERE truth_score >= 75) as truthful_count,
    COUNT(*) FILTER (WHERE truth_score < 25) as false_count,
    COUNT(*) FILTER (WHERE importance_level = 'CRITICAL') as critical_count
FROM truth_score_history
GROUP BY category, item_type
ORDER BY avg_truth_score DESC;

-- Processing cost summary
CREATE OR REPLACE VIEW processing_cost_summary AS
SELECT
    DATE(created_at) as processing_date,
    analysis_type,
    COUNT(*) as analysis_count,
    SUM(tokens_used) as total_tokens,
    SUM(api_cost_usd) as total_cost_usd,
    AVG(processing_time_ms) as avg_processing_time_ms
FROM ai_analysis_results
GROUP BY DATE(created_at), analysis_type
ORDER BY processing_date DESC, total_cost_usd DESC;

-- Active processing jobs
CREATE OR REPLACE VIEW active_processing_jobs AS
SELECT
    job_type,
    job_name,
    status,
    progress_percentage,
    items_processed,
    items_total,
    started_at,
    EXTRACT(EPOCH FROM (NOW() - started_at)) / 60 as runtime_minutes
FROM processing_jobs_log
WHERE status IN ('pending', 'running')
ORDER BY started_at DESC;

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to clean expired cache entries
CREATE OR REPLACE FUNCTION clean_expired_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM system_processing_cache
    WHERE expires_at IS NOT NULL AND expires_at < NOW();

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to increment cache hit count
CREATE OR REPLACE FUNCTION increment_cache_hit(p_cache_key VARCHAR)
RETURNS VOID AS $$
BEGIN
    UPDATE system_processing_cache
    SET
        hit_count = hit_count + 1,
        last_hit_at = NOW()
    WHERE cache_key = p_cache_key;
END;
$$ LANGUAGE plpgsql;

-- Function to auto-archive old contexts
CREATE OR REPLACE FUNCTION archive_old_contexts(p_days_old INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    UPDATE context_preservation_metadata
    SET is_archived = TRUE
    WHERE
        is_archived = FALSE
        AND created_at < NOW() - (p_days_old || ' days')::INTERVAL
        AND context_type NOT IN ('permanent', 'reference');

    GET DIAGNOSTICS archived_count = ROW_COUNT;
    RETURN archived_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE system_processing_cache IS 'Cache for expensive AI processing results to avoid recomputation';
COMMENT ON TABLE dashboard_snapshots IS 'Complete dashboard states for quick restore and historical reference';
COMMENT ON TABLE ai_analysis_results IS 'All AI model outputs with prompts, responses, and cost tracking';
COMMENT ON TABLE query_results_cache IS 'Cache for expensive Supabase queries';
COMMENT ON TABLE truth_score_history IS 'Complete history of truth scores with 5W+H context';
COMMENT ON TABLE justice_score_rollups IS 'Aggregated justice scores with breakdowns';
COMMENT ON TABLE processing_jobs_log IS 'Log of all long-running processing jobs';
COMMENT ON TABLE context_preservation_metadata IS 'Context data for AI conversation continuity';

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
