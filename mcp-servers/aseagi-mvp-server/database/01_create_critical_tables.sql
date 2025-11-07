-- ============================================================================
-- ASEAGI Critical Database Tables
-- Version: 1.0.0
-- Purpose: Core evidence, timeline, and document tracking infrastructure
-- ============================================================================

-- TABLE 1: communications
-- Critical for evidence - tracks all case communications
-- ============================================================================

CREATE TABLE IF NOT EXISTS communications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Communication Details
    sender TEXT NOT NULL,
    recipient TEXT NOT NULL,
    subject TEXT,
    content TEXT,
    summary TEXT,

    -- Metadata
    communication_date TIMESTAMP WITH TIME ZONE NOT NULL,
    communication_method TEXT CHECK (communication_method IN (
        'email', 'text', 'phone', 'letter', 'in_person',
        'court_filing', 'social_media', 'other'
    )),

    -- Evidence Scoring (0-1000 scale)
    truthfulness_score INTEGER CHECK (truthfulness_score >= 0 AND truthfulness_score <= 1000),
    contains_contradiction BOOLEAN DEFAULT FALSE,
    contains_manipulation BOOLEAN DEFAULT FALSE,
    relevancy_score INTEGER CHECK (relevancy_score >= 0 AND relevancy_score <= 1000),

    -- Case Linkage
    case_id TEXT,
    document_id UUID REFERENCES legal_documents(id) ON DELETE SET NULL,

    -- Attachments
    has_attachments BOOLEAN DEFAULT FALSE,
    attachment_count INTEGER DEFAULT 0,
    attachment_urls TEXT[],

    -- Classification
    communication_type TEXT, -- 'threat', 'request', 'update', 'evidence', etc.
    tags TEXT[],
    categories TEXT[],

    -- Full text search
    search_vector tsvector
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_communications_date ON communications(communication_date DESC);
CREATE INDEX IF NOT EXISTS idx_communications_sender ON communications(sender);
CREATE INDEX IF NOT EXISTS idx_communications_recipient ON communications(recipient);
CREATE INDEX IF NOT EXISTS idx_communications_method ON communications(communication_method);
CREATE INDEX IF NOT EXISTS idx_communications_search ON communications USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_communications_case ON communications(case_id);

-- Update search vector automatically
CREATE OR REPLACE FUNCTION communications_search_vector_update()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.subject, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.content, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.sender, '')), 'C') ||
        setweight(to_tsvector('english', COALESCE(NEW.recipient, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER communications_search_vector_trigger
    BEFORE INSERT OR UPDATE ON communications
    FOR EACH ROW EXECUTE FUNCTION communications_search_vector_update();

-- Update timestamp automatically
CREATE TRIGGER communications_updated_at_trigger
    BEFORE UPDATE ON communications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE communications IS 'Critical evidence table - tracks all case communications for legal analysis';
COMMENT ON COLUMN communications.truthfulness_score IS 'Truth score 0-1000 (0=perjury, 1000=verified truth)';
COMMENT ON COLUMN communications.relevancy_score IS 'Relevance to case 0-1000';


-- ============================================================================
-- TABLE 2: events
-- Most important timeline factor - tracks all case events chronologically
-- ============================================================================

CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Event Details
    event_date TIMESTAMP WITH TIME ZONE NOT NULL,
    event_title TEXT NOT NULL,
    event_description TEXT,
    event_type TEXT CHECK (event_type IN (
        'hearing', 'filing', 'motion', 'ruling', 'order',
        'deadline', 'communication', 'incident', 'evaluation',
        'investigation', 'service', 'testimony', 'evidence_submission',
        'other'
    )),

    -- Court Information
    judge_name TEXT,
    department TEXT,
    case_number TEXT,

    -- Outcome & Impact
    event_outcome TEXT,
    outcome_favorable BOOLEAN,
    significance_score INTEGER CHECK (significance_score >= 0 AND significance_score <= 1000),

    -- Parties Involved
    parties_involved TEXT[],
    attorney_present TEXT[],
    witnesses TEXT[],

    -- Legal Context
    legal_standard_applied TEXT,
    laws_cited TEXT[],
    evidence_presented TEXT[],

    -- Compliance Tracking
    proper_notice_given BOOLEAN,
    due_process_followed BOOLEAN,
    violations_occurred TEXT[],

    -- Document Linkage
    related_documents UUID[],
    court_minutes_url TEXT,
    recording_url TEXT,
    transcript_url TEXT,

    -- Classification
    tags TEXT[],
    categories TEXT[],
    milestone BOOLEAN DEFAULT FALSE,

    -- Analysis
    notes TEXT,
    red_flags TEXT[],
    action_items TEXT[],

    -- Search
    search_vector tsvector
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_events_date ON events(event_date DESC);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_case ON events(case_number);
CREATE INDEX IF NOT EXISTS idx_events_judge ON events(judge_name);
CREATE INDEX IF NOT EXISTS idx_events_significance ON events(significance_score DESC);
CREATE INDEX IF NOT EXISTS idx_events_milestone ON events(milestone) WHERE milestone = TRUE;
CREATE INDEX IF NOT EXISTS idx_events_search ON events USING GIN(search_vector);

-- Update search vector automatically
CREATE OR REPLACE FUNCTION events_search_vector_update()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.event_title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.event_description, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.event_outcome, '')), 'C') ||
        setweight(to_tsvector('english', COALESCE(NEW.notes, '')), 'D');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER events_search_vector_trigger
    BEFORE INSERT OR UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION events_search_vector_update();

-- Update timestamp automatically
CREATE TRIGGER events_updated_at_trigger
    BEFORE UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE events IS 'Critical timeline table - most important factor for case chronology and pattern analysis';
COMMENT ON COLUMN events.significance_score IS 'Event importance 0-1000 for case outcome';


-- ============================================================================
-- TABLE 3: document_journal
-- Critical for tracking document processing and long-term growth assessment
-- ============================================================================

CREATE TABLE IF NOT EXISTS document_journal (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Document Reference
    document_id UUID REFERENCES legal_documents(id) ON DELETE CASCADE,
    original_filename TEXT NOT NULL,
    document_type TEXT,

    -- Processing Timeline
    scan_date TIMESTAMP WITH TIME ZONE,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_date TIMESTAMP WITH TIME ZONE,
    analyzed_date TIMESTAMP WITH TIME ZONE,
    reviewed_date TIMESTAMP WITH TIME ZONE,

    -- Processing Status
    processing_status TEXT CHECK (processing_status IN (
        'pending', 'scanning', 'uploading', 'processing',
        'analyzing', 'review_needed', 'completed', 'error'
    )) DEFAULT 'pending',

    -- Processing Details
    ocr_completed BOOLEAN DEFAULT FALSE,
    ocr_confidence_score DECIMAL(5,2),
    page_count INTEGER,
    word_count INTEGER,

    -- AI Analysis Tracking
    micro_analysis_completed BOOLEAN DEFAULT FALSE,
    macro_analysis_completed BOOLEAN DEFAULT FALSE,
    violation_detection_completed BOOLEAN DEFAULT FALSE,

    -- Scoring (0-1000 scale)
    relevancy_score INTEGER CHECK (relevancy_score >= 0 AND relevancy_score <= 1000),
    truth_score INTEGER CHECK (truth_score >= 0 AND truth_score <= 1000),
    micro_score INTEGER CHECK (micro_score >= 0 AND micro_score <= 1000),
    macro_score INTEGER CHECK (macro_score >= 0 AND macro_score <= 1000),

    -- Quality Metrics
    quality_score INTEGER CHECK (quality_score >= 0 AND quality_score <= 1000),
    completeness_score INTEGER CHECK (completeness_score >= 0 AND completeness_score <= 1000),

    -- Growth Assessment
    insights_extracted INTEGER DEFAULT 0,
    contradictions_found INTEGER DEFAULT 0,
    violations_detected INTEGER DEFAULT 0,
    connections_made INTEGER DEFAULT 0,

    -- Version Control
    version INTEGER DEFAULT 1,
    previous_version_id UUID REFERENCES document_journal(id),

    -- Processing Metadata
    processor_name TEXT, -- AI model or human name
    processing_duration_seconds INTEGER,
    tokens_used INTEGER,
    cost_usd DECIMAL(10,4),

    -- Error Tracking
    errors_encountered TEXT[],
    warnings_encountered TEXT[],

    -- Notes & Context
    processing_notes TEXT,
    review_notes TEXT,
    upgrade_recommendations TEXT[],

    -- Classification
    tags TEXT[],
    categories TEXT[],

    -- Storage
    storage_path TEXT,
    file_size_bytes BIGINT,
    checksum TEXT,

    -- Search
    search_vector tsvector
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_document_journal_doc_id ON document_journal(document_id);
CREATE INDEX IF NOT EXISTS idx_document_journal_status ON document_journal(processing_status);
CREATE INDEX IF NOT EXISTS idx_document_journal_upload_date ON document_journal(upload_date DESC);
CREATE INDEX IF NOT EXISTS idx_document_journal_processed_date ON document_journal(processed_date DESC);
CREATE INDEX IF NOT EXISTS idx_document_journal_relevancy ON document_journal(relevancy_score DESC);
CREATE INDEX IF NOT EXISTS idx_document_journal_search ON document_journal USING GIN(search_vector);

-- Update search vector automatically
CREATE OR REPLACE FUNCTION document_journal_search_vector_update()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.original_filename, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.document_type, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.processing_notes, '')), 'C') ||
        setweight(to_tsvector('english', COALESCE(NEW.review_notes, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER document_journal_search_vector_trigger
    BEFORE INSERT OR UPDATE ON document_journal
    FOR EACH ROW EXECUTE FUNCTION document_journal_search_vector_update();

-- Update timestamp automatically
CREATE TRIGGER document_journal_updated_at_trigger
    BEFORE UPDATE ON document_journal
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Automatically increment version on update
CREATE OR REPLACE FUNCTION document_journal_version_increment()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.id IS NOT NULL THEN
        NEW.version := OLD.version + 1;
        NEW.previous_version_id := OLD.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER document_journal_version_trigger
    BEFORE UPDATE ON document_journal
    FOR EACH ROW EXECUTE FUNCTION document_journal_version_increment();

COMMENT ON TABLE document_journal IS 'Critical tracking table - records every document scan, processing step, and assessment for long-term growth analysis';
COMMENT ON COLUMN document_journal.processing_status IS 'Current processing state of document';
COMMENT ON COLUMN document_journal.insights_extracted IS 'Number of legal insights extracted during processing';
COMMENT ON COLUMN document_journal.contradictions_found IS 'Number of contradictions identified in document';


-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Recent communications requiring review
CREATE OR REPLACE VIEW communications_needing_review AS
SELECT
    id,
    communication_date,
    sender,
    recipient,
    subject,
    truthfulness_score,
    contains_contradiction,
    contains_manipulation
FROM communications
WHERE
    truthfulness_score IS NULL
    OR truthfulness_score < 500
    OR contains_contradiction = TRUE
    OR contains_manipulation = TRUE
ORDER BY communication_date DESC;

-- View: Upcoming events and deadlines
CREATE OR REPLACE VIEW upcoming_events AS
SELECT
    id,
    event_date,
    event_title,
    event_type,
    significance_score,
    action_items
FROM events
WHERE
    event_date >= NOW()
ORDER BY event_date ASC;

-- View: Documents pending processing
CREATE OR REPLACE VIEW documents_pending_processing AS
SELECT
    id,
    original_filename,
    upload_date,
    processing_status,
    micro_analysis_completed,
    macro_analysis_completed
FROM document_journal
WHERE
    processing_status IN ('pending', 'processing', 'review_needed')
    OR micro_analysis_completed = FALSE
    OR macro_analysis_completed = FALSE
ORDER BY upload_date ASC;


-- ============================================================================
-- GRANT PERMISSIONS (adjust as needed for your Supabase setup)
-- ============================================================================

-- Grant appropriate permissions to authenticated users
GRANT SELECT, INSERT, UPDATE ON communications TO authenticated;
GRANT SELECT, INSERT, UPDATE ON events TO authenticated;
GRANT SELECT, INSERT, UPDATE ON document_journal TO authenticated;

GRANT SELECT ON communications_needing_review TO authenticated;
GRANT SELECT ON upcoming_events TO authenticated;
GRANT SELECT ON documents_pending_processing TO authenticated;


-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✓ ASEAGI Critical Tables Created Successfully';
    RAISE NOTICE '  - communications: Evidence tracking';
    RAISE NOTICE '  - events: Timeline (most important)';
    RAISE NOTICE '  - document_journal: Processing & growth assessment';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Verify tables in Supabase dashboard';
    RAISE NOTICE '2. Populate with existing data if needed';
    RAISE NOTICE '3. Update MCP server to use these tables';
END $$;
