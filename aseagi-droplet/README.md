# ASEAGI Droplet Deployment
## Hybrid Cloud: Vast.ai GPU + DigitalOcean Services

**Quick Deploy:** Mac Mini → DigitalOcean Droplet

---

## 🚀 Quick Start (5 Minutes)

### On Your Mac Mini

```bash
# 1. Clone this repo
git clone https://github.com/yourusername/aseagi-droplet.git
cd aseagi-droplet

# 2. Setup environment
cp .env.example .env
nano .env  # Add your credentials

# 3. Build Docker image for Vast.ai
cd vastai
./build_and_push.sh

# 4. Deploy to Droplet
cd ..
./scripts/deploy.sh
```

---

## 💰 Cost Summary

| Service | Monthly Cost | Purpose |
|---------|--------------|---------|
| DigitalOcean Droplet | $24 | Control plane + dashboard |
| DO Spaces (250GB) | $5 | Document storage |
| Vast.ai GPU | ~$32 | On-demand processing |
| Supabase | $25 | Database |
| **TOTAL** | **$86/month** | **vs $800 GPU droplet** |

**Savings: $714/month = $8,568/year**

---

## 🏗️ Architecture

```
Telegram → Droplet → S3 Spaces
             ↓
         Vast.ai GPU (on-demand)
             ↓
         Supabase → Droplet Dashboard
```

---

## 📦 What's Included

### Droplet Services (Always Running)
- ✅ Flask API (control plane)
- ✅ Streamlit dashboard (monitoring)
- ✅ Telegram bot (webhook mode)
- ✅ Nginx (reverse proxy + SSL)

### Vast.ai Worker (On-Demand)
- ✅ GPU-accelerated OCR
- ✅ Claude Vision analysis
- ✅ Auto-scales to zero
- ✅ S3 integration

### Storage
- ✅ DigitalOcean Spaces (cold storage)
- ✅ Supabase (metadata)
- ✅ No local storage on Vast.ai

---

## 📝 Files

```
aseagi-droplet/
├── app/                    # Flask control plane
├── dashboard/              # Streamlit monitoring
├── vastai/                 # Docker for GPU processing
├── scripts/                # Deployment automation
└── nginx/                  # Web server config
```

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

---

## 🎯 Workflows

### Upload Document
```bash
# Via Telegram
Send photo → Bot uploads to S3 → Creates job → Vast.ai processes

# Via Dashboard
Upload file → S3 → Queue job → Vast.ai processes
```

### View Documents
```bash
# Open dashboard
https://your-droplet-ip:8501

# All documents visible (no GPU needed)
```

### Bulk Processing
```bash
# Upload folder to S3
rclone sync /local/folder spaces:aseagi-documents/raw/

# Click "Process All" in dashboard
# Vast.ai instance auto-launches
# Processes all docs
# Auto-destroys when done
```

---

## 🔐 Security

- ✅ HTTPS/SSL (Let's Encrypt)
- ✅ Telegram webhook (HTTPS only)
- ✅ S3 signed URLs (temp access)
- ✅ Supabase RLS (row-level security)
- ✅ No data stored on Vast.ai

---

## 📊 Monitoring

Dashboard shows:
- Real-time job status
- Vast.ai instance health
- Cost tracking
- Document browser
- Processing logs

---

## 🚀 Next Steps

1. **Setup Droplet:** [docs/DROPLET_SETUP.md](docs/DROPLET_SETUP.md)
2. **Configure S3:** [docs/SPACES_SETUP.md](docs/SPACES_SETUP.md)
3. **Deploy Services:** [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
4. **Test Processing:** [docs/TESTING.md](docs/TESTING.md)

---

**Ready?** Run `./scripts/deploy.sh` and you're live in 10 minutes.
