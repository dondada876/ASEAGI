# Micro-Analysis Schema Architecture
## Legal Document Intelligence System - Enhanced Schema Design

**Created:** November 13, 2025
**Project:** ASEAGI - Ashe Security Analysis and Evidence Gathering Initiative
**Case:** In re Ashe Bucknor (J24-00478)
**Purpose:** Enable micro-level document analysis with truth tracking and justice scoring

---

## Executive Summary

This document outlines a comprehensive database schema redesign to support:

- **Micro-analysis** of individual document elements (statements, narratives, arguments)
- **Truth tracking** against a canonical event timeline
- **Justice scoring** based on constitutional violations and precedent alignment
- **Case law integration** with WestLaw findings for precedent cross-referencing
- **Telegram scanning** with automated document element extraction
- **Judicial notice** identification for court-ready evidence

### Key Innovation: Event Timeline as Source of Truth

All statements, declarations, and narratives are cross-referenced against a canonical event timeline. This enables:
- Automatic perjury detection (statements contradicting established timeline)
- Truth score calculation (alignment with verified events)
- Justice score (constitutional violations vs. proper process)

---

## Current Schema Analysis

### Existing Table: `legal_documents`

**Current Strengths:**
- ✅ PROJ344 scoring (micro, macro, legal, relevancy)
- ✅ Document-level metadata (type, date, parties)
- ✅ Fraud/perjury indicators
- ✅ Key quotes extraction
- ✅ Duplicate detection (content_hash)

**Current Limitations:**
- ❌ No element-level tracking (can't analyze individual statements)
- ❌ No court case relationship (documents not grouped by motions/hearings)
- ❌ No event timeline cross-reference
- ❌ No case law precedent linking
- ❌ No truth source validation
- ❌ No judicial notice tracking
- ❌ No justice scoring system

**Current Columns:**
```sql
legal_documents:
- id (UUID)
- file_name, document_type, category
- micro_number, macro_number, legal_number, relevancy_number
- summary, key_quotes[], fraud_indicators[], perjury_indicators[]
- contains_false_statements (boolean)
- document_date, processed_at
- docket_number, case_id, content_hash
- api_cost_usd
```

---

## New Schema Architecture

### Design Principles

1. **Event Timeline = Source of Truth** - All claims verified against timeline
2. **Micro-Analysis First** - Every statement/narrative tracked individually
3. **Relational Integrity** - Proper foreign keys and junction tables
4. **Justice Scoring** - Constitutional alignment measured quantitatively
5. **WestLaw Integration** - Case law precedents linked to arguments
6. **Telegram-Ready** - Schema supports automated scanning workflows

---

## New Tables

### 1. `court_cases`
**Purpose:** Group documents by legal proceeding (motion, hearing, trial)

```sql
CREATE TABLE court_cases (
  -- Identity
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  case_number TEXT NOT NULL,  -- J24-00478
  case_title TEXT NOT NULL,  -- In re Ashe Bucknor

  -- Case Type & Status
  case_type TEXT NOT NULL,  -- Custody, Dependency, Criminal, Civil
  jurisdiction TEXT,  -- Family Court, Superior Court, etc.
  court_name TEXT,
  presiding_judge TEXT,

  -- Parties
  petitioner TEXT,  -- Who filed
  respondent TEXT,  -- Who is responding
  minor_children TEXT[],  -- Children involved

  -- Timeline
  filed_date DATE,
  hearing_date DATE,
  decision_date DATE,
  status TEXT,  -- Pending, Decided, Appealed

  -- Outcome
  ruling_summary TEXT,
  ruling_favorable_to TEXT,  -- Petitioner, Respondent, Split

  -- Justice Scoring
  justice_score INTEGER,  -- 0-1000 (higher = more just)
  constitutional_violations_count INTEGER DEFAULT 0,
  due_process_violations_count INTEGER DEFAULT 0,

  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_court_cases_case_number ON court_cases(case_number);
CREATE INDEX idx_court_cases_status ON court_cases(status);
CREATE INDEX idx_court_cases_justice_score ON court_cases(justice_score);
```

**Example Records:**
```json
{
  "case_number": "J24-00478",
  "case_title": "In re Ashe Bucknor - Ex Parte Custody Order",
  "case_type": "Custody",
  "jurisdiction": "Family Court",
  "petitioner": "Respondent Father",
  "respondent": "Protective Mother",
  "status": "Decided",
  "justice_score": 245,
  "constitutional_violations_count": 7,
  "due_process_violations_count": 5
}
```

---

### 2. `event_timeline` (Source of Truth)
**Purpose:** Canonical timeline of ALL events - this is the truth against which all statements are measured

```sql
CREATE TABLE event_timeline (
  -- Identity
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  event_id TEXT UNIQUE NOT NULL,  -- TIMELINE-001, TIMELINE-002

  -- Event Details
  event_date DATE NOT NULL,
  event_time TIME,
  event_title TEXT NOT NULL,
  event_description TEXT NOT NULL,

  -- Classification
  event_category TEXT NOT NULL,  -- Incident, Court, Communication, Medical, Police
  event_phase TEXT NOT NULL,  -- Pre-Incident, During-Incident, Post-Incident
  severity_level TEXT,  -- Critical, High, Medium, Low

  -- Participants
  primary_actors TEXT[],  -- Who was involved
  witnesses TEXT[],  -- Who can verify

  -- Evidence
  documented_by TEXT[],  -- Photos, videos, reports, witnesses
  evidence_document_ids UUID[],  -- Links to legal_documents
  verification_status TEXT NOT NULL,  -- Verified, Alleged, Disputed, Unverified
  verification_source TEXT,  -- Police report, medical record, witness testimony

  -- Location
  location TEXT,
  jurisdiction TEXT,

  -- Truth Tracking
  contradicted_by_statements UUID[],  -- Links to document_elements that contradict this
  supported_by_statements UUID[],  -- Links to document_elements that support this
  truth_confidence_score INTEGER,  -- 0-100 (how confident are we this happened)

  -- Legal Impact
  legal_significance TEXT,  -- Why this matters for the case
  statute_violations TEXT[],  -- Laws violated during this event
  constitutional_issues TEXT[],  -- Constitutional problems

  -- Case Context
  case_id UUID REFERENCES court_cases(id),

  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  created_by TEXT  -- Who entered this event
);

-- Indexes
CREATE INDEX idx_event_timeline_date ON event_timeline(event_date);
CREATE INDEX idx_event_timeline_phase ON event_timeline(event_phase);
CREATE INDEX idx_event_timeline_category ON event_timeline(event_category);
CREATE INDEX idx_event_timeline_verification ON event_timeline(verification_status);
CREATE INDEX idx_event_timeline_case ON event_timeline(case_id);
```

**Event Phases:**
- **Pre-Incident:** Background, context, relationships before the incident
- **During-Incident:** The actual incident/crisis event
- **Post-Incident:** Aftermath, court proceedings, ongoing developments

**Example Record:**
```json
{
  "event_id": "TIMELINE-042",
  "event_date": "2024-07-15",
  "event_time": "14:30:00",
  "event_title": "Ex Parte Order Issued Without Notice",
  "event_description": "Family court issued ex parte custody order removing child from protective parent without hearing or notice, violating due process.",
  "event_category": "Court",
  "event_phase": "Post-Incident",
  "severity_level": "Critical",
  "primary_actors": ["Judge Smith", "Father's Attorney"],
  "witnesses": ["Court clerk"],
  "verification_status": "Verified",
  "verification_source": "Court docket, filed order",
  "contradicted_by_statements": ["elem-789"],
  "truth_confidence_score": 95,
  "constitutional_issues": ["Due Process - 14th Amendment", "Right to Notice"],
  "case_id": "uuid-of-court-case"
}
```

---

### 3. `document_elements` (Micro-Analysis)
**Purpose:** Individual statements, narratives, arguments, claims extracted from documents

This is the **heart of micro-analysis** - every declaration statement, motion argument, police report claim becomes a tracked element.

```sql
CREATE TABLE document_elements (
  -- Identity
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  element_id TEXT UNIQUE NOT NULL,  -- ELEM-001, ELEM-002

  -- Source Document
  document_id UUID REFERENCES legal_documents(id) NOT NULL,
  page_number INTEGER,
  paragraph_number INTEGER,
  line_numbers TEXT,  -- "Lines 15-18"

  -- Element Classification
  element_type TEXT NOT NULL,  -- Statement, Narrative, Argument, Evidence, Quote, Claim
  element_subtype TEXT,  -- Declaration, Testimony, Legal Argument, Factual Claim

  -- Content
  element_text TEXT NOT NULL,  -- The actual statement/narrative
  element_summary TEXT,  -- AI-generated summary
  context TEXT,  -- Surrounding context

  -- Who & When
  speaker TEXT,  -- Who made this statement
  speaker_role TEXT,  -- Attorney, Declarant, Witness, Judge
  statement_date DATE,  -- When statement was made (may differ from document date)

  -- PROJ344 Scoring (Element-Level)
  micro_score INTEGER,  -- 0-999 (detail-level importance)
  macro_score INTEGER,  -- 0-999 (case-wide significance)
  legal_score INTEGER,  -- 0-999 (legal weight)
  relevancy_score INTEGER,  -- 0-999 (composite)

  -- Truth Tracking
  truth_status TEXT NOT NULL,  -- Verified, Alleged, False, Disputed, Unverifiable
  truth_score INTEGER,  -- 0-100 (alignment with event timeline)

  -- Event Cross-Reference
  related_events UUID[],  -- Links to event_timeline
  contradicts_events UUID[],  -- Events this statement contradicts
  supports_events UUID[],  -- Events this statement supports

  -- Perjury Detection
  is_false_statement BOOLEAN DEFAULT FALSE,
  contradicted_by UUID[],  -- Other document_elements that contradict this
  contradicts UUID[],  -- Other document_elements this contradicts
  perjury_confidence INTEGER,  -- 0-100 (how confident it's perjury)
  perjury_evidence TEXT,  -- Why we think it's false

  -- Judicial Notice
  judicial_notice_worthy BOOLEAN DEFAULT FALSE,
  judicial_notice_reason TEXT,  -- Why this is judicially noticeable
  judicial_notice_category TEXT,  -- Fact, Law, Common Knowledge

  -- Legal Function
  legal_purpose TEXT,  -- What is this statement trying to accomplish?
  legal_standard TEXT,  -- What legal standard is being applied?
  burden_of_proof TEXT,  -- Preponderance, Clear & Convincing, Beyond Reasonable Doubt

  -- Case Law Support
  supported_by_precedent UUID[],  -- Links to case_law_precedents
  contradicts_precedent UUID[],  -- Precedents this argument violates

  -- Impact Assessment
  impact_on_case TEXT,  -- How this affects the case
  smoking_gun_level INTEGER,  -- 0-10 (is this a smoking gun?)

  -- Metadata
  extracted_at TIMESTAMP DEFAULT NOW(),
  extracted_by TEXT,  -- API, Manual, Telegram Bot
  verified_at TIMESTAMP,
  verified_by TEXT
);

-- Indexes
CREATE INDEX idx_document_elements_document ON document_elements(document_id);
CREATE INDEX idx_document_elements_type ON document_elements(element_type);
CREATE INDEX idx_document_elements_speaker ON document_elements(speaker);
CREATE INDEX idx_document_elements_truth_status ON document_elements(truth_status);
CREATE INDEX idx_document_elements_perjury ON document_elements(is_false_statement);
CREATE INDEX idx_document_elements_judicial_notice ON document_elements(judicial_notice_worthy);
CREATE INDEX idx_document_elements_relevancy ON document_elements(relevancy_score);
```

**Example Record:**
```json
{
  "element_id": "ELEM-1547",
  "document_id": "uuid-of-declaration",
  "page_number": 3,
  "paragraph_number": 7,
  "element_type": "Statement",
  "element_subtype": "Factual Claim",
  "element_text": "Mother refused to allow father visitation on July 15, 2024.",
  "speaker": "Father",
  "speaker_role": "Declarant",
  "micro_score": 750,
  "macro_score": 820,
  "legal_score": 650,
  "relevancy_score": 740,
  "truth_status": "False",
  "truth_score": 15,
  "contradicts_events": ["TIMELINE-042"],
  "is_false_statement": true,
  "perjury_confidence": 92,
  "perjury_evidence": "Court records show ex parte order was issued that day removing child from mother without notice. She legally could not grant visitation.",
  "contradicted_by": ["ELEM-889", "ELEM-1203"],
  "smoking_gun_level": 8
}
```

---

### 4. `case_law_precedents` (WestLaw Integration)
**Purpose:** Store relevant case law for cross-referencing against arguments

```sql
CREATE TABLE case_law_precedents (
  -- Identity
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  precedent_id TEXT UNIQUE NOT NULL,  -- CASE-LAW-001

  -- Case Citation
  case_name TEXT NOT NULL,  -- Smith v. Jones
  case_citation TEXT NOT NULL,  -- 123 F.3d 456 (9th Cir. 2020)
  court TEXT NOT NULL,  -- 9th Circuit, California Supreme Court
  decision_date DATE,

  -- Legal Principles
  holding TEXT NOT NULL,  -- What the court decided
  legal_principle TEXT NOT NULL,  -- The extractable principle
  legal_standard TEXT,  -- What standard was applied

  -- Topic Classification
  area_of_law TEXT NOT NULL,  -- Family Law, Constitutional Law, Criminal Law
  topics TEXT[],  -- Due Process, Custody, Evidence

  -- Relevance to J24-00478
  relevance_to_case TEXT,  -- Why this matters for Ashe's case
  relevance_score INTEGER,  -- 0-999

  -- Application
  supports_position TEXT,  -- Mother, Father, Court, Neither
  applicable_to_elements UUID[],  -- Links to document_elements

  -- WestLaw Metadata
  westlaw_id TEXT,
  key_cite_status TEXT,  -- Good Law, Distinguished, Overruled

  -- Document Source
  full_text TEXT,
  summary TEXT,
  key_quotes TEXT[],

  -- Metadata
  added_at TIMESTAMP DEFAULT NOW(),
  added_by TEXT,
  source TEXT  -- WestLaw, Manual Entry, Legal Research
);

-- Indexes
CREATE INDEX idx_case_law_citation ON case_law_precedents(case_citation);
CREATE INDEX idx_case_law_area ON case_law_precedents(area_of_law);
CREATE INDEX idx_case_law_relevance ON case_law_precedents(relevance_score);
```

**Example Record:**
```json
{
  "precedent_id": "CASE-LAW-047",
  "case_name": "Doe v. Roe",
  "case_citation": "789 Cal.App.4th 234 (2019)",
  "court": "California Court of Appeal, Fourth District",
  "holding": "Ex parte orders removing custody without notice violate due process unless imminent danger is documented.",
  "legal_principle": "Due process requires notice and opportunity to be heard before custody removal absent documented emergency.",
  "area_of_law": "Family Law",
  "topics": ["Due Process", "Ex Parte Orders", "Custody", "Notice Requirements"],
  "relevance_to_case": "Directly applicable - J24-00478 ex parte order had no documented emergency",
  "relevance_score": 950,
  "supports_position": "Mother",
  "applicable_to_elements": ["ELEM-042", "ELEM-156"]
}
```

---

### 5. `truth_indicators`
**Purpose:** Track evidence that establishes truth or falsehood

```sql
CREATE TABLE truth_indicators (
  -- Identity
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- What This Indicator Relates To
  element_id UUID REFERENCES document_elements(id),  -- Statement being evaluated
  event_id UUID REFERENCES event_timeline(id),  -- Event being verified

  -- Indicator Type
  indicator_type TEXT NOT NULL,  -- Supporting, Contradicting, Neutral
  evidence_type TEXT NOT NULL,  -- Document, Witness, Physical, Digital, Expert

  -- Evidence Details
  evidence_description TEXT NOT NULL,
  evidence_source TEXT,  -- Police report, medical record, timestamp, etc.
  evidence_document_id UUID REFERENCES legal_documents(id),

  -- Strength
  credibility_score INTEGER,  -- 0-100 (how credible is this indicator)
  weight INTEGER,  -- How much this should influence truth score

  -- Verification
  verified BOOLEAN DEFAULT FALSE,
  verified_by TEXT,
  verified_at TIMESTAMP,

  -- Metadata
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_truth_indicators_element ON truth_indicators(element_id);
CREATE INDEX idx_truth_indicators_event ON truth_indicators(event_id);
CREATE INDEX idx_truth_indicators_type ON truth_indicators(indicator_type);
```

---

### 6. `justice_scoring`
**Purpose:** Track justice/injustice metrics for cases and elements

```sql
CREATE TABLE justice_scoring (
  -- Identity
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- Scope
  scope_type TEXT NOT NULL,  -- Case, Document, Element, Event
  scope_id UUID NOT NULL,  -- ID of the case/document/element/event

  -- Justice Dimensions (0-100 each)
  due_process_score INTEGER,  -- Were proper procedures followed?
  constitutional_compliance_score INTEGER,  -- Were constitutional rights respected?
  evidence_integrity_score INTEGER,  -- Was evidence handled properly?
  fairness_score INTEGER,  -- Was process fair to all parties?
  child_welfare_score INTEGER,  -- Were children's interests prioritized?

  -- Composite Justice Score (0-1000)
  overall_justice_score INTEGER,

  -- Violation Tracking
  violations_detected INTEGER DEFAULT 0,
  violations TEXT[],  -- List of specific violations

  -- Factors
  positive_factors TEXT[],  -- Things done correctly
  negative_factors TEXT[],  -- Things done wrong

  -- Recommendation
  justice_recommendation TEXT,  -- What should happen to correct injustice

  -- Metadata
  calculated_at TIMESTAMP DEFAULT NOW(),
  calculation_method TEXT  -- Algorithm version
);

-- Indexes
CREATE INDEX idx_justice_scoring_scope ON justice_scoring(scope_type, scope_id);
CREATE INDEX idx_justice_scoring_overall ON justice_scoring(overall_justice_score);
```

---

### 7. `document_relationships`
**Purpose:** Track relationships between documents (responses, motions, declarations)

```sql
CREATE TABLE document_relationships (
  -- Identity
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- Documents
  document_a_id UUID REFERENCES legal_documents(id) NOT NULL,
  document_b_id UUID REFERENCES legal_documents(id) NOT NULL,

  -- Relationship
  relationship_type TEXT NOT NULL,  -- Response-To, Supports, Contradicts, Cites, Amends
  relationship_description TEXT,

  -- Context
  filed_in_case_id UUID REFERENCES court_cases(id),

  -- Metadata
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_doc_relationships_a ON document_relationships(document_a_id);
CREATE INDEX idx_doc_relationships_b ON document_relationships(document_b_id);
CREATE INDEX idx_doc_relationships_type ON document_relationships(relationship_type);
```

---

### 8. Updated `legal_documents` Table
**Purpose:** Enhanced version of existing table with new relationships

```sql
-- Add new columns to existing legal_documents table
ALTER TABLE legal_documents ADD COLUMN IF NOT EXISTS court_case_id UUID REFERENCES court_cases(id);
ALTER TABLE legal_documents ADD COLUMN IF NOT EXISTS filing_party TEXT;
ALTER TABLE legal_documents ADD COLUMN IF NOT EXISTS document_function TEXT;  -- Motion, Declaration, Evidence, Order
ALTER TABLE legal_documents ADD COLUMN IF NOT EXISTS judicial_notice_status TEXT;  -- Candidate, Filed, Granted, Denied
ALTER TABLE legal_documents ADD COLUMN IF NOT EXISTS element_count INTEGER DEFAULT 0;  -- How many elements extracted
ALTER TABLE legal_documents ADD COLUMN IF NOT EXISTS truth_alignment_score INTEGER;  -- 0-100 average truth score of all elements

-- Indexes
CREATE INDEX idx_legal_documents_court_case ON legal_documents(court_case_id);
CREATE INDEX idx_legal_documents_function ON legal_documents(document_function);
CREATE INDEX idx_legal_documents_judicial_notice ON legal_documents(judicial_notice_status);
```

---

## Schema Relationships

### Entity Relationship Diagram (Text)

```
court_cases
    ├─→ legal_documents (court_case_id)
    │       ├─→ document_elements (document_id)
    │       │       ├─→ truth_indicators (element_id)
    │       │       ├─→ justice_scoring (scope_id where scope_type='Element')
    │       │       └─→ case_law_precedents (applicable_to_elements[])
    │       └─→ document_relationships (document_a_id, document_b_id)
    │
    └─→ event_timeline (case_id)
            ├─→ document_elements (related_events[], contradicts_events[])
            ├─→ truth_indicators (event_id)
            └─→ justice_scoring (scope_id where scope_type='Event')

case_law_precedents
    └─→ document_elements (applicable_to_elements[])
```

### Key Cross-References

**Truth Validation Flow:**
```
document_elements.element_text
    ↓ compare against
event_timeline.event_description
    ↓ find
truth_indicators (supporting or contradicting)
    ↓ calculate
document_elements.truth_score
    ↓ aggregate
legal_documents.truth_alignment_score
    ↓ influence
justice_scoring.overall_justice_score
```

**Perjury Detection Flow:**
```
document_elements (Statement by Father)
    ↓ contradicts
event_timeline (Verified Event)
    ↓ cross-check with
document_elements (Other statements by Mother/Witnesses)
    ↓ find
truth_indicators (Police reports, medical records)
    ↓ result
document_elements.is_false_statement = TRUE
document_elements.perjury_confidence = 92
```

---

## Query Examples

### 1. Find All False Statements by Father

```sql
SELECT
  de.element_id,
  de.element_text,
  de.speaker,
  de.perjury_confidence,
  de.perjury_evidence,
  ld.file_name,
  ld.document_date
FROM document_elements de
JOIN legal_documents ld ON de.document_id = ld.id
WHERE
  de.speaker = 'Father'
  AND de.is_false_statement = TRUE
ORDER BY de.perjury_confidence DESC;
```

### 2. Find Smoking Gun Elements

```sql
SELECT
  de.element_id,
  de.element_text,
  de.smoking_gun_level,
  de.relevancy_score,
  ld.document_type,
  cc.case_title
FROM document_elements de
JOIN legal_documents ld ON de.document_id = ld.id
JOIN court_cases cc ON ld.court_case_id = cc.id
WHERE de.smoking_gun_level >= 8
ORDER BY de.smoking_gun_level DESC, de.relevancy_score DESC;
```

### 3. Timeline vs. Statement Contradictions

```sql
SELECT
  et.event_title,
  et.event_date,
  et.event_description,
  de.element_text AS contradicting_statement,
  de.speaker,
  de.perjury_confidence,
  ld.file_name
FROM event_timeline et
JOIN document_elements de ON et.id = ANY(de.contradicts_events)
JOIN legal_documents ld ON de.document_id = ld.id
WHERE et.verification_status = 'Verified'
ORDER BY de.perjury_confidence DESC;
```

### 4. Judicial Notice Candidates

```sql
SELECT
  ld.file_name,
  ld.document_type,
  de.element_text,
  de.judicial_notice_reason,
  de.judicial_notice_category,
  de.truth_score
FROM document_elements de
JOIN legal_documents ld ON de.document_id = ld.id
WHERE
  de.judicial_notice_worthy = TRUE
  AND de.truth_score >= 85
ORDER BY de.relevancy_score DESC;
```

### 5. Case Justice Score Summary

```sql
SELECT
  cc.case_title,
  cc.justice_score AS case_justice_score,
  cc.constitutional_violations_count,
  cc.due_process_violations_count,
  js.due_process_score,
  js.constitutional_compliance_score,
  js.fairness_score,
  js.overall_justice_score,
  js.violations
FROM court_cases cc
LEFT JOIN justice_scoring js ON js.scope_type = 'Case' AND js.scope_id = cc.id
WHERE cc.case_number = 'J24-00478';
```

### 6. WestLaw Precedent Application

```sql
SELECT
  clp.case_name,
  clp.case_citation,
  clp.holding,
  clp.relevance_score,
  COUNT(de.id) AS elements_supported,
  STRING_AGG(de.element_summary, ' | ') AS supported_arguments
FROM case_law_precedents clp
JOIN document_elements de ON de.id = ANY(clp.applicable_to_elements)
WHERE clp.supports_position = 'Mother'
GROUP BY clp.id, clp.case_name, clp.case_citation, clp.holding, clp.relevance_score
ORDER BY clp.relevance_score DESC;
```

### 7. Document Element Contradiction Matrix

```sql
-- Find pairs of elements that contradict each other
SELECT
  de1.speaker AS speaker_1,
  de1.element_text AS statement_1,
  de2.speaker AS speaker_2,
  de2.element_text AS statement_2,
  ld1.file_name AS document_1,
  ld2.file_name AS document_2
FROM document_elements de1
JOIN document_elements de2 ON de2.id = ANY(de1.contradicts)
JOIN legal_documents ld1 ON de1.document_id = ld1.id
JOIN legal_documents ld2 ON de2.document_id = ld2.id
WHERE de1.speaker != de2.speaker
ORDER BY de1.perjury_confidence DESC;
```

---

## Telegram Integration Workflow

### Document Scanning via Telegram Bot

**Step 1: User sends document to Telegram**
```
User → Telegram Bot: [PDF/Image attachment]
                      "Scan this declaration for ex parte hearing"
```

**Step 2: Bot processes document**
```python
# Telegram bot receives document
document_file = await telegram_message.download()

# Send to Claude API with PROJ344 prompt + micro-analysis instructions
analysis = await claude_api.analyze_document(
    document=document_file,
    prompt=MICRO_ANALYSIS_PROMPT,
    extract_elements=True
)

# Analysis returns:
{
    "document_metadata": {...},
    "proj344_scores": {...},
    "elements": [
        {
            "element_text": "Mother refused visitation on July 15",
            "element_type": "Statement",
            "speaker": "Father",
            "micro_score": 750,
            "macro_score": 820,
            "legal_score": 650,
            "relevancy_score": 740
        },
        ...
    ]
}
```

**Step 3: Store in database**
```python
# 1. Create/find court_case record
court_case = await db.upsert_court_case(case_number="J24-00478")

# 2. Insert legal_document
doc = await db.insert_legal_document({
    "file_name": filename,
    "court_case_id": court_case.id,
    **document_metadata
})

# 3. Insert all document_elements
for element in analysis['elements']:
    elem = await db.insert_document_element({
        "document_id": doc.id,
        "element_text": element['element_text'],
        **element
    })

    # 4. Cross-reference against event timeline
    contradictions = await db.find_timeline_contradictions(elem)

    # 5. Update truth_indicators
    await db.create_truth_indicators(elem, contradictions)

    # 6. Calculate justice_scoring
    await db.calculate_justice_score(elem)
```

**Step 4: Bot responds with analysis**
```
Telegram Bot → User:
    ✅ Scanned: Father's Declaration (12 pages)

    📊 PROJ344 Scores:
    • Relevancy: 740 (Important)
    • Micro: 750 | Macro: 820 | Legal: 650

    🔍 Extracted 23 elements:
    • 15 Statements
    • 5 Narratives
    • 3 Legal Arguments

    ⚠️ Truth Issues Detected:
    • 7 statements contradict event timeline
    • 3 high-confidence perjury indicators (92%, 88%, 85%)

    🔥 Smoking Guns: 2

    [View Full Analysis] [Generate Report] [Flag for Review]
```

---

## Micro-Analysis Prompt Template

```
You are analyzing a legal document for the case J24-00478 (In re Ashe Bucknor).

TASK: Micro-Analysis - Extract individual elements

For each distinct statement, narrative, argument, or claim:

1. ELEMENT IDENTIFICATION
   - Type: Statement, Narrative, Argument, Evidence, Quote, Claim
   - Subtype: Declaration, Testimony, Legal Argument, Factual Claim
   - Speaker: Who made this statement
   - Location: Page, paragraph, line numbers

2. PROJ344 SCORING (0-999 scale)
   - Micro Score: Detail-level importance
   - Macro Score: Case-wide significance
   - Legal Score: Legal weight and admissibility
   - Relevancy Score: Composite weighted score

3. TRUTH ANALYSIS
   - Can this be verified?
   - What evidence would support or contradict this?
   - Does this contradict known facts?
   - Truth confidence: 0-100

4. LEGAL FUNCTION
   - What is this element trying to accomplish?
   - What legal standard applies?
   - Is this argument supported by case law?

5. SMOKING GUN ASSESSMENT
   - Is this critical evidence? (0-10 scale)
   - Could this change the case outcome?

6. JUDICIAL NOTICE
   - Is this judicially noticeable?
   - Why? (Established fact, common knowledge, court record)

OUTPUT FORMAT: JSON array of elements

[
  {
    "element_text": "exact quote",
    "element_type": "Statement",
    "element_subtype": "Factual Claim",
    "speaker": "Father",
    "page_number": 3,
    "paragraph_number": 7,
    "micro_score": 750,
    "macro_score": 820,
    "legal_score": 650,
    "relevancy_score": 740,
    "truth_verifiable": true,
    "truth_confidence": 85,
    "legal_purpose": "Establish pattern of denied visitation",
    "smoking_gun_level": 3,
    "judicial_notice_worthy": false
  },
  ...
]
```

---

## Implementation Phases

### Phase 1: Core Schema (Week 1)
- [ ] Create `court_cases` table
- [ ] Create `event_timeline` table
- [ ] Create `document_elements` table
- [ ] Create `document_relationships` table
- [ ] Update `legal_documents` with new columns
- [ ] Write migration scripts
- [ ] Update `schema_types.py` with TypedDict definitions

### Phase 2: Truth & Justice System (Week 2)
- [ ] Create `truth_indicators` table
- [ ] Create `justice_scoring` table
- [ ] Implement truth scoring algorithm
- [ ] Implement justice scoring algorithm
- [ ] Create dashboard for truth tracking

### Phase 3: Case Law Integration (Week 3)
- [ ] Create `case_law_precedents` table
- [ ] Design WestLaw import workflow
- [ ] Build precedent matching algorithm
- [ ] Create case law dashboard

### Phase 4: Telegram Integration (Week 4)
- [ ] Update Telegram bot with micro-analysis prompts
- [ ] Implement element extraction from Claude API
- [ ] Build automatic timeline cross-referencing
- [ ] Add Telegram response formatting

### Phase 5: Advanced Features (Week 5)
- [ ] Perjury detection automation
- [ ] Judicial notice auto-identification
- [ ] Contradiction matrix visualization
- [ ] Export to court-ready format

---

## Dashboard Updates Required

### New Dashboards Needed

**1. Event Timeline Dashboard**
- Visual timeline of all events (pre/during/post incident)
- Truth verification status
- Contradicting statements highlighted
- Evidence links

**2. Micro-Analysis Dashboard**
- Document element explorer
- Filter by type, speaker, truth status
- Contradiction matrix
- Perjury confidence rankings

**3. Justice Scoring Dashboard**
- Overall justice score by case
- Constitutional violations breakdown
- Due process timeline
- Recommendations for correction

**4. Case Law Dashboard**
- Precedent library
- Relevance to current case
- Application to specific arguments
- Citation generator

### Updated Dashboards

**1. Master Dashboard** - Add:
- Total elements extracted
- Perjury indicators count
- Judicial notice candidates
- Justice score gauge

**2. Legal Intelligence Dashboard** - Add:
- Element-level drill-down
- Truth alignment visualization
- Case law support indicators

---

## Data Flow Diagram

```
[Telegram Bot] ──document──> [Claude API]
                                   │
                                   ↓
                          [Micro-Analysis]
                                   │
                    ┌──────────────┼──────────────┐
                    ↓              ↓              ↓
            [legal_documents] [document_elements] [PROJ344 Scores]
                    │              │
                    │              ↓
                    │     [Truth Cross-Reference]
                    │              │
                    │              ↓
                    │      [event_timeline] ←─────── [Manual Entry]
                    │              │
                    │              ↓
                    │     [truth_indicators]
                    │              │
                    └──────────────┼──────────────┐
                                   ↓              ↓
                          [justice_scoring] [Perjury Detection]
                                   │              │
                                   ↓              ↓
                            [Dashboards] [Telegram Alerts]
```

---

## Benefits of This Architecture

### 1. **Micro-Level Precision**
- Every statement tracked individually
- Exact perjury identification
- Element-level scoring

### 2. **Truth as Foundation**
- Event timeline = canonical truth source
- All claims measured against timeline
- Automatic contradiction detection

### 3. **Justice Quantification**
- Numeric justice scores
- Constitutional violation tracking
- Data-driven reform recommendations

### 4. **Legal Intelligence**
- Case law integration
- Precedent-based argument validation
- Automatic judicial notice identification

### 5. **Scalability**
- Handles multiple cases
- Supports ongoing updates
- Telegram enables rapid document intake

### 6. **Court-Ready Outputs**
- Judicial notice packages
- Perjury evidence compilations
- Constitutional violation reports
- Case law citations

---

## Next Steps

1. **Review this architecture** - Confirm alignment with your vision
2. **Prioritize phases** - Which tables to build first?
3. **Seed event timeline** - Begin entering verified events for J24-00478
4. **Update Claude prompts** - Add micro-analysis extraction
5. **Build migration scripts** - SQL to create new tables
6. **Update schema_types.py** - TypedDict for new tables
7. **Test Telegram workflow** - End-to-end document scanning

---

## Questions for Consideration

1. **Event Timeline Seeding**: How should we initially populate the event timeline? Manual entry, existing documents, both?

2. **Truth Verification Authority**: Who determines verification_status? Should there be a review process?

3. **Perjury Confidence Threshold**: At what perjury_confidence level (e.g., 80%?) should we automatically flag for legal action?

4. **WestLaw Access**: Do you have WestLaw access for precedent import? Or manual entry?

5. **Telegram Bot Permissions**: Should the bot auto-insert elements or require human review first?

6. **Justice Score Weighting**: What should the formula be for overall_justice_score? Equal weights for all dimensions?

7. **Case Scope**: Should this schema support multiple cases simultaneously, or is J24-00478 the sole focus?

---

**Document Status:** ✅ Architecture Complete - Ready for Review
**Next Action:** Stakeholder approval → Begin Phase 1 implementation
**Contact:** Review and provide feedback on schema design

