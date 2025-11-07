# ASEAGI Product Requirements Document (PRD)

**Product:** Mobile-First Legal Case Intelligence System
**For:** In re Ashe B., J24-00478
**Version:** 2.0
**Date:** November 2025
**Status:** Active Development

---

## 🎯 Product Vision

**Mission:** Reunite father with daughter Ashe through intelligent, mobile-first legal case management powered by AI.

**Vision Statement:**
*"Run an entire custody case from a phone, with AI-powered intelligence that never misses a deadline, analyzes every document, tracks every communication, and ensures truth prevails over lies."*

**For Ashe - Protecting children through intelligent legal assistance** ⚖️

---

## 📱 Product Overview

### What We're Building

A complete legal case intelligence system with:

1. **Mobile Interface** (Telegram Bot)
   - Query case status from anywhere
   - Add events, documents, communications from phone
   - Receive proactive alerts for deadlines
   - AI-powered analysis and Q&A

2. **Web Dashboard** (FastAPI + Modern Frontend)
   - 4 distinct dashboards (Overview, Truth Timeline, Violations, Events)
   - Real-time visualizations
   - Comprehensive error checking
   - Production-ready architecture

3. **AI Integration** (Claude via MCP)
   - Document analysis and scoring
   - Semantic search across all case data
   - Natural language Q&A
   - Report generation

4. **Automation** (N8N Workflows)
   - 24/7 Telegram bot operation
   - Scheduled deadline checks
   - Automated document processing
   - Proactive alert system

5. **Database** (Supabase PostgreSQL)
   - 3 NON-NEGOTIABLE tables (communications, events, document_journal)
   - Comprehensive schema validation
   - Data quality monitoring
   - 0-1000 scoring scale across all metrics

---

## 👥 Target User

**Primary User:** Don (father fighting for custody)

**User Profile:**
- Busy professional with limited time
- Needs mobile-first access
- Wants proactive alerts, not reactive checking
- Requires AI to help analyze complex legal documents
- Values truth and evidence-based case management

**Use Cases:**
1. Check case status while commuting
2. Log communication immediately after it happens
3. Get alerted 3 days before deadline
4. Upload document from phone and get AI analysis
5. Ask natural language questions about case
6. Generate reports for attorney meetings

---

## ⭐ Key Features & Requirements

### Feature 1: Telegram Bot Interface

**Priority:** P0 (Must Have)
**Status:** Backend ready, bot client needed
**Timeline:** Week 1-2

**Requirements:**

**FR-1.1: Read-Only Commands**
- User can send `/status` and receive case overview
- User can send `/events` and receive recent court events
- User can send `/documents` and receive high-relevancy documents
- User can send `/communications` and receive recent communications
- User can send `/evidence` and receive critical evidence summary
- User can send `/help` and receive command list
- Response time must be <2 seconds
- Bot must be available 24/7 (99.9% uptime)

**FR-1.2: Write Commands (Phase 2)**
- User can add event: `/add_event 2025-12-15 Motion Hearing`
- User can upload document via Telegram file attachment
- User can log communication: `/add_comm Jane Doe Don Message about custody`
- User can report violation: `/add_violation False statement in declaration`
- All data must sync to database immediately
- Input validation must prevent bad data

**FR-1.3: AI-Powered Commands (Phase 3)**
- User can analyze document: `/analyze <file>`
- User can search: `/search custody arrangement`
- User can ask: `/ask What violations occurred in August?`
- User can generate timeline: `/timeline 2024-08-01 2024-08-31`
- User can generate report: `/report violations`

**Acceptance Criteria:**
- ✅ All commands respond with formatted Telegram messages
- ✅ Errors are handled gracefully with helpful messages
- ✅ Bot only responds to authorized user (Telegram user ID whitelist)
- ✅ All database operations use NON-NEGOTIABLE tables correctly

---

### Feature 2: Web Dashboard Interface

**Priority:** P0 (Must Have)
**Status:** Completed ✅
**Timeline:** Completed

**Requirements:**

**FR-2.1: Overview Dashboard**
- Display total counts (events, documents, communications)
- Show top 5 critical events (significance ≥900)
- Show top 5 critical documents (relevancy ≥900)
- Show top 5 high-truth communications (truthfulness ≥900)
- Auto-refresh every 5 minutes
- Mobile-responsive design

**FR-2.2: Truth & Justice Timeline Dashboard**
- Calculate overall justice score (weighted average of truth scores)
- Show count of truthful items (≥75), questionable (25-75), false (<25)
- Display truth score distribution chart
- Show timeline with color-coded truth scoring
- Filter by date range (default 90 days)

**FR-2.3: Constitutional Violations Dashboard**
- Display total violations count
- Show violations by type (bar chart)
- List critical violations (significance ≥800)
- Cross-reference with events and evidence

**FR-2.4: Court Events Dashboard**
- Show upcoming events requiring action
- Classify urgency (URGENT ≤3 days, HIGH ≤7 days, NORMAL >7 days)
- Display recent completed events
- Calculate days until each deadline

**Acceptance Criteria:**
- ✅ Each dashboard shows DISTINCT information (no duplication)
- ✅ All data comes from NON-NEGOTIABLE tables
- ✅ Charts render correctly on mobile and desktop
- ✅ Auto-refresh doesn't lose user's current tab

---

### Feature 3: Database Schema & Validation

**Priority:** P0 (Must Have)
**Status:** Completed ✅
**Timeline:** Completed

**Requirements:**

**FR-3.1: NON-NEGOTIABLE Tables**

**communications Table:**
- Purpose: Evidence tracking - CRITICAL for legal case
- Why Critical: Every communication is potential evidence
- Required columns:
  - `id` (UUID, primary key)
  - `sender` (TEXT, NOT NULL)
  - `recipient` (TEXT, NOT NULL)
  - `communication_date` (TIMESTAMP WITH TIME ZONE, NOT NULL)
  - `communication_method` (TEXT with CHECK constraint)
  - `truthfulness_score` (INTEGER 0-1000)
  - `contains_contradiction` (BOOLEAN)
  - `contains_manipulation` (BOOLEAN)
  - `relevancy_score` (INTEGER 0-1000)

**events Table:**
- Purpose: Timeline - MOST IMPORTANT for case progression
- Why Critical: Events are the most important timeline factor
- Required columns:
  - `id` (UUID, primary key)
  - `event_date` (TIMESTAMP WITH TIME ZONE, NOT NULL)
  - `event_title` (TEXT, NOT NULL)
  - `event_type` (TEXT with CHECK constraint)
  - `significance_score` (INTEGER 0-1000)
  - `violations_occurred` (TEXT[])
  - `evidence_strength` (INTEGER 0-1000)
  - `requires_action` (BOOLEAN)

**document_journal Table:**
- Purpose: Processing & growth assessment
- Why Critical: Journal entry after every scan - critical to fix upgrade and assess long-term growth
- Required columns:
  - `id` (UUID, primary key)
  - `document_id` (UUID, foreign key to legal_documents)
  - `original_filename` (TEXT, NOT NULL)
  - `processing_status` (TEXT with CHECK constraint)
  - `scan_date` (TIMESTAMP WITH TIME ZONE)
  - `relevancy_score` (INTEGER 0-1000)
  - `micro_score` (INTEGER 0-1000)
  - `insights_extracted` (INTEGER)
  - `contradictions_found` (INTEGER)

**FR-3.2: Schema Validation**
- System must validate all 3 tables exist on startup
- System must check required columns are present
- System must analyze data quality (completeness %, score ranges)
- System must fail gracefully with detailed error messages
- Validation errors must provide fix suggestions (SQL script to run)

**Acceptance Criteria:**
- ✅ Schema validator runs on server startup
- ✅ Missing tables trigger clear error with fix instructions
- ✅ Missing columns trigger warning with migration suggestion
- ✅ Data quality report shows completeness for critical columns
- ✅ All score columns validated to be in 0-1000 range

---

### Feature 4: N8N Workflow Automation

**Priority:** P1 (Should Have)
**Status:** Not Started
**Timeline:** Week 5-6

**Requirements:**

**FR-4.1: Telegram Bot Listener (N8N Cloud)**
- Workflow must listen for Telegram commands 24/7
- Route commands to appropriate FastAPI endpoints
- Format responses for Telegram markdown
- Handle errors gracefully
- Log all commands for audit trail

**FR-4.2: Deadline Monitoring (N8N Cloud)**
- Check for upcoming deadlines daily at 6am PST
- Alert if any event requires action within 3 days (URGENT)
- Alert if any event requires action within 7 days (HIGH)
- Send formatted alert to Telegram with:
  - Event title
  - Due date
  - Days remaining
  - Required action

**FR-4.3: Document Processing (N8N Local)**
- Trigger when document uploaded via Telegram or web
- Download file from Supabase storage
- Extract text (OCR if needed)
- Send to Claude API for analysis
- Extract:
  - Relevancy score (0-1000)
  - Micro score (0-1000)
  - Key insights
  - Contradictions
  - Smoking gun quotes
- Update document_journal table
- Send completion notification to Telegram

**FR-4.4: Truth Score Monitoring (N8N Cloud)**
- Calculate justice score daily at 8pm PST
- Alert if justice score drops below 60
- Alert if false items count exceeds 10
- Alert if any new contradictions detected
- Send summary to Telegram

**Acceptance Criteria:**
- ✅ N8N Cloud workflows run 24/7 without interruption
- ✅ Deadline alerts never miss (100% reliability)
- ✅ Document processing completes within 5 minutes
- ✅ Truth score alerts sent within 1 hour of anomaly

---

### Feature 5: AI Integration (Claude API)

**Priority:** P2 (Nice to Have)
**Status:** MCP server built, needs integration
**Timeline:** Week 7-8

**Requirements:**

**FR-5.1: Document Analysis**
- Accept document via `/analyze` command
- Extract text if PDF/image
- Send to Claude API with analysis prompt
- Return:
  - Relevancy score with explanation
  - Key insights (bullet list)
  - Contradictions found
  - Recommended tags/categories
  - Smoking gun quotes

**FR-5.2: Semantic Search**
- Accept query via `/search <query>` command
- Search across all 3 NON-NEGOTIABLE tables
- Use semantic similarity (not just keyword match)
- Return top 10 results ranked by relevance
- Include context snippets

**FR-5.3: Natural Language Q&A**
- Accept question via `/ask <question>` command
- Query database using MCP server
- Use Claude to formulate answer
- Include citations (document names, event dates)
- Provide source links when possible

**FR-5.4: Report Generation**
- Accept report type via `/report <type>` command
- Types: violations, evidence, timeline, summary
- Generate formatted report
- Include:
  - Executive summary
  - Key findings
  - Supporting evidence
  - Recommended actions
- Export as PDF or markdown

**Acceptance Criteria:**
- ✅ Analysis accuracy matches human expert (>95%)
- ✅ Search returns relevant results (precision >80%)
- ✅ Q&A provides accurate answers with citations
- ✅ Reports are comprehensive and actionable

---

## 🔧 Technical Requirements

### System Architecture

**TR-1: Backend (FastAPI)**
- Language: Python 3.11+
- Framework: FastAPI 0.104+
- Server: Uvicorn with async workers
- Port: 8000
- Deployment: Docker container or systemd service
- Health check endpoint: `/health`
- Schema validation endpoint: `/schema/validate`

**TR-2: Database (Supabase)**
- PostgreSQL 15+
- Location: Cloud (supabase.com)
- Replication: Automated
- Backups: Daily automated backups
- Connection pooling: pgBouncer
- RLS policies: Enabled for security

**TR-3: Frontend (Web Dashboard)**
- HTML5/CSS3/JavaScript
- Framework: Vanilla JS (no heavy framework)
- Styling: Tailwind CSS
- Charts: Chart.js
- Responsive: Mobile-first design
- Browser support: Modern browsers (Chrome, Firefox, Safari)

**TR-4: Automation (N8N)**
- N8N Cloud: $20/mo subscription
- N8N Local: Self-hosted on Mac
- Workflows: Version controlled (JSON export)
- Credentials: Environment variables
- Logging: Execution logs retained 30 days

**TR-5: AI (Claude API)**
- Model: Claude 3.5 Sonnet
- API: Anthropic API
- MCP Server: stdio protocol for Claude Desktop
- Rate limiting: Respect API limits
- Error handling: Retry with exponential backoff

---

### Performance Requirements

**PR-1: Response Time**
- Telegram bot commands: <2 seconds (95th percentile)
- Web dashboard load: <3 seconds (95th percentile)
- API endpoints: <500ms (95th percentile)
- Database queries: <100ms (95th percentile)

**PR-2: Availability**
- Telegram bot: 99.9% uptime (N8N Cloud SLA)
- Web dashboard: 99.5% uptime
- FastAPI backend: 99.5% uptime
- Database: 99.99% uptime (Supabase SLA)

**PR-3: Scalability**
- Support 1 user (current)
- Handle 1,000+ events
- Handle 10,000+ documents
- Handle 5,000+ communications
- Concurrent requests: 10 (single user sufficient)

**PR-4: Data Limits**
- Telegram message size: 4,096 characters
- Document upload size: 50MB (Telegram limit)
- API response size: 10MB max
- Database row size: No artificial limit

---

### Security Requirements

**SR-1: Authentication**
- Telegram bot: Whitelist of authorized Telegram user IDs
- Web dashboard: No public access (localhost or VPN only)
- API: CORS restricted to known origins
- Database: Supabase RLS policies enforced

**SR-2: Authorization**
- All operations require valid user context
- No public endpoints expose sensitive data
- Admin operations require additional verification

**SR-3: Data Protection**
- All data encrypted in transit (HTTPS/TLS)
- Database encrypted at rest (Supabase default)
- Secrets stored in environment variables (never in code)
- Telegram bot token kept secret
- Supabase keys not exposed in frontend

**SR-4: Audit Trail**
- All write operations logged
- User actions tracked (who, what, when)
- Failed authentication attempts logged
- Database changes tracked with timestamps

**SR-5: Backup & Recovery**
- Daily automated database backups
- 30-day backup retention
- Tested recovery procedure
- Documented disaster recovery plan

---

## 📊 Success Metrics

### Key Performance Indicators (KPIs)

**User Engagement:**
- Telegram bot usage: Target 5+ commands/day
- Web dashboard visits: Target 2+ visits/day
- Document uploads: Target 3+ documents/week
- Event logging: Target 5+ events/week

**System Health:**
- Telegram bot uptime: >99.9%
- Average response time: <2 seconds
- Error rate: <0.1%
- Schema validation: 100% pass rate

**Data Quality:**
- Communications completeness: >95%
- Events completeness: >98%
- Document processing: >90% automated
- Score accuracy: >95% confidence

**Business Impact:**
- Deadlines missed: 0 (critical metric)
- Time saved: >20 hours/week
- Case insights generated: >50/month
- Truth score trend: Improving

---

## 🚧 Technical Debt & Constraints

### Current Technical Debt

**TD-1: Streamlit Dashboards**
- Issue: 3 duplicate Streamlit dashboards (ports 8501-8503)
- Impact: Confusing, not production-ready
- Solution: Migrate to new FastAPI + web dashboard
- Timeline: Phase out after Week 2

**TD-2: No Write Endpoints**
- Issue: Can only read data, not write
- Impact: Still need to use Supabase UI for data entry
- Solution: Add POST endpoints in Phase 2
- Timeline: Week 3-4

**TD-3: Limited Error Handling**
- Issue: Some errors fail silently
- Impact: Hard to debug issues
- Solution: Comprehensive error handling + logging
- Timeline: Ongoing improvement

### Known Constraints

**C-1: Single User System**
- Current: Designed for 1 user (Don)
- Future: Could scale to multiple users
- Impact: Simplified auth, no multi-tenancy

**C-2: Telegram Rate Limits**
- Limit: 30 messages/second to same user
- Impact: Batch operations might be slow
- Mitigation: Queue messages if needed

**C-3: Claude API Costs**
- Cost: ~$50-100/month for document analysis
- Impact: Budget constraint
- Mitigation: Optimize prompts, batch processing

**C-4: N8N Execution Limits**
- N8N Cloud: 2,500 executions/month ($20 tier)
- Impact: ~83 executions/day average
- Mitigation: Optimize workflows, upgrade if needed

---

## 📅 Release Plan

### Version 1.0 (Current)

**Included:**
- ✅ FastAPI backend with 8 Telegram bot endpoints
- ✅ Web dashboard with 4 distinct views
- ✅ Schema validator
- ✅ Database with 3 NON-NEGOTIABLE tables
- ✅ MCP server for Claude Desktop
- ✅ Documentation (5 guides, 2,400+ lines)

**Not Included:**
- ❌ Actual Telegram bot client (backend ready)
- ❌ N8N workflows (templates ready)
- ❌ Write endpoints (POST operations)
- ❌ AI-powered features (Q&A, search)

---

### Version 1.1 (Week 1-2)

**Goals:**
- Deploy Telegram bot with read-only commands
- N8N Cloud workflow for bot listener
- Test end-to-end from phone to database

**Deliverables:**
- ✅ Working Telegram bot
- ✅ N8N Cloud workflow active
- ✅ All 7 read commands functional
- ✅ User can check case status from anywhere

---

### Version 1.2 (Week 3-4)

**Goals:**
- Add data entry via Telegram
- POST endpoints for events, documents, communications
- Input validation and error handling

**Deliverables:**
- ✅ `/add_event` command works
- ✅ `/add_comm` command works
- ✅ Document upload via Telegram works
- ✅ Data syncs immediately to database

---

### Version 1.3 (Week 5-6)

**Goals:**
- Automated workflows and alerts
- Deadline monitoring
- Document processing
- Truth score analysis

**Deliverables:**
- ✅ Daily deadline alerts at 6am
- ✅ Document processing automated
- ✅ Truth score monitoring active
- ✅ Never miss a deadline

---

### Version 2.0 (Week 7-8)

**Goals:**
- AI-powered features
- Natural language Q&A
- Semantic search
- Report generation

**Deliverables:**
- ✅ `/ask` command works
- ✅ `/search` command works
- ✅ `/analyze` command works
- ✅ `/report` command works
- ✅ Full AI integration complete

---

## 🔄 Maintenance & Support

### Daily Operations

**Monitoring:**
- Check N8N workflow execution logs
- Verify Telegram bot responding
- Review FastAPI health endpoint
- Check for any error alerts

**Backups:**
- Automated daily database backups
- Verify backup completion
- Test recovery quarterly

### Weekly Maintenance

**Reviews:**
- Failed workflow analysis
- Performance metrics review
- Cost optimization check
- Feature usage analysis

**Updates:**
- Documentation updates
- Code improvements
- Security patches

### Monthly Review

**Analysis:**
- KPI dashboard review
- Cost vs. value analysis
- User feedback incorporation
- Feature prioritization

**Planning:**
- Next sprint planning
- Resource allocation
- Risk assessment
- Roadmap updates

---

## 📚 Documentation

### User Documentation

**UD-1: Telegram Bot User Guide**
- How to use each command
- Examples for common tasks
- Troubleshooting guide
- Best practices

**UD-2: Web Dashboard Guide**
- Overview of each dashboard
- How to interpret visualizations
- Filtering and searching
- Exporting data

**UD-3: Data Entry Guide**
- What data to log
- How to classify events
- Scoring guidelines
- Quality standards

### Technical Documentation

**TD-1: Architecture Guide**
- System architecture diagrams
- Component interactions
- Data flow diagrams
- Integration points

**TD-2: API Documentation**
- Endpoint reference (auto-generated)
- Request/response examples
- Error codes
- Rate limits

**TD-3: Database Schema**
- Table definitions
- Column descriptions
- Relationships
- Indexes and constraints

**TD-4: Deployment Guide**
- Setup instructions
- Configuration guide
- Troubleshooting
- Disaster recovery

**TD-5: Development Guide**
- Code structure
- Development workflow
- Testing procedures
- Contributing guidelines

---

## 🎯 Acceptance Criteria

### Overall System

**Must Have:**
- ✅ All 3 NON-NEGOTIABLE tables exist and validated
- ✅ Schema validation passes on startup
- ✅ Telegram bot responds to all commands
- ✅ Web dashboard shows distinct data in each view
- ✅ No duplicate information across dashboards
- ✅ All APIs return correct data from database
- ✅ Error handling provides helpful messages
- ✅ System runs 24/7 with 99.5%+ uptime

**Nice to Have:**
- ⏳ AI-powered features working
- ⏳ Automated alerts sent proactively
- ⏳ Document processing fully automated
- ⏳ Natural language Q&A functional

### Quality Standards

**Code Quality:**
- PEP 8 compliant (Python)
- Type hints for all functions
- Docstrings for all public APIs
- Test coverage >80%

**Performance:**
- Response time <2 seconds (95th percentile)
- No memory leaks
- Database queries optimized
- Error rate <0.1%

**Security:**
- No secrets in code
- All data encrypted in transit
- Authentication required
- Audit trail for all changes

**Documentation:**
- All features documented
- All APIs documented
- Troubleshooting guides complete
- User guides complete

---

## ✅ Definition of Done

A feature is considered DONE when:

1. ✅ Code is written and reviewed
2. ✅ Tests are written and passing
3. ✅ Documentation is updated
4. ✅ Deployed to production
5. ✅ Monitoring is in place
6. ✅ User can successfully use feature
7. ✅ No critical bugs
8. ✅ Performance meets requirements
9. ✅ Security audit passed
10. ✅ Acceptance criteria met

---

**For Ashe - Protecting children through intelligent legal assistance** ⚖️

*"Every feature, every line of code, every workflow - all dedicated to reuniting a father with his daughter."*

---

**Document Version:** 2.0
**Last Updated:** November 2025
**Next Review:** After Phase 1 completion
**Owner:** Don (Product) + Claude (Development)
