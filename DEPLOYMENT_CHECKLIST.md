# ASEAGI Deployment Checklist

**Complete deployment guide for Digital Ocean droplet with batch processing system**

This checklist walks you through deploying the entire ASEAGI system to your Digital Ocean droplet, including the Telegram bot API, batch processor, and all supporting services.

---

## 🎯 Overview

### What You're Deploying

**Services:**
1. **FastAPI Telegram Bot + Web Interface** (port 8000)
2. **Batch Processor** (port 8001) - for 7TB Google Drive processing
3. **Redis** (port 6379) - job queue
4. **Nginx** (ports 80/443) - reverse proxy (optional, production)

**Infrastructure:**
- Digital Ocean Droplet (orchestration + API)
- Vast.ai GPU instances (batch processing)
- Supabase (database)
- N8N Cloud (workflow automation)
- Google Drive (7TB document storage)

---

## ✅ Pre-Deployment Checklist

### 1. Digital Ocean Droplet

- [ ] Droplet created and accessible via SSH
- [ ] Minimum specs: 2 GB RAM, 50 GB disk, 1 vCPU
- [ ] Ubuntu 22.04 LTS installed
- [ ] SSH key configured
- [ ] Firewall rules configured:
  - Port 22 (SSH)
  - Port 80 (HTTP)
  - Port 443 (HTTPS)
  - Port 8000 (API)
  - Port 8001 (Batch Processor)

**Test connectivity:**
```bash
ssh root@YOUR_DROPLET_IP
```

---

### 2. API Keys and Credentials

Collect all required API keys and credentials:

#### Supabase
- [ ] Project URL: `https://jvjlhxodmbkodzmggwpu.supabase.co`
- [ ] Anon/Public key from Supabase dashboard

#### Vast.ai
- [ ] Account created at https://vast.ai/
- [ ] $100 credit added
- [ ] API key from Account → API Keys

#### Claude API
- [ ] API key from https://console.anthropic.com/
- [ ] Account has credits

#### Google Drive
- [ ] Google Cloud project created
- [ ] Google Drive API enabled
- [ ] OAuth2 credentials created and downloaded (`credentials.json`)

#### Telegram Bot (if using)
- [ ] Bot created via @BotFather
- [ ] Bot token saved

#### N8N Cloud (if using)
- [ ] Account created at https://n8n.io/
- [ ] Workflow created for Telegram bot

---

### 3. Local Files Ready

- [ ] `credentials.json` (Google OAuth2)
- [ ] `.env` file with all secrets
- [ ] SSH access to Digital Ocean droplet
- [ ] Git repository cloned

---

## 🚀 Deployment Steps

### Step 1: Prepare Digital Ocean Droplet

**SSH into your droplet:**

```bash
ssh root@YOUR_DROPLET_IP
```

**Update system:**

```bash
apt update && apt upgrade -y
```

**Install Docker and Docker Compose:**

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Verify installation
docker --version
docker-compose --version
```

**Install Git:**

```bash
apt install git -y
```

---

### Step 2: Clone Repository

**Clone ASEAGI repository to droplet:**

```bash
cd /opt
git clone https://github.com/dondada876/ASEAGI.git
cd ASEAGI

# Checkout the feature branch
git checkout claude/fix-scatter-plot-size-error-011CUqVMtQbyPHjuZaDcwco3
```

---

### Step 3: Configure Environment Variables

**Create `.env` file:**

```bash
cd /opt/ASEAGI/telegram-bot
nano .env
```

**Add the following (replace with your actual values):**

```bash
# Supabase
SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
SUPABASE_KEY=your-supabase-anon-key-here

# Vast.ai
VAST_AI_API_KEY=your-vastai-api-key-here

# Claude API
CLAUDE_API_KEY=your-claude-api-key-here

# Telegram Bot (if using)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here

# Google Drive
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/credentials.json
```

**Save and exit:** `Ctrl+X`, then `Y`, then `Enter`

---

### Step 4: Upload Google Drive Credentials

**Create credentials directory:**

```bash
mkdir -p /opt/ASEAGI/telegram-bot/credentials
```

**Upload `credentials.json` from your local machine:**

```bash
# From your LOCAL machine (not the droplet)
scp /path/to/credentials.json root@YOUR_DROPLET_IP:/opt/ASEAGI/telegram-bot/credentials/
```

**Verify file exists:**

```bash
# Back on the droplet
ls -la /opt/ASEAGI/telegram-bot/credentials/
```

---

### Step 5: Build and Start Services

**Navigate to telegram-bot directory:**

```bash
cd /opt/ASEAGI/telegram-bot
```

**Build Docker images:**

```bash
docker-compose build
```

This will take 5-10 minutes. It builds:
- FastAPI Telegram bot + web interface
- Batch processor

**Start all services:**

```bash
docker-compose up -d
```

**Check service status:**

```bash
docker-compose ps
```

Expected output:
```
NAME                        STATUS              PORTS
aseagi-telegram-api         Up (healthy)        0.0.0.0:8000->8000/tcp
aseagi-batch-processor      Up (healthy)        0.0.0.0:8001->8001/tcp
aseagi-redis                Up (healthy)        0.0.0.0:6379->6379/tcp
```

---

### Step 6: Verify Deployment

**Check API health:**

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-11-07T12:00:00"
}
```

**Check batch processor health:**

```bash
curl http://localhost:8001/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-07T12:00:00",
  "batch_manager_initialized": true
}
```

**Check schema validation:**

```bash
curl http://localhost:8000/schema/validate
```

Should show all NON-NEGOTIABLE tables validated successfully.

**Check Vast.ai balance:**

```bash
curl http://localhost:8001/vastai/balance
```

Should show your $100 balance.

---

### Step 7: Test Batch Processor with Small Batch

**Authenticate Google Drive (first time only):**

This requires a browser, so you'll need to run it locally first or use SSH port forwarding:

```bash
# From your LOCAL machine
ssh -L 8001:localhost:8001 root@YOUR_DROPLET_IP

# Then access http://localhost:8001/docs in your browser
```

**Start test batch (10 documents):**

```bash
curl -X POST http://localhost:8001/batch/start \
  -H "Content-Type: application/json" \
  -d '{
    "max_documents": 10,
    "batch_size": 10,
    "max_cost_per_hour": 1.0
  }'
```

**Monitor progress:**

```bash
watch -n 5 curl http://localhost:8001/batch/status
```

**Check logs:**

```bash
docker-compose logs -f batch-processor
```

---

### Step 8: Configure Nginx (Production Only)

**Create Nginx configuration directory:**

```bash
mkdir -p /opt/ASEAGI/telegram-bot/nginx
```

**Create Nginx config:**

```bash
nano /opt/ASEAGI/telegram-bot/nginx/nginx.conf
```

**Add configuration:**

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    upstream batch-processor {
        server batch-processor:8001;
    }

    # HTTP → HTTPS redirect
    server {
        listen 80;
        server_name YOUR_DOMAIN.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name YOUR_DOMAIN.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        # API endpoints
        location / {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # Batch processor endpoints
        location /batch/ {
            proxy_pass http://batch-processor;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

**Get SSL certificate (Let's Encrypt):**

```bash
apt install certbot -y

certbot certonly --standalone -d YOUR_DOMAIN.com

# Certificates will be in:
# /etc/letsencrypt/live/YOUR_DOMAIN.com/fullchain.pem
# /etc/letsencrypt/live/YOUR_DOMAIN.com/privkey.pem
```

**Copy certificates to nginx directory:**

```bash
mkdir -p /opt/ASEAGI/telegram-bot/nginx/ssl
cp /etc/letsencrypt/live/YOUR_DOMAIN.com/fullchain.pem /opt/ASEAGI/telegram-bot/nginx/ssl/
cp /etc/letsencrypt/live/YOUR_DOMAIN.com/privkey.pem /opt/ASEAGI/telegram-bot/nginx/ssl/
```

**Start Nginx:**

```bash
cd /opt/ASEAGI/telegram-bot
docker-compose --profile production up -d nginx
```

---

### Step 9: Set Up N8N Workflows

**Sign up for N8N Cloud:**

1. Go to https://n8n.io/
2. Create account ($20/mo plan)
3. Create new workflow

**Import Workflow 1 (Telegram Bot Handler):**

1. Copy JSON from `N8N_WORKFLOW_GUIDE.md` → Workflow 1
2. In N8N: Create → Import from JSON
3. Configure Telegram trigger with your bot token
4. Configure HTTP request node with your droplet IP
5. Activate workflow

**Test Telegram bot:**

```bash
# From Telegram app
/status
/events
/documents
```

---

### Step 10: Start Full 7TB Processing

**Verify everything is ready:**

```bash
# Check Vast.ai balance
curl http://localhost:8001/vastai/balance

# Estimate cost
curl "http://localhost:8001/batch/estimate?total_documents=70000"

# Check Google Drive connection
curl "http://localhost:8001/drive/documents?max_results=10"
```

**Start full batch processing:**

```bash
curl -X POST http://localhost:8001/batch/start \
  -H "Content-Type: application/json" \
  -d '{
    "mime_types": ["application/pdf"],
    "batch_size": 100,
    "max_cost_per_hour": 1.0
  }'
```

**Expected output:**

```json
{
  "session_id": "batch_session_1699358400",
  "status": "running",
  "total_documents": 70000,
  "total_batches": 700,
  "estimated_completion": "2025-11-11T00:00:00",
  "total_cost": 44.0
}
```

**Monitor progress:**

```bash
# Every 5 minutes
watch -n 300 curl http://localhost:8001/batch/status
```

**View logs:**

```bash
docker-compose logs -f batch-processor
```

---

## 📊 Post-Deployment Monitoring

### Service Health Checks

**Check all services:**

```bash
docker-compose ps
docker-compose logs --tail=50
```

**Test API endpoints:**

```bash
# Telegram API
curl http://localhost:8000/health
curl http://localhost:8000/telegram/status

# Batch Processor
curl http://localhost:8001/health
curl http://localhost:8001/batch/status

# Schema Validation
curl http://localhost:8000/schema/validate
```

---

### Database Verification

**Check processed documents:**

```bash
curl -X POST http://localhost:8000/telegram/status
```

**Query Supabase directly:**

```sql
-- Go to Supabase dashboard → SQL Editor

-- Check total documents
SELECT
    processing_status,
    COUNT(*) as count
FROM document_journal
GROUP BY processing_status;

-- Check recent events
SELECT *
FROM events
ORDER BY event_date DESC
LIMIT 10;

-- Check communications
SELECT *
FROM communications
ORDER BY communication_date DESC
LIMIT 10;
```

---

### Cost Monitoring

**Check Vast.ai usage:**

```bash
curl http://localhost:8001/vastai/balance
```

**Track processing cost:**

Every 100 batches ≈ $6.25 spent

- Batch 100: ~$6.25 spent, $93.75 remaining
- Batch 200: ~$12.50 spent, $87.50 remaining
- Batch 700: ~$43.75 spent, $56.25 remaining

---

## 🛡️ Backup and Recovery

### Backup Strategy

**Checkpoint files (automatic):**

Saved every 10 batches in `/opt/ASEAGI/telegram-bot/batch_state/`

**Manual backup:**

```bash
# Backup checkpoint files
tar -czf aseagi-checkpoints-$(date +%Y%m%d).tar.gz /opt/ASEAGI/telegram-bot/batch_state/

# Upload to cloud storage
scp aseagi-checkpoints-*.tar.gz user@backup-server:/backups/
```

---

### Recovery from Checkpoint

**If processing stops:**

1. Check logs:
   ```bash
   docker-compose logs batch-processor | tail -100
   ```

2. List available checkpoints:
   ```bash
   curl http://localhost:8001/checkpoints
   ```

3. Resume from last checkpoint:
   ```bash
   curl -X POST http://localhost:8001/batch/resume/checkpoint_100.json
   ```

---

## 🔧 Troubleshooting

### Service Won't Start

**Check Docker logs:**

```bash
docker-compose logs api
docker-compose logs batch-processor
```

**Common issues:**

1. **Missing environment variables:**
   ```bash
   docker-compose config
   ```

2. **Port already in use:**
   ```bash
   netstat -tulpn | grep 8000
   netstat -tulpn | grep 8001
   ```

3. **Docker out of disk space:**
   ```bash
   df -h
   docker system prune -a
   ```

---

### Batch Processing Failed

**Check batch processor logs:**

```bash
docker-compose logs batch-processor
```

**Common issues:**

1. **Google Drive authentication failed:**
   - Verify `credentials.json` exists
   - Run OAuth flow locally first

2. **Vast.ai insufficient balance:**
   - Check balance: `curl http://localhost:8001/vastai/balance`
   - Add more credit at https://vast.ai/billing

3. **GPU instance crashed:**
   - Stop instance: `curl -X POST http://localhost:8001/batch/stop`
   - Resume from checkpoint

---

### Database Connection Issues

**Test Supabase connection:**

```bash
curl http://localhost:8000/schema/validate
```

**Check environment variables:**

```bash
docker exec aseagi-telegram-api env | grep SUPABASE
```

**Verify Supabase is accessible:**

```bash
curl https://jvjlhxodmbkodzmggwpu.supabase.co
```

---

## 📋 Maintenance

### Regular Tasks

**Weekly:**
- [ ] Check Docker container health: `docker-compose ps`
- [ ] Check disk space: `df -h`
- [ ] Check logs for errors: `docker-compose logs --tail=100`
- [ ] Backup checkpoint files

**Monthly:**
- [ ] Update Docker images: `docker-compose pull`
- [ ] Update system packages: `apt update && apt upgrade`
- [ ] Review Vast.ai spending
- [ ] Review Supabase storage usage

---

### Updating Deployment

**Pull latest changes:**

```bash
cd /opt/ASEAGI
git pull origin claude/fix-scatter-plot-size-error-011CUqVMtQbyPHjuZaDcwco3
```

**Rebuild and restart:**

```bash
cd /opt/ASEAGI/telegram-bot
docker-compose build
docker-compose up -d
```

**Verify update:**

```bash
docker-compose ps
curl http://localhost:8000/health
curl http://localhost:8001/health
```

---

## ✅ Deployment Complete!

### What You've Deployed

✅ **FastAPI Telegram Bot** - http://YOUR_DROPLET_IP:8000
✅ **Batch Processor API** - http://YOUR_DROPLET_IP:8001
✅ **Redis Job Queue** - running on port 6379
✅ **Docker Services** - all containers healthy
✅ **Nginx Reverse Proxy** - (if production profile enabled)

### Next Steps

1. **Test Telegram Bot** - Send `/status` command
2. **Test Batch Processor** - Start small batch (10 docs)
3. **Set Up N8N Workflows** - Automate Telegram bot responses
4. **Start 7TB Processing** - Run full batch (70,000 docs)
5. **Monitor Progress** - Check status every few hours

---

### Key URLs

- **API Health:** http://YOUR_DROPLET_IP:8000/health
- **API Docs:** http://YOUR_DROPLET_IP:8000/docs
- **Batch Processor Docs:** http://YOUR_DROPLET_IP:8001/docs
- **Web Dashboard:** http://YOUR_DROPLET_IP:8000/static/dashboard.html
- **Schema Validator:** http://YOUR_DROPLET_IP:8000/schema/validate

---

**For Ashe - Protecting children through intelligent legal assistance** ⚖️

*"Deployment is the bridge between planning and justice."*

---

**Version:** 1.0.0
**Status:** Production Ready
**Last Updated:** November 2025
