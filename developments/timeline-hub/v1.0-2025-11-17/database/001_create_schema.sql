-- ============================================================================
-- TIMELINE HUB DATABASE SCHEMA - ISOLATED DEPLOYMENT
-- ============================================================================
--
-- Purpose: Master timeline and communications tracking system
-- Version: 1.0
-- Date: 2025-11-17
-- Case: J24-00478 (In re Ashe Bucknor)
--
-- ISOLATION: This schema is completely independent of other systems:
--   - Does NOT use: legal_documents, bugs, court_events tables
--   - Uses prefix: timeline_, comm_, participant_ for clarity
--   - Can be deployed/tested separately
--   - Can be dropped without affecting other systems
--
-- Tables Created:
--   1. timeline_events (master event timeline)
--   2. timeline_communications (detailed communication log)
--   3. timeline_relationships (event correlation)
--   4. timeline_participants (people registry)
--   5. timeline_phases (case periods)
--   6. timeline_processing_queue (upload queue)
--
-- ============================================================================

-- ============================================================================
-- TABLE 1: TIMELINE_EVENTS - Master Event Timeline
-- ============================================================================

CREATE TABLE IF NOT EXISTS timeline_events (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Event Classification
    event_type TEXT NOT NULL CHECK (event_type IN (
        'COURT_HEARING',
        'COURT_ORDER',
        'DECLARATION_FILED',
        'TEXT_MESSAGE',
        'EMAIL',
        'PHONE_CALL',
        'VOICEMAIL',
        'POLICE_REPORT',
        'INCIDENT',
        'DOCUMENT_FILED',
        'STATEMENT_MADE',
        'EVIDENCE_SUBMITTED',
        'VIOLATION_DETECTED',
        'MEDICAL_APPOINTMENT',
        'CPS_VISIT',
        'OTHER'
    )),

    event_subtype TEXT,
    /* Examples: hearing_detention, ruling_custody, filing_388, etc. */

    -- Event Details
    event_date DATE NOT NULL,
    event_time TIME,
    event_title TEXT NOT NULL,
    event_description TEXT,
    event_location TEXT,

    -- Participants (using standardized codes)
    primary_actor TEXT,
    /* Who initiated this event */

    primary_subject TEXT,
    /* Who was affected by this event */

    participants TEXT[] DEFAULT ARRAY[]::TEXT[],
    /* All people involved - array of codes */

    -- Participant Codes Reference:
    -- MOT (Mother), FAT (Father), MIN (Minor), CPS (CPS Worker),
    -- JUD (Judge), POL (Police), MED (Medical), ATT_MOT (Mother's Attorney),
    -- ATT_FAT (Father's Attorney), ATT_MIN (Minor's Counsel)

    -- Source Documentation
    source_type TEXT NOT NULL CHECK (source_type IN (
        'SCREENSHOT',
        'COURT_DOCUMENT',
        'EMAIL',
        'POLICE_REPORT',
        'MEDICAL_RECORD',
        'AUDIO_RECORDING',
        'VIDEO_RECORDING',
        'PHOTOGRAPH',
        'TEXT_FILE',
        'OTHER'
    )),

    source_file_path TEXT,
    /* Path to source file on disk or cloud */

    source_page_number INT,
    /* If from multi-page document */

    source_external_id UUID,
    /* Optional: Link to external system (e.g., legal_documents table if needed) */

    -- Communication Specific Fields
    communication_method TEXT CHECK (communication_method IN (
        'SMS',
        'iMessage',
        'EMAIL',
        'PHONE_CALL',
        'VOICEMAIL',
        'IN_PERSON',
        'VIDEO_CALL',
        'LETTER',
        'FAX',
        NULL
    )),

    sender TEXT,
    /* Participant code of sender */

    recipients TEXT[] DEFAULT ARRAY[]::TEXT[],
    /* Array of participant codes */

    message_preview TEXT,
    /* First 200 characters */

    message_full_text TEXT,
    /* Complete message content */

    -- Court Specific Fields
    court_name TEXT,
    case_number TEXT DEFAULT 'J24-00478',
    judge_name TEXT,
    hearing_type TEXT,
    court_outcome TEXT,

    -- Police Report Specific Fields
    report_number TEXT,
    reporting_officer TEXT,
    incident_type TEXT,

    -- Evidence & Legal Analysis
    importance INT DEFAULT 500 CHECK (importance >= 0 AND importance <= 999),
    /* PROJ344-style scoring:
       900-999: Critical (smoking gun)
       800-899: Important
       700-799: Significant
       600-699: Useful
       0-599: Reference
    */

    is_evidence BOOLEAN DEFAULT FALSE,
    evidence_category TEXT CHECK (evidence_category IN (
        'SMOKING_GUN',
        'IMPEACHMENT',
        'PATTERN',
        'TIMELINE',
        'CONTRADICTION',
        'ADMISSION',
        'THREAT',
        NULL
    )),

    legal_relevance INT DEFAULT 50 CHECK (legal_relevance >= 0 AND legal_relevance <= 100),
    admissible BOOLEAN,

    -- Content Analysis Flags
    contains_admission BOOLEAN DEFAULT FALSE,
    contains_threat BOOLEAN DEFAULT FALSE,
    contains_false_statement BOOLEAN DEFAULT FALSE,
    contains_deadline BOOLEAN DEFAULT FALSE,

    admission_text TEXT,
    threat_text TEXT,
    false_statement_text TEXT,
    deadline_date DATE,

    -- Metadata & Organization
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    keywords TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Timeline Analysis
    timeline_phase TEXT,
    /* PRE_DETENTION, DETENTION, POST_DETENTION, REUNIFICATION, APPEAL */

    days_since_case_start INT,
    days_since_detention INT,

    -- Relationships (stored as UUID arrays)
    related_events UUID[] DEFAULT ARRAY[]::UUID[],
    contradicts_events UUID[] DEFAULT ARRAY[]::UUID[],
    supports_events UUID[] DEFAULT ARRAY[]::UUID[],
    parent_event_id UUID REFERENCES timeline_events(id) ON DELETE SET NULL,

    -- Verification
    verified BOOLEAN DEFAULT FALSE,
    verified_by TEXT,
    verified_date TIMESTAMP,

    -- System Fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by TEXT DEFAULT 'system',

    -- Full-text Search
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english',
            coalesce(event_title, '') || ' ' ||
            coalesce(event_description, '') || ' ' ||
            coalesce(message_full_text, '') || ' ' ||
            coalesce(array_to_string(keywords, ' '), '')
        )
    ) STORED
);

-- Indexes for timeline_events
CREATE INDEX idx_timeline_events_date ON timeline_events(event_date DESC, event_time DESC NULLS LAST);
CREATE INDEX idx_timeline_events_type ON timeline_events(event_type);
CREATE INDEX idx_timeline_events_importance ON timeline_events(importance DESC);
CREATE INDEX idx_timeline_events_participants ON timeline_events USING GIN(participants);
CREATE INDEX idx_timeline_events_case ON timeline_events(case_number);
CREATE INDEX idx_timeline_events_search ON timeline_events USING GIN(search_vector);
CREATE INDEX idx_timeline_events_phase ON timeline_events(timeline_phase) WHERE timeline_phase IS NOT NULL;
CREATE INDEX idx_timeline_events_sender ON timeline_events(sender) WHERE sender IS NOT NULL;

-- ============================================================================
-- TABLE 2: TIMELINE_COMMUNICATIONS - Detailed Communication Log
-- ============================================================================

CREATE TABLE IF NOT EXISTS timeline_communications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Link to Timeline Event
    event_id UUID REFERENCES timeline_events(id) ON DELETE CASCADE,
    /* Each communication creates a timeline event */

    -- Communication Metadata
    comm_type TEXT NOT NULL CHECK (comm_type IN (
        'TEXT_MESSAGE',
        'EMAIL',
        'PHONE_CALL',
        'VOICEMAIL',
        'LETTER',
        'FAX',
        'VIDEO_CALL',
        'IN_PERSON',
        'OTHER'
    )),

    comm_date DATE NOT NULL,
    comm_time TIME,
    comm_datetime TIMESTAMP GENERATED ALWAYS AS (
        (comm_date + COALESCE(comm_time, '00:00:00'::TIME))
    ) STORED,

    -- Parties
    sender TEXT NOT NULL,
    sender_phone TEXT,
    sender_email TEXT,

    recipients TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    recipients_phones TEXT[] DEFAULT ARRAY[]::TEXT[],
    recipients_emails TEXT[] DEFAULT ARRAY[]::TEXT[],

    cc TEXT[] DEFAULT ARRAY[]::TEXT[],
    bcc TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Content
    subject TEXT,
    message_body TEXT,
    message_length INT GENERATED ALWAYS AS (LENGTH(message_body)) STORED,

    attachments JSONB DEFAULT '[]'::JSONB,
    /* [{name: "file.pdf", size: 1024, type: "application/pdf"}] */

    attachment_count INT GENERATED ALWAYS AS (jsonb_array_length(attachments)) STORED,

    -- Message Analysis
    sentiment TEXT CHECK (sentiment IN ('positive', 'negative', 'neutral', 'hostile', 'urgent', NULL)),
    tone TEXT CHECK (tone IN ('professional', 'casual', 'threatening', 'urgent', 'friendly', NULL)),

    -- Evidence Markers
    contains_admission BOOLEAN DEFAULT FALSE,
    contains_threat BOOLEAN DEFAULT FALSE,
    contains_false_statement BOOLEAN DEFAULT FALSE,
    contains_deadline BOOLEAN DEFAULT FALSE,

    admission_quotes TEXT[] DEFAULT ARRAY[]::TEXT[],
    threat_quotes TEXT[] DEFAULT ARRAY[]::TEXT[],
    false_statement_quotes TEXT[] DEFAULT ARRAY[]::TEXT[],
    deadline_mentioned DATE,

    -- Thread/Conversation Tracking
    thread_id UUID,
    /* Group related messages */

    in_reply_to UUID REFERENCES timeline_communications(id) ON DELETE SET NULL,
    conversation_participants TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Source
    source_platform TEXT,
    /* iPhone, Android, Gmail, Outlook, Signal, WhatsApp, etc. */

    source_screenshot_path TEXT,

    -- Scoring
    importance INT DEFAULT 500 CHECK (importance >= 0 AND importance <= 999),

    -- Metadata
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    keywords TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- System
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for timeline_communications
CREATE INDEX idx_timeline_comms_date ON timeline_communications(comm_date DESC, comm_time DESC NULLS LAST);
CREATE INDEX idx_timeline_comms_sender ON timeline_communications(sender);
CREATE INDEX idx_timeline_comms_type ON timeline_communications(comm_type);
CREATE INDEX idx_timeline_comms_thread ON timeline_communications(thread_id) WHERE thread_id IS NOT NULL;
CREATE INDEX idx_timeline_comms_event ON timeline_communications(event_id);

-- ============================================================================
-- TABLE 3: TIMELINE_RELATIONSHIPS - Event Correlation
-- ============================================================================

CREATE TABLE IF NOT EXISTS timeline_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Events Being Related
    event_1_id UUID NOT NULL REFERENCES timeline_events(id) ON DELETE CASCADE,
    event_2_id UUID NOT NULL REFERENCES timeline_events(id) ON DELETE CASCADE,

    -- Relationship Type
    relationship_type TEXT NOT NULL CHECK (relationship_type IN (
        'CAUSED_BY',
        'LEADS_TO',
        'CONTRADICTS',
        'SUPPORTS',
        'PART_OF',
        'RESPONSE_TO',
        'ESCALATION',
        'PATTERN',
        'SAME_THREAD',
        'FOLLOWS',
        'PRECEDES'
    )),

    -- Relationship Details
    relationship_strength INT DEFAULT 50 CHECK (relationship_strength >= 0 AND relationship_strength <= 100),
    relationship_description TEXT,

    -- Timeline Analysis
    time_gap_days INT,
    time_gap_hours INT,
    sequence_order INT,

    -- Pattern Detection
    pattern_id UUID,
    pattern_name TEXT,
    pattern_frequency INT,

    -- Legal Significance
    legal_significance INT DEFAULT 50 CHECK (legal_significance >= 0 AND legal_significance <= 100),
    proves_element TEXT,
    /* What legal element this relationship proves */

    -- System
    detected_by TEXT DEFAULT 'manual',
    /* 'system' or 'manual' */

    detected_at TIMESTAMP DEFAULT NOW(),
    verified BOOLEAN DEFAULT FALSE,
    verified_by TEXT,
    verified_at TIMESTAMP,

    -- Ensure no self-references
    CONSTRAINT no_self_reference CHECK (event_1_id != event_2_id)
);

-- Indexes for timeline_relationships
CREATE INDEX idx_timeline_rel_event1 ON timeline_relationships(event_1_id);
CREATE INDEX idx_timeline_rel_event2 ON timeline_relationships(event_2_id);
CREATE INDEX idx_timeline_rel_type ON timeline_relationships(relationship_type);
CREATE INDEX idx_timeline_rel_pattern ON timeline_relationships(pattern_id) WHERE pattern_id IS NOT NULL;

-- ============================================================================
-- TABLE 4: TIMELINE_PARTICIPANTS - People Registry
-- ============================================================================

CREATE TABLE IF NOT EXISTS timeline_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Identity
    participant_code TEXT UNIQUE NOT NULL,
    /* Standardized codes: MOT, FAT, MIN, CPS, JUD, POL, MED, etc. */

    full_name TEXT NOT NULL,

    role TEXT NOT NULL CHECK (role IN (
        'PARENT',
        'CHILD',
        'CPS_WORKER',
        'JUDGE',
        'ATTORNEY',
        'POLICE_OFFICER',
        'MEDICAL_PROFESSIONAL',
        'SOCIAL_WORKER',
        'WITNESS',
        'GUARDIAN_AD_LITEM',
        'THERAPIST',
        'OTHER'
    )),

    -- Contact Information
    phone_numbers TEXT[] DEFAULT ARRAY[]::TEXT[],
    email_addresses TEXT[] DEFAULT ARRAY[]::TEXT[],
    addresses JSONB DEFAULT '[]'::JSONB,

    -- Case Relationship
    party_type TEXT CHECK (party_type IN (
        'PETITIONER',
        'RESPONDENT',
        'MINOR',
        'AGENCY',
        'COURT',
        'THIRD_PARTY',
        NULL
    )),

    representing TEXT,
    /* If attorney: who they represent */

    -- Participation Summary (auto-calculated)
    total_events INT DEFAULT 0,
    total_communications_sent INT DEFAULT 0,
    total_communications_received INT DEFAULT 0,

    first_appearance DATE,
    last_appearance DATE,

    -- Notes & Aliases
    notes TEXT,
    aliases TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- System
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for timeline_participants
CREATE INDEX idx_timeline_participants_code ON timeline_participants(participant_code);
CREATE INDEX idx_timeline_participants_role ON timeline_participants(role);

-- ============================================================================
-- TABLE 5: TIMELINE_PHASES - Case Periods
-- ============================================================================

CREATE TABLE IF NOT EXISTS timeline_phases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Phase Definition
    phase_name TEXT NOT NULL,
    phase_description TEXT,

    -- Date Range
    start_date DATE NOT NULL,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,

    -- Phase Type
    phase_type TEXT CHECK (phase_type IN (
        'PRE_CASE',
        'FILING',
        'DETENTION',
        'REUNIFICATION',
        'TRIAL',
        'APPEAL',
        'POST_JUDGMENT',
        'CUSTOM'
    )),

    -- Summary Metrics (calculated)
    total_events INT DEFAULT 0,
    critical_events INT DEFAULT 0,
    communications_count INT DEFAULT 0,

    -- Legal Status During Phase
    custody_status TEXT,
    visitation_status TEXT,
    case_status TEXT,

    -- System
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Ensure no date overlap for same case
    CONSTRAINT valid_date_range CHECK (end_date IS NULL OR end_date >= start_date)
);

-- Indexes for timeline_phases
CREATE INDEX idx_timeline_phases_dates ON timeline_phases(start_date, end_date);
CREATE INDEX idx_timeline_phases_current ON timeline_phases(is_current) WHERE is_current = TRUE;

-- ============================================================================
-- TABLE 6: TIMELINE_PROCESSING_QUEUE - Document Upload Queue
-- ============================================================================

CREATE TABLE IF NOT EXISTS timeline_processing_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Source
    source_type TEXT NOT NULL CHECK (source_type IN (
        'TELEGRAM',
        'WEB_UPLOAD',
        'EMAIL',
        'SCAN',
        'API',
        'MANUAL'
    )),

    source_identifier TEXT,
    /* Telegram message ID, upload session ID, etc. */

    -- File Information
    file_path TEXT NOT NULL,
    file_name TEXT,
    file_type TEXT,
    file_size_bytes BIGINT,
    file_hash TEXT,
    /* MD5 or SHA256 for deduplication */

    -- Processing Request
    processing_type TEXT NOT NULL CHECK (processing_type IN (
        'TEXT_MESSAGE',
        'EMAIL',
        'COURT_DOC',
        'POLICE_REPORT',
        'MEDICAL_RECORD',
        'SCREENSHOT',
        'GENERIC'
    )),

    -- Processing Options
    extract_events BOOLEAN DEFAULT TRUE,
    extract_communications BOOLEAN DEFAULT TRUE,
    extract_statements BOOLEAN DEFAULT TRUE,

    -- Status
    status TEXT DEFAULT 'pending' CHECK (status IN (
        'pending',
        'processing',
        'completed',
        'failed',
        'skipped',
        'duplicate'
    )),

    priority INT DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    /* 1 = lowest, 10 = highest */

    -- Processing Results
    events_created INT DEFAULT 0,
    communications_created INT DEFAULT 0,
    statements_created INT DEFAULT 0,

    created_event_ids UUID[] DEFAULT ARRAY[]::UUID[],

    -- Errors
    error_message TEXT,
    error_details JSONB,

    -- Timing
    queued_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    processing_time_seconds INT,

    -- System
    processed_by TEXT,

    CONSTRAINT valid_status_transition CHECK (
        (status = 'pending' AND started_at IS NULL) OR
        (status != 'pending')
    )
);

-- Indexes for timeline_processing_queue
CREATE INDEX idx_timeline_queue_status ON timeline_processing_queue(status);
CREATE INDEX idx_timeline_queue_priority ON timeline_processing_queue(priority DESC, queued_at ASC);
CREATE INDEX idx_timeline_queue_hash ON timeline_processing_queue(file_hash) WHERE file_hash IS NOT NULL;

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to update participant stats
CREATE OR REPLACE FUNCTION update_participant_stats(p_code TEXT)
RETURNS VOID AS $$
BEGIN
    UPDATE timeline_participants
    SET
        total_events = (
            SELECT COUNT(*)
            FROM timeline_events
            WHERE p_code = ANY(participants)
        ),
        total_communications_sent = (
            SELECT COUNT(*)
            FROM timeline_communications
            WHERE sender = p_code
        ),
        total_communications_received = (
            SELECT COUNT(*)
            FROM timeline_communications
            WHERE p_code = ANY(recipients)
        ),
        first_appearance = (
            SELECT MIN(event_date)
            FROM timeline_events
            WHERE p_code = ANY(participants)
        ),
        last_appearance = (
            SELECT MAX(event_date)
            FROM timeline_events
            WHERE p_code = ANY(participants)
        ),
        updated_at = NOW()
    WHERE participant_code = p_code;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate time gap between events
CREATE OR REPLACE FUNCTION calculate_time_gap(
    date1 TIMESTAMP,
    date2 TIMESTAMP,
    OUT gap_days INT,
    OUT gap_hours INT
) AS $$
BEGIN
    gap_days := EXTRACT(DAYS FROM (date2 - date1))::INT;
    gap_hours := EXTRACT(HOURS FROM (date2 - date1))::INT;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- INITIAL DATA - Standard Participants
-- ============================================================================

INSERT INTO timeline_participants (participant_code, full_name, role, party_type)
VALUES
    ('MOT', 'Mariyam Yonas Rufael', 'PARENT', 'RESPONDENT'),
    ('FAT', 'Don Bucknor', 'PARENT', 'RESPONDENT'),
    ('MIN', 'Ashe Bucknor', 'CHILD', 'MINOR'),
    ('CPS', 'CPS Social Worker', 'CPS_WORKER', 'AGENCY'),
    ('JUD', 'Judge', 'JUDGE', 'COURT')
ON CONFLICT (participant_code) DO NOTHING;

-- ============================================================================
-- GRANTS (if needed for specific users)
-- ============================================================================

-- Grant permissions to authenticated users (Supabase)
-- ALTER DEFAULT PRIVILEGES GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;

-- ============================================================================
-- SCHEMA VERSION TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS timeline_schema_version (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT NOW(),
    description TEXT
);

INSERT INTO timeline_schema_version (version, description)
VALUES ('1.0', 'Initial timeline hub schema - isolated deployment')
ON CONFLICT (version) DO NOTHING;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

-- Verification Queries:
--
-- SELECT COUNT(*) FROM timeline_events;
-- SELECT COUNT(*) FROM timeline_communications;
-- SELECT COUNT(*) FROM timeline_participants;
-- SELECT * FROM timeline_schema_version;
