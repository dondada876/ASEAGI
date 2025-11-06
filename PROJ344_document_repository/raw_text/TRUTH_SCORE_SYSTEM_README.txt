# Truth Score & Justice Analysis System
**Complete Guide to Enhanced Truth Scoring, Timeline Analysis & Police Report Integration**

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Core Components](#core-components)
3. [Database Schema](#database-schema)
4. [Police Report Scanner](#police-report-scanner)
5. [Enhanced Dashboard](#enhanced-dashboard)
6. [Truth Scoring Methodology](#truth-scoring-methodology)
7. [Justice Score Calculation](#justice-score-calculation)
8. [Usage Guide](#usage-guide)
9. [API Reference](#api-reference)

---

## 🎯 System Overview

The Truth Score & Justice Analysis System provides comprehensive tracking and analysis of every statement, event, action, motion, and filing in your legal case. Each entry is scored for truthfulness (0-100) and rolls up into an overall **Justice Score** that represents the integrity of the entire case.

### Key Features

✅ **Truth Scoring** - Every timeline entry scored 0-100 (0=proven false, 100=verified true)
✅ **Justice Score Rollup** - Weighted average of all truth scores
✅ **5W+H Master Timeline** - Complete source of truth answering When, Where, Who, What, Why, How
✅ **Police Report Integration** - Automated scanning and PX naming convention
✅ **Enhanced Visualizations** - Heatmaps, trends, actor comparisons, timeline charts
✅ **Evidence Binding** - Link police reports and evidence to timeline events
✅ **Lie Detection** - Automatically identify and track proven false statements

---

## 🏗️ Core Components

### 1. Master Absolute Timeline (`master_absolute_timeline` table)

The **source of truth** for your case. Every event, statement, action, motion, and filing is recorded with:

- **5W+H Analysis**: When, Where, Who, What, Why, How
- **Truth Score**: 0-100 rating of truthfulness
- **Evidence Links**: Supporting and contradicting evidence
- **Fraud Detection**: Perjury and fraud scoring
- **Importance Weighting**: CRITICAL, HIGH, MEDIUM, LOW

### 2. Police Report Scanner (`police_report_scanner.py`)

Automated system to:

- Scan police report images/PDFs
- Extract page numbers using Claude Vision AI
- Apply PX naming convention
- Tag and categorize reports
- Extract case numbers and dates

### 3. Enhanced Dashboard (`enhanced_truth_score_dashboard.py`)

Interactive Streamlit dashboard with:

- Justice Score gauge (main metric)
- Truth score heatmaps
- Timeline trend analysis
- Actor comparison charts
- 5W+H master matrix
- Lies and false statements tracker
- Export and reporting tools

---

## 🗄️ Database Schema

### Tables

#### 1. `master_absolute_timeline`

Primary table storing all timeline entries with truth scores.

**Key Fields:**

```sql
- entry_id (TEXT)           -- Unique ID: TYPE-YYYYMMDD-NNN
- entry_type (TEXT)          -- STATEMENT, EVENT, ACTION, MOTION, FILING, etc.
- category (TEXT)            -- COURT_EVENT, LEGAL_DOCUMENT, VIOLATION, etc.

-- 5W+H Fields
- when_datetime (TIMESTAMPTZ)     -- When did it happen?
- where_location (TEXT)            -- Where did it occur?
- who_primary (TEXT)               -- Who is the primary actor?
- what_title (TEXT)                -- What happened (brief)?
- what_description (TEXT)          -- What happened (detailed)?
- why_stated_reason (TEXT)         -- Why did it happen?
- how_method (TEXT)                -- How was it done?

-- Truth Scoring
- truth_score (INTEGER 0-100)      -- 0=False, 100=True
- fraud_score (INTEGER 0-100)      -- 0=No fraud, 100=Definite fraud
- perjury_score (INTEGER 0-100)    -- Perjury likelihood

-- Evidence
- has_supporting_evidence (BOOLEAN)
- supporting_evidence_ids (TEXT[])
- contradicted_by_evidence (BOOLEAN)
- contradicting_evidence_ids (TEXT[])

-- Verification
- verified_by_official_record (BOOLEAN)
- official_record_reference (TEXT)
- witness_corroboration (BOOLEAN)

-- Importance
- importance_level (TEXT)          -- CRITICAL, HIGH, MEDIUM, LOW
- relevancy_score (INTEGER 0-1000)
```

#### 2. `police_reports`

Police reports with PX naming convention and page tracking.

**Key Fields:**

```sql
- id (BIGSERIAL PRIMARY KEY)
- px_code (TEXT)                   -- PX0, PX01, PX06-P1-P6, etc.
- report_number (TEXT)             -- Official report number
- report_type (TEXT)               -- Incident, CAD, Arrest, etc.
- incident_date (TIMESTAMPTZ)
- total_pages (INTEGER)
- current_page (INTEGER)
- truth_score (INTEGER 0-100)
- is_smoking_gun (BOOLEAN)
- relevancy_score (INTEGER 0-1000)
```

#### 3. `evidence_timeline_binding`

Links police reports to timeline entries.

**Key Fields:**

```sql
- timeline_entry_id (BIGINT)       -- FK to master_absolute_timeline
- police_report_id (BIGINT)        -- FK to police_reports
- binding_type (TEXT)              -- SUPPORTS, CONTRADICTS, NEUTRAL, CLARIFIES
- binding_strength (TEXT)          -- DEFINITIVE, STRONG, MODERATE, WEAK
- truth_impact (INTEGER)           -- Impact on truth score (+/- points)
```

#### 4. `truth_score_history`

Tracks changes to truth scores over time.

**Key Fields:**

```sql
- timeline_entry_id (BIGINT)
- old_truth_score (INTEGER)
- new_truth_score (INTEGER)
- score_change (INTEGER)
- change_reason (TEXT)
- changed_by (TEXT)
- changed_at (TIMESTAMPTZ)
```

---

## 🔍 Police Report Scanner

### PX Naming Convention

The system automatically renames police report files using the PX convention:

| Format | Meaning | Example |
|--------|---------|---------|
| `PX0` | No pages (0 pages) | `PX0_empty_report.pdf` |
| `PX01` | Single page (1 page) | `PX01_incident_summary.pdf` |
| `PX06-P1-P6` | 6 pages, showing page 1 | `PX06-P1-P6_arrest_report.pdf` |
| `PX12-P5-P12` | 12 pages, showing page 5 | `PX12-P5-P12_full_investigation.pdf` |

### Usage

```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY='your-key-here'

# Scan a directory for police reports (dry run)
python3 police_report_scanner.py /path/to/documents

# Actually rename files
python3 police_report_scanner.py /path/to/documents --rename

# Move renamed files to output directory
python3 police_report_scanner.py /path/to/documents --rename --output-dir /path/to/organized

# Non-recursive (current directory only)
python3 police_report_scanner.py /path/to/documents --no-recursive
```

### What It Does

1. **Scans** directory for files matching police report patterns
2. **Analyzes** each image/PDF using Claude Vision AI
3. **Extracts**:
   - Page numbers (current page / total pages)
   - Report type (Incident, CAD, Arrest, etc.)
   - Case/Incident number
   - Report date
   - Confidence score
4. **Renames** files with PX convention
5. **Generates** JSON report with all findings

### Example Output

```
🚔 POLICE REPORT SCANNER & LABELING SYSTEM
══════════════════════════════════════════════════════════════════
Directory: /home/user/evidence/police_reports
Recursive: True
Rename files: True
══════════════════════════════════════════════════════════════════

📂 Found 25 potential documents in /home/user/evidence/police_reports
🚔 15 files match police report patterns

[1/15] Processing: incident_report_aug2024.pdf
  ✓ Confidence: 95%
  ✓ Type: Incident Report
  ✓ Case: 2024-12345
  ✓ Pages: 6
✅ Renamed: incident_report_aug2024.pdf → PX06-P1-P6_incident_report_aug2024.pdf

...

📊 Report saved to: police_reports_scan_results.json

=== SUMMARY ===
Total files processed: 15
Successful scans: 15
Files renamed: 15
Police reports identified: 14
```

---

## 📊 Enhanced Dashboard

### Launch

```bash
streamlit run enhanced_truth_score_dashboard.py
```

Access at: http://localhost:8501

### Dashboard Sections

#### 1. ⚖️ Justice Score

**Main metric** showing overall case truth integrity.

- **Gauge visualization** (0-100)
- **Truth distribution** (Truthful / Questionable / False)
- **Pie chart** breakdown
- **Key statistics**

#### 2. 📈 Truth Score Visualizations

Four interactive tabs:

**📊 Heatmap**
- Categories (rows) × Time (columns)
- Color-coded truth scores
- Identify patterns and trends

**📉 Trends**
- Daily average truth scores
- Activity volume overlay
- Threshold lines (75% truthful, 25% false)

**👥 By Actor**
- Compare truth scores by person
- Identify credible vs. non-credible actors
- Sorted from lowest to highest truth

**📅 Timeline**
- Scatter plot: truth score over time
- Color-coded by category
- Size indicates importance
- Interactive hover details

#### 3. 🔍 5W+H Master Matrix

Complete reference table with filters:

- **Category filter** (Court Event, Document, Violation, etc.)
- **Truth score range** slider
- **Importance filter** (Critical, High, Medium, Low)
- **Entry type filter** (Statement, Event, Action, Motion, Filing)

Displays:
- When, Where, Who, What, Why, How
- Truth score (color-coded)
- Importance level
- Category

#### 4. 🚨 Lies & False Statements

Dedicated section for proven lies (truth score < 25):

- **Count of false statements**
- **Expandable details** for each lie
- **Actor identification**
- **Fraud and perjury scores**
- **Timestamp and location**

#### 5. 🚔 Police Reports Integration

If police reports table exists:

- **Total reports count**
- **Smoking gun count**
- **Average truth score**
- **High relevancy count**
- **Full report list** with PX codes

#### 6. 📥 Export & Reporting

Three export options:

1. **Full Justice Report** (TXT)
   - Justice score
   - Truth summary
   - All proven lies
   - Formatted for printing

2. **Timeline CSV** (CSV)
   - Complete timeline data
   - All fields and scores
   - For Excel analysis

3. **Lies Only CSV** (CSV)
   - Only false statements
   - For targeted review

---

## 🎯 Truth Scoring Methodology

### How Truth Scores Are Calculated

Each timeline entry receives a truth score (0-100) based on:

#### Base Score: 50 (Neutral)

**Evidence of Truth** (adds points):
- `+25` Has supporting evidence
- `+25` Verified by official record (court order, transcript, etc.)
- `+10` Witness corroboration
- `+10` Timestamp verified

**Evidence of Falsehood** (subtracts points):
- `-40` Contradicted by evidence
- `-20` Inconsistent statements
- `-15` Missing required evidence
- `0` Proven false (overrides to 0)

**Fraud Indicators** (subtracts points):
- `fraud_score > 70`: `-30`
- `fraud_score 50-70`: `-15`

#### Truth Score Categories

| Score | Category | Meaning |
|-------|----------|---------|
| 90-100 | VERIFIED_TRUE | Confirmed by multiple sources |
| 75-89 | LIKELY_TRUE | Strong evidence, few contradictions |
| 50-74 | UNVERIFIED | Neutral, needs investigation |
| 25-49 | QUESTIONABLE | Contradictions or inconsistencies |
| 10-24 | LIKELY_FALSE | Strong contradicting evidence |
| 0-9 | PROVEN_FALSE | Definitively disproven |

### Truth Status Flags

```python
truth_status IN (
    'VERIFIED_TRUE',      # Confirmed by official records
    'LIKELY_TRUE',        # Strong supporting evidence
    'UNVERIFIED',         # No evidence either way
    'QUESTIONABLE',       # Some contradictions
    'LIKELY_FALSE',       # Probable lie
    'PROVEN_FALSE'        # Definitively false
)
```

---

## ⚖️ Justice Score Calculation

### Weighted Average Formula

The **Justice Score** is a weighted average of all truth scores, emphasizing critical items.

```python
weights = []
scores = []

for item in timeline:
    weight = 1.0  # Base weight

    # Weight by importance
    if item.importance == 'CRITICAL':
        weight = 3.0
    elif item.importance == 'HIGH':
        weight = 2.0
    elif item.importance == 'MEDIUM':
        weight = 1.0
    else:  # LOW
        weight = 0.5

    # Extra weight for court filings
    if item.entry_type in ['MOTION', 'FILING', 'DECLARATION']:
        weight *= 1.5

    weights.append(weight)
    scores.append(item.truth_score)

justice_score = weighted_average(scores, weights)
```

### Interpretation

| Justice Score | Assessment | Action |
|---------------|------------|--------|
| 85-100 | **Excellent** - High integrity case | Strong position |
| 70-84 | **Good** - Mostly truthful with some issues | Address weaknesses |
| 50-69 | **Fair** - Mixed truth and falsehoods | Investigation needed |
| 25-49 | **Poor** - Significant dishonesty | Major concerns |
| 0-24 | **Critical** - Widespread fraud/perjury | Urgent action required |

---

## 📚 Usage Guide

### Step 1: Deploy Database Schema

```bash
# Connect to Supabase
# Copy and run master_timeline_schema.sql in SQL Editor

# Or use command line:
psql -h db.xxx.supabase.co -U postgres -d postgres -f master_timeline_schema.sql
```

### Step 2: Populate Timeline Data

#### Option A: Manual Entry

```sql
INSERT INTO master_absolute_timeline (
    entry_id, entry_type, category,
    when_datetime, where_location, who_primary,
    what_title, what_description,
    why_stated_reason, how_method,
    truth_score, importance_level
) VALUES (
    'FILING-20240815-001',
    'FILING',
    'LEGAL_DOCUMENT',
    '2024-08-15 14:30:00',
    'Superior Court',
    'Jane Doe',
    'Motion to Dismiss',
    'Motion filed requesting dismissal of case',
    'Lack of jurisdiction',
    'Court filing system',
    75,
    'HIGH'
);
```

#### Option B: Import from Existing Tables

The dashboard automatically aggregates from:
- `court_events`
- `legal_documents`
- `legal_violations`
- `communications_matrix`

### Step 3: Scan Police Reports

```bash
# Set API key
export ANTHROPIC_API_KEY='sk-ant-...'

# Scan and rename police reports
python3 police_report_scanner.py ~/evidence/police --rename --output-dir ~/evidence/organized
```

### Step 4: Bind Evidence to Timeline

```sql
-- Link police report to timeline entry
INSERT INTO evidence_timeline_binding (
    timeline_entry_id, police_report_id,
    binding_type, binding_strength,
    binding_description, truth_impact
) VALUES (
    123,  -- timeline entry ID
    45,   -- police report ID
    'CONTRADICTS',
    'DEFINITIVE',
    'Police report shows different timeline than stated in declaration',
    -30   -- Reduces truth score by 30 points
);
```

### Step 5: Launch Dashboard

```bash
streamlit run enhanced_truth_score_dashboard.py
```

### Step 6: Analyze & Export

1. **Review Justice Score** - Overall case integrity
2. **Check Heatmaps** - Identify patterns
3. **Review Lies Section** - Focus on proven false statements
4. **Compare Actors** - Who is credible?
5. **Export Reports** - Generate documentation

---

## 🔧 API Reference

### Python Functions

#### `calculate_truth_score(item_data: Dict) -> int`

Calculate truth score for a timeline item.

**Parameters:**
```python
item_data = {
    'has_supporting_evidence': bool,
    'verified_by_official_record': bool,
    'witness_corroboration': bool,
    'timestamp_verified': bool,
    'contradicted_by_evidence': bool,
    'proven_false': bool,
    'inconsistent_statements': bool,
    'missing_required_evidence': bool,
    'fraud_score': int (0-100)
}
```

**Returns:** `int` (0-100)

#### `calculate_justice_score(truth_scores: List[Dict]) -> float`

Calculate weighted justice score from all truth scores.

**Parameters:**
```python
truth_scores = [
    {
        'truth_score': int,
        'importance': str,  # CRITICAL, HIGH, MEDIUM, LOW
        'category': str     # MOTION, FILING, etc.
    },
    ...
]
```

**Returns:** `float` (rounded to 1 decimal)

### SQL Views

#### `v_timeline_truth_analysis`

All timeline entries with truth scores and evidence counts.

```sql
SELECT * FROM v_timeline_truth_analysis
WHERE truth_score < 50
ORDER BY when_datetime DESC;
```

#### `v_proven_lies`

Only entries with truth score < 25.

```sql
SELECT * FROM v_proven_lies
WHERE who_primary = 'John Doe';
```

#### `v_justice_score_calculation`

Overall justice score and statistics.

```sql
SELECT * FROM v_justice_score_calculation;
```

Output:
```
total_entries | simple_average | weighted_justice_score | truthful_count | false_count | questionable_count
--------------|----------------|------------------------|----------------|-------------|-------------------
247           | 67.3           | 71.8                   | 158            | 23          | 66
```

#### `v_truth_by_actor`

Truth scores grouped by actor.

```sql
SELECT * FROM v_truth_by_actor
ORDER BY lies_count DESC;
```

---

## 📝 Examples

### Example 1: Add Court Event

```sql
INSERT INTO master_absolute_timeline (
    entry_id, entry_type, category,
    when_datetime, where_location, who_primary,
    what_title, what_description,
    how_method, truth_score, importance_level,
    verified_by_official_record
) VALUES (
    'EVENT-20240820-001',
    'EVENT',
    'COURT_EVENT',
    '2024-08-20 10:00:00',
    'Superior Court, Dept 12',
    'Judge Smith',
    'Ex Parte Hearing',
    'Emergency hearing on custody modification',
    'In-person court proceeding',
    95,
    'CRITICAL',
    true
);
```

### Example 2: Record False Statement

```sql
INSERT INTO master_absolute_timeline (
    entry_id, entry_type, category,
    when_datetime, where_location, who_primary,
    what_title, what_description,
    is_under_oath, contains_false_statements,
    false_statement_details,
    truth_score, perjury_score, fraud_score,
    importance_level, contradicted_by_evidence,
    contradicting_evidence_ids
) VALUES (
    'STATEMENT-20240815-002',
    'STATEMENT',
    'VIOLATION',
    '2024-08-15 14:30:00',
    'Sworn Declaration',
    'Jane Doe',
    'False statement about income',
    'Declared income as $30,000 when tax returns show $75,000',
    true,  -- under oath
    true,  -- contains false statements
    'Understated income by $45,000 in sworn declaration',
    0,     -- truth score: proven false
    95,    -- perjury score
    90,    -- fraud score
    'CRITICAL',
    true,  -- contradicted by evidence
    ARRAY['TAX-2023-W2', 'TAX-2023-1040']
);
```

### Example 3: Bind Police Report to Event

```sql
-- First, insert police report
INSERT INTO police_reports (
    px_code, report_number, report_type,
    incident_date, total_pages, truth_score,
    relevancy_score, is_smoking_gun
) VALUES (
    'PX06-P1-P6',
    '2024-08-15-1234',
    'Incident Report',
    '2024-08-15 20:00:00',
    6,
    85,
    950,
    true
) RETURNING id;

-- Then bind to timeline
INSERT INTO evidence_timeline_binding (
    timeline_entry_id, police_report_id,
    binding_type, binding_strength,
    binding_description, truth_impact
) VALUES (
    456,  -- timeline entry about alleged incident
    789,  -- police report ID from above
    'CONTRADICTS',
    'DEFINITIVE',
    'Police report shows no evidence of alleged assault. Officer notes no visible injuries, no witnesses, conflicting statements.',
    -50
);
```

---

## 🚀 Quick Start Checklist

- [ ] Deploy `master_timeline_schema.sql` to Supabase
- [ ] Set `ANTHROPIC_API_KEY` environment variable
- [ ] Install Python dependencies: `pip install streamlit pandas plotly numpy supabase anthropic pillow PyPDF2`
- [ ] Scan police reports: `python3 police_report_scanner.py /path/to/reports --rename`
- [ ] Populate timeline data (manual or import)
- [ ] Launch dashboard: `streamlit run enhanced_truth_score_dashboard.py`
- [ ] Review justice score and lies
- [ ] Bind evidence to timeline entries
- [ ] Export reports

---

## 📞 Support

For issues or questions:

1. Check the SQL views for data issues: `v_timeline_truth_analysis`
2. Review the police scanner JSON report: `police_reports_scan_results.json`
3. Check Streamlit logs for dashboard errors
4. Verify Supabase connection and credentials

---

## 📄 License

ASEAGI System - Legal Case Intelligence Platform
Copyright (c) 2025

---

**Last Updated:** 2025-11-05
**Version:** 2.0.0
**Status:** ✅ Production Ready
