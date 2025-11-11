# Cloud GPU & Video Processing Setup Guide

**Date:** November 11, 2025
**Services:** Parsec, DigitalOcean Droplet, Vast.ai
**Purpose:** Video rendering, data processing, remote desktop access

---

## 🎯 Overview

### Service Purposes

| Service | Purpose | Best For | Cost |
|---------|---------|----------|------|
| **Parsec** | Remote desktop streaming | Accessing GPU machines remotely with low latency | Free (Personal) / $10/mo (Teams) |
| **DigitalOcean Droplet** | Always-on server | Databases, dashboards, web services, light processing | $6-$48/mo |
| **Vast.ai** | On-demand GPU compute | Video rendering, AI processing, heavy compute tasks | $0.10-$2.00/hr |

### Use Cases for ASEAGI Project

- **Video Evidence Processing**: Render court video evidence, extract frames, transcribe audio
- **Document OCR**: GPU-accelerated OCR for scanned legal documents
- **AI Document Analysis**: Run Claude/GPT models on large document batches
- **Dashboard Hosting**: Keep dashboards running 24/7 on droplet
- **Remote Work**: Access powerful GPU from anywhere via Parsec

---

## 🖥️ Part 1: DigitalOcean Droplet Setup

### Current Droplet Status

**IP:** 137.184.1.91
**Current Use:** Bug tracker, dashboards (ports 8501-8507)
**OS:** Ubuntu Linux

### Recommended Upgrades for Video Processing

#### Option A: Upgrade Existing Droplet

```bash
# SSH into droplet
ssh root@137.184.1.91

# Check current specs
free -h          # Memory
df -h            # Disk space
nproc            # CPU cores

# If you need more resources, upgrade via DigitalOcean dashboard:
# - Basic: $12/mo (2 GB RAM, 2 vCPUs) - Current
# - Premium: $24/mo (4 GB RAM, 2 vCPUs) - Light video work
# - CPU-Optimized: $48/mo (8 GB RAM, 4 vCPUs) - Heavy processing
```

#### Option B: Add Second Droplet for GPU Work

Create a separate droplet for heavy processing:

1. **Go to DigitalOcean Dashboard** → Create → Droplets
2. **Choose:**
   - **OS:** Ubuntu 22.04 LTS
   - **Plan:** CPU-Optimized ($48/mo for 4 vCPUs, 8GB RAM)
   - **Datacenter:** Same region as current droplet (for low latency)
   - **Additional:** Enable backups ($2.40/mo)
3. **Add SSH Key:** Use same key as existing droplet
4. **Name:** `aseagi-gpu-worker`

### Install Video Processing Tools on Droplet

```bash
ssh root@137.184.1.91

# Update system
apt update && apt upgrade -y

# Install FFmpeg (video processing)
apt install -y ffmpeg

# Install video codecs
apt install -y libavcodec-extra libavformat-dev libavutil-dev libswscale-dev

# Install Python video libraries
pip3 install opencv-python opencv-contrib-python moviepy imageio

# Test FFmpeg
ffmpeg -version

# Test video conversion (example)
# ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium output.mp4
```

### Install GPU Monitoring (if using GPU droplet)

```bash
# Install nvidia-smi for GPU monitoring
apt install -y nvidia-utils-535

# Monitor GPU usage
watch -n 1 nvidia-smi
```

---

## 🎮 Part 2: Parsec Setup

### What is Parsec?

Parsec provides ultra-low latency remote desktop access. Perfect for:
- Accessing Vast.ai GPU machines
- Remote work on video editing
- Testing dashboards remotely
- Accessing your droplet with GUI

### Install Parsec

#### On Your Local Machine (Mac/Windows/Linux)

1. **Download Parsec:**
   - Visit: https://parsec.app/downloads
   - Download for your OS (Mac, Windows, Linux)
   - Install and create account

2. **Login:**
   ```
   Email: your_email@example.com
   Password: (create strong password)
   ```

#### On Vast.ai GPU Instance (when you rent one)

Parsec will be pre-installed if you select a Parsec-compatible template (recommended).

### Parsec Configuration

**Best Settings for Video Work:**

```
Resolution: 1920x1080 (Full HD)
FPS: 60
Bandwidth: 50 Mbps (adjust based on internet speed)
Color Mode: 4:4:4 (best quality for editing)
H.265 (HEVC): Enabled (better compression)
```

**Access via Parsec:**

1. Start Parsec on local machine
2. See available computers (your Vast.ai instance will appear)
3. Click to connect
4. Full desktop access with GPU acceleration

---

## 🚀 Part 3: Vast.ai GPU Setup

### What is Vast.ai?

Vast.ai is a marketplace for renting cheap GPU compute. Perfect for:
- Video rendering (Adobe Premiere, DaVinci Resolve)
- AI model inference (Claude, GPT, Whisper)
- Batch processing legal documents
- OCR on large document sets

### Cost Comparison

| GPU Type | VRAM | Performance | Vast.ai Cost/hr | Use Case |
|----------|------|-------------|-----------------|----------|
| **RTX 3060** | 12GB | Good | $0.10-$0.20 | Light video editing, OCR |
| **RTX 3080** | 10GB | Great | $0.25-$0.40 | Video editing, AI inference |
| **RTX 4090** | 24GB | Excellent | $0.60-$1.20 | 4K video, large AI models |
| **A100** | 40GB | Professional | $1.50-$2.50 | Heavy AI training, batch processing |

**Example Costs:**
- 8 hours of video editing on RTX 3080: $0.35/hr × 8 = **$2.80**
- Batch OCR 500 documents on RTX 4090: $1.00/hr × 2 hrs = **$2.00**
- Compare to: AWS p3.2xlarge (Tesla V100): **$3.06/hr** 😱

### Sign Up for Vast.ai

1. **Visit:** https://vast.ai
2. **Create Account:**
   - Email: your_email@example.com
   - Verify email
3. **Add Payment Method:**
   - Credit card or crypto
   - Minimum deposit: $10
4. **Get $5 Credit:** Use referral code `PARSEC` (if available)

### Rent a GPU Instance

#### Step 1: Search for GPUs

```bash
# Go to: https://vast.ai/console/create/

# Filter by:
- GPU Type: RTX 3080 or RTX 4090
- VRAM: ≥ 12GB
- Disk Space: ≥ 100GB
- DLPerf: ≥ 50 (reliability score)
- Bandwidth: ≥ 100 Mbps
```

#### Step 2: Select Template

**For Video Rendering:**
- **Template:** `parsec-ubuntu-20.04` (recommended)
- **Includes:** Parsec, CUDA, FFmpeg, Python

**For AI/Document Processing:**
- **Template:** `pytorch-2.0-cuda-11.8`
- **Includes:** Python, PyTorch, CUDA, Jupyter

#### Step 3: Configure Instance

```yaml
Disk Space: 100 GB (minimum)
Image: parsec-ubuntu-20.04
Docker: Disabled (unless you need it)
Launch Mode: On-Demand (can stop anytime)
```

#### Step 4: Launch Instance

1. Click **"Rent"** on selected GPU
2. Wait 2-5 minutes for provisioning
3. Instance will appear in **"Instances"** tab
4. Status will change: `loading` → `running`

### Connect to Vast.ai Instance

#### Method 1: SSH (Terminal Access)

```bash
# Get SSH command from Vast.ai dashboard
# Example:
ssh -p 12345 root@ssh.vast.ai -L 8080:localhost:8080

# Or use direct IP:
ssh root@<instance-ip>
```

#### Method 2: Parsec (GUI Access)

1. **On Vast.ai instance terminal:**
   ```bash
   # Parsec is pre-installed on parsec templates
   # Get Parsec connection code:
   cat /home/user/.parsec/parsec-peer-id
   ```

2. **On your local Parsec app:**
   - Click "Add Computer"
   - Enter peer ID from above
   - Connect!

3. **Login to Ubuntu Desktop:**
   - Username: `user`
   - Password: Check Vast.ai dashboard notes

#### Method 3: Jupyter Notebook

```bash
# If using Jupyter template, access at:
http://<instance-ip>:8080

# Password shown in Vast.ai dashboard logs
```

---

## 🎬 Part 4: Video Processing Workflows

### Workflow 1: Render Video on Vast.ai

```bash
# SSH into Vast.ai instance
ssh root@vast-instance

# Upload video file (from your machine)
# On your local machine:
scp -P 12345 input_video.mp4 root@ssh.vast.ai:/workspace/

# Or use rsync for large files:
rsync -avz -e "ssh -p 12345" input_video.mp4 root@ssh.vast.ai:/workspace/

# On Vast.ai instance, render video
cd /workspace

# Example: Convert to H.265 (smaller file)
ffmpeg -i input_video.mp4 -c:v libx265 -crf 28 -c:a aac -b:a 128k output_video.mp4

# Extract frames for evidence analysis
ffmpeg -i video.mp4 -vf fps=1 frames/frame_%04d.png

# Download result
# On your machine:
scp -P 12345 root@ssh.vast.ai:/workspace/output_video.mp4 ./
```

### Workflow 2: Batch Video Processing

```python
# batch_video_processor.py
import subprocess
import os
from pathlib import Path

def process_video(input_path, output_path, quality='medium'):
    """Process video with FFmpeg"""

    # Quality presets
    presets = {
        'low': {'crf': 32, 'preset': 'fast'},
        'medium': {'crf': 28, 'preset': 'medium'},
        'high': {'crf': 23, 'preset': 'slow'}
    }

    settings = presets[quality]

    cmd = [
        'ffmpeg', '-i', input_path,
        '-c:v', 'libx265',
        '-crf', str(settings['crf']),
        '-preset', settings['preset'],
        '-c:a', 'aac', '-b:a', '128k',
        output_path
    ]

    subprocess.run(cmd, check=True)
    print(f"✅ Processed: {input_path} → {output_path}")

def batch_process(input_dir, output_dir, quality='medium'):
    """Process all videos in directory"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    video_files = list(input_path.glob('*.mp4')) + list(input_path.glob('*.mov'))

    for i, video in enumerate(video_files, 1):
        output_file = output_path / f"{video.stem}_processed.mp4"
        print(f"[{i}/{len(video_files)}] Processing: {video.name}")
        process_video(str(video), str(output_file), quality)

    print(f"✅ Batch complete! Processed {len(video_files)} videos.")

if __name__ == '__main__':
    batch_process('/workspace/videos/input', '/workspace/videos/output', quality='medium')
```

### Workflow 3: Extract Audio from Court Videos

```bash
# Extract audio for transcription
ffmpeg -i court_hearing.mp4 -vn -acodec pcm_s16le -ar 16000 audio.wav

# Use Whisper for transcription (if installed)
whisper audio.wav --model medium --output_format txt

# Or upload to Claude/GPT for transcription analysis
```

---

## 📊 Part 5: Integration with ASEAGI Project

### Use Case 1: Video Evidence Processing

**Scenario:** Court hearing videos need frame extraction and analysis

```bash
# On Vast.ai GPU instance
cd /workspace

# Upload court video
# (via scp from local machine or droplet)

# Extract key frames (1 per second)
ffmpeg -i court_hearing.mp4 -vf fps=1 frames/frame_%04d.png

# Analyze frames with Claude API
python3 analyze_frames.py --input frames/ --output analysis.json

# Upload results to Supabase
python3 upload_to_supabase.py --file analysis.json --table video_evidence
```

### Use Case 2: Batch Document OCR

**Scenario:** 500 scanned PDF documents need OCR

```python
# batch_ocr.py
import os
from pathlib import Path
import pytesseract
from pdf2image import convert_from_path
from supabase import create_client

def ocr_pdf(pdf_path):
    """OCR a PDF and return text"""
    images = convert_from_path(pdf_path, dpi=300)
    text = ""
    for i, image in enumerate(images):
        page_text = pytesseract.image_to_string(image)
        text += f"\n--- Page {i+1} ---\n{page_text}"
    return text

def batch_ocr(input_dir, supabase_url, supabase_key):
    """OCR all PDFs and upload to Supabase"""
    client = create_client(supabase_url, supabase_key)

    pdf_files = list(Path(input_dir).glob('*.pdf'))

    for i, pdf in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] OCR: {pdf.name}")

        text = ocr_pdf(str(pdf))

        # Upload to Supabase
        client.table('documents_ocr').insert({
            'filename': pdf.name,
            'ocr_text': text,
            'processed_at': 'now()'
        }).execute()

        print(f"✅ Uploaded to Supabase: {pdf.name}")

if __name__ == '__main__':
    batch_ocr(
        '/workspace/pdfs',
        'https://jvjlhxodmbkodzmggwpu.supabase.co',
        'your_supabase_key'
    )
```

### Use Case 3: AI Document Analysis with GPU

```python
# gpu_document_analysis.py
import torch
from transformers import pipeline

# Use GPU for faster inference
device = 0 if torch.cuda.is_available() else -1

# Load AI model (e.g., legal document classifier)
classifier = pipeline("text-classification",
                     model="nlpaueb/legal-bert-base-uncased",
                     device=device)

def analyze_document(text):
    """Classify legal document with GPU acceleration"""
    result = classifier(text[:512])  # First 512 tokens
    return result

# Process 1000 documents in minutes instead of hours!
```

---

## 💰 Part 6: Cost Optimization

### Cost-Effective Strategies

#### 1. Use DigitalOcean for Always-On Services

```yaml
Always Running on Droplet ($12/mo):
  - Dashboards (Streamlit)
  - Bug tracker
  - Supabase connection
  - Small batch jobs

Total: $12/month fixed cost
```

#### 2. Use Vast.ai for Heavy Compute (On-Demand)

```yaml
Pay Only When Rendering:
  - Video editing: $0.35/hr × 10 hrs/month = $3.50
  - Batch OCR: $0.80/hr × 5 hrs/month = $4.00
  - AI processing: $1.00/hr × 3 hrs/month = $3.00

Total: ~$10-15/month variable cost
```

#### 3. Use Parsec for Remote Access (Free)

```yaml
Parsec Personal (Free):
  - 1 user
  - Unlimited hours
  - Up to 3 connected devices

Total: $0/month
```

### Monthly Cost Estimate

| Service | Cost | Purpose |
|---------|------|---------|
| DigitalOcean Droplet | $12/mo | 24/7 dashboards & database |
| Vast.ai GPU (10-20 hrs) | $10-15/mo | Video rendering & AI processing |
| Parsec | Free | Remote access |
| **Total** | **$22-27/mo** | Complete cloud GPU setup |

**Compare to:**
- AWS EC2 with GPU: $200+/mo
- Google Cloud GPU: $150+/mo
- Local workstation GPU: $1,500+ upfront

---

## 🔧 Part 7: Setup Checklist

### Phase 1: Droplet Optimization (Your Existing Server)

- [ ] SSH into droplet: `ssh root@137.184.1.91`
- [ ] Install FFmpeg: `apt install -y ffmpeg`
- [ ] Install Python video libs: `pip3 install opencv-python moviepy`
- [ ] Test video conversion: `ffmpeg -version`
- [ ] Verify dashboards still running: `ps aux | grep streamlit`

### Phase 2: Parsec Installation

- [ ] Download Parsec: https://parsec.app/downloads
- [ ] Create Parsec account
- [ ] Install on local machine (Mac/Windows/Linux)
- [ ] Test connection to droplet (optional, needs GUI on droplet)

### Phase 3: Vast.ai Account Setup

- [ ] Sign up: https://vast.ai
- [ ] Verify email
- [ ] Add payment method
- [ ] Deposit $10 (minimum)
- [ ] Browse GPU marketplace

### Phase 4: First GPU Rental (Test Run)

- [ ] Search for RTX 3060 (cheapest for testing)
- [ ] Filter: DLPerf ≥ 50, Disk ≥ 50GB
- [ ] Select template: `parsec-ubuntu-20.04`
- [ ] Launch instance
- [ ] Connect via SSH
- [ ] Test FFmpeg: `ffmpeg -version`
- [ ] Test GPU: `nvidia-smi`
- [ ] **IMPORTANT:** Stop instance when done! (Go to Instances → Stop)

### Phase 5: Integration Test

- [ ] Upload sample video to Vast.ai instance
- [ ] Process video with FFmpeg
- [ ] Download result to local machine
- [ ] Upload result to droplet or Supabase
- [ ] Calculate total cost for workflow

---

## 📚 Part 8: Resources & Commands Cheat Sheet

### Quick Commands

```bash
# === DROPLET (137.184.1.91) ===

# Check running services
ps aux | grep streamlit
docker ps

# Check disk space
df -h

# Check memory
free -h

# === VAST.AI GPU INSTANCE ===

# Check GPU status
nvidia-smi
watch -n 1 nvidia-smi  # Live monitoring

# Convert video to smaller file
ffmpeg -i input.mp4 -c:v libx265 -crf 28 output.mp4

# Extract audio
ffmpeg -i video.mp4 -vn audio.wav

# Extract frames
ffmpeg -i video.mp4 -vf fps=1 frame_%04d.png

# Check Python GPU support
python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# === FILE TRANSFER ===

# Upload to Vast.ai
scp -P <port> file.mp4 root@ssh.vast.ai:/workspace/

# Download from Vast.ai
scp -P <port> root@ssh.vast.ai:/workspace/output.mp4 ./

# Upload to Droplet
scp file.mp4 root@137.184.1.91:/root/uploads/

# === COST MANAGEMENT ===

# Check Vast.ai balance
# Go to: https://vast.ai/console/billing

# Stop instance (IMPORTANT!)
# Go to: https://vast.ai/console/instances → Stop

# View spending history
# https://vast.ai/console/billing/history
```

### Important URLs

- **DigitalOcean Dashboard:** https://cloud.digitalocean.com/
- **Vast.ai Console:** https://vast.ai/console/
- **Parsec Dashboard:** https://parsec.app/dashboard
- **Supabase Dashboard:** https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu
- **ASEAGI Dashboards:** http://137.184.1.91:8501-8507

### Support & Documentation

- **Vast.ai Docs:** https://vast.ai/docs/
- **Parsec Support:** https://support.parsec.app/
- **FFmpeg Docs:** https://ffmpeg.org/documentation.html
- **CUDA Installation:** https://developer.nvidia.com/cuda-downloads

---

## ⚠️ Important Warnings

### 1. **ALWAYS STOP VAST.AI INSTANCES!**

```
⚠️ CRITICAL: Vast.ai charges per minute while running.
Forgetting to stop = $50+ surprise bill!

TO STOP:
1. Go to https://vast.ai/console/instances
2. Click "STOP" on your instance
3. Verify status shows "stopped"
```

### 2. **Backup Before Heavy Processing**

```bash
# Backup droplet before major changes
# DigitalOcean Dashboard → Droplet → Snapshots → Take Snapshot
```

### 3. **Secure Your Credentials**

```bash
# Never commit credentials to git
echo "SUPABASE_KEY=your_key" >> ~/.env
echo ".env" >> .gitignore

# Use environment variables
export SUPABASE_URL="https://jvjlhxodmbkodzmggwpu.supabase.co"
export SUPABASE_KEY="your_key"
```

### 4. **Monitor Vast.ai Spending**

- Set budget alerts in Vast.ai dashboard
- Check balance before long renders
- Stop instances immediately after use

---

## 🎯 Next Steps

1. **Today:** Set up Parsec on your local machine
2. **This Week:** Rent first Vast.ai GPU for test render (budget: $2)
3. **This Month:** Optimize droplet for video workflows
4. **Future:** Automate video processing pipeline

---

**Questions?** Check the troubleshooting section or create an issue in the ASEAGI repository.

**Last Updated:** November 11, 2025
