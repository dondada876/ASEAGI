"""
Criminal Complaint Schema for Evidence Correlation
Maps specific false statements to supporting documentary evidence
"""
from typing import TypedDict, List, Optional
from datetime import datetime

class FalseStatement(TypedDict):
    """Individual false statement made under oath"""
    id: str
    declaration_date: str  # Date of sworn statement
    claim_text: str  # Exact quote from declaration
    claim_type: str  # JAMAICA_FLIGHT_RISK, RETURN_AGREEMENT, HISTORY_VIOLATIONS, etc.
    contradicted_by: List[str]  # Document IDs that contradict this claim
    evidence_weight: int  # 0-100 scale
    penal_code: List[str]  # PC §118.1, §135, §148

class EvidenceDocument(TypedDict):
    """Document that supports complaint"""
    document_id: str
    relevancy_number: int  # From PROJ344 scoring
    claim_correlation: int  # 0-100 - How strongly it supports the claim
    key_quote: str  # Specific quote that contradicts false statement
    document_type: str  # TEXT, TRANSCRIPT, DECLARATION, etc.
    document_date: str
    contradiction_score: int  # 0-999 - Strength of contradiction

class CriminalComplaint(TypedDict):
    """Complete criminal complaint structure"""
    id: str
    complaint_date: str
    subject_name: str  # Person who committed perjury
    complainant_name: str
    case_reference: str  # D22-03244
    penal_codes: List[str]
    false_statements: List[FalseStatement]
    supporting_documents: List[EvidenceDocument]
    total_evidence_weight: int
    prosecutability_score: int  # 0-100

# Master Criminal Complaint Data Structure
PERJURY_COMPLAINT_2025 = {
    "id": "COMPLAINT-001-PERJURY-2025",
    "complaint_date": "2025-11-17",
    "subject_name": "Mariyam Yonas Rufael",
    "complainant_name": "Don Bucknor",
    "case_reference": "D22-03244",
    "penal_codes": ["PC-118.1", "PC-135", "PC-148"],

    "false_statements": [
        {
            "id": "FS-001-JAMAICA-FLIGHT",
            "declaration_date": "2024-08-12",
            "claim_text": "I'm terrified that he will use this Good Cause Report to ignore the current court order made on May 22 2024, and will abscond with the pain Ashe to Jamaica. Jamaica is not a Hague Convention member, so this court would have no jurisdiction to bring the minor back to the States if Respondent were to leave with Ashe.",
            "claim_type": "JAMAICA_FLIGHT_RISK",
            "contradicted_by": [],  # Will be populated by query
            "evidence_weight": 100,  # Maximum - complete contradiction
            "penal_code": ["PC-118.1"],
            "search_keywords": ["jamaica", "travel", "flight", "passport", "mother's ashes", "ashes", "leave country", "abscond"],
            "date_range": ["2024-05-01", "2024-08-07"],  # Text message period
            "expected_evidence_type": "TEXT",
            "contradiction_logic": "ABSENCE_OF_MENTION",  # 201+ texts, ZERO mentions
        },
        {
            "id": "FS-002-RETURN-AGREEMENT",
            "declaration_date": "2024-08-14",
            "claim_text": "Respondent and I agreed Ashe would be returned to me on 8/9/2024 at 5pm. Respondent did not return her Ashe and has been withholding her since",
            "claim_type": "RETURN_AGREEMENT_VIOLATION",
            "contradicted_by": [],
            "evidence_weight": 95,
            "penal_code": ["PC-118.1"],
            "search_keywords": ["good cause", "district attorney", "DA office", "Rick Rivera", "protective custody", "return", "August 7"],
            "date_range": ["2024-08-07", "2024-08-09"],
            "expected_evidence_type": "TEXT",
            "contradiction_logic": "DIRECT_CONTRADICTION",  # Text explicitly states Good Cause Report
        },
        {
            "id": "FS-003-HISTORY-VIOLATIONS",
            "declaration_date": "2024-08-14",
            "claim_text": "Respondent has no ties to the United States has a history of ignoring Court orders and ultimately lost joint custody because of behaviors exactly like this.",
            "claim_type": "HISTORY_OF_VIOLATIONS",
            "contradicted_by": [],
            "evidence_weight": 85,
            "penal_code": ["PC-118.1"],
            "search_keywords": ["court order", "violation", "custody", "joint custody", "good cause report", "first time"],
            "date_range": ["2020-01-01", "2024-08-12"],
            "expected_evidence_type": "ORDR",  # Court orders
            "contradiction_logic": "ABSENCE_OF_EVIDENCE",  # No prior violations documented
        },
        {
            "id": "FS-004-CONCEALED-INVESTIGATION",
            "declaration_date": "2024-08-12",
            "claim_text": "[Material omission] Failed to disclose maternal grandfather was investigation target and child forensic interview named grandfather",
            "claim_type": "CONCEALMENT_OF_EVIDENCE",
            "contradicted_by": [],
            "evidence_weight": 100,
            "penal_code": ["PC-135", "PC-118.1"],
            "search_keywords": ["grandfather", "sexual abuse", "forensic", "CIC", "Cal OES", "investigation", "Dr. Brown"],
            "date_range": ["2024-01-01", "2024-08-15"],
            "expected_evidence_type": "MEDR",  # Medical/forensic records
            "contradiction_logic": "MATERIAL_OMISSION",  # Should have disclosed, didn't
        },
        {
            "id": "FS-005-MOTHER-ASHES-CLAIM",
            "declaration_date": "2024-08-12",
            "claim_text": "[Implied] Father's travel to Jamaica was to spread mother's ashes",
            "claim_type": "FALSE_TRAVEL_MOTIVE",
            "contradicted_by": [],
            "evidence_weight": 90,
            "penal_code": ["PC-118.1"],
            "search_keywords": ["uncle", "funeral", "September", "mother ashes", "ashes", "jamaica reason"],
            "date_range": ["2024-08-12", "2024-09-30"],
            "expected_evidence_type": "TRNS",  # Transcript showing real reason
            "contradiction_logic": "DIRECT_CONTRADICTION",  # Transcript shows uncle's funeral
        },
    ],

    "required_evidence_categories": [
        "TEXT_MESSAGES_MAY_AUGUST_2024",
        "GOOD_CAUSE_REPORT_DA_DIRECTIVE",
        "SEPTEMBER_20_JUVENILE_TRANSCRIPT",
        "AUGUST_15_COURT_ORDER",
        "AUGUST_27_DETENTION_ORDER",
        "FORENSIC_INTERVIEW_RESULTS",
        "FL312_CHILD_ABDUCTION_FORM",
    ]
}

# Evidence correlation scoring
class CorrelationScoring:
    """Calculate how strongly a document supports the complaint"""

    @staticmethod
    def calculate_contradiction_score(
        document_relevancy: int,  # 0-999 from PROJ344
        keyword_matches: int,     # Number of keywords found
        date_relevance: int,      # 0-100 - How close to claim date
        document_type_match: bool  # Does doc type match expected?
    ) -> int:
        """
        Calculate contradiction score (0-999)
        Higher score = stronger evidence of perjury
        """
        base_score = document_relevancy

        # Keyword bonus (up to +100)
        keyword_bonus = min(keyword_matches * 20, 100)

        # Date relevance bonus (up to +100)
        date_bonus = date_relevance

        # Type match bonus (+50)
        type_bonus = 50 if document_type_match else 0

        total = base_score + keyword_bonus + date_bonus + type_bonus
        return min(total, 999)

    @staticmethod
    def calculate_prosecutability_score(
        total_documents: int,     # Total supporting documents
        avg_contradiction: int,   # Average contradiction score
        direct_contradictions: int,  # Documents with direct contradictions
        witness_statements: int    # Sworn statements supporting
    ) -> int:
        """
        Calculate overall prosecutability (0-100)
        Higher = stronger case for prosecution
        """
        # Base from number of documents (up to 30 points)
        doc_score = min(total_documents * 3, 30)

        # Contradiction strength (up to 40 points)
        contradiction_score = int((avg_contradiction / 999) * 40)

        # Direct contradiction bonus (up to 20 points)
        direct_score = min(direct_contradictions * 4, 20)

        # Witness statement bonus (up to 10 points)
        witness_score = min(witness_statements * 5, 10)

        total = doc_score + contradiction_score + direct_score + witness_score
        return min(total, 100)

# Query templates for finding evidence
EVIDENCE_QUERIES = {
    "JAMAICA_FLIGHT_RISK": """
        SELECT
            id,
            file_name,
            document_type,
            relevancy_number,
            key_quotes,
            document_date,
            processed_at
        FROM legal_documents
        WHERE
            (
                key_quotes::text ILIKE '%jamaica%' OR
                key_quotes::text ILIKE '%travel%' OR
                key_quotes::text ILIKE '%passport%' OR
                key_quotes::text ILIKE '%ashes%' OR
                key_quotes::text ILIKE '%mother ashes%' OR
                summary ILIKE '%jamaica%'
            )
            AND document_date BETWEEN '2024-05-01' AND '2024-08-07'
            AND case_id = 'ashe-bucknor-j24-00478'
        ORDER BY relevancy_number DESC;
    """,

    "TEXT_MESSAGE_ANALYSIS": """
        SELECT
            id,
            file_name,
            document_type,
            relevancy_number,
            key_quotes,
            document_date,
            summary
        FROM legal_documents
        WHERE
            document_type = 'TEXT'
            AND document_date BETWEEN '2024-05-01' AND '2024-08-07'
            AND case_id = 'ashe-bucknor-j24-00478'
        ORDER BY document_date ASC;
    """,

    "GOOD_CAUSE_REPORT": """
        SELECT *
        FROM legal_documents
        WHERE
            (
                key_quotes::text ILIKE '%good cause%' OR
                summary ILIKE '%district attorney%' OR
                summary ILIKE '%Rick Rivera%' OR
                key_quotes::text ILIKE '%protective custody%'
            )
            AND document_date BETWEEN '2024-08-07' AND '2024-08-15'
        ORDER BY relevancy_number DESC;
    """,

    "FORENSIC_EVIDENCE": """
        SELECT *
        FROM legal_documents
        WHERE
            document_type IN ('MEDR', 'FORN')
            AND (
                key_quotes::text ILIKE '%grandfather%' OR
                key_quotes::text ILIKE '%sexual abuse%' OR
                summary ILIKE '%forensic interview%' OR
                summary ILIKE '%CAL OES 2-925%'
            )
        ORDER BY relevancy_number DESC;
    """,

    "COURT_ORDERS": """
        SELECT *
        FROM legal_documents
        WHERE
            document_type = 'ORDR'
            AND document_date BETWEEN '2024-05-01' AND '2024-08-31'
        ORDER BY document_date ASC;
    """,

    "TRANSCRIPTS": """
        SELECT *
        FROM legal_documents
        WHERE
            document_type = 'TRNS'
            AND (
                key_quotes::text ILIKE '%jamaica%' OR
                key_quotes::text ILIKE '%uncle%' OR
                key_quotes::text ILIKE '%funeral%'
            )
            AND document_date >= '2024-09-20'
        ORDER BY document_date ASC;
    """
}
