-- ============================================================================
-- ASEAGI Micro-Analysis Schema Migration
-- ============================================================================
-- Migration: 001
-- Created: November 13, 2025
-- Purpose: Create comprehensive micro-analysis database schema
--          Enables element-level document analysis, truth tracking,
--          justice scoring, and case law integration
-- Case: In re Ashe Bucknor (J24-00478)
-- ============================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABLE 1: court_cases
-- Purpose: Group documents by legal proceeding (motion, hearing, trial)
-- ============================================================================

CREATE TABLE IF NOT EXISTS court_cases (
  -- Identity
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  case_number TEXT NOT NULL UNIQUE,  -- J24-00478
  case_title TEXT NOT NULL,  -- In re Ashe Bucknor

  -- Case Type & Status
  case_type TEXT NOT NULL CHECK (case_type IN ('Custody', 'Dependency', 'Criminal', 'Civil', 'Appeal')),
  jurisdiction TEXT,  -- Family Court, Superior Court, etc.
  court_name TEXT,
  court_location TEXT,  -- County/City
  presiding_judge TEXT,

  -- Parties
  petitioner TEXT,  -- Who filed
  respondent TEXT,  -- Who is responding
  minor_children TEXT[],  -- Children involved
  attorneys TEXT[],  -- All attorneys involved

  -- Timeline
  filed_date DATE,
  hearing_date DATE,
  decision_date DATE,
  status TEXT NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'Decided', 'Appealed', 'Closed', 'Dismissed')),

  -- Outcome
  ruling_summary TEXT,
  ruling_favorable_to TEXT CHECK (ruling_favorable_to IN ('Petitioner', 'Respondent', 'Split', 'N/A')),
  court_order_text TEXT,

  -- Justice Scoring
  justice_score INTEGER CHECK (justice_score >= 0 AND justice_score <= 1000),
  constitutional_violations_count INTEGER DEFAULT 0,
  due_process_violations_count INTEGER DEFAULT 0,
  procedural_violations_count INTEGER DEFAULT 0,

  -- Notes
  case_notes TEXT,
  case_significance TEXT,

  -- Metadata
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by TEXT,
  updated_by TEXT
);

-- Indexes for court_cases
CREATE INDEX idx_court_cases_case_number ON court_cases(case_number);
CREATE INDEX idx_court_cases_status ON court_cases(status);
CREATE INDEX idx_court_cases_case_type ON court_cases(case_type);
CREATE INDEX idx_court_cases_justice_score ON court_cases(justice_score DESC);
CREATE INDEX idx_court_cases_filed_date ON court_cases(filed_date DESC);
CREATE INDEX idx_court_cases_hearing_date ON court_cases(hearing_date);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_court_cases_updated_at BEFORE UPDATE
    ON court_cases FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE court_cases IS 'Legal proceedings and cases - groups related documents';
COMMENT ON COLUMN court_cases.justice_score IS 'Overall justice score 0-1000 (higher = more just process)';

-- ============================================================================
-- TABLE 2: event_timeline
-- Purpose: Canonical timeline of ALL events - source of truth
-- ============================================================================

CREATE TABLE IF NOT EXISTS event_timeline (
  -- Identity
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  event_id TEXT UNIQUE NOT NULL,  -- TIMELINE-001, TIMELINE-002

  -- Event Details
  event_date DATE NOT NULL,
  event_time TIME,
  event_title TEXT NOT NULL,
  event_description TEXT NOT NULL,

  -- Classification
  event_category TEXT NOT NULL CHECK (event_category IN (
    'Incident', 'Court', 'Communication', 'Medical', 'Police',
    'School', 'CPS', 'Therapy', 'Other'
  )),
  event_phase TEXT NOT NULL CHECK (event_phase IN (
    'Pre-Incident', 'During-Incident', 'Post-Incident'
  )),
  severity_level TEXT CHECK (severity_level IN ('Critical', 'High', 'Medium', 'Low', 'Info')),

  -- Participants
  primary_actors TEXT[],  -- Who was involved
  witnesses TEXT[],  -- Who can verify
  children_present TEXT[],  -- Which children were there

  -- Evidence
  documented_by TEXT[],  -- Photos, videos, reports, witnesses
  evidence_document_ids UUID[],  -- Links to legal_documents
  physical_evidence TEXT[],  -- Physical items preserved

  verification_status TEXT NOT NULL DEFAULT 'Unverified' CHECK (verification_status IN (
    'Verified', 'Alleged', 'Disputed', 'Unverified', 'Disproven'
  )),
  verification_source TEXT,  -- Police report, medical record, witness testimony
  verification_date DATE,

  -- Location
  location TEXT,
  location_type TEXT,  -- Home, School, Court, Hospital, Public Place
  jurisdiction TEXT,

  -- Truth Tracking
  contradicted_by_statements UUID[],  -- Links to document_elements that contradict this
  supported_by_statements UUID[],  -- Links to document_elements that support this
  truth_confidence_score INTEGER CHECK (truth_confidence_score >= 0 AND truth_confidence_score <= 100),

  -- Legal Impact
  legal_significance TEXT,  -- Why this matters for the case
  statute_violations TEXT[],  -- Laws violated during this event
  constitutional_issues TEXT[],  -- Constitutional problems
  case_law_applicable TEXT[],  -- Relevant precedents

  -- Impact on Children
  child_impact TEXT,  -- How this affected the children
  child_welfare_concerns TEXT[],

  -- Case Context
  case_id UUID REFERENCES court_cases(id) ON DELETE CASCADE,

  -- Metadata
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by TEXT,  -- Who entered this event
  updated_by TEXT,

  -- Source Documentation
  source_type TEXT,  -- Court Record, Police Report, Medical Record, Witness Statement
  source_document_id UUID  -- Link to original document
);

-- Indexes for event_timeline
CREATE INDEX idx_event_timeline_date ON event_timeline(event_date DESC);
CREATE INDEX idx_event_timeline_event_id ON event_timeline(event_id);
CREATE INDEX idx_event_timeline_phase ON event_timeline(event_phase);
CREATE INDEX idx_event_timeline_category ON event_timeline(event_category);
CREATE INDEX idx_event_timeline_verification ON event_timeline(verification_status);
CREATE INDEX idx_event_timeline_severity ON event_timeline(severity_level);
CREATE INDEX idx_event_timeline_case ON event_timeline(case_id);
CREATE INDEX idx_event_timeline_truth_score ON event_timeline(truth_confidence_score DESC);

-- GIN indexes for array columns
CREATE INDEX idx_event_timeline_primary_actors ON event_timeline USING GIN(primary_actors);
CREATE INDEX idx_event_timeline_witnesses ON event_timeline USING GIN(witnesses);
CREATE INDEX idx_event_timeline_violations ON event_timeline USING GIN(statute_violations);

CREATE TRIGGER update_event_timeline_updated_at BEFORE UPDATE
    ON event_timeline FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE event_timeline IS 'Canonical timeline - source of truth for all events';
COMMENT ON COLUMN event_timeline.verification_status IS 'Verification level of this event';
COMMENT ON COLUMN event_timeline.truth_confidence_score IS 'Confidence level 0-100 that this event occurred as described';

-- ============================================================================
-- TABLE 3: document_elements
-- Purpose: Individual statements, narratives, arguments from documents
--          This is the core of micro-analysis
-- ============================================================================

CREATE TABLE IF NOT EXISTS document_elements (
  -- Identity
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  element_id TEXT UNIQUE NOT NULL,  -- ELEM-001, ELEM-002

  -- Source Document
  document_id UUID NOT NULL REFERENCES legal_documents(id) ON DELETE CASCADE,
  page_number INTEGER,
  paragraph_number INTEGER,
  line_numbers TEXT,  -- "Lines 15-18"
  section_heading TEXT,  -- Which section of document

  -- Element Classification
  element_type TEXT NOT NULL CHECK (element_type IN (
    'Statement', 'Narrative', 'Argument', 'Evidence', 'Quote', 'Claim',
    'Conclusion', 'Request', 'Assertion', 'Testimony'
  )),
  element_subtype TEXT CHECK (element_subtype IN (
    'Declaration', 'Testimony', 'Legal Argument', 'Factual Claim',
    'Opinion', 'Hearsay', 'Expert Opinion', 'Character Statement'
  )),

  -- Content
  element_text TEXT NOT NULL,  -- The actual statement/narrative
  element_summary TEXT,  -- AI-generated summary
  context TEXT,  -- Surrounding context

  -- Who & When
  speaker TEXT NOT NULL,  -- Who made this statement
  speaker_role TEXT CHECK (speaker_role IN (
    'Attorney', 'Declarant', 'Witness', 'Judge', 'Expert',
    'Social Worker', 'Police Officer', 'Medical Professional', 'Other'
  )),
  statement_date DATE,  -- When statement was made (may differ from document date)
  statement_location TEXT,  -- Where statement was made

  -- PROJ344 Scoring (Element-Level)
  micro_score INTEGER CHECK (micro_score >= 0 AND micro_score <= 999),
  macro_score INTEGER CHECK (macro_score >= 0 AND macro_score <= 999),
  legal_score INTEGER CHECK (legal_score >= 0 AND legal_score <= 999),
  relevancy_score INTEGER CHECK (relevancy_score >= 0 AND relevancy_score <= 999),

  -- Truth Tracking
  truth_status TEXT NOT NULL DEFAULT 'Unverified' CHECK (truth_status IN (
    'Verified', 'Alleged', 'False', 'Disputed', 'Unverifiable', 'Partially-True'
  )),
  truth_score INTEGER CHECK (truth_score >= 0 AND truth_score <= 100),
  truth_verifiable BOOLEAN DEFAULT TRUE,
  truth_verification_method TEXT,

  -- Event Cross-Reference
  related_events UUID[],  -- Links to event_timeline
  contradicts_events UUID[],  -- Events this statement contradicts
  supports_events UUID[],  -- Events this statement supports

  -- Perjury Detection
  is_false_statement BOOLEAN DEFAULT FALSE,
  contradicted_by UUID[],  -- Other document_elements that contradict this
  contradicts UUID[],  -- Other document_elements this contradicts
  perjury_confidence INTEGER CHECK (perjury_confidence >= 0 AND perjury_confidence <= 100),
  perjury_evidence TEXT,  -- Why we think it's false
  perjury_type TEXT CHECK (perjury_type IN (
    'Material Fact', 'Timeline Discrepancy', 'Direct Contradiction',
    'Omission', 'Exaggeration', NULL
  )),

  -- Judicial Notice
  judicial_notice_worthy BOOLEAN DEFAULT FALSE,
  judicial_notice_reason TEXT,  -- Why this is judicially noticeable
  judicial_notice_category TEXT CHECK (judicial_notice_category IN (
    'Fact', 'Law', 'Common Knowledge', 'Court Record', 'Public Record', NULL
  )),
  judicial_notice_status TEXT CHECK (judicial_notice_status IN (
    'Candidate', 'Requested', 'Granted', 'Denied', NULL
  )),

  -- Legal Function
  legal_purpose TEXT,  -- What is this statement trying to accomplish?
  legal_standard TEXT,  -- What legal standard is being applied?
  burden_of_proof TEXT CHECK (burden_of_proof IN (
    'Preponderance', 'Clear and Convincing', 'Beyond Reasonable Doubt',
    'Substantial Evidence', NULL
  )),
  admissibility TEXT CHECK (admissibility IN (
    'Admissible', 'Inadmissible', 'Objectionable', 'Unknown'
  )),
  admissibility_issues TEXT[],  -- Hearsay, Relevance, Prejudicial, etc.

  -- Case Law Support
  supported_by_precedent UUID[],  -- Links to case_law_precedents
  contradicts_precedent UUID[],  -- Precedents this argument violates

  -- Impact Assessment
  impact_on_case TEXT,  -- How this affects the case
  smoking_gun_level INTEGER CHECK (smoking_gun_level >= 0 AND smoking_gun_level <= 10),
  impeachment_value INTEGER CHECK (impeachment_value >= 0 AND impeachment_value <= 10),

  -- Child Welfare
  child_impact_statement BOOLEAN DEFAULT FALSE,
  child_welfare_relevance TEXT,

  -- Metadata
  extracted_at TIMESTAMP NOT NULL DEFAULT NOW(),
  extracted_by TEXT,  -- API, Manual, Telegram Bot
  extraction_method TEXT,  -- How was this extracted
  verified_at TIMESTAMP,
  verified_by TEXT,

  -- Version Control
  version INTEGER DEFAULT 1,
  previous_version_id UUID,

  -- Flags
  flagged_for_review BOOLEAN DEFAULT FALSE,
  review_notes TEXT
);

-- Indexes for document_elements
CREATE INDEX idx_document_elements_document ON document_elements(document_id);
CREATE INDEX idx_document_elements_element_id ON document_elements(element_id);
CREATE INDEX idx_document_elements_type ON document_elements(element_type);
CREATE INDEX idx_document_elements_speaker ON document_elements(speaker);
CREATE INDEX idx_document_elements_truth_status ON document_elements(truth_status);
CREATE INDEX idx_document_elements_perjury ON document_elements(is_false_statement);
CREATE INDEX idx_document_elements_judicial_notice ON document_elements(judicial_notice_worthy);
CREATE INDEX idx_document_elements_relevancy ON document_elements(relevancy_score DESC);
CREATE INDEX idx_document_elements_smoking_gun ON document_elements(smoking_gun_level DESC);
CREATE INDEX idx_document_elements_truth_score ON document_elements(truth_score DESC);
CREATE INDEX idx_document_elements_perjury_confidence ON document_elements(perjury_confidence DESC);

-- GIN indexes for array columns
CREATE INDEX idx_document_elements_related_events ON document_elements USING GIN(related_events);
CREATE INDEX idx_document_elements_contradicts_events ON document_elements USING GIN(contradicts_events);
CREATE INDEX idx_document_elements_contradicted_by ON document_elements USING GIN(contradicted_by);

-- Full text search
CREATE INDEX idx_document_elements_text_search ON document_elements USING GIN(to_tsvector('english', element_text));

COMMENT ON TABLE document_elements IS 'Micro-analysis: individual statements, narratives, and arguments extracted from documents';
COMMENT ON COLUMN document_elements.truth_score IS 'Alignment with event timeline 0-100';
COMMENT ON COLUMN document_elements.perjury_confidence IS 'Confidence 0-100 that this is a false statement';

-- ============================================================================
-- TABLE 4: case_law_precedents
-- Purpose: Store relevant case law for cross-referencing
-- ============================================================================

CREATE TABLE IF NOT EXISTS case_law_precedents (
  -- Identity
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  precedent_id TEXT UNIQUE NOT NULL,  -- CASE-LAW-001

  -- Case Citation
  case_name TEXT NOT NULL,  -- Smith v. Jones
  case_citation TEXT NOT NULL,  -- 123 F.3d 456 (9th Cir. 2020)
  court TEXT NOT NULL,  -- 9th Circuit, California Supreme Court
  court_level TEXT CHECK (court_level IN (
    'Supreme Court', 'Circuit Court', 'Court of Appeal',
    'Superior Court', 'District Court', 'Trial Court'
  )),
  decision_date DATE,

  -- Judges
  authored_by TEXT,  -- Judge who wrote opinion
  panel_judges TEXT[],

  -- Legal Principles
  holding TEXT NOT NULL,  -- What the court decided
  legal_principle TEXT NOT NULL,  -- The extractable principle
  legal_standard TEXT,  -- What standard was applied
  key_facts TEXT,  -- Facts that led to this decision
  procedural_history TEXT,

  -- Topic Classification
  area_of_law TEXT NOT NULL,  -- Family Law, Constitutional Law, Criminal Law
  topics TEXT[],  -- Due Process, Custody, Evidence
  legal_issues TEXT[],  -- Specific issues addressed

  -- Relevance to J24-00478
  relevance_to_case TEXT,  -- Why this matters for current case
  relevance_score INTEGER CHECK (relevance_score >= 0 AND relevance_score <= 999),
  applicability TEXT,  -- How to apply this precedent

  -- Application
  supports_position TEXT CHECK (supports_position IN (
    'Mother', 'Father', 'Court', 'CPS', 'Neither', 'Both'
  )),
  applicable_to_elements UUID[],  -- Links to document_elements
  cited_in_documents UUID[],  -- Links to legal_documents

  -- WestLaw Metadata
  westlaw_id TEXT,
  key_cite_status TEXT CHECK (key_cite_status IN (
    'Good Law', 'Distinguished', 'Overruled', 'Questioned', 'Limited', 'Superseded'
  )),
  depth_of_treatment INTEGER,  -- How extensively discussed (1-4 stars)
  times_cited INTEGER,  -- How many times cited by other courts

  -- Document Source
  full_text TEXT,
  summary TEXT,
  key_quotes TEXT[],
  dissenting_opinion TEXT,

  -- Shepardizing (Case Law Validation)
  shepardized_date DATE,
  shepard_status TEXT,
  negative_treatment BOOLEAN DEFAULT FALSE,

  -- Metadata
  added_at TIMESTAMP NOT NULL DEFAULT NOW(),
  added_by TEXT,
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  source TEXT CHECK (source IN ('WestLaw', 'Manual Entry', 'Legal Research', 'Lexis', 'Casetext')),

  -- Notes
  application_notes TEXT,
  distinguishing_factors TEXT  -- How our case differs
);

-- Indexes for case_law_precedents
CREATE INDEX idx_case_law_precedent_id ON case_law_precedents(precedent_id);
CREATE INDEX idx_case_law_citation ON case_law_precedents(case_citation);
CREATE INDEX idx_case_law_case_name ON case_law_precedents(case_name);
CREATE INDEX idx_case_law_area ON case_law_precedents(area_of_law);
CREATE INDEX idx_case_law_relevance ON case_law_precedents(relevance_score DESC);
CREATE INDEX idx_case_law_court_level ON case_law_precedents(court_level);
CREATE INDEX idx_case_law_keycite ON case_law_precedents(key_cite_status);

-- GIN indexes
CREATE INDEX idx_case_law_topics ON case_law_precedents USING GIN(topics);
CREATE INDEX idx_case_law_applicable_elements ON case_law_precedents USING GIN(applicable_to_elements);

-- Full text search
CREATE INDEX idx_case_law_text_search ON case_law_precedents USING GIN(
  to_tsvector('english', case_name || ' ' || holding || ' ' || COALESCE(summary, ''))
);

CREATE TRIGGER update_case_law_updated_at BEFORE UPDATE
    ON case_law_precedents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE case_law_precedents IS 'Case law precedents for legal argument validation';

-- ============================================================================
-- TABLE 5: truth_indicators
-- Purpose: Track evidence that establishes truth or falsehood
-- ============================================================================

CREATE TABLE IF NOT EXISTS truth_indicators (
  -- Identity
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- What This Indicator Relates To
  element_id UUID REFERENCES document_elements(id) ON DELETE CASCADE,  -- Statement being evaluated
  event_id UUID REFERENCES event_timeline(id) ON DELETE CASCADE,  -- Event being verified

  -- Indicator Type
  indicator_type TEXT NOT NULL CHECK (indicator_type IN (
    'Supporting', 'Contradicting', 'Neutral', 'Corroborating', 'Refuting'
  )),
  evidence_type TEXT NOT NULL CHECK (evidence_type IN (
    'Document', 'Witness', 'Physical', 'Digital', 'Expert',
    'Medical', 'Police Report', 'Court Record', 'Photograph',
    'Video', 'Audio', 'Timestamp', 'Communication Record'
  )),

  -- Evidence Details
  evidence_description TEXT NOT NULL,
  evidence_source TEXT,  -- Police report, medical record, timestamp, etc.
  evidence_document_id UUID REFERENCES legal_documents(id) ON DELETE SET NULL,
  evidence_location TEXT,  -- Where evidence is stored

  -- Specifics
  specific_fact_supported TEXT,  -- Exact fact this supports/contradicts
  how_it_supports TEXT,  -- Explanation of how evidence relates

  -- Strength
  credibility_score INTEGER CHECK (credibility_score >= 0 AND credibility_score <= 100),
  weight INTEGER CHECK (weight >= 1 AND weight <= 10),  -- How much this should influence truth score
  reliability TEXT CHECK (reliability IN ('High', 'Medium', 'Low', 'Unknown')),

  -- Chain of Custody (for physical/digital evidence)
  chain_of_custody_intact BOOLEAN,
  chain_of_custody_notes TEXT,

  -- Verification
  verified BOOLEAN DEFAULT FALSE,
  verified_by TEXT,
  verified_at TIMESTAMP,
  verification_method TEXT,

  -- Admissibility
  admissible BOOLEAN,
  admissibility_notes TEXT,

  -- Metadata
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by TEXT,

  -- Constraints
  CONSTRAINT check_element_or_event CHECK (
    (element_id IS NOT NULL AND event_id IS NULL) OR
    (element_id IS NULL AND event_id IS NOT NULL) OR
    (element_id IS NOT NULL AND event_id IS NOT NULL)
  )
);

-- Indexes for truth_indicators
CREATE INDEX idx_truth_indicators_element ON truth_indicators(element_id);
CREATE INDEX idx_truth_indicators_event ON truth_indicators(event_id);
CREATE INDEX idx_truth_indicators_type ON truth_indicators(indicator_type);
CREATE INDEX idx_truth_indicators_evidence_type ON truth_indicators(evidence_type);
CREATE INDEX idx_truth_indicators_credibility ON truth_indicators(credibility_score DESC);

COMMENT ON TABLE truth_indicators IS 'Evidence that supports or contradicts statements and events';

-- ============================================================================
-- TABLE 6: justice_scoring
-- Purpose: Track justice/injustice metrics
-- ============================================================================

CREATE TABLE IF NOT EXISTS justice_scoring (
  -- Identity
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- Scope
  scope_type TEXT NOT NULL CHECK (scope_type IN ('Case', 'Document', 'Element', 'Event', 'Hearing')),
  scope_id UUID NOT NULL,  -- ID of the case/document/element/event

  -- Justice Dimensions (0-100 each)
  due_process_score INTEGER CHECK (due_process_score >= 0 AND due_process_score <= 100),
  constitutional_compliance_score INTEGER CHECK (constitutional_compliance_score >= 0 AND constitutional_compliance_score <= 100),
  evidence_integrity_score INTEGER CHECK (evidence_integrity_score >= 0 AND evidence_integrity_score <= 100),
  fairness_score INTEGER CHECK (fairness_score >= 0 AND fairness_score <= 100),
  child_welfare_score INTEGER CHECK (child_welfare_score >= 0 AND child_welfare_score <= 100),
  procedural_compliance_score INTEGER CHECK (procedural_compliance_score >= 0 AND procedural_compliance_score <= 100),

  -- Composite Justice Score (0-1000)
  overall_justice_score INTEGER CHECK (overall_justice_score >= 0 AND overall_justice_score <= 1000),

  -- Violation Tracking
  violations_detected INTEGER DEFAULT 0,
  violations JSONB,  -- Detailed violation records
  violation_categories TEXT[],

  -- Factors
  positive_factors TEXT[],  -- Things done correctly
  negative_factors TEXT[],  -- Things done wrong

  -- Specific Constitutional Issues
  first_amendment_violations INTEGER DEFAULT 0,
  fourth_amendment_violations INTEGER DEFAULT 0,
  fifth_amendment_violations INTEGER DEFAULT 0,
  sixth_amendment_violations INTEGER DEFAULT 0,
  fourteenth_amendment_violations INTEGER DEFAULT 0,

  -- Recommendation
  justice_recommendation TEXT,  -- What should happen to correct injustice
  remedies_available TEXT[],
  urgency_level TEXT CHECK (urgency_level IN ('Critical', 'High', 'Medium', 'Low')),

  -- Scoring Breakdown
  scoring_methodology TEXT,
  scoring_factors JSONB,

  -- Comparison
  benchmark_score INTEGER,  -- What score should ideal process get
  score_gap INTEGER,  -- Difference from benchmark

  -- Metadata
  calculated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  calculation_method TEXT,  -- Algorithm version
  calculated_by TEXT,

  -- Review
  reviewed BOOLEAN DEFAULT FALSE,
  reviewed_by TEXT,
  reviewed_at TIMESTAMP,
  review_notes TEXT
);

-- Indexes for justice_scoring
CREATE INDEX idx_justice_scoring_scope ON justice_scoring(scope_type, scope_id);
CREATE INDEX idx_justice_scoring_overall ON justice_scoring(overall_justice_score DESC);
CREATE INDEX idx_justice_scoring_due_process ON justice_scoring(due_process_score DESC);
CREATE INDEX idx_justice_scoring_urgency ON justice_scoring(urgency_level);

COMMENT ON TABLE justice_scoring IS 'Justice/injustice metrics and constitutional compliance tracking';
COMMENT ON COLUMN justice_scoring.overall_justice_score IS 'Composite 0-1000 (higher = more just)';

-- ============================================================================
-- TABLE 7: document_relationships
-- Purpose: Track relationships between documents
-- ============================================================================

CREATE TABLE IF NOT EXISTS document_relationships (
  -- Identity
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- Documents
  document_a_id UUID REFERENCES legal_documents(id) ON DELETE CASCADE NOT NULL,
  document_b_id UUID REFERENCES legal_documents(id) ON DELETE CASCADE NOT NULL,

  -- Relationship
  relationship_type TEXT NOT NULL CHECK (relationship_type IN (
    'Response-To', 'Supports', 'Contradicts', 'Cites', 'Amends',
    'Supersedes', 'Incorporates', 'Exhibits', 'Opposes', 'Supplements'
  )),
  relationship_description TEXT,

  -- Specifics
  specific_sections TEXT,  -- Which sections relate
  page_references TEXT,

  -- Context
  filed_in_case_id UUID REFERENCES court_cases(id) ON DELETE SET NULL,
  relationship_date DATE,  -- When relationship was established

  -- Metadata
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  created_by TEXT,

  -- Constraints
  CONSTRAINT no_self_reference CHECK (document_a_id != document_b_id),
  CONSTRAINT unique_relationship UNIQUE (document_a_id, document_b_id, relationship_type)
);

-- Indexes for document_relationships
CREATE INDEX idx_doc_relationships_a ON document_relationships(document_a_id);
CREATE INDEX idx_doc_relationships_b ON document_relationships(document_b_id);
CREATE INDEX idx_doc_relationships_type ON document_relationships(relationship_type);
CREATE INDEX idx_doc_relationships_case ON document_relationships(filed_in_case_id);

COMMENT ON TABLE document_relationships IS 'Tracks how documents relate to each other';

-- ============================================================================
-- TABLE 8: Update legal_documents with new columns
-- ============================================================================

-- Add new columns to existing legal_documents table
ALTER TABLE legal_documents
  ADD COLUMN IF NOT EXISTS court_case_id UUID REFERENCES court_cases(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS filing_party TEXT CHECK (filing_party IN ('Mother', 'Father', 'Court', 'CPS', 'Third Party', NULL)),
  ADD COLUMN IF NOT EXISTS document_function TEXT CHECK (document_function IN ('Motion', 'Declaration', 'Evidence', 'Order', 'Brief', 'Report', 'Exhibit', NULL)),
  ADD COLUMN IF NOT EXISTS judicial_notice_status TEXT CHECK (judicial_notice_status IN ('Candidate', 'Filed', 'Granted', 'Denied', NULL)),
  ADD COLUMN IF NOT EXISTS element_count INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS truth_alignment_score INTEGER CHECK (truth_alignment_score >= 0 AND truth_alignment_score <= 100),
  ADD COLUMN IF NOT EXISTS perjury_elements_count INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS smoking_gun_elements_count INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS judicial_notice_elements_count INTEGER DEFAULT 0;

-- Indexes for new columns
CREATE INDEX IF NOT EXISTS idx_legal_documents_court_case ON legal_documents(court_case_id);
CREATE INDEX IF NOT EXISTS idx_legal_documents_function ON legal_documents(document_function);
CREATE INDEX IF NOT EXISTS idx_legal_documents_judicial_notice ON legal_documents(judicial_notice_status);
CREATE INDEX IF NOT EXISTS idx_legal_documents_filing_party ON legal_documents(filing_party);
CREATE INDEX IF NOT EXISTS idx_legal_documents_truth_alignment ON legal_documents(truth_alignment_score DESC);

COMMENT ON COLUMN legal_documents.truth_alignment_score IS 'Average truth score of all elements in this document';
COMMENT ON COLUMN legal_documents.element_count IS 'Number of document_elements extracted from this document';

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: High-confidence perjury elements
CREATE OR REPLACE VIEW perjury_elements AS
SELECT
  de.element_id,
  de.element_text,
  de.speaker,
  de.perjury_confidence,
  de.perjury_evidence,
  de.perjury_type,
  ld.file_name,
  ld.document_type,
  ld.document_date,
  cc.case_number
FROM document_elements de
JOIN legal_documents ld ON de.document_id = ld.id
LEFT JOIN court_cases cc ON ld.court_case_id = cc.id
WHERE de.is_false_statement = TRUE
  AND de.perjury_confidence >= 70
ORDER BY de.perjury_confidence DESC;

COMMENT ON VIEW perjury_elements IS 'High-confidence false statements for perjury tracking';

-- View: Smoking gun elements
CREATE OR REPLACE VIEW smoking_gun_elements AS
SELECT
  de.element_id,
  de.element_text,
  de.smoking_gun_level,
  de.relevancy_score,
  de.speaker,
  ld.file_name,
  ld.document_type,
  cc.case_number
FROM document_elements de
JOIN legal_documents ld ON de.document_id = ld.id
LEFT JOIN court_cases cc ON ld.court_case_id = cc.id
WHERE de.smoking_gun_level >= 7
ORDER BY de.smoking_gun_level DESC, de.relevancy_score DESC;

COMMENT ON VIEW smoking_gun_elements IS 'Critical evidence elements (smoking gun level >= 7)';

-- View: Judicial notice candidates
CREATE OR REPLACE VIEW judicial_notice_candidates AS
SELECT
  de.element_id,
  de.element_text,
  de.judicial_notice_reason,
  de.judicial_notice_category,
  de.truth_score,
  de.relevancy_score,
  ld.file_name,
  ld.document_type
FROM document_elements de
JOIN legal_documents ld ON de.document_id = ld.id
WHERE de.judicial_notice_worthy = TRUE
  AND de.truth_score >= 80
ORDER BY de.relevancy_score DESC;

COMMENT ON VIEW judicial_notice_candidates IS 'Elements suitable for judicial notice requests';

-- View: Timeline contradictions
CREATE OR REPLACE VIEW timeline_contradictions AS
SELECT
  et.event_id,
  et.event_title,
  et.event_date,
  et.verification_status AS event_verification,
  de.element_id,
  de.element_text,
  de.speaker,
  de.perjury_confidence,
  ld.file_name
FROM event_timeline et
JOIN document_elements de ON et.id = ANY(de.contradicts_events)
JOIN legal_documents ld ON de.document_id = ld.id
WHERE et.verification_status = 'Verified'
ORDER BY de.perjury_confidence DESC;

COMMENT ON VIEW timeline_contradictions IS 'Statements that contradict verified timeline events';

-- ============================================================================
-- FUNCTIONS FOR AUTOMATED CALCULATIONS
-- ============================================================================

-- Function: Calculate truth score for an element
CREATE OR REPLACE FUNCTION calculate_element_truth_score(element_uuid UUID)
RETURNS INTEGER AS $$
DECLARE
  supporting_count INTEGER;
  contradicting_count INTEGER;
  avg_credibility NUMERIC;
  truth_score INTEGER;
BEGIN
  -- Count supporting indicators
  SELECT COUNT(*), COALESCE(AVG(credibility_score), 50)
  INTO supporting_count, avg_credibility
  FROM truth_indicators
  WHERE element_id = element_uuid AND indicator_type IN ('Supporting', 'Corroborating');

  -- Count contradicting indicators
  SELECT COUNT(*)
  INTO contradicting_count
  FROM truth_indicators
  WHERE element_id = element_uuid AND indicator_type IN ('Contradicting', 'Refuting');

  -- Calculate score (simple algorithm - can be enhanced)
  IF contradicting_count > supporting_count THEN
    truth_score := LEAST(100, GREATEST(0, 50 - (contradicting_count * 15)));
  ELSE
    truth_score := LEAST(100, GREATEST(0, 50 + (supporting_count * 10)));
  END IF;

  -- Factor in credibility
  truth_score := LEAST(100, truth_score * (avg_credibility / 100.0));

  -- Update element
  UPDATE document_elements
  SET truth_score = truth_score,
      truth_status = CASE
        WHEN truth_score >= 80 THEN 'Verified'
        WHEN truth_score <= 30 THEN 'False'
        ELSE 'Disputed'
      END
  WHERE id = element_uuid;

  RETURN truth_score;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_element_truth_score IS 'Calculate truth score for a document element based on truth indicators';

-- Function: Calculate justice score for a case
CREATE OR REPLACE FUNCTION calculate_case_justice_score(case_uuid UUID)
RETURNS INTEGER AS $$
DECLARE
  due_process_avg NUMERIC;
  constitutional_avg NUMERIC;
  evidence_avg NUMERIC;
  fairness_avg NUMERIC;
  child_welfare_avg NUMERIC;
  overall_score INTEGER;
BEGIN
  -- Average all justice dimensions
  SELECT
    COALESCE(AVG(due_process_score), 50),
    COALESCE(AVG(constitutional_compliance_score), 50),
    COALESCE(AVG(evidence_integrity_score), 50),
    COALESCE(AVG(fairness_score), 50),
    COALESCE(AVG(child_welfare_score), 50)
  INTO
    due_process_avg,
    constitutional_avg,
    evidence_avg,
    fairness_avg,
    child_welfare_avg
  FROM justice_scoring
  WHERE scope_type = 'Case' AND scope_id = case_uuid;

  -- Calculate weighted overall score (0-1000 scale)
  overall_score := (
    (due_process_avg * 2.5) +  -- Due process weighted heavily
    (constitutional_avg * 2.5) +  -- Constitution weighted heavily
    (evidence_avg * 2.0) +
    (fairness_avg * 1.5) +
    (child_welfare_avg * 1.5)
  )::INTEGER;

  overall_score := LEAST(1000, GREATEST(0, overall_score));

  -- Update court case
  UPDATE court_cases
  SET justice_score = overall_score
  WHERE id = case_uuid;

  RETURN overall_score;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_case_justice_score IS 'Calculate overall justice score for a court case';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Log migration completion
DO $$
BEGIN
  RAISE NOTICE '✅ Migration 001 Complete: Micro-Analysis Schema Created';
  RAISE NOTICE '📊 Tables Created: 7 new tables';
  RAISE NOTICE '📝 Views Created: 4 analytical views';
  RAISE NOTICE '⚙️  Functions Created: 2 calculation functions';
  RAISE NOTICE '🔗 Relationships: Comprehensive foreign keys and indexes';
  RAISE NOTICE '';
  RAISE NOTICE 'Next Steps:';
  RAISE NOTICE '1. Update schema_types.py with new TypedDict definitions';
  RAISE NOTICE '2. Seed event_timeline with verified events';
  RAISE NOTICE '3. Update document scanners to extract elements';
  RAISE NOTICE '4. Update Telegram bot for micro-analysis';
  RAISE NOTICE '5. Create dashboards for new data';
END $$;
