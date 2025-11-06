# 🐑 Claude Shepherd Agent - Complete Usage Guide

Your AI-powered guardian for code quality, database monitoring, and case intelligence.

---

## 📖 Table of Contents

1. [What is the Shepherd Agent?](#what-is-the-shepherd-agent)
2. [Quick Start](#quick-start)
3. [Code & Repository Features](#code--repository-features)
4. [Database Monitoring Features](#database-monitoring-features)
5. [Case Impact Analysis](#case-impact-analysis)
6. [Usage Examples](#usage-examples)
7. [Telegram Commands](#telegram-commands)
8. [CLI Interface](#cli-interface)
9. [Python API](#python-api)
10. [Best Practices](#best-practices)
11. [Advanced Features](#advanced-features)
12. [Troubleshooting](#troubleshooting)

---

## What is the Shepherd Agent?

The **Claude Shepherd Agent** is an AI-powered assistant that monitors your ASEAGI repository and legal case documents. Think of it as your personal AI consultant that:

- 🔍 Reviews your code changes before they go live
- 💬 Answers questions about your codebase
- 📊 Monitors database health 24/7
- 📈 Analyzes how new evidence impacts your legal case
- 🐛 Catches issues before they become problems
- 📝 Generates documentation automatically

**Powered by:**
- **Claude Sonnet 4** - Anthropic's most advanced AI
- **Qdrant** - Vector database for semantic search
- **GitHub API** - Repository access
- **Supabase** - Database monitoring

---

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY='sk-ant-api03-your-key'
export GITHUB_TOKEN='ghp_your-token'
export SUPABASE_URL='your-supabase-url'
export SUPABASE_KEY='your-supabase-key'

# Run the agent
python claude_shepherd_agent.py
```

### First Commands

```bash
# Monitor database (last 24 hours)
python claude_shepherd_agent.py
> Choice: 6
> Time period: 24h

# Generate case impact report
> Choice: 7
> Time period: 24h

# Ask a question
> Choice: 3
> Your question: How does document upload work?
```

---

## Code & Repository Features

### 1. Repository Indexing

**What it does:** Creates a searchable vector database of your entire codebase.

**When to use:**
- First time setup
- After major code changes
- Weekly refresh for active projects

**Usage:**

```bash
# CLI
python claude_shepherd_agent.py
> Choice: 1  # Index repository

# What happens:
# 1. Scans all files in GitHub repository
# 2. Generates embeddings for each file
# 3. Stores in Qdrant vector database
# 4. Enables semantic search
```

**Output:**
```
🔍 Indexing repository: dondada876/ASEAGI
📦 Creating collection 'aseagi_codebase'
📄 Found 47 files
✅ Indexed 47 files
🎉 Indexing complete!
```

**Time:** 5-10 minutes for typical repository

### 2. Pull Request Review

**What it does:** AI-powered code review with security analysis.

**When to use:**
- Before merging any PR
- For complex changes
- When you want a second opinion

**Usage:**

```bash
# CLI
python claude_shepherd_agent.py
> Choice: 2  # Review PR
> PR number: 5

# Telegram
/shepherd_review_pr 5
```

**What the agent checks:**

1. **Alignment Check**
   - Does code fit project architecture?
   - Follows existing patterns?
   - Consistent with coding standards?

2. **Quality Assessment**
   - Code readability
   - Best practices followed
   - Potential bugs or issues

3. **Security Review**
   - SQL injection risks
   - XSS vulnerabilities
   - API key exposure
   - Authentication issues

4. **Integration Points**
   - How it affects other components
   - Database schema changes
   - API contract changes

5. **Suggestions**
   - Specific improvements
   - Alternative approaches
   - Optimization opportunities

6. **Risk Assessment**
   - Breaking changes identified
   - Deployment risks
   - Rollback strategy needed?

**Output Example:**

```json
{
  "pr_number": 5,
  "title": "Add video upload support",
  "author": "dondada876",
  "files_changed": 3,
  "recommendation": "✅ Approve - Looks good to merge",
  "summary": "This PR adds video file support to the upload system.
             Code quality is good, no security issues found.
             Database schema changes are backward compatible.
             Recommend merge after CI passes."
}
```

### 3. Q&A System (RAG)

**What it does:** Answer questions about your codebase using AI + semantic search.

**When to use:**
- Onboarding new team members
- Understanding complex code
- Finding specific implementations
- Documentation research

**Usage:**

```bash
# CLI
python claude_shepherd_agent.py
> Choice: 3  # Answer question
> Your question: How does the Telegram bot handle document uploads?

# Telegram
/shepherd_ask How does the Telegram bot handle document uploads?
```

**Example Questions:**

**Architecture:**
- "What is the overall system architecture?"
- "How do the components communicate?"
- "Where is data stored?"

**Implementation:**
- "How does document upload work?"
- "Where is the relevancy score calculated?"
- "How are notifications sent?"

**Database:**
- "What tables store police reports?"
- "How is the audit trail implemented?"
- "Where are processing logs stored?"

**Troubleshooting:**
- "Why might an upload fail?"
- "How to retry failed uploads?"
- "Where are error logs stored?"

**Output Example:**

```
🤔 Consulting repository knowledge...

The Telegram bot handles document uploads through a conversational
flow implemented in telegram_document_bot.py:

1. User sends /start command
2. Bot responds with upload instructions
3. User uploads file (photo, PDF, document)
4. Bot enters ConversationHandler state machine
5. Collects metadata in sequence:
   - Document type (PLCR, DECL, EVID, etc.)
   - Document date
   - Title
   - Notes
   - Relevancy score (0-1000)
6. Stores in telegram_uploads table
7. Triggers n8n webhook for processing
8. Returns confirmation to user

Key files:
- telegram_document_bot.py:145 - Upload handler
- telegram_system_schema.sql:50 - telegram_uploads table
- n8n_telegram_processing_workflow.json - Processing workflow
```

### 4. Architecture Analysis

**What it does:** Comprehensive analysis of repository structure.

**When to use:**
- Planning new features
- Refactoring decisions
- Architecture reviews
- Documentation updates

**Usage:**

```bash
# CLI
python claude_shepherd_agent.py
> Choice: 4  # Analyze architecture

# Telegram
/shepherd_analyze
```

**What it analyzes:**

- File organization
- Component relationships
- Data flow patterns
- Integration points
- Technology choices
- Potential improvements
- Missing components
- Code duplication

**Output Example:**

```json
{
  "total_files": 47,
  "breakdown": {
    "python": 12,
    "sql": 3,
    "markdown": 15,
    "json": 5
  },
  "analysis": "
    System Architecture Overview:
    - Mobile-first design using Telegram
    - Event-driven processing with n8n
    - Multi-tier storage (S3, Drive, Backblaze)
    - PostgreSQL database with 5 core tables

    Component Relationships:
    - Telegram bot → n8n webhooks → Supabase
    - Dashboards → Supabase (read-only)
    - Shepherd agent → All components (monitoring)

    Potential Improvements:
    - Add caching layer for dashboard queries
    - Implement rate limiting on webhooks
    - Add integration tests for workflows
  "
}
```

### 5. Documentation Generation

**What it does:** Auto-generate comprehensive documentation for any file.

**When to use:**
- Creating README files
- Onboarding documentation
- API documentation
- Code handoffs

**Usage:**

```bash
# CLI
python claude_shepherd_agent.py
> Choice: 5  # Generate documentation
> File path: telegram_document_bot.py
```

**Generated Sections:**

1. **Purpose & Overview**
   - What the file does
   - Why it exists
   - How it fits in the system

2. **Key Functions/Classes**
   - Function signatures
   - Parameters and return types
   - Description of each function

3. **Dependencies**
   - External libraries
   - Internal imports
   - API requirements

4. **Usage Examples**
   - Code snippets
   - Common use cases
   - Configuration options

5. **Integration Points**
   - Which components it connects to
   - Data flow in/out
   - Events it triggers

**Output Example:**

```markdown
# telegram_document_bot.py

## Purpose
Telegram bot for mobile document upload in the ASEAGI system.
Provides conversational interface for collecting document metadata
and triggering the n8n processing pipeline.

## Key Functions

### start(update, context)
**Parameters:**
- update: Telegram Update object
- context: CallbackContext

**Returns:** None

**Description:** Handles /start command, displays welcome message
and upload instructions.

### handle_document(update, context)
**Parameters:**
- update: Telegram Update object with document
- context: CallbackContext

**Returns:** ConversationHandler state

**Description:** Receives document upload, initiates metadata
collection conversation flow.

## Dependencies
- python-telegram-bot: Telegram Bot API
- supabase: Database client
- requests: HTTP client for webhooks

## Usage Example
```python
# Start the bot
python telegram_document_bot.py

# User interaction:
# 1. /start
# 2. Upload document
# 3. Answer prompts
# 4. Receive confirmation
```

## Integration Points
- **Database:** Inserts to telegram_uploads table
- **n8n:** Triggers webhook for processing
- **Storage:** Files uploaded to S3 via n8n
```

---

## Database Monitoring Features

### 6. Monitor Ingestion Tables

**What it does:** Real-time monitoring of all data ingestion tables.

**When to use:**
- Daily health checks
- Troubleshooting upload issues
- Performance monitoring
- Before/after deployments

**Usage:**

```bash
# CLI
python claude_shepherd_agent.py
> Choice: 6  # Monitor ingestion tables
> Time period: 24h  # Options: 1h, 24h, 7d, 30d

# Telegram
/shepherd_monitor 24h
```

**Monitored Tables:**

1. **telegram_uploads** (Source of Truth)
   - Total uploads
   - Completed vs. failed
   - Processing status
   - Document type breakdown

2. **processing_logs** (Audit Trail)
   - Stages executed
   - Success/failure rates
   - Error patterns
   - Processing duration

3. **storage_registry** (File Locations)
   - Files stored
   - Storage provider distribution
   - Total storage usage (MB/GB)
   - Verification status

4. **notification_queue** (Async Notifications)
   - Total notifications
   - Sent vs. pending
   - Failed deliveries
   - Average delivery time

**Health Score:**
- 🟢 **HEALTHY** - >95% success rate
- 🟡 **DEGRADED** - 80-95% success rate
- 🔴 **CRITICAL** - <80% success rate

**Output Example:**

```json
{
  "period": "24h",
  "timestamp": "2025-11-06T10:30:00Z",
  "health_score": "🟢 HEALTHY - 98.5% success rate",

  "uploads": {
    "total": 12,
    "completed": 11,
    "failed": 1,
    "processing": 0,
    "by_type": {
      "PLCR": 5,
      "DECL": 3,
      "EVID": 4
    }
  },

  "processing": {
    "validation_completed": 12,
    "storage_completed": 11,
    "extraction_completed": 11,
    "enhancement_completed": 10
  },

  "storage": {
    "total_files": 11,
    "total_size_mb": 45.6,
    "by_provider": {
      "s3": 11,
      "google_drive": 10,
      "backblaze": 9
    }
  },

  "notifications": {
    "total": 24,
    "sent": 23,
    "pending": 1,
    "failed": 0
  }
}
```

**When to act:**

- **🔴 CRITICAL** - Immediate investigation required
- **🟡 DEGRADED** - Review errors, check logs
- **🟢 HEALTHY** - System operating normally

### 7. Monitor Schema Changes

**What it does:** Verify database schema integrity.

**When to use:**
- After database migrations
- Before major deployments
- Weekly health checks
- Troubleshooting data issues

**Usage:**

```bash
# CLI
python claude_shepherd_agent.py
> Choice: 9  # Monitor schema changes

# Telegram
/shepherd_schema
```

**What it checks:**

- ✅ All expected tables exist
- ✅ No unexpected tables
- ✅ Table structure matches schema
- ⚠️ Missing tables
- ⚠️ Extra tables (schema drift)

**Expected Tables:**
1. `telegram_uploads`
2. `processing_logs`
3. `storage_registry`
4. `notification_queue`
5. `user_preferences`
6. `legal_documents`

**Output Example:**

```json
{
  "timestamp": "2025-11-06T10:30:00Z",
  "schema_health": "HEALTHY",
  "expected_tables": 6,
  "actual_tables": 6,
  "missing_tables": [],
  "unexpected_tables": []
}
```

**If schema is DEGRADED:**

```json
{
  "schema_health": "DEGRADED",
  "missing_tables": ["user_preferences"],
  "unexpected_tables": ["temp_uploads_backup"],
  "recommendation": "Run telegram_system_schema.sql to create missing tables"
}
```

---

## Case Impact Analysis

### 8. Generate Case Impact Report

**What it does:** AI-powered analysis of how new documents affect case D22-03244.

**When to use:**
- After uploading new evidence
- Daily case reviews
- Pre-court preparation
- Strategy planning sessions

**Usage:**

```bash
# CLI
python claude_shepherd_agent.py
> Choice: 7  # Generate case impact report
> Time period: 24h  # Options: 1h, 24h, 7d, 30d

# Telegram
/shepherd_impact 7d
```

**Case Context (Built-in):**
- **Case:** D22-03244 (Custody case)
- **Parties:** Richmond PD, Berkeley PD
- **Critical Date:** August 4, 2024
- **Focus:** Constitutional violations, police conduct, custody arrangements

**Analysis Includes:**

1. **Document Classification**
   - Type (police report, declaration, evidence)
   - Relevance (0-1000 scale)
   - Date and timeline placement
   - Parties involved

2. **Case Impact**
   - Does it strengthen or weaken case?
   - What arguments does it support?
   - What claims does it contradict?
   - How does it change case strategy?

3. **Timeline Updates**
   - New events added to timeline
   - Gaps filled in narrative
   - Sequence of events clarified
   - Critical dates identified

4. **Evidence Strength**
   - Rating (1-10) for each document
   - Admissibility assessment
   - Credibility factors
   - Corroboration with existing evidence

5. **Contradictions**
   - Conflicts with other evidence
   - Witness statement discrepancies
   - Timeline inconsistencies
   - Explanation or resolution needed

6. **Next Steps**
   - What actions to take
   - Which documents to review together
   - What additional evidence to seek
   - Court filing recommendations

7. **Priority Documents**
   - Which documents need immediate attention
   - Documents for expert review
   - Documents to share with counsel

**Output Example:**

```json
{
  "period": "7d",
  "new_documents_count": 5,
  "documents_analyzed": 5,
  "average_relevancy": 850,

  "document_types": {
    "PLCR": 3,
    "DECL": 1,
    "EVID": 1
  },

  "claude_analysis": "
    === CASE IMPACT ANALYSIS ===

    Document Classification:
    Three new police reports (PLCR) significantly strengthen the case:

    1. Richmond PD Report 24-7889 (Aug 4, 2024) - Relevancy: 920/1000
       - PRIMARY EVIDENCE: Initial incident report
       - Directly supports constitutional violation claims
       - Establishes timeline baseline

    2. Berkeley PD Follow-up (Aug 5, 2024) - Relevancy: 850/1000
       - CORROBORATING EVIDENCE: Second jurisdiction confirms facts
       - Provides witness statements

    3. Richmond PD Supplemental (Aug 10, 2024) - Relevancy: 780/1000
       - ADDITIONAL DETAILS: Investigation findings
       - May contain new witness interviews

    Case Impact:
    These documents STRENGTHEN the case significantly:
    - Establish multi-jurisdictional documentation
    - Provide official police acknowledgment of incident
    - Create verifiable timeline
    - Support claims with official records

    Timeline Updates:
    - Aug 4, 2024: Initial incident (Richmond PD responds)
    - Aug 5, 2024: Berkeley PD involvement (inter-departmental)
    - Aug 10, 2024: Follow-up investigation completed

    Evidence Strength Ratings:
    - Richmond PD Report 24-7889: 9/10 (Official record, contemporaneous)
    - Berkeley PD Follow-up: 8/10 (Corroborates primary evidence)
    - Richmond PD Supplemental: 7/10 (Additional details, investigation)

    Contradictions:
    NONE IDENTIFIED - All three reports align consistently
    This strengthens credibility significantly

    Next Steps:
    1. IMMEDIATE: Review Richmond PD Report 24-7889 in detail
    2. Request body camera footage from Aug 4, 2024
    3. Cross-reference witness names in Berkeley PD report
    4. Obtain complete investigation file (Richmond PD Supplemental)
    5. Prepare timeline exhibit for court filing
    6. Share with legal counsel for strategy session

    Priority Documents:
    1. Richmond PD Report 24-7889 (CRITICAL - foundation evidence)
    2. Berkeley PD Follow-up (HIGH - corroboration)
    3. Richmond PD Supplemental (MEDIUM - additional support)

    === RECOMMENDATION ===
    These documents form a strong evidentiary foundation. Recommend:
    - File motion to compel additional records
    - Prepare comprehensive timeline exhibit
    - Schedule expert review of police conduct
    - Consider settlement leverage increased
  ",

  "documents": [
    {
      "type": "PLCR",
      "title": "Richmond PD Report 24-7889",
      "date": "2024-08-04",
      "notes": "Initial police report filed after incident...",
      "relevancy_score": 920
    }
    // ... more documents
  ]
}
```

**How to use the report:**

1. **Read AI Analysis** - Get high-level overview
2. **Check Priority Documents** - Know what to review first
3. **Review Next Steps** - Action items to complete
4. **Examine Contradictions** - Issues to resolve
5. **Update Case Strategy** - Incorporate new evidence

### 9. Analyze Document Relevance

**What it does:** Deep dive analysis of a specific document.

**When to use:**
- After uploading important document
- Before court filing
- For expert review preparation
- When document impact is unclear

**Usage:**

```bash
# CLI
python claude_shepherd_agent.py
> Choice: 8  # Analyze document relevance
> Document ID: a1b2c3d4-5678-90ef-ghij-klmnopqrstuv

# Telegram
/shepherd_analyze_doc a1b2c3d4-5678-90ef-ghij-klmnopqrstuv
```

**Analysis Includes:**

1. **Relevance Assessment**
   - Why is this document important?
   - What makes it valuable evidence?
   - Strengths and weaknesses

2. **Case Integration**
   - How does it fit with existing evidence?
   - What gap does it fill?
   - Which arguments does it support?

3. **Timeline Placement**
   - Where in the case timeline?
   - What events does it document?
   - What came before/after?

4. **Legal Value**
   - Admissibility factors
   - Evidentiary weight
   - Credibility indicators
   - Potential challenges

5. **Action Items**
   - What should be done with this?
   - Who needs to review it?
   - What follow-up is needed?

6. **Related Documents**
   - What other docs to review alongside?
   - What additional evidence to seek?
   - Cross-references identified

7. **Risk Assessment**
   - Any issues with this document?
   - Potential weaknesses?
   - Defense arguments to anticipate?

**Output Example:**

```json
{
  "document_id": "a1b2c3d4-...",
  "document": {
    "type": "PLCR",
    "title": "Richmond PD Report 24-7889",
    "date": "2024-08-04",
    "relevancy_score": 920
  },

  "processing_history": [
    {"stage": "validation", "status": "completed", "duration_ms": 250},
    {"stage": "storage", "status": "completed", "duration_ms": 1850},
    {"stage": "extraction", "status": "completed", "duration_ms": 3200}
  ],

  "analysis": "
    === DOCUMENT RELEVANCE ANALYSIS ===

    Relevance Assessment:
    This is a CRITICAL document - the foundation of the case.

    Why Important:
    - Official police record (high credibility)
    - Contemporaneous documentation (Aug 4, 2024)
    - Establishes facts before any litigation
    - First official acknowledgment of incident

    Strengths:
    - Official government document
    - Created in normal course of business
    - Contains officer observations
    - Includes witness statements
    - Establishes timeline baseline

    Weaknesses:
    - May contain officer bias
    - Limited to officer's perspective
    - Does not include all witness interviews

    Case Integration:
    This document serves as the ANCHOR for the case:
    - All other evidence references this incident
    - Timeline starts here (Aug 4, 2024)
    - Corroborated by Berkeley PD report (Aug 5)
    - Supports constitutional violation claims
    - Establishes jurisdiction and parties

    Timeline Placement:
    DAY 1 - August 4, 2024 (CRITICAL DATE)
    - Incident occurs
    - Richmond PD responds
    - Report filed
    - Investigation initiated

    Legal Value: 9/10

    Admissibility:
    - ✅ Business records exception (hearsay)
    - ✅ Official records privilege
    - ✅ Authenticated by officer signature
    - ✅ Contemporaneous documentation

    Evidentiary Weight:
    - HIGH: Official police documentation
    - CORROBORATED: Berkeley PD confirms
    - CREDIBLE: Professional duty to report accurately

    Potential Challenges:
    - Defense may question officer bias
    - Defense may claim procedural errors
    - May need officer testimony to authenticate

    Action Items:

    IMMEDIATE:
    1. Obtain officer's full personnel file
    2. Request body camera footage
    3. Subpoena dispatch recordings
    4. Interview witnesses listed in report

    SHORT-TERM:
    5. Prepare exhibit for court filing
    6. Create timeline graphic with this as anchor
    7. Cross-reference with Berkeley PD report
    8. Identify all witness names for follow-up

    LONG-TERM:
    9. Depose officer who prepared report
    10. Expert review for procedure compliance
    11. Compare with similar incidents (pattern)

    Related Documents:

    MUST REVIEW TOGETHER:
    - Berkeley PD Follow-up Report (Aug 5, 2024)
      → Corroboration from second jurisdiction

    - Richmond PD Supplemental (Aug 10, 2024)
      → Follow-up investigation findings

    - Dispatch Recordings (Aug 4, 2024)
      → Timeline verification

    SHOULD OBTAIN:
    - Body camera footage (Richmond PD, Aug 4)
    - Witness statements (formal interviews)
    - Prior incident reports (pattern evidence)
    - Officer training records (procedure compliance)

    Risk Assessment:

    RISKS:
    - Officer may claim memory faded (need deposition soon)
    - Body camera footage may be deleted (7-day retention)
    - Witnesses may become unavailable
    - Report may contain factual errors

    MITIGATION:
    - Immediate preservation letter for all evidence
    - Quick witness interviews
    - Expert review to identify any report inconsistencies
    - Cross-reference with all available sources

    === RECOMMENDATION ===

    This is your FOUNDATION document. Treat as CRITICAL EVIDENCE.

    Priority Actions:
    1. Send preservation letter IMMEDIATELY
    2. Depose officer within 30 days
    3. Obtain body camera footage THIS WEEK
    4. Interview all listed witnesses
    5. Prepare court exhibit

    Overall Assessment: STRONG EVIDENCE, HIGH VALUE, IMMEDIATE ACTION REQUIRED
  "
}
```

---

## Usage Examples

### Example 1: Morning Routine

```bash
# Check system health
/shepherd_monitor 24h

# Review new evidence
/shepherd_impact 24h

# Check database
/shepherd_schema

# Output:
# ✅ System healthy (98% success rate)
# ✅ 3 new documents uploaded
# ✅ 1 critical police report requires review
# ✅ Database schema intact
```

### Example 2: Pre-Court Preparation

```bash
# Generate 30-day impact report
/shepherd_impact 30d

# Analyze key document
/shepherd_analyze_doc <document-id>

# Get comprehensive timeline
> Review AI analysis for timeline events
> Export priority documents list
> Share with legal counsel
```

### Example 3: Code Review Workflow

```bash
# Developer creates PR
git push origin feature/video-upload

# Create PR on GitHub
# PR #5 created

# Shepherd review
/shepherd_review_pr 5

# Output:
# ✅ Code quality: Good
# ⚠️ Note: Database migration needed
# ✅ Security: No issues found
# ✅ Recommendation: Approve after CI passes
```

### Example 4: Troubleshooting Upload Failure

```bash
# Monitor recent activity
/shepherd_monitor 1h

# Output shows failed upload
# Failed: 1 upload in last hour

# Get details from processing_logs
SELECT * FROM processing_logs
WHERE status = 'failed'
ORDER BY logged_at DESC
LIMIT 5;

# Analyze the specific document
/shepherd_analyze_doc <failed-doc-id>

# AI identifies issue and suggests fix
```

### Example 5: Weekly Health Check

```bash
# Monday morning routine
/shepherd_monitor 7d
/shepherd_impact 7d
/shepherd_schema

# Review outputs:
# - Upload success rate
# - New evidence summary
# - Database integrity
# - Action items for the week
```

---

## Telegram Commands Reference

### Code & Repository
```
/shepherd_review_pr <number>     Review a pull request
/shepherd_ask <question>         Ask about the codebase
/shepherd_analyze                Analyze repository architecture
```

### Database & Monitoring
```
/shepherd_monitor [period]       Monitor ingestion tables
                                 period: 1h, 24h, 7d, 30d (default: 24h)

/shepherd_impact [period]        Generate case impact report
                                 period: 1h, 24h, 7d, 30d (default: 24h)

/shepherd_analyze_doc <id>       Analyze specific document
                                 id: UUID from telegram_uploads

/shepherd_schema                 Check database schema health
```

### Help
```
/shepherd_help                   Show all commands with examples
```

### Examples
```
/shepherd_monitor 7d
/shepherd_impact 24h
/shepherd_analyze_doc a1b2c3d4-5678-90ef-ghij-klmnopqrstuv
/shepherd_ask How are notifications sent?
/shepherd_review_pr 5
```

---

## CLI Interface Reference

```
🐑 Claude Shepherd Agent
==================================================

CODE & REPOSITORY:
1. Index repository
2. Review PR
3. Answer question
4. Analyze architecture
5. Generate documentation

DATABASE & MONITORING:
6. Monitor ingestion tables
7. Generate case impact report
8. Analyze document relevance
9. Monitor schema changes

0. Exit
```

---

## Python API Reference

### Basic Usage

```python
import asyncio
from claude_shepherd_agent import ClaudeShepherdAgent

async def main():
    agent = ClaudeShepherdAgent()

    # Monitor database
    report = await agent.monitor_ingestion_tables('24h')
    print(f"Health: {report['health_score']}")
    print(f"Uploads: {report['uploads']['total']}")

    # Case impact analysis
    impact = await agent.generate_case_impact_report('7d')
    print(f"New docs: {impact['new_documents_count']}")
    print(f"Analysis: {impact['claude_analysis']}")

    # Document analysis
    doc_analysis = await agent.analyze_document_relevance('doc-uuid')
    print(doc_analysis['analysis'])

asyncio.run(main())
```

### Advanced Usage

```python
from claude_shepherd_agent import (
    ClaudeShepherdAgent,
    RepositoryIndexer
)

async def advanced_workflow():
    agent = ClaudeShepherdAgent()

    # Index repository first
    indexer = RepositoryIndexer()
    await indexer.index_repository()

    # Review all open PRs
    open_prs = [1, 2, 3, 5, 7]
    for pr_num in open_prs:
        review = await agent.review_pr(pr_num)
        if review['recommendation'].startswith('❌'):
            print(f"PR {pr_num} has issues!")

    # Monitor health and alert if degraded
    health = await agent.monitor_ingestion_tables('24h')
    if '🔴 CRITICAL' in health['health_score']:
        # Send alert
        print("ALERT: System health critical!")

    # Generate daily report
    impact = await agent.generate_case_impact_report('24h')
    if impact['new_documents_count'] > 0:
        print(f"New evidence: {impact['new_documents_count']} docs")
        print(impact['claude_analysis'])

asyncio.run(advanced_workflow())
```

---

## Best Practices

### 1. Regular Monitoring

**Daily:**
- Run `/shepherd_monitor 24h`
- Check health score
- Review any failures

**Weekly:**
- Run `/shepherd_impact 7d`
- Generate comprehensive case report
- Review schema health

**Monthly:**
- Run `/shepherd_impact 30d`
- Full repository re-index
- Architecture analysis

### 2. Document Analysis Workflow

1. **Upload document via Telegram**
2. **Wait for processing** (check notifications)
3. **Run impact report** (`/shepherd_impact 1h`)
4. **Analyze critical docs** individually
5. **Review AI recommendations**
6. **Take suggested actions**

### 3. Code Review Workflow

1. **Create PR on GitHub**
2. **Request shepherd review** (`/shepherd_review_pr <number>`)
3. **Address issues** identified by AI
4. **Re-request review** if major changes
5. **Merge** after approval

### 4. Troubleshooting Workflow

1. **Monitor shows degraded health**
2. **Query processing_logs** for errors
3. **Identify failed uploads**
4. **Analyze failed document** (if specific)
5. **Review error message**
6. **Apply fix**
7. **Retry upload**
8. **Confirm success**

---

## Advanced Features

### Custom Knowledge Base

Extend the agent's knowledge:

```python
def _build_knowledge_base(self) -> str:
    kb = f"""# ASEAGI Repository Knowledge Base

    ## Custom Section
    - Case-specific legal precedents
    - Jurisdiction-specific rules
    - Custom document types

    {super()._build_knowledge_base()}
    """
    return kb
```

### Scheduled Reports

Automate daily reports:

```python
import schedule
import time

async def daily_report():
    agent = ClaudeShepherdAgent()
    impact = await agent.generate_case_impact_report('24h')
    # Send via email or Telegram
    print(impact['claude_analysis'])

schedule.every().day.at("09:00").do(lambda: asyncio.run(daily_report()))

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Integration with CI/CD

```yaml
# .github/workflows/pr-review.yml
name: Shepherd PR Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Shepherd Review
        run: |
          python -c "
          import asyncio
          from claude_shepherd_agent import ClaudeShepherdAgent

          async def review():
              agent = ClaudeShepherdAgent()
              review = await agent.review_pr(${{ github.event.pull_request.number }})
              print(review['summary'])

          asyncio.run(review())
          "
```

---

## Troubleshooting

### Issue: "Claude API not configured"

**Solution:**
```bash
export ANTHROPIC_API_KEY='sk-ant-api03-your-key'
```

Verify:
```python
import os
print(os.environ.get('ANTHROPIC_API_KEY'))
```

### Issue: "Supabase connection failed"

**Solution:**
```bash
export SUPABASE_URL='https://your-project.supabase.co'
export SUPABASE_KEY='your-service-role-key'
```

### Issue: "No documents found in time period"

**Possible causes:**
- No uploads in selected time period
- Incorrect time period format
- Database connection issue

**Solution:**
```bash
# Try longer time period
/shepherd_impact 7d

# Check database directly
SELECT COUNT(*) FROM telegram_uploads
WHERE created_at >= NOW() - INTERVAL '24 hours';
```

### Issue: "Qdrant collection not found"

**Solution:**
```bash
# Index repository first
python claude_shepherd_agent.py
> Choice: 1  # Index repository
```

### Issue: "Rate limit exceeded"

**Cause:** Too many Claude API requests

**Solution:**
- Wait a few minutes
- Reduce frequency of requests
- Consider upgrading Claude API tier

---

## Performance Tips

1. **Index incrementally** - Only re-index changed files
2. **Cache reports** - Store recent reports to avoid re-generation
3. **Batch operations** - Process multiple documents together
4. **Use time periods wisely** - Shorter periods = faster responses
5. **Monitor API usage** - Track Claude API costs

---

## Security Reminders

- ✅ Never commit API keys
- ✅ Use environment variables
- ✅ Rotate credentials every 90 days
- ✅ Limit token scopes (GitHub, Supabase)
- ✅ Monitor API usage for anomalies
- ✅ Enable rate limiting in production
- ✅ Use service role keys (not anon keys)

---

## Support

**Documentation:**
- [CLAUDE_SHEPHERD_SETUP.md](CLAUDE_SHEPHERD_SETUP.md) - Setup guide
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - System overview
- [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) - Technical details

**External:**
- Claude API: https://docs.anthropic.com
- Qdrant: https://qdrant.tech/documentation
- Supabase: https://supabase.com/docs

---

**Last Updated:** 2025-11-06
**Version:** 1.0
**Maintained By:** ASEAGI Development Team
