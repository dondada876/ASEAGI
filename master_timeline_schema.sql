-- ============================================================================
-- MASTER ABSOLUTE TIMELINE SCHEMA
-- Source of Truth for all events, statements, actions, motions, and filings
-- Comprehensive 5W+H tracking with truth scoring
-- ============================================================================
-- Author: ASEAGI System
-- Date: 2025-11-05
-- Purpose: Absolute timeline with truth scores for justice analysis
-- ============================================================================

-- ============================================================================
-- 1. MASTER TIMELINE TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS master_absolute_timeline (
    -- Primary Key
    id BIGSERIAL PRIMARY KEY,

    -- Timeline Entry Identification
    entry_id TEXT UNIQUE NOT NULL, -- Format: TYPE-YYYYMMDD-NNN (e.g., EVENT-20240815-001)
    entry_type TEXT NOT NULL, -- STATEMENT, EVENT, ACTION, MOTION, FILING, ORDER, VIOLATION
    category TEXT NOT NULL, -- COURT_EVENT, LEGAL_DOCUMENT, COMMUNICATION, VIOLATION, POLICE_REPORT

    -- 5W+H - Core Questions (Source of Truth)
    when_datetime TIMESTAMPTZ NOT NULL, -- When did it happen/was it said/filed?
    when_description TEXT, -- Additional temporal context

    where_location TEXT NOT NULL, -- Where did it occur? (Court, Address, Virtual, etc.)
    where_jurisdiction TEXT, -- Court/County/State jurisdiction
    where_physical_address TEXT, -- Specific address if applicable

    who_primary TEXT NOT NULL, -- Who is the primary actor/speaker/filer?
    who_secondary TEXT[], -- Who else was involved? (array of people)
    who_witnesses TEXT[], -- Who witnessed it? (array)
    who_role TEXT, -- Role of primary person (Judge, Attorney, Party, Officer, etc.)

    what_title TEXT NOT NULL, -- What happened? (brief title)
    what_description TEXT NOT NULL, -- What happened? (detailed description)
    what_type_specific TEXT, -- Specific type (Hearing, Motion to Dismiss, Declaration, etc.)

    why_stated_reason TEXT, -- Why did it happen? (stated reason)
    why_actual_reason TEXT, -- Why did it actually happen? (analysis)
    why_purpose TEXT, -- Purpose/intent

    how_method TEXT NOT NULL, -- How was it done? (Filed, Spoken, Written, etc.)
    how_details TEXT, -- How details (specific methodology)

    -- TRUTH SCORING (Core Feature)
    truth_score INTEGER CHECK (truth_score >= 0 AND truth_score <= 100), -- 0=False, 100=True
    truth_status TEXT CHECK (truth_status IN ('VERIFIED_TRUE', 'LIKELY_TRUE', 'UNVERIFIED', 'QUESTIONABLE', 'LIKELY_FALSE', 'PROVEN_FALSE')),

    -- Truth Evidence
    has_supporting_evidence BOOLEAN DEFAULT FALSE,
    supporting_evidence_ids TEXT[], -- References to evidence documents
    verified_by_official_record BOOLEAN DEFAULT FALSE,
    official_record_reference TEXT, -- Court order, transcript, etc.
    witness_corroboration BOOLEAN DEFAULT FALSE,
    witness_list TEXT[],
    contradicted_by_evidence BOOLEAN DEFAULT FALSE,
    contradicting_evidence_ids TEXT[],

    -- Fraud/Perjury Indicators
    fraud_score INTEGER CHECK (fraud_score >= 0 AND fraud_score <= 100), -- 0=No fraud, 100=Definite fraud
    perjury_score INTEGER CHECK (perjury_score >= 0 AND perjury_score <= 100),
    is_under_oath BOOLEAN DEFAULT FALSE,
    is_sworn_statement BOOLEAN DEFAULT FALSE,
    contains_false_statements BOOLEAN DEFAULT FALSE,
    false_statement_details TEXT,

    -- Importance & Impact
    importance_level TEXT CHECK (importance_level IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    relevancy_score INTEGER CHECK (relevancy_score >= 0 AND relevancy_score <= 1000),
    legal_impact TEXT CHECK (legal_impact IN ('CASE_DETERMINATIVE', 'SIGNIFICANT', 'MODERATE', 'MINOR', 'NONE')),
    constitutional_impact BOOLEAN DEFAULT FALSE,

    -- Document Linkage
    linked_document_id BIGINT, -- References legal_documents.id
    linked_event_id BIGINT, -- References court_events.id
    linked_violation_id BIGINT, -- References legal_violations.id
    linked_police_report_id BIGINT, -- References police_reports.id (new table)

    -- Source Information
    source_table TEXT, -- Which table is this originally from?
    source_id BIGINT, -- Original table's ID
    source_file_path TEXT, -- File path if from document
    source_page_number INTEGER, -- Page number in source document

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT DEFAULT 'SYSTEM',
    verified_by TEXT, -- Who verified this entry?
    verification_date TIMESTAMPTZ,

    -- Notes & Analysis
    analyst_notes TEXT,
    key_quotes TEXT, -- Important quotes from the entry
    tags TEXT[], -- Searchable tags

    -- Status
    is_disputed BOOLEAN DEFAULT FALSE,
    dispute_details TEXT,
    needs_verification BOOLEAN DEFAULT TRUE,
    verification_status TEXT CHECK (verification_status IN ('PENDING', 'IN_PROGRESS', 'VERIFIED', 'REJECTED'))
);

-- Indexes for performance
CREATE INDEX idx_master_timeline_when ON master_absolute_timeline(when_datetime DESC);
CREATE INDEX idx_master_timeline_type ON master_absolute_timeline(entry_type);
CREATE INDEX idx_master_timeline_category ON master_absolute_timeline(category);
CREATE INDEX idx_master_timeline_truth_score ON master_absolute_timeline(truth_score);
CREATE INDEX idx_master_timeline_who_primary ON master_absolute_timeline(who_primary);
CREATE INDEX idx_master_timeline_importance ON master_absolute_timeline(importance_level);
CREATE INDEX idx_master_timeline_verified ON master_absolute_timeline(verified_by_official_record);

-- Full-text search index
CREATE INDEX idx_master_timeline_search ON master_absolute_timeline
USING gin(to_tsvector('english', what_title || ' ' || what_description));

-- ============================================================================
-- 2. POLICE REPORTS TABLE (New - for binding)
-- ============================================================================

CREATE TABLE IF NOT EXISTS police_reports (
    id BIGSERIAL PRIMARY KEY,

    -- Report Identification
    report_number TEXT UNIQUE, -- Official report/case number
    report_type TEXT, -- Incident Report, CAD Report, Arrest Report, etc.
    agency TEXT NOT NULL, -- Police department/agency

    -- PX Naming Convention
    px_code TEXT NOT NULL, -- PX0, PX01, PX06-P1-P6, etc.
    original_filename TEXT,
    stored_filename TEXT NOT NULL, -- After PX renaming
    file_path TEXT NOT NULL,

    -- Page Information
    total_pages INTEGER DEFAULT 1,
    current_page INTEGER, -- For multi-page documents
    page_range TEXT, -- e.g., "1-6" for full document

    -- Report Details
    incident_date TIMESTAMPTZ,
    report_date TIMESTAMPTZ,
    incident_location TEXT,
    case_number TEXT,

    -- Parties Involved
    reporting_officer TEXT,
    badge_number TEXT,
    involved_parties TEXT[], -- Names of people in report

    -- Content Analysis
    report_summary TEXT,
    contains_false_info BOOLEAN DEFAULT FALSE,
    truth_score INTEGER CHECK (truth_score >= 0 AND truth_score <= 100),

    -- Linkage to Timeline
    timeline_event_ids BIGINT[], -- Links to master_absolute_timeline.id
    linked_violation_ids BIGINT[], -- Links to legal_violations.id

    -- Evidence Classification
    evidence_category TEXT, -- EXCULPATORY, INCULPATORY, NEUTRAL
    is_smoking_gun BOOLEAN DEFAULT FALSE,
    relevancy_score INTEGER CHECK (relevancy_score >= 0 AND relevancy_score <= 1000),

    -- OCR/Text Extraction
    extracted_text TEXT, -- Full text from OCR
    key_findings TEXT[], -- Important points

    -- Metadata
    confidence_score INTEGER CHECK (confidence_score >= 0 AND confidence_score <= 100), -- AI confidence
    scanned_at TIMESTAMPTZ DEFAULT NOW(),
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_police_reports_number ON police_reports(report_number);
CREATE INDEX idx_police_reports_px_code ON police_reports(px_code);
CREATE INDEX idx_police_reports_date ON police_reports(incident_date DESC);
CREATE INDEX idx_police_reports_truth ON police_reports(truth_score);

-- ============================================================================
-- 3. EVIDENCE BINDING TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS evidence_timeline_binding (
    id BIGSERIAL PRIMARY KEY,

    -- Link Evidence to Timeline
    timeline_entry_id BIGINT REFERENCES master_absolute_timeline(id) ON DELETE CASCADE,
    police_report_id BIGINT REFERENCES police_reports(id) ON DELETE CASCADE,
    document_id BIGINT, -- References legal_documents.id

    -- Binding Details
    binding_type TEXT CHECK (binding_type IN ('SUPPORTS', 'CONTRADICTS', 'NEUTRAL', 'CLARIFIES')),
    binding_strength TEXT CHECK (binding_strength IN ('DEFINITIVE', 'STRONG', 'MODERATE', 'WEAK')),

    -- Analysis
    binding_description TEXT NOT NULL,
    page_references TEXT, -- Specific pages that bind
    key_excerpts TEXT, -- Important quotes

    -- Impact on Truth Score
    truth_impact INTEGER, -- How much this changes truth score (+/- points)

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT DEFAULT 'SYSTEM',
    verified_by TEXT,

    UNIQUE(timeline_entry_id, police_report_id)
);

CREATE INDEX idx_evidence_binding_timeline ON evidence_timeline_binding(timeline_entry_id);
CREATE INDEX idx_evidence_binding_police ON evidence_timeline_binding(police_report_id);
CREATE INDEX idx_evidence_binding_type ON evidence_timeline_binding(binding_type);

-- ============================================================================
-- 4. TRUTH SCORE HISTORY (Track Changes)
-- ============================================================================

CREATE TABLE IF NOT EXISTS truth_score_history (
    id BIGSERIAL PRIMARY KEY,
    timeline_entry_id BIGINT REFERENCES master_absolute_timeline(id) ON DELETE CASCADE,

    -- Score Change
    old_truth_score INTEGER,
    new_truth_score INTEGER,
    score_change INTEGER, -- Calculated: new - old

    -- Reason for Change
    change_reason TEXT NOT NULL,
    evidence_added TEXT[], -- New evidence IDs

    -- Who/When
    changed_by TEXT NOT NULL,
    changed_at TIMESTAMPTZ DEFAULT NOW(),

    -- Notes
    notes TEXT
);

CREATE INDEX idx_truth_history_entry ON truth_score_history(timeline_entry_id);
CREATE INDEX idx_truth_history_date ON truth_score_history(changed_at DESC);

-- ============================================================================
-- 5. VIEWS FOR ANALYSIS
-- ============================================================================

-- All timeline entries with current truth scores
CREATE OR REPLACE VIEW v_timeline_truth_analysis AS
SELECT
    t.entry_id,
    t.entry_type,
    t.category,
    t.when_datetime,
    t.who_primary,
    t.what_title,
    t.where_location,
    t.truth_score,
    t.truth_status,
    t.fraud_score,
    t.importance_level,
    t.verified_by_official_record,
    t.has_supporting_evidence,
    COUNT(DISTINCT eb.police_report_id) as evidence_count,
    t.created_at
FROM master_absolute_timeline t
LEFT JOIN evidence_timeline_binding eb ON t.id = eb.timeline_entry_id
GROUP BY t.id, t.entry_id, t.entry_type, t.category, t.when_datetime,
         t.who_primary, t.what_title, t.where_location, t.truth_score,
         t.truth_status, t.fraud_score, t.importance_level,
         t.verified_by_official_record, t.has_supporting_evidence, t.created_at
ORDER BY t.when_datetime DESC;

-- Proven false statements (truth score < 25)
CREATE OR REPLACE VIEW v_proven_lies AS
SELECT
    entry_id,
    when_datetime,
    who_primary,
    what_title,
    what_description,
    truth_score,
    fraud_score,
    perjury_score,
    is_under_oath,
    false_statement_details,
    contradicting_evidence_ids
FROM master_absolute_timeline
WHERE truth_score < 25
ORDER BY when_datetime DESC;

-- High-truth verified statements (truth score >= 75)
CREATE OR REPLACE VIEW v_verified_truth AS
SELECT
    entry_id,
    when_datetime,
    who_primary,
    what_title,
    truth_score,
    verified_by_official_record,
    official_record_reference,
    witness_corroboration,
    supporting_evidence_ids
FROM master_absolute_timeline
WHERE truth_score >= 75
ORDER BY when_datetime DESC;

-- Justice Score Calculation (Weighted Average)
CREATE OR REPLACE VIEW v_justice_score_calculation AS
SELECT
    COUNT(*) as total_entries,
    ROUND(AVG(truth_score), 1) as simple_average,
    ROUND(
        SUM(
            truth_score *
            CASE importance_level
                WHEN 'CRITICAL' THEN 3.0
                WHEN 'HIGH' THEN 2.0
                WHEN 'MEDIUM' THEN 1.0
                ELSE 0.5
            END
        ) /
        SUM(
            CASE importance_level
                WHEN 'CRITICAL' THEN 3.0
                WHEN 'HIGH' THEN 2.0
                WHEN 'MEDIUM' THEN 1.0
                ELSE 0.5
            END
        ),
        1
    ) as weighted_justice_score,
    COUNT(*) FILTER (WHERE truth_score >= 75) as truthful_count,
    COUNT(*) FILTER (WHERE truth_score < 25) as false_count,
    COUNT(*) FILTER (WHERE truth_score >= 25 AND truth_score < 75) as questionable_count
FROM master_absolute_timeline;

-- Truth scores by actor (who)
CREATE OR REPLACE VIEW v_truth_by_actor AS
SELECT
    who_primary,
    COUNT(*) as total_statements,
    ROUND(AVG(truth_score), 1) as avg_truth_score,
    COUNT(*) FILTER (WHERE truth_score < 25) as lies_count,
    COUNT(*) FILTER (WHERE fraud_score > 70) as fraud_count,
    COUNT(*) FILTER (WHERE perjury_score > 70) as perjury_count,
    MAX(when_datetime) as last_entry
FROM master_absolute_timeline
GROUP BY who_primary
ORDER BY avg_truth_score ASC, lies_count DESC;

-- Timeline gaps analysis
CREATE OR REPLACE VIEW v_timeline_gaps AS
WITH timeline_ordered AS (
    SELECT
        entry_id,
        when_datetime,
        LAG(when_datetime) OVER (ORDER BY when_datetime) as prev_datetime,
        EXTRACT(EPOCH FROM (when_datetime - LAG(when_datetime) OVER (ORDER BY when_datetime))) / 86400 as days_gap
    FROM master_absolute_timeline
)
SELECT
    entry_id,
    prev_datetime as gap_start,
    when_datetime as gap_end,
    ROUND(days_gap::numeric, 1) as days_between,
    CASE
        WHEN days_gap > 90 THEN 'CRITICAL_GAP'
        WHEN days_gap > 30 THEN 'SIGNIFICANT_GAP'
        WHEN days_gap > 7 THEN 'NOTABLE_GAP'
        ELSE 'NORMAL'
    END as gap_severity
FROM timeline_ordered
WHERE days_gap > 7
ORDER BY days_gap DESC;

-- Police reports with bound timeline events
CREATE OR REPLACE VIEW v_police_reports_bound AS
SELECT
    pr.id,
    pr.px_code,
    pr.report_number,
    pr.report_type,
    pr.incident_date,
    pr.truth_score as report_truth_score,
    COUNT(DISTINCT eb.timeline_entry_id) as bound_events_count,
    STRING_AGG(DISTINCT t.entry_type, ', ') as event_types,
    pr.is_smoking_gun,
    pr.relevancy_score
FROM police_reports pr
LEFT JOIN evidence_timeline_binding eb ON pr.id = eb.police_report_id
LEFT JOIN master_absolute_timeline t ON eb.timeline_entry_id = t.id
GROUP BY pr.id, pr.px_code, pr.report_number, pr.report_type,
         pr.incident_date, pr.truth_score, pr.is_smoking_gun, pr.relevancy_score
ORDER BY pr.incident_date DESC;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE master_absolute_timeline IS 'Master source of truth: all events, statements, actions, motions, and filings with comprehensive 5W+H tracking and truth scoring';
COMMENT ON TABLE police_reports IS 'Police reports with PX naming convention and page numbering';
COMMENT ON TABLE evidence_timeline_binding IS 'Binds police reports and evidence to timeline entries';
COMMENT ON TABLE truth_score_history IS 'Historical tracking of truth score changes';

-- ============================================================================
-- GRANTS (Adjust as needed)
-- ============================================================================

-- GRANT ALL ON master_absolute_timeline TO authenticated;
-- GRANT ALL ON police_reports TO authenticated;
-- GRANT ALL ON evidence_timeline_binding TO authenticated;
-- GRANT ALL ON truth_score_history TO authenticated;
