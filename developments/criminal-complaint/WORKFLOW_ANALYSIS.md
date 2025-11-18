# CRIMINAL COMPLAINT SYSTEM - WORKFLOW & ARCHITECTURE ANALYSIS

**Date:** November 17, 2025
**Status:** Analysis & Redesign Recommendations
**Current Version:** v1.0 (Limited - 5 hardcoded claims only)

---

## 🔍 **CURRENT WORKFLOW (AS-IS)**

### **Phase 1: Document Upload**

```
┌─────────────────────────────────────────────────────────────┐
│ INPUT SOURCES (Current)                                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
    ┌──────────────────┬──────────────────┬──────────────────┐
    │ Telegram Bot     │ Manual Scan      │ Batch Upload     │
    │ (Mobile)         │ (Local Files)    │ (Script)         │
    └────────┬─────────┴────────┬─────────┴────────┬─────────┘
             │                  │                  │
             └──────────────────┴──────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ STORAGE: /data/telegram-inbox/YYYY-MM-DD/                  │
│ Files stored permanently, never deleted                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ PROCESSING: batch_scan_documents.py                         │
│ - Calculate MD5 hash                                        │
│ - Check for duplicates                                      │
│ - Convert to base64 (images)                                │
│ - Send to Claude API                                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ ANALYSIS: Claude Sonnet 4.5                                 │
│ - FULL PAGE analysis only (no granular options)            │
│ - PROJ344 scoring (0-999)                                   │
│ - Extract key quotes                                        │
│ - Detect fraud/perjury indicators                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ DATABASE: Supabase legal_documents table                    │
│ - Single record per document                                │
│ - No page-level granularity                                │
│ - No statement-level extraction                            │
└─────────────────────────────────────────────────────────────┘
```

### **Phase 2: Criminal Complaint Analysis (Current - Limited)**

```
┌─────────────────────────────────────────────────────────────┐
│ HARDCODED: 5 False Statements in schema.py                  │
│ - FS-001-JAMAICA-FLIGHT                                     │
│ - FS-002-RETURN-AGREEMENT                                   │
│ - FS-003-HISTORY-VIOLATIONS                                 │
│ - FS-004-CONCEALED-INVESTIGATION                            │
│ - FS-005-MOTHER-ASHES-CLAIM                                 │
│                                                             │
│ ❌ LIMITATION: Cannot add more without editing code         │
│ ❌ LIMITATION: No automatic statement extraction            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ ANALYSIS: analyzer.py                                        │
│ - Queries ALL documents from database                       │
│ - Searches for keywords in full document only              │
│ - No page-level search                                      │
│ - No statement-level analysis                               │
│ - Calculates contradiction scores                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ OUTPUT: Master Report                                        │
│ - Document-level evidence only                              │
│ - No statement-by-statement breakdown                       │
│ - No timeline cross-reference                               │
└─────────────────────────────────────────────────────────────┘
```

---

## ❌ **CRITICAL LIMITATIONS**

### **1. Upload/Analysis Granularity**

**Current:**
- ✅ Full page analysis only
- ❌ No quarter-page analysis
- ❌ No half-page analysis
- ❌ No multi-page documents broken into sections
- ❌ No re-upload with different focus areas

**Needed:**
- Multiple analysis passes per document:
  - Full page (overview)
  - Half page (detailed sections)
  - Quarter page (specific paragraphs)
  - Statement-by-statement (micro-level)

### **2. Storage Architecture**

**Current:**
```
Local Only:
/data/telegram-inbox/YYYY-MM-DD/document.jpg
    ↓
Supabase: legal_documents table
    ↓
No cloud backup
No tiered storage
```

**Missing:**
- ❌ Cloud storage (Google Drive, Backblaze)
- ❌ CDN for fast access
- ❌ Redundant backups
- ❌ Tiered storage by importance
- ❌ Web upload interface
- ❌ Mobile app upload

### **3. Statement Analysis**

**Current:**
- Only 5 hardcoded false statements
- Searches entire documents for keywords
- No automatic statement extraction

**Missing:**
- ❌ Extract ALL statements from documents automatically
- ❌ Categorize statements (claims, facts, admissions, denials)
- ❌ Track who made each statement
- ❌ When each statement was made
- ❌ What subject each statement is about
- ❌ Automatic contradiction detection between statements

### **4. Timeline/Event Analysis**

**Current:**
- No timeline functionality
- No event sequencing
- No chronological cross-reference
- No discrepancy detection across time

**Missing:**
- ❌ Event timeline (court dates, incidents, statements)
- ❌ Macro analysis across timeline
- ❌ Automated discrepancy detection
- ❌ Timeline visualization
- ❌ Event correlation

### **5. Complaint Generation**

**Current:**
- Manual: Add false statements to schema.py
- Limited: Only 5 claims tracked
- Static: No dynamic complaint generation

**Missing:**
- ❌ Unlimited complaints
- ❌ Dynamic complaint generation from statement analysis
- ❌ Automatic complaint drafting
- ❌ Evidence correlation automation

---

## 🏗️ **PROPOSED ENHANCED ARCHITECTURE**

### **Level 1: MICRO ANALYSIS (Statement-Level)**

```
Document Upload
    ↓
┌─────────────────────────────────────────────────────────────┐
│ GRANULAR ANALYSIS OPTIONS                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ [X] Full Page    (1 analysis per page)                      │
│ [X] Half Page    (2 analyses per page)                      │
│ [X] Quarter Page (4 analyses per page)                      │
│ [X] Statement    (N analyses - each statement)              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ STATEMENT EXTRACTION (New System Needed)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ For EACH document, extract:                                 │
│   - Speaker/Author                                          │
│   - Statement text                                          │
│   - Statement type (claim/fact/admission/denial)            │
│   - Subject matter                                          │
│   - Date made                                               │
│   - Context                                                 │
│   - Verifiability (can it be proven true/false?)           │
│                                                             │
│ Store in: document_statements table                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
    ↓
DATABASE SCHEMA (New):
┌──────────────────────────────────────────┐
│ document_statements                      │
├──────────────────────────────────────────┤
│ id                UUID                   │
│ document_id       UUID (FK)              │
│ page_number       INT                    │
│ section          TEXT (full/half/quarter)│
│ speaker          TEXT (MOT/FAT/CPS/etc.) │
│ statement_text   TEXT                    │
│ statement_type   TEXT (claim/fact/etc.)  │
│ subject_matter   TEXT                    │
│ date_made        DATE                    │
│ verifiable       BOOLEAN                 │
│ verified_status  TEXT (true/false/unknown)│
│ contradicts      UUID[] (other statements)│
│ evidence_refs    UUID[] (supporting docs) │
└──────────────────────────────────────────┘
```

### **Level 2: TIMELINE ANALYSIS (Macro)**

```
┌─────────────────────────────────────────────────────────────┐
│ EVENT TIMELINE SYSTEM (New)                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Events tracked:                                             │
│   - Court hearings                                          │
│   - Declarations filed                                      │
│   - Statements made (from micro analysis)                   │
│   - Incidents reported                                      │
│   - Evidence submitted                                      │
│   - Violations detected                                     │
│                                                             │
│ Cross-reference engine:                                     │
│   1. Plot all events on timeline                            │
│   2. Identify statements made at each point                 │
│   3. Compare statements across time                         │
│   4. Detect contradictions/changes                          │
│   5. Flag discrepancies                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
    ↓
DATABASE SCHEMA (New):
┌──────────────────────────────────────────┐
│ event_timeline                           │
├──────────────────────────────────────────┤
│ id                UUID                   │
│ event_type       TEXT                    │
│ event_date       TIMESTAMP               │
│ event_title      TEXT                    │
│ event_desc       TEXT                    │
│ participants     TEXT[]                  │
│ statements_made  UUID[] (FK to statements)│
│ documents_filed  UUID[] (FK to docs)     │
│ related_events   UUID[] (FK to events)   │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│ statement_contradictions (New)           │
├──────────────────────────────────────────┤
│ id                   UUID                │
│ statement_1_id       UUID (FK)           │
│ statement_2_id       UUID (FK)           │
│ contradiction_type   TEXT                │
│ severity            INT (0-100)          │
│ date_gap            INT (days)           │
│ detected_at         TIMESTAMP            │
│ verified            BOOLEAN              │
│ complaint_generated BOOLEAN              │
└──────────────────────────────────────────┘
```

### **Level 3: DYNAMIC COMPLAINT GENERATION**

```
┌─────────────────────────────────────────────────────────────┐
│ AUTOMATED COMPLAINT SYSTEM (New)                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Input: Detected contradictions                              │
│   ↓                                                         │
│ 1. Contradiction Analysis Engine                            │
│    - Analyze severity                                       │
│    - Check if under oath                                    │
│    - Verify materiality                                     │
│    - Assess criminal liability                              │
│   ↓                                                         │
│ 2. Complaint Generator                                      │
│    - Draft complaint text                                   │
│    - Cite specific statements                               │
│    - Reference timeline events                              │
│    - List supporting evidence                               │
│    - Calculate prosecutability                              │
│   ↓                                                         │
│ 3. Evidence Mapper                                          │
│    - Link to documents                                      │
│    - Extract key quotes                                     │
│    - Build evidence package                                 │
│   ↓                                                         │
│ OUTPUT: Unlimited complaints (not just 5)                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘

DATABASE SCHEMA (New):
┌──────────────────────────────────────────┐
│ generated_complaints                     │
├──────────────────────────────────────────┤
│ id                   UUID                │
│ complaint_number     TEXT                │
│ subject_name         TEXT                │
│ false_statement_id   UUID (FK)           │
│ contradiction_id     UUID (FK)           │
│ penal_codes          TEXT[]              │
│ complaint_text       TEXT                │
│ evidence_documents   UUID[]              │
│ prosecutability      INT (0-100)         │
│ status              TEXT                 │
│ generated_at        TIMESTAMP            │
└──────────────────────────────────────────┘
```

---

## 📊 **STORAGE ARCHITECTURE DESIGN**

### **Option A: Multi-Tier Storage (Recommended)**

```
┌─────────────────────────────────────────────────────────────┐
│ TIER 1: HOT STORAGE (Instant Access)                        │
│ - Digital Ocean Droplet: /data/telegram-inbox/             │
│ - Supabase PostgreSQL: legal_documents table               │
│ - Use: Active case documents (score ≥900)                  │
│ - Cost: ~$12/month for 50GB                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ TIER 2: WARM STORAGE (Fast Access)                         │
│ - Backblaze B2: Primary cloud backup                       │
│ - Use: All case documents                                   │
│ - Cost: $0.005/GB/month = $3.50 for 700GB                 │
│ - API: Direct integration with Supabase                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ TIER 3: COLD ARCHIVE (Long-term)                           │
│ - Google Drive: User access/sharing                        │
│ - Use: Historical archive, client access                   │
│ - Cost: $0 (existing account) or $1.99/100GB              │
└─────────────────────────────────────────────────────────────┘
```

### **Upload Interfaces (Multi-Channel)**

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ TELEGRAM BOT    │  │ WEB INTERFACE   │  │ MOBILE APP      │
│ (Current)       │  │ (Needed)        │  │ (Future)        │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         └────────────────────┴────────────────────┘
                              ↓
         ┌─────────────────────────────────────────┐
         │ UPLOAD API (Flask/FastAPI)              │
         │ - Handles multi-part uploads            │
         │ - Validates file types                  │
         │ - Assigns granularity level             │
         │ - Triggers appropriate analysis         │
         └────────────┬────────────────────────────┘
                      ↓
         ┌─────────────────────────────────────────┐
         │ PROCESSING QUEUE                        │
         │ - Full page analysis                    │
         │ - Half page analysis (if requested)     │
         │ - Quarter page analysis (if requested)  │
         │ - Statement extraction (always)         │
         └────────────┬────────────────────────────┘
                      ↓
         ┌─────────────────────────────────────────┐
         │ STORAGE TIER ROUTER                     │
         │ - Tier 1: Droplet (immediate)           │
         │ - Tier 2: Backblaze (async)            │
         │ - Tier 3: Google Drive (batch)         │
         └─────────────────────────────────────────┘
```

---

## 🗂️ **CODEBASE HIERARCHY PLACEMENT**

### **Current Structure:**
```
ASEAGI/
├── developments/
│   └── criminal-complaint/v1.0/       ← CURRENT SYSTEM (limited)
│       ├── schema.py                  ← 5 hardcoded complaints
│       ├── analyzer.py                ← Document-level search
│       └── dashboard.py               ← Basic visualization
```

### **Proposed Enhanced Structure:**

```
ASEAGI/
├── developments/
│   ├── criminal-complaint/
│   │   ├── v1.0-2025-11-17/          ← Current (keep for reference)
│   │   └── v2.0-2025-11-18/          ← NEW ENHANCED SYSTEM
│   │       ├── VERSION.txt            (2.0)
│   │       ├── README.md
│   │       ├── CHANGELOG.md
│   │       │
│   │       ├── core/
│   │       │   ├── __init__.py
│   │       │   ├── statement_extractor.py      ← NEW: Extract statements
│   │       │   ├── timeline_builder.py         ← NEW: Build timelines
│   │       │   ├── contradiction_detector.py   ← NEW: Find contradictions
│   │       │   └── complaint_generator.py      ← NEW: Generate complaints
│   │       │
│   │       ├── database/
│   │       │   ├── schema_v2.py               ← NEW: Enhanced schemas
│   │       │   ├── migrations/
│   │       │   │   ├── 001_add_statements_table.sql
│   │       │   │   ├── 002_add_timeline_table.sql
│   │       │   │   └── 003_add_contradictions_table.sql
│   │       │   └── queries.py
│   │       │
│   │       ├── analysis/
│   │       │   ├── micro_analyzer.py          ← NEW: Statement-level
│   │       │   ├── macro_analyzer.py          ← NEW: Timeline-level
│   │       │   └── discrepancy_engine.py      ← NEW: Cross-reference
│   │       │
│   │       ├── upload/
│   │       │   ├── web_uploader.py            ← NEW: Web interface
│   │       │   ├── telegram_handler.py        ← Enhanced Telegram
│   │       │   ├── storage_router.py          ← NEW: Multi-tier storage
│   │       │   └── granularity_selector.py    ← NEW: Choose analysis level
│   │       │
│   │       ├── dashboards/
│   │       │   ├── complaint_dashboard.py     ← Enhanced version
│   │       │   ├── timeline_dashboard.py      ← NEW: Timeline viz
│   │       │   └── statement_explorer.py      ← NEW: Statement browser
│   │       │
│   │       └── cli/
│   │           ├── analyze.py                 ← Main CLI
│   │           ├── extract_statements.py
│   │           ├── build_timeline.py
│   │           └── generate_complaints.py
│   │
│   ├── document-upload/                      ← NEW FEATURE
│   │   └── v1.0-2025-11-18/
│   │       ├── web_interface/
│   │       │   ├── app.py                    ← Flask/FastAPI app
│   │       │   ├── templates/
│   │       │   └── static/
│   │       ├── api/
│   │       │   ├── upload_handler.py
│   │       │   └── granularity_api.py
│   │       └── storage/
│   │           ├── backblaze_client.py
│   │           ├── gdrive_client.py
│   │           └── tier_router.py
│   │
│   └── timeline-analysis/                    ← NEW FEATURE
│       └── v1.0-2025-11-18/
│           ├── event_manager.py
│           ├── timeline_visualizer.py
│           └── discrepancy_detector.py
```

---

## 🎯 **CORE FOCUS & BENEFITS**

### **Criminal Complaint System - Purpose:**

**CORE FOCUS:**
1. **Document Perjury** - Prove false statements under oath
2. **Build Evidence Package** - Compile supporting documentation
3. **Calculate Strength** - Assess prosecutability (0-100)
4. **Generate Reports** - Create DA-ready submissions

**WHERE TO USE:**
- Criminal referrals to District Attorney
- CCP §473 motions to vacate fraudulent orders
- Appellate briefs showing systematic fraud
- Impeachment evidence preparation

**BENEFITS:**
- ✅ Automates evidence correlation
- ✅ Calculates contradiction strength
- ✅ Generates prosecution-ready reports
- ✅ Maps documents to claims
- ✅ Provides visual dashboards

**LIMITATIONS (Current v1.0):**
- ❌ Only 5 hardcoded complaints
- ❌ No statement-level extraction
- ❌ No timeline analysis
- ❌ No automatic contradiction detection
- ❌ Document-level analysis only (no page granularity)
- ❌ Manual complaint creation required

---

## 🔄 **CURRENT WORKFLOW (Detailed)**

### **Step-by-Step Process:**

```
1. DOCUMENT UPLOAD (Telegram Bot)
   User sends document → @aseagi_legal_bot
   ↓
   Bot receives → Stores in /data/telegram-inbox/2025-11-17/
   ↓
   Calculates MD5 hash → Checks for duplicates
   ↓
   NO GRANULARITY OPTIONS (full page only)

2. DOCUMENT ANALYSIS (batch_scan_documents.py)
   Reads entire document → Converts to base64
   ↓
   Sends to Claude API → PROJ344 scoring
   ↓
   Extracts: summary, key_quotes, fraud_indicators
   ↓
   NO STATEMENT EXTRACTION
   NO PAGE-LEVEL ANALYSIS

3. DATABASE STORAGE (Supabase)
   Inserts into legal_documents table
   ↓
   Single record per document
   ↓
   NO STATEMENT TRACKING
   NO TIMELINE EVENTS

4. CRIMINAL COMPLAINT ANALYSIS (analyzer.py)
   Loads 5 hardcoded false statements from schema.py
   ↓
   Searches for keywords in full documents
   ↓
   Calculates contradiction scores (0-999)
   ↓
   NO AUTOMATIC DETECTION
   NO DYNAMIC COMPLAINT GENERATION

5. REPORT GENERATION
   Creates MASTER_PERJURY_REPORT.md
   ↓
   Lists supporting documents
   ↓
   NO STATEMENT-BY-STATEMENT BREAKDOWN
   NO TIMELINE CROSS-REFERENCE

6. MANUAL REVIEW
   User reads report → Manually verifies
   ↓
   MANUAL COMPLAINT DRAFTING REQUIRED
```

---

## 🚀 **PROPOSED ENHANCED WORKFLOW**

### **Step-by-Step Process (v2.0):**

```
1. DOCUMENT UPLOAD (Multi-Channel)
   ┌─────────────┬─────────────┬─────────────┐
   │ Telegram    │ Web Upload  │ Mobile App  │
   └──────┬──────┴──────┬──────┴──────┬──────┘
          └─────────────┴─────────────┘
                      ↓
   ┌─────────────────────────────────────────┐
   │ GRANULARITY SELECTOR                    │
   │ [ ] Full Page                           │
   │ [X] Half Page                           │
   │ [X] Quarter Page                        │
   │ [X] Statement Extraction (always)       │
   └─────────────────────────────────────────┘
                      ↓
   Stores in:
   - Tier 1: Droplet (immediate)
   - Tier 2: Backblaze (async)
   - Tier 3: Google Drive (batch)

2. MULTI-LEVEL ANALYSIS
   ┌─────────────────────────────────────────┐
   │ A. Full Page Analysis                   │
   │    → Overall PROJ344 score              │
   │    → Document summary                   │
   │    → Category assignment                │
   └─────────────────────────────────────────┘
   ┌─────────────────────────────────────────┐
   │ B. Half Page Analysis (if selected)     │
   │    → Detailed section scoring           │
   │    → Section-specific quotes            │
   └─────────────────────────────────────────┘
   ┌─────────────────────────────────────────┐
   │ C. Quarter Page Analysis (if selected)  │
   │    → Paragraph-level detail             │
   │    → Specific claim identification      │
   └─────────────────────────────────────────┘
   ┌─────────────────────────────────────────┐
   │ D. Statement Extraction (ALWAYS)        │
   │    → Extract ALL statements             │
   │    → Identify speaker                   │
   │    → Categorize type                    │
   │    → Track subject matter               │
   │    → Store in statements table          │
   └─────────────────────────────────────────┘

3. DATABASE STORAGE (Enhanced)
   legal_documents table (existing)
   +
   document_statements table (NEW)
   +
   event_timeline table (NEW)

4. TIMELINE CONSTRUCTION (Automatic)
   ┌─────────────────────────────────────────┐
   │ TIMELINE BUILDER                        │
   │ - Extract dates from all documents      │
   │ - Identify events                       │
   │ - Plot statements on timeline           │
   │ - Cross-reference statements by date    │
   └─────────────────────────────────────────┘

5. CONTRADICTION DETECTION (Automatic)
   ┌─────────────────────────────────────────┐
   │ DISCREPANCY ENGINE                      │
   │ - Compare ALL statements                │
   │ - Detect contradictions                 │
   │ - Calculate severity                    │
   │ - Flag timeline discrepancies           │
   │ - Store in contradictions table         │
   └─────────────────────────────────────────┘

6. COMPLAINT GENERATION (Automatic)
   ┌─────────────────────────────────────────┐
   │ COMPLAINT GENERATOR                     │
   │ - Analyze contradictions                │
   │ - Check if under oath                   │
   │ - Assess materiality                    │
   │ - Draft complaint text                  │
   │ - Link evidence automatically           │
   │ - Calculate prosecutability             │
   │ → UNLIMITED COMPLAINTS (not just 5)     │
   └─────────────────────────────────────────┘

7. REPORT GENERATION (Enhanced)
   ┌─────────────────────────────────────────┐
   │ MASTER REPORT (v2.0)                    │
   │ - Statement-by-statement breakdown      │
   │ - Timeline visualization                │
   │ - Contradiction matrix                  │
   │ - Evidence package per complaint        │
   │ - Automatically updated as docs added   │
   └─────────────────────────────────────────┘
```

---

## 📊 **QUANTIFIED HIERARCHY**

### **Code Complexity Levels:**

```
LEVEL 1: CORE INFRASTRUCTURE (Foundation)
├── Database schemas (schema_v2.py)
├── Storage tier routing (storage_router.py)
├── Upload API (web_uploader.py)
└── Statement extraction (statement_extractor.py)
    Complexity: HIGH
    Priority: CRITICAL
    Effort: 40 hours

LEVEL 2: ANALYSIS ENGINES (Processing)
├── Timeline builder (timeline_builder.py)
├── Contradiction detector (contradiction_detector.py)
├── Micro analyzer (micro_analyzer.py)
└── Macro analyzer (macro_analyzer.py)
    Complexity: VERY HIGH
    Priority: HIGH
    Effort: 60 hours

LEVEL 3: COMPLAINT GENERATION (Output)
├── Complaint generator (complaint_generator.py)
├── Evidence mapper (evidence_mapper.py)
└── Report generator v2 (report_generator_v2.py)
    Complexity: MEDIUM
    Priority: MEDIUM
    Effort: 30 hours

LEVEL 4: USER INTERFACES (Interaction)
├── Web upload interface (Flask app)
├── Timeline dashboard (Streamlit)
├── Statement explorer (Streamlit)
└── Enhanced complaint dashboard
    Complexity: MEDIUM
    Priority: LOW
    Effort: 40 hours

TOTAL EFFORT: ~170 hours (4-5 weeks full-time)
```

---

## 🎯 **IMMEDIATE NEXT STEPS**

### **Phase 1: Statement Extraction (Week 1)**
1. Create `document_statements` table schema
2. Build statement extractor
3. Test on 10 sample documents
4. Verify extraction accuracy

### **Phase 2: Timeline System (Week 2)**
1. Create `event_timeline` table
2. Build timeline constructor
3. Implement cross-reference engine
4. Create timeline visualization

### **Phase 3: Contradiction Detection (Week 3)**
1. Create `statement_contradictions` table
2. Build comparison algorithm
3. Implement severity calculation
4. Test on known contradictions

### **Phase 4: Dynamic Complaints (Week 4)**
1. Build complaint generator
2. Create evidence linking
3. Implement unlimited complaint support
4. Generate test complaints

### **Phase 5: Upload Enhancement (Week 5)**
1. Build web upload interface
2. Implement granularity selector
3. Set up Backblaze integration
4. Test multi-tier storage

---

**Would you like me to:**
1. Start building the enhanced v2.0 system?
2. Create the database migration scripts first?
3. Build the statement extraction engine?
4. Design the web upload interface?

Let me know which component to prioritize!
