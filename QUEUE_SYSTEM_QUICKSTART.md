# ASEAGI Queue Management System - Quick Start Guide

**Created:** 2025-11-06
**For:** In re Ashe B., J24-00478
**Purpose:** Universal document journal and processing queue management

---

## 📋 Overview

The Queue Management System provides:

1. **Universal Journal** - Truth table tracking every document that enters the system
2. **Assessment Phase** - Smart evaluation before expensive processing
3. **Processing Queue** - Prioritized queue for approved documents
4. **Metrics Logging** - Detailed tracking of every processing step
5. **Document Type Rules** - Different processing logic per document type

### Key Benefits

- ✅ **No duplicates processed twice** - 3-tier deduplication catches renamed/rescanned files
- ✅ **Complete audit trail** - Track every document from submission to completion
- ✅ **Cost optimization** - Skip duplicates early, saving 90% on processing costs
- ✅ **Performance tracking** - AI confidence scores, OCR quality, processing time
- ✅ **Reprocessing support** - Mark documents for deeper analysis later

---

## 🚀 Quick Start

### Step 1: Deploy Schema to Supabase

```bash
# Run deployment script
./deploy_queue_schema.sh
```

Follow the manual deployment instructions to run the SQL in Supabase Dashboard.

**What gets created:**
- `document_journal` - Universal truth table
- `processing_queue` - Active processing queue
- `processing_metrics_log` - Detailed step-by-step logs
- `document_type_rules` - Rules per document type
- 5+ views for common queries
- Helper functions

### Step 2: Verify Schema Deployment

In Supabase SQL Editor:

```sql
-- Check tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('document_journal', 'processing_queue', 'processing_metrics_log', 'document_type_rules');

-- Should return 4 rows

-- Check views
SELECT table_name
FROM information_schema.views
WHERE table_schema = 'public'
  AND table_name LIKE '%queue%';

-- Should return several rows (queue_dashboard, processing_performance, etc.)

-- Check document type rules
SELECT document_type, default_priority
FROM document_type_rules;

-- Should show business_card, legal_document, court_filing, etc.
```

### Step 3: Start the API Server

```bash
# Set environment variables
export SUPABASE_URL="https://jvjlhxodmbkodzmggwpu.supabase.co"
export SUPABASE_KEY="your-supabase-anon-key"
export OPENAI_API_KEY="sk-proj-your-key"

# Start FastAPI server
python3 mobile_scanner_api.py
```

The API will start on `http://localhost:8000`

### Step 4: Open Queue Dashboard

In a separate terminal:

```bash
# Start Streamlit dashboard
streamlit run dashboard_queue_monitor.py
```

The dashboard will open at `http://localhost:8501`

### Step 5: Test Document Upload

```bash
# Upload a test document
curl -X POST http://localhost:8000/api/upload \
  -F "file=@test_document.pdf" \
  -F "source=test" \
  -F "source_device=laptop"
```

**Expected response:**

```json
{
  "journal_id": 1,
  "should_process": true,
  "reason": "Assessment passed, ready for processing",
  "document_type": "legal_document",
  "priority": 9,
  "status": "queued",
  "message": "✅ Added to processing queue (priority 9)"
}
```

### Step 6: Upload Same Document Again (Test Duplicate Detection)

```bash
# Upload the same document
curl -X POST http://localhost:8000/api/upload \
  -F "file=@test_document.pdf" \
  -F "source=test"
```

**Expected response:**

```json
{
  "journal_id": 2,
  "should_process": false,
  "reason": "Already in system (status: queued)",
  "is_duplicate": true,
  "duplicate_of": 1,
  "status": "duplicate",
  "message": "⚠️ Duplicate detected: Already in system (status: queued)"
}
```

### Step 7: Check Queue Stats

```bash
# Get queue statistics
curl http://localhost:8000/api/queue/stats
```

**Expected response:**

```json
{
  "queue_stats": {
    "queued": 1,
    "skipped_duplicate": 1
  },
  "processing_performance": [],
  "timestamp": "2025-11-06T10:30:00"
}
```

---

## 📊 Understanding the Workflow

### Document Submission Flow

```
1. Upload Document
   ↓
2. Add to document_journal (universal truth table)
   ↓
3. ASSESSMENT PHASE
   ├─ Detect document type (business_card, legal_document, etc.)
   ├─ Run 3-tier deduplication
   │  ├─ Tier 0: Filename similarity (fast)
   │  ├─ Tier 1: OCR content matching (moderate)
   │  └─ Tier 2: AI semantic embeddings (slow but accurate)
   ├─ Apply document type rules
   └─ Calculate priority
   ↓
4. DECISION
   ├─ If duplicate → Mark as skipped_duplicate
   ├─ If manual review required → Mark for review
   └─ If approved → Add to processing_queue
   ↓
5. Processing (by GPU worker or local processor)
   ↓
6. Update journal with results
```

### Document Statuses

| Status | Meaning | Next Step |
|--------|---------|-----------|
| `pending` | Just logged, awaiting assessment | Auto-assessed immediately |
| `assessing` | Running assessment phase | Will transition to queued or skipped |
| `queued` | Approved, ready for processing | Worker will pick up |
| `processing` | Currently being processed | Will transition to completed/failed |
| `completed` | Successfully processed | Archived |
| `failed` | Processing error | Review and retry |
| `skipped_duplicate` | Duplicate detected | No further action |
| `skipped_manual_review` | Requires human review | Manual intervention needed |

### Document Types and Priorities

| Document Type | Priority | Rules |
|--------------|----------|-------|
| `court_filing` | 10 | Full AI analysis, high priority |
| `legal_document` | 9 | Full AI analysis |
| `form` | 7 | OCR + structured extraction |
| `receipt` | 5 | OCR only, basic extraction |
| `business_card` | 3 | Quick contact extraction |
| `photo` | 2 | Image analysis only |
| `sign` | 2 | OCR for text content |
| `unknown` | 5 | Standard processing |

---

## 🔍 Monitoring and Debugging

### View Queue Dashboard

The Streamlit dashboard (`dashboard_queue_monitor.py`) shows:

- **Queue Status Distribution** - Pie chart of document statuses
- **Document Type Distribution** - Bar chart of types
- **Duplicate Detection Stats** - Performance by tier
- **Processing Performance** - AI confidence, costs per type
- **Recent Documents Table** - Filterable list
- **Queue Activity Timeline** - Submissions over time

### Query the Journal Directly

```sql
-- View all documents
SELECT
  journal_id,
  original_filename,
  document_type,
  queue_status,
  is_duplicate,
  date_logged
FROM document_journal
ORDER BY date_logged DESC
LIMIT 20;

-- View queue dashboard
SELECT * FROM queue_dashboard;

-- View duplicates
SELECT
  journal_id,
  original_filename,
  duplicate_detection_tier,
  duplicate_similarity_score,
  duplicate_of_journal_id
FROM document_journal
WHERE is_duplicate = TRUE;

-- View processing performance
SELECT * FROM processing_performance;

-- View detailed metrics for a specific document
SELECT
  log_id,
  processing_step,
  step_duration_seconds,
  step_status,
  metrics
FROM processing_metrics_log
WHERE journal_id = 1
ORDER BY step_started_at;
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/upload` | POST | Upload document |
| `/api/queue/stats` | GET | Queue statistics |
| `/api/queue/items` | GET | List journal items |
| `/api/queue/dashboard` | GET | Dashboard view |
| `/docs` | GET | API documentation |

### Check Logs

```bash
# API server logs (shows assessment phase details)
# Look for lines like:
# "DOCUMENT SUBMISSION"
# "ASSESSMENT PHASE"
# "Tier 0: Filename check..."
# "Tier 1: OCR check..."
# "Tier 2: Semantic check..."
# "✅ Added to processing queue"

# Streamlit dashboard logs
streamlit run dashboard_queue_monitor.py --logger.level=debug
```

---

## 🎯 Common Use Cases

### Use Case 1: Mobile Document Scanning at Courthouse

```bash
# On phone, open: http://[your-server-ip]:8000
# Take photo of document
# Upload via web interface

# Backend automatically:
# 1. Adds to journal
# 2. Detects it's a "court_filing"
# 3. Sets priority = 10
# 4. Checks for duplicates
# 5. Queues for processing
```

### Use Case 2: Batch Upload from Google Drive

```bash
# Upload multiple documents
for file in /path/to/google-drive/*.pdf; do
  curl -X POST http://localhost:8000/api/upload \
    -F "file=@$file" \
    -F "source=google_drive" \
    -F "source_device=mac_mini"
  sleep 1  # Rate limiting
done

# System automatically:
# - Deduplicates across all sources
# - Detects types
# - Queues unique documents
# - Skips duplicates
```

### Use Case 3: Reprocess Low-Confidence Documents

```sql
-- Find documents with low AI confidence
SELECT
  journal_id,
  original_filename,
  ai_confidence_score,
  document_type
FROM document_journal
WHERE ai_confidence_score < 70
  AND queue_status = 'completed';

-- Mark for reprocessing
UPDATE document_journal
SET
  reprocessing_requested = TRUE,
  reprocessing_reason = 'Low AI confidence score',
  reprocessing_tier = 'tier2_semantic',
  queue_status = 'pending'
WHERE ai_confidence_score < 70
  AND queue_status = 'completed';
```

### Use Case 4: Monitor Processing Costs

```sql
-- Total costs by document type
SELECT
  document_type,
  COUNT(*) as documents,
  SUM(ai_cost_usd) as total_ai_cost,
  AVG(ai_cost_usd) as avg_ai_cost,
  SUM(total_cost_usd) as total_cost
FROM document_journal
WHERE queue_status = 'completed'
GROUP BY document_type
ORDER BY total_cost DESC;

-- Daily cost tracking
SELECT
  DATE(date_processing_completed) as date,
  COUNT(*) as documents_processed,
  SUM(total_cost_usd) as total_cost
FROM document_journal
WHERE queue_status = 'completed'
GROUP BY DATE(date_processing_completed)
ORDER BY date DESC;
```

---

## ⚙️ Configuration

### Document Type Rules

Customize processing rules in the `document_type_rules` table:

```sql
-- Add custom rule for medical records
INSERT INTO document_type_rules (
  document_type,
  requires_ocr,
  requires_ai_analysis,
  requires_human_review,
  min_ocr_confidence,
  processing_rules,
  compliance_requirements,
  default_priority
) VALUES (
  'medical_record',
  true,
  true,
  true,  -- Requires human review for HIPAA compliance
  85.0,
  '{"extract_phi": true, "redact_sensitive": true}',
  ARRAY['HIPAA', 'PHI_PROTECTION'],
  8
);

-- Update existing rule
UPDATE document_type_rules
SET default_priority = 10
WHERE document_type = 'court_filing';
```

### Environment Variables

```bash
# .env file
SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
SUPABASE_KEY=your-anon-key
OPENAI_API_KEY=sk-proj-your-key
ANTHROPIC_API_KEY=sk-ant-your-key  # Optional

# Redis (for distributed queue)
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your-redis-password

# Neo4j (for graph relationships)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password
```

---

## 🐛 Troubleshooting

### Issue: "Queue Manager not configured"

**Cause:** Missing environment variables

**Fix:**
```bash
# Check environment
echo $SUPABASE_URL
echo $SUPABASE_KEY

# Set if missing
export SUPABASE_URL="https://jvjlhxodmbkodzmggwpu.supabase.co"
export SUPABASE_KEY="your-key"
```

### Issue: Tables not found

**Cause:** Schema not deployed

**Fix:**
1. Run `./deploy_queue_schema.sh`
2. Follow manual deployment instructions
3. Verify with:
   ```sql
   SELECT * FROM document_journal LIMIT 1;
   ```

### Issue: Duplicates not detected

**Cause:** Deduplication tier not working

**Debug:**
```python
# Test deduplication directly
from queue_manager import QueueManager
from queue_manager import DocumentSubmission

qm = QueueManager(
    supabase_url="...",
    supabase_key="...",
    openai_key="..."
)

submission = DocumentSubmission(
    file_path="/path/to/test.pdf",
    original_filename="test.pdf",
    source_type="test"
)

result = qm.submit_document(submission)
print(f"Is duplicate: {result.is_duplicate}")
print(f"Tier: {result.duplicate_tier}")
```

### Issue: Documents stuck in "assessing" status

**Cause:** Assessment phase crashed

**Fix:**
1. Check API logs for errors
2. Verify OpenAI API key is valid (for Tier 2)
3. Manually update status:
   ```sql
   UPDATE document_journal
   SET queue_status = 'pending'
   WHERE queue_status = 'assessing';
   ```

---

## 📈 Performance Optimization

### Database Indexes

The schema includes indexes on:
- `file_hash` (unique, for fast duplicate lookups)
- `queue_status` (for queue queries)
- `document_type` (for type-based filtering)
- `date_logged` (for timeline queries)

### Caching

For high-volume scenarios, consider caching:

```python
# Cache recent documents in Redis
import redis
r = redis.Redis(host='localhost', port=6379)

# Cache queue stats (TTL 30s)
stats = queue_manager.get_queue_stats()
r.setex('queue_stats', 30, json.dumps(stats))
```

### Batch Processing

For large uploads, use batch mode:

```python
from queue_manager import QueueManager, DocumentSubmission
import os

qm = QueueManager(...)

documents = []
for filename in os.listdir('/path/to/batch'):
    documents.append(DocumentSubmission(
        file_path=f'/path/to/batch/{filename}',
        original_filename=filename,
        source_type='batch_upload'
    ))

results = []
for doc in documents:
    result = qm.submit_document(doc)
    results.append(result)

print(f"Processed: {len([r for r in results if r.should_process])}")
print(f"Duplicates: {len([r for r in results if r.is_duplicate])}")
```

---

## 🚀 Production Deployment

### Docker Deployment

The queue system is integrated into the Docker stack:

```bash
# Deploy full stack (includes queue system)
docker-compose -f docker-compose.full.yml up -d

# Check queue manager status
curl http://localhost:8000/health

# Should show:
# {
#   "status": "healthy",
#   "queue_manager": "ready",
#   ...
# }
```

### Monitoring

Set up alerts for:

```sql
-- Alert if queue is backing up
SELECT COUNT(*) FROM document_journal
WHERE queue_status = 'queued'
  AND date_logged < NOW() - INTERVAL '1 hour';

-- Alert if many failures
SELECT COUNT(*) FROM document_journal
WHERE queue_status = 'failed'
  AND date_processing_completed > NOW() - INTERVAL '1 day';

-- Alert if duplicate rate is too high
SELECT
  COUNT(*) FILTER (WHERE is_duplicate = TRUE)::float / COUNT(*) as dup_rate
FROM document_journal
WHERE date_logged > NOW() - INTERVAL '1 day';
```

---

## 📚 Additional Resources

### Files

- `queue_manager.py` - Queue management service (queue_manager.py:54)
- `mobile_scanner_api.py` - FastAPI backend with queue integration (mobile_scanner_api.py:106)
- `dashboard_queue_monitor.py` - Streamlit queue dashboard
- `document_journal_queue_schema.sql` - Database schema
- `deploy_queue_schema.sh` - Deployment script

### Related Documentation

- `TIERED_DEDUPLICATION_MOBILE_SCANNER.md` - Deduplication architecture
- `DIGITAL_OCEAN_VASTAI_DEPLOYMENT.md` - Production deployment
- `INTEGRATED_ARCHITECTURE_TELEGRAM_QDRANT_NEO4J_N8N.md` - Complete system architecture

### Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API logs
3. Query the journal directly
4. Test components individually

---

**For Ashe. For Justice. For All Children. 🛡️**
