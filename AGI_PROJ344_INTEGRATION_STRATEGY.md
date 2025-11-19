# AGI Protocol + PROJ344 Integration Strategy

**Date:** November 19, 2025
**Status:** ✅ Foundation Complete, Ready for Implementation
**Risk Level:** 🟢 Low (Zero Breaking Changes)

---

## Executive Summary

The AGI Protocol and PROJ344 systems are designed to work **in harmony**, not competition. This document outlines the safe, conflict-free integration strategy.

### Key Principle: **Zero Conflicts Design**

✅ **Separate Ports** - No port conflicts
✅ **Shared Database** - Read-only access via bridge
✅ **Independent Deployment** - Can run separately or together
✅ **Modular Architecture** - AGI can be removed without affecting PROJ344
✅ **Safe Rollback** - Complete isolation allows instant rollback

---

## System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                    ASEAGI UNIFIED SYSTEM                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────┐      ┌─────────────────────────┐   │
│  │   PROJ344 Systems       │      │   AGI Protocol          │   │
│  │   (Existing - Fixed)    │◄─────┤   (New - Isolated)     │   │
│  ├─────────────────────────┤      ├─────────────────────────┤   │
│  │                         │      │                         │   │
│  │ 🎨 Dashboards           │      │ 🤖 FastAPI Backend      │   │
│  │   Ports: 8501-8506      │      │   Port: 8000            │   │
│  │                         │      │                         │   │
│  │ 📊 Document Scanners    │      │ 📱 Telegram Bot         │   │
│  │   Batch processing      │      │   Port: 8443            │   │
│  │                         │      │                         │   │
│  │ 🔧 Bug Tracking         │      │ 🔗 PROJ344 Bridge       │   │
│  │   Automatic errors      │      │   Read-only queries     │   │
│  │                         │      │                         │   │
│  │ ⏰ n8n Workflows        │      │ 🧠 Multi-Agent AI       │   │
│  │   Telegram alerts       │      │   Legal research        │   │
│  └─────────────────────────┘      └─────────────────────────┘   │
│              │                               │                   │
│              └───────────┬───────────────────┘                   │
│                          │                                       │
│                          ▼                                       │
│             ┌──────────────────────────┐                         │
│             │  Shared Supabase DB      │                         │
│             │  PostgreSQL Database     │                         │
│             │  - legal_documents       │                         │
│             │  - legal_violations      │                         │
│             │  - court_events          │                         │
│             │  - bugs                  │                         │
│             └──────────────────────────┘                         │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Port Allocation Matrix

### **PROJ344 Ports (Protected - No Changes)**

| Port | Service | File | Status |
|------|---------|------|--------|
| 8501 | Master Dashboard | `proj344_master_dashboard.py` | ✅ Active |
| 8502 | Legal Intelligence | `legal_intelligence_dashboard.py` | ✅ Active |
| 8503 | CEO Dashboard | `ceo_dashboard.py` | ✅ Active |
| 8504 | Enhanced Scanning Monitor | `enhanced_scanning_monitor.py` | ✅ Active |
| 8505 | Timeline & Violations | `timeline_violations_dashboard.py` | ✅ Active |
| 8506 | Master 5W+H | `master_5wh_dashboard.py` | ✅ Active |

### **AGI Protocol Ports (New - No Conflicts)**

| Port | Service | Container | Status |
|------|---------|-----------|--------|
| 8000 | FastAPI Backend | `agi-protocol-api` | 🆕 Ready |
| 8443 | Telegram Webhook | `agi-telegram-bot` | 🆕 Ready |
| 6379 | Redis Cache | `agi-redis` | 🆕 Optional |

**Result:** ✅ **ZERO PORT CONFLICTS**

---

## Shared Resources Strategy

### 1. Database (Supabase)

**Connection:**
- Both systems use **same** `SUPABASE_URL` and `SUPABASE_KEY`
- Both read from `.env` file (or environment variables)

**Access Pattern:**
```
PROJ344:
  ✅ Read access to legal_documents
  ✅ Write access to legal_documents (via scanners)
  ✅ Full CRUD on all tables

AGI Protocol:
  ✅ Read access to legal_documents (via PROJ344 Bridge)
  ✅ Read access to legal_violations (via PROJ344 Bridge)
  ⛔ NO write access to PROJ344 tables (safety)
  ✅ Write access to its own tables (agi_*)
```

**Safety Mechanisms:**
```python
# agi-protocol/api/integrations/proj344_bridge.py
# ALL methods are read-only:
async def get_smoking_guns():  # ✅ SELECT only
async def get_violations():   # ✅ SELECT only
# NO insert_document()         # ⛔ Not allowed
# NO update_document()         # ⛔ Not allowed
# NO delete_document()         # ⛔ Not allowed
```

### 2. API Keys (Anthropic Claude)

**Shared Key:** `ANTHROPIC_API_KEY`

**Usage Pattern:**
```
PROJ344:
  - batch_scan_documents.py uses for document analysis
  - Cost: ~$0.013 per document
  - Tracked in legal_documents.api_cost_usd

AGI Protocol:
  - Uses for intelligent Telegram responses (optional)
  - Uses for motion generation (future)
  - Separate cost tracking (won't affect PROJ344 budgets)
```

**Rate Limits:**
- Both systems respect Anthropic rate limits
- AGI Protocol implements optional caching via Redis
- No interference between systems

### 3. File Storage

**Strategy: Complete Separation**

```
PROJ344:
  - Scans documents from disk
  - Stores metadata in Supabase
  - No shared file system with AGI

AGI Protocol:
  - Uploads via Telegram bot
  - Stores in /agi-protocol/uploads/
  - Can reference PROJ344 documents via bridge
```

---

## Deployment Strategies

### Strategy 1: Independent Deployment (Recommended for Testing)

```bash
# Start PROJ344 only
docker-compose up -d

# Start AGI Protocol only
docker-compose -f docker-compose.agi.yml up -d

# Stop PROJ344 (AGI continues)
docker-compose down

# Stop AGI (PROJ344 continues)
docker-compose -f docker-compose.agi.yml down
```

**Use Case:** Testing, development, gradual rollout

### Strategy 2: Unified Deployment (Production)

```bash
# Start both systems together
docker-compose up -d && docker-compose -f docker-compose.agi.yml up -d

# Stop both systems
docker-compose down && docker-compose -f docker-compose.agi.yml down
```

**Use Case:** Full production deployment

### Strategy 3: Local PROJ344 + Dockerized AGI

```bash
# Run PROJ344 dashboards locally (for development)
./scripts/launch-all-dashboards.sh

# Run AGI Protocol in Docker
docker-compose -f docker-compose.agi.yml up -d
```

**Use Case:** Development workflow

---

## Integration Points

### 1. PROJ344 Bridge Module

**Location:** `agi-protocol/api/integrations/proj344_bridge.py`

**Purpose:** Safe, read-only access to PROJ344 data

**Methods:**
```python
class PROJ344Bridge:
    # Document Queries
    async def get_smoking_guns(min_relevancy=900)
    async def get_documents_by_score_range(min, max)
    async def get_perjury_indicators()
    async def get_document_by_id(doc_id)
    async def search_documents(query, field)

    # Violations Queries
    async def get_violations(category=None)

    # Statistics
    async def get_dashboard_stats()
    async def get_recent_documents(limit, days)

    # Health
    async def health_check()
```

**Safety Features:**
- ✅ All methods are read-only (SELECT only)
- ✅ Independent error handling
- ✅ Logging separate from PROJ344
- ✅ Failures don't affect PROJ344
- ✅ No shared state

### 2. Telegram Bot Integration

**Workflow:**
```
User → Telegram → AGI Bot → FastAPI → PROJ344 Bridge → Supabase
                                ↓
                          Format Response
                                ↓
                          Send to Telegram
```

**Example Commands:**
```
/report      → Queries PROJ344 stats via bridge
/violations  → Queries legal_violations table
/search      → Searches documents via bridge
/upload      → Stores in AGI system (not PROJ344)
```

### 3. Dashboard Cross-Linking (Future)

**Potential Enhancement:**
```python
# Add link in PROJ344 dashboard to AGI Protocol
st.markdown("[🤖 AGI Protocol API](http://localhost:8000/docs)")

# Add link in AGI Protocol to PROJ344
response["proj344_dashboard"] = "http://localhost:8501"
```

---

## Safety & Rollback Procedures

### Emergency Rollback

**If AGI Protocol causes issues:**

```bash
# 1. Stop AGI Protocol immediately
docker-compose -f docker-compose.agi.yml down

# 2. Verify PROJ344 still working
curl http://localhost:8501/_stcore/health  # Should return 200

# 3. Remove AGI Protocol entirely (if needed)
rm -rf agi-protocol/

# 4. PROJ344 continues to function normally ✅
```

**Recovery Time:** < 10 seconds

### Health Monitoring

**Check PROJ344:**
```bash
# Dashboards
curl http://localhost:8501/_stcore/health
curl http://localhost:8502/_stcore/health

# Database
python3 -c "from supabase import create_client; import os; print(create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY']).table('legal_documents').select('count').execute())"
```

**Check AGI Protocol:**
```bash
# API
curl http://localhost:8000/health

# Database access via bridge
curl http://localhost:8000/status
```

---

## Development Workflow

### Adding New AGI Features

**Safe Development Process:**

1. **Develop in `agi-protocol/` directory only**
   ```bash
   cd agi-protocol
   # Make changes only in this directory
   ```

2. **Test independently**
   ```bash
   # Test AGI without PROJ344 running
   docker-compose -f docker-compose.agi.yml up
   ```

3. **Test integration**
   ```bash
   # Start both systems
   ./scripts/launch-all-dashboards.sh  # PROJ344
   docker-compose -f docker-compose.agi.yml up  # AGI
   ```

4. **Verify PROJ344 unaffected**
   ```bash
   # Check all PROJ344 dashboards still work
   curl http://localhost:8501/_stcore/health
   curl http://localhost:8502/_stcore/health
   # ... etc
   ```

### Modifying PROJ344

**Safe Modification Process:**

1. **NEVER modify PROJ344 code from AGI Protocol**
   - AGI code lives in `agi-protocol/`
   - PROJ344 code lives in root directories

2. **If PROJ344 database schema changes:**
   ```python
   # Update PROJ344 Bridge to match
   # agi-protocol/api/integrations/proj344_bridge.py
   async def get_new_table():
       # Add new read-only query
   ```

3. **Test both systems after PROJ344 changes:**
   ```bash
   # Ensure AGI Bridge still works
   curl http://localhost:8000/status
   ```

---

## Configuration Management

### Environment Variables

**Shared Variables (use same values):**
```env
# .env (root level - used by both systems)
SUPABASE_URL=...
SUPABASE_KEY=...
ANTHROPIC_API_KEY=...
```

**AGI-Specific Variables:**
```env
# .env (additional variables for AGI)
TELEGRAM_BOT_TOKEN=...
API_SECRET_KEY=...
REDIS_URL=...
```

**Best Practice:**
```bash
# Single .env file with all variables
SUPABASE_URL=...
SUPABASE_KEY=...
ANTHROPIC_API_KEY=...
TELEGRAM_BOT_TOKEN=...  # Only used by AGI
API_SECRET_KEY=...      # Only used by AGI
```

---

## Testing Checklist

### Before Deploying AGI Protocol

- [ ] PROJ344 dashboards running (8501-8506)
- [ ] PROJ344 database accessible
- [ ] AGI ports available (8000, 8443)
- [ ] Environment variables set
- [ ] Docker installed and running

### After Deploying AGI Protocol

- [ ] AGI API health check passes (`/health`)
- [ ] PROJ344 Bridge connection works (`/status`)
- [ ] PROJ344 dashboards still accessible
- [ ] No port conflicts
- [ ] Both systems logging correctly

### Integration Testing

- [ ] AGI can query PROJ344 data
- [ ] PROJ344 continues to scan documents
- [ ] Telegram bot receives commands
- [ ] API documentation accessible (`/docs`)
- [ ] Both systems can be stopped independently

---

## Future Enhancements

### Phase 2: Enhanced Integration

1. **Real-time Updates**
   - AGI Protocol WebSocket pushes updates to dashboards
   - PROJ344 dashboards subscribe to AGI events

2. **Unified Search**
   - Single search endpoint across both systems
   - Federated query execution

3. **Shared Analytics**
   - Combined metrics dashboard
   - Cross-system performance monitoring

### Phase 3: Advanced Features

1. **Multi-Agent Orchestration**
   - Coordinated document analysis
   - Parallel processing across systems

2. **Automated Workflows**
   - n8n workflows trigger AGI Protocol actions
   - AGI Protocol results feed back to PROJ344

---

## Contact & Support

### For PROJ344 Issues
- Check `BUGS_FIXED_2025-11-19.md`
- Review `CLAUDE.md`
- Check dashboard logs

### For AGI Protocol Issues
- Check `agi-protocol/README.md`
- Review API logs: `agi-protocol/logs/`
- Test health endpoint: `/health`

### For Integration Issues
- Check both system logs
- Verify environment variables
- Test PROJ344 Bridge: `/status`
- Review this document

---

## Summary

✅ **Zero Conflicts** - Different ports, modular design
✅ **Safe Integration** - Read-only bridge, independent deployment
✅ **Easy Rollback** - Remove AGI without affecting PROJ344
✅ **Shared Resources** - Same database, same API keys, efficient
✅ **Independent Development** - Each system evolves separately

**Status:** Ready for implementation. All foundations in place.

**For Ashe. For Justice. For All Children.** 🛡️
