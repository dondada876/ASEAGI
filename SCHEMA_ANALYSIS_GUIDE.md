# PROJ344 Schema Analysis System

**Comprehensive Database Schema Analysis with 5W+H Framework**

## Overview

The Schema Analysis System provides deep insights into the PROJ344 database structure using the **5W+H Framework**:

- **Why**: Purpose and business logic
- **When**: Temporal aspects and update frequency
- **Where**: Storage location and relationships
- **Who**: Data owners and stakeholders
- **How**: Access patterns and usage

Plus comprehensive analysis of:
- **Records**: Row counts and data volume
- **Relevancy**: Business criticality (CRITICAL/HIGH/MEDIUM/LOW)
- **Requirements**: Must-have vs optional fields
- **Usage**: Frequency and access patterns
- **Importance**: Scored 1-10 for prioritization

## Quick Start

### Run Schema Analysis

```bash
# Make sure credentials are configured
python utilities/schema_analyzer.py
```

### Output Example

```
📊 GLOBAL SCHEMA OVERVIEW
────────────────────────────────────────────────────────────────
  Total Tables Analyzed: 30
  ✅ Existing Tables: 24
  🟢 Active Tables (with data): 15
  ⚪ Empty Tables: 9
  ❌ Missing Tables: 6
  📊 Total Records: 2,543
  📋 Total Columns: 385
```

## Schema Categories

Tables are organized into functional categories:

### 1. Core Data (4 tables)
- `legal_documents` - Primary document repository
- `court_events` - Court proceedings and timeline
- `legal_violations` - Due process violations
- `document_pages` - Page-level document storage

### 2. Tracking & Monitoring (4 tables)
- `court_case_tracker` - Multi-jurisdiction tracking
- `dvro_violations_tracker` - DVRO violation tracking
- `processing_jobs_log` - Job monitoring
- `error_logs` - System error tracking

### 3. Analysis & Intelligence (5 tables)
- `truth_score_history` - Truth scoring with 5W+H
- `justice_score_rollups` - Aggregated justice metrics
- `police_response_analysis` - Police report analysis
- `actions_intentions_matrix` - Intent vs action analysis
- `violation_patterns` - Pattern detection

### 4. Communication (1 table)
- `communications_matrix` - Email/text/call tracking

### 5. Reference Data (2 tables)
- `legal_citations` - Case law and statutes
- `file_metadata` - Raw file information

### 6. Performance & Caching (2 tables)
- `system_processing_cache` - AI result caching
- `query_results_cache` - Query result caching

### 7. Context & State (3 tables)
- `dashboard_snapshots` - Dashboard state preservation
- `context_preservation_metadata` - AI conversation context
- `ai_analysis_results` - AI cost and audit tracking

### 8. Multi-Purpose (2 tables)
- `general_documents` - Universal document intake
- `cross_system_priorities` - Cross-system task management

### 9. CEO Dashboard (3 tables)
- `business_documents` - Business operations
- `personal_documents` - Personal tracking
- `family_documents` - Family-related docs

### 10. Timeline (2 tables)
- `timeline_events` - Event timeline
- `constitutional_violations` - Constitutional violation tracking

### 11. Perjury Detection (3 tables)
- `false_statements_on_forms` - Form statement tracking
- `checkbox_perjury_summary` - Checkbox analysis
- `actions_intentions_discrepancies` - Discrepancy tracking

## Table Relevancy Levels

### 🔴 CRITICAL (Importance: 9-10)
Tables essential for core system functionality:
- `legal_documents` - Core document repository
- `court_events` - Timeline foundation
- `legal_violations` - Legal strategy basis

**Impact if unavailable**: System cannot function

### 🟠 HIGH (Importance: 7-8)
Tables important for key features:
- `document_pages` - Document viewing
- `truth_score_history` - Truth analysis
- `dvro_violations_tracker` - Violation tracking
- `communications_matrix` - Pattern analysis

**Impact if unavailable**: Major features degraded

### 🟡 MEDIUM (Importance: 5-6)
Tables supporting secondary features:
- `file_metadata` - File tracking
- `system_processing_cache` - Performance optimization
- `ai_analysis_results` - Cost tracking
- `context_preservation_metadata` - AI continuity

**Impact if unavailable**: Minor feature loss or performance degradation

### ⚪ LOW (Importance: 1-4)
Tables for convenience or future use:
- `dashboard_snapshots` - State restoration
- `query_results_cache` - Query optimization

**Impact if unavailable**: Minimal - convenience features only

## 5W+H Framework Explanation

### Why (Purpose)
**Question**: Why does this table exist?

**Answer Components**:
- Business purpose
- Problem it solves
- Value it provides

**Example**:
> `legal_documents`: Store and track all legal documents with AI-powered scoring and analysis

### When (Temporal Aspects)
**Question**: When is data created/updated?

**Answer Components**:
- Creation trigger
- Update frequency
- Archival policy

**Example**:
> `legal_documents`: Created when documents uploaded; Updated during AI processing

### Where (Location & Relationships)
**Question**: Where does this data fit in the system?

**Answer Components**:
- Storage location
- Parent/child relationships
- Integration points

**Example**:
> `legal_documents`: Central document repository; Links to document_pages and file_metadata

### Who (Stakeholders)
**Question**: Who owns and accesses this data?

**Answer Components**:
- Data owner
- Primary users
- Access level requirements

**Example**:
> `legal_documents`: Document owners: Don Bucknor; Accessed by: Legal team, AI processors

### How (Usage & Access)
**Question**: How is this data used?

**Answer Components**:
- Query patterns
- Access frequency
- Integration methods

**Example**:
> `legal_documents`: Queried by dashboards for document intelligence; Updated by AI scanners

## Table Requirements

Each table analysis includes field requirements:

### Must Have
Fields absolutely required for table to function:
```
Must have: original_filename, relevancy_number, processing_status
```

### Should Have
Fields strongly recommended but not strictly required:
```
Should have: executive_summary, keywords
```

### Optional
Fields that enhance functionality:
```
Optional: smoking_guns, api_cost_usd
```

## Usage Frequency Classification

- **Very High**: Accessed on every page load or operation
- **High**: Accessed multiple times per session
- **Medium**: Accessed occasionally during specific workflows
- **Low**: Accessed rarely for specific tasks
- **Very Low**: Accessed only for admin/audit purposes

## Running Analysis

### Prerequisites

1. **Supabase credentials configured**:
```bash
# Option 1: Environment variables
export SUPABASE_URL="https://jvjlhxodmbkodzmggwpu.supabase.co"
export SUPABASE_KEY="your-key-here"

# Option 2: .streamlit/secrets.toml
SUPABASE_URL = "https://jvjlhxodmbkodzmggwpu.supabase.co"
SUPABASE_KEY = "your-key-here"
```

2. **Python dependencies**:
```bash
pip install supabase toml
```

### Run Analysis

```bash
python utilities/schema_analyzer.py
```

### Save Report to File

```bash
python utilities/schema_analyzer.py > schema_analysis_report.txt
```

### Analysis Sections

The report includes:

1. **Global Schema Overview**
   - Total tables, records, columns
   - Active vs empty tables
   - Missing tables

2. **Category Breakdown**
   - Tables grouped by function
   - Active count per category

3. **Detailed Table Analysis**
   - Sorted by importance
   - Full 5W+H breakdown
   - Column listing
   - Requirements

4. **Missing Tables**
   - Tables defined but not yet created
   - Purpose of each missing table

5. **Recommendations**
   - Critical empty tables to populate
   - Missing critical tables to create
   - Performance optimization suggestions

## Understanding the Output

### Status Indicators

- 🟢 **ACTIVE** - Table exists and has data
- ⚪ **EMPTY** - Table exists but has no rows
- ❌ **MISSING** - Table not found in database

### Relevancy Indicators

- 🔴 **CRITICAL** - Essential for core functionality
- 🟠 **HIGH** - Important for key features
- 🟡 **MEDIUM** - Supporting features
- ⚪ **LOW** - Convenience or future use

### Importance Scores

Scale: 1-10 (automatically adjusted based on data presence)

- **10**: Absolutely critical
- **8-9**: Very important
- **6-7**: Important
- **4-5**: Moderate importance
- **1-3**: Low importance

## Recommendations Section

The analyzer automatically generates recommendations:

### Critical Issues 🚨
```
🚨 Create court_case_tracker - marked as HIGH relevancy but missing
```
**Action**: Create table immediately using schema definition

### Warnings ⚠️
```
⚠️  Populate communications_matrix - marked as HIGH relevancy but currently empty
```
**Action**: Begin data collection for this table

### Performance 🔧
```
🔧 Consider cache cleanup for system_processing_cache - has 15,234 entries
```
**Action**: Review cache expiration settings or run cleanup

## Customizing Analysis

### Adding New Tables

Edit `utilities/schema_analyzer.py` and add to `TABLE_METADATA`:

```python
TABLE_METADATA = {
    'your_new_table': {
        'why': 'Purpose of the table',
        'when': 'When data is created/updated',
        'where': 'Where it fits in the system',
        'who': 'Data owners and users',
        'how': 'How it is accessed and used',
        'relevancy': 'CRITICAL|HIGH|MEDIUM|LOW',
        'importance': 8,  # 1-10 scale
        'usage_frequency': 'Very High|High|Medium|Low|Very Low',
        'requirements': 'Must have: field1, field2; Should have: field3',
    },
}
```

### Adding New Categories

Edit `categorize_table()` function:

```python
categories = {
    'Your New Category': ['table1', 'table2', 'table3'],
    # ...
}
```

## Integration with Other Tools

### Dashboard Integration

Use schema analysis to:
- Identify which tables dashboards should query
- Determine caching strategies based on usage frequency
- Prioritize dashboard features by table importance

### Development Priorities

Use schema analysis to:
- Prioritize table creation based on relevancy
- Identify data gaps (empty critical tables)
- Plan data migration strategies

### Documentation

Use schema analysis to:
- Generate technical documentation
- Create onboarding materials
- Maintain system architecture docs

## Best Practices

### Regular Analysis
- Run weekly during active development
- Run monthly in production
- Run after major schema changes

### Action on Recommendations
- Address 🚨 critical issues within 24 hours
- Address ⚠️ warnings within 1 week
- Review 🔧 performance suggestions monthly

### Keep Metadata Updated
- Update `TABLE_METADATA` when tables are created
- Update requirements when schema changes
- Update usage patterns as system evolves

## Troubleshooting

### "Missing SUPABASE_KEY"

**Solution**: Create `.streamlit/secrets.toml` with credentials

### "Table not found" errors for known tables

**Possible causes**:
1. Table not yet created (check schema files)
2. Wrong database connection
3. Row Level Security blocking access

**Solution**: Verify table exists in Supabase dashboard

### Inaccurate row counts

**Possible causes**:
1. RLS policies filtering data
2. Cache issues

**Solution**: Use service role key (not anon key) for accurate counts

## Example Output

```
🟢 LEGAL_DOCUMENTS
────────────────────────────────────────────────────────────────
  Category: Core Data
  Status: ACTIVE | Records: 653 | Columns: 42
  🔴 Relevancy: CRITICAL | Importance: 10/10

  ❓ WHY (Purpose):
     Store and track all legal documents with AI-powered scoring and analysis

  ⏰ WHEN (Temporal Aspects):
     Created when documents uploaded; Updated during AI processing

  📍 WHERE (Location & Relationships):
     Central document repository; Links to document_pages and file_metadata

  👤 WHO (Stakeholders):
     Document owners: Don Bucknor; Accessed by: Legal team, AI processors

  🔧 HOW (Usage & Access):
     Queried by dashboards for document intelligence; Updated by AI scanners

  📊 Usage Frequency: Very High - Core table for all dashboards

  ✅ Requirements:
     Must have: original_filename, relevancy_number, processing_status;
     Optional: executive_summary, keywords

  📋 Columns (42):
     - id
     - original_filename
     - renamed_filename
     - document_type
     - relevancy_number
     - legal_number
     - micro_number
     - macro_number
     - executive_summary
     - keywords
     ... and 32 more
```

## Advanced Features

### Export to JSON

Modify the script to export structured data:

```python
# Add to schema_analyzer.py
def export_to_json(tables, metadata):
    output = {
        'generated': datetime.now().isoformat(),
        'tables': {}
    }

    for table_name, table_info in tables.items():
        output['tables'][table_name] = {
            'metadata': metadata.get(table_name, {}),
            'stats': table_info
        }

    return json.dumps(output, indent=2)
```

### Custom Reports

Create filtered reports for specific audiences:

```python
# Executive summary (CRITICAL and HIGH only)
# Developer guide (with column details)
# Data team guide (with relationships)
```

## Related Documentation

- [Context Preservation Schema](schemas/README_CONTEXT_PRESERVATION.md)
- [Database Schema Files](schemas/)
- [System Architecture](PROJ344_SYSTEM_SUMMARY.md)

## Support

For questions or issues:
- Review this guide
- Check table metadata in `schema_analyzer.py`
- Review schema SQL files in `schemas/` directory

---

**Last Updated**: 2025-11-05
**Version**: 1.0.0
**Author**: PROJ344 Development Team
