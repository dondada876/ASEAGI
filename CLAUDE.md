# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

ASEAGI is an enterprise-grade legal intelligence platform for case analysis. It processes 745+ legal documents for the case "In re Ashe B., J24-00478" with multi-dimensional scoring (micro, macro, legal, category, relevancy 0-1000). The system integrates Telegram bots, Streamlit dashboards, bulk document processing, and hybrid cloud deployment (DigitalOcean + Vast.ai GPU).

**Supabase Database:** 39 tables across 11 schemas, 52 analytical views modeling court cases, violations, documents, events, and communications.

---

## Essential Commands

### Running Dashboards

```bash
# Master legal case dashboard (port 8501)
streamlit run proj344_master_dashboard.py

# Legal intelligence with document scoring
streamlit run legal_intelligence_dashboard.py

# CEO holistic dashboard (port 8503)
streamlit run ceo_global_dashboard.py --server.port=8503

# Bulk ingestion progress monitor
streamlit run bulk_ingestion_dashboard.py

# Court events timeline
streamlit run court_events_dashboard.py
```

### Document Processing

```bash
# Bulk ingestion of 10,000+ documents
python bulk_document_ingestion.py

# With specific options
python bulk_document_ingestion.py --input-dir /path/to/docs --max-files 100 --workers 8

# Convert RTF documents to markdown
python convert_rtf_to_markdown.py

# Upload processed documents to Supabase
python document_repository_to_supabase.py

# Check recent Telegram uploads
python check_telegram_uploads.py
```

### Telegram Bots

```bash
# Orchestrator bot (RECOMMENDED: 90-95% accuracy, human-in-loop)
python telegram_bot_orchestrator.py

# Enhanced bot (fast: 70-80% accuracy, auto-analysis)
python telegram_document_bot_enhanced.py

# Original bot (manual: 100% accuracy, 7-step form)
python start_telegram_bot.py
```

### Production Deployment

```bash
# Navigate to deployment directory
cd aseagi-droplet

# Deploy with Docker Compose
docker compose up -d

# View logs
docker compose logs -f api
docker compose logs -f dashboard

# Restart services
docker compose restart

# Check Vast.ai GPU instances
vastai show instances
```

---

## Architecture Overview

### Data Flow

```
INPUT (Telegram/Web/Bulk)
  ↓
DEDUPLICATION (MD5 hash)
  ↓
OCR LAYER (Tesseract → Claude Vision fallback)
  ↓
AI ANALYSIS (Claude: micro/macro/legal/category/relevancy scores)
  ↓
STORAGE (S3 Spaces + Supabase metadata)
  ↓
INDEXING (Full-text + vector embeddings)
  ↓
DASHBOARDS (Visualization & search)
```

### Hybrid Cloud Architecture (Production)

- **DigitalOcean Droplet** ($24/mo): Always-on control plane, Flask API, Streamlit dashboards, Redis job queue
- **DO Spaces S3** ($5/mo): Cold storage for raw/processed documents
- **Vast.ai GPU** ($32/mo avg): On-demand RTX 3080 for OCR/AI processing, auto-launches when jobs queued, auto-destroys when idle
- **Supabase** ($25/mo): PostgreSQL with 39 tables, 52 views, RLS security

**Cost Savings:** $86/mo vs $800/mo traditional GPU droplet (90% reduction)

### Configuration Priority Hierarchy

The `config_loader.py` module implements universal secret management:

1. Streamlit secrets.toml (dashboard context)
2. Specified .env file
3. Local .env in current directory
4. Shared ~/.proj344_secrets/.env
5. System environment variables

**Critical:** Never commit secrets. Use `.env.example` as template.

### Document Scoring System

All documents in `legal_documents` table have five scoring dimensions:

- **Relevancy (0-1000)**: Overall case importance (900+ = critical smoking guns)
- **Micro Score**: Page-level fraud/perjury detection
- **Macro Score**: Document-level significance
- **Legal Score**: Statutory/case law relevance
- **Category Score**: Content classification accuracy

Query critical documents: `relevancy_number >= 900` or use view `critical_documents`.

---

## Key Components

### Telegram Bot Selection

Three bots available (see `BOT_COMPARISON.md` for decision tree):

1. **telegram_bot_orchestrator.py** (RECOMMENDED)
   - Intelligent with human-in-loop
   - Asks clarifying questions when uncertain
   - Preview before database commit
   - Edit capability
   - 90-95% accuracy, 30-60 sec/upload

2. **telegram_document_bot_enhanced.py**
   - Fast auto-analysis with Tesseract + Claude
   - No preview or editing
   - 70-80% accuracy, 20 sec/upload

3. **telegram_document_bot.py**
   - Complete manual control (7-step form)
   - 100% accuracy, 2-3 min/upload
   - Metadata only (no image storage)

**Bot States:** Use ConversationHandler pattern. State persisted to Supabase during multi-step flows.

### Bulk Processing Pipeline

`bulk_document_ingestion.py` (800+ lines):

- **Progress Tracking**: SQLite database (`bulk_ingestion_progress.db`) for resume capability
- **Tiered OCR**: Tesseract (fast, $0.001/doc) → Claude Vision (fallback, $0.01-0.02/doc)
- **Parallel Processing**: ThreadPoolExecutor with configurable workers (8-32)
- **Cost Monitoring**: Tracks API spend per document
- **Formats**: JPG, PNG, HEIC, PDF, TXT, RTF, DOCX
- **Capacity**: 10,000+ documents, ~1000 docs in 2-4 hours

**Resume After Interruption:**
```python
# Checks file_hash against database
# Skips already processed files
# Continues from last checkpoint
```

### Dashboard Caching Strategy

All dashboards use Streamlit caching:

```python
@st.cache_resource  # For expensive connections (Supabase client)
def init_supabase_client():
    return create_client(url, key)

@st.cache_data(ttl=60)  # For data queries (1 minute TTL)
def get_documents():
    return supabase.table('legal_documents').select('*').execute()
```

**Performance:** Master dashboard queries 39 tables with 60-second cache. Clear cache with `st.cache_data.clear()`.

### Supabase Integration Patterns

**Common Query Patterns:**

```python
# Critical documents (relevancy >= 900)
supabase.table('critical_documents').select('*').execute()

# Recent uploads (last 24 hours)
supabase.table('legal_documents')\
    .select('*')\
    .gte('created_at', yesterday)\
    .order('created_at', desc=True)\
    .execute()

# Documents by type
supabase.table('legal_documents')\
    .select('*')\
    .eq('document_type', 'PLCR')\
    .execute()

# Aggregate statistics
supabase.table('legal_documents')\
    .select('*', count='exact')\
    .execute()
```

**Document Types:** PLCR (police report), DECL (declaration), EVID (evidence), CPSR (CPS report), MCOD (medical), DVRO (restraining order), MOTN (motion), ORDR (order)

---

## Database Schema (Critical Tables)

### Core Document Tables

- **legal_documents**: Main documents with all 5 scores, OCR text, metadata
- **document_pages**: Page-level analysis for multi-page docs
- **form_fields_extracted**: Extracted field data (checkbox analysis)

### Case Management

- **court_case_tracker**: Multi-jurisdiction case tracking
- **case_timeline**: Chronological view of all events
- **parties_registry**: All individuals involved (mother, father, agencies, lawyers)

### Violations & Evidence

- **legal_violations**: 300+ violations categorized by severity (0-100)
- **violation_evidence_map**: Links documents to violations
- **violation_patterns**: Temporal and contextual pattern detection

### Events & Communications

- **court_events**: Hearings, motions, deadlines (with upcoming_events view)
- **event_documents**: Document-to-event relationships
- **communications_matrix**: All logged communications
- **police_cad_incidents**: Police response tracking

### High-Value Views

- **critical_documents**: Relevancy >= 900 (smoking guns)
- **critical_violations**: Severity >= 80
- **documents_by_fraud_score**: Ordered by micro score
- **complete_case_timeline**: Full chronological view
- **upcoming_deadlines**: Next 30 days

---

## Development Patterns

### Error Handling in Processing Pipeline

```python
try:
    # Primary path (fast)
    result = tesseract_ocr(file_path)
except Exception as e:
    logger.warning(f"Tesseract failed: {e}, falling back to Claude")
    # Fallback path (reliable)
    result = claude_vision_ocr(file_path)
```

### Progress Tracking Pattern

```python
# Before processing batch
tracker = ProgressTracker("bulk_ingestion_progress.db")
tracker.init_batch("batch_name", source_dir, total_files)

# During processing
for file in files:
    if tracker.is_processed(file_hash):
        continue  # Skip duplicates

    result = process_file(file)
    tracker.record_file(batch_id, file, result)

# Query progress
stats = tracker.get_batch_stats(batch_id)
# Returns: {processed, skipped, errors, total_cost}
```

### Telegram Conversation State

```python
# Define states
DOCUMENT_TYPE, DATE, TITLE, NOTES = range(4)

# Conversation handler
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        DOCUMENT_TYPE: [MessageHandler(filters.TEXT, handle_type)],
        DATE: [MessageHandler(filters.TEXT, handle_date)],
        # ... more states
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

# Store context between states
context.user_data['document_info'] = {...}
```

---

## Production Deployment Notes

### Vast.ai GPU Worker Pattern

Docker container runs stateless worker:

1. Fetch jobs from Supabase (`status='queued'`)
2. Download document from S3
3. Process with GPU (OCR + Claude)
4. Upload results to S3
5. Update Supabase (`status='completed'`)
6. Auto-shutdown after 5 min idle

**Key:** No local storage. All state in Supabase, all files in S3.

### Environment Variables (Production)

Required for `aseagi-droplet/docker-compose.yml`:

```env
# Supabase
SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
SUPABASE_KEY=<anon-key>

# APIs
ANTHROPIC_API_KEY=<claude-key>
TELEGRAM_BOT_TOKEN=<bot-token>

# Storage (DO Spaces - S3 compatible)
S3_ENDPOINT=https://nyc3.digitaloceanspaces.com
S3_ACCESS_KEY=<spaces-key>
S3_SECRET_KEY=<spaces-secret>
S3_BUCKET=aseagi-documents

# Vast.ai
VASTAI_API_KEY=<vastai-key>
```

### Docker Compose Services

- **api**: Flask control plane (port 5000) - Vast.ai orchestration
- **dashboard**: Streamlit monitor (port 8501) - Job/cost tracking
- **redis**: Job queue (port 6379) - In-memory state
- **nginx**: Reverse proxy (port 80/443) - SSL termination
- **certbot**: SSL renewal - Let's Encrypt automation

### Cost Tracking

Monitor monthly spend across:
- Vast.ai GPU hours × $0.40/hr
- Claude API calls × $0.01-0.02/doc
- DO Spaces storage × $0.023/GB
- Fixed: Droplet ($24) + Spaces ($5) + Supabase ($25)

Dashboard shows real-time cost accumulation and monthly projections.

---

## Testing Strategy

### Local Testing (Before Production)

```bash
# Test with small batch
python bulk_document_ingestion.py --input-dir ./test_docs --max-files 10

# Verify Supabase connection
python -c "from config_loader import load_config; print(load_config())"

# Test Telegram bot (development mode - polling)
python telegram_bot_orchestrator.py  # Ctrl+C to stop

# Verify dashboard loads
streamlit run proj344_master_dashboard.py  # Should open browser
```

### Production Smoke Test

```bash
# After deployment to droplet
curl https://your-droplet-ip:8501  # Dashboard accessible
docker compose ps  # All services running
docker compose logs api | grep ERROR  # No errors
vastai show instances  # Can communicate with Vast.ai
```

---

## Common Tasks

### Add New Document Type

1. Update Supabase enum: `ALTER TYPE document_type ADD VALUE 'NEWTYPE'`
2. Add to bot keyboards in `telegram_bot_orchestrator.py`
3. Update documentation strings

### Query Critical Documents

```python
critical = supabase.table('critical_documents').select('*').execute()
# Or direct filter
high_relevancy = supabase.table('legal_documents')\
    .select('*')\
    .gte('relevancy_number', 900)\
    .execute()
```

### Resume Interrupted Batch

```bash
# Progress database tracks state
python bulk_document_ingestion.py --input-dir /same/dir
# Automatically skips already-processed files via hash check
```

### Deploy Configuration Changes

```bash
cd aseagi-droplet
nano .env  # Update config
docker compose down
docker compose up -d  # Recreates containers with new env
```

### Monitor Vast.ai Instance

```bash
# List running instances
vastai show instances

# View logs
vastai logs INSTANCE_ID

# Manual destroy (if auto-shutdown fails)
vastai destroy instance INSTANCE_ID
```

---

## Important File Locations

### Configuration
- `.streamlit/secrets.toml` - Dashboard secrets (encrypted by Streamlit)
- `.env` - Production environment variables (not in git)
- `config_loader.py` - Universal secret management

### Core Processing
- `bulk_document_ingestion.py` - Main batch processor
- `document_extractor.py` - RTF/DOC/PDF text extraction
- `document_repository_to_supabase.py` - Upload to database

### Dashboards
- `proj344_master_dashboard.py` - Legal case overview
- `legal_intelligence_dashboard.py` - Document scoring
- `court_events_dashboard.py` - Timeline visualization
- `ceo_global_dashboard.py` - Holistic life management

### Telegram Bots
- `telegram_bot_orchestrator.py` - Intelligent with Q&A (RECOMMENDED)
- `telegram_document_bot_enhanced.py` - Fast auto-analysis
- `telegram_document_bot.py` - Manual control

### Deployment
- `aseagi-droplet/docker-compose.yml` - Multi-container orchestration
- `aseagi-droplet/requirements.txt` - Lightweight dependencies (no GPU)
- `DEPLOYMENT_ARCHITECTURE_ANALYSIS.md` - Full deployment strategy

### Documentation
- `BOT_COMPARISON.md` - Bot selection guide
- `BULK_INGESTION_GUIDE.md` - Processing documentation
- `VASTAI_HYBRID_ARCHITECTURE.md` - Production architecture
- `CONFIG_MANAGEMENT_GUIDE.md` - Secret management

---

## Architectural Decisions

### Why Hybrid Cloud (DigitalOcean + Vast.ai)?

- **Problem**: Single GPU droplet costs $800/mo, mostly idle
- **Solution**: Separate compute (elastic) from storage (persistent)
- **Result**: $86/mo vs $800/mo (90% savings), scales to 10,000+ docs

### Why Three Telegram Bots?

- **Orchestrator**: Production use (accuracy > speed)
- **Enhanced**: Rapid bulk uploads (speed > accuracy)
- **Original**: Full manual control (legal compliance scenarios)

Decision tree in `BOT_COMPARISON.md` helps choose based on use case.

### Why Tiered OCR?

- **Tesseract**: Fast (2-5 sec), free, 90% accuracy for clean scans
- **Claude Vision**: Slower (5-10 sec), $0.01/doc, 98% accuracy, handles poor quality
- **Strategy**: Try Tesseract first, fallback to Claude on failure

Reduces cost while maintaining high accuracy.

### Why SQLite Progress Tracking?

- Lightweight, no server required
- Resume capability critical for 10,000+ doc batches
- Independent of Supabase (network resilience)
- Fast local queries for monitoring

### Why Supabase Over Self-Hosted PostgreSQL?

- Managed service (no maintenance)
- Built-in RLS (row-level security)
- Real-time subscriptions for dashboards
- pgvector for semantic search
- API and client libraries

---

## Performance Considerations

### Dashboard Load Times

- **Master dashboard**: ~2-3 seconds (39 table queries, cached 60s)
- **Intelligence dashboard**: ~1-2 seconds (fewer queries)
- **Bulk ingestion monitor**: <1 second (SQLite local reads)

**Optimization**: Use `@st.cache_data(ttl=60)` for expensive Supabase queries. Increase TTL for stable data (case timeline), decrease for real-time data (processing status).

### Processing Throughput

- **Tesseract**: ~120-300 docs/hour (parallel)
- **Claude Vision**: ~60-120 docs/hour (API rate limits)
- **Mixed**: ~100 docs/hour typical
- **Bottleneck**: Usually Claude API, not GPU

Scale workers based on API quota and cost tolerance.

### Database Query Performance

- **Indexed fields**: `relevancy_number`, `document_type`, `created_at`, `case_number`
- **Full-text search**: Built-in PostgreSQL FTS on `ocr_text` column
- **Vector search**: pgvector extension for semantic search
- **Views**: Pre-computed aggregations (52 views) for common queries

Use views for complex analytics to avoid repeated joins.

---

## Troubleshooting

### "Supabase connection failed"

Check config priority: secrets.toml → .env → environment. Verify URL format: `https://PROJECT_ID.supabase.co`

### "Telegram bot not responding"

1. Check token: `python test_telegram_connection.py`
2. Verify webhook vs polling mode (production uses webhook)
3. Check for multiple running instances (conflict error)
4. Use `start_telegram_bot.py` to auto-kill old instances

### "Vast.ai instance won't launch"

1. Verify API key: `vastai account`
2. Check available offers: `vastai search offers "gpu_name=RTX 3080"`
3. Ensure Docker image exists on Docker Hub
4. Check environment variables in launch command

### "Dashboard shows no data"

1. Verify Supabase connection in browser console
2. Check table exists: Query in Supabase dashboard
3. Clear Streamlit cache: `st.cache_data.clear()`
4. Verify RLS policies allow read access

### "Bulk ingestion stuck"

1. Check progress: `SELECT * FROM file_processing WHERE status='processing'`
2. View SQLite: `sqlite3 bulk_ingestion_progress.db "SELECT * FROM batches"`
3. Check API quotas (Claude, OpenAI)
4. Review logs for errors
5. Resume: Re-run same command (auto-skips completed)

---

## Security Notes

### Secret Management

- **NEVER** commit `.env` or `secrets.toml` to git
- Use `.env.example` as template
- Rotate API keys quarterly
- Use separate keys for dev/prod

### Supabase RLS

All tables have row-level security enabled. Anon key has limited access. Service key (admin) only for backend processing.

### S3 Access

- Bucket not public
- Use signed URLs (temporary access)
- Keys in environment only
- Files auto-deleted from Vast.ai after upload

### Telegram Security

- Bot token never exposed in logs (masked by config_loader)
- Webhook uses HTTPS only
- User whitelist in production (by Telegram user ID)

---

## Project History Context

This is a legal case management system built for analyzing custody case documents. The system evolved from manual document review to AI-powered batch processing with multi-dimensional scoring. Current focus: Processing 10,000+ historical documents and deploying cost-optimized production infrastructure.

**Key Milestone**: Transitioning from development (Windows) to production (Mac Mini → DigitalOcean hybrid cloud) with 90% cost reduction through architectural optimization.
