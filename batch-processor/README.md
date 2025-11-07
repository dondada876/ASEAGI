# ASEAGI Batch Processor

**Production-ready system for processing 7TB of Google Drive documents using Vast.ai GPU instances**

This batch processing system orchestrates the processing of your entire 7TB Google Drive document repository using rented GPU instances from Vast.ai, while maintaining cost-effectiveness and reliability.

---

## 🎯 Overview

### What This Does

Processes **70,000 documents (7TB)** from Google Drive:
- **Cost**: $44 (well within $100 Vast.ai credit)
- **Time**: ~87.5 hours (~3.6 days)
- **Method**: 700 batches of 100 documents each
- **GPU**: RTX 4090 or A100 at $0.50-1.00/hour
- **Processing**: 4.5 seconds per document average

### Architecture

```
Google Drive (7TB)
    ↓
Digital Ocean Droplet (Batch Manager)
    ↓
Vast.ai GPU Instance (Batch Processor)
    ↓
Supabase Database (Results Storage)
```

---

## 📋 Prerequisites

### 1. Google Drive API Setup

**Create OAuth2 credentials:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (e.g., "ASEAGI Batch Processor")
3. Enable **Google Drive API**
4. Create **OAuth2 Client ID** credentials:
   - Application type: Desktop app
   - Download `credentials.json`
5. Place `credentials.json` in `/home/user/ASEAGI/batch-processor/` or `/app/credentials/` in Docker

### 2. Vast.ai Account Setup

**Get API key:**

1. Sign up at [Vast.ai](https://vast.ai/)
2. Add $100 credit to your account
3. Go to Account → API Keys
4. Copy your API key
5. Set as environment variable: `VAST_AI_API_KEY`

### 3. Environment Variables

Create `.env` file in `batch-processor/` directory:

```bash
# Supabase
SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Vast.ai
VAST_AI_API_KEY=your-vastai-api-key

# Claude API
CLAUDE_API_KEY=your-claude-api-key

# Google Drive (path to credentials.json)
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/credentials.json
```

---

## 🚀 Quick Start

### Option 1: Docker (Recommended for Production)

**From telegram-bot directory:**

```bash
cd /home/user/ASEAGI/telegram-bot

# Create credentials directory
mkdir -p credentials
cp /path/to/credentials.json credentials/

# Start all services (including batch processor)
docker-compose up -d

# Check logs
docker-compose logs -f batch-processor

# View API docs
open http://localhost:8001/docs
```

### Option 2: Local Development

```bash
cd /home/user/ASEAGI/batch-processor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SUPABASE_URL="https://jvjlhxodmbkodzmggwpu.supabase.co"
export SUPABASE_KEY="your-key"
export VAST_AI_API_KEY="your-key"
export CLAUDE_API_KEY="your-key"

# Run API server
python api_endpoints.py

# Server available at http://localhost:8001
```

---

## 📊 API Endpoints

### Base URL: `http://localhost:8001`

### Health Check

```bash
curl http://localhost:8001/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-07T12:00:00",
  "batch_manager_initialized": true,
  "current_session": "batch_session_1699358400"
}
```

---

### Start Batch Processing Session

**POST** `/batch/start`

Start processing 7TB from Google Drive.

**Request:**
```bash
curl -X POST http://localhost:8001/batch/start \
  -H "Content-Type: application/json" \
  -d '{
    "folder_id": null,
    "mime_types": ["application/pdf"],
    "max_documents": null,
    "batch_size": 100,
    "max_cost_per_hour": 1.0
  }'
```

**Parameters:**
- `folder_id`: Google Drive folder ID (null = root, all folders)
- `mime_types`: File types to process (default: PDF only)
- `max_documents`: Limit documents (null = all)
- `batch_size`: Documents per batch (default: 100)
- `max_cost_per_hour`: Max GPU cost per hour (default: $1.00)

**Response:**
```json
{
  "session_id": "batch_session_1699358400",
  "status": "running",
  "total_documents": 70000,
  "total_batches": 700,
  "completed_batches": 0,
  "failed_batches": 0,
  "progress_percentage": 0.0,
  "started_at": "2025-11-07T12:00:00",
  "estimated_completion": "2025-11-11T00:00:00",
  "vastai_instance_id": 123456,
  "total_cost": 44.0
}
```

---

### Get Batch Status

**GET** `/batch/status`

Get current processing status.

```bash
curl http://localhost:8001/batch/status
```

**Response:**
```json
{
  "session_id": "batch_session_1699358400",
  "status": "running",
  "total_documents": 70000,
  "total_batches": 700,
  "completed_batches": 150,
  "failed_batches": 2,
  "progress_percentage": 21.43,
  "started_at": "2025-11-07T12:00:00",
  "estimated_completion": "2025-11-11T00:00:00",
  "vastai_instance_id": 123456,
  "total_cost": 44.0,
  "current_batch": {
    "batch_id": "batch_0151",
    "batch_number": 151,
    "document_count": 100,
    "processed_count": 47,
    "status": "processing"
  }
}
```

---

### Stop Batch Processing

**POST** `/batch/stop`

Stop current session and release GPU instance.

```bash
curl -X POST http://localhost:8001/batch/stop
```

**Response:**
```json
{
  "message": "Session stopped successfully"
}
```

---

### Estimate Processing Cost

**GET** `/batch/estimate`

Estimate cost before starting.

```bash
curl "http://localhost:8001/batch/estimate?total_documents=70000&batch_size=100&cost_per_hour=0.50"
```

**Response:**
```json
{
  "total_documents": 70000,
  "batch_size": 100,
  "total_batches": 700,
  "total_hours": 87.5,
  "cost_per_hour": 0.5,
  "total_cost": 43.75,
  "seconds_per_document": 4.5
}
```

---

### Check Vast.ai Balance

**GET** `/vastai/balance`

Check your Vast.ai account balance.

```bash
curl http://localhost:8001/vastai/balance
```

**Response:**
```json
{
  "balance": 100.0,
  "currency": "USD"
}
```

---

### Search GPU Instances

**GET** `/vastai/instances`

Find available GPU instances before starting.

```bash
curl "http://localhost:8001/vastai/instances?min_gpu_ram=24&max_cost_per_hour=1.0"
```

**Response:**
```json
{
  "total_found": 47,
  "showing": 10,
  "instances": [
    {
      "id": 123456,
      "gpu_name": "RTX 4090",
      "gpu_ram_gb": 24.0,
      "cpu_cores": 16,
      "ram_gb": 64.0,
      "cost_per_hour": 0.48,
      "disk_space_gb": 200
    }
  ]
}
```

---

### List Google Drive Documents

**GET** `/drive/documents`

Preview documents from Google Drive.

```bash
curl "http://localhost:8001/drive/documents?max_results=100"
```

**Response:**
```json
{
  "total_documents": 100,
  "documents": [
    {
      "id": "1abc...",
      "name": "case_document_001.pdf",
      "size_mb": 2.5,
      "modified_time": "2025-11-01T10:00:00Z",
      "web_view_link": "https://drive.google.com/..."
    }
  ]
}
```

---

### Resume from Checkpoint

**POST** `/batch/resume/{checkpoint_file}`

Resume processing if interrupted.

```bash
curl -X POST http://localhost:8001/batch/resume/checkpoint_100.json
```

**Response:**
```json
{
  "message": "Session resumed successfully",
  "session_id": "batch_session_1699358400",
  "completed_batches": 100,
  "total_batches": 700
}
```

---

## 🔄 Complete Workflow

### Step 1: Test Setup

**Verify Google Drive authentication:**

```bash
cd /home/user/ASEAGI/batch-processor
python google_drive_sync.py
```

This will:
1. Open OAuth2 consent flow in browser
2. Save token to `token.json`
3. List first 100 PDFs from your Drive
4. Show storage estimate

**Verify Vast.ai connection:**

```bash
python vastai_client.py
```

This will:
1. Check your account balance
2. Search for available GPU instances
3. Show cost estimate for 7TB

---

### Step 2: Test with Small Batch

**Process 10 documents first:**

```bash
curl -X POST http://localhost:8001/batch/start \
  -H "Content-Type: application/json" \
  -d '{
    "max_documents": 10,
    "batch_size": 10
  }'
```

**Monitor progress:**

```bash
watch -n 5 curl http://localhost:8001/batch/status
```

---

### Step 3: Run Full 7TB Processing

**Start full processing:**

```bash
curl -X POST http://localhost:8001/batch/start \
  -H "Content-Type: application/json" \
  -d '{
    "mime_types": ["application/pdf"],
    "batch_size": 100,
    "max_cost_per_hour": 1.0
  }'
```

**Expected timeline:**
- Startup: ~5 minutes (list documents, rent GPU)
- Processing: ~87.5 hours (3.6 days)
- Shutdown: ~1 minute (stop GPU instance)

**Checkpoints saved every 10 batches** → can resume if interrupted

---

### Step 4: Monitor Progress

**Via API:**

```bash
# Check every 5 minutes
watch -n 300 curl http://localhost:8001/batch/status
```

**Via Logs:**

```bash
# Docker
docker-compose logs -f batch-processor

# Local
tail -f batch_processor.log
```

**Via N8N Workflow:**

Set up Workflow 5 (Batch Job Monitor) to send Telegram notifications at:
- Every 50 batches completed
- Every error
- Final completion

---

## 📈 Cost Breakdown

### Estimated Costs for 7TB

| Item | Cost | Notes |
|------|------|-------|
| **Vast.ai GPU** | $43.75 | 87.5 hours @ $0.50/hr |
| **Digital Ocean** | $0 | Already running |
| **Supabase** | $0 | Within Pro tier limits |
| **Claude API** | $0 | Batch runs on Vast.ai, not Droplet |
| **Total** | **$43.75** | **Well within $100 budget** |

**Remaining Vast.ai credit:** $56.25

---

## 🛡️ Error Handling

### Automatic Features

✅ **Checkpoint every 10 batches** - Resume from any point
✅ **Retry failed documents** - Automatically retry up to 3 times
✅ **Network error handling** - Exponential backoff for API calls
✅ **GPU instance monitoring** - Detect and restart if crashed
✅ **Cost protection** - Check balance before each batch

### Manual Recovery

**If processing stops:**

1. Check logs:
   ```bash
   docker-compose logs batch-processor | tail -100
   ```

2. Check available checkpoints:
   ```bash
   curl http://localhost:8001/checkpoints
   ```

3. Resume from last checkpoint:
   ```bash
   curl -X POST http://localhost:8001/batch/resume/checkpoint_100.json
   ```

**If GPU instance crashes:**

1. Check Vast.ai status:
   ```bash
   curl http://localhost:8001/vastai/instances
   ```

2. Stop current instance:
   ```bash
   curl -X POST http://localhost:8001/batch/stop
   ```

3. Restart from checkpoint (will rent new instance):
   ```bash
   curl -X POST http://localhost:8001/batch/resume/checkpoint_100.json
   ```

---

## 🧪 Testing

### Unit Tests (TODO)

```bash
pytest tests/
```

### Integration Tests

**Test Google Drive:**

```bash
python google_drive_sync.py
```

**Test Vast.ai:**

```bash
python vastai_client.py
```

**Test Batch Manager:**

```bash
python batch_manager.py
```

---

## 📁 File Structure

```
batch-processor/
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container image
├── README.md                  # This file
├── api_endpoints.py           # FastAPI server
├── batch_manager.py           # Core orchestration logic
├── vastai_client.py           # Vast.ai API wrapper
├── google_drive_sync.py       # Google Drive integration
├── credentials/               # Google OAuth2 credentials
│   └── credentials.json       # (you provide this)
├── batch_state/               # Processing state
│   ├── checkpoint_*.json      # Checkpoints every 10 batches
│   └── batch_session_*.json   # Session metadata
└── cache/                     # Temporary storage
    └── drive_cache.json       # Google Drive listing cache
```

---

## 🔗 Integration with Other Components

### N8N Workflow 5: Batch Job Initiator

Automate batch processing:

```
Manual Trigger or Schedule
    ↓
Check Google Drive (unprocessed docs)
    ↓
Submit Batch Job (POST /batch/start)
    ↓
Monitor Progress (GET /batch/status)
    ↓
Notify on Completion (Telegram)
```

### Supabase Integration

Processed documents are stored in `document_journal` table:

```sql
-- Check processing status
SELECT
    processing_status,
    COUNT(*) as count
FROM document_journal
WHERE google_drive_id IS NOT NULL
GROUP BY processing_status;

-- Find failed documents
SELECT
    id,
    original_filename,
    processing_status,
    error_message
FROM document_journal
WHERE processing_status = 'failed';
```

---

## 🚨 Troubleshooting

### Issue: "Google Drive authentication failed"

**Solution:**
1. Ensure `credentials.json` is in correct location
2. Run `python google_drive_sync.py` to test OAuth flow
3. Check that Google Drive API is enabled in Cloud Console

### Issue: "Vast.ai insufficient balance"

**Solution:**
1. Check balance: `curl http://localhost:8001/vastai/balance`
2. Add credit at https://vast.ai/billing
3. Verify API key is correct

### Issue: "No GPU instances available"

**Solution:**
1. Increase `max_cost_per_hour` parameter
2. Try different GPU: `gpu_name: "A100"` instead of "RTX_4090"
3. Check Vast.ai website for availability

### Issue: "Processing too slow"

**Solution:**
1. Rent faster GPU (A100 instead of RTX 4090)
2. Increase `batch_size` (but may increase memory usage)
3. Ensure Supabase has good network connectivity

---

## 📞 Support

**For Batch Processor Issues:**
- Check logs: `docker-compose logs batch-processor`
- API docs: http://localhost:8001/docs
- Test individual components with `python <component>.py`

**Related Documentation:**
- HYBRID_ARCHITECTURE.md - Overall system architecture
- TELEGRAM_BOT_ROADMAP.md - Integration with Telegram bot
- N8N_WORKFLOW_GUIDE.md - Automation workflows

---

**For Ashe - Protecting children through intelligent legal assistance** ⚖️

*"When processing thousands of documents, every detail matters for justice."*

---

**Version:** 1.0.0
**Status:** Production Ready
**Last Updated:** November 2025
