# ☁️ Cloud Services Integration Guide
**Using Qdrant Cloud, Neo4j Aura, and n8n Cloud with ASEAGI**

---

## 🎉 **Excellent Choice! Cloud Services Are Better**

You mentioned you have API keys for:
- ✅ Qdrant
- ✅ Neo4j
- ✅ n8n

This is **BETTER** than self-hosting because:
- 💾 Uses less RAM on your droplet (4GB vs 8GB)
- 🚀 Better performance (dedicated infrastructure)
- 🔒 Managed backups and security
- 📈 Easy to scale
- 🛠️ Professional support

---

## 🤔 **First: Clarify Your Services**

### **Are these cloud services or self-hosted?**

#### **Option A: Cloud Services** ✅ **Recommended**

**Qdrant Cloud**
- URL format: `https://xyz123.us-east-1-0.aws.cloud.qdrant.io:6333`
- Has API key
- Dashboard: https://cloud.qdrant.io/

**Neo4j Aura**
- URL format: `neo4j+s://abc123.databases.neo4j.io`
- Has username/password
- Dashboard: https://console.neo4j.io/

**n8n Cloud**
- URL format: `https://abc123.app.n8n.cloud`
- Has API key
- Dashboard: https://app.n8n.cloud/

#### **Option B: Self-Hosted** (Less common)

If you have these services running somewhere else (not cloud), you just need the connection URLs.

---

## 📋 **What Information Do You Need?**

### **For Qdrant Cloud:**

1. **Cluster URL**
   - Example: `https://abc123.us-east-1-0.aws.cloud.qdrant.io:6333`
   - Find: Dashboard → Your Cluster → Overview

2. **API Key**
   - Example: `qdrant_xxx_yyy_zzz`
   - Find: Dashboard → Cluster → API Keys → Create Key

### **For Neo4j Aura:**

1. **Connection URI**
   - Example: `neo4j+s://12345678.databases.neo4j.io`
   - Find: Console → Instance → Connection URI

2. **Username** (usually `neo4j`)

3. **Password**
   - You set this when creating instance
   - Cannot be recovered, only reset

### **For n8n Cloud:**

1. **Instance URL**
   - Example: `https://yourname.app.n8n.cloud`
   - Find: Your n8n cloud URL

2. **API Key** (optional, only if calling n8n from code)
   - Find: Settings → API → Create API Key

**Note:** If using n8n Cloud, you create workflows in their UI, not locally!

---

## 🚀 **Deployment Steps (Cloud-Hybrid)**

### **Step 1: Gather All Your Credentials**

**Create a text file with:**

```
=== SUPABASE ===
URL: https://jvjlhxodmbkodzmggwpu.supabase.co
Key: eyJ...

=== TELEGRAM ===
Bot Token: 1234567890:ABC...

=== QDRANT CLOUD ===
URL: https://xyz.us-east-1-0.aws.cloud.qdrant.io:6333
API Key: qdrant_...

=== NEO4J AURA ===
URI: neo4j+s://abc123.databases.neo4j.io
User: neo4j
Password: ...

=== N8N CLOUD (optional) ===
URL: https://yourname.app.n8n.cloud
API Key: n8n_...
```

---

### **Step 2: Connect to Droplet**

```bash
ssh root@137.184.1.91
cd /opt/ASEAGI
```

---

### **Step 3: Pull Latest Code**

```bash
git pull origin claude/create-truth-score-charts-011CUqV28kW1jcpJE1z2B5rM
```

---

### **Step 4: Generate Redis Password**

```bash
echo "REDIS_PASSWORD=$(openssl rand -base64 32)"
# Copy this password!
```

---

### **Step 5: Create .env File**

```bash
cp .env.cloud.example .env
nano .env
```

**Paste your configuration:**

```bash
# ============================================================================
# ASEAGI CLOUD-HYBRID CONFIGURATION
# ============================================================================

# SUPABASE
SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
SUPABASE_KEY=paste-your-actual-supabase-key

# TELEGRAM
TELEGRAM_BOT_TOKEN=paste-your-bot-token

# REDIS (local cache)
REDIS_PASSWORD=paste-generated-redis-password

# QDRANT CLOUD
QDRANT_URL=https://your-cluster.us-east-1-0.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=paste-your-qdrant-api-key

# NEO4J AURA
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=paste-your-neo4j-password

# N8N CLOUD (optional)
N8N_URL=https://yourname.app.n8n.cloud
N8N_API_KEY=paste-your-n8n-api-key

# SYSTEM
DOMAIN=137.184.1.91
TIMEZONE=America/Los_Angeles

# OPTIONAL - AI APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

**Save:** `Ctrl+X`, `Y`, `Enter`

---

### **Step 6: Deploy Cloud-Hybrid Stack**

```bash
# Stop any existing deployment
docker compose down

# Deploy with cloud services
docker-compose -f docker-compose.cloud.yml up -d
```

**This deploys ONLY:**
- ✅ FastAPI (local)
- ✅ Telegram Bot (local)
- ✅ Streamlit Dashboards (local)
- ✅ Redis Cache (local)

**And connects to CLOUD:**
- ☁️ Qdrant Cloud (your API key)
- ☁️ Neo4j Aura (your credentials)
- ☁️ n8n Cloud (your instance)

---

### **Step 7: Verify Deployment**

```bash
docker-compose -f docker-compose.cloud.yml ps
```

**Expected:**
```
NAME                STATUS              PORTS
aseagi-api          Up (healthy)        0.0.0.0:8000->8000/tcp
aseagi-telegram     Up
aseagi-dashboard    Up (healthy)        0.0.0.0:80->8501/tcp
aseagi-redis        Up (healthy)        0.0.0.0:6379->6379/tcp
```

**Notice:** Only 4 containers (vs 8 for full self-hosted)!

---

### **Step 8: Test Connections**

#### **Test API:**
```bash
curl http://localhost:8000/health
```

#### **Test Qdrant Connection:**
```bash
# Check if API can reach Qdrant
docker logs aseagi-api | grep -i qdrant
```

#### **Test Neo4j Connection:**
```bash
# Check if API can reach Neo4j
docker logs aseagi-api | grep -i neo4j
```

#### **Test Telegram Bot:**
1. Open Telegram
2. Find your bot
3. Send `/start`
4. Should get welcome message! ✅

---

## 🔧 **Setting Up Cloud Services**

### **Qdrant Cloud Setup**

#### **If you don't have a cluster yet:**

1. Go to: https://cloud.qdrant.io/
2. Sign up / Log in
3. Click "Create Cluster"
4. Select region (US East or EU)
5. Choose "Free" tier (1GB)
6. Wait for provisioning (2-3 minutes)

#### **Get your credentials:**

1. Click on your cluster
2. Copy "Cluster URL"
   - Example: `https://abc123.us-east-1-0.aws.cloud.qdrant.io:6333`
3. Go to "API Keys" tab
4. Click "Create API Key"
5. Copy the key (shows once!)
6. Add to .env file

---

### **Neo4j Aura Setup**

#### **If you don't have an instance yet:**

1. Go to: https://console.neo4j.io/
2. Sign up / Log in
3. Click "Create Instance"
4. Select "AuraDB Free" (free forever!)
5. Choose region
6. Set password (save this!)
7. Wait for provisioning (5 minutes)

#### **Get your credentials:**

1. Click on your instance
2. Copy "Connection URI"
   - Example: `neo4j+s://12345678.databases.neo4j.io`
3. Username is always: `neo4j`
4. Password: what you set during creation
5. Add to .env file

**Test connection:**
```bash
# Install neo4j driver
pip install neo4j

# Test in Python
from neo4j import GraphDatabase
uri = "neo4j+s://your-instance.databases.neo4j.io"
driver = GraphDatabase.driver(uri, auth=("neo4j", "your-password"))
with driver.session() as session:
    result = session.run("RETURN 'Hello World' AS message")
    print(result.single()["message"])
driver.close()
```

---

### **n8n Cloud Setup**

#### **Two options:**

**Option A: Use n8n Cloud** (Easiest)

1. Go to: https://n8n.io/cloud/
2. Sign up ($20/month Starter plan)
3. Get your instance URL: `https://yourname.app.n8n.cloud`
4. Create workflows in n8n Cloud UI
5. Point workflows to: `http://137.184.1.91:8000/telegram/*`

**Option B: Self-host n8n on droplet** (Free)

Use `docker-compose.full.yml` instead of `docker-compose.cloud.yml`

---

## 📊 **Resource Comparison**

### **Cloud-Hybrid (What you'll deploy):**

| Service | Location | RAM | Cost |
|---------|----------|-----|------|
| FastAPI | Droplet | 1GB | $0 |
| Telegram Bot | Droplet | 512MB | $0 |
| Dashboards | Droplet | 1GB | $0 |
| Redis | Droplet | 256MB | $0 |
| **Droplet Total** | **16GB available** | **~3GB used** | **$96/mo** |
| Qdrant Cloud | AWS | - | Free tier |
| Neo4j Aura | Cloud | - | Free tier |
| n8n Cloud | Cloud | - | $20/mo (optional) |
| **Total Cost** | - | - | **$96-116/mo** |

### **Self-Hosted Everything:**

| Service | Location | RAM | Cost |
|---------|----------|-----|------|
| All services | Droplet | ~8GB | $96/mo |

**Cloud-Hybrid Advantages:**
- ✅ Uses only 3GB RAM (vs 8GB)
- ✅ Better performance (dedicated infra)
- ✅ Managed backups
- ✅ Professional support
- ✅ Same or lower cost!

---

## 🎯 **Which Deployment Should You Use?**

### **Use Cloud-Hybrid If:**
- ✅ You have Qdrant Cloud account ← **YOU!**
- ✅ You have Neo4j Aura account ← **YOU!**
- ✅ You have n8n Cloud account ← **YOU!**
- ✅ You want better reliability
- ✅ You want managed services

**Deploy with:**
```bash
docker-compose -f docker-compose.cloud.yml up -d
```

### **Use Full Self-Hosted If:**
- You want everything on your droplet
- You don't have cloud accounts
- You want complete control

**Deploy with:**
```bash
docker-compose -f docker-compose.full.yml up -d
```

---

## 🔌 **How Services Connect**

### **Your Droplet (FastAPI) Connects To:**

```
┌──────────────────┐
│  Your Droplet    │
│  137.184.1.91    │
├──────────────────┤
│  FastAPI         │──────> Supabase (PostgreSQL + pgvector)
│                  │──────> Qdrant Cloud (vector search)
│                  │──────> Neo4j Aura (graph database)
│                  │
│  Telegram Bot    │──────> Telegram API
│                  │──────> FastAPI (internal)
│                  │
│  Dashboards      │──────> FastAPI (internal)
│                  │──────> Qdrant Cloud (direct)
│                  │──────> Neo4j Aura (direct)
└──────────────────┘

┌──────────────────┐
│  n8n Cloud       │──────> Your API (http://137.184.1.91:8000)
│  (your instance) │──────> Telegram API
└──────────────────┘
```

---

## ✅ **Complete Setup Checklist**

### **Cloud Services:**
- [ ] Qdrant Cloud cluster created
- [ ] Qdrant API key generated
- [ ] Neo4j Aura instance created
- [ ] Neo4j credentials saved
- [ ] n8n Cloud account (optional)

### **Deployment:**
- [ ] Connected to droplet
- [ ] Pulled latest code
- [ ] Generated Redis password
- [ ] Created .env with all credentials
- [ ] Deployed: `docker-compose -f docker-compose.cloud.yml up -d`
- [ ] Verified all containers running

### **Testing:**
- [ ] API health check passes
- [ ] Telegram bot responds
- [ ] Dashboards accessible
- [ ] Qdrant connection works
- [ ] Neo4j connection works

---

## 🚨 **Troubleshooting Cloud Connections**

### **Problem: Can't connect to Qdrant Cloud**

**Check:**
```bash
# Test from droplet
curl -X GET "https://your-cluster.cloud.qdrant.io:6333/collections" \
  -H "api-key: your-api-key"
```

**Common issues:**
- Wrong URL (check dashboard for exact URL)
- Wrong API key (regenerate if needed)
- Firewall (Qdrant Cloud should be accessible)

---

### **Problem: Can't connect to Neo4j Aura**

**Check:**
```bash
# Test with cypher-shell
docker run --rm -it neo4j:5-community \
  cypher-shell -a "neo4j+s://your-instance.databases.neo4j.io" \
  -u neo4j -p "your-password" \
  "RETURN 'Hello' AS message"
```

**Common issues:**
- Wrong URI format (must include `neo4j+s://`)
- Wrong password (reset in console if forgotten)
- Instance paused (free tier pauses after inactivity)

---

### **Problem: n8n workflows can't reach API**

**Check:**
- Is API accessible externally? `curl http://137.184.1.91:8000/health`
- Is firewall allowing port 8000? `ufw status`
- Is n8n using correct URL? `http://137.184.1.91:8000` (NOT https)

---

## 📚 **Next Steps**

### **After Successful Deployment:**

1. **Configure n8n Workflows**
   - If n8n Cloud: Create workflows in cloud UI
   - If self-hosted: Import JSON templates

2. **Populate Qdrant with Embeddings**
   - Create collections
   - Upload document embeddings
   - Test similarity search

3. **Build Neo4j Graph**
   - Import party relationships
   - Link case events
   - Map document connections

4. **Test End-to-End**
   - Use Telegram bot to search
   - Check vector search results
   - Verify graph relationships

---

## 💡 **Pro Tips**

### **Qdrant Cloud:**
- Start with free tier (1GB)
- Upgrade as needed
- Use snapshots for backups

### **Neo4j Aura:**
- AuraDB Free never expires!
- Max 200k nodes
- Auto-pauses after 3 days inactive
- Resume instantly when accessed

### **n8n Cloud:**
- Starter: 5,000 workflow executions/month
- Can always self-host for free later
- Export workflows as JSON (portable)

---

## 🎯 **Quick Decision Guide**

**Have all cloud credentials ready?** → Use `docker-compose.cloud.yml`

**Don't have cloud accounts yet?** → Two options:
1. Create free cloud accounts (20 min)
2. Use `docker-compose.full.yml` (self-host everything)

**Want to save droplet resources?** → Use cloud services

**Want everything local?** → Self-host all

---

## 📞 **Support**

### **Cloud Service Support:**
- Qdrant: https://qdrant.tech/documentation/
- Neo4j: https://aura.support.neo4j.com/
- n8n: https://community.n8n.io/

### **Your Services:**
- API Docs: `http://137.184.1.91:8000/docs`
- Logs: `docker logs aseagi-api`

---

**For Ashe. For Justice. For All Children.** 🛡️

---

## 🚀 **Ready to Deploy?**

**Share your cloud service details and I'll help you configure the .env file!**

**Format:**
```
Qdrant URL: ...
Qdrant API Key: ...
Neo4j URI: ...
Neo4j Password: ...
n8n URL (if cloud): ...
```
