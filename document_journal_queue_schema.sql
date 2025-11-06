-- ============================================================================
-- UNIVERSAL DOCUMENT JOURNAL & QUEUE MANAGEMENT SYSTEM
-- The "Source of Truth" for all documents in the system
-- ============================================================================

-- ============================================================================
-- TABLE 1: DOCUMENT_JOURNAL (Universal Truth Table)
-- ============================================================================
-- This is the master reference table for EVERY document that enters the system
-- Used for: deduplication, cross-reference, audit trail, compliance, optimization

CREATE TABLE IF NOT EXISTS document_journal (
    -- ========================================================================
    -- PRIMARY IDENTIFIERS
    -- ========================================================================
    journal_id BIGSERIAL PRIMARY KEY,
    file_hash TEXT UNIQUE NOT NULL,  -- MD5 hash (primary dedup key)

    -- ========================================================================
    -- FILE METADATA (Original)
    -- ========================================================================
    original_filename TEXT NOT NULL,
    original_file_path TEXT,
    original_file_extension TEXT,
    original_file_size BIGINT,
    original_mime_type TEXT,

    -- ========================================================================
    -- FILE METADATA (Standardized/Converted)
    -- ========================================================================
    converted_filename TEXT,  -- Renamed for consistency
    standardized_path TEXT,   -- Where we stored it
    converted_format TEXT,    -- If we converted (e.g., HEIC -> JPG)

    -- ========================================================================
    -- SOURCE TRACKING
    -- ========================================================================
    source_type TEXT NOT NULL,  -- 'mobile', 'telegram', 'web_upload', 'email', 'api'
    source_device TEXT,         -- Device ID or name
    source_location_lat DECIMAL(10, 8),
    source_location_lon DECIMAL(11, 8),
    source_ip_address INET,
    source_user_id TEXT,

    -- ========================================================================
    -- TIMESTAMP TRACKING
    -- ========================================================================
    date_logged TIMESTAMPTZ DEFAULT NOW() NOT NULL,  -- When entered system
    date_first_seen TIMESTAMPTZ,                     -- Original file creation
    date_last_modified TIMESTAMPTZ,                  -- File last modified
    date_uploaded TIMESTAMPTZ,                       -- Upload timestamp
    date_processing_started TIMESTAMPTZ,
    date_processing_completed TIMESTAMPTZ,

    -- ========================================================================
    -- DOCUMENT CLASSIFICATION
    -- ========================================================================
    document_type TEXT,  -- 'business_card', 'legal_document', 'photo', 'scan', 'form', 'receipt', 'sign', 'other'
    document_subtype TEXT,
    page_count INTEGER DEFAULT 1,
    is_multi_page BOOLEAN DEFAULT FALSE,

    -- Document type specific rules
    processing_rules JSONB,  -- Rules that apply to this document type
    compliance_requirements TEXT[],

    -- ========================================================================
    -- EXTRACTED METADATA (from filename, EXIF, etc.)
    -- ========================================================================
    extracted_metadata JSONB,  -- All metadata extracted
    /*
    Example:
    {
      "exif": {"camera": "iPhone 13", "date_taken": "2025-11-06"},
      "filename_parsed": {"case": "JUV-2024", "doc_type": "MOTION"},
      "ocr_detected_dates": ["2024-11-06", "2024-10-15"],
      "parties_mentioned": ["Person A", "Agency B"]
    }
    */

    -- ========================================================================
    -- PROCESSING STATUS & QUEUE
    -- ========================================================================
    queue_status TEXT DEFAULT 'pending' NOT NULL,
    /*
    Status flow:
    - pending: Just entered system, awaiting assessment
    - assessing: In assessment phase
    - queued: Passed assessment, queued for processing
    - processing: Currently being processed
    - completed: Processing finished successfully
    - failed: Processing failed
    - skipped_duplicate: Identified as duplicate, skipped
    - skipped_low_priority: Skipped due to low priority
    - needs_review: Manual review required
    - archived: Completed and archived
    */

    queue_priority INTEGER DEFAULT 5,  -- 1-10 (10 = highest)
    retry_count INTEGER DEFAULT 0,
    last_retry_date TIMESTAMPTZ,

    -- ========================================================================
    -- DEDUPLICATION TRACKING
    -- ========================================================================
    is_duplicate BOOLEAN DEFAULT FALSE,
    duplicate_of_journal_id BIGINT REFERENCES document_journal(journal_id),
    duplicate_detection_tier INTEGER,  -- 0, 1, 2 (which tier caught it)
    duplicate_similarity_score DECIMAL(5,4),  -- 0.0000 to 1.0000
    duplicate_detection_method TEXT,  -- 'filename', 'ocr_content', 'semantic', 'hash'

    -- ========================================================================
    -- PROCESSING METRICS & AI PERFORMANCE
    -- ========================================================================

    -- AI Processing Success
    ai_analysis_success BOOLEAN,
    ai_confidence_score DECIMAL(5,2),  -- 0.00 to 100.00
    ai_model_used TEXT,  -- 'claude-sonnet-4', 'gpt-4', etc.
    ai_processing_time_seconds DECIMAL(8,2),
    ai_cost_usd DECIMAL(8,4),

    -- OCR Metrics
    ocr_engine_used TEXT,  -- 'tesseract', 'textract', etc.
    ocr_confidence_average DECIMAL(5,2),
    ocr_text_length INTEGER,
    ocr_processing_time_seconds DECIMAL(8,2),

    -- Document Quality Metrics
    image_quality_score DECIMAL(5,2),  -- 0-100
    readability_score DECIMAL(5,2),    -- 0-100
    completeness_score DECIMAL(5,2),   -- 0-100 (is document complete?)

    -- Processing Summary
    total_processing_time_seconds DECIMAL(8,2),
    total_cost_usd DECIMAL(8,4),
    processing_error TEXT,

    -- ========================================================================
    -- DOCUMENT SCORES (Copied from analysis results)
    -- ========================================================================
    truth_score INTEGER,            -- 0-100
    justice_score INTEGER,          -- 0-100
    legal_credit_score INTEGER,     -- 300-850
    relevancy_score INTEGER,        -- 0-999
    fraud_score INTEGER,            -- 0-100
    perjury_score INTEGER,          -- 0-100

    -- ========================================================================
    -- LINKING TO OTHER TABLES
    -- ========================================================================
    document_repository_id BIGINT,  -- Link to document_repository table
    embedding_id BIGINT,            -- Link to document_embeddings
    neo4j_node_id TEXT,             -- Link to Neo4j node
    qdrant_point_id TEXT,           -- Link to Qdrant point

    -- ========================================================================
    -- REPROCESSING TRACKING
    -- ========================================================================
    reprocessing_requested BOOLEAN DEFAULT FALSE,
    reprocessing_reason TEXT,
    reprocessing_priority INTEGER,
    times_reprocessed INTEGER DEFAULT 0,
    last_reprocessed_date TIMESTAMPTZ,
    reprocessing_tier TEXT,  -- 'tier1_ocr', 'tier2_semantic', 'full_reanalysis'

    -- ========================================================================
    -- AUDIT TRAIL
    -- ========================================================================
    created_by TEXT,
    modified_by TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Versions (if document is updated)
    version INTEGER DEFAULT 1,
    superseded_by_journal_id BIGINT REFERENCES document_journal(journal_id),

    -- ========================================================================
    -- TAGS & CATEGORIZATION
    -- ========================================================================
    tags TEXT[],
    case_references TEXT[],  -- e.g., ['JUV-2024-00478', 'CV-2024-12345']
    party_references TEXT[],

    -- ========================================================================
    -- NOTES & FLAGS
    -- ========================================================================
    notes TEXT,
    flags TEXT[],  -- ['urgent', 'smoking_gun', 'needs_review', 'high_priority']
    manual_review_required BOOLEAN DEFAULT FALSE,
    manual_review_notes TEXT,

    -- ========================================================================
    -- INDEXES
    -- ========================================================================
    CONSTRAINT unique_file_hash UNIQUE (file_hash)
);

-- Indexes for fast lookups
CREATE INDEX idx_journal_queue_status ON document_journal(queue_status);
CREATE INDEX idx_journal_date_logged ON document_journal(date_logged DESC);
CREATE INDEX idx_journal_source_type ON document_journal(source_type);
CREATE INDEX idx_journal_document_type ON document_journal(document_type);
CREATE INDEX idx_journal_is_duplicate ON document_journal(is_duplicate);
CREATE INDEX idx_journal_priority ON document_journal(queue_priority DESC);
CREATE INDEX idx_journal_hash ON document_journal(file_hash);
CREATE INDEX idx_journal_original_filename ON document_journal USING gin(to_tsvector('english', original_filename));


-- ============================================================================
-- TABLE 2: PROCESSING_QUEUE (Active Queue Management)
-- ============================================================================
-- Separate table for active queue items (performance optimization)

CREATE TABLE IF NOT EXISTS processing_queue (
    queue_id BIGSERIAL PRIMARY KEY,
    journal_id BIGINT REFERENCES document_journal(journal_id) UNIQUE NOT NULL,

    -- Queue metadata
    queued_at TIMESTAMPTZ DEFAULT NOW(),
    priority INTEGER DEFAULT 5,
    processing_tier TEXT,  -- 'assessment', 'tier0', 'tier1', 'tier2', 'full_processing'

    -- Assignment
    assigned_to_worker TEXT,  -- Worker ID that picked up this job
    assigned_at TIMESTAMPTZ,

    -- Status
    status TEXT DEFAULT 'queued',  -- 'queued', 'assigned', 'processing', 'completed', 'failed'
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,

    -- Timing
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    timeout_at TIMESTAMPTZ,

    -- Results
    result_data JSONB,
    error_message TEXT,

    -- Auto-update
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_queue_status ON processing_queue(status);
CREATE INDEX idx_queue_priority ON processing_queue(priority DESC, queued_at ASC);
CREATE INDEX idx_queue_assigned_to ON processing_queue(assigned_to_worker);


-- ============================================================================
-- TABLE 3: PROCESSING_METRICS_LOG (Detailed processing log)
-- ============================================================================
-- Detailed log of every processing step for analysis and optimization

CREATE TABLE IF NOT EXISTS processing_metrics_log (
    log_id BIGSERIAL PRIMARY KEY,
    journal_id BIGINT REFERENCES document_journal(journal_id) NOT NULL,

    -- Processing step
    processing_step TEXT NOT NULL,  -- 'assessment', 'tier0_check', 'tier1_ocr', 'tier2_semantic', 'ai_analysis'
    step_started_at TIMESTAMPTZ DEFAULT NOW(),
    step_completed_at TIMESTAMPTZ,
    step_duration_seconds DECIMAL(8,2),

    -- Status
    step_status TEXT,  -- 'success', 'failed', 'skipped', 'partial'

    -- Metrics
    metrics JSONB,
    /*
    Example:
    {
      "ocr": {
        "engine": "tesseract",
        "confidence": 92.5,
        "words_extracted": 1234,
        "processing_time": 3.2
      },
      "ai_analysis": {
        "model": "claude-sonnet-4",
        "tokens_used": 5000,
        "cost": 0.015,
        "confidence": 95.0
      },
      "deduplication": {
        "tier": 1,
        "similarity": 0.87,
        "matched_journal_id": 12345
      }
    }
    */

    -- Resource usage
    cpu_usage_percent DECIMAL(5,2),
    memory_usage_mb INTEGER,
    gpu_usage_percent DECIMAL(5,2),

    -- Costs
    step_cost_usd DECIMAL(8,4),

    -- Worker info
    worker_id TEXT,
    worker_type TEXT,  -- 'local', 'vastai_gpu', 'lambda_function'

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_metrics_journal_id ON processing_metrics_log(journal_id);
CREATE INDEX idx_metrics_step ON processing_metrics_log(processing_step);
CREATE INDEX idx_metrics_status ON processing_metrics_log(step_status);


-- ============================================================================
-- TABLE 4: DOCUMENT_TYPE_RULES (Rules per document type)
-- ============================================================================

CREATE TABLE IF NOT EXISTS document_type_rules (
    rule_id SERIAL PRIMARY KEY,
    document_type TEXT UNIQUE NOT NULL,

    -- Processing requirements
    requires_ocr BOOLEAN DEFAULT TRUE,
    requires_ai_analysis BOOLEAN DEFAULT TRUE,
    requires_human_review BOOLEAN DEFAULT FALSE,

    -- Confidence thresholds
    min_ocr_confidence DECIMAL(5,2) DEFAULT 70.0,
    min_ai_confidence DECIMAL(5,2) DEFAULT 80.0,
    min_image_quality DECIMAL(5,2) DEFAULT 60.0,

    -- Compliance
    retention_period_days INTEGER,
    requires_encryption BOOLEAN DEFAULT FALSE,
    requires_audit_trail BOOLEAN DEFAULT TRUE,

    -- Processing rules
    processing_rules JSONB,
    /*
    Example for business_card:
    {
      "auto_extract_contact_info": true,
      "skip_full_ai_analysis": true,
      "fast_track": true
    }

    Example for legal_document:
    {
      "requires_full_analysis": true,
      "extract_citations": true,
      "detect_perjury": true,
      "min_relevancy_score": 500
    }
    */

    -- Priority
    default_priority INTEGER DEFAULT 5,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Default rules
INSERT INTO document_type_rules (document_type, processing_rules, default_priority) VALUES
('legal_document', '{"requires_full_analysis": true, "extract_citations": true}', 9),
('court_filing', '{"detect_perjury": true, "extract_parties": true}', 10),
('business_card', '{"auto_extract_contact": true, "skip_full_ai": true}', 3),
('photo', '{"requires_ocr": true, "image_enhancement": true}', 5),
('receipt', '{"extract_amounts": true, "extract_dates": true}', 4),
('sign', '{"ocr_only": true, "skip_ai": true}', 2),
('form', '{"extract_fields": true, "detect_checkboxes": true}', 7)
ON CONFLICT (document_type) DO NOTHING;


-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Current Queue Status
CREATE OR REPLACE VIEW queue_dashboard AS
SELECT
    queue_status,
    COUNT(*) as count,
    AVG(queue_priority) as avg_priority,
    MIN(date_logged) as oldest_entry,
    MAX(date_logged) as newest_entry
FROM document_journal
WHERE queue_status IN ('pending', 'assessing', 'queued', 'processing')
GROUP BY queue_status
ORDER BY
    CASE queue_status
        WHEN 'processing' THEN 1
        WHEN 'queued' THEN 2
        WHEN 'assessing' THEN 3
        WHEN 'pending' THEN 4
    END;

-- View: Processing Performance
CREATE OR REPLACE VIEW processing_performance AS
SELECT
    document_type,
    COUNT(*) as total_processed,
    AVG(ai_confidence_score) as avg_ai_confidence,
    AVG(total_processing_time_seconds) as avg_processing_time,
    AVG(total_cost_usd) as avg_cost,
    SUM(CASE WHEN ai_analysis_success THEN 1 ELSE 0 END) as successful,
    SUM(CASE WHEN is_duplicate THEN 1 ELSE 0 END) as duplicates_detected
FROM document_journal
WHERE queue_status = 'completed'
GROUP BY document_type
ORDER BY total_processed DESC;

-- View: Duplicate Detection Efficiency
CREATE OR REPLACE VIEW duplicate_detection_stats AS
SELECT
    duplicate_detection_tier,
    duplicate_detection_method,
    COUNT(*) as duplicates_caught,
    AVG(duplicate_similarity_score) as avg_similarity,
    SUM(total_cost_usd) * -1 as cost_saved
FROM document_journal
WHERE is_duplicate = TRUE
GROUP BY duplicate_detection_tier, duplicate_detection_method
ORDER BY duplicates_caught DESC;

-- View: Documents Needing Attention
CREATE OR REPLACE VIEW documents_needing_attention AS
SELECT
    journal_id,
    original_filename,
    document_type,
    queue_status,
    queue_priority,
    date_logged,
    flags,
    CASE
        WHEN manual_review_required THEN 'MANUAL REVIEW'
        WHEN queue_status = 'failed' AND retry_count >= 3 THEN 'MAX RETRIES'
        WHEN ai_confidence_score < 70 THEN 'LOW CONFIDENCE'
        WHEN queue_status = 'needs_review' THEN 'NEEDS REVIEW'
        ELSE 'ATTENTION'
    END as attention_reason
FROM document_journal
WHERE
    manual_review_required = TRUE
    OR (queue_status = 'failed' AND retry_count >= 3)
    OR ai_confidence_score < 70
    OR queue_status = 'needs_review'
ORDER BY queue_priority DESC, date_logged ASC;

-- View: Daily Processing Summary
CREATE OR REPLACE VIEW daily_processing_summary AS
SELECT
    DATE(date_logged) as processing_date,
    COUNT(*) as total_documents,
    SUM(CASE WHEN is_duplicate THEN 1 ELSE 0 END) as duplicates,
    SUM(CASE WHEN queue_status = 'completed' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN queue_status = 'failed' THEN 1 ELSE 0 END) as failed,
    AVG(total_processing_time_seconds) as avg_processing_time,
    SUM(total_cost_usd) as total_cost,
    AVG(ai_confidence_score) as avg_confidence
FROM document_journal
WHERE date_logged >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(date_logged)
ORDER BY processing_date DESC;


-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function: Add document to journal and queue
CREATE OR REPLACE FUNCTION add_to_journal_and_queue(
    p_file_hash TEXT,
    p_original_filename TEXT,
    p_source_type TEXT,
    p_document_type TEXT DEFAULT 'unknown',
    p_priority INTEGER DEFAULT NULL
)
RETURNS BIGINT AS $$
DECLARE
    v_journal_id BIGINT;
    v_priority INTEGER;
BEGIN
    -- Get default priority for document type
    IF p_priority IS NULL THEN
        SELECT default_priority INTO v_priority
        FROM document_type_rules
        WHERE document_type = p_document_type;

        v_priority := COALESCE(v_priority, 5);
    ELSE
        v_priority := p_priority;
    END IF;

    -- Insert into journal
    INSERT INTO document_journal (
        file_hash,
        original_filename,
        source_type,
        document_type,
        queue_status,
        queue_priority
    ) VALUES (
        p_file_hash,
        p_original_filename,
        p_source_type,
        p_document_type,
        'pending',
        v_priority
    )
    RETURNING journal_id INTO v_journal_id;

    RETURN v_journal_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Move to processing queue
CREATE OR REPLACE FUNCTION move_to_processing_queue(p_journal_id BIGINT)
RETURNS VOID AS $$
BEGIN
    INSERT INTO processing_queue (journal_id, priority)
    SELECT journal_id, queue_priority
    FROM document_journal
    WHERE journal_id = p_journal_id
    ON CONFLICT (journal_id) DO NOTHING;

    UPDATE document_journal
    SET queue_status = 'queued'
    WHERE journal_id = p_journal_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Log processing metrics
CREATE OR REPLACE FUNCTION log_processing_step(
    p_journal_id BIGINT,
    p_step TEXT,
    p_status TEXT,
    p_metrics JSONB DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO processing_metrics_log (
        journal_id,
        processing_step,
        step_status,
        metrics
    ) VALUES (
        p_journal_id,
        p_step,
        p_status,
        p_metrics
    );
END;
$$ LANGUAGE plpgsql;

-- Trigger: Update timestamp
CREATE OR REPLACE FUNCTION update_journal_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_journal_timestamp
    BEFORE UPDATE ON document_journal
    FOR EACH ROW
    EXECUTE FUNCTION update_journal_timestamp();


-- ============================================================================
-- SAMPLE QUERIES
-- ============================================================================

-- Check queue status
-- SELECT * FROM queue_dashboard;

-- Find duplicates that saved money
-- SELECT * FROM duplicate_detection_stats;

-- Get documents needing attention
-- SELECT * FROM documents_needing_attention LIMIT 10;

-- Daily processing summary
-- SELECT * FROM daily_processing_summary LIMIT 30;

-- Find specific document
-- SELECT * FROM document_journal WHERE original_filename LIKE '%motion%';

-- Reprocess a document
-- UPDATE document_journal SET reprocessing_requested = TRUE WHERE journal_id = 123;


-- ============================================================================
-- NOTES
-- ============================================================================

/*
UNIVERSAL TRUTH TABLE (document_journal):
- Every document that enters the system gets ONE row
- Never deleted (only archived)
- Source of truth for deduplication
- Reference for all processing decisions
- Audit trail for compliance
- Performance metrics for optimization

QUEUE MANAGEMENT (processing_queue):
- Active queue items only
- Performance optimization (smaller table)
- Worker assignment tracking
- Retry logic

PROCESSING METRICS (processing_metrics_log):
- Detailed step-by-step logs
- Used for optimization analysis
- Cost tracking per step
- Performance tuning data

DOCUMENT TYPE RULES (document_type_rules):
- Different rules for different document types
- Business card: fast, minimal processing
- Legal document: full analysis, high priority
- Photo/Sign: OCR only, skip AI

For Ashe. For Justice. For All Children. 🛡️
*/
