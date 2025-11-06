# 🎯 ASEAGI Deployment Options Guide
**Droplet:** `137.184.1.91`
**Date:** November 6, 2025

---

## 🤔 **Your Question: Do I Need Qdrant and n8n Setup First?**

**Short Answer:** ❌ **NO!** You don't need to configure them beforehand.

**Why?** Docker Compose handles all service setup automatically. You just need:
1. ✅ Supabase credentials (you have)
2. ✅ Telegram bot token (get from @BotFather)
3. ✅ Choose deployment option (minimal, standard, or full)

---

## 📊 **Service Dependency Matrix**

| Service | Required? | Auto-Setup? | Breaks System If Missing? | What It Does |
|---------|-----------|-------------|---------------------------|--------------|
| **Supabase** | ✅ YES | ❌ No (external) | ✅ YES | Database - ALL data |
| **FastAPI** | ✅ YES | ✅ Yes | ✅ YES | API backend |
| **Telegram Bot** | ✅ YES | ✅ Yes | ⚠️ Only bot | Bot client |
| **Redis** | ⚡ Recommended | ✅ Yes | ❌ NO | Cache (performance) |
| **Qdrant** | ⭐ Optional | ✅ Yes | ❌ NO | Vector search |
| **Neo4j** | ⭐ Optional | ✅ Yes | ❌ NO | Graph database |
| **n8n** | ⭐ Optional | ✅ Yes | ❌ NO | Automation |
| **Dashboards** | ⭐ Optional | ✅ Yes | ❌ NO | Web UI |

**Legend:**
- ✅ YES = System won't work without it
- ⚡ Recommended = Should include for best performance
- ⭐ Optional = Nice to have, not critical
- ❌ NO = System works fine without it

---

## 🚀 **Three Deployment Options**

### **Option 1: Minimal (Telegram Bot Only)** ⚡

**Services Deployed:**
```
✓ FastAPI (API backend)
✓ Telegram Bot (9 commands)
✓ Supabase (external - you have)
```

**Services NOT Deployed:**
```
✗ Redis (no cache)
✗ Qdrant (no vector search)
✗ Neo4j (no graph)
✗ n8n (no automation)
✗ Dashboards (web UI)
```

**Use Case:**
- Just want Telegram bot working
- Minimum complexity
- Testing before full deployment

**Pros:**
- ⚡ Fastest deployment (5 min)
- 💾 Lowest resource usage (2GB RAM)
- 🛡️ Least likely to break
- ✅ Telegram bot works perfectly

**Cons:**
- ⚠️ No web dashboards
- ⚠️ No automation
- ⚠️ Slower performance

**Command:**
```bash
# Create minimal compose file first (see below)
docker-compose -f docker-compose.minimal.yml up -d
```

---

### **Option 2: Standard (Recommended)** ⚖️ ✅

**Services Deployed:**
```
✓ FastAPI (API backend)
✓ Telegram Bot (9 commands)
✓ Redis (cache for speed)
✓ Streamlit Dashboards (web UI)
✓ Supabase (external)
```

**Services NOT Deployed:**
```
✗ Qdrant (can add later)
✗ Neo4j (can add later)
✗ n8n (can add later)
```

**Use Case:**
- Want Telegram bot + dashboards
- Good performance with cache
- Room to grow later

**Pros:**
- ⚡ Fast deployment (10-15 min)
- 💾 Moderate resources (4GB RAM)
- 🚀 Better performance (Redis)
- 📊 Web dashboards included
- ➕ Easy to add services later

**Cons:**
- ⚠️ No automation yet
- ⚠️ No vector/graph search yet

**Command:**
```bash
docker-compose -f docker-compose.standard.yml up -d
```

**✅ THIS IS MY RECOMMENDATION!**

---

### **Option 3: Full Stack** 🚀

**Services Deployed:**
```
✓ FastAPI (API backend)
✓ Telegram Bot (9 commands)
✓ Redis (cache)
✓ Streamlit Dashboards (web UI)
✓ Qdrant (vector search)
✓ Neo4j (graph database)
✓ n8n (automation)
✓ Nginx (reverse proxy)
✓ Supabase (external)
```

**Use Case:**
- Want ALL features
- Need automation
- Need advanced analytics
- Production deployment

**Pros:**
- 🎯 Complete system
- 🤖 Automation ready
- 🔍 Advanced search
- 📈 All analytics
- 🌐 Production-ready

**Cons:**
- ⏱️ Longer deployment (20-30 min)
- 💾 Higher resources (8GB RAM - you have 16GB ✅)
- 🔧 More complexity
- ⚠️ More services that could fail

**Command:**
```bash
docker-compose -f docker-compose.full.yml up -d
```

---

## 📋 **Deployment Comparison**

| Feature | Minimal | Standard ✅ | Full |
|---------|---------|------------|------|
| **Telegram Bot** | ✅ | ✅ | ✅ |
| **REST API** | ✅ | ✅ | ✅ |
| **Web Dashboards** | ❌ | ✅ | ✅ |
| **Redis Cache** | ❌ | ✅ | ✅ |
| **Vector Search** | ❌ | ❌ | ✅ |
| **Graph Database** | ❌ | ❌ | ✅ |
| **Automation (n8n)** | ❌ | ❌ | ✅ |
| **Setup Time** | 5 min | 15 min | 30 min |
| **RAM Usage** | 2GB | 4GB | 8GB |
| **Complexity** | Low | Medium | High |
| **Break Risk** | Low | Low | Medium |

---

## 🎯 **Recommended Path**

### **Start with Option 2 (Standard), Add Services Later**

**Phase 1: Standard Deployment (Today)**
```bash
# Deploy Telegram bot + Dashboards + Redis
docker-compose -f docker-compose.standard.yml up -d
```

**Phase 2: Add n8n When You Need Automation (Later)**
```bash
# Stop standard
docker-compose -f docker-compose.standard.yml down

# Deploy with n8n added
docker-compose -f docker-compose.with-n8n.yml up -d
```

**Phase 3: Add Qdrant/Neo4j When You Need Advanced Analytics (Later)**
```bash
# Deploy full stack
docker-compose -f docker-compose.full.yml up -d
```

---

## 🔧 **Prerequisites for Each Option**

### **For ALL Options:**
```
✅ Supabase credentials (you have)
✅ Telegram bot token (get from @BotFather)
✅ Docker installed (you have)
✅ .env file configured
```

### **For Option 1 (Minimal):**
```
No additional prerequisites!
```

### **For Option 2 (Standard):**
```
✅ Generate Redis password (1 command)
```

### **For Option 3 (Full):**
```
✅ Generate Redis password
✅ Generate Neo4j password
✅ Generate n8n password
✅ Open additional firewall ports (5678, 6333, 7474)
```

---

## 🚀 **Step-by-Step: Deploy Standard (Recommended)**

### **Step 1: Get Telegram Bot Token (5 min)**

```bash
# On your phone/computer:
1. Open Telegram
2. Message: @BotFather
3. Send: /newbot
4. Name: ASEAGI Case Manager
5. Username: aseagi_yourname_bot
6. Copy token: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

---

### **Step 2: Connect to Droplet**

```bash
ssh root@137.184.1.91
cd /opt/ASEAGI
```

---

### **Step 3: Verify You're on Correct Branch**

```bash
git status
# Should show: On branch claude/create-truth-score-charts-011CUqV28kW1jcpJE1z2B5rM

# If not:
git checkout claude/create-truth-score-charts-011CUqV28kW1jcpJE1z2B5rM
```

---

### **Step 4: Pull Latest Code (with docker-compose.standard.yml)**

```bash
git pull origin claude/create-truth-score-charts-011CUqV28kW1jcpJE1z2B5rM
```

---

### **Step 5: Generate Redis Password**

```bash
echo "REDIS_PASSWORD=$(openssl rand -base64 32)"
# Copy this password!
```

---

### **Step 6: Configure .env File**

```bash
nano .env
```

**Paste (replace with YOUR values):**

```bash
# ============================================================
# ASEAGI STANDARD DEPLOYMENT CONFIGURATION
# ============================================================

# SUPABASE (Required)
SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
SUPABASE_KEY=your-existing-supabase-anon-key

# TELEGRAM BOT (Required)
TELEGRAM_BOT_TOKEN=paste-your-bot-token-from-botfather

# API CONFIGURATION
API_HOST=0.0.0.0
API_PORT=8000
API_BASE_URL=http://api:8000
CORS_ORIGINS=*

# REDIS (Required for Standard)
REDIS_PASSWORD=paste-generated-redis-password

# DOMAIN
DOMAIN=137.184.1.91
TIMEZONE=America/Los_Angeles

# OPTIONAL - AI Keys (if you have them)
OPENAI_API_KEY=sk-your-key-if-you-have-one
ANTHROPIC_API_KEY=sk-ant-your-key-if-you-have-one
```

**Save:** `Ctrl+X`, `Y`, `Enter`

---

### **Step 7: Stop Current Deployment**

```bash
docker compose down
```

---

### **Step 8: Deploy Standard Stack**

```bash
docker-compose -f docker-compose.standard.yml up -d
```

**What happens:**
```
[+] Running 5/5
 ✔ Network aseagi-network   Created
 ✔ Container aseagi-redis    Started
 ✔ Container aseagi-api      Started
 ✔ Container aseagi-telegram Started
 ✔ Container aseagi-dashboard Started
```

**Wait 5-10 minutes for initial setup...**

---

### **Step 9: Verify Deployment**

```bash
docker-compose -f docker-compose.standard.yml ps
```

**Expected output:**
```
NAME                STATUS              PORTS
aseagi-api          Up (healthy)        0.0.0.0:8000->8000/tcp
aseagi-telegram     Up
aseagi-dashboard    Up (healthy)        0.0.0.0:80->8501/tcp
aseagi-redis        Up (healthy)        0.0.0.0:6379->6379/tcp
```

✅ **All "Up" = Success!**

---

### **Step 10: Test Everything**

#### **Test API:**
```bash
curl http://localhost:8000/health
```

**Expected:**
```json
{"status":"healthy","service":"ASEAGI API"}
```

#### **Test Telegram Bot:**
1. Open Telegram on phone
2. Find your bot
3. Send: `/start`
4. **Expected:** Welcome message! ✅

#### **Test Dashboard:**
- Open browser: `http://137.184.1.91`
- **Expected:** Streamlit dashboard loads ✅

---

## ✅ **What You Get with Standard Deployment**

### **Access URLs:**
```
API:        http://137.184.1.91:8000
API Docs:   http://137.184.1.91:8000/docs
Dashboard:  http://137.184.1.91
Telegram:   (message your bot from anywhere!)
```

### **Telegram Bot Commands:**
```
/start       - Welcome message
/help        - Show all commands
/search      - Search communications
/timeline    - Show case events
/actions     - Show pending tasks
/violations  - Show legal violations
/deadline    - Show upcoming deadlines
/report      - Daily summary
/hearing     - Show hearings
/motion      - Generate motion outline
```

### **Resource Usage:**
```
RAM:  ~4GB / 16GB (25% usage)
CPU:  2-4 cores (moderate)
Disk: ~10GB
```

---

## ➕ **Adding Services Later**

### **To Add n8n Later:**

1. Edit `.env`, add:
   ```bash
   N8N_PASSWORD=$(openssl rand -base64 32)
   N8N_USER=admin
   ```

2. Update firewall:
   ```bash
   ufw allow 5678/tcp
   ```

3. Deploy with n8n:
   ```bash
   # Create docker-compose.with-n8n.yml or use full
   docker-compose -f docker-compose.full.yml up -d n8n
   ```

### **To Add Qdrant Later:**

```bash
# Add to existing deployment
docker-compose -f docker-compose.full.yml up -d qdrant
```

### **To Add Neo4j Later:**

1. Add to `.env`:
   ```bash
   NEO4J_PASSWORD=$(openssl rand -base64 32)
   ```

2. Deploy:
   ```bash
   docker-compose -f docker-compose.full.yml up -d neo4j
   ```

---

## 🚨 **Troubleshooting**

### **Problem: Container won't start**

```bash
# Check logs
docker logs aseagi-api
docker logs aseagi-telegram

# Common issues:
# - Missing .env variable
# - Wrong Supabase credentials
# - Wrong bot token
```

**Fix:**
```bash
# Edit .env and fix credentials
nano .env

# Restart
docker-compose -f docker-compose.standard.yml restart
```

---

### **Problem: Telegram bot not responding**

```bash
# Check bot logs
docker logs aseagi-telegram

# Check if API is accessible
curl http://localhost:8000/health
```

**Common causes:**
- Wrong bot token in .env
- API not running
- Bot can't reach API

**Fix:**
```bash
# Verify token
cat .env | grep TELEGRAM_BOT_TOKEN

# Restart bot
docker-compose -f docker-compose.standard.yml restart telegram
```

---

### **Problem: Out of memory**

```bash
# Check usage
free -h
docker stats
```

**Solution:**
- Option 1: Use Minimal deployment (2GB)
- Option 2: Add swap space
- Option 3: Upgrade droplet

---

## 📊 **Decision Helper**

### **Choose Minimal If:**
- ✅ You just want to test Telegram bot
- ✅ You have limited resources
- ✅ You don't need dashboards yet

### **Choose Standard If:** ✅ **RECOMMENDED**
- ✅ You want Telegram bot + dashboards
- ✅ You want good performance (Redis)
- ✅ You might add services later
- ✅ You have 16GB RAM (you do!)

### **Choose Full If:**
- ✅ You need automation NOW
- ✅ You need vector/graph search NOW
- ✅ You're ready for full complexity
- ✅ You have 16GB+ RAM

---

## 📝 **Quick Reference**

### **Deploy Standard (Recommended):**
```bash
ssh root@137.184.1.91
cd /opt/ASEAGI
git pull
nano .env  # Configure
docker compose down
docker-compose -f docker-compose.standard.yml up -d
```

### **Deploy Full:**
```bash
docker-compose -f docker-compose.full.yml up -d
```

### **Check Status:**
```bash
docker-compose -f docker-compose.standard.yml ps
```

### **View Logs:**
```bash
docker-compose -f docker-compose.standard.yml logs -f
```

---

## ✅ **Summary**

**Your Question:** "Do I need to setup Qdrant and n8n first?"

**Answer:** ❌ **No!**
- Docker Compose sets them up automatically
- Start with **Standard deployment** (no Qdrant/n8n)
- Add them later if needed
- System won't break without them

**Recommended:** Deploy Standard today, add services later as needed.

---

**For Ashe. For Justice. For All Children.** 🛡️
