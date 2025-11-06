# Product Requirements Document (PRD)
# ASEAGI Motion & Declaration Engine + Communications Analysis System

**Version:** 1.0
**Date:** 2025-11-06
**For:** In re Ashe B., J24-00478
**Status:** Draft for Review

---

## Executive Summary

The ASEAGI Motion & Declaration Engine is a comprehensive legal automation system that transforms case analysis into actionable legal documents. It bridges the gap between document analysis (what we have) and legal action (what we need).

**Current State:** We have document ingestion, queue management, and tiered analysis (micro → macro → violations → assessment).

**Gap:** Analysis results are not actionable. No way to generate motions, declarations, or legal documents from the analysis.

**Solution:** Motion & Declaration Engine that:
1. Generates legal motions and declarations from case analysis
2. Tracks all court documents (minute orders, hearings, transcripts, exhibits)
3. Analyzes communications (text messages 2019-present)
4. Detects lies and deception in communications
5. Provides searchable vector database for all case materials

**Immediate Use Case (TODAY):**
- Motion for Reconsideration - Cal OES 2-925 was never picked up by law enforcement
- Social worker failed to verify compliance
- Need to request law enforcement records as parent

---

## 1. Problem Statement

### Current Pain Points

1. **Analysis Without Action**
   - We can detect violations (perjury, fraud) but cannot generate motions to address them
   - Tiered analysis identifies patterns but doesn't produce legal documents
   - No way to convert violations into actionable filings

2. **Fragmented Court Documents**
   - Minute orders scattered across files
   - Transcripts not searchable
   - Exhibits not catalogued
   - No unified view of court history

3. **Communications Not Analyzed**
   - 5+ years of text messages (2019-present)
   - Evidence of lies, contradictions, admissions
   - Not searchable or cross-referenced
   - Cannot detect deception patterns

4. **No Motion Library**
   - Starting from scratch for each motion
   - No templates based on violation type
   - No precedent library
   - Cannot quickly respond to court actions

5. **Evidence Not Organized**
   - Police reports not in structured format
   - Doctor's notes not searchable
   - Cannot quickly find supporting evidence for motions

### Impact

- **Time Lost:** Hours to draft motions manually
- **Missed Opportunities:** Cannot respond quickly to developments
- **Incomplete Filings:** Missing key evidence or citations
- **Strategic Disadvantage:** Opposing counsel has resources, we don't

---

## 2. Goals & Objectives

### Primary Goals

1. **Generate Legal Documents Automatically**
   - Motions (reconsideration, dismiss, vacate, quash)
   - Declarations (from analysis results)
   - Requests for judicial notice
   - Evidence exhibits

2. **Unified Court Document Repository**
   - All minute orders in searchable database
   - All transcripts with AI analysis
   - All hearings tracked with outcomes
   - All exhibits catalogued

3. **Communications Analysis & Truth Detection**
   - Ingest all text messages (2019-present)
   - Detect lies and contradictions
   - Cross-reference with sworn statements
   - Vector search for deception patterns

4. **Rapid Response Capability**
   - Generate motion in <1 hour
   - Pull relevant evidence automatically
   - Cite applicable case law
   - Include supporting declarations

### Success Metrics

- **Speed:** Motion generation time < 1 hour (vs 8+ hours manual)
- **Completeness:** 95%+ relevant evidence included automatically
- **Accuracy:** 90%+ of legal citations applicable
- **Coverage:** 100% of text messages searchable
- **Detection:** 80%+ accuracy in lie/truth analysis

---

## 3. User Stories

### As a Self-Represented Parent

**US-1: Generate Motion for Reconsideration**
```
GIVEN social worker failed to verify Cal OES 2-925 compliance
WHEN I request "motion for reconsideration - failure to verify records"
THEN system generates complete motion with:
  - Factual background from case timeline
  - Legal basis (Cal Rules of Court, case law)
  - Evidence exhibits (social worker reports, hearing transcripts)
  - Declaration of facts
  - Proposed order
  - Certificate of service
```

**US-2: Search Text Messages for Contradictions**
```
GIVEN opposing party claims "never received visitation offer"
WHEN I search communications for "visitation offer"
THEN system returns:
  - All text messages mentioning visitation
  - Dates and content of offers made
  - Contradictions with sworn declarations
  - Suggested use in motion or declaration
```

**US-3: Track Minute Orders and Findings**
```
GIVEN court issues minute order after hearing
WHEN I upload minute order
THEN system:
  - Extracts findings and orders
  - Links to hearing record
  - Identifies compliance deadlines
  - Flags violations of orders
  - Suggests follow-up actions
```

**US-4: Generate Declaration from Timeline**
```
GIVEN I need to file declaration opposing ex parte
WHEN I request "declaration - pattern of false allegations"
THEN system generates declaration with:
  - Chronological list of incidents
  - Evidence supporting each fact
  - Citations to exhibits
  - Verification statement
```

**US-5: Analyze Doctor's Notes for Contradictions**
```
GIVEN opposing party claims child was injured
WHEN I search doctor's notes
THEN system:
  - Finds all medical visits for relevant period
  - Extracts findings (no injuries observed)
  - Cross-references with allegations
  - Flags contradictions
  - Suggests use in motion
```

### As a Legal Researcher

**US-6: Find Precedent for Motion**
```
GIVEN I need case law for motion to dismiss
WHEN I query "grounds for dismissal - false allegations"
THEN system returns:
  - Relevant California cases
  - Key holdings
  - Applicable citations
  - Similar fact patterns
```

---

## 4. System Architecture

### High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│ EXISTING SYSTEM (from previous work)                               │
├────────────────────────────────────────────────────────────────────┤
│ Document Upload → Queue → Micro Analysis → Macro Analysis →       │
│ Violation Detection → Timeline & Profiles → Judicial Assessment   │
└────────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────────┐
│ NEW: COURT DOCUMENTS REPOSITORY                                    │
├────────────────────────────────────────────────────────────────────┤
│ • minute_orders         - Court minute orders & rulings            │
│ • hearings              - Hearing records & outcomes               │
│ • transcripts           - Full transcripts with AI analysis        │
│ • exhibits              - Evidence exhibits catalogue              │
│ • police_reports        - Structured police report data            │
│ • doctors_notes         - Medical records & findings               │
│ • findings_and_orders   - Judicial findings after hearings         │
└────────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────────┐
│ NEW: COMMUNICATIONS REPOSITORY                                     │
├────────────────────────────────────────────────────────────────────┤
│ • communications        - All text messages, emails, calls         │
│ • communication_threads - Grouped conversations                    │
│ • communication_analysis- Truth/lie detection results              │
│ • contradiction_links   - Links to sworn statements                │
└────────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────────┐
│ NEW: ACTION ITEMS & MOTIONS                                        │
├────────────────────────────────────────────────────────────────────┤
│ • action_items          - Things that need to be done              │
│ • motion_templates      - Templates for different motion types     │
│ • generated_motions     - Completed motions ready to file          │
│ • motion_evidence_links - Links motion → supporting evidence       │
│ • filing_history        - Track what was filed when                │
└────────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────────┐
│ NEW: MOTION GENERATOR ENGINE                                       │
├────────────────────────────────────────────────────────────────────┤
│ Input: Motion type + Context                                       │
│ Process:                                                           │
│   1. Retrieve relevant evidence (violations, timeline, docs)       │
│   2. Pull applicable case law and codes                            │
│   3. Generate factual background from micro/macro analysis         │
│   4. Create legal argument citing precedent                        │
│   5. Attach supporting declarations                                │
│   6. Format per court rules                                        │
│ Output: Complete motion ready to file (PDF + DOCX)                 │
└────────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────────┐
│ NEW: COMMUNICATIONS ANALYSIS ENGINE                                │
├────────────────────────────────────────────────────────────────────┤
│ Input: Text messages, emails, call logs                            │
│ Process:                                                           │
│   1. Ingest and parse communications (dates, participants, content)│
│   2. Generate embeddings for vector search                         │
│   3. Cross-reference with sworn statements (macro analysis)        │
│   4. Detect contradictions and lies                                │
│   5. Score truthfulness per message                                │
│   6. Build deception pattern profile                               │
│ Output: Searchable database + truth/lie scores                     │
└────────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────────┐
│ USER INTERFACE                                                     │
├────────────────────────────────────────────────────────────────────┤
│ • Motion Generator Dashboard                                       │
│ • Communications Search Interface                                  │
│ • Court Documents Timeline                                         │
│ • Action Items List                                                │
│ • Evidence Browser                                                 │
└────────────────────────────────────────────────────────────────────┘
```

### Data Flow for Motion Generation

```
USER REQUEST: "Generate motion for reconsideration - Cal OES 2-925"
    ↓
MOTION GENERATOR ENGINE
    ↓
STEP 1: Analyze Request
  - Motion type: Reconsideration
  - Issue: Failure to verify Cal OES 2-925 pickup
  - Court: Juvenile Dependency
    ↓
STEP 2: Retrieve Evidence
  - Query minute_orders: Find orders requiring Cal OES verification
  - Query hearings: Find relevant hearings
  - Query transcripts: Find social worker testimony
  - Query police_reports: Find Cal OES 2-925 records (or lack thereof)
  - Query violations: Find "negligence" violations for social worker
    ↓
STEP 3: Retrieve Legal Authority
  - Query case_law_citations: Motions for reconsideration precedent
  - Query legal_codes: California Rules of Court § 1008
  - Query legal_codes: Welfare & Institutions Code § 300
    ↓
STEP 4: Generate Motion Sections
  - Caption (case name, case number, court)
  - Notice of Motion (what we're asking for)
  - Memorandum of Points & Authorities
    * Introduction
    * Statement of Facts (from timeline, micro analysis)
    * Legal Argument (citing case law)
    * Conclusion
  - Declaration in Support (facts + evidence)
  - Proposed Order
  - Certificate of Service
    ↓
STEP 5: Format & Output
  - Apply court formatting rules
  - Number exhibits
  - Generate PDF
  - Generate DOCX (for editing)
    ↓
OUTPUT: Complete motion ready to file
```

---

## 5. Feature Requirements

### 5.1 MVP Features (Ship in 2 weeks)

#### MVP-1: Court Documents Repository

**Priority: P0 (Critical)**

**Tables Required:**
- `minute_orders` - Court minute orders
- `hearings` - Hearing records
- `findings_and_orders` - Judicial findings
- `transcripts` - Court transcripts
- `exhibits` - Evidence exhibits

**Features:**
- Upload court documents
- Extract key information (date, judge, findings, orders)
- Link to relevant journal documents
- Search by date, keyword, order type

**Acceptance Criteria:**
- Can upload minute order and extract findings
- Can search minute orders by keyword
- Can view hearing history chronologically

#### MVP-2: Communications Repository & Ingestion

**Priority: P0 (Critical)**

**Tables Required:**
- `communications` - All text messages, emails, calls
- `communication_participants` - Who was involved
- `communication_threads` - Grouped conversations

**Features:**
- Import text messages from iPhone export (JSON, CSV)
- Import text messages from Android export
- Parse date, time, sender, recipient, content
- Store in searchable database
- Generate embeddings for vector search

**Acceptance Criteria:**
- Can import 1000+ messages in <5 minutes
- Can search messages by keyword
- Can filter by date range
- Can filter by participant

#### MVP-3: Basic Motion Generator

**Priority: P0 (Critical)**

**Motion Types Supported (MVP):**
1. Motion for Reconsideration (Cal Rules of Court § 1008)
2. Request for Judicial Notice (Evid. Code § 450-460)
3. Declaration in Support

**Features:**
- Select motion type from dropdown
- Fill in key facts (AI-assisted with suggestions from case)
- System pulls relevant evidence automatically
- System cites applicable case law
- Generate PDF + DOCX

**Acceptance Criteria:**
- Can generate motion for reconsideration in <30 minutes
- Motion includes factual background from case timeline
- Motion cites at least 2 relevant cases
- Motion attaches 3+ supporting exhibits
- Output is properly formatted per court rules

#### MVP-4: Truth/Lie Detection (Basic)

**Priority: P1 (High)**

**Features:**
- Compare text message content with sworn declarations
- Flag contradictions
- Calculate consistency score per participant
- Highlight potential lies

**Acceptance Criteria:**
- Can detect contradiction between text and declaration
- Shows side-by-side comparison
- Provides confidence score (0-100)

#### MVP-5: Action Items Dashboard

**Priority: P1 (High)**

**Features:**
- List of things that need to be done
- Deadlines from minute orders
- Suggested motions based on violations
- Filing status tracking

**Acceptance Criteria:**
- Shows upcoming deadlines
- Lists suggested actions based on case analysis
- Can create motion from action item

### 5.2 Enterprise Features (Post-MVP)

#### ENT-1: Advanced Motion Types

**Additional Motion Types:**
- Motion to Dismiss (CCP § 583.310)
- Motion to Vacate (CCP § 473)
- Motion to Quash Service
- Motion for Protective Order
- Motion to Compel Discovery
- Motion for Sanctions (CCP § 128.5)
- Motion to Strike (CCP § 436)
- Appeal Brief

#### ENT-2: Advanced Communications Analysis

**Features:**
- Sentiment analysis
- Manipulation detection
- Coercion patterns
- Gaslighting detection
- Timeline of promises vs actions
- Voice-to-text for call recordings
- Email analysis (Gmail, Outlook integration)

#### ENT-3: AI Legal Research Assistant

**Features:**
- Natural language queries ("Find cases where false CPS reports led to custody change")
- Automatic legal research
- Shepardizing (checking if cases still valid)
- Local rules automation
- Judge-specific practices

#### ENT-4: Collaborative Features

**Features:**
- Share case with attorney
- Collaborate on motions
- Comments and suggestions
- Version control
- Review workflow

#### ENT-5: Court Filing Integration

**Features:**
- E-filing direct from system
- Track filing status
- Calendar integration
- Automatic proof of service generation
- Court appearance reminders

---

## 6. Technical Requirements

### 6.1 Database Schema (New Tables)

#### Court Documents Tables

```sql
-- Minute Orders
CREATE TABLE minute_orders (
    minute_order_id BIGSERIAL PRIMARY KEY,
    hearing_id BIGINT REFERENCES hearings(hearing_id),
    journal_id BIGINT REFERENCES document_journal(journal_id),

    hearing_date DATE NOT NULL,
    judge_name TEXT,
    department TEXT,

    orders_made TEXT[],
    findings TEXT[],
    next_hearing_date DATE,
    compliance_deadlines JSONB,

    full_text TEXT,
    extracted_data JSONB
);

-- Hearings
CREATE TABLE hearings (
    hearing_id BIGSERIAL PRIMARY KEY,

    hearing_date DATE NOT NULL,
    hearing_time TIME,
    hearing_type TEXT,  -- 'detention', 'jurisdiction', 'disposition', 'review', 'permanency'
    department TEXT,
    judge_name TEXT,

    parties_present TEXT[],
    attorneys_present TEXT[],

    outcome TEXT,
    continued_to DATE,

    minute_order_id BIGINT REFERENCES minute_orders(minute_order_id),
    transcript_id BIGINT REFERENCES transcripts(transcript_id)
);

-- Transcripts
CREATE TABLE transcripts (
    transcript_id BIGSERIAL PRIMARY KEY,
    hearing_id BIGINT REFERENCES hearings(hearing_id),
    journal_id BIGINT REFERENCES document_journal(journal_id),

    transcript_date DATE NOT NULL,
    page_count INTEGER,

    full_text TEXT,

    speakers JSONB[],
    /* [
      {"speaker": "Judge", "lines": 45},
      {"speaker": "County Counsel", "lines": 32}
    ] */

    key_statements JSONB[],
    /* Extracted by AI */

    embeddings_generated BOOLEAN DEFAULT FALSE
);

-- Findings and Orders
CREATE TABLE findings_and_orders (
    finding_id BIGSERIAL PRIMARY KEY,
    hearing_id BIGINT REFERENCES hearings(hearing_id),
    minute_order_id BIGINT REFERENCES minute_orders(minute_order_id),

    finding_type TEXT,  -- 'jurisdictional', 'dispositional', 'review'
    finding_text TEXT,

    legal_basis TEXT,  -- 'WIC § 300(b)', etc.

    order_text TEXT,
    compliance_required BOOLEAN DEFAULT FALSE,
    compliance_deadline DATE,

    appealed BOOLEAN DEFAULT FALSE,
    appeal_outcome TEXT
);

-- Exhibits
CREATE TABLE exhibits (
    exhibit_id BIGSERIAL PRIMARY KEY,

    exhibit_number TEXT,  -- 'A', 'B', '1', '2', etc.
    exhibit_letter TEXT,

    exhibit_description TEXT,
    exhibit_type TEXT,  -- 'photo', 'document', 'record', 'report'

    source_journal_id BIGINT REFERENCES document_journal(journal_id),

    admitted_at_hearing_id BIGINT REFERENCES hearings(hearing_id),
    admitted_date DATE,
    admitted_by TEXT,  -- Who offered it

    relevance TEXT
);

-- Police Reports (Structured)
CREATE TABLE police_reports (
    police_report_id BIGSERIAL PRIMARY KEY,
    journal_id BIGINT REFERENCES document_journal(journal_id),

    report_number TEXT,
    agency TEXT,
    officer_name TEXT,
    badge_number TEXT,

    incident_date DATE,
    incident_time TIME,
    incident_location TEXT,

    incident_type TEXT,
    allegations TEXT[],

    disposition TEXT,  -- 'founded', 'unfounded', 'inconclusive'

    statements JSONB[],
    evidence_collected TEXT[],

    follow_up_required BOOLEAN DEFAULT FALSE,
    case_status TEXT
);

-- Doctor's Notes (Structured)
CREATE TABLE doctors_notes (
    doctors_note_id BIGSERIAL PRIMARY KEY,
    journal_id BIGINT REFERENCES document_journal(journal_id),

    provider_name TEXT,
    facility TEXT,
    visit_date DATE,

    patient_name TEXT,
    chief_complaint TEXT,

    diagnosis TEXT,
    findings TEXT,
    injuries_observed TEXT[],
    treatment_provided TEXT,

    recommendations TEXT,
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE
);
```

#### Communications Tables

```sql
-- Communications (Text Messages, Emails, Calls)
CREATE TABLE communications (
    communication_id BIGSERIAL PRIMARY KEY,

    communication_type TEXT NOT NULL,  -- 'sms', 'email', 'call', 'voicemail'

    sent_date TIMESTAMPTZ NOT NULL,

    sender TEXT NOT NULL,
    sender_phone TEXT,
    sender_email TEXT,

    recipient TEXT NOT NULL,
    recipient_phone TEXT,
    recipient_email TEXT,

    subject TEXT,  -- For emails
    content TEXT,  -- Message content

    attachments TEXT[],  -- File paths or URLs

    thread_id BIGINT REFERENCES communication_threads(thread_id),

    -- Truth/Lie Analysis
    analyzed BOOLEAN DEFAULT FALSE,
    truthfulness_score DECIMAL(5,2),  -- 0-100
    contains_contradiction BOOLEAN DEFAULT FALSE,
    contradiction_details JSONB,

    -- Embeddings for vector search
    embedding VECTOR(1536),  -- OpenAI ada-002

    -- Links to case documents
    related_declarations BIGINT[],  -- Declaration journal_ids
    related_violations BIGINT[],     -- Violation IDs

    -- Source
    source_file TEXT,
    imported_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_communications_sent_date ON communications(sent_date);
CREATE INDEX idx_communications_sender ON communications(sender);
CREATE INDEX idx_communications_type ON communications(communication_type);
CREATE INDEX idx_communications_truthfulness ON communications(truthfulness_score);

-- Communication Threads (Grouped Conversations)
CREATE TABLE communication_threads (
    thread_id BIGSERIAL PRIMARY KEY,

    participants TEXT[],

    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,

    message_count INTEGER DEFAULT 0,

    thread_summary TEXT,  -- AI-generated summary

    key_topics TEXT[],

    -- Truth analysis for entire thread
    thread_truthfulness_score DECIMAL(5,2),
    deception_patterns JSONB[]
);

-- Communication Analysis Results
CREATE TABLE communication_analysis (
    analysis_id BIGSERIAL PRIMARY KEY,
    communication_id BIGINT REFERENCES communications(communication_id),

    analysis_type TEXT,  -- 'truth_detection', 'sentiment', 'manipulation'

    analysis_result JSONB,
    /*
    For truth detection:
    {
      "truthfulness_score": 25.0,
      "likely_false": true,
      "contradicts": [
        {
          "statement": "I never denied visitation",
          "contradicted_by": "Text on 2023-01-20: 'You can't see the child'",
          "confidence": 0.95
        }
      ]
    }
    */

    confidence_score DECIMAL(5,2),

    analyzed_at TIMESTAMPTZ DEFAULT NOW(),
    ai_model_used TEXT
);

-- Contradiction Links (Communications vs Sworn Statements)
CREATE TABLE contradiction_links (
    contradiction_id BIGSERIAL PRIMARY KEY,

    communication_id BIGINT REFERENCES communications(communication_id),
    declaration_journal_id BIGINT REFERENCES document_journal(journal_id),

    communication_statement TEXT,
    declaration_statement TEXT,

    contradiction_type TEXT,  -- 'direct', 'implied', 'omission'

    severity TEXT,  -- 'minor', 'moderate', 'severe'

    confidence_score DECIMAL(5,2),

    detected_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### Motion & Action Items Tables

```sql
-- Action Items
CREATE TABLE action_items (
    action_id BIGSERIAL PRIMARY KEY,

    action_type TEXT NOT NULL,  -- 'file_motion', 'respond_to_filing', 'compliance_deadline', 'prepare_for_hearing'

    title TEXT NOT NULL,
    description TEXT,

    due_date DATE,
    priority TEXT,  -- 'urgent', 'high', 'medium', 'low'

    status TEXT DEFAULT 'pending',  -- 'pending', 'in_progress', 'completed', 'cancelled'

    -- What triggered this action
    triggered_by_violation_id BIGINT REFERENCES violations(violation_id),
    triggered_by_minute_order_id BIGINT REFERENCES minute_orders(minute_order_id),
    triggered_by_hearing_id BIGINT REFERENCES hearings(hearing_id),

    -- Suggested motion type (if applicable)
    suggested_motion_type TEXT,

    -- Completion
    completed_at TIMESTAMPTZ,
    completed_motion_id BIGINT REFERENCES generated_motions(motion_id),

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Motion Templates
CREATE TABLE motion_templates (
    template_id BIGSERIAL PRIMARY KEY,

    motion_type TEXT NOT NULL UNIQUE,
    /* Types:
       'motion_for_reconsideration'
       'motion_to_dismiss'
       'motion_to_vacate'
       'motion_to_quash'
       'request_for_judicial_notice'
       'motion_for_sanctions'
       'motion_to_strike'
       'motion_to_compel_discovery'
       'declaration_in_support'
    */

    motion_name TEXT NOT NULL,

    court_type TEXT,  -- 'juvenile_dependency', 'family', 'civil'

    template_content TEXT,
    /* Jinja2 template with placeholders like:
       {{ case_name }}
       {{ case_number }}
       {{ factual_background }}
       {{ legal_argument }}
       {{ exhibits }}
    */

    required_fields JSONB,
    /* Fields that must be filled:
    {
      "case_name": "string",
      "case_number": "string",
      "moving_party": "string",
      "grounds": "text"
    }
    */

    legal_authority TEXT[],  -- Default case law and codes

    instructions TEXT,

    version INTEGER DEFAULT 1,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Generated Motions
CREATE TABLE generated_motions (
    motion_id BIGSERIAL PRIMARY KEY,

    template_id BIGINT REFERENCES motion_templates(template_id),
    action_item_id BIGINT REFERENCES action_items(action_id),

    motion_type TEXT NOT NULL,
    motion_title TEXT NOT NULL,

    -- Case information
    case_name TEXT,
    case_number TEXT,
    court_name TEXT,
    department TEXT,

    -- Generated content
    caption TEXT,
    notice_of_motion TEXT,
    memorandum TEXT,
    declaration TEXT,
    proposed_order TEXT,
    certificate_of_service TEXT,

    -- Evidence attached
    exhibits_attached BIGINT[],  -- exhibit_ids

    -- Legal citations used
    case_law_cited BIGINT[],  -- citation_ids
    legal_codes_cited BIGINT[],  -- code_ids

    -- Violations addressed
    violations_addressed BIGINT[],  -- violation_ids

    -- Generated files
    pdf_path TEXT,
    docx_path TEXT,

    -- Status
    status TEXT DEFAULT 'draft',  -- 'draft', 'review', 'ready_to_file', 'filed'

    filed_date DATE,
    filing_confirmation TEXT,

    -- Metadata
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    generated_by TEXT,  -- 'ai', 'manual', 'assisted'
    ai_model_used TEXT,
    generation_time_seconds DECIMAL(8,2),

    reviewed_by TEXT,
    reviewed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Motion Evidence Links
CREATE TABLE motion_evidence_links (
    link_id BIGSERIAL PRIMARY KEY,

    motion_id BIGINT REFERENCES generated_motions(motion_id),

    evidence_type TEXT,  -- 'exhibit', 'declaration', 'transcript', 'minute_order', 'communication'

    evidence_id BIGINT,  -- Could reference different tables
    evidence_table TEXT,  -- Which table ('exhibits', 'communications', etc.)

    exhibit_label TEXT,  -- 'Exhibit A', 'Exhibit 1', etc.

    relevance TEXT,  -- Why this evidence supports the motion

    page_references TEXT  -- 'pp. 3-5', 'lines 12-18', etc.
);

-- Filing History
CREATE TABLE filing_history (
    filing_id BIGSERIAL PRIMARY KEY,

    motion_id BIGINT REFERENCES generated_motions(motion_id),

    filed_date DATE NOT NULL,
    filed_time TIME,

    filing_method TEXT,  -- 'efiling', 'in_person', 'mail'
    filing_confirmation TEXT,

    hearing_date DATE,
    hearing_result TEXT,

    order_after_hearing TEXT,

    successful BOOLEAN,

    notes TEXT
);
```

### 6.2 API Requirements

#### Motion Generation API

```
POST /api/motions/generate
Body: {
  "motion_type": "motion_for_reconsideration",
  "case_context": {
    "issue": "Cal OES 2-925 not verified",
    "hearing_date": "2023-11-15"
  },
  "auto_include_evidence": true
}

Response: {
  "motion_id": 123,
  "status": "generated",
  "pdf_url": "/motions/123.pdf",
  "docx_url": "/motions/123.docx",
  "exhibits_count": 5,
  "citations_count": 3
}
```

#### Communications Search API

```
GET /api/communications/search?q=visitation&sender=Father&date_start=2023-01-01

Response: {
  "results": [
    {
      "communication_id": 456,
      "date": "2023-01-20",
      "sender": "Father",
      "recipient": "Mother",
      "content": "You can pick up child at 3pm",
      "truthfulness_score": 85.0,
      "contradicts": []
    }
  ],
  "total": 15
}
```

#### Truth Analysis API

```
POST /api/communications/analyze_truth
Body: {
  "communication_ids": [456, 457, 458],
  "compare_to_declarations": [123, 124]
}

Response: {
  "contradictions_found": 3,
  "contradictions": [
    {
      "communication_id": 456,
      "communication_text": "Mother denied all contact",
      "declaration_id": 123,
      "declaration_text": "Father declined offered visitation",
      "confidence": 0.95
    }
  ]
}
```

---

## 7. Implementation Roadmap

### Phase 1: MVP (Weeks 1-2)

**Week 1:**
- [ ] Day 1-2: Create database schema (all new tables)
- [ ] Day 3-4: Build communications ingestion pipeline
  - Import iPhone text messages (JSON)
  - Import Android text messages (CSV)
  - Generate embeddings
- [ ] Day 5: Build court documents upload & parsing
  - Minute orders extraction
  - Hearings tracking

**Week 2:**
- [ ] Day 1-3: Build Motion Generator Engine
  - Motion for Reconsideration template
  - Request for Judicial Notice template
  - Declaration template
  - Evidence auto-attachment
  - PDF generation
- [ ] Day 4: Build basic truth/lie detection
  - Compare communications with declarations
  - Flag contradictions
- [ ] Day 5: Build Action Items dashboard
  - List upcoming deadlines
  - Suggest motions
- [ ] Integration testing
- [ ] User acceptance testing

**Deliverable:** Working system that can:
1. Ingest text messages (2019-present)
2. Generate motion for reconsideration
3. Detect contradictions in communications
4. Track court documents

### Phase 2: Enhanced Features (Weeks 3-4)

- [ ] Add more motion types (dismiss, vacate, quash)
- [ ] Advanced communication analysis (sentiment, manipulation)
- [ ] Transcript AI analysis
- [ ] Better evidence search

### Phase 3: Enterprise (Weeks 5-8)

- [ ] All motion types
- [ ] Legal research assistant
- [ ] E-filing integration
- [ ] Collaborative features

---

## 8. Immediate Next Steps (TODAY)

### For Motion for Reconsideration - Cal OES 2-925

**What we need NOW:**

1. **Deploy court documents schema**
   - minute_orders table
   - hearings table
   - police_reports table

2. **Upload relevant documents:**
   - Minute order requiring Cal OES 2-925 verification
   - Social worker reports (showing non-verification)
   - Hearing transcript (if available)

3. **Generate motion:**
   ```python
   motion_generator.generate(
       motion_type='motion_for_reconsideration',
       issue='Social worker failed to verify Cal OES 2-925 was picked up by law enforcement',
       relief_requested='Request court to order production of law enforcement records',
       legal_basis=['Cal Rules of Court § 1008', 'WIC § 827']
   )
   ```

**Output needed TODAY:**
- Motion for Reconsideration (PDF + DOCX)
- Declaration in Support
- Request for Judicial Notice (if needed)
- Certificate of Service

---

## 9. Success Metrics

### MVP Success Criteria

- ✅ Can ingest 5+ years of text messages in <10 minutes
- ✅ Can search messages with <1 second response time
- ✅ Can detect contradictions with 80%+ accuracy
- ✅ Can generate motion in <30 minutes (vs 8+ hours manual)
- ✅ Generated motion includes 90%+ relevant evidence
- ✅ Motion is properly formatted per court rules

### User Satisfaction

- ✅ Reduces motion drafting time by 80%+
- ✅ Increases confidence in filings (nothing missed)
- ✅ Enables rapid response to court actions

---

## 10. Risks & Mitigations

### Technical Risks

**Risk:** Text message import format varies
**Mitigation:** Support multiple formats (JSON, CSV, XML)

**Risk:** AI-generated motion may have errors
**Mitigation:** Always output DOCX for human review/editing

**Risk:** Truth detection may have false positives
**Mitigation:** Show confidence scores, allow manual override

### Legal Risks

**Risk:** Generated motion may miss key legal issues
**Mitigation:** Include disclaimer, require attorney review for complex motions

**Risk:** Privacy of communications
**Mitigation:** All data stored locally/encrypted, no cloud upload without consent

---

## 11. Open Questions

1. **Should we integrate with court e-filing systems?**
   - Pro: One-click filing
   - Con: Complex integration, varies by county

2. **Should communications be automatically analyzed, or on-demand?**
   - Auto: Proactive detection of lies
   - On-demand: Lower resource usage

3. **How to handle voice recordings?**
   - MVP: Manual transcription
   - Future: Automatic speech-to-text

4. **Export format for motions?**
   - PDF (for filing)
   - DOCX (for editing)
   - Both?

---

## 12. Conclusion

The Motion & Declaration Engine transforms ASEAGI from an analysis system into an **action system**. It closes the loop: analyze → detect → act.

**Immediate Impact:**
- TODAY: Generate motion for reconsideration in <1 hour
- THIS WEEK: Search 5 years of text messages for contradictions
- NEXT WEEK: Never miss a deadline or filing opportunity

**Strategic Impact:**
- Level the playing field against resourced opponents
- Rapid response capability
- Complete case management end-to-end

**Ready to build?** Let's start with the schema deployment and get you that motion for TODAY's court.

---

**For Ashe. For Justice. For All Children. 🛡️**

---

## Appendix A: Motion Types Reference

| Motion Type | Court Rules | Use Case |
|-------------|-------------|----------|
| Motion for Reconsideration | CRC § 1008 | New facts, change in law |
| Motion to Dismiss | CCP § 583.310 | Lack of prosecution, other grounds |
| Motion to Vacate | CCP § 473 | Mistake, inadvertence, excusable neglect |
| Motion to Quash Service | CCP § 418.10 | Improper service |
| Request for Judicial Notice | Evid. Code § 450-460 | Court records, published materials |
| Motion for Sanctions | CCP § 128.5 | Frivolous filings, bad faith |
| Motion to Strike | CCP § 436 | Irrelevant, false, improper matter |
| Motion to Compel Discovery | CCP § 2031.300 | Failure to respond to discovery |

## Appendix B: Data Sources

| Data Source | Format | Ingestion Method |
|-------------|--------|------------------|
| iPhone Messages | JSON export | Automated parser |
| Android Messages | CSV/XML | Automated parser |
| Gmail | MBOX | Email client export |
| Court Documents | PDF | OCR + AI extraction |
| Call Logs | CSV | Manual export from carrier |
| Voice Recordings | MP3/WAV | Speech-to-text |
