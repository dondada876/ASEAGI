# Complete Integrated Architecture: Telegram + Qdrant + Neo4j + n8n
**Full-stack document intelligence system with workflow automation**

---

## 🏗️ COMPLETE ARCHITECTURE

```
┌──────────────────────────────────────────────────────────────────┐
│                    USER ACCESS LAYER                             │
├───────────┬───────────┬──────────┬──────────┬───────────────────┤
│  Mobile   │ Telegram  │Streamlit │  n8n UI  │  Neo4j Browser    │
│  Scanner  │    Bot    │Dashboard │(Workflow)│  (Graph Viz)      │
└───────────┴───────────┴──────────┴──────────┴───────────────────┘
```

**Key Decision: YES, separate Telegram container!**

### **Why Separate Telegram Docker Container?**

✅ **Different port** (8443 vs 8000) - No conflicts
✅ **Independent restart** - Bot crashes don't affect API
✅ **Easier scaling** - Can run multiple bot instances
✅ **Security isolation** - Bot token separate from API keys

---

## 🔌 SERVICE PORTS (No Conflicts!)

```yaml
Port Mapping:
  80/443   → Nginx (reverse proxy)
    ├─ / → Streamlit Dashboard
    ├─ /api → FastAPI
    ├─ /telegram-webhook → Telegram Bot
    └─ /n8n → n8n Workflows

  8000   → FastAPI Backend
  8443   → Telegram Bot webhook
  5678   → n8n UI
  6333   → Qdrant API
  7474   → Neo4j Browser
  7687   → Neo4j Bolt
  6379   → Redis
```

---

## 💰 COSTS

| Service | Cost |
|---------|------|
| Digital Ocean 8GB RAM | $24/month |
| Vast.ai GPU | $0.20/hour (on-demand) |
| Supabase | Free tier |
| **TOTAL** | **~$26/month** |

**Worth it?** YES! You get:
- Telegram bot (24/7)
- Vector search (Qdrant)
- Graph database (Neo4j)
- Workflow automation (n8n)
- GPU processing (Vast.ai)
- All integrated seamlessly

---

## 🎯 DATA FLOWS

### **Flow 1: Telegram Upload**
```
User takes photo → Sends to Telegram bot
  ↓
Telegram bot (port 8443) → FastAPI (internal: api:8000)
  ↓
FastAPI → Redis queue → Vast.ai GPU worker
  ↓
Results → Supabase + Qdrant + Neo4j
  ↓
Telegram bot sends reply: "✅ Processed! Truth Score: 85/100"
```

### **Flow 2: Vector Search**
```
User query: "Find documents about protective orders"
  ↓
FastAPI → Qdrant semantic search
  ↓
Returns similar documents
  ↓
Display in Dashboard or Telegram
```

### **Flow 3: Graph RAG**
```
Query: "Find all docs mentioning Person X that cite Statute Y"
  ↓
FastAPI → Neo4j graph traversal
  ↓
Find connected documents via relationships
  ↓
Return results with relationship paths
```

### **Flow 4: n8n Automation**
```
Trigger: New document uploaded (webhook)
  ↓
n8n workflow:
  1. Check Qdrant for duplicates
  2. If new, queue for GPU processing
  3. Wait for results
  4. Store relationships in Neo4j
  5. Send Telegram notification
  6. Update dashboard
```

---

## 🚀 WHY ADD N8N?

### **n8n = No-Code Workflow Automation**

**Use Cases:**
1. **Daily Fraud Reports** - Auto-generate and send via Telegram
2. **Duplicate Alerts** - Notify when similar docs found
3. **Scheduled Processing** - Batch process documents at night
4. **Multi-step Workflows** - Complex automation without coding
5. **Integration Hub** - Connect all services visually

**Example Workflow:**
```
Cron: 6am daily
  → Query Supabase for yesterday's documents
  → Filter: truth_score < 70
  → Neo4j: Find related documents
  → Generate fraud report
  → Send Telegram message
```

---

## 🎯 SHOULD YOU ADD N8N?

**YES! Here's why:**

✅ **Visual workflow builder** - Drag and drop, no coding
✅ **100+ integrations** - Telegram, Supabase, webhooks, etc
✅ **Free and open-source** - Self-hosted, no subscription
✅ **Perfect for your use case** - Automate fraud detection workflows
✅ **Saves time** - Set up once, runs forever

**When to add:** After core system is working (Week 2-3)

---

## 📊 INTEGRATION MATRIX

| From | To | Method | Use Case |
|------|-----|--------|----------|
| Telegram | FastAPI | HTTP (internal) | Upload documents |
| FastAPI | Qdrant | HTTP API | Vector search |
| FastAPI | Neo4j | Bolt protocol | Graph queries |
| FastAPI | Redis | Redis protocol | Job queue |
| n8n | All services | HTTP/APIs | Workflow automation |
| Vast.ai Worker | Redis | Redis protocol | Pick up jobs |
| Dashboard | Qdrant + Neo4j | HTTP APIs | Display search results |

---

## 🔄 COMPLETE DOCKER-COMPOSE

```yaml
version: '3.8'

services:
  # FastAPI Backend
  api:
    ports:
      - "8000:8000"
    environment:
      - QDRANT_URL=http://qdrant:6333
      - NEO4J_URI=bolt://neo4j:7687
    networks:
      - aseagi-network

  # Telegram Bot (SEPARATE CONTAINER!)
  telegram:
    ports:
      - "8443:8443"  # Different port!
    environment:
      - API_URL=http://api:8000  # Internal Docker network
    networks:
      - aseagi-network

  # n8n Workflow Automation
  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    volumes:
      - n8n-data:/home/node/.n8n
    networks:
      - aseagi-network

  # Qdrant Vector Database
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant-data:/qdrant/storage
    networks:
      - aseagi-network

  # Neo4j Graph Database
  neo4j:
    image: neo4j:5-community
    ports:
      - "7474:7474"  # Browser
      - "7687:7687"  # Bolt
    environment:
      - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}
    volumes:
      - neo4j-data:/data
    networks:
      - aseagi-network

networks:
  aseagi-network:
    driver: bridge

volumes:
  n8n-data:
  qdrant-data:
  neo4j-data:
```

---

## 🎨 EXAMPLE: TELEGRAM BOT CODE

```python
# telegram_bot.py

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler
import requests

# Connect to FastAPI via Docker network
API_URL = "http://api:8000"  # NOT localhost!

async def upload(update: Update, context):
    """Handle document upload"""

    file = await update.message.document.get_file()
    file_bytes = await file.download_as_bytearray()

    # Send to FastAPI
    response = requests.post(
        f"{API_URL}/api/upload",
        files={"file": file_bytes}
    )

    result = response.json()

    if result["status"] == "duplicate":
        await update.message.reply_text(
            f"⚠️ Duplicate: {result['similarity']:.0%} match"
        )
    else:
        await update.message.reply_text(
            f"✅ Truth Score: {result['truth_score']}/100"
        )

async def search(update: Update, context):
    """Search documents via Qdrant"""

    query = " ".join(context.args)

    response = requests.get(
        f"{API_URL}/api/search",
        params={"query": query}
    )

    results = response.json()["results"]

    message = "🔍 Found:\n\n"
    for doc in results:
        message += f"📄 {doc['file_name']}\n"

    await update.message.reply_text(message)
```

---

## 📈 DEPLOYMENT PHASES

### **Phase 1: Core (Week 1)**
```bash
# Deploy: FastAPI + Dashboard + Redis + Qdrant
docker-compose up -d api dashboard redis qdrant
```

### **Phase 2: Telegram (Week 1)**
```bash
# Add Telegram bot
docker-compose up -d telegram

# Set webhook
curl -X POST https://api.telegram.org/bot$TOKEN/setWebhook \
  -d url=https://$YOUR_IP:8443/webhook
```

### **Phase 3: Graph (Week 2)**
```bash
# Add Neo4j
docker-compose up -d neo4j

# Populate with existing documents
python3 populate_neo4j.py
```

### **Phase 4: Automation (Week 3)**
```bash
# Add n8n
docker-compose up -d n8n

# Access at: http://$YOUR_IP:5678
# Create workflows
```

---

## 💡 MY RECOMMENDATION

**Deploy in this order:**

1. **NOW:** Core system (FastAPI + Dashboard + Qdrant)
2. **Day 2:** Add Telegram bot (separate container)
3. **Week 2:** Add Neo4j (when you have >100 documents)
4. **Week 3:** Add n8n (when you want automation)

**Start simple, add complexity as needed.**

---

## 🎯 IMMEDIATE NEXT STEP

**Option A: Deploy with Telegram NOW**
```bash
./deploy_digitalocean_full.sh  # I'll create this
```

**Option B: Add Telegram to existing deployment**
```bash
docker-compose up -d telegram
```

**Option C: Test locally first**
```bash
docker-compose up api dashboard telegram qdrant
```

---

**Want me to create the full deployment with all services integrated?** 🚀

**For Ashe. For Justice. For All Children.** 🛡️
