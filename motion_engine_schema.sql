-- ============================================================================
-- ASEAGI MOTION ENGINE & COMMUNICATIONS ANALYSIS SCHEMA
-- Complete schema for actionable legal document generation
-- For: In re Ashe B., J24-00478
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";  -- For pgvector (embeddings)

-- ============================================================================
-- PART 1: COURT DOCUMENTS REPOSITORY
-- ============================================================================

-- ============================================================================
-- Hearings Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS hearings (
    hearing_id BIGSERIAL PRIMARY KEY,

    -- Hearing details
    hearing_date DATE NOT NULL,
    hearing_time TIME,
    hearing_type TEXT NOT NULL,
    /* Types: 'detention', 'jurisdiction', 'disposition', 'review_6month',
              'review_12month', 'permanency', 'selection_implementation',
              'post_permanency', 'modification', 'termination' */

    department TEXT,
    courtroom TEXT,
    judge_name TEXT,

    -- Participants
    parties_present TEXT[],
    /* ['mother', 'father', 'child', 'social_worker'] */
    attorneys_present JSONB[],
    /*
    [
      {"role": "mother_attorney", "name": "Jane Smith", "bar_number": "12345"},
      {"role": "county_counsel", "name": "John Doe", "bar_number": "67890"}
    ]
    */

    -- Outcome
    outcome TEXT,
    /* 'continued', 'contested', 'submitted', 'orders_made' */
    continued_to DATE,
    continuation_reason TEXT,

    -- Links
    minute_order_id BIGINT,  -- Will reference minute_orders after it's created
    transcript_id BIGINT,    -- Will reference transcripts after it's created

    -- Notes
    hearing_notes TEXT,
    issues_addressed TEXT[],

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_hearings_date ON hearings(hearing_date);
CREATE INDEX idx_hearings_type ON hearings(hearing_type);
CREATE INDEX idx_hearings_judge ON hearings(judge_name);

COMMENT ON TABLE hearings IS 'All court hearings with participants, outcomes, and links to orders';

-- ============================================================================
-- Minute Orders Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS minute_orders (
    minute_order_id BIGSERIAL PRIMARY KEY,

    -- Link to hearing and document journal
    hearing_id BIGINT REFERENCES hearings(hearing_id) ON DELETE CASCADE,
    journal_id BIGINT REFERENCES document_journal(journal_id) ON DELETE CASCADE,

    -- Order details
    hearing_date DATE NOT NULL,
    judge_name TEXT,
    department TEXT,

    -- Orders and findings (structured)
    orders_made TEXT[],
    /* ['Child to remain in foster care', 'Services continued for mother'] */

    findings TEXT[],
    /* ['Mother made substantial progress', 'Father failed to comply'] */

    -- Next steps
    next_hearing_date DATE,
    next_hearing_type TEXT,

    -- Compliance tracking
    compliance_deadlines JSONB[],
    /*
    [
      {
        "party": "mother",
        "requirement": "Complete parenting classes",
        "deadline": "2024-03-01",
        "completed": false
      }
    ]
    */

    -- Full text
    full_text TEXT,

    -- Extracted data (AI analysis)
    extracted_data JSONB,
    /*
    {
      "key_orders": ["maintain placement", "services continued"],
      "violations_noted": ["father missed 3 visits"],
      "concerns_raised": ["child's behavior at school"]
    }
    */

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_minute_orders_hearing_date ON minute_orders(hearing_date);
CREATE INDEX idx_minute_orders_next_hearing ON minute_orders(next_hearing_date);
CREATE INDEX idx_minute_orders_judge ON minute_orders(judge_name);

COMMENT ON TABLE minute_orders IS 'Court minute orders with extracted findings and compliance tracking';

-- Add foreign key references now that both tables exist
ALTER TABLE hearings ADD CONSTRAINT fk_hearings_minute_order
    FOREIGN KEY (minute_order_id) REFERENCES minute_orders(minute_order_id) ON DELETE SET NULL;

-- ============================================================================
-- Findings and Orders Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS findings_and_orders (
    finding_id BIGSERIAL PRIMARY KEY,

    hearing_id BIGINT REFERENCES hearings(hearing_id) ON DELETE CASCADE,
    minute_order_id BIGINT REFERENCES minute_orders(minute_order_id) ON DELETE CASCADE,

    -- Type of finding
    finding_type TEXT NOT NULL,
    /* 'jurisdictional', 'dispositional', 'review', 'permanency', 'termination' */

    -- Finding details
    finding_text TEXT NOT NULL,
    legal_basis TEXT,
    /* 'WIC § 300(b)', 'WIC § 366.21(e)', etc. */

    finding_date DATE NOT NULL,

    -- Associated order
    order_text TEXT,
    order_type TEXT,
    /* 'custody', 'services', 'visitation', 'placement', 'case_plan' */

    -- Compliance
    compliance_required BOOLEAN DEFAULT FALSE,
    compliance_party TEXT,
    compliance_deadline DATE,
    compliance_status TEXT DEFAULT 'pending',
    /* 'pending', 'completed', 'partial', 'failed' */

    -- Appeal tracking
    appealed BOOLEAN DEFAULT FALSE,
    appeal_filed_date DATE,
    appeal_outcome TEXT,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_findings_type ON findings_and_orders(finding_type);
CREATE INDEX idx_findings_date ON findings_and_orders(finding_date);
CREATE INDEX idx_findings_compliance ON findings_and_orders(compliance_status);

COMMENT ON TABLE findings_and_orders IS 'Judicial findings and orders with compliance tracking';

-- ============================================================================
-- Transcripts Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS transcripts (
    transcript_id BIGSERIAL PRIMARY KEY,

    hearing_id BIGINT REFERENCES hearings(hearing_id) ON DELETE CASCADE,
    journal_id BIGINT REFERENCES document_journal(journal_id) ON DELETE CASCADE,

    transcript_date DATE NOT NULL,
    page_count INTEGER,

    -- Full text
    full_text TEXT,

    -- Speakers (extracted)
    speakers JSONB[],
    /*
    [
      {"speaker": "Judge", "line_count": 45, "key_statements": ["..."]},
      {"speaker": "County Counsel", "line_count": 32}
    ]
    */

    -- Key statements (AI extracted)
    key_statements JSONB[],
    /*
    [
      {
        "speaker": "Social Worker",
        "page": 12,
        "lines": "15-18",
        "statement": "Cal OES 2-925 was never verified",
        "significance": "high"
      }
    ]
    */

    -- Testimony tracking
    testimonies JSONB[],
    /*
    [
      {
        "witness": "Dr. Jane Smith",
        "testified_about": ["child's emotional state", "therapy progress"],
        "pages": "45-52"
      }
    ]
    */

    -- Embeddings for vector search
    embeddings_generated BOOLEAN DEFAULT FALSE,
    embedding_chunks INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_transcripts_date ON transcripts(transcript_date);
CREATE INDEX idx_transcripts_hearing ON transcripts(hearing_id);

-- Add foreign key reference
ALTER TABLE hearings ADD CONSTRAINT fk_hearings_transcript
    FOREIGN KEY (transcript_id) REFERENCES transcripts(transcript_id) ON DELETE SET NULL;

COMMENT ON TABLE transcripts IS 'Court transcripts with AI-extracted key statements';

-- ============================================================================
-- Exhibits Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS exhibits (
    exhibit_id BIGSERIAL PRIMARY KEY,

    -- Exhibit identification
    exhibit_number TEXT,
    exhibit_letter TEXT,
    full_exhibit_label TEXT,
    /* 'Exhibit A', 'Exhibit 1', 'Petitioner's Exhibit 3', etc. */

    -- Description
    exhibit_description TEXT NOT NULL,
    exhibit_type TEXT,
    /* 'photo', 'document', 'medical_record', 'police_report', 'communication',
       'video', 'audio', 'physical_evidence' */

    -- Source
    source_journal_id BIGINT REFERENCES document_journal(journal_id),
    source_file_path TEXT,

    -- Admission details
    admitted_at_hearing_id BIGINT REFERENCES hearings(hearing_id),
    admitted_date DATE,
    admitted_by TEXT,
    /* 'mother', 'father', 'county', 'minors_counsel' */

    admitted BOOLEAN DEFAULT FALSE,
    admission_objections TEXT[],

    -- Relevance
    relevance TEXT,
    relates_to_issue TEXT[],

    -- Metadata
    page_count INTEGER,
    file_size_bytes BIGINT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_exhibits_hearing ON exhibits(admitted_at_hearing_id);
CREATE INDEX idx_exhibits_type ON exhibits(exhibit_type);
CREATE INDEX idx_exhibits_admitted_by ON exhibits(admitted_by);

COMMENT ON TABLE exhibits IS 'Evidence exhibits catalogue with admission tracking';

-- ============================================================================
-- Police Reports Table (Structured)
-- ============================================================================

CREATE TABLE IF NOT EXISTS police_reports (
    police_report_id BIGSERIAL PRIMARY KEY,

    journal_id BIGINT REFERENCES document_journal(journal_id) ON DELETE CASCADE,

    -- Report identification
    report_number TEXT,
    agency TEXT,
    /* 'LAPD', 'Sheriff', 'CHP', etc. */

    -- Officer information
    officer_name TEXT,
    badge_number TEXT,
    supervisor_name TEXT,

    -- Incident details
    incident_date DATE,
    incident_time TIME,
    incident_location TEXT,
    incident_address TEXT,

    incident_type TEXT,
    /* 'domestic_violence', 'child_abuse', 'welfare_check', 'custody_dispute' */

    allegations TEXT[],
    /* ['physical abuse', 'neglect', 'endangerment'] */

    -- Investigation
    disposition TEXT,
    /* 'founded', 'unfounded', 'inconclusive', 'pending' */

    investigation_summary TEXT,

    -- Statements (structured)
    statements JSONB[],
    /*
    [
      {
        "speaker": "Officer Smith",
        "statement": "No signs of abuse observed",
        "timestamp": "2023-01-15 14:30"
      },
      {
        "speaker": "Father",
        "statement": "Child was injured by mother",
        "timestamp": "2023-01-15 14:45"
      }
    ]
    */

    -- Evidence
    evidence_collected TEXT[],
    photos_taken INTEGER DEFAULT 0,

    -- Follow-up
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_notes TEXT,
    referred_to_agency TEXT,
    /* 'CPS', 'DA', 'none' */

    case_status TEXT DEFAULT 'closed',
    /* 'open', 'closed', 'pending', 'referred' */

    -- Full report text
    full_report_text TEXT,

    -- Metadata
    report_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_police_reports_incident_date ON police_reports(incident_date);
CREATE INDEX idx_police_reports_disposition ON police_reports(disposition);
CREATE INDEX idx_police_reports_agency ON police_reports(agency);
CREATE INDEX idx_police_reports_report_number ON police_reports(report_number);

COMMENT ON TABLE police_reports IS 'Structured police report data with statements and disposition';

-- ============================================================================
-- Doctor's Notes Table (Structured)
-- ============================================================================

CREATE TABLE IF NOT EXISTS doctors_notes (
    doctors_note_id BIGSERIAL PRIMARY KEY,

    journal_id BIGINT REFERENCES document_journal(journal_id) ON DELETE CASCADE,

    -- Provider information
    provider_name TEXT NOT NULL,
    provider_specialty TEXT,
    facility TEXT,
    facility_address TEXT,

    -- Visit details
    visit_date DATE NOT NULL,
    visit_time TIME,
    visit_type TEXT,
    /* 'emergency', 'followup', 'consultation', 'physical_exam' */

    -- Patient
    patient_name TEXT,
    patient_dob DATE,

    -- Clinical information
    chief_complaint TEXT,
    presenting_problem TEXT,

    diagnosis TEXT,
    diagnosis_code TEXT,
    /* ICD-10 code */

    findings TEXT,
    examination_results TEXT,

    injuries_observed TEXT[],
    /* ['bruise on left arm', 'laceration on forehead'] */

    injury_details JSONB[],
    /*
    [
      {
        "injury": "bruise on left arm",
        "size": "2cm x 3cm",
        "age": "2-3 days old",
        "consistent_with": "accidental fall"
      }
    ]
    */

    -- Treatment
    treatment_provided TEXT,
    medications_prescribed TEXT[],
    procedures_performed TEXT[],

    -- Recommendations
    recommendations TEXT,
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    follow_up_instructions TEXT,

    -- Abuse assessment (if applicable)
    abuse_suspected BOOLEAN DEFAULT FALSE,
    abuse_reported BOOLEAN DEFAULT FALSE,
    reported_to_agency TEXT,
    /* 'CPS', 'police', 'none' */

    -- Full note text
    full_note_text TEXT,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_doctors_notes_visit_date ON doctors_notes(visit_date);
CREATE INDEX idx_doctors_notes_provider ON doctors_notes(provider_name);
CREATE INDEX idx_doctors_notes_diagnosis ON doctors_notes(diagnosis);
CREATE INDEX idx_doctors_notes_abuse_suspected ON doctors_notes(abuse_suspected);

COMMENT ON TABLE doctors_notes IS 'Structured medical records with injury and abuse tracking';

-- ============================================================================
-- PART 2: COMMUNICATIONS REPOSITORY
-- ============================================================================

-- ============================================================================
-- Communication Threads Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS communication_threads (
    thread_id BIGSERIAL PRIMARY KEY,

    -- Participants
    participants TEXT[] NOT NULL,
    /* ['Father', 'Mother'] */

    participant_phones TEXT[],
    participant_emails TEXT[],

    -- Thread metadata
    thread_subject TEXT,
    thread_topic TEXT,
    /* 'visitation', 'child_support', 'school', 'medical' */

    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    last_message_date TIMESTAMPTZ,

    message_count INTEGER DEFAULT 0,

    -- AI analysis
    thread_summary TEXT,
    /* AI-generated summary of entire thread */

    key_topics TEXT[],
    /* ['visitation denial', 'false allegations', 'manipulation'] */

    -- Truth analysis for entire thread
    thread_truthfulness_score DECIMAL(5,2),
    /* 0-100, average across all messages */

    deception_patterns JSONB[],
    /*
    [
      {
        "pattern": "gaslighting",
        "frequency": 5,
        "examples": [...]
      }
    ]
    */

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_threads_participants ON communication_threads USING GIN(participants);
CREATE INDEX idx_threads_start_date ON communication_threads(start_date);

COMMENT ON TABLE communication_threads IS 'Grouped conversations with truth analysis';

-- ============================================================================
-- Communications Table (Text Messages, Emails, Calls)
-- ============================================================================

CREATE TABLE IF NOT EXISTS communications (
    communication_id BIGSERIAL PRIMARY KEY,

    -- Type
    communication_type TEXT NOT NULL,
    /* 'sms', 'imessage', 'email', 'call', 'voicemail', 'whatsapp' */

    -- Timing
    sent_date TIMESTAMPTZ NOT NULL,
    received_date TIMESTAMPTZ,

    -- Participants
    sender TEXT NOT NULL,
    sender_phone TEXT,
    sender_email TEXT,
    sender_role TEXT,
    /* 'father', 'mother', 'social_worker', 'attorney', 'other' */

    recipient TEXT NOT NULL,
    recipient_phone TEXT,
    recipient_email TEXT,
    recipient_role TEXT,

    -- Content
    subject TEXT,
    /* For emails */

    content TEXT,
    /* Message text */

    attachments TEXT[],
    /* File paths or URLs to attachments */

    -- Thread
    thread_id BIGINT REFERENCES communication_threads(thread_id) ON DELETE CASCADE,
    in_reply_to BIGINT REFERENCES communications(communication_id),
    /* Links to message this is replying to */

    -- Context
    communication_context TEXT,
    /* 'regarding_visitation', 'regarding_court_order', 'regarding_child_welfare' */

    -- Truth/Lie Analysis
    analyzed BOOLEAN DEFAULT FALSE,
    analysis_date TIMESTAMPTZ,

    truthfulness_score DECIMAL(5,2),
    /* 0-100, how truthful is this message */

    contains_contradiction BOOLEAN DEFAULT FALSE,
    contradiction_details JSONB[],
    /*
    [
      {
        "contradicts_communication_id": 123,
        "contradicts_declaration_id": 456,
        "statement_here": "I never denied visitation",
        "contradictory_statement": "You can't see the child (2023-01-20)",
        "confidence": 0.95
      }
    ]
    */

    contains_manipulation BOOLEAN DEFAULT FALSE,
    manipulation_types TEXT[],
    /* ['gaslighting', 'coercion', 'false_promises', 'threats'] */

    -- Embeddings for vector search
    embedding VECTOR(1536),
    /* OpenAI text-embedding-ada-002 */

    -- Links to case documents
    related_declarations BIGINT[],
    /* journal_ids of declarations that mention this communication */

    related_violations BIGINT[],
    /* violation_ids this communication evidences */

    related_hearings BIGINT[],
    /* hearing_ids where this was discussed */

    -- Evidence tracking
    used_as_evidence BOOLEAN DEFAULT FALSE,
    exhibit_id BIGINT REFERENCES exhibits(exhibit_id),

    -- Source
    source_file TEXT,
    /* Path to original export file */

    source_format TEXT,
    /* 'iphone_json', 'android_xml', 'gmail_mbox', 'manual_entry' */

    imported_at TIMESTAMPTZ DEFAULT NOW(),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_communications_sent_date ON communications(sent_date);
CREATE INDEX idx_communications_sender ON communications(sender);
CREATE INDEX idx_communications_recipient ON communications(recipient);
CREATE INDEX idx_communications_type ON communications(communication_type);
CREATE INDEX idx_communications_truthfulness ON communications(truthfulness_score);
CREATE INDEX idx_communications_thread ON communications(thread_id);
CREATE INDEX idx_communications_contains_contradiction ON communications(contains_contradiction);

-- Vector index for similarity search
CREATE INDEX ON communications USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

COMMENT ON TABLE communications IS 'All communications with truth analysis and vector search';

-- ============================================================================
-- Communication Analysis Results Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS communication_analysis (
    analysis_id BIGSERIAL PRIMARY KEY,

    communication_id BIGINT REFERENCES communications(communication_id) ON DELETE CASCADE,

    -- Analysis type
    analysis_type TEXT NOT NULL,
    /* 'truth_detection', 'sentiment', 'manipulation', 'intent', 'emotion' */

    -- Analysis result
    analysis_result JSONB NOT NULL,
    /*
    For truth detection:
    {
      "truthfulness_score": 25.0,
      "likely_false": true,
      "reasons": ["contradicts text from 2023-01-20", "implausible timeline"],
      "contradicts": [
        {
          "type": "communication",
          "id": 456,
          "statement": "You can't see the child",
          "date": "2023-01-20"
        },
        {
          "type": "declaration",
          "journal_id": 789,
          "statement": "I always encouraged visitation",
          "date": "2023-02-01"
        }
      ]
    }

    For sentiment:
    {
      "sentiment": "hostile",
      "sentiment_score": -0.85,
      "emotions": ["anger", "contempt"],
      "tone": "aggressive"
    }

    For manipulation:
    {
      "manipulation_detected": true,
      "types": ["gaslighting", "guilt_tripping"],
      "severity": "high",
      "examples": [
        {
          "text": "You're imagining things again",
          "manipulation_type": "gaslighting"
        }
      ]
    }
    */

    confidence_score DECIMAL(5,2),
    /* 0-100, confidence in this analysis */

    -- AI model used
    ai_model_used TEXT,
    /* 'gpt-4', 'claude-3', 'custom_model' */

    analysis_version TEXT,
    /* Track which version of analysis logic was used */

    -- Metadata
    analyzed_at TIMESTAMPTZ DEFAULT NOW(),
    analysis_duration_seconds DECIMAL(8,2)
);

CREATE INDEX idx_comm_analysis_type ON communication_analysis(analysis_type);
CREATE INDEX idx_comm_analysis_comm_id ON communication_analysis(communication_id);

COMMENT ON TABLE communication_analysis IS 'Detailed analysis results for each communication';

-- ============================================================================
-- Contradiction Links Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS contradiction_links (
    contradiction_id BIGSERIAL PRIMARY KEY,

    -- What contradicts what
    communication_id BIGINT REFERENCES communications(communication_id) ON DELETE CASCADE,
    declaration_journal_id BIGINT REFERENCES document_journal(journal_id) ON DELETE CASCADE,

    -- The contradiction
    communication_statement TEXT NOT NULL,
    communication_date TIMESTAMPTZ NOT NULL,

    declaration_statement TEXT NOT NULL,
    declaration_date DATE NOT NULL,
    declaration_sworn BOOLEAN DEFAULT TRUE,

    -- Type of contradiction
    contradiction_type TEXT NOT NULL,
    /* 'direct' - directly contradictory statements
       'implied' - implied contradiction
       'omission' - failure to mention something material
       'timeline' - timeline doesn't match up
       'impossible' - logically impossible
    */

    -- Severity
    severity TEXT,
    /* 'minor', 'moderate', 'severe', 'perjury' */

    -- Confidence
    confidence_score DECIMAL(5,2),
    /* 0-100, how confident are we this is a real contradiction */

    -- Impact
    legal_impact TEXT,
    /* 'impeachment', 'perjury_charge', 'credibility', 'evidence_exclusion' */

    -- Notes
    explanation TEXT,
    analysis_notes TEXT,

    -- Verification
    verified_by_human BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMPTZ,
    verified_by TEXT,

    -- Usage
    used_in_motion_id BIGINT,
    /* references generated_motions(motion_id), will add FK later */

    -- Metadata
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    detection_method TEXT,
    /* 'ai_auto', 'ai_assisted', 'manual' */

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_contradiction_comm_id ON contradiction_links(communication_id);
CREATE INDEX idx_contradiction_decl_id ON contradiction_links(declaration_journal_id);
CREATE INDEX idx_contradiction_severity ON contradiction_links(severity);
CREATE INDEX idx_contradiction_verified ON contradiction_links(verified_by_human);

COMMENT ON TABLE contradiction_links IS 'Links between contradictory communications and sworn statements';

-- ============================================================================
-- PART 3: ACTION ITEMS & MOTION GENERATION
-- ============================================================================

-- ============================================================================
-- Motion Templates Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS motion_templates (
    template_id BIGSERIAL PRIMARY KEY,

    -- Motion type (unique identifier)
    motion_type TEXT NOT NULL UNIQUE,
    /*
    'motion_for_reconsideration'
    'motion_to_dismiss'
    'motion_to_vacate'
    'motion_to_quash'
    'request_for_judicial_notice'
    'motion_for_sanctions'
    'motion_to_strike'
    'motion_to_compel_discovery'
    'declaration_in_support'
    'request_for_law_enforcement_records'
    */

    -- Display name
    motion_name TEXT NOT NULL,

    -- Court type
    court_type TEXT,
    /* 'juvenile_dependency', 'family', 'civil', 'criminal' */

    -- Template content (Jinja2 template)
    template_content TEXT,
    /*
    Contains placeholders like:
    {{ case_name }}
    {{ case_number }}
    {{ judge_name }}
    {{ factual_background }}
    {{ legal_argument }}
    {{ exhibits }}
    {{ proposed_order }}
    */

    -- Required fields
    required_fields JSONB,
    /*
    {
      "case_name": {"type": "string", "required": true},
      "case_number": {"type": "string", "required": true},
      "grounds": {"type": "text", "required": true},
      "relief_requested": {"type": "text", "required": true}
    }
    */

    -- Default legal authority
    default_legal_authority TEXT[],
    /* ['Cal Rules of Court § 1008', 'WIC § 827'] */

    default_case_law BIGINT[],
    /* citation_ids from case_law_citations table */

    -- Instructions for filling out
    instructions TEXT,

    -- Version tracking
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT,
    last_modified_by TEXT
);

CREATE INDEX idx_motion_templates_type ON motion_templates(motion_type);
CREATE INDEX idx_motion_templates_court_type ON motion_templates(court_type);
CREATE INDEX idx_motion_templates_active ON motion_templates(is_active);

COMMENT ON TABLE motion_templates IS 'Templates for generating legal motions and declarations';

-- ============================================================================
-- Action Items Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS action_items (
    action_id BIGSERIAL PRIMARY KEY,

    -- Action type
    action_type TEXT NOT NULL,
    /*
    'file_motion'
    'respond_to_filing'
    'compliance_deadline'
    'prepare_for_hearing'
    'submit_evidence'
    'request_records'
    'appeal_deadline'
    */

    -- Details
    title TEXT NOT NULL,
    description TEXT,

    -- Timeline
    due_date DATE,
    due_time TIME,
    priority TEXT DEFAULT 'medium',
    /* 'urgent', 'high', 'medium', 'low' */

    -- Status
    status TEXT DEFAULT 'pending',
    /* 'pending', 'in_progress', 'completed', 'cancelled', 'overdue' */

    -- What triggered this action
    triggered_by_violation_id BIGINT REFERENCES violations(violation_id) ON DELETE SET NULL,
    triggered_by_minute_order_id BIGINT REFERENCES minute_orders(minute_order_id) ON DELETE SET NULL,
    triggered_by_hearing_id BIGINT REFERENCES hearings(hearing_id) ON DELETE SET NULL,
    triggered_by_finding_id BIGINT REFERENCES findings_and_orders(finding_id) ON DELETE SET NULL,

    trigger_type TEXT,
    /* 'violation_detected', 'court_order', 'deadline', 'manual' */

    -- Suggested response
    suggested_motion_type TEXT,
    /* references motion_templates.motion_type */

    suggested_evidence BIGINT[],
    /* exhibit_ids, communication_ids, etc. */

    -- Completion tracking
    completed_at TIMESTAMPTZ,
    completed_by TEXT,
    completed_motion_id BIGINT,
    /* references generated_motions(motion_id), will add FK later */

    completion_notes TEXT,

    -- Reminder
    reminder_sent BOOLEAN DEFAULT FALSE,
    reminder_date DATE,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT
);

CREATE INDEX idx_action_items_due_date ON action_items(due_date);
CREATE INDEX idx_action_items_status ON action_items(status);
CREATE INDEX idx_action_items_priority ON action_items(priority);
CREATE INDEX idx_action_items_type ON action_items(action_type);

COMMENT ON TABLE action_items IS 'Action items triggered by violations, orders, or deadlines';

-- ============================================================================
-- Generated Motions Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS generated_motions (
    motion_id BIGSERIAL PRIMARY KEY,

    -- Template used
    template_id BIGINT REFERENCES motion_templates(template_id) ON DELETE SET NULL,
    action_item_id BIGINT REFERENCES action_items(action_id) ON DELETE SET NULL,

    -- Motion details
    motion_type TEXT NOT NULL,
    motion_title TEXT NOT NULL,

    -- Case information
    case_name TEXT,
    case_number TEXT,
    court_name TEXT,
    department TEXT,
    judge_name TEXT,

    -- Generated content sections
    caption TEXT,
    notice_of_motion TEXT,
    memorandum_of_points_and_authorities TEXT,
    statement_of_facts TEXT,
    legal_argument TEXT,
    declaration TEXT,
    proposed_order TEXT,
    certificate_of_service TEXT,

    -- Evidence attached
    exhibits_attached BIGINT[],
    /* exhibit_ids */

    communications_attached BIGINT[],
    /* communication_ids */

    transcripts_attached BIGINT[],
    /* transcript_ids */

    -- Legal citations used
    case_law_cited BIGINT[],
    /* citation_ids from case_law_citations table */

    legal_codes_cited BIGINT[],
    /* code_ids from legal_codes table */

    -- Violations addressed
    violations_addressed BIGINT[],
    /* violation_ids */

    contradictions_used BIGINT[],
    /* contradiction_ids */

    -- Generated files
    pdf_path TEXT,
    docx_path TEXT,
    file_size_bytes BIGINT,

    -- Metadata about generation
    generation_method TEXT DEFAULT 'ai_assisted',
    /* 'ai_full', 'ai_assisted', 'manual', 'template_only' */

    ai_model_used TEXT,
    /* 'gpt-4', 'claude-3-opus', etc. */

    generation_time_seconds DECIMAL(8,2),
    generation_cost_usd DECIMAL(8,4),

    prompt_used TEXT,
    /* The prompt given to AI */

    -- Status
    status TEXT DEFAULT 'draft',
    /* 'draft', 'review', 'ready_to_file', 'filed', 'served' */

    -- Review
    reviewed_by TEXT,
    reviewed_at TIMESTAMPTZ,
    review_notes TEXT,
    changes_requested TEXT[],

    -- Filing
    filed_date DATE,
    filed_time TIME,
    filing_method TEXT,
    /* 'efiling', 'in_person', 'mail' */

    filing_confirmation TEXT,
    filing_receipt_path TEXT,

    -- Hearing
    hearing_date DATE,
    hearing_result TEXT,
    order_after_hearing TEXT,

    successful BOOLEAN,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT
);

CREATE INDEX idx_generated_motions_type ON generated_motions(motion_type);
CREATE INDEX idx_generated_motions_status ON generated_motions(status);
CREATE INDEX idx_generated_motions_filed_date ON generated_motions(filed_date);
CREATE INDEX idx_generated_motions_hearing_date ON generated_motions(hearing_date);

COMMENT ON TABLE generated_motions IS 'AI-generated legal motions with evidence and citations';

-- Add foreign key references now
ALTER TABLE action_items ADD CONSTRAINT fk_action_items_completed_motion
    FOREIGN KEY (completed_motion_id) REFERENCES generated_motions(motion_id) ON DELETE SET NULL;

ALTER TABLE contradiction_links ADD CONSTRAINT fk_contradiction_used_in_motion
    FOREIGN KEY (used_in_motion_id) REFERENCES generated_motions(motion_id) ON DELETE SET NULL;

-- ============================================================================
-- Motion Evidence Links Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS motion_evidence_links (
    link_id BIGSERIAL PRIMARY KEY,

    motion_id BIGINT REFERENCES generated_motions(motion_id) ON DELETE CASCADE,

    -- Evidence type and ID
    evidence_type TEXT NOT NULL,
    /*
    'exhibit', 'communication', 'transcript', 'minute_order', 'police_report',
    'doctors_note', 'violation', 'contradiction', 'case_law', 'legal_code'
    */

    evidence_id BIGINT NOT NULL,
    /* ID from the relevant table */

    evidence_table TEXT NOT NULL,
    /* Table name for reference */

    -- Labeling
    exhibit_label TEXT,
    /* 'Exhibit A', 'Exhibit 1', 'Petitioner's Exhibit 3' */

    exhibit_order INTEGER,
    /* Order in which exhibits are attached */

    -- Relevance
    relevance TEXT,
    /* Why this evidence supports the motion */

    cited_in_section TEXT,
    /* 'statement_of_facts', 'legal_argument', 'declaration' */

    page_references TEXT,
    /* 'pp. 3-5', 'lines 12-18', 'para. 4' */

    -- Metadata
    added_at TIMESTAMPTZ DEFAULT NOW(),
    added_by TEXT
);

CREATE INDEX idx_motion_evidence_motion_id ON motion_evidence_links(motion_id);
CREATE INDEX idx_motion_evidence_type ON motion_evidence_links(evidence_type);
CREATE INDEX idx_motion_evidence_order ON motion_evidence_links(exhibit_order);

COMMENT ON TABLE motion_evidence_links IS 'Links between motions and supporting evidence';

-- ============================================================================
-- Filing History Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS filing_history (
    filing_id BIGSERIAL PRIMARY KEY,

    motion_id BIGINT REFERENCES generated_motions(motion_id) ON DELETE CASCADE,

    -- Filing details
    filed_date DATE NOT NULL,
    filed_time TIME,
    filed_by TEXT,

    filing_method TEXT NOT NULL,
    /* 'efiling', 'in_person', 'mail', 'fax' */

    filing_confirmation TEXT,
    filing_receipt_path TEXT,

    -- Service
    served_date DATE,
    service_method TEXT,
    /* 'personal', 'mail', 'email', 'fax' */

    parties_served TEXT[],
    proof_of_service_path TEXT,

    -- Hearing
    hearing_scheduled BOOLEAN DEFAULT FALSE,
    hearing_date DATE,
    hearing_time TIME,
    hearing_department TEXT,

    -- Outcome
    hearing_held BOOLEAN DEFAULT FALSE,
    hearing_result TEXT,
    /* 'granted', 'denied', 'continued', 'taken_under_submission' */

    order_after_hearing_path TEXT,
    order_favorable BOOLEAN,

    -- Appeal
    appealed BOOLEAN DEFAULT FALSE,
    appeal_filed_date DATE,

    -- Notes
    filing_notes TEXT,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_filing_history_motion_id ON filing_history(motion_id);
CREATE INDEX idx_filing_history_filed_date ON filing_history(filed_date);
CREATE INDEX idx_filing_history_hearing_date ON filing_history(hearing_date);

COMMENT ON TABLE filing_history IS 'Complete filing history with outcomes';

-- ============================================================================
-- VIEWS FOR MOTION ENGINE
-- ============================================================================

-- View: Pending Action Items
CREATE OR REPLACE VIEW pending_action_items AS
SELECT
    ai.action_id,
    ai.title,
    ai.description,
    ai.due_date,
    ai.priority,
    ai.suggested_motion_type,
    CASE
        WHEN ai.due_date < CURRENT_DATE THEN 'overdue'
        WHEN ai.due_date = CURRENT_DATE THEN 'due_today'
        WHEN ai.due_date <= CURRENT_DATE + INTERVAL '7 days' THEN 'due_soon'
        ELSE 'upcoming'
    END as urgency,
    mt.motion_name as suggested_motion_name
FROM action_items ai
LEFT JOIN motion_templates mt ON ai.suggested_motion_type = mt.motion_type
WHERE ai.status IN ('pending', 'in_progress')
ORDER BY ai.due_date ASC, ai.priority DESC;

-- View: Motion Dashboard
CREATE OR REPLACE VIEW motion_dashboard AS
SELECT
    gm.motion_id,
    gm.motion_title,
    gm.motion_type,
    gm.status,
    gm.filed_date,
    gm.hearing_date,
    gm.created_at,
    ARRAY_LENGTH(gm.exhibits_attached, 1) as exhibits_count,
    ARRAY_LENGTH(gm.case_law_cited, 1) as citations_count,
    ARRAY_LENGTH(gm.violations_addressed, 1) as violations_count,
    ai.title as action_item_title
FROM generated_motions gm
LEFT JOIN action_items ai ON gm.action_item_id = ai.action_id
ORDER BY gm.created_at DESC;

-- View: Communication Search Helper
CREATE OR REPLACE VIEW searchable_communications AS
SELECT
    c.communication_id,
    c.communication_type,
    c.sent_date,
    c.sender,
    c.sender_role,
    c.recipient,
    c.recipient_role,
    c.content,
    c.truthfulness_score,
    c.contains_contradiction,
    c.contains_manipulation,
    ARRAY_LENGTH(c.contradiction_details, 1) as contradiction_count
FROM communications c
WHERE c.content IS NOT NULL
ORDER BY c.sent_date DESC;

-- View: Court Calendar
CREATE OR REPLACE VIEW court_calendar AS
SELECT
    'hearing' as event_type,
    h.hearing_id as event_id,
    h.hearing_date as event_date,
    h.hearing_time as event_time,
    h.hearing_type as event_description,
    h.judge_name,
    h.department
FROM hearings h
WHERE h.hearing_date >= CURRENT_DATE
UNION ALL
SELECT
    'filing_deadline' as event_type,
    ai.action_id as event_id,
    ai.due_date as event_date,
    ai.due_time as event_time,
    ai.title as event_description,
    NULL as judge_name,
    NULL as department
FROM action_items ai
WHERE ai.due_date >= CURRENT_DATE
  AND ai.status IN ('pending', 'in_progress')
ORDER BY event_date ASC, event_time ASC;

-- View: Evidence Inventory
CREATE OR REPLACE VIEW evidence_inventory AS
SELECT
    'exhibit' as evidence_type,
    e.exhibit_id as evidence_id,
    e.full_exhibit_label as label,
    e.exhibit_description as description,
    e.admitted_date as date,
    e.admitted_at_hearing_id as hearing_id
FROM exhibits e
UNION ALL
SELECT
    'communication' as evidence_type,
    c.communication_id as evidence_id,
    c.communication_type as label,
    LEFT(c.content, 100) as description,
    c.sent_date::date as date,
    NULL as hearing_id
FROM communications c
WHERE c.used_as_evidence = TRUE
UNION ALL
SELECT
    'transcript' as evidence_type,
    t.transcript_id as evidence_id,
    'Transcript' as label,
    'Hearing transcript - ' || t.page_count || ' pages' as description,
    t.transcript_date as date,
    t.hearing_id
FROM transcripts t
ORDER BY date DESC;

-- View: Contradiction Summary
CREATE OR REPLACE VIEW contradiction_summary AS
SELECT
    cl.contradiction_id,
    cl.communication_date,
    cl.communication_statement,
    cl.declaration_date,
    cl.declaration_statement,
    cl.contradiction_type,
    cl.severity,
    cl.confidence_score,
    c.sender as who_contradicted,
    cl.used_in_motion_id IS NOT NULL as used_in_motion
FROM contradiction_links cl
JOIN communications c ON cl.communication_id = c.communication_id
ORDER BY cl.severity DESC, cl.confidence_score DESC;

-- ============================================================================
-- FUNCTIONS FOR MOTION ENGINE
-- ============================================================================

-- Function to create action item from violation
CREATE OR REPLACE FUNCTION create_action_from_violation(
    p_violation_id BIGINT,
    p_suggested_motion_type TEXT,
    p_due_date DATE
)
RETURNS BIGINT AS $$
DECLARE
    v_action_id BIGINT;
    v_violation violations%ROWTYPE;
BEGIN
    -- Get violation details
    SELECT * INTO v_violation FROM violations WHERE violation_id = p_violation_id;

    -- Create action item
    INSERT INTO action_items (
        action_type,
        title,
        description,
        due_date,
        priority,
        triggered_by_violation_id,
        trigger_type,
        suggested_motion_type
    ) VALUES (
        'file_motion',
        'File motion addressing ' || v_violation.violation_type,
        'Violation detected: ' || v_violation.violation_description,
        p_due_date,
        CASE
            WHEN v_violation.violation_severity = 'severe' THEN 'urgent'
            WHEN v_violation.violation_severity = 'moderate' THEN 'high'
            ELSE 'medium'
        END,
        p_violation_id,
        'violation_detected',
        p_suggested_motion_type
    )
    RETURNING action_id INTO v_action_id;

    RETURN v_action_id;
END;
$$ LANGUAGE plpgsql;

-- Function to create action item from minute order deadline
CREATE OR REPLACE FUNCTION create_action_from_minute_order_deadline(
    p_minute_order_id BIGINT,
    p_deadline JSONB
)
RETURNS BIGINT AS $$
DECLARE
    v_action_id BIGINT;
BEGIN
    INSERT INTO action_items (
        action_type,
        title,
        description,
        due_date,
        priority,
        triggered_by_minute_order_id,
        trigger_type
    ) VALUES (
        'compliance_deadline',
        'Comply with court order: ' || (p_deadline->>'requirement'),
        'Party: ' || (p_deadline->>'party') || ' - Requirement: ' || (p_deadline->>'requirement'),
        (p_deadline->>'deadline')::DATE,
        'high',
        p_minute_order_id,
        'court_order'
    )
    RETURNING action_id INTO v_action_id;

    RETURN v_action_id;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-create action items from minute orders
CREATE OR REPLACE FUNCTION auto_create_actions_from_minute_orders()
RETURNS TRIGGER AS $$
DECLARE
    deadline_item JSONB;
BEGIN
    -- For each compliance deadline in the minute order
    IF NEW.compliance_deadlines IS NOT NULL THEN
        FOR deadline_item IN SELECT * FROM jsonb_array_elements(NEW.compliance_deadlines)
        LOOP
            PERFORM create_action_from_minute_order_deadline(NEW.minute_order_id, deadline_item);
        END LOOP;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auto_create_actions
    AFTER INSERT ON minute_orders
    FOR EACH ROW
    EXECUTE FUNCTION auto_create_actions_from_minute_orders();

-- ============================================================================
-- SAMPLE DATA (Motion Templates)
-- ============================================================================

-- Insert default motion templates
INSERT INTO motion_templates (motion_type, motion_name, court_type, instructions, default_legal_authority) VALUES
(
    'motion_for_reconsideration',
    'Motion for Reconsideration',
    'juvenile_dependency',
    'Use when new facts or law warrant reconsideration of a prior ruling',
    ARRAY['Cal Rules of Court, rule 5.570(e)', 'Cal Rules of Court, rule 1008', 'Code Civ. Proc. § 1008']
),
(
    'request_for_judicial_notice',
    'Request for Judicial Notice',
    'juvenile_dependency',
    'Request court to take notice of official records, court files, or other judicially noticeable facts',
    ARRAY['Evid. Code § 452', 'Evid. Code § 453', 'Evid. Code § 459']
),
(
    'request_for_law_enforcement_records',
    'Request for Law Enforcement Records',
    'juvenile_dependency',
    'Request law enforcement records including 911 calls, CAD reports, body cam footage, etc.',
    ARRAY['Welf. & Inst. Code § 827', 'Cal Rules of Court, rule 5.552']
),
(
    'motion_to_dismiss',
    'Motion to Dismiss',
    'juvenile_dependency',
    'Motion to dismiss the dependency case for lack of evidence or other grounds',
    ARRAY['Welf. & Inst. Code § 390', 'In re N.M. (2011) 197 Cal.App.4th 159']
);

-- ============================================================================
-- SUMMARY
-- ============================================================================

COMMENT ON SCHEMA public IS 'ASEAGI Motion Engine & Communications Analysis System';

-- For Ashe. For Justice. For All Children. 🛡️
