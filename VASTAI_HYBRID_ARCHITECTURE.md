# ASEAGI Hybrid Cloud Architecture
## Vast.ai GPU Processing + DigitalOcean Persistent Services

**Date:** November 14, 2025
**Version:** 1.0
**Target:** Mac Mini development → Production deployment

---

## 🎯 Architecture Philosophy

### The Smart Approach: Elastic GPU + Persistent Storage

```
💰 COST OPTIMIZATION STRATEGY:

OLD WAY (Expensive):
├─ GPU Droplet: $800/month running 24/7
├─ Most time idle (no processing)
└─ Total: $9,600/year wasted

NEW WAY (Smart):
├─ Vast.ai GPU: $0.40/hour × 4 hours/day × 20 days = $32/month
├─ Droplet (no GPU): $24/month running 24/7
├─ Cloud Storage: $5/month (DigitalOcean Spaces)
└─ Total: $61/month = $732/year (SAVES $8,868!)
```

### Key Principles

1. **Vast.ai for Processing** - Spin up only when needed
2. **Droplet for Services** - Always-on lightweight dashboard
3. **Cloud Storage for Files** - Persistent, accessible from both
4. **Supabase for Database** - Metadata and logs
5. **Ephemeral Compute** - No state on Vast.ai instances

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERFACES                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  📱 Telegram Bot        🌐 Web Dashboard       💻 Mac Mini       │
│  (Mobile upload)        (Monitor & control)    (Development)      │
│                                                                   │
└────────────────┬──────────────┬──────────────┬───────────────────┘
                 │              │              │
                 ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│          DIGITALOCEAN DROPLET (Always Running - $24/mo)          │
│                    Ubuntu 22.04 | 2GB RAM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  🎛️ Control Plane (Flask API)                                   │
│     ├─ Vast.ai instance launcher                                │
│     ├─ Job queue manager                                        │
│     ├─ Status monitor                                           │
│     └─ Telegram webhook receiver                                │
│                                                                   │
│  📊 Monitoring Dashboard (Streamlit)                             │
│     ├─ Processing status                                        │
│     ├─ Cost tracking                                            │
│     ├─ Document browser                                         │
│     └─ Vast.ai instance control                                 │
│                                                                   │
│  🗄️ Lightweight Services                                         │
│     ├─ Redis (job queue)                                        │
│     ├─ Nginx (reverse proxy)                                    │
│     └─ Certbot (SSL)                                            │
│                                                                   │
└────────────────┬──────────────┬──────────────┬───────────────────┘
                 │              │              │
                 │              │              ▼
                 │              │      ┌─────────────────┐
                 │              │      │  SUPABASE DB    │
                 │              │      ├─────────────────┤
                 │              │      │ • Metadata      │
                 │              │      │ • File paths    │
                 │              │      │ • Processing    │
                 │              │      │   logs          │
                 │              │      │ • User data     │
                 │              │      └─────────────────┘
                 │              │
                 │              ▼
                 │      ┌─────────────────────────────────┐
                 │      │  CLOUD STORAGE (DO Spaces)      │
                 │      │  S3-Compatible - $5/mo          │
                 │      ├─────────────────────────────────┤
                 │      │                                 │
                 │      │  📁 /raw-documents/             │
                 │      │     └─ Original uploads         │
                 │      │                                 │
                 │      │  📁 /processed/                 │
                 │      │     ├─ OCR text                 │
                 │      │     ├─ Thumbnails               │
                 │      │     └─ Metadata JSON            │
                 │      │                                 │
                 │      │  📁 /exports/                   │
                 │      │     └─ Generated reports        │
                 │      │                                 │
                 │      └─────────────────────────────────┘
                 │              ▲
                 │              │ (Mounts via s3fs)
                 ▼              │
┌─────────────────────────────────────────────────────────────────┐
│         VAST.AI GPU INSTANCE (On-Demand - $0.40/hr)             │
│                RTX 3080 | 8GB VRAM | Docker                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  🐳 Docker Container: aseagi/document-processor:latest          │
│                                                                   │
│  📦 Installed:                                                   │
│     ├─ Python 3.11                                              │
│     ├─ PyTorch (GPU)                                            │
│     ├─ Tesseract OCR                                            │
│     ├─ Claude API client                                        │
│     ├─ Supabase client                                          │
│     ├─ S3 client (boto3)                                        │
│     └─ All processing scripts                                   │
│                                                                   │
│  ⚙️ Processing Pipeline:                                         │
│     1. Mount cloud storage (read-only for raw docs)             │
│     2. Fetch job from Supabase queue                            │
│     3. Download document from S3                                │
│     4. Run GPU-accelerated OCR                                  │
│     5. Claude Vision analysis                                   │
│     6. Upload results to S3                                     │
│     7. Update Supabase metadata                                 │
│     8. Report status to Droplet                                 │
│     9. Process next job                                         │
│    10. Auto-shutdown when queue empty                           │
│                                                                   │
│  💾 NO Local Storage (Stateless)                                │
│     └─ All data goes to S3 immediately                          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                                ▲
                                │ (Destroyed after processing)
                                ▼
                        ⚡ Instance Lifecycle:
                        ├─ Created: When jobs queued
                        ├─ Runs: Until queue empty
                        ├─ Destroyed: After idle 5 min
                        └─ Cost: Only pay for actual use
```

---

## 💾 Cloud Storage Strategy (DigitalOcean Spaces)

### Why DigitalOcean Spaces?

- ✅ S3-compatible (works with boto3)
- ✅ $5/month for 250GB
- ✅ Same datacenter as Droplet (fast)
- ✅ CDN included (Spaces CDN)
- ✅ Easy to mount on both systems

### Alternative: AWS S3
- Cheaper for large storage
- More complex billing
- Higher egress costs

### Storage Structure

```
aseagi-documents/  (DO Spaces bucket)
│
├── raw/                          # Original uploads
│   ├── 2025/
│   │   ├── 11/
│   │   │   ├── 14/
│   │   │   │   ├── abc123.pdf
│   │   │   │   ├── def456.jpg
│   │   │   │   └── ghi789.png
│   │
├── processed/                    # After GPU processing
│   ├── 2025/11/14/
│   │   ├── abc123/
│   │   │   ├── ocr.txt
│   │   │   ├── metadata.json
│   │   │   ├── thumbnail.jpg
│   │   │   └── analysis.json
│   │
├── cache/                        # Temporary processing
│   └── (auto-cleaned daily)
│
└── exports/                      # Generated reports
    ├── weekly-report-2025-11-14.pdf
    └── case-summary-proj344.pdf
```

---

## 🔄 Processing Workflow

### Scenario 1: Upload via Telegram

```
1. User sends document to Telegram bot
   ↓
2. Droplet receives webhook
   ↓
3. Droplet uploads to S3 Spaces (/raw/)
   ↓
4. Droplet creates job in Supabase:
   {
     "job_id": "uuid",
     "file_path": "s3://aseagi/raw/2025/11/14/doc.pdf",
     "status": "queued",
     "priority": "high"
   }
   ↓
5. Droplet checks: Any Vast.ai instance running?
   ├─ YES: Job will be picked up
   └─ NO: Launch Vast.ai instance
   ↓
6. Vast.ai instance starts (2-3 minutes)
   ↓
7. Container runs worker script:
   - Connects to Supabase
   - Fetches jobs with status="queued"
   - Downloads from S3
   - Processes with GPU
   - Uploads results to S3
   - Updates Supabase status="completed"
   ↓
8. After 5 min idle: Instance auto-destroys
   ↓
9. User sees result in:
   - Telegram bot reply
   - Web dashboard
   - Supabase metadata
```

### Scenario 2: Bulk Upload (1000+ documents)

```
1. User uploads folder to S3 Spaces via:
   - Mac Mini → rclone sync
   - Or web dashboard → direct upload
   ↓
2. User clicks "Start Bulk Processing" in dashboard
   ↓
3. Droplet creates jobs for all files:
   - Scans S3 bucket
   - Creates Supabase job records
   - Estimates cost ($0.02 × 1000 = $20)
   ↓
4. User confirms
   ↓
5. Droplet launches Vast.ai instance
   (selects cheapest available RTX 3080)
   ↓
6. Instance processes in parallel (8 workers)
   - ~100 docs/hour
   - 10 hours total
   - Cost: $0.40/hr × 10 = $4.00
   ↓
7. Progress visible in dashboard (real-time)
   ↓
8. Instance auto-destroys when done
   ↓
9. All results in S3 + Supabase
```

### Scenario 3: View Document (No GPU needed)

```
1. User opens web dashboard
   ↓
2. Searches for "police report"
   ↓
3. Droplet queries Supabase metadata
   ↓
4. Returns matching documents
   ↓
5. User clicks to view
   ↓
6. Droplet generates signed S3 URL
   ↓
7. Browser loads document directly from S3 CDN
   (No processing, no GPU, no Vast.ai cost)
```

---

## 🐳 Vast.ai Docker Image

### Dockerfile

```dockerfile
# Dockerfile for Vast.ai GPU Processing
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install --no-cache-dir \
    anthropic \
    supabase \
    boto3 \
    pillow \
    pytesseract \
    opencv-python-headless \
    python-dotenv \
    redis \
    requests

# Create working directory
WORKDIR /app

# Copy processing scripts
COPY scripts/ /app/scripts/
COPY worker.py /app/
COPY config.py /app/

# Set executable permissions
RUN chmod +x /app/worker.py

# Environment variables (will be set by Vast.ai)
ENV SUPABASE_URL=""
ENV SUPABASE_KEY=""
ENV ANTHROPIC_API_KEY=""
ENV S3_ENDPOINT=""
ENV S3_ACCESS_KEY=""
ENV S3_SECRET_KEY=""
ENV S3_BUCKET=""

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)"

# Start worker
CMD ["python3", "-u", "worker.py"]
```

### worker.py (GPU Processing Worker)

```python
#!/usr/bin/env python3
"""
Vast.ai GPU Worker
Processes documents from queue, uses GPU, writes to S3
"""

import os
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import boto3
from supabase import create_client
import anthropic
from PIL import Image
import pytesseract

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VastaiWorker:
    def __init__(self):
        # Initialize clients
        self.supabase = create_client(
            os.environ['SUPABASE_URL'],
            os.environ['SUPABASE_KEY']
        )

        self.claude = anthropic.Anthropic(
            api_key=os.environ['ANTHROPIC_API_KEY']
        )

        self.s3 = boto3.client(
            's3',
            endpoint_url=os.environ['S3_ENDPOINT'],
            aws_access_key_id=os.environ['S3_ACCESS_KEY'],
            aws_secret_access_key=os.environ['S3_SECRET_KEY']
        )

        self.bucket = os.environ['S3_BUCKET']
        self.idle_count = 0
        self.max_idle = 5  # 5 minutes idle = shutdown

    def fetch_job(self) -> Optional[Dict[str, Any]]:
        """Fetch next job from Supabase"""
        try:
            result = self.supabase.table('processing_jobs')\
                .select('*')\
                .eq('status', 'queued')\
                .order('priority', desc=True)\
                .limit(1)\
                .execute()

            if result.data:
                job = result.data[0]
                # Mark as processing
                self.supabase.table('processing_jobs')\
                    .update({'status': 'processing', 'started_at': 'now()'})\
                    .eq('id', job['id'])\
                    .execute()
                return job
            return None
        except Exception as e:
            logger.error(f"Error fetching job: {e}")
            return None

    def download_from_s3(self, s3_path: str, local_path: str):
        """Download file from S3"""
        # Extract key from s3:// URL
        key = s3_path.replace(f"s3://{self.bucket}/", "")
        self.s3.download_file(self.bucket, key, local_path)

    def upload_to_s3(self, local_path: str, s3_key: str):
        """Upload file to S3"""
        self.s3.upload_file(local_path, self.bucket, s3_key)

    def process_document(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing function"""
        job_id = job['id']
        s3_path = job['file_path']

        logger.info(f"Processing job {job_id}: {s3_path}")

        # Create temp directory
        temp_dir = Path(f"/tmp/job_{job_id}")
        temp_dir.mkdir(exist_ok=True)

        try:
            # Download file
            local_file = temp_dir / "input.file"
            self.download_from_s3(s3_path, str(local_file))

            # Run OCR (GPU accelerated)
            ocr_text = pytesseract.image_to_string(Image.open(local_file))

            # Claude Vision analysis
            with open(local_file, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode()

            response = self.claude.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data
                            }
                        },
                        {
                            "type": "text",
                            "text": "Analyze this legal document. Extract: type, date, parties, case number, relevancy score."
                        }
                    ]
                }]
            )

            analysis = response.content[0].text

            # Save results to S3
            results_dir = temp_dir / "results"
            results_dir.mkdir(exist_ok=True)

            # OCR text
            ocr_file = results_dir / "ocr.txt"
            ocr_file.write_text(ocr_text)
            self.upload_to_s3(
                str(ocr_file),
                f"processed/{job_id}/ocr.txt"
            )

            # Analysis JSON
            analysis_file = results_dir / "analysis.json"
            analysis_file.write_text(analysis)
            self.upload_to_s3(
                str(analysis_file),
                f"processed/{job_id}/analysis.json"
            )

            # Update Supabase
            result = {
                'status': 'completed',
                'completed_at': 'now()',
                'ocr_path': f"s3://{self.bucket}/processed/{job_id}/ocr.txt",
                'analysis_path': f"s3://{self.bucket}/processed/{job_id}/analysis.json",
                'ocr_text': ocr_text[:1000],  # First 1000 chars
                'error': None
            }

            return result

        except Exception as e:
            logger.error(f"Error processing job {job_id}: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'completed_at': 'now()'
            }

        finally:
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    def run(self):
        """Main worker loop"""
        logger.info("🚀 Vast.ai worker started")
        logger.info(f"Bucket: {self.bucket}")

        while True:
            # Fetch job
            job = self.fetch_job()

            if job:
                self.idle_count = 0

                # Process
                result = self.process_document(job)

                # Update Supabase
                self.supabase.table('processing_jobs')\
                    .update(result)\
                    .eq('id', job['id'])\
                    .execute()

                logger.info(f"✅ Job {job['id']} completed")

            else:
                # No jobs
                self.idle_count += 1
                logger.info(f"⏰ Idle {self.idle_count}/{self.max_idle} minutes")

                if self.idle_count >= self.max_idle:
                    logger.info("💤 Max idle reached, shutting down")
                    # Signal to Vast.ai to destroy instance
                    # (Vast.ai will auto-destroy on exit)
                    break

                # Wait 1 minute
                time.sleep(60)

if __name__ == "__main__":
    worker = VastaiWorker()
    worker.run()
```

---

## 🎛️ Droplet Control Plane (Flask API)

### app.py (Flask API on Droplet)

```python
#!/usr/bin/env python3
"""
ASEAGI Control Plane
Runs on DigitalOcean Droplet
Manages Vast.ai instances and job queue
"""

from flask import Flask, request, jsonify, render_template
from supabase import create_client
import subprocess
import os
import json

app = Flask(__name__)

# Initialize Supabase
supabase = create_client(
    os.environ['SUPABASE_URL'],
    os.environ['SUPABASE_KEY']
)

VASTAI_API_KEY = os.environ['VASTAI_API_KEY']

class VastaiController:
    """Control Vast.ai instances"""

    def find_cheapest_instance(self, gpu_type="RTX 3080"):
        """Find cheapest available instance"""
        cmd = f"vastai search offers 'gpu_name={gpu_type} rentable=True' --raw"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            offers = json.loads(result.stdout)
            # Sort by price
            offers.sort(key=lambda x: x['dph_total'])
            return offers[0] if offers else None
        return None

    def launch_instance(self, offer_id, docker_image="aseagi/document-processor:latest"):
        """Launch Vast.ai instance"""
        env_vars = {
            'SUPABASE_URL': os.environ['SUPABASE_URL'],
            'SUPABASE_KEY': os.environ['SUPABASE_KEY'],
            'ANTHROPIC_API_KEY': os.environ['ANTHROPIC_API_KEY'],
            'S3_ENDPOINT': os.environ['S3_ENDPOINT'],
            'S3_ACCESS_KEY': os.environ['S3_ACCESS_KEY'],
            'S3_SECRET_KEY': os.environ['S3_SECRET_KEY'],
            'S3_BUCKET': os.environ['S3_BUCKET']
        }

        env_str = " ".join([f"-e {k}={v}" for k, v in env_vars.items()])

        cmd = f"vastai create instance {offer_id} --image {docker_image} {env_str}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            return json.loads(result.stdout)
        return None

    def get_running_instances(self):
        """Get list of running instances"""
        cmd = "vastai show instances --raw"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            return json.loads(result.stdout)
        return []

    def destroy_instance(self, instance_id):
        """Destroy Vast.ai instance"""
        cmd = f"vastai destroy instance {instance_id}"
        subprocess.run(cmd, shell=True)

controller = VastaiController()

@app.route('/api/jobs/create', methods=['POST'])
def create_job():
    """Create new processing job"""
    data = request.json

    job = {
        'file_path': data['file_path'],
        'priority': data.get('priority', 'normal'),
        'status': 'queued',
        'created_at': 'now()'
    }

    result = supabase.table('processing_jobs').insert(job).execute()

    # Check if we need to launch instance
    jobs_queued = supabase.table('processing_jobs')\
        .select('id')\
        .eq('status', 'queued')\
        .execute()

    running_instances = controller.get_running_instances()

    if len(jobs_queued.data) > 0 and len(running_instances) == 0:
        # Launch instance
        offer = controller.find_cheapest_instance()
        if offer:
            instance = controller.launch_instance(offer['id'])
            return jsonify({
                'job': result.data[0],
                'instance_launched': True,
                'instance_id': instance.get('new_contract')
            })

    return jsonify({'job': result.data[0], 'instance_launched': False})

@app.route('/api/instances/status', methods=['GET'])
def instances_status():
    """Get status of all instances"""
    instances = controller.get_running_instances()

    jobs_queued = supabase.table('processing_jobs')\
        .select('id')\
        .eq('status', 'queued')\
        .execute()

    jobs_processing = supabase.table('processing_jobs')\
        .select('id')\
        .eq('status', 'processing')\
        .execute()

    return jsonify({
        'instances': instances,
        'jobs_queued': len(jobs_queued.data),
        'jobs_processing': len(jobs_processing.data)
    })

@app.route('/telegram/webhook', methods=['POST'])
def telegram_webhook():
    """Handle Telegram uploads"""
    data = request.json

    # Upload to S3 Spaces
    # Create job
    # Return response

    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## 📦 Repository Structure for Droplet

```
aseagi-droplet/
├── README.md
├── requirements.txt
├── .env.example
├── docker-compose.yml
│
├── app/
│   ├── __init__.py
│   ├── app.py              # Flask control plane
│   ├── vastai_controller.py
│   └── telegram_bot.py
│
├── dashboard/
│   ├── streamlit_app.py    # Monitoring dashboard
│   └── pages/
│       ├── documents.py
│       ├── jobs.py
│       └── costs.py
│
├── scripts/
│   ├── deploy.sh
│   ├── backup.sh
│   └── setup_spaces.sh
│
├── vastai/
│   ├── Dockerfile          # For Vast.ai GPU
│   ├── worker.py
│   ├── config.py
│   └── build_and_push.sh
│
└── nginx/
    └── aseagi.conf
```

Let me continue creating the actual implementation files...

