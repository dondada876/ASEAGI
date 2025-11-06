# ASEAGI Tiered Analysis Architecture

**Created:** 2025-11-06
**For:** In re Ashe B., J24-00478
**Purpose:** Multi-tier legal document analysis system

---

## 🎯 Overview

The Tiered Analysis System is a sophisticated multi-layer architecture for analyzing legal documents at different levels of granularity, from individual document extraction (micro) to cross-document comparison (macro) to violation detection and final judicial assessment.

### Key Insight

**You cannot do macro analysis without micro analysis first.**
**You cannot detect violations without macro analysis.**
**Each tier builds on the previous one.**

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│ DOCUMENT UPLOAD                                                     │
│ (Mobile, Telegram, Web, Batch)                                      │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ QUEUE SYSTEM (from previous work)                                  │
│ - Assessment phase                                                  │
│ - Duplicate detection                                               │
│ - Priority assignment                                               │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ TIER 1: MICRO ANALYSIS (Per Document)                              │
│                                                                     │
│ Purpose: Extract critical data from individual documents            │
│ Granularity: DOCUMENT-LEVEL                                        │
│                                                                     │
│ For a police report:                                               │
│   ✓ Extract officer name, badge number                            │
│   ✓ Extract incident date, time, location                         │
│   ✓ Extract statements from all parties                           │
│   ✓ Extract allegations (abuse, neglect, etc.)                    │
│   ✓ Extract disposition (founded/unfounded)                       │
│                                                                     │
│ For a court declaration:                                           │
│   ✓ Extract declarant name and role                               │
│   ✓ Extract date sworn                                             │
│   ✓ Extract all claims made                                        │
│   ✓ Extract specific incidents described                          │
│   ✓ Extract dates of alleged incidents                            │
│                                                                     │
│ For a medical report:                                              │
│   ✓ Extract doctor name, facility                                 │
│   ✓ Extract visit date                                             │
│   ✓ Extract diagnosis and findings                                │
│   ✓ Extract injuries (if any)                                     │
│   ✓ Extract recommendations                                        │
│                                                                     │
│ ⚠️  CANNOT determine relevancy yet (no context)                    │
│ ⚠️  CANNOT cross-reference with other documents                    │
│                                                                     │
│ Output: micro_analysis table row                                   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ TIER 2: MACRO ANALYSIS (Cross-Document)                            │
│                                                                     │
│ Purpose: Cross-reference micro results, compare statements         │
│ Granularity: MULTI-DOCUMENT-LEVEL                                  │
│                                                                     │
│ Analysis Types:                                                    │
│   • Consistency Check                                              │
│     - Compare statements across documents                          │
│     - Find contradictions                                          │
│     - Example: Declaration says "Child was injured"                │
│               Police report says "No injuries observed"            │
│                                                                     │
│   • Ex Parte Verification                                          │
│     - Check ex parte claims against evidence                       │
│     - Example: Ex parte claims "immediate danger"                  │
│               But no evidence supports this                        │
│     - Calculate fraudulent filing likelihood                       │
│                                                                     │
│   • Timeline Verification                                          │
│     - Verify event sequence across documents                       │
│     - Find timeline inconsistencies                                │
│                                                                     │
│   • Statement Comparison                                           │
│     - Compare same person's statements over time                   │
│     - Find self-contradictions                                     │
│                                                                     │
│ ✓ NOW we can determine legal relevancy (we have context!)         │
│ ✓ Consistency scores                                               │
│ ✓ Reliability scores                                               │
│                                                                     │
│ Output: macro_analysis table row                                   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ TIER 3: VIOLATION ANALYSIS                                         │
│                                                                     │
│ Purpose: Detect legal violations using macro results               │
│ Granularity: VIOLATION-LEVEL                                       │
│                                                                     │
│ Violation Types Detected:                                          │
│   • Perjury (California Penal Code § 118)                         │
│     - False statements made under oath                             │
│     - Requires: Sworn statement + proof it's false                 │
│                                                                     │
│   • Fraud Upon Court                                               │
│     - Ex parte filing with false information                       │
│     - Misleading the court                                         │
│                                                                     │
│   • Protective Order Violations                                    │
│     - Violations of restraining orders                             │
│     - Documented violations                                        │
│                                                                     │
│   • Child Endangerment (California Penal Code § 273a)             │
│     - Actions that endanger child                                  │
│                                                                     │
│   • Negligence                                                     │
│     - Failure to act when required                                 │
│     - Professional negligence (social workers, etc.)               │
│                                                                     │
│   • False Allegations Pattern                                      │
│     - Repeated false allegations                                   │
│     - Pattern of behavior                                          │
│                                                                     │
│ For each violation:                                                │
│   ✓ Violator identified                                            │
│   ✓ Violation date/range                                           │
│   ✓ Specific law/order violated                                    │
│   ✓ Evidence documents linked                                      │
│   ✓ Confidence score                                               │
│   ✓ Recommended action                                             │
│                                                                     │
│ Output: violations table rows                                      │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ TIER 4: CASE LAW & LEGAL CITATIONS                                │
│                                                                     │
│ Purpose: Link relevant precedents and codes                        │
│ Granularity: LEGAL-REFERENCE-LEVEL                                 │
│                                                                     │
│ Case Law Citations:                                                │
│   • Relevant California cases                                      │
│   • Precedents for this case type                                  │
│   • Holdings that apply                                            │
│   • Attached to events/statements/violations                       │
│                                                                     │
│ Example:                                                           │
│   In re Marriage of Smith, 123 Cal.App.4th 456 (2004)            │
│   → Holding: "Pattern of false allegations is grounds for         │
│               custody modification"                                │
│   → Applies to: Violations #1, #5, #12                            │
│                                                                     │
│ Legal Codes:                                                       │
│   • Family Code (custody, visitation)                              │
│   • Penal Code (criminal violations)                               │
│   • Welfare & Institutions Code (CPS, dependency)                 │
│   • Evidence Code (admissibility)                                  │
│                                                                     │
│ Can be referenced across all documents over 2-3 years              │
│                                                                     │
│ Output: case_law_citations, legal_codes tables                     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ TIER 5: EVENT TIMELINE & PROFILES                                 │
│                                                                     │
│ Purpose: Build comprehensive picture over 2-3 years                │
│ Granularity: CASE-LEVEL                                            │
│                                                                     │
│ Event Timeline:                                                    │
│   • Extract all events from all documents                          │
│   • Order chronologically                                          │
│   • Link related events                                            │
│   • Track significance                                             │
│   • Verify accuracy (cross-reference)                              │
│   • Flag contradictions                                            │
│                                                                     │
│ Example Timeline:                                                  │
│   2022-01-15: Father files ex parte (priority 10)                 │
│   2022-01-16: Police investigate - no evidence found              │
│   2022-02-01: Father files another ex parte                        │
│   2022-02-02: Court denies - no emergency shown                    │
│   ... (pattern emerges)                                            │
│                                                                     │
│ Profiles:                                                          │
│   • Build profile for each person                                  │
│   • Aggregate all statements made                                  │
│   • Track behavior patterns                                        │
│   • Calculate credibility scores                                   │
│   • Identify relationships                                         │
│                                                                     │
│ Example Profile (Father):                                         │
│   - Statements made: 47                                            │
│   - Verified statements: 5 (10.6%)                                │
│   - Contradicted statements: 28 (59.6%)                           │
│   - Credibility score: 15/100                                      │
│   - Pattern: Repeated false allegations                            │
│   - Violations committed: 12                                       │
│                                                                     │
│ Output: events, profiles tables                                    │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ TIER 6: JUDICIAL ASSESSMENT                                        │
│                                                                     │
│ Purpose: Final synthesis and report                                │
│ Granularity: FINAL-ASSESSMENT-LEVEL                                │
│                                                                     │
│ Synthesizes:                                                       │
│   ✓ All violations found (Tier 3)                                 │
│   ✓ Case law precedent (Tier 4)                                   │
│   ✓ Macro analysis results (Tier 2)                               │
│   ✓ Pattern analysis (Tier 5)                                     │
│   ✓ Credibility assessments (Tier 5)                              │
│   ✓ Timeline of events (Tier 5)                                   │
│                                                                     │
│ Produces:                                                          │
│   • Executive summary                                              │
│   • Violations summary (by type, party, severity)                 │
│   • Pattern analysis (systematic behavior)                         │
│   • Credibility assessments (per party)                           │
│   • Recommendations                                                │
│   • Truth Score (0-100)                                            │
│   • Justice Score (0-100)                                          │
│   • Legal Credit Score per party (0-100)                          │
│   • Final conclusion                                               │
│                                                                     │
│ Output: judicial_assessment table row + PDF report                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Database Schema

### TIER 1: `micro_analysis`

```sql
CREATE TABLE micro_analysis (
    micro_id BIGSERIAL PRIMARY KEY,
    journal_id BIGINT REFERENCES document_journal,

    document_type TEXT NOT NULL,
    document_date DATE,
    document_title TEXT,
    document_author TEXT,

    -- Extracted data (document-specific)
    critical_statements JSONB,
    entities JSONB,  -- people, agencies, locations
    dates_mentioned JSONB,
    claims JSONB[],
    facts JSONB[],

    extraction_confidence DECIMAL(5,2),

    ready_for_macro_analysis BOOLEAN DEFAULT TRUE,
    needs_manual_review BOOLEAN DEFAULT FALSE
);
```

**Example row (police report):**
```json
{
  "micro_id": 1,
  "journal_id": 123,
  "document_type": "police_report",
  "critical_statements": {
    "officer_name": "John Smith",
    "badge_number": "12345",
    "incident_date": "2023-01-15",
    "statements": [
      {"speaker": "Officer Smith", "statement": "No signs of abuse observed"},
      {"speaker": "Father", "statement": "Child was beaten"}
    ],
    "disposition": "unfounded"
  },
  "entities": {
    "people": [
      {"name": "Officer John Smith", "role": "police"},
      {"name": "Father", "role": "parent"}
    ]
  },
  "extraction_confidence": 92.5
}
```

### TIER 2: `macro_analysis`

```sql
CREATE TABLE macro_analysis (
    macro_id BIGSERIAL PRIMARY KEY,

    analysis_type TEXT NOT NULL,
    documents_analyzed BIGINT[],

    findings JSONB,
    consistency_score DECIMAL(5,2),
    reliability_score DECIMAL(5,2),
    cross_references JSONB[],
    patterns JSONB[],
    legal_relevancy_score DECIMAL(5,2),

    potential_violations_detected BOOLEAN DEFAULT FALSE
);
```

**Example row (ex parte verification):**
```json
{
  "macro_id": 1,
  "analysis_type": "ex_parte_verification",
  "documents_analyzed": [123, 124, 125],
  "findings": {
    "ex_parte_journal_id": 123,
    "claims_made": [
      {"claim": "immediate danger", "supported": false, "evidence": "none"},
      {"claim": "denied visitation", "supported": false, "evidence": "contradicted by texts"}
    ],
    "fraudulent_filing_likelihood": 0.85
  },
  "consistency_score": 15.0,
  "legal_relevancy_score": 95.0,
  "potential_violations_detected": true
}
```

### TIER 3: `violations`

```sql
CREATE TABLE violations (
    violation_id BIGSERIAL PRIMARY KEY,
    macro_analysis_id BIGINT REFERENCES macro_analysis,

    violation_type TEXT NOT NULL,
    violation_severity TEXT,
    violator_name TEXT,
    violation_date DATE,
    violated_law_or_order TEXT,

    evidence_documents BIGINT[],
    false_statements JSONB[],

    confidence_score DECIMAL(5,2),
    recommended_action TEXT
);
```

**Example row:**
```json
{
  "violation_id": 1,
  "violation_type": "fraud_upon_court",
  "violation_severity": "severe",
  "violator_name": "John Doe",
  "violation_date": "2023-02-05",
  "violated_law_or_order": "Fraud upon the Court",
  "evidence_documents": [123, 124, 125],
  "false_statements": [
    {
      "statement": "Mother denied all visitation",
      "truth": "Mother offered visitation, father declined",
      "evidence_journal_ids": [124, 125]
    }
  ],
  "confidence_score": 85.0,
  "recommended_action": "Sanctions, costs, referral for investigation"
}
```

### TIER 5: `events` (Timeline)

```sql
CREATE TABLE events (
    event_id BIGSERIAL PRIMARY KEY,

    event_date DATE NOT NULL,
    event_type TEXT NOT NULL,
    event_title TEXT,
    event_description TEXT,

    participants JSONB[],
    source_documents BIGINT[],

    related_violations BIGINT[],
    related_case_law BIGINT[],

    significance_score DECIMAL(5,2),
    verified BOOLEAN DEFAULT FALSE,
    contradicted BOOLEAN DEFAULT FALSE
);
```

### TIER 5: `profiles`

```sql
CREATE TABLE profiles (
    profile_id BIGSERIAL PRIMARY KEY,

    person_name TEXT NOT NULL,
    person_role TEXT NOT NULL,

    behavior_patterns JSONB[],
    statements_made JSONB[],

    truthfulness_score DECIMAL(5,2),
    consistency_score DECIMAL(5,2),
    credibility_score DECIMAL(5,2),

    violations_committed BIGINT[]
);
```

### TIER 6: `judicial_assessment`

```sql
CREATE TABLE judicial_assessment (
    assessment_id BIGSERIAL PRIMARY KEY,

    assessment_name TEXT NOT NULL,
    assessment_date DATE NOT NULL,

    violations_found BIGINT[],
    case_law_applied BIGINT[],

    patterns_identified JSONB[],
    credibility_assessments JSONB[],

    truth_score INTEGER,
    justice_score INTEGER,
    legal_credit_scores JSONB,

    final_conclusion TEXT
);
```

---

## 🔄 Workflow Example

### Example: Analyzing Ex Parte Filing

**Documents:**
1. Ex parte request (filed by Father)
2. Police report from same date
3. Medical report from same date
4. Text messages between parents

**Step 1: TIER 1 - Micro Analysis**

Run micro analysis on each document:

```bash
python3 tiered_analyzer.py micro 1  # Ex parte
python3 tiered_analyzer.py micro 2  # Police report
python3 tiered_analyzer.py micro 3  # Medical report
python3 tiered_analyzer.py micro 4  # Text messages
```

**Extracted (Tier 1):**

*Ex parte (journal_id=1):*
```json
{
  "critical_statements": {
    "filing_party": "Father",
    "claims": [
      "Mother denied all visitation",
      "Child is in immediate danger",
      "Emergency custody needed"
    ],
    "evidence_cited": ["police report", "medical report"]
  }
}
```

*Police report (journal_id=2):*
```json
{
  "critical_statements": {
    "officer_name": "Officer Smith",
    "disposition": "unfounded",
    "findings": "No evidence of abuse or danger",
    "statements": [
      {"speaker": "Officer", "statement": "Child appears healthy and safe"}
    ]
  }
}
```

*Medical report (journal_id=3):*
```json
{
  "critical_statements": {
    "doctor_name": "Dr. Jane Doe",
    "findings": "No injuries observed",
    "diagnosis": "Child is healthy"
  }
}
```

*Text messages (journal_id=4):*
```json
{
  "critical_statements": {
    "messages": [
      {"from": "Mother", "to": "Father", "date": "2023-01-20", "text": "You can pick up child at 3pm today"},
      {"from": "Father", "to": "Mother", "date": "2023-01-20", "text": "I'm busy, maybe next week"}
    ]
  }
}
```

**Step 2: TIER 2 - Macro Analysis**

Cross-reference the ex parte against supporting evidence:

```bash
python3 tiered_analyzer.py macro 1,2,3,4 --type ex_parte_verification
```

**Macro Analysis Result:**
```json
{
  "analysis_type": "ex_parte_verification",
  "findings": {
    "claims_verification": [
      {
        "claim": "Mother denied all visitation",
        "supported": false,
        "contradiction": "Text messages show Mother offered visitation, Father declined"
      },
      {
        "claim": "Child is in immediate danger",
        "supported": false,
        "contradiction": "Police report and medical report show no danger"
      }
    ],
    "fraudulent_filing_likelihood": 0.95
  },
  "consistency_score": 5.0,
  "potential_violations_detected": true
}
```

**Step 3: TIER 3 - Violation Detection**

Detect violations based on macro analysis:

```bash
python3 tiered_analyzer.py violations <macro_id>
```

**Violations Detected:**
```json
{
  "violation_type": "fraud_upon_court",
  "violator_name": "Father",
  "violated_law_or_order": "Fraud upon the Court",
  "false_statements": [
    {
      "statement": "Mother denied all visitation",
      "truth": "Mother offered visitation, Father declined",
      "evidence": [4]
    },
    {
      "statement": "Child is in immediate danger",
      "truth": "No danger found by police or doctor",
      "evidence": [2, 3]
    }
  ],
  "confidence_score": 95.0,
  "recommended_action": "Sanctions, attorney fees, referral for investigation"
}
```

**Step 4: TIER 5 - Build Timeline & Profile**

Add this event to timeline and update Father's profile:

*Event added:*
```json
{
  "event_date": "2023-02-05",
  "event_type": "court_filing",
  "event_title": "Ex Parte Filing (fraudulent)",
  "related_violations": [1],
  "significance_score": 95.0
}
```

*Profile updated:*
```json
{
  "person_name": "Father",
  "truthfulness_score": 15.0,  // decreased
  "consistency_score": 20.0,   // decreased
  "credibility_score": 18.0,   // decreased
  "violations_committed": [1, 5, 12],  // added new
  "behavior_patterns": [
    {
      "pattern": "repeated_false_ex_parte_filings",
      "frequency": 3,
      "severity": "severe"
    }
  ]
}
```

**Step 5: TIER 6 - Judicial Assessment**

Generate final assessment report synthesizing everything.

---

## 🎯 Use Cases

### Use Case 1: Detecting Perjury

**Scenario:** Father testifies under oath that "Mother never allowed visitation"

**Tier 1:** Extract sworn statement from declaration
**Tier 2:** Cross-reference with:
- Text messages showing Mother offered visitation
- Calendar showing Father declined scheduled visits
- Police report showing Father admitted he was "too busy"

**Tier 3:** Detect perjury violation (false statement under oath + proof)
**Tier 6:** Recommend perjury charges

### Use Case 2: Pattern of False Allegations

**Scenario:** Multiple allegations made over 2 years

**Tier 1:** Extract each allegation from each document
**Tier 2:** Cross-reference each with investigation results
**Tier 3:** Detect repeated false allegations
**Tier 5:** Build timeline showing pattern
**Tier 6:** Conclude systematic abuse of court process

### Use Case 3: Ex Parte Fraud Detection

**Scenario:** Ex parte claims "immediate danger" without evidence

**Tier 1:** Extract ex parte claims
**Tier 2:** Verify each claim against evidence
**Tier 3:** Detect fraud upon court
**Tier 6:** Recommend sanctions and custody modification

---

## 📈 Scoring Systems

### Truth Score (0-100)

Measures overall truthfulness of case presentation:
- 90-100: Highly truthful, well-supported
- 70-89: Mostly truthful, some inconsistencies
- 50-69: Mixed accuracy
- 30-49: Significant falsehoods
- 0-29: Predominantly false

### Justice Score (0-100)

Measures alignment with justice principles:
- Did the system protect the child?
- Were violations detected and addressed?
- Was evidence properly considered?

### Legal Credit Score (Per Party, 0-100)

Measures party's legal conduct:
- Truthfulness in filings
- Compliance with orders
- Good faith in litigation
- Respect for process

**Example:**
```json
{
  "Father": {
    "score": 15,
    "reasoning": "12 violations, repeated false statements, fraud upon court"
  },
  "Mother": {
    "score": 85,
    "reasoning": "Consistent statements, supported by evidence, no violations"
  }
}
```

---

## 🚀 Deployment

### Step 1: Deploy Schema

```bash
# Deploy tiered analysis schema to Supabase
cd /home/user/ASEAGI
./deploy_queue_schema.sh  # Deploys queue system (already done)

# Now deploy tiered analysis schema
# Open Supabase Dashboard → SQL Editor
# Copy/paste tiered_analysis_schema.sql
# Click Run
```

### Step 2: Verify Tables

```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
    'micro_analysis',
    'macro_analysis',
    'violations',
    'case_law_citations',
    'legal_codes',
    'events',
    'profiles',
    'judicial_assessment'
  );

-- Should return 8 rows
```

### Step 3: Test Analyzer

```bash
export SUPABASE_URL="https://jvjlhxodmbkodzmggwpu.supabase.co"
export SUPABASE_KEY="your-anon-key"
export OPENAI_API_KEY="sk-proj-your-key"

# Run micro analysis on document
python3 tiered_analyzer.py micro 123

# Run macro analysis on multiple documents
python3 tiered_analyzer.py macro 123,124,125

# Detect violations
python3 tiered_analyzer.py violations 1
```

---

## 📚 API Reference

### TieredAnalyzer Class

```python
from tiered_analyzer import TieredAnalyzer

analyzer = TieredAnalyzer(supabase_url, supabase_key, openai_key)

# Tier 1: Micro analysis
result = analyzer.micro_analyze_document(journal_id=123)

# Tier 2: Macro analysis
result = analyzer.macro_analyze_cross_reference(
    document_ids=[123, 124, 125],
    analysis_type='ex_parte_verification'
)

# Tier 3: Violation detection
violations = analyzer.detect_violations(macro_analysis_id=1)

# Tier 5: Timeline building
events = analyzer.build_timeline(journal_ids=[123, 124, 125])

# Tier 5: Profile building
profiles = analyzer.build_profiles(journal_ids=[123, 124, 125])
```

---

## 🔍 Monitoring

View analysis progress:

```sql
-- Documents ready for micro analysis
SELECT * FROM documents_ready_for_micro_analysis;

-- Micro analyses ready for macro
SELECT * FROM micro_analyses_ready_for_macro;

-- Violations pending review
SELECT * FROM violations_pending_review;

-- Timeline view
SELECT * FROM timeline_view;

-- Party credibility summary
SELECT * FROM party_credibility_summary;
```

---

## ✅ Benefits

1. **Granular Analysis** - Extract every detail from every document
2. **Cross-Reference Capability** - Compare across documents
3. **Violation Detection** - Automatic detection of legal violations
4. **Pattern Recognition** - Identify systematic behavior
5. **Complete Timeline** - 2-3 year comprehensive picture
6. **Credibility Tracking** - Score each party's truthfulness
7. **Legal Citations** - Link precedents and codes
8. **Final Assessment** - Synthesize everything into report

---

**For Ashe. For Justice. For All Children. 🛡️**
