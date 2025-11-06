# PROJ344: Legal Case Intelligence Dashboard - Complete Guide

**Case:** In re Ashe B., J24-00478
**Purpose:** Comprehensive legal case intelligence, document analysis, and constitutional violations tracking

---

## Dashboard Overview

The PROJ344 Master Dashboard provides a multi-dimensional analysis system for legal case management, combining document intelligence, violation tracking, court event monitoring, and micro-level content analysis.

---

## 📊 Main Navigation Categories

### 🏠 **Overview**
**Purpose:** High-level snapshot of the entire case system
**Key Metrics:**
- **Legal Documents**: Total count of all documents in the system
- **Violations Tracked**: Number of constitutional/legal violations identified
- **Court Events**: Scheduled and historical court proceedings
- **Pages Analyzed**: Individual pages processed for micro-level analysis
- **Communications**: Matrix of all communications between parties
- **DVRO Violations**: Domestic Violence Restraining Order violations tracked
- **Court Cases**: Related or linked court proceedings
- **Legal Citations**: Legal references and case law citations

**Critical Documents Section:**
- Shows documents with Relevancy Score 900+ (extremely critical)
- These represent the most important evidence in the case
- Includes executive summaries for quick understanding

---

## 📄 **Documents Intelligence**

### Purpose
Analyzes and categorizes all legal documents in the case with multi-dimensional scoring.

### Charts & Metadata

#### 1. **Documents by Type** (Pie Chart)
**What it shows:** Distribution of document categories
**Document Types Include:**
- Court Filings (motions, petitions, responses)
- Evidence Documents (photos, records, statements)
- Police Reports
- Medical Records
- Communications (emails, texts, letters)
- Expert Witness Reports
- Financial Records
- Case Law / Legal Citations

**Why it matters:** Helps identify what types of evidence dominate the case and where documentation may be lacking.

---

#### 2. **Documents by Importance** (Bar Chart)
**What it shows:** How documents are rated in terms of case impact
**Importance Levels:**
- **Critical**: Case-determining documents
- **High**: Significant supporting evidence
- **Medium**: Contextual or procedural documents
- **Low**: Administrative or background materials

**Metadata Used:**
- `importance` field from `legal_documents` table
- Assigned based on legal relevance, evidentiary value, and case impact

**Why it matters:** Prioritizes which documents need immediate review and which support overall narrative.

---

#### 3. **Relevancy Score Distribution** (Histogram)
**What it shows:** Statistical distribution of how relevant each document is to the case

**Scoring System (0-1000):**
- **900-1000**: Critical evidence, case-defining
- **700-899**: Highly relevant, strong support
- **500-699**: Moderately relevant, contextual
- **300-499**: Supporting information
- **0-299**: Background or procedural

**Metadata Components:**
The relevancy_number is calculated from:
- **Micro Number**: Page-level content analysis (false statements, perjury, fraud indicators)
- **Macro Number**: Document-level strategic importance
- **Legal Number**: Legal precedent strength and citation value
- **Category Score**: Document type weighting

**Formula:** `relevancy_number = (micro_number + macro_number + legal_number + category_score) / 4`

**Why it matters:** Identifies which documents carry the most weight in legal arguments and need priority attention.

---

#### 4. **Top 20 Documents by Relevancy** (Data Table)
**What it shows:** The most critical documents ranked by combined scoring

**Columns Displayed:**
- **Filename**: Document identifier
- **Relevancy Number**: Overall importance score (0-1000)
- **Micro Number**: Page-level analysis score
- **Macro Number**: Strategic document-level score
- **Legal Number**: Legal strength score
- **Document Type**: Category of document
- **Importance**: Critical/High/Medium/Low rating

**Why it matters:** This is your "smoking gun" list - the documents that will win or lose the case.

---

## ⚖️ **Legal Violations**

### Purpose
Tracks constitutional violations, due process violations, and rights infringements.

### Metrics
- **Total Violations**: Count of all tracked violations
- **Avg Severity Score**: How serious violations are (0-100 scale)
- **Avg Proof Strength**: How strong the evidence is (0-100 scale)

### Charts

#### **Violations by Category**
**Categories Include:**
- Due Process Violations
- Constitutional Rights Violations (1st, 4th, 5th, 6th, 14th Amendment)
- Brady Violations (prosecutorial misconduct)
- Discovery Violations
- Court Order Violations
- DVRO Violations
- Evidence Tampering/Destruction

#### **Violations by Perpetrator**
Shows which parties (CPS workers, opposing counsel, court officials, etc.) committed violations.

#### **Violations Timeline**
Chronological scatter plot showing:
- **X-axis**: Date of violation
- **Y-axis**: Severity score
- **Size**: Proof strength (larger bubbles = stronger evidence)

**Why it matters:** Establishes patterns of misconduct and builds grounds for appeals, sanctions, or civil rights claims.

---

## 📅 **Court Events & Timeline**

### Purpose
Complete chronological record of all court proceedings and deadlines.

### Metrics
- **Total Events**: All court dates (past + future)
- **Upcoming Events**: Future hearings/deadlines
- **Past Events**: Historical court record

### Sections

#### **Events by Type**
- Hearings
- Motions
- Trials
- Conferences
- Deadlines
- Rulings/Orders

#### **Upcoming Events**
Next scheduled court dates with:
- Event title
- Date/Time
- Court location
- Required actions

#### **Complete Case Timeline**
Full historical view linking:
- Court events
- Document filings
- Violation occurrences
- Key communications

**Why it matters:** Ensures nothing is missed and provides a master chronology for case strategy.

---

## 🔬 **Micro Document Analysis**

### Purpose
Page-by-page deep analysis of documents for false statements, perjury, and fraud.

### Metrics
- **Pages Analyzed**: Total pages processed
- **Avg Fraud Score**: Average fraud indicators per page
- **Avg Perjury Score**: Average perjury risk per page

### Critical Sections

#### **🚨 False Statements on Forms**
Identifies specific false statements on legal forms such as:
- FL-300 (Request for Order)
- DV-100 (DVRO Petition)
- Police reports
- Declarations under penalty of perjury

**Fields Tracked:**
- Form type
- Page number
- Statement made
- Contradicting evidence
- Proof strength

#### **☑️ Checkbox Perjury Summary**
Tracks checked boxes on forms that are provably false:
- "I do not know respondent's address" (when evidence shows they do)
- "No prior restraining orders" (when records show otherwise)
- "Fear for safety" (when contradicted by actions/communications)

#### **⚠️ Actions vs. Intentions Discrepancies**
Compares:
- **Stated intentions** (in declarations/testimony)
- **Actual actions** (proven by evidence)
- Highlights contradictions that prove dishonesty

**Why it matters:** Builds evidence of perjury and fraud, which can invalidate orders and establish criminal liability.

---

## 👥 **Multi-Jurisdiction Tracker**

### Purpose
Tracks related cases across multiple jurisdictions that impact the main case.

**Tracks:**
- Related family law cases
- Criminal proceedings
- CPS cases
- Civil rights lawsuits
- Appeals

**Why it matters:** Prevents contradictory rulings and identifies judicial conflicts.

---

## 💬 **Communications Analysis**

### Purpose
Matrix of all communications between parties, attorneys, and officials.

**Analyzes:**
- Emails
- Text messages
- Voicemails
- Letters
- Court filings

**Metadata:**
- Date/time
- Sender/recipient
- Topic/subject
- Relevancy score
- Linked documents
- Violation flags

**Why it matters:** Establishes timeline, proves notice, identifies coordination or conspiracy, catches lies.

---

## 🎯 **Critical Actions Required**

### Purpose
Action items dashboard showing what needs immediate attention.

**Sections:**
- Upcoming deadlines
- Required responses
- Evidence gaps
- High-priority violations needing documentation
- Documents needing review

**Why it matters:** Task management for case strategy - ensures nothing falls through the cracks.

---

## 📊 Scoring Methodology

### Multi-Dimensional Scoring System

All documents receive four component scores that combine into the final relevancy rating:

#### **1. Micro Number (0-250)**
Page-level content analysis:
- False statement detection
- Perjury indicators
- Fraud markers
- Contradiction identification
- Evidence tampering signs

#### **2. Macro Number (0-250)**
Document-level strategic value:
- Case impact potential
- Precedent-setting nature
- Strategic positioning value
- Narrative strength
- Rebuttal power

#### **3. Legal Number (0-250)**
Legal authority and citation strength:
- Case law alignment
- Statutory support
- Constitutional grounding
- Legal precedent power
- Admissibility strength

#### **4. Category Score (0-250)**
Document type weighting:
- Court orders (highest)
- Expert witness reports
- Police reports
- Medical records
- Declarations
- Evidence photos
- Administrative documents (lowest)

### **Final Relevancy Score**
`relevancy_number = (micro + macro + legal + category) / 4`

**Result:** 0-1000 scale where:
- 900+ = Case-critical evidence
- 700-899 = High-value documents
- 500-699 = Supporting evidence
- 300-499 = Contextual material
- 0-299 = Background/procedural

---

## 🗄️ Database Structure

### Core Tables (39 Total)
- `legal_documents` - All case documents
- `document_pages` - Page-level analysis
- `legal_violations` - Tracked violations
- `court_events` - Court calendar
- `communications_matrix` - All communications
- `dvro_violations_tracker` - DVRO breach tracking
- `court_case_tracker` - Multi-jurisdiction cases
- `legal_citations` - Case law references

### Views (52 Total)
Pre-computed queries for:
- Critical documents (relevancy 900+)
- Violations by perpetrator
- Upcoming events
- Timeline consolidation
- False statements summary
- Checkbox perjury analysis

---

## 🎯 Use Cases

### For Legal Strategy
1. **Identify strongest evidence** (Top 20 relevancy list)
2. **Track constitutional violations** (grounds for appeals/lawsuits)
3. **Monitor deadlines** (Court events calendar)
4. **Document perjury** (Micro analysis false statements)

### For Court Filings
1. **Build motions** using highest-scored documents
2. **Reference violations** with proof strength metrics
3. **Create timelines** from event tracker
4. **Cite contradictions** from actions vs. intentions analysis

### For Settlement Negotiations
1. **Demonstrate strength** with high relevancy scores
2. **Show violation patterns** from perpetrator tracking
3. **Reference evidence volume** from overview metrics

---

## 🔐 Data Security

All data stored in Supabase cloud database:
- **URL**: `https://jvjlhxodmbkodzmggwpu.supabase.co`
- **Access**: Encrypted credentials in `.streamlit/secrets.toml`
- **Sync**: Real-time updates from Mac Mini processing
- **Backup**: Automatic cloud backups

---

## 📱 Access

**Local Dashboard**: http://localhost:8501
**Network Access**: http://192.168.4.24:8501
**Run Command**: `streamlit run proj344_master_dashboard.py`

---

## 🔄 Data Processing Flow

1. **Mac Mini** processes documents → uploads to Supabase
2. **Windows Dashboard** reads from Supabase in real-time
3. **Both machines** connected to same central database
4. **Updates appear instantly** across all devices

---

*This dashboard represents a comprehensive legal intelligence system combining traditional legal analysis with modern data science to build the strongest possible case.*
