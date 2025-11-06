-- ============================================================================
-- ASEAGI TIERED ANALYSIS SCHEMA
-- Multi-tier legal document analysis system
-- For: In re Ashe B., J24-00478
-- ============================================================================
--
-- ARCHITECTURE:
--
-- TIER 1: MICRO ANALYSIS (per document)
--   → Extract critical statements, data, fields from individual documents
--   → Cannot determine relevancy yet (no context)
--   → Examples: Extract officer name from police report, claims from declaration
--
-- TIER 2: MACRO ANALYSIS (cross-document)
--   → Cross-reference micro analysis results
--   → Compare statements across documents (consistency checks)
--   → Example: Declaration claims X, but police report says Y
--   → Example: Ex parte filing contradicts evidence
--
-- TIER 3: VIOLATION ANALYSIS
--   → Detect legal violations using macro results
--   → Perjury, negligence, protective order violations, child endangerment
--
-- TIER 4: CASE LAW & CITATIONS
--   → Relevant precedent cases
--   → Legal codes (Family Code, Penal Code, Welfare & Institutions Code)
--   → Attached to events/statements
--
-- TIER 5: EVENT TIMELINE & PROFILES
--   → Comprehensive timeline across 2-3 years
--   → Connect statements/events across documents
--   → Build profiles for all parties
--
-- TIER 6: JUDICIAL ASSESSMENT
--   → Final synthesis: violations + case law + macro + patterns
--   → Produces final assessment report
--
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TIER 1: MICRO ANALYSIS (Per Document)
-- ============================================================================

CREATE TABLE IF NOT EXISTS micro_analysis (
    micro_id BIGSERIAL PRIMARY KEY,

    -- Link to document journal
    journal_id BIGINT REFERENCES document_journal(journal_id) ON DELETE CASCADE,

    -- Document metadata
    document_type TEXT NOT NULL,
    document_date DATE,
    document_title TEXT,
    document_author TEXT,
    filing_party TEXT,  -- Who filed this document

    -- Extracted critical information (document-specific)
    critical_statements JSONB,
    /*
    Structure depends on document type:

    Police Report:
    {
      "officer_name": "John Smith",
      "badge_number": "12345",
      "incident_date": "2023-01-15",
      "incident_time": "14:30",
      "location": "123 Main St",
      "statements": [
        {"speaker": "Officer Smith", "statement": "..."},
        {"speaker": "Jane Doe", "statement": "..."}
      ],
      "allegations": ["abuse", "neglect"],
      "disposition": "unfounded"
    }

    Medical Report:
    {
      "doctor_name": "Dr. Jane Smith",
      "facility": "General Hospital",
      "visit_date": "2023-01-16",
      "diagnosis": "No injuries observed",
      "findings": "Child appears healthy",
      "recommendations": "Follow up in 2 weeks"
    }

    Court Declaration:
    {
      "declarant": "John Doe",
      "declarant_role": "father",
      "sworn_date": "2023-02-01",
      "claims": [
        {"claim": "Mother denied visitation", "date": "2023-01-20"},
        {"claim": "Child was injured", "date": "2023-01-15"}
      ]
    }

    Ex Parte:
    {
      "filing_date": "2023-02-05",
      "requested_orders": ["emergency custody", "no visitation"],
      "justification": "immediate danger",
      "evidence_cited": ["police report", "medical report"]
    }
    */

    -- Key entities extracted (people, agencies, locations)
    entities JSONB,
    /*
    {
      "people": [
        {"name": "John Doe", "role": "father"},
        {"name": "Jane Doe", "role": "mother"}
      ],
      "agencies": [
        {"name": "CPS", "case_number": "12345"}
      ],
      "locations": [
        {"address": "123 Main St", "type": "incident_location"}
      ]
    }
    */

    -- Key dates mentioned
    dates_mentioned JSONB,
    /*
    {
      "incident_dates": ["2023-01-15", "2023-01-20"],
      "court_dates": ["2023-02-05"],
      "deadline_dates": ["2023-03-01"]
    }
    */

    -- Claims/allegations made in this document
    claims JSONB[],
    /*
    [
      {
        "claim": "Mother denied visitation",
        "made_by": "John Doe",
        "date_of_claim": "2023-02-01",
        "regarding_date": "2023-01-20",
        "severity": "moderate"
      }
    ]
    */

    -- Facts stated (vs claims/allegations)
    facts JSONB[],
    /*
    [
      {
        "fact": "Child attended school on 2023-01-15",
        "source": "school records",
        "verifiable": true
      }
    ]
    */

    -- Metrics
    extraction_confidence DECIMAL(5,2),  -- 0-100
    num_statements INTEGER DEFAULT 0,
    num_claims INTEGER DEFAULT 0,
    num_facts INTEGER DEFAULT 0,
    num_entities INTEGER DEFAULT 0,

    -- Processing metadata
    analyzed_at TIMESTAMPTZ DEFAULT NOW(),
    analysis_method TEXT,  -- 'ai', 'ocr', 'manual'
    ai_model_used TEXT,
    analysis_duration_seconds DECIMAL(8,2),
    analysis_cost_usd DECIMAL(8,4),

    -- Flags for next-tier processing
    ready_for_macro_analysis BOOLEAN DEFAULT TRUE,
    needs_manual_review BOOLEAN DEFAULT FALSE,
    manual_review_reason TEXT,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_micro_analysis_journal_id ON micro_analysis(journal_id);
CREATE INDEX idx_micro_analysis_document_type ON micro_analysis(document_type);
CREATE INDEX idx_micro_analysis_ready_for_macro ON micro_analysis(ready_for_macro_analysis);
CREATE INDEX idx_micro_analysis_document_date ON micro_analysis(document_date);

-- ============================================================================
-- TIER 2: MACRO ANALYSIS (Cross-Document)
-- ============================================================================

CREATE TABLE IF NOT EXISTS macro_analysis (
    macro_id BIGSERIAL PRIMARY KEY,

    -- Analysis metadata
    analysis_name TEXT NOT NULL,
    analysis_type TEXT NOT NULL,  -- 'consistency_check', 'cross_reference', 'timeline_verification'
    analysis_description TEXT,

    -- Documents involved (array of journal_ids)
    documents_analyzed BIGINT[],

    -- Micro analysis records involved
    micro_analyses_involved BIGINT[],

    -- Analysis results
    findings JSONB,
    /*
    Consistency Check Example:
    {
      "type": "statement_contradiction",
      "documents": [
        {"journal_id": 123, "document_type": "declaration", "party": "father"},
        {"journal_id": 456, "document_type": "police_report", "party": "police"}
      ],
      "contradiction": {
        "statement_1": "Child was injured on 2023-01-15",
        "statement_2": "No injuries observed on 2023-01-15",
        "severity": "high",
        "explanation": "Father claims injury, but police report shows no injuries"
      }
    }

    Ex Parte Verification Example:
    {
      "type": "ex_parte_verification",
      "ex_parte_journal_id": 789,
      "claims_made": [
        {"claim": "immediate danger", "supported": false, "evidence": "none"},
        {"claim": "denied visitation", "supported": true, "evidence": ["text messages"]}
      ],
      "fraudulent_filing_likelihood": 0.85,
      "reasons": ["no evidence of immediate danger", "contradicts prior court orders"]
    }
    */

    -- Consistency scores
    consistency_score DECIMAL(5,2),  -- 0-100 (100 = fully consistent)
    reliability_score DECIMAL(5,2),  -- 0-100 (how reliable are the findings)

    -- Cross-references found
    cross_references JSONB[],
    /*
    [
      {
        "reference_type": "supporting",
        "doc1_journal_id": 123,
        "doc2_journal_id": 456,
        "statement": "Child was at school",
        "verified": true
      },
      {
        "reference_type": "contradicting",
        "doc1_journal_id": 123,
        "doc2_journal_id": 789,
        "statement_1": "Mother denied access",
        "statement_2": "Father did not attempt contact",
        "verified": false
      }
    ]
    */

    -- Patterns detected
    patterns JSONB[],
    /*
    [
      {
        "pattern_type": "repeated_false_allegations",
        "occurrences": 5,
        "date_range": {"start": "2022-01-01", "end": "2024-01-01"},
        "pattern_description": "Father repeatedly makes allegations that are not supported by evidence"
      }
    ]
    */

    -- Legal relevancy (now we have context!)
    legal_relevancy_score DECIMAL(5,2),  -- 0-100
    relevancy_reasoning TEXT,

    -- Processing metadata
    analyzed_at TIMESTAMPTZ DEFAULT NOW(),
    analysis_method TEXT,
    ai_model_used TEXT,
    analysis_duration_seconds DECIMAL(8,2),
    analysis_cost_usd DECIMAL(8,4),

    -- Flags for next-tier processing
    ready_for_violation_analysis BOOLEAN DEFAULT TRUE,
    potential_violations_detected BOOLEAN DEFAULT FALSE,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_macro_analysis_type ON macro_analysis(analysis_type);
CREATE INDEX idx_macro_analysis_ready_for_violations ON macro_analysis(ready_for_violation_analysis);
CREATE INDEX idx_macro_analysis_potential_violations ON macro_analysis(potential_violations_detected);

-- ============================================================================
-- TIER 3: VIOLATION ANALYSIS
-- ============================================================================

CREATE TABLE IF NOT EXISTS violations (
    violation_id BIGSERIAL PRIMARY KEY,

    -- Link to macro analysis that detected this
    macro_analysis_id BIGINT REFERENCES macro_analysis(macro_id) ON DELETE CASCADE,

    -- Violation details
    violation_type TEXT NOT NULL,
    /* Types:
       - 'perjury' (false statements under oath)
       - 'fraud_upon_court' (ex parte filings with false info)
       - 'protective_order_violation'
       - 'child_endangerment'
       - 'negligence' (failure to act)
       - 'contempt_of_court'
       - 'false_allegations'
       - 'parental_alienation'
       - 'witness_tampering'
    */

    violation_severity TEXT,  -- 'minor', 'moderate', 'severe', 'criminal'

    -- Who committed the violation
    violator_name TEXT,
    violator_role TEXT,  -- 'parent', 'attorney', 'social_worker', 'agency', 'court_official'

    -- When it occurred
    violation_date DATE,
    violation_date_range DATERANGE,  -- If ongoing

    -- What was violated
    violated_law_or_order TEXT,
    /* Examples:
       - "California Penal Code § 118 (Perjury)"
       - "Court Order dated 2023-01-15"
       - "California Family Code § 3011"
       - "Restraining Order Case #12345"
    */

    -- Evidence of violation
    evidence_documents BIGINT[],  -- journal_ids
    evidence_micro_analyses BIGINT[],  -- micro_ids
    evidence_macro_analyses BIGINT[],  -- macro_ids

    -- Detailed description
    violation_description TEXT,

    -- Specific false statements (for perjury)
    false_statements JSONB[],
    /*
    [
      {
        "statement": "Mother denied all visitation",
        "document_journal_id": 123,
        "date_made": "2023-02-01",
        "sworn": true,
        "truth": "Mother offered visitation, father declined",
        "evidence_journal_ids": [456, 789],
        "provably_false": true
      }
    ]
    */

    -- Confidence in violation detection
    confidence_score DECIMAL(5,2),  -- 0-100
    confidence_reasoning TEXT,

    -- Legal impact
    legal_impact TEXT,  -- 'affects_custody', 'criminal_charges', 'sanctions', 'contempt'
    recommended_action TEXT,

    -- Status
    violation_status TEXT DEFAULT 'detected',
    /* Status workflow:
       detected → reviewed → confirmed → reported → resolved
    */

    reviewed_by TEXT,
    reviewed_at TIMESTAMPTZ,
    review_notes TEXT,

    -- Processing metadata
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    detection_method TEXT,
    ai_model_used TEXT,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_violations_type ON violations(violation_type);
CREATE INDEX idx_violations_severity ON violations(violation_severity);
CREATE INDEX idx_violations_violator ON violations(violator_name);
CREATE INDEX idx_violations_status ON violations(violation_status);
CREATE INDEX idx_violations_date ON violations(violation_date);

-- ============================================================================
-- TIER 4: CASE LAW & LEGAL CITATIONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS case_law_citations (
    citation_id BIGSERIAL PRIMARY KEY,

    -- Case information
    case_name TEXT NOT NULL,
    case_citation TEXT,  -- e.g., "In re Marriage of Smith, 123 Cal.App.4th 456 (2004)"
    court TEXT,  -- 'California Supreme Court', 'Court of Appeal', 'Superior Court'
    year INTEGER,

    -- Legal principle established
    legal_principle TEXT,
    holding TEXT,  -- What the court decided

    -- Relevance to this case
    relevance_to_case TEXT,
    relevance_score DECIMAL(5,2),  -- 0-100

    -- What it applies to
    applies_to_violation_ids BIGINT[],  -- violation_ids
    applies_to_events BIGINT[],  -- event_ids (from TIER 5)
    applies_to_documents BIGINT[],  -- journal_ids

    -- Citation details
    full_citation_text TEXT,
    key_quotes TEXT[],

    -- Source
    source_url TEXT,
    source_document TEXT,

    -- Audit
    added_by TEXT,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_case_law_case_name ON case_law_citations(case_name);
CREATE INDEX idx_case_law_year ON case_law_citations(year);
CREATE INDEX idx_case_law_relevance ON case_law_citations(relevance_score);

CREATE TABLE IF NOT EXISTS legal_codes (
    code_id BIGSERIAL PRIMARY KEY,

    -- Code information
    code_type TEXT NOT NULL,  -- 'Family Code', 'Penal Code', 'Welfare & Institutions Code', 'Evidence Code'
    code_section TEXT NOT NULL,  -- e.g., '3011', '118', '300'
    full_code_reference TEXT,  -- e.g., 'California Family Code § 3011'

    -- Code text
    code_title TEXT,
    code_text TEXT,
    code_summary TEXT,

    -- Relevance to this case
    relevance_to_case TEXT,
    relevance_score DECIMAL(5,2),  -- 0-100

    -- What it applies to
    applies_to_violation_ids BIGINT[],
    applies_to_events BIGINT[],
    applies_to_documents BIGINT[],

    -- Interpretation
    interpretation_notes TEXT,

    -- Audit
    added_by TEXT,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_legal_codes_type ON legal_codes(code_type);
CREATE INDEX idx_legal_codes_section ON legal_codes(code_section);
CREATE INDEX idx_legal_codes_relevance ON legal_codes(relevance_score);

-- ============================================================================
-- TIER 5: EVENT TIMELINE & PROFILES
-- ============================================================================

CREATE TABLE IF NOT EXISTS events (
    event_id BIGSERIAL PRIMARY KEY,

    -- Event details
    event_date DATE NOT NULL,
    event_time TIME,
    event_date_is_approximate BOOLEAN DEFAULT FALSE,

    event_type TEXT NOT NULL,
    /* Types:
       - 'court_hearing'
       - 'incident'
       - 'document_filed'
       - 'visitation'
       - 'police_call'
       - 'cps_investigation'
       - 'medical_visit'
       - 'school_incident'
       - 'communication' (call, text, email)
    */

    event_title TEXT NOT NULL,
    event_description TEXT,

    -- Location
    event_location TEXT,
    event_location_type TEXT,  -- 'home', 'school', 'court', 'hospital', 'police_station'

    -- Participants
    participants JSONB[],
    /*
    [
      {"name": "Ashe B.", "role": "child"},
      {"name": "John Doe", "role": "father"},
      {"name": "Officer Smith", "role": "police"}
    ]
    */

    -- Source documents
    source_documents BIGINT[],  -- journal_ids
    source_micro_analyses BIGINT[],  -- micro_ids

    -- Statements made during event
    statements_made JSONB[],
    /*
    [
      {
        "speaker": "Officer Smith",
        "statement": "No signs of abuse observed",
        "document_journal_id": 123
      }
    ]
    */

    -- Outcome of event
    event_outcome TEXT,
    event_impact TEXT,  -- Impact on case

    -- Links to other entities
    related_violations BIGINT[],  -- violation_ids
    related_case_law BIGINT[],  -- citation_ids
    related_legal_codes BIGINT[],  -- code_ids

    -- Timeline context
    previous_event_id BIGINT REFERENCES events(event_id),  -- Creates timeline chain
    next_event_id BIGINT REFERENCES events(event_id),

    -- Significance
    significance_score DECIMAL(5,2),  -- 0-100 (how important is this event)
    significance_reasoning TEXT,

    -- Verification
    verified BOOLEAN DEFAULT FALSE,
    verification_source TEXT,
    contradicted BOOLEAN DEFAULT FALSE,
    contradiction_details TEXT,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_events_date ON events(event_date);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_significance ON events(significance_score);

CREATE TABLE IF NOT EXISTS profiles (
    profile_id BIGSERIAL PRIMARY KEY,

    -- Person details
    person_name TEXT NOT NULL,
    person_role TEXT NOT NULL,  -- 'child', 'father', 'mother', 'social_worker', 'attorney', 'judge'

    -- Profile data (built from all documents over 2-3 years)
    profile_summary TEXT,

    -- Behavior patterns
    behavior_patterns JSONB[],
    /*
    [
      {
        "pattern": "repeated_false_allegations",
        "frequency": 5,
        "date_range": {"start": "2022-01-01", "end": "2024-01-01"},
        "evidence_event_ids": [1, 5, 12, 23, 45]
      }
    ]
    */

    -- Statements made (across all documents)
    statements_made JSONB[],
    /*
    [
      {
        "statement": "Mother denied visitation",
        "date": "2023-02-01",
        "document_journal_id": 123,
        "verified": false,
        "contradicted_by_journal_ids": [456]
      }
    ]
    */

    -- Reliability metrics
    truthfulness_score DECIMAL(5,2),  -- 0-100 (based on verified vs contradicted statements)
    consistency_score DECIMAL(5,2),  -- 0-100 (how consistent are their statements)
    credibility_score DECIMAL(5,2),  -- 0-100 (overall credibility)

    -- Events involved in
    events_involved BIGINT[],  -- event_ids

    -- Documents mentioning this person
    documents_mentioned_in BIGINT[],  -- journal_ids

    -- Violations committed (if any)
    violations_committed BIGINT[],  -- violation_ids

    -- Relationships
    relationships JSONB[],
    /*
    [
      {
        "related_person": "Jane Doe",
        "relationship_type": "ex-spouse",
        "relationship_quality": "hostile",
        "custody_status": "joint_legal_sole_physical"
      }
    ]
    */

    -- Timeline
    first_mentioned_date DATE,
    last_mentioned_date DATE,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_profiles_person_name ON profiles(person_name);
CREATE INDEX idx_profiles_person_role ON profiles(person_role);
CREATE INDEX idx_profiles_credibility ON profiles(credibility_score);

-- ============================================================================
-- TIER 6: JUDICIAL ASSESSMENT
-- ============================================================================

CREATE TABLE IF NOT EXISTS judicial_assessment (
    assessment_id BIGSERIAL PRIMARY KEY,

    -- Assessment metadata
    assessment_name TEXT NOT NULL,
    assessment_date DATE NOT NULL,
    assessment_type TEXT,  -- 'interim', 'final', 'specific_issue'

    -- Scope
    date_range_start DATE,
    date_range_end DATE,
    documents_included BIGINT[],  -- journal_ids

    -- Summary
    executive_summary TEXT,

    -- Violations found
    violations_found BIGINT[],  -- violation_ids
    violations_summary JSONB,
    /*
    {
      "total_violations": 15,
      "by_type": {
        "perjury": 5,
        "fraud_upon_court": 3,
        "false_allegations": 7
      },
      "by_party": {
        "John Doe": 12,
        "CPS": 3
      },
      "severity_breakdown": {
        "severe": 8,
        "moderate": 5,
        "minor": 2
      }
    }
    */

    -- Case law precedent applied
    case_law_applied BIGINT[],  -- citation_ids
    case_law_summary TEXT,

    -- Legal codes violated
    legal_codes_violated BIGINT[],  -- code_ids

    -- Macro analysis results
    macro_analyses_reviewed BIGINT[],  -- macro_ids
    key_findings TEXT[],

    -- Pattern analysis
    patterns_identified JSONB[],
    /*
    [
      {
        "pattern": "systematic_false_allegations",
        "by_whom": "John Doe",
        "frequency": "monthly",
        "impact": "severe_harm_to_child",
        "recommendation": "sanctions_and_custody_modification"
      }
    ]
    */

    -- Credibility assessments
    credibility_assessments JSONB[],
    /*
    [
      {
        "person": "John Doe",
        "credibility_score": 15,
        "reasoning": "Repeated false statements, contradicted by evidence",
        "recommendation": "testimony_should_be_viewed_skeptically"
      }
    ]
    */

    -- Recommendations
    recommendations TEXT[],
    recommended_actions TEXT[],

    -- Truth Score (Overall)
    truth_score INTEGER,  -- 0-100
    truth_score_explanation TEXT,

    -- Justice Score
    justice_score INTEGER,  -- 0-100
    justice_score_explanation TEXT,

    -- Legal Credit Score (for each party)
    legal_credit_scores JSONB,
    /*
    {
      "John Doe": {
        "score": 15,
        "reasoning": "Multiple violations, false statements, fraud upon court"
      },
      "Jane Doe": {
        "score": 85,
        "reasoning": "Consistent statements, supported by evidence"
      }
    }
    */

    -- Final assessment
    final_conclusion TEXT,

    -- Attachments
    supporting_documents BIGINT[],  -- journal_ids

    -- Status
    assessment_status TEXT DEFAULT 'draft',  -- 'draft', 'review', 'final'

    --審核 (Review)
    reviewed_by TEXT,
    reviewed_at TIMESTAMPTZ,
    review_notes TEXT,

    -- Audit
    created_by TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_judicial_assessment_date ON judicial_assessment(assessment_date);
CREATE INDEX idx_judicial_assessment_status ON judicial_assessment(assessment_status);
CREATE INDEX idx_judicial_assessment_truth_score ON judicial_assessment(truth_score);

-- ============================================================================
-- VIEWS FOR ANALYSIS WORKFLOW
-- ============================================================================

-- Documents ready for micro analysis
CREATE OR REPLACE VIEW documents_ready_for_micro_analysis AS
SELECT
    dj.journal_id,
    dj.original_filename,
    dj.document_type,
    dj.date_logged,
    dj.queue_status
FROM document_journal dj
LEFT JOIN micro_analysis ma ON dj.journal_id = ma.journal_id
WHERE ma.micro_id IS NULL  -- No micro analysis yet
  AND dj.queue_status = 'completed'  -- Document processing complete
ORDER BY dj.date_logged DESC;

-- Micro analyses ready for macro analysis
CREATE OR REPLACE VIEW micro_analyses_ready_for_macro AS
SELECT
    ma.micro_id,
    ma.journal_id,
    ma.document_type,
    ma.analyzed_at,
    ma.extraction_confidence
FROM micro_analysis ma
WHERE ma.ready_for_macro_analysis = TRUE
  AND ma.needs_manual_review = FALSE
ORDER BY ma.analyzed_at DESC;

-- Macro analyses ready for violation detection
CREATE OR REPLACE VIEW macro_analyses_ready_for_violations AS
SELECT
    ma.macro_id,
    ma.analysis_name,
    ma.analysis_type,
    ma.analyzed_at,
    ma.potential_violations_detected
FROM macro_analysis ma
WHERE ma.ready_for_violation_analysis = TRUE
  AND ma.potential_violations_detected = TRUE
ORDER BY ma.analyzed_at DESC;

-- Violations pending review
CREATE OR REPLACE VIEW violations_pending_review AS
SELECT
    v.violation_id,
    v.violation_type,
    v.violation_severity,
    v.violator_name,
    v.violation_date,
    v.confidence_score,
    v.detected_at
FROM violations v
WHERE v.violation_status = 'detected'
ORDER BY v.violation_severity DESC, v.confidence_score DESC;

-- Timeline view (all events chronologically)
CREATE OR REPLACE VIEW timeline_view AS
SELECT
    e.event_id,
    e.event_date,
    e.event_type,
    e.event_title,
    e.event_description,
    e.significance_score,
    e.verified,
    e.contradicted
FROM events e
ORDER BY e.event_date DESC, e.significance_score DESC;

-- Party credibility summary
CREATE OR REPLACE VIEW party_credibility_summary AS
SELECT
    p.profile_id,
    p.person_name,
    p.person_role,
    p.truthfulness_score,
    p.consistency_score,
    p.credibility_score,
    ARRAY_LENGTH(p.violations_committed, 1) as violations_count,
    ARRAY_LENGTH(p.statements_made, 1) as statements_count
FROM profiles p
ORDER BY p.credibility_score DESC;

-- ============================================================================
-- FUNCTIONS FOR TIERED ANALYSIS
-- ============================================================================

-- Function to create micro analysis for a document
CREATE OR REPLACE FUNCTION create_micro_analysis(
    p_journal_id BIGINT,
    p_document_type TEXT,
    p_critical_statements JSONB,
    p_entities JSONB,
    p_dates_mentioned JSONB,
    p_extraction_confidence DECIMAL
)
RETURNS BIGINT AS $$
DECLARE
    v_micro_id BIGINT;
BEGIN
    INSERT INTO micro_analysis (
        journal_id,
        document_type,
        critical_statements,
        entities,
        dates_mentioned,
        extraction_confidence,
        analyzed_at
    ) VALUES (
        p_journal_id,
        p_document_type,
        p_critical_statements,
        p_entities,
        p_dates_mentioned,
        p_extraction_confidence,
        NOW()
    )
    RETURNING micro_id INTO v_micro_id;

    RETURN v_micro_id;
END;
$$ LANGUAGE plpgsql;

-- Function to create violation
CREATE OR REPLACE FUNCTION create_violation(
    p_macro_analysis_id BIGINT,
    p_violation_type TEXT,
    p_violator_name TEXT,
    p_violation_date DATE,
    p_evidence_documents BIGINT[],
    p_confidence_score DECIMAL
)
RETURNS BIGINT AS $$
DECLARE
    v_violation_id BIGINT;
BEGIN
    INSERT INTO violations (
        macro_analysis_id,
        violation_type,
        violator_name,
        violation_date,
        evidence_documents,
        confidence_score,
        detected_at
    ) VALUES (
        p_macro_analysis_id,
        p_violation_type,
        p_violator_name,
        p_violation_date,
        p_evidence_documents,
        p_confidence_score,
        NOW()
    )
    RETURNING violation_id INTO v_violation_id;

    RETURN v_violation_id;
END;
$$ LANGUAGE plpgsql;

-- Function to add event to timeline
CREATE OR REPLACE FUNCTION add_event_to_timeline(
    p_event_date DATE,
    p_event_type TEXT,
    p_event_title TEXT,
    p_source_documents BIGINT[],
    p_significance_score DECIMAL
)
RETURNS BIGINT AS $$
DECLARE
    v_event_id BIGINT;
BEGIN
    INSERT INTO events (
        event_date,
        event_type,
        event_title,
        source_documents,
        significance_score,
        created_at
    ) VALUES (
        p_event_date,
        p_event_type,
        p_event_title,
        p_source_documents,
        p_significance_score,
        NOW()
    )
    RETURNING event_id INTO v_event_id;

    RETURN v_event_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SUMMARY
-- ============================================================================

COMMENT ON TABLE micro_analysis IS 'TIER 1: Per-document analysis - extract critical data';
COMMENT ON TABLE macro_analysis IS 'TIER 2: Cross-document analysis - compare and cross-reference';
COMMENT ON TABLE violations IS 'TIER 3: Legal violation detection - perjury, fraud, etc.';
COMMENT ON TABLE case_law_citations IS 'TIER 4: Relevant case law and precedents';
COMMENT ON TABLE legal_codes IS 'TIER 4: Relevant legal codes (Family Code, Penal Code, etc.)';
COMMENT ON TABLE events IS 'TIER 5: Event timeline over 2-3 years';
COMMENT ON TABLE profiles IS 'TIER 5: Profiles for all parties built from documents';
COMMENT ON TABLE judicial_assessment IS 'TIER 6: Final synthesis and assessment report';

-- For Ashe. For Justice. For All Children. 🛡️
