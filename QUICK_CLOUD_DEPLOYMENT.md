# 🚀 Quick Cloud-Hybrid Deployment Checklist

**You have cloud service API keys - this is the BEST option!**

---

## 📋 Step 1: Gather Your Credentials

You need these 5 things:

### 1. Supabase ✅ (You already have this!)
```
SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
SUPABASE_KEY=eyJhbGci... (from your existing .env)
```

### 2. Telegram Bot Token
- Get from: @BotFather on Telegram
- Format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### 3. Qdrant Cloud
- Dashboard: https://cloud.qdrant.io/
- Need:
  - Cluster URL: `https://xyz-abc.us-east-1-0.aws.cloud.qdrant.io:6333`
  - API Key: `qdrant_...`

### 4. Neo4j Aura
- Dashboard: https://console.neo4j.io/
- Need:
  - URI: `neo4j+s://abc123.databases.neo4j.io`
  - User: `neo4j` (default)
  - Password: (what you set when creating instance)

### 5. n8n Cloud (Optional)
- Dashboard: https://app.n8n.cloud/
- Need:
  - URL: `https://yourname.app.n8n.cloud`
  - API Key: (from Settings → API)

---

## 📝 Step 2: Create .env File on Droplet

### Connect to your droplet:
```bash
ssh root@137.184.1.91
cd /opt/ASEAGI
```

### Generate Redis password:
```bash
REDIS_PASSWORD=$(openssl rand -base64 32)
echo "Generated Redis Password: $REDIS_PASSWORD"
# COPY THIS PASSWORD!
```

### Create .env file:
```bash
# Backup existing .env first
cp .env .env.backup

# Create new .env with all credentials
nano .env
```

### Paste this configuration (fill in your actual values):

```bash
# ============================================================================
# ASEAGI CLOUD-HYBRID CONFIGURATION
# ============================================================================

# SUPABASE (from your existing .env)
SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
SUPABASE_KEY=paste-your-actual-supabase-key-here

# TELEGRAM BOT
TELEGRAM_BOT_TOKEN=paste-your-telegram-bot-token-here

# REDIS (local cache - use generated password from above)
REDIS_PASSWORD=paste-generated-redis-password-here

# QDRANT CLOUD
QDRANT_URL=https://your-cluster.us-east-1-0.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=paste-your-qdrant-api-key-here

# NEO4J AURA
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=paste-your-neo4j-password-here

# N8N CLOUD (optional - leave blank if not using)
N8N_URL=https://yourname.app.n8n.cloud
N8N_API_KEY=paste-your-n8n-api-key-here

# SYSTEM
DOMAIN=137.184.1.91
TIMEZONE=America/Los_Angeles
API_HOST=0.0.0.0
API_PORT=8000
API_BASE_URL=http://api:8000
CORS_ORIGINS=*

# OPTIONAL - AI APIs (if you have them)
OPENAI_API_KEY=sk-your-openai-key-if-you-have-one
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-if-you-have-one
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

---

## 🚀 Step 3: Pull Latest Code and Deploy

```bash
# Pull the cloud-hybrid deployment files
git pull origin claude/create-truth-score-charts-011CUqV28kW1jcpJE1z2B5rM

# Stop any existing deployment
docker compose down

# Deploy cloud-hybrid stack (only 4 containers!)
docker-compose -f docker-compose.cloud.yml up -d

# Watch the deployment
docker-compose -f docker-compose.cloud.yml logs -f
```

**Wait for:** All containers to show "healthy" status (about 2 minutes)

Press `Ctrl+C` to stop watching logs.

---

## ✅ Step 4: Verify Deployment

### Check containers are running:
```bash
docker-compose -f docker-compose.cloud.yml ps
```

**Expected output:**
```
NAME                STATUS              PORTS
aseagi-api          Up (healthy)        0.0.0.0:8000->8000/tcp
aseagi-telegram     Up
aseagi-dashboard    Up (healthy)        0.0.0.0:80->8501/tcp
aseagi-redis        Up (healthy)        0.0.0.0:6379->6379/tcp
```

**Notice:** Only 4 containers! (Not 8 like full self-hosted)

### Test API:
```bash
curl http://localhost:8000/health
```

**Expected:** `{"status": "healthy"}`

### Check cloud connections:
```bash
# Check Qdrant connection
docker logs aseagi-api 2>&1 | grep -i qdrant

# Check Neo4j connection
docker logs aseagi-api 2>&1 | grep -i neo4j

# Should see successful connection messages!
```

### Test Telegram Bot:
1. Open Telegram app
2. Find your bot
3. Send: `/start`
4. Should get welcome message! ✅

### Test Dashboard:
1. Open browser: `http://137.184.1.91`
2. Should see ASEAGI dashboard! ✅

---

## 📊 What You Just Deployed

### LOCAL (on your droplet):
- ✅ FastAPI (port 8000)
- ✅ Telegram Bot
- ✅ Streamlit Dashboard (port 80)
- ✅ Redis Cache (port 6379)

### CLOUD (managed services):
- ☁️ Qdrant Cloud (vector search)
- ☁️ Neo4j Aura (graph database)
- ☁️ Supabase (PostgreSQL)
- ☁️ n8n Cloud (workflows - optional)

### Resource Usage:
- **RAM:** ~4GB (you have 16GB available)
- **CPU:** ~25% (plenty of room)
- **Disk:** ~5GB

---

## 🔧 Step 5: Set Up n8n Workflows (Optional)

### If using n8n Cloud:
1. Go to: https://app.n8n.cloud/
2. Create new workflow
3. Import JSON files from: `/opt/ASEAGI/n8n-workflows/`
4. Configure to call: `http://137.184.1.91:8000/telegram/*`

### If self-hosting n8n:
Use `docker-compose.full.yml` instead (adds n8n container locally)

**See:** `N8N_SETUP_GUIDE.md` for detailed instructions

---

## 🚨 Troubleshooting

### Problem: API won't start
```bash
# Check logs
docker logs aseagi-api

# Common issue: Missing .env variable
# Solution: Check .env file has all required variables
```

### Problem: Can't connect to Qdrant Cloud
```bash
# Test connection manually
curl -X GET "https://your-cluster.cloud.qdrant.io:6333/collections" \
  -H "api-key: your-api-key"

# Should return: {"result": {"collections": []}}
```

### Problem: Can't connect to Neo4j Aura
```bash
# Test with cypher-shell
docker run --rm -it neo4j:5-community \
  cypher-shell -a "neo4j+s://your-instance.databases.neo4j.io" \
  -u neo4j -p "your-password" \
  "RETURN 'Hello' AS message"

# Should return: Hello
```

### Problem: Telegram bot not responding
```bash
# Check bot logs
docker logs aseagi-telegram

# Check bot token
cat .env | grep TELEGRAM_BOT_TOKEN

# Restart bot
docker-compose -f docker-compose.cloud.yml restart telegram
```

---

## 🎯 Next Steps After Deployment

### 1. Test Telegram Bot Commands:
```
/start       - Welcome message
/help        - Available commands
/timeline    - Recent case events
/actions     - Pending tasks
/violations  - Legal violations
/deadline    - Upcoming deadlines
/search      - Search documents
```

### 2. Populate Qdrant with Embeddings:
- Upload document embeddings
- Create collections
- Test similarity search

### 3. Build Neo4j Graph:
- Import party relationships
- Link case events
- Map document connections

### 4. Configure n8n Workflows:
- Import 3 pre-made workflows
- Set up daily reports
- Enable violation monitoring

---

## 📊 Cost Breakdown

| Service | Cost | Notes |
|---------|------|-------|
| DigitalOcean Droplet (16GB) | $96/mo | Your base infrastructure |
| Qdrant Cloud | FREE | 1GB free tier |
| Neo4j Aura | FREE | AuraDB Free (200k nodes) |
| Supabase | FREE | Your existing account |
| n8n Cloud | $20/mo | Optional (can self-host) |
| **Total** | **$96-116/mo** | Managed + reliable |

**vs Self-Hosted Everything:** Same $96/mo but uses 8GB RAM and requires manual maintenance

---

## ✅ Deployment Success Checklist

Before you're done, confirm:

- [ ] All 4 containers running: `docker ps | grep aseagi`
- [ ] API health check passes: `curl http://localhost:8000/health`
- [ ] Telegram bot responds to `/start`
- [ ] Dashboard loads at: `http://137.184.1.91`
- [ ] Qdrant connection works: `docker logs aseagi-api | grep -i qdrant`
- [ ] Neo4j connection works: `docker logs aseagi-api | grep -i neo4j`
- [ ] Redis cache working: `docker logs aseagi-redis`

---

## 📞 Support Resources

- **ASEAGI API Docs:** `http://137.184.1.91:8000/docs`
- **Qdrant Cloud:** https://qdrant.tech/documentation/
- **Neo4j Aura:** https://aura.support.neo4j.com/
- **n8n Cloud:** https://community.n8n.io/
- **Detailed Guides:**
  - `CLOUD_SERVICES_INTEGRATION.md` - Full cloud setup guide
  - `N8N_SETUP_GUIDE.md` - n8n workflow setup
  - `DEPLOYMENT_OPTIONS_GUIDE.md` - All deployment options

---

**For Ashe. For Justice. For All Children.** 🛡️

---

## 🎬 Ready to Deploy?

**On your Mac, you can copy this to your droplet:**
```bash
# Pull latest code on droplet
ssh root@137.184.1.91 "cd /opt/ASEAGI && git pull origin claude/create-truth-score-charts-011CUqV28kW1jcpJE1z2B5rM"
```

**Then SSH in and follow Steps 2-4 above!**

**When you have your cloud credentials ready, just paste them into the .env file and deploy!**
