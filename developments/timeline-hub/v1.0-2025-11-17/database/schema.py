"""
Master Timeline & Communications Hub - Database Schema
=======================================================

Comprehensive schema for tracking all events, communications, and timeline data
across multiple sources: Courts, Texts, Emails, Police Reports, Screenshots

Database: Supabase PostgreSQL
Case: J24-00478 (In re Ashe Bucknor)
"""

# ============================================================================
# TABLE 1: MASTER EVENTS TIMELINE
# ============================================================================

CREATE_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS timeline_events (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Event Classification
    event_type TEXT NOT NULL,
    /* Types:
       - COURT_HEARING
       - COURT_ORDER
       - DECLARATION_FILED
       - TEXT_MESSAGE
       - EMAIL
       - PHONE_CALL
       - POLICE_REPORT
       - INCIDENT
       - DOCUMENT_FILED
       - STATEMENT_MADE
       - EVIDENCE_SUBMITTED
       - VIOLATION_DETECTED
    */

    event_subtype TEXT,
    /* Subtypes by category:
       Court: hearing, ruling, filing, continuance
       Communication: sent, received, missed
       Incident: abuse, neglect, welfare_check
       Legal: motion, declaration, response, objection
    */

    -- Event Details
    event_date TIMESTAMP NOT NULL,
    event_time TIME,
    event_title TEXT NOT NULL,
    event_description TEXT,
    event_location TEXT,

    -- Participants
    primary_actor TEXT,     -- Who initiated/caused the event
    primary_subject TEXT,   -- Who was affected
    participants TEXT[],    -- All people involved
    /* Participant codes:
       MOT - Mother (Mariyam)
       FAT - Father (Don)
       MIN - Minor (Ashe)
       CPS - CPS social worker
       JUD - Judge
       ATT_MOT - Mother's attorney
       ATT_FAT - Father's attorney
       POL - Police officer
       MED - Medical professional
    */

    -- Source Documentation
    source_type TEXT NOT NULL,
    /* COURT_DOCUMENT, TEXT_MESSAGE, EMAIL, SCREENSHOT,
       POLICE_REPORT, MEDICAL_RECORD, AUDIO, VIDEO */

    source_document_id UUID REFERENCES legal_documents(id),
    source_file_path TEXT,
    source_page_number INT,

    -- Communication Specific
    communication_method TEXT,
    /* SMS, EMAIL, CALL, VOICEMAIL, IN_PERSON, VIDEO_CALL */

    sender TEXT,
    recipients TEXT[],
    message_preview TEXT,    -- First 200 chars
    message_full_text TEXT,

    -- Court Specific
    court_name TEXT,
    case_number TEXT DEFAULT 'J24-00478',
    judge_name TEXT,
    hearing_type TEXT,
    court_outcome TEXT,

    -- Police Report Specific
    report_number TEXT,
    reporting_officer TEXT,
    incident_type TEXT,

    -- Metadata
    importance INT CHECK (importance >= 0 AND importance <= 999),
    /* 0-999 PROJ344 style:
       900-999: Critical events (smoking gun)
       800-899: Important events
       700-799: Significant events
       600-699: Useful context
       0-599: Reference
    */

    tags TEXT[],
    keywords TEXT[],

    -- Relationships
    related_events UUID[],           -- Other events connected to this
    contradicts_events UUID[],       -- Events this contradicts
    supports_events UUID[],          -- Events this supports
    parent_event_id UUID REFERENCES timeline_events(id),  -- Part of larger event

    -- Timeline Analysis
    timeline_phase TEXT,
    /* PRE_DETENTION, DETENTION, POST_DETENTION, REUNIFICATION, etc. */

    days_since_detention INT,
    days_until_next_hearing INT,

    -- Verification
    verified BOOLEAN DEFAULT FALSE,
    verified_by TEXT,
    verified_date TIMESTAMP,

    -- Evidence & Legal
    is_evidence BOOLEAN DEFAULT FALSE,
    evidence_category TEXT,
    /* SMOKING_GUN, IMPEACHMENT, PATTERN, TIMELINE, CONTRADICTION */

    legal_relevance INT,    -- 0-100
    admissible BOOLEAN,

    -- System Fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by TEXT DEFAULT 'system',

    -- Search optimization
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english',
            coalesce(event_title, '') || ' ' ||
            coalesce(event_description, '') || ' ' ||
            coalesce(message_full_text, '')
        )
    ) STORED
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_events_date ON timeline_events(event_date DESC);
CREATE INDEX IF NOT EXISTS idx_events_type ON timeline_events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_participants ON timeline_events USING GIN(participants);
CREATE INDEX IF NOT EXISTS idx_events_importance ON timeline_events(importance DESC);
CREATE INDEX IF NOT EXISTS idx_events_search ON timeline_events USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_events_case ON timeline_events(case_number);
"""

# ============================================================================
# TABLE 2: COMMUNICATIONS LOG (Detailed tracking)
# ============================================================================

CREATE_COMMUNICATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS communications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Link to main timeline
    event_id UUID REFERENCES timeline_events(id),

    -- Communication Details
    comm_type TEXT NOT NULL,
    /* TEXT_MESSAGE, EMAIL, PHONE_CALL, VOICEMAIL,
       LETTER, FAX, VIDEO_CALL, IN_PERSON */

    comm_date TIMESTAMP NOT NULL,
    comm_time TIME,

    -- Parties
    sender TEXT NOT NULL,
    sender_phone TEXT,
    sender_email TEXT,

    recipients TEXT[] NOT NULL,
    recipients_phones TEXT[],
    recipients_emails TEXT[],

    cc TEXT[],
    bcc TEXT[],

    -- Content
    subject TEXT,
    message_body TEXT,
    message_length INT,
    attachment_count INT,
    attachments JSONB,

    -- Message Analysis
    sentiment TEXT,  -- positive, negative, neutral, hostile
    tone TEXT,       -- professional, casual, threatening, urgent
    keywords TEXT[],

    -- Evidence Markers
    contains_admission BOOLEAN DEFAULT FALSE,
    contains_threat BOOLEAN DEFAULT FALSE,
    contains_false_statement BOOLEAN DEFAULT FALSE,
    contains_deadline BOOLEAN DEFAULT FALSE,

    admission_text TEXT[],
    threat_text TEXT[],
    false_statement_text TEXT[],
    deadline_mentioned DATE,

    -- Thread/Conversation
    thread_id UUID,
    in_reply_to UUID REFERENCES communications(id),
    conversation_participants TEXT[],

    -- Source
    source_platform TEXT,
    /* iPhone, Android, Gmail, Outlook, Court_Portal, etc. */

    source_screenshot_path TEXT,
    source_document_id UUID REFERENCES legal_documents(id),

    -- Metadata
    importance INT CHECK (importance >= 0 AND importance <= 999),
    tags TEXT[],

    -- System
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_comms_date ON communications(comm_date DESC);
CREATE INDEX IF NOT EXISTS idx_comms_sender ON communications(sender);
CREATE INDEX IF NOT EXISTS idx_comms_type ON communications(comm_type);
CREATE INDEX IF NOT EXISTS idx_comms_thread ON communications(thread_id);
"""

# ============================================================================
# TABLE 3: EVENT RELATIONSHIPS & PATTERNS
# ============================================================================

CREATE_EVENT_RELATIONSHIPS_TABLE = """
CREATE TABLE IF NOT EXISTS event_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Events being related
    event_1_id UUID NOT NULL REFERENCES timeline_events(id),
    event_2_id UUID NOT NULL REFERENCES timeline_events(id),

    -- Relationship Type
    relationship_type TEXT NOT NULL,
    /*
       CAUSED_BY - Event 2 caused Event 1
       LEADS_TO - Event 1 leads to Event 2
       CONTRADICTS - Events contradict each other
       SUPPORTS - Events support each other
       PART_OF - Event 1 is part of Event 2
       RESPONSE_TO - Event 1 responds to Event 2
       ESCALATION - Event 2 escalates Event 1
       PATTERN - Part of recurring pattern
    */

    -- Relationship Details
    relationship_strength INT CHECK (relationship_strength >= 0 AND relationship_strength <= 100),
    relationship_description TEXT,

    -- Timeline Analysis
    time_gap_days INT,
    time_gap_hours INT,
    sequence_order INT,

    -- Pattern Detection
    pattern_id UUID,
    pattern_name TEXT,
    pattern_frequency INT,

    -- Evidence Value
    legal_significance INT,
    proves_element TEXT,  -- What legal element this proves

    -- System
    detected_by TEXT,  -- 'system' or 'manual'
    detected_at TIMESTAMP DEFAULT NOW(),
    verified BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_rel_event1 ON event_relationships(event_1_id);
CREATE INDEX IF NOT EXISTS idx_rel_event2 ON event_relationships(event_2_id);
CREATE INDEX IF NOT EXISTS idx_rel_type ON event_relationships(relationship_type);
"""

# ============================================================================
# TABLE 4: PARTICIPANTS REGISTRY
# ============================================================================

CREATE_PARTICIPANTS_TABLE = """
CREATE TABLE IF NOT EXISTS participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Identity
    participant_code TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL,
    /* PARENT, CHILD, CPS_WORKER, JUDGE, ATTORNEY,
       POLICE_OFFICER, MEDICAL_PROFESSIONAL, WITNESS, OTHER */

    -- Contact Info
    phone_numbers TEXT[],
    email_addresses TEXT[],
    addresses JSONB,

    -- Case Relationship
    party_type TEXT,
    /* PETITIONER, RESPONDENT, MINOR, AGENCY, COURT, THIRD_PARTY */

    representing TEXT,  -- Who they represent (if attorney)

    -- Participation Summary
    total_events INT DEFAULT 0,
    total_communications_sent INT DEFAULT 0,
    total_communications_received INT DEFAULT 0,

    first_appearance DATE,
    last_appearance DATE,

    -- Notes
    notes TEXT,
    aliases TEXT[],

    -- System
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_participants_code ON participants(participant_code);
CREATE INDEX IF NOT EXISTS idx_participants_role ON participants(role);
"""

# ============================================================================
# TABLE 5: TIMELINE PHASES & PERIODS
# ============================================================================

CREATE_TIMELINE_PHASES_TABLE = """
CREATE TABLE IF NOT EXISTS timeline_phases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Phase Definition
    phase_name TEXT NOT NULL,
    phase_description TEXT,

    -- Date Range
    start_date DATE NOT NULL,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,

    -- Phase Characteristics
    phase_type TEXT,
    /* PRE_CASE, FILING, DETENTION, REUNIFICATION,
       TRIAL, APPEAL, POST_JUDGMENT */

    key_events UUID[],  -- References to timeline_events

    -- Metrics
    total_events INT DEFAULT 0,
    critical_events INT DEFAULT 0,
    communications_count INT DEFAULT 0,

    -- Legal Status
    custody_status TEXT,
    visitation_status TEXT,
    case_status TEXT,

    -- System
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_phases_dates ON timeline_phases(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_phases_current ON timeline_phases(is_current);
"""

# ============================================================================
# TABLE 6: DOCUMENT PROCESSING QUEUE
# ============================================================================

CREATE_PROCESSING_QUEUE_TABLE = """
CREATE TABLE IF NOT EXISTS document_processing_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Source
    source_type TEXT NOT NULL,
    /* TELEGRAM, WEB_UPLOAD, EMAIL, SCAN, API */

    source_identifier TEXT,  -- Telegram message ID, upload session, etc.

    -- File Info
    file_path TEXT NOT NULL,
    file_name TEXT,
    file_type TEXT,
    file_size_bytes BIGINT,

    -- Processing Request
    processing_type TEXT NOT NULL,
    /* TEXT_MESSAGE, EMAIL, COURT_DOC, POLICE_REPORT,
       SCREENSHOT, MEDICAL_RECORD, GENERIC */

    extract_events BOOLEAN DEFAULT TRUE,
    extract_communications BOOLEAN DEFAULT TRUE,
    extract_statements BOOLEAN DEFAULT TRUE,

    -- Status
    status TEXT DEFAULT 'pending',
    /* pending, processing, completed, failed, skipped */

    priority INT DEFAULT 5,  -- 1-10, 10 highest

    -- Processing Results
    events_created INT DEFAULT 0,
    communications_created INT DEFAULT 0,
    statements_created INT DEFAULT 0,
    errors TEXT[],

    -- Timing
    queued_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    processing_time_seconds INT,

    -- System
    processed_by TEXT
);

CREATE INDEX IF NOT EXISTS idx_queue_status ON document_processing_queue(status);
CREATE INDEX IF NOT EXISTS idx_queue_priority ON document_processing_queue(priority DESC, queued_at ASC);
"""

# ============================================================================
# PYTHON TYPE DEFINITIONS
# ============================================================================

from typing import TypedDict, List, Optional
from datetime import datetime, date, time

class TimelineEvent(TypedDict, total=False):
    """Type definition for timeline_events table"""
    id: str
    event_type: str
    event_subtype: Optional[str]
    event_date: datetime
    event_time: Optional[time]
    event_title: str
    event_description: Optional[str]
    event_location: Optional[str]
    primary_actor: Optional[str]
    primary_subject: Optional[str]
    participants: List[str]
    source_type: str
    source_document_id: Optional[str]
    source_file_path: Optional[str]
    source_page_number: Optional[int]
    communication_method: Optional[str]
    sender: Optional[str]
    recipients: List[str]
    message_preview: Optional[str]
    message_full_text: Optional[str]
    court_name: Optional[str]
    case_number: str
    judge_name: Optional[str]
    hearing_type: Optional[str]
    court_outcome: Optional[str]
    report_number: Optional[str]
    reporting_officer: Optional[str]
    incident_type: Optional[str]
    importance: int
    tags: List[str]
    keywords: List[str]
    related_events: List[str]
    contradicts_events: List[str]
    supports_events: List[str]
    parent_event_id: Optional[str]
    timeline_phase: Optional[str]
    days_since_detention: Optional[int]
    days_until_next_hearing: Optional[int]
    verified: bool
    verified_by: Optional[str]
    verified_date: Optional[datetime]
    is_evidence: bool
    evidence_category: Optional[str]
    legal_relevance: Optional[int]
    admissible: Optional[bool]
    created_at: datetime
    updated_at: datetime
    created_by: str

class Communication(TypedDict, total=False):
    """Type definition for communications table"""
    id: str
    event_id: Optional[str]
    comm_type: str
    comm_date: datetime
    comm_time: Optional[time]
    sender: str
    sender_phone: Optional[str]
    sender_email: Optional[str]
    recipients: List[str]
    recipients_phones: List[str]
    recipients_emails: List[str]
    cc: List[str]
    bcc: List[str]
    subject: Optional[str]
    message_body: Optional[str]
    message_length: Optional[int]
    attachment_count: Optional[int]
    attachments: dict
    sentiment: Optional[str]
    tone: Optional[str]
    keywords: List[str]
    contains_admission: bool
    contains_threat: bool
    contains_false_statement: bool
    contains_deadline: bool
    admission_text: List[str]
    threat_text: List[str]
    false_statement_text: List[str]
    deadline_mentioned: Optional[date]
    thread_id: Optional[str]
    in_reply_to: Optional[str]
    conversation_participants: List[str]
    source_platform: Optional[str]
    source_screenshot_path: Optional[str]
    source_document_id: Optional[str]
    importance: int
    tags: List[str]
    created_at: datetime
    updated_at: datetime

# ============================================================================
# HELPER QUERIES
# ============================================================================

COMMON_QUERIES = {
    "get_timeline": """
        SELECT * FROM timeline_events
        WHERE case_number = %s
        ORDER BY event_date DESC, event_time DESC
        LIMIT %s OFFSET %s
    """,

    "get_events_by_date_range": """
        SELECT * FROM timeline_events
        WHERE event_date BETWEEN %s AND %s
        AND case_number = %s
        ORDER BY event_date ASC
    """,

    "get_communications_by_sender": """
        SELECT * FROM communications
        WHERE sender = %s
        ORDER BY comm_date DESC
    """,

    "get_critical_events": """
        SELECT * FROM timeline_events
        WHERE importance >= 900
        AND case_number = %s
        ORDER BY importance DESC, event_date DESC
    """,

    "search_timeline": """
        SELECT * FROM timeline_events
        WHERE search_vector @@ to_tsquery('english', %s)
        ORDER BY event_date DESC
    """,

    "get_event_relationships": """
        SELECT
            e1.event_title as event_1,
            e2.event_title as event_2,
            r.relationship_type,
            r.relationship_strength,
            r.time_gap_days
        FROM event_relationships r
        JOIN timeline_events e1 ON r.event_1_id = e1.id
        JOIN timeline_events e2 ON r.event_2_id = e2.id
        WHERE e1.id = %s OR e2.id = %s
    """,

    "get_participant_activity": """
        SELECT
            event_type,
            COUNT(*) as count,
            MIN(event_date) as first_event,
            MAX(event_date) as last_event
        FROM timeline_events
        WHERE %s = ANY(participants)
        GROUP BY event_type
        ORDER BY count DESC
    """
}
