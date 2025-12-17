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
    """Schema for legal_documents table"""
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

# Example usage:
"""
from database.schema_types import LegalViolation, SeverityLevel
from typing import List

def get_violations() -> List[LegalViolation]:
    result = supabase.table('legal_violations').select('*').execute()
    return result.data

violations = get_violations()
for violation in violations:
    # Type hints will show correct field names
    category = violation['violation_category']  # ✓ Correct
    title = violation['violation_title']        # ✓ Correct
    score = violation['severity_score']         # ✓ Correct

    # IDE will warn about incorrect names
    # wrong = violation['violation_type']       # ✗ Wrong - IDE warning
    # wrong = violation['document_title']       # ✗ Wrong - IDE warning

    # Calculate severity level
    level = SeverityLevel.from_score(score)
    print(f"{level}: {title}")
"""
