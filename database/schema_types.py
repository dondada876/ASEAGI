"""
Type definitions for database schema
Provides type hints to prevent schema mismatch issues
"""
from typing import TypedDict, Optional, List
from datetime import datetime

class LegalViolation(TypedDict, total=False):
    """
    Schema for legal_violations table

    CORRECT column names (use these):
    - violation_category (not violation_type)
    - violation_title (not document_title)
    - severity_score (not severity)
    """
    id: str
    violation_category: str  # NOT violation_type
    violation_title: str  # NOT document_title
    violation_description: str
    perpetrator: str
    violation_date: str
    severity_score: int  # NOT severity (0-100 scale)
    legal_basis: Optional[str]
    evidence_summary: Optional[str]
    document_id: Optional[str]
    incident_id: Optional[str]
    created_at: str
    updated_at: str

class LegalDocument(TypedDict, total=False):
    """
    Schema for legal_documents table (UPDATED with micro-analysis columns)

    NEW COLUMNS (added with micro-analysis schema):
    - court_case_id (UUID reference to court_cases)
    - filing_party (Mother, Father, Court, CPS, Third Party)
    - document_function (Motion, Declaration, Evidence, Order, Brief, Report, Exhibit)
    - judicial_notice_status (Candidate, Filed, Granted, Denied)
    - element_count (number of document_elements extracted)
    - truth_alignment_score (0-100 average truth score of all elements)
    - perjury_elements_count (count of false statements)
    - smoking_gun_elements_count (count of smoking gun elements)
    - judicial_notice_elements_count (count of judicial notice worthy elements)
    """
    id: str
    file_name: str
    document_type: str
    category: str
    purpose: Optional[str]
    micro_number: int
    macro_number: int
    legal_number: int
    relevancy_number: int
    summary: Optional[str]
    key_quotes: Optional[List[str]]
    fraud_indicators: Optional[List[str]]
    perjury_indicators: Optional[List[str]]
    contains_false_statements: bool
    document_date: Optional[str]
    processed_at: str
    docket_number: str
    content_hash: Optional[str]
    api_cost_usd: Optional[float]
    # NEW COLUMNS
    court_case_id: Optional[str]
    filing_party: Optional[str]
    document_function: Optional[str]
    judicial_notice_status: Optional[str]
    element_count: int
    truth_alignment_score: Optional[int]
    perjury_elements_count: int
    smoking_gun_elements_count: int
    judicial_notice_elements_count: int

class CourtEvent(TypedDict, total=False):
    """Schema for court_events table"""
    id: str
    event_date: str
    event_title: str
    event_description: str
    event_type: str
    judge_name: Optional[str]
    case_id: str
    created_at: str
    updated_at: str

class Bug(TypedDict, total=False):
    """Schema for bugs table"""
    id: str
    bug_number: str
    title: str
    description: str
    bug_type: str
    severity: str
    priority: str
    status: str
    component: str
    tags: List[str]
    workspace_id: str
    created_at: str
    updated_at: str

class Incident(TypedDict, total=False):
    """Schema for incidents table"""
    id: str
    incident_date: str
    incident_title: str
    incident_description: str
    incident_category: str
    severity_level: str
    reported_by: Optional[str]
    case_id: str
    created_at: str
    updated_at: str

# Severity score ranges for legal_violations
class SeverityLevel:
    """Calculate severity level from severity_score (0-100)"""
    CRITICAL = (90, 100)  # severity_score >= 90
    HIGH = (70, 89)       # 70 <= severity_score < 90
    MEDIUM = (50, 69)     # 50 <= severity_score < 70
    LOW = (0, 49)         # severity_score < 50

    @staticmethod
    def from_score(score: int) -> str:
        """Convert severity_score to text level"""
        if score >= 90:
            return "CRITICAL"
        elif score >= 70:
            return "HIGH"
        elif score >= 50:
            return "MEDIUM"
        else:
            return "LOW"

# ============================================================================
# MICRO-ANALYSIS SCHEMA TYPES (Added November 13, 2025)
# ============================================================================

class CourtCase(TypedDict, total=False):
    """
    Schema for court_cases table
    Groups documents by legal proceeding (motion, hearing, trial)
    """
    id: str
    case_number: str  # J24-00478
    case_title: str  # In re Ashe Bucknor

    # Case Type & Status
    case_type: str  # Custody, Dependency, Criminal, Civil, Appeal
    jurisdiction: str
    court_name: str
    court_location: str
    presiding_judge: str

    # Parties
    petitioner: str
    respondent: str
    minor_children: List[str]
    attorneys: List[str]

    # Timeline
    filed_date: str
    hearing_date: str
    decision_date: str
    status: str  # Pending, Decided, Appealed, Closed, Dismissed

    # Outcome
    ruling_summary: str
    ruling_favorable_to: str  # Petitioner, Respondent, Split, N/A
    court_order_text: str

    # Justice Scoring
    justice_score: int  # 0-1000
    constitutional_violations_count: int
    due_process_violations_count: int
    procedural_violations_count: int

    # Notes
    case_notes: str
    case_significance: str

    # Metadata
    created_at: str
    updated_at: str
    created_by: str
    updated_by: str


class EventTimeline(TypedDict, total=False):
    """
    Schema for event_timeline table
    Canonical timeline - source of truth for all events
    """
    id: str
    event_id: str  # TIMELINE-001

    # Event Details
    event_date: str
    event_time: str
    event_title: str
    event_description: str

    # Classification
    event_category: str  # Incident, Court, Communication, Medical, Police, School, CPS, Therapy, Other
    event_phase: str  # Pre-Incident, During-Incident, Post-Incident
    severity_level: str  # Critical, High, Medium, Low, Info

    # Participants
    primary_actors: List[str]
    witnesses: List[str]
    children_present: List[str]

    # Evidence
    documented_by: List[str]
    evidence_document_ids: List[str]
    physical_evidence: List[str]

    verification_status: str  # Verified, Alleged, Disputed, Unverified, Disproven
    verification_source: str
    verification_date: str

    # Location
    location: str
    location_type: str
    jurisdiction: str

    # Truth Tracking
    contradicted_by_statements: List[str]
    supported_by_statements: List[str]
    truth_confidence_score: int  # 0-100

    # Legal Impact
    legal_significance: str
    statute_violations: List[str]
    constitutional_issues: List[str]
    case_law_applicable: List[str]

    # Impact on Children
    child_impact: str
    child_welfare_concerns: List[str]

    # Case Context
    case_id: str

    # Metadata
    created_at: str
    updated_at: str
    created_by: str
    updated_by: str

    # Source Documentation
    source_type: str
    source_document_id: str


class DocumentElement(TypedDict, total=False):
    """
    Schema for document_elements table
    Individual statements, narratives, arguments extracted from documents
    This is the heart of micro-analysis
    """
    id: str
    element_id: str  # ELEM-001

    # Source Document
    document_id: str
    page_number: int
    paragraph_number: int
    line_numbers: str
    section_heading: str

    # Element Classification
    element_type: str  # Statement, Narrative, Argument, Evidence, Quote, Claim, Conclusion, Request, Assertion, Testimony
    element_subtype: str  # Declaration, Testimony, Legal Argument, Factual Claim, Opinion, Hearsay, Expert Opinion, Character Statement

    # Content
    element_text: str
    element_summary: str
    context: str

    # Who & When
    speaker: str
    speaker_role: str  # Attorney, Declarant, Witness, Judge, Expert, Social Worker, Police Officer, Medical Professional, Other
    statement_date: str
    statement_location: str

    # PROJ344 Scoring (Element-Level)
    micro_score: int  # 0-999
    macro_score: int  # 0-999
    legal_score: int  # 0-999
    relevancy_score: int  # 0-999

    # Truth Tracking
    truth_status: str  # Verified, Alleged, False, Disputed, Unverifiable, Partially-True
    truth_score: int  # 0-100
    truth_verifiable: bool
    truth_verification_method: str

    # Event Cross-Reference
    related_events: List[str]
    contradicts_events: List[str]
    supports_events: List[str]

    # Perjury Detection
    is_false_statement: bool
    contradicted_by: List[str]
    contradicts: List[str]
    perjury_confidence: int  # 0-100
    perjury_evidence: str
    perjury_type: str  # Material Fact, Timeline Discrepancy, Direct Contradiction, Omission, Exaggeration

    # Judicial Notice
    judicial_notice_worthy: bool
    judicial_notice_reason: str
    judicial_notice_category: str  # Fact, Law, Common Knowledge, Court Record, Public Record
    judicial_notice_status: str  # Candidate, Requested, Granted, Denied

    # Legal Function
    legal_purpose: str
    legal_standard: str
    burden_of_proof: str  # Preponderance, Clear and Convincing, Beyond Reasonable Doubt, Substantial Evidence
    admissibility: str  # Admissible, Inadmissible, Objectionable, Unknown
    admissibility_issues: List[str]

    # Case Law Support
    supported_by_precedent: List[str]
    contradicts_precedent: List[str]

    # Impact Assessment
    impact_on_case: str
    smoking_gun_level: int  # 0-10
    impeachment_value: int  # 0-10

    # Child Welfare
    child_impact_statement: bool
    child_welfare_relevance: str

    # Metadata
    extracted_at: str
    extracted_by: str
    extraction_method: str
    verified_at: str
    verified_by: str

    # Version Control
    version: int
    previous_version_id: str

    # Flags
    flagged_for_review: bool
    review_notes: str


class CaseLawPrecedent(TypedDict, total=False):
    """
    Schema for case_law_precedents table
    Relevant case law for cross-referencing arguments
    """
    id: str
    precedent_id: str  # CASE-LAW-001

    # Case Citation
    case_name: str  # Smith v. Jones
    case_citation: str  # 123 F.3d 456 (9th Cir. 2020)
    court: str
    court_level: str  # Supreme Court, Circuit Court, Court of Appeal, Superior Court, District Court, Trial Court
    decision_date: str

    # Judges
    authored_by: str
    panel_judges: List[str]

    # Legal Principles
    holding: str
    legal_principle: str
    legal_standard: str
    key_facts: str
    procedural_history: str

    # Topic Classification
    area_of_law: str  # Family Law, Constitutional Law, Criminal Law
    topics: List[str]
    legal_issues: List[str]

    # Relevance
    relevance_to_case: str
    relevance_score: int  # 0-999
    applicability: str

    # Application
    supports_position: str  # Mother, Father, Court, CPS, Neither, Both
    applicable_to_elements: List[str]
    cited_in_documents: List[str]

    # WestLaw Metadata
    westlaw_id: str
    key_cite_status: str  # Good Law, Distinguished, Overruled, Questioned, Limited, Superseded
    depth_of_treatment: int
    times_cited: int

    # Document Source
    full_text: str
    summary: str
    key_quotes: List[str]
    dissenting_opinion: str

    # Shepardizing
    shepardized_date: str
    shepard_status: str
    negative_treatment: bool

    # Metadata
    added_at: str
    added_by: str
    updated_at: str
    source: str  # WestLaw, Manual Entry, Legal Research, Lexis, Casetext

    # Notes
    application_notes: str
    distinguishing_factors: str


class TruthIndicator(TypedDict, total=False):
    """
    Schema for truth_indicators table
    Evidence that supports or contradicts statements and events
    """
    id: str

    # What This Relates To
    element_id: str
    event_id: str

    # Indicator Type
    indicator_type: str  # Supporting, Contradicting, Neutral, Corroborating, Refuting
    evidence_type: str  # Document, Witness, Physical, Digital, Expert, Medical, Police Report, Court Record, Photograph, Video, Audio, Timestamp, Communication Record

    # Evidence Details
    evidence_description: str
    evidence_source: str
    evidence_document_id: str
    evidence_location: str

    # Specifics
    specific_fact_supported: str
    how_it_supports: str

    # Strength
    credibility_score: int  # 0-100
    weight: int  # 1-10
    reliability: str  # High, Medium, Low, Unknown

    # Chain of Custody
    chain_of_custody_intact: bool
    chain_of_custody_notes: str

    # Verification
    verified: bool
    verified_by: str
    verified_at: str
    verification_method: str

    # Admissibility
    admissible: bool
    admissibility_notes: str

    # Metadata
    created_at: str
    created_by: str


class JusticeScoring(TypedDict, total=False):
    """
    Schema for justice_scoring table
    Tracks justice/injustice metrics and constitutional compliance
    """
    id: str

    # Scope
    scope_type: str  # Case, Document, Element, Event, Hearing
    scope_id: str

    # Justice Dimensions (0-100 each)
    due_process_score: int
    constitutional_compliance_score: int
    evidence_integrity_score: int
    fairness_score: int
    child_welfare_score: int
    procedural_compliance_score: int

    # Composite Justice Score (0-1000)
    overall_justice_score: int

    # Violation Tracking
    violations_detected: int
    violations: dict  # JSONB
    violation_categories: List[str]

    # Factors
    positive_factors: List[str]
    negative_factors: List[str]

    # Constitutional Issues
    first_amendment_violations: int
    fourth_amendment_violations: int
    fifth_amendment_violations: int
    sixth_amendment_violations: int
    fourteenth_amendment_violations: int

    # Recommendation
    justice_recommendation: str
    remedies_available: List[str]
    urgency_level: str  # Critical, High, Medium, Low

    # Scoring Breakdown
    scoring_methodology: str
    scoring_factors: dict  # JSONB

    # Comparison
    benchmark_score: int
    score_gap: int

    # Metadata
    calculated_at: str
    calculation_method: str
    calculated_by: str

    # Review
    reviewed: bool
    reviewed_by: str
    reviewed_at: str
    review_notes: str


class DocumentRelationship(TypedDict, total=False):
    """
    Schema for document_relationships table
    Tracks how documents relate to each other
    """
    id: str

    # Documents
    document_a_id: str
    document_b_id: str

    # Relationship
    relationship_type: str  # Response-To, Supports, Contradicts, Cites, Amends, Supersedes, Incorporates, Exhibits, Opposes, Supplements
    relationship_description: str

    # Specifics
    specific_sections: str
    page_references: str

    # Context
    filed_in_case_id: str
    relationship_date: str

    # Metadata
    created_at: str
    created_by: str


# ============================================================================
# HELPER CLASSES
# ============================================================================

class TruthScore:
    """Calculate truth level from truth_score (0-100)"""
    VERIFIED = (80, 100)  # truth_score >= 80
    LIKELY_TRUE = (60, 79)  # 60 <= truth_score < 80
    DISPUTED = (40, 59)  # 40 <= truth_score < 60
    LIKELY_FALSE = (20, 39)  # 20 <= truth_score < 40
    FALSE = (0, 19)  # truth_score < 20

    @staticmethod
    def from_score(score: int) -> str:
        """Convert truth_score to text level"""
        if score >= 80:
            return "VERIFIED"
        elif score >= 60:
            return "LIKELY_TRUE"
        elif score >= 40:
            return "DISPUTED"
        elif score >= 20:
            return "LIKELY_FALSE"
        else:
            return "FALSE"


class JusticeLevel:
    """Calculate justice level from justice_score (0-1000)"""
    JUST = (800, 1000)  # justice_score >= 800
    MOSTLY_JUST = (600, 799)  # 600 <= justice_score < 800
    QUESTIONABLE = (400, 599)  # 400 <= justice_score < 600
    UNJUST = (200, 399)  # 200 <= justice_score < 400
    SEVERELY_UNJUST = (0, 199)  # justice_score < 200

    @staticmethod
    def from_score(score: int) -> str:
        """Convert justice_score to text level"""
        if score >= 800:
            return "JUST"
        elif score >= 600:
            return "MOSTLY_JUST"
        elif score >= 400:
            return "QUESTIONABLE"
        elif score >= 200:
            return "UNJUST"
        else:
            return "SEVERELY_UNJUST"


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

# Example usage:
"""
from database.schema_types import (
    LegalViolation, SeverityLevel,
    CourtCase, EventTimeline, DocumentElement,
    CaseLawPrecedent, TruthIndicator, JusticeScoring,
    TruthScore, JusticeLevel
)
from typing import List

# Query violations
def get_violations() -> List[LegalViolation]:
    result = supabase.table('legal_violations').select('*').execute()
    return result.data

violations = get_violations()
for violation in violations:
    category = violation['violation_category']  # ✓ Correct
    title = violation['violation_title']        # ✓ Correct
    score = violation['severity_score']         # ✓ Correct
    level = SeverityLevel.from_score(score)
    print(f"{level}: {title}")

# Query document elements with perjury
def get_perjury_elements() -> List[DocumentElement]:
    result = supabase.table('document_elements')\
        .select('*')\
        .eq('is_false_statement', True)\
        .gte('perjury_confidence', 80)\
        .order('perjury_confidence', desc=True)\
        .execute()
    return result.data

perjury_elements = get_perjury_elements()
for elem in perjury_elements:
    speaker = elem['speaker']
    text = elem['element_text']
    confidence = elem['perjury_confidence']
    truth_level = TruthScore.from_score(elem['truth_score'])
    print(f"{speaker} ({confidence}% perjury confidence, {truth_level}): {text[:100]}...")

# Query case justice scores
def get_case_justice(case_number: str) -> JusticeScoring:
    result = supabase.table('justice_scoring')\
        .select('*')\
        .eq('scope_type', 'Case')\
        .execute()
    return result.data[0] if result.data else None

justice = get_case_justice('J24-00478')
if justice:
    overall = justice['overall_justice_score']
    level = JusticeLevel.from_score(overall)
    print(f"Case J24-00478 Justice Score: {overall}/1000 ({level})")
    print(f"Constitutional Violations: {justice['constitutional_compliance_score']}/100")
    print(f"Due Process: {justice['due_process_score']}/100")
"""
