# ASEAGI Multi-Tiered Global Hybrid Architecture

**Optimized for: Batch Processing (7TB) + Real-Time Courtroom Scanning**

**For Ashe - Enterprise-Grade Legal Intelligence with Optimal Resource Utilization** ⚖️

---

## 🏗️ Infrastructure Inventory

### Cloud Resources

| Resource | Specs | Use Case | Status |
|----------|-------|----------|--------|
| **Digital Ocean Droplet** | Docker-enabled | Production API + Web | ✅ Active |
| **Vast.ai GPU Instance** | $100 credit, GPU | Batch AI processing | 🎯 Ready |
| **N8N Cloud** | $20/mo, 2,500 exec | Telegram bot + orchestration | ⏳ Deploy |
| **Supabase** | PostgreSQL + Storage | Database + file storage | ✅ Active |
| **Google Drive** | 7TB documents | Source for batch processing | ✅ Active |

### On-Premise Resources

| Resource | Specs | Use Case | Status |
|----------|-------|----------|--------|
| **Mac Mini** | Always-on | Development + courtroom real-time | ✅ Active |
| **Surface Pro** | Windows workstation | Mobile courtroom processing | ✅ Active |
| **ML350 G6 Server** | Future NVIDIA GPU | On-premise GPU processing | 🔮 Future |

---

## 🎯 Two Critical Use Cases

### Use Case 1: Bulk Batch Processing (7TB Google Drive)

**Scenario:** Process 7TB of historical legal documents in batches

**Requirements:**
- Process 7TB efficiently (estimated 70,000+ documents)
- GPU-accelerated AI analysis
- Cost-effective (use Vast.ai credit)
- Parallel processing
- Progress tracking
- Error handling & retry

**Pipeline:**
```
Google Drive (7TB)
    ↓
Digital Ocean Droplet (Orchestrator)
    ↓
Vast.ai GPU Instance (Batch Processor)
    ↓
Supabase Database (Store results)
```

**Estimated Volume:**
- 7TB / 100KB avg = ~70,000 documents
- Vast.ai GPU: ~50-100 docs/hour
- Total time: ~700-1400 hours (with parallelization: 70-140 hours)
- Cost: $100 credit + minimal Droplet cost

---

### Use Case 2: Real-Time Courtroom Scanning

**Scenario:** Scan document in courtroom, process immediately, add to database

**Requirements:**
- Fast processing (<5 minutes)
- Mobile-friendly (Surface Pro or phone)
- Offline capability
- Immediate feedback
- High accuracy
- Secure transmission

**Pipeline:**
```
Surface Pro (Scan) or Telegram (Upload)
    ↓
Mac Mini (Local processing) OR Digital Ocean (Cloud processing)
    ↓
Claude API (AI analysis)
    ↓
Supabase Database (Immediate storage)
    ↓
Telegram Notification (Confirmation)
```

**Estimated Volume:**
- 1-5 documents per court session
- 1-2 court sessions per week
- ~5-10 documents per week
- Processing: <5 minutes per document

---

## 🏛️ Complete Multi-Tiered Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION TIER                               │
│                     (User-Facing Interfaces)                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │
│  │  Telegram    │  │   Web        │  │  Surface Pro │                │
│  │  Mobile Bot  │  │  Dashboard   │  │  Courtroom   │                │
│  │  (Phone)     │  │  (Browser)   │  │  Scanner     │                │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                │
│         │                  │                  │                         │
└─────────┼──────────────────┼──────────────────┼─────────────────────────┘
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼─────────────────────────┐
│                      ORCHESTRATION TIER                                 │
│                 (Workflow Management & Routing)                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                     N8N CLOUD (Always On)                        │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │ │
│  │  │ Telegram Bot   │  │ Batch Job      │  │ Deadline       │    │ │
│  │  │ Listener       │  │ Orchestrator   │  │ Monitor        │    │ │
│  │  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘    │ │
│  └───────────┼──────────────────┼──────────────────┼─────────────┘ │
│              │                  │                  │                 │
└──────────────┼──────────────────┼──────────────────┼─────────────────┘
               │                  │                  │
┌──────────────▼──────────────────▼──────────────────▼─────────────────────┐
│                      APPLICATION TIER                                   │
│                 (Business Logic & APIs)                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │         DIGITAL OCEAN DROPLET (Production)                      │  │
│  │                                                                  │  │
│  │  ┌────────────────────────────────────────────────────────────┐ │  │
│  │  │  Docker Container: FastAPI Server (Port 8000)              │ │  │
│  │  │  • Telegram Bot API (/telegram/*)                          │ │  │
│  │  │  • Web Dashboard API (/api/dashboard/*)                    │ │  │
│  │  │  • Batch Processing API (/batch/*)                         │ │  │
│  │  │  • Schema Validation                                       │ │  │
│  │  │  • Health Checks                                           │ │  │
│  │  └────────────────────────────────────────────────────────────┘ │  │
│  │                                                                  │  │
│  │  ┌────────────────────────────────────────────────────────────┐ │  │
│  │  │  Docker Container: Nginx Reverse Proxy (Ports 80/443)     │ │  │
│  │  │  • SSL/TLS termination                                    │ │  │
│  │  │  • Static file serving                                    │ │  │
│  │  │  • Load balancing (future)                                │ │  │
│  │  └────────────────────────────────────────────────────────────┘ │  │
│  │                                                                  │  │
│  │  ┌────────────────────────────────────────────────────────────┐ │  │
│  │  │  Docker Container: Batch Job Manager                      │ │  │
│  │  │  • Google Drive sync                                      │ │  │
│  │  │  • Vast.ai job submission                                 │ │  │
│  │  │  • Progress tracking                                      │ │  │
│  │  │  • Result collection                                      │ │  │
│  │  └────────────────────────────────────────────────────────────┘ │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │         MAC MINI (Local Development + Real-Time Processing)     │  │
│  │                                                                  │  │
│  │  • N8N Local (document processing workflows)                   │  │
│  │  • Development environment                                      │  │
│  │  • Real-time courtroom document processing                      │  │
│  │  • MCP Server for Claude Desktop                                │  │
│  │  • Backup processing (if Droplet down)                          │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
               │                  │                  │
┌──────────────▼──────────────────▼──────────────────▼─────────────────────┐
│                      PROCESSING TIER                                    │
│                 (AI & Heavy Computation)                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │              VAST.AI GPU INSTANCE (Batch Processing)            │  │
│  │                                                                  │  │
│  │  ┌────────────────────────────────────────────────────────────┐ │  │
│  │  │  Docker Container: Batch Document Processor                │ │  │
│  │  │  • Pull documents from queue (Redis/RabbitMQ)              │ │  │
│  │  │  • GPU-accelerated OCR (Tesseract GPU)                     │ │  │
│  │  │  • GPU-accelerated embeddings                              │ │  │
│  │  │  • Parallel Claude API calls                               │ │  │
│  │  │  • Batch size: 100 documents at a time                     │ │  │
│  │  │  • Auto-scaling based on queue depth                       │ │  │
│  │  └────────────────────────────────────────────────────────────┘ │  │
│  │                                                                  │  │
│  │  Specs: RTX 4090 or A100 (24GB VRAM)                            │  │
│  │  Cost: ~$0.50-1.00/hour with $100 credit = 100-200 hours        │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │         FUTURE: ML350 G6 SERVER (On-Premise GPU)                │  │
│  │                                                                  │  │
│  │  • NVIDIA GPU (TBD - RTX 4090 or similar)                       │  │
│  │  • Replaces Vast.ai for batch processing                        │  │
│  │  • Zero ongoing costs after hardware purchase                   │  │
│  │  • Faster local processing                                      │  │
│  │  • Privacy-first (all data on-premise)                          │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
               │                  │
┌──────────────▼──────────────────▼─────────────────────────────────────────┐
│                      DATA TIER                                          │
│                 (Storage & Database)                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                    SUPABASE CLOUD                                │  │
│  │                                                                  │  │
│  │  ┌────────────────────────────────────────────────────────────┐ │  │
│  │  │  PostgreSQL Database                                       │ │  │
│  │  │  • events (timeline)                                       │ │  │
│  │  │  • communications (evidence)                               │ │  │
│  │  │  • document_journal (processing log)                       │ │  │
│  │  │  • legal_documents (metadata)                              │ │  │
│  │  │  • batch_jobs (processing queue)                           │ │  │
│  │  └────────────────────────────────────────────────────────────┘ │  │
│  │                                                                  │  │
│  │  ┌────────────────────────────────────────────────────────────┐ │  │
│  │  │  Supabase Storage                                          │ │  │
│  │  │  • Original documents (PDF, images)                        │ │  │
│  │  │  • Processed files (text, embeddings)                      │ │  │
│  │  │  • Bucket: legal-documents/                                │ │  │
│  │  │  • Bucket: batch-processing/                               │ │  │
│  │  └────────────────────────────────────────────────────────────┘ │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                    GOOGLE DRIVE (7TB)                            │  │
│  │                                                                  │  │
│  │  • Source repository for batch processing                       │  │
│  │  • Organized folder structure                                   │  │
│  │  • Read-only access for processing                              │  │
│  │  • Backup storage for processed documents                       │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │         DIGITAL OCEAN SPACES (Optional Cache)                    │  │
│  │                                                                  │  │
│  │  • Temporary storage for batch jobs                             │  │
│  │  • Faster access than Google Drive                              │  │
│  │  • Cost: $5/mo for 250GB                                        │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Use Case 1: Batch Processing (7TB Google Drive)

### Architecture Flow

```
┌──────────────────┐
│  Manual Trigger  │ (Start batch job via web dashboard or Telegram)
│  or Scheduled    │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  N8N Cloud: Batch Job Orchestrator Workflow                │
│  • Checks Google Drive for unprocessed documents           │
│  • Creates batch jobs (100 docs per batch)                 │
│  • Calls Digital Ocean API to start processing             │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Digital Ocean Droplet: Batch Job Manager                  │
│  • Receives batch job request                              │
│  • Pulls document list from Google Drive API               │
│  • Chunks into processing batches (100 docs)               │
│  • Uploads batch to Supabase Storage                       │
│  • Submits job to Vast.ai via API                          │
│  • Tracks job status                                       │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Vast.ai GPU Instance: Batch Processor                     │
│  • Pulls batch from Supabase Storage (100 docs)            │
│  • For each document:                                      │
│    1. Extract text (GPU-accelerated OCR if needed)         │
│    2. Generate embeddings (GPU-accelerated)                │
│    3. Call Claude API for analysis (parallel)              │
│    4. Extract:                                             │
│       - Relevancy score (0-1000)                           │
│       - Micro score (0-1000)                               │
│       - Key insights                                       │
│       - Contradictions                                     │
│       - Smoking gun quotes                                 │
│  • Batch results together                                  │
│  • Upload results to Supabase Database                     │
│  • Mark batch as complete                                  │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Digital Ocean Droplet: Result Processor                   │
│  • Receives completion notification                        │
│  • Validates results                                       │
│  • Updates document_journal table                          │
│  • Sends progress notification to Telegram                 │
│  • Triggers next batch if more documents remain            │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  N8N Cloud: Progress Notification                          │
│  • Sends Telegram update:                                  │
│    "✅ Batch 1/700 complete                                │
│     Processed: 100 documents                               │
│     Avg Relevancy: 750/1000                                │
│     Critical docs found: 15                                │
│     Next batch: Starting in 2 minutes..."                  │
└─────────────────────────────────────────────────────────────┘
```

### Batch Processing Specifications

**Batch Configuration:**
- Batch size: 100 documents
- Parallel processing: 10 documents at a time (GPU)
- Estimated time per document: 30-60 seconds
- Estimated time per batch: 5-10 minutes
- Total batches needed: 700 (for 70,000 documents)

**Resource Utilization:**
- Vast.ai GPU: RTX 4090 ($0.50/hour)
- Processing time: 700 batches × 7.5 minutes = 87.5 hours
- Cost: 87.5 hours × $0.50 = $43.75 (well within $100 credit!)
- Remaining credit: $56.25 for re-processing or additional documents

**Error Handling:**
- Retry failed documents (max 3 attempts)
- Skip corrupted files (log for manual review)
- Resume capability (if job interrupted)
- Checkpoint every 10 batches

**Progress Tracking:**
```sql
CREATE TABLE batch_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_number INTEGER NOT NULL,
    total_batches INTEGER NOT NULL,
    documents_in_batch INTEGER NOT NULL,
    status TEXT CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    documents_processed INTEGER DEFAULT 0,
    documents_failed INTEGER DEFAULT 0,
    avg_relevancy_score INTEGER,
    critical_docs_found INTEGER,
    vast_ai_instance_id TEXT,
    error_log TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 📱 Use Case 2: Real-Time Courtroom Scanning

### Architecture Flow

```
┌──────────────────┐
│  Surface Pro or  │ (Scan document or take photo)
│  Telegram Upload │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Option A: Direct Upload to Digital Ocean                  │
│  • Upload via web interface on Surface Pro                 │
│  • OR send via Telegram (photo or file)                    │
│  • Immediate upload to Supabase Storage                    │
│  • Returns upload ID                                       │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  N8N Cloud: Real-Time Processing Trigger                   │
│  • Detects new upload via webhook                          │
│  • Routes to fastest available processor:                  │
│    Priority 1: Mac Mini (if online, fastest)               │
│    Priority 2: Digital Ocean (always available)            │
│    Priority 3: Vast.ai (if GPU needed for OCR)             │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Mac Mini OR Digital Ocean: Real-Time Processor            │
│  • Download document from Supabase Storage                 │
│  • Extract text (OCR if needed, ~30 seconds)               │
│  • Call Claude API for immediate analysis (~60 seconds)    │
│  • Extract all scoring and insights                        │
│  • Upload results to document_journal table                │
│  • Total time: <3 minutes                                  │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  N8N Cloud: Instant Notification                           │
│  • Sends Telegram notification:                            │
│    "✅ Document Processed                                  │
│     Filename: Court_Order_2025-11-07.pdf                   │
│     Relevancy: 850/1000 🔥                                 │
│     Insights: 5 key points found                           │
│     Contradictions: 2 detected ⚠️                          │
│     View details: [link to web dashboard]"                 │
└─────────────────────────────────────────────────────────────┘
```

### Real-Time Processing Specifications

**Speed Optimization:**
- Target: <3 minutes from scan to database
- OCR (if needed): <30 seconds (Tesseract)
- Claude API: ~60-90 seconds
- Database write: <5 seconds
- Notification: <2 seconds

**Offline Capability (Surface Pro):**
```
Surface Pro (Offline Mode)
    ↓
Scan & Queue Locally
    ↓
When Online: Auto-upload to Digital Ocean
    ↓
Process normally
```

**Redundancy:**
- Primary: Mac Mini (fastest, local)
- Backup: Digital Ocean (always available)
- Fallback: Queue for next available processor

---

## 🚀 Deployment Strategy

### Phase 1: Digital Ocean Droplet Setup (Week 1)

**Droplet Specifications:**
- **Plan:** Basic ($6/mo) or Professional ($12/mo)
- **RAM:** 1-2GB (Basic) or 2-4GB (Professional)
- **Storage:** 25-50GB SSD
- **Location:** Closest to you (e.g., SFO1 for California)

**Docker Compose Setup:**

```yaml
version: '3.8'

services:
  # FastAPI Application
  api:
    build: ./telegram-bot
    container_name: aseagi-api
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - ENVIRONMENT=production
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
    networks:
      - aseagi-network

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: aseagi-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./telegram-bot/static:/usr/share/nginx/html
    depends_on:
      - api
    restart: unless-stopped
    networks:
      - aseagi-network

  # Batch Job Manager
  batch-manager:
    build: ./batch-processor
    container_name: aseagi-batch-manager
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - VAST_AI_API_KEY=${VAST_AI_API_KEY}
      - GOOGLE_DRIVE_CREDENTIALS=${GOOGLE_DRIVE_CREDENTIALS}
    restart: unless-stopped
    volumes:
      - ./batch-data:/app/data
    networks:
      - aseagi-network

  # Redis for job queue
  redis:
    image: redis:alpine
    container_name: aseagi-redis
    ports:
      - "6379:6379"
    restart: unless-stopped
    networks:
      - aseagi-network

networks:
  aseagi-network:
    driver: bridge
```

**Deployment Commands:**

```bash
# SSH into droplet
ssh root@your-droplet-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Clone repository
git clone https://github.com/yourusername/ASEAGI.git
cd ASEAGI

# Create .env file
nano .env
# Add:
# SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
# SUPABASE_KEY=your-key
# CLAUDE_API_KEY=your-key
# VAST_AI_API_KEY=your-key

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

---

### Phase 2: Vast.ai GPU Instance (Week 2)

**Instance Selection:**
- **GPU:** RTX 4090 (24GB VRAM) or A100 (if available)
- **RAM:** 32GB+
- **Storage:** 100GB SSD
- **Cost:** ~$0.50-1.00/hour
- **Usage:** On-demand (start when batch job begins, stop when complete)

**Docker Image for Vast.ai:**

```dockerfile
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

# Install Python
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    tesseract-ocr \
    git

# Install Python packages
RUN pip3 install \
    torch torchvision --index-url https://download.pytorch.org/whl/cu122 \
    transformers \
    anthropic \
    supabase \
    pillow \
    pytesseract \
    fastapi \
    uvicorn

# Copy batch processor
COPY batch-processor /app
WORKDIR /app

# Run batch processor
CMD ["python3", "batch_processor.py"]
```

**Vast.ai Setup:**

```bash
# 1. Create account at vast.ai
# 2. Add $100 credit
# 3. Search for instances:
#    GPU: RTX 4090
#    RAM: 32GB+
#    Storage: 100GB+
#    Sort by: Price (lowest first)

# 4. Rent instance (via API or web UI)

# 5. SSH into instance
ssh -p PORT_NUMBER root@instance-ip

# 6. Pull Docker image
docker pull your-dockerhub/aseagi-batch-processor

# 7. Run batch processor
docker run -d \
  -e SUPABASE_URL=$SUPABASE_URL \
  -e SUPABASE_KEY=$SUPABASE_KEY \
  -e CLAUDE_API_KEY=$CLAUDE_API_KEY \
  --gpus all \
  your-dockerhub/aseagi-batch-processor
```

**Auto-Scaling Script (on Digital Ocean):**

```python
# batch_orchestrator.py
import vastai
import time

class VastAIOrchestrator:
    def __init__(self, api_key):
        self.client = vastai.Client(api_key)

    def start_batch_job(self, batch_id):
        # Search for available instances
        instances = self.client.search_offers(
            gpu_name="RTX_4090",
            min_gpu_ram_gb=20,
            max_price_per_hour=1.0
        )

        # Rent cheapest instance
        instance = instances[0]
        instance_id = self.client.rent_instance(
            instance['id'],
            image='your-dockerhub/aseagi-batch-processor',
            env={
                'BATCH_ID': batch_id,
                'SUPABASE_URL': os.environ['SUPABASE_URL'],
                'SUPABASE_KEY': os.environ['SUPABASE_KEY'],
                'CLAUDE_API_KEY': os.environ['CLAUDE_API_KEY']
            }
        )

        # Wait for completion
        while True:
            status = self.client.get_instance_status(instance_id)
            if status == 'completed':
                # Stop instance to save money
                self.client.stop_instance(instance_id)
                break
            time.sleep(60)  # Check every minute
```

---

### Phase 3: Mac Mini Local Processing (Week 1)

**Mac Mini Setup:**

```bash
# 1. Ensure N8N Local running (from earlier setup)
# 2. Install additional dependencies
brew install tesseract
pip3 install opencv-python pillow pytesseract

# 3. Create real-time processor
cd ~/ASEAGI
mkdir realtime-processor
cd realtime-processor

# 4. Copy real-time processing script (will create below)

# 5. Run as background service
cat > ~/Library/LaunchAgents/com.aseagi.realtime.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aseagi.realtime</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/yourname/ASEAGI/realtime-processor/processor.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.aseagi.realtime.plist
```

---

## 💰 Cost Analysis - Multi-Tiered

### Monthly Recurring Costs

| Service | Cost | Purpose |
|---------|------|---------|
| **Digital Ocean Droplet** | $12/mo | Production API + Web + Batch Manager |
| **N8N Cloud** | $20/mo | Telegram bot + orchestration |
| **Supabase Pro** | $25/mo | Database + storage |
| **Claude API** | $50-100/mo | AI analysis (batch + real-time) |
| **DO Spaces** (optional) | $5/mo | Cache for batch processing |
| **TOTAL Monthly** | **$112-162/mo** | Full production system |

### One-Time / Variable Costs

| Service | Cost | Purpose |
|---------|------|---------|
| **Vast.ai GPU** | $44 (one-time) | Process 7TB Google Drive (~88 hours) |
| **Remaining Credit** | $56 | Additional processing or re-runs |
| **Domain** (optional) | $12/year | Custom domain (aseagi.com) |
| **SSL Cert** (optional) | Free | Let's Encrypt via nginx |

### Future Hardware Investment

| Hardware | Estimated Cost | Benefit |
|----------|---------------|---------|
| **ML350 G6 Server** | $500-800 (used) | One-time, replaces Vast.ai |
| **NVIDIA GPU** | $500-1500 | RTX 4070-4090 |
| **RAM Upgrade** | $100-200 | 32-64GB for server |
| **Storage** | $100-300 | 2-4TB SSD |
| **TOTAL Investment** | **$1,200-2,800** | Zero ongoing GPU costs |

**Break-Even Analysis:**
- Vast.ai cost if processing ongoing: ~$50/month
- Hardware payback: 24-56 months
- **Recommendation:** Use Vast.ai credit now, buy GPU server after credit exhausted

---

## 📈 Performance Estimates

### Batch Processing (7TB Google Drive)

**Scenario:** Process 70,000 documents

| Metric | Estimate |
|--------|----------|
| **Documents** | 70,000 |
| **Batch size** | 100 documents |
| **Total batches** | 700 |
| **Time per batch** | 7.5 minutes (GPU-accelerated) |
| **Total processing time** | 87.5 hours |
| **Parallel instances** | 1 (Vast.ai) |
| **Calendar time** | 3.6 days (continuous) or 2 weeks (8hr/day) |
| **Cost** | $44 (Vast.ai @ $0.50/hr) |
| **Documents/hour** | 800 |
| **Cost per document** | $0.00063 |

### Real-Time Processing (Courtroom Scanning)

**Scenario:** Process individual documents on-demand

| Metric | Estimate |
|--------|----------|
| **Upload time** | 5-30 seconds (Surface Pro → DO) |
| **OCR time** | 20-40 seconds (if needed) |
| **Claude API** | 60-90 seconds |
| **Database write** | 2-5 seconds |
| **Notification** | 1-2 seconds |
| **Total time** | **2-3 minutes** |
| **Cost per document** | $0.01-0.02 (Claude API) |
| **Availability** | 99.9% (Digital Ocean SLA) |

---

## 🔄 Workflow Integration

### N8N Workflow 5: Batch Job Initiator (N8N Cloud)

**Purpose:** Start batch processing of Google Drive documents

```json
{
  "name": "ASEAGI Batch Job Initiator",
  "nodes": [
    {
      "name": "Manual Trigger or Schedule",
      "type": "n8n-nodes-base.manualTrigger",
      "position": [240, 300]
    },
    {
      "name": "Check Google Drive",
      "type": "n8n-nodes-base.googleDrive",
      "parameters": {
        "operation": "list",
        "folderId": "YOUR_GOOGLE_DRIVE_FOLDER_ID",
        "filters": {
          "query": "mimeType='application/pdf' or mimeType='image/jpeg'"
        }
      },
      "position": [460, 300]
    },
    {
      "name": "Get Processed Documents",
      "type": "n8n-nodes-base.postgres",
      "parameters": {
        "query": "SELECT google_drive_id FROM document_journal WHERE source = 'batch_google_drive'"
      },
      "position": [680, 300]
    },
    {
      "name": "Filter Unprocessed",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "// Filter out already processed documents\nconst processed = $node['Get Processed Documents'].json.map(d => d.google_drive_id);\nconst unprocessed = $items().filter(item => !processed.includes(item.json.id));\nreturn unprocessed;"
      },
      "position": [900, 300]
    },
    {
      "name": "Create Batches",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "// Chunk into batches of 100\nconst batchSize = 100;\nconst batches = [];\nfor (let i = 0; i < $items().length; i += batchSize) {\n  batches.push($items().slice(i, i + batchSize));\n}\nreturn batches.map((batch, i) => ({json: {batch_number: i+1, documents: batch}}));"
      },
      "position": [1120, 300]
    },
    {
      "name": "Submit to Digital Ocean",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://your-droplet-ip:8000/batch/submit",
        "method": "POST",
        "bodyParametersJson": "={{$json}}"
      },
      "position": [1340, 300]
    },
    {
      "name": "Notify Start",
      "type": "n8n-nodes-base.telegram",
      "parameters": {
        "text": "🚀 Batch Processing Started\\n\\nTotal documents: {{$json.total_documents}}\\nBatches: {{$json.total_batches}}\\nEstimated time: {{$json.estimated_hours}} hours\\n\\nTracking: http://your-droplet-ip:8000/batch/status",
        "chatId": "YOUR_TELEGRAM_USER_ID"
      },
      "position": [1560, 300]
    }
  ]
}
```

### N8N Workflow 6: Real-Time Document Processor (N8N Cloud)

**Purpose:** Process documents uploaded via Telegram or web in real-time

```json
{
  "name": "ASEAGI Real-Time Document Processor",
  "nodes": [
    {
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "document-upload",
        "httpMethod": "POST"
      },
      "position": [240, 300]
    },
    {
      "name": "Route to Processor",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "// Choose fastest available processor\nif (MAC_MINI_ONLINE) {\n  return {processor: 'mac-mini', endpoint: 'http://mac-mini-ip:5000/process'};\n} else {\n  return {processor: 'digital-ocean', endpoint: 'http://droplet-ip:8000/process-realtime'};\n}"
      },
      "position": [460, 300]
    },
    {
      "name": "Submit for Processing",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{$json.endpoint}}",
        "method": "POST",
        "bodyParametersJson": "={{$json}}"
      },
      "position": [680, 300]
    },
    {
      "name": "Wait for Completion",
      "type": "n8n-nodes-base.wait",
      "parameters": {
        "resume": "webhook",
        "timeout": 300
      },
      "position": [900, 300]
    },
    {
      "name": "Send Notification",
      "type": "n8n-nodes-base.telegram",
      "parameters": {
        "text": "✅ Document Processed\\n\\n*{{$json.filename}}*\\n\\nRelevancy: {{$json.relevancy_score}}/1000\\nInsights: {{$json.insights_count}}\\nContradictions: {{$json.contradictions_count}}\\n\\nView: http://droplet-ip:8000/document/{{$json.id}}",
        "chatId": "YOUR_TELEGRAM_USER_ID",
        "additionalFields": {
          "parse_mode": "Markdown"
        }
      },
      "position": [1120, 300]
    }
  ]
}
```

---

## 📝 Implementation Checklist

### Week 1: Digital Ocean Setup
- [ ] Create Digital Ocean account
- [ ] Provision droplet ($12/mo)
- [ ] SSH into droplet
- [ ] Install Docker + Docker Compose
- [ ] Clone ASEAGI repository
- [ ] Configure environment variables
- [ ] Deploy FastAPI container
- [ ] Deploy Nginx container
- [ ] Configure SSL/TLS (Let's Encrypt)
- [ ] Test API endpoints
- [ ] Point domain to droplet (optional)

### Week 2: Vast.ai Batch Processing
- [ ] Create Vast.ai account
- [ ] Add $100 credit
- [ ] Build Docker image for batch processing
- [ ] Push to Docker Hub
- [ ] Create batch job manager on Droplet
- [ ] Test with small batch (10 documents)
- [ ] Deploy N8N Workflow 5 (Batch Initiator)
- [ ] Start full batch processing
- [ ] Monitor progress

### Week 2: Real-Time Processing
- [ ] Deploy real-time processor on Mac Mini
- [ ] Configure N8N Workflow 6
- [ ] Test upload via Telegram
- [ ] Test upload via Surface Pro web interface
- [ ] Verify <3 minute processing time
- [ ] Set up notifications

### Week 3: Monitoring & Optimization
- [ ] Set up logging (Digital Ocean logs)
- [ ] Configure alerts (Telegram notifications)
- [ ] Optimize batch size
- [ ] Review costs
- [ ] Plan for ML350 G6 GPU server

---

**For Ashe - Enterprise-grade hybrid architecture for optimal performance** ⚖️

*"Process 7TB of history while scanning the present in real-time"*

---

**Last Updated:** November 2025
**Status:** Ready for multi-tiered deployment
**Next:** Deploy Digital Ocean Droplet
