# AGI Protocol Integration Plan

## Executive Summary

This document outlines the integration strategy for the **AGI Protocol Legal Defense System** as a separate module within the existing ASEAGI repository, ensuring zero conflicts with existing systems while enabling seamless interoperability.

## Current System Overview (ASEAGI/PROJ344)

**Purpose:** Legal document intelligence and case management
**Architecture:**
- Streamlit dashboards (ports 8501-8503)
- Document scanners with multi-dimensional scoring (0-999)
- Supabase database backend
- Bug tracking system
- n8n workflow automation
- MCP server integrations

**Key Components:**
```
ASEAGI/
├── core/              # Bug tracking, workspace config
├── dashboards/        # Streamlit UI (Master, Legal Intel, CEO)
├── database/          # Supabase schemas, migrations
├── scanners/          # Document scanning & scoring
├── docs/              # Documentation
├── integrations/      # External system integrations
├── n8n-workflows/     # Workflow automation
├── mcp-servers/       # Model Context Protocol servers
└── scripts/           # Utility scripts
```

## New System Overview (AGI Protocol)

**Purpose:** Comprehensive AI-powered legal defense orchestration
**Architecture:**
- Multi-agent system with master orchestrator
- Specialized agents (8 agent types)
- Context window optimization
- FastAPI REST API
- Multiple databases (PostgreSQL, Redis, Neo4j, Qdrant)

## Integration Strategy: Modular Coexistence

### Design Principle: **Separation with Bridges**

The AGI Protocol will exist as a **separate module** with **well-defined integration points** to the existing ASEAGI system.

```
┌─────────────────────────────────────────────────────────────────┐
│                    ASEAGI REPOSITORY                            │
│                                                                 │
│  ┌────────────────────┐         ┌─────────────────────────┐   │
│  │  EXISTING SYSTEM   │         │   AGI PROTOCOL (NEW)    │   │
│  │  (PROJ344)         │◄───────►│   Multi-Agent System    │   │
│  │                    │  Bridge │                         │   │
│  │  • Dashboards      │         │  • Master Orchestrator  │   │
│  │  • Scanners        │         │  • Document Agent       │   │
│  │  • Supabase DB     │         │  • Research Agent       │   │
│  │  • Bug Tracking    │         │  • Motion Agent         │   │
│  │  • n8n Workflows   │         │  • Evidence Agent       │   │
│  └────────────────────┘         │  • Citation Agent       │   │
│                                  │  • Strategic Agent      │   │
│                                  │  • Outreach Agent       │   │
│                                  │  • FastAPI Layer        │   │
│                                  └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Folder Structure

```
ASEAGI/
├── core/                          # [EXISTING] Shared utilities
│   ├── bug_tracker.py
│   ├── workspace_config.py
│   └── __init__.py
│
├── dashboards/                    # [EXISTING] Streamlit dashboards
│   ├── proj344_master_dashboard.py
│   ├── legal_intelligence_dashboard.py
│   └── ceo_dashboard.py
│
├── scanners/                      # [EXISTING] Document scanners
│   ├── batch_scan_documents.py
│   └── query_legal_documents.py
│
├── database/                      # [EXISTING] Supabase schemas
│   ├── schema_types.py
│   └── migrations/
│
├── agi-protocol/                  # [NEW] AGI Protocol Module
│   ├── README.md                  # AGI Protocol overview
│   ├── requirements.txt           # Specific dependencies
│   ├── .env.example               # AGI-specific config
│   │
│   ├── docs/                      # [NEW] AGI Protocol documentation
│   │   ├── PRD.md                 # Full PRD (moved here)
│   │   ├── architecture.md
│   │   ├── agent_specs/
│   │   ├── api_reference.md
│   │   └── deployment.md
│   │
│   ├── src/                       # [NEW] AGI Protocol source code
│   │   ├── __init__.py
│   │   │
│   │   ├── core/                  # Core orchestration
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py
│   │   │   ├── base_agent.py
│   │   │   ├── context_manager.py
│   │   │   └── workflow_engine.py
│   │   │
│   │   ├── agents/                # Specialized agents
│   │   │   ├── __init__.py
│   │   │   ├── document_intelligence/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── processor.py
│   │   │   │   ├── analyzer.py
│   │   │   │   └── indexer.py
│   │   │   ├── legal_research/
│   │   │   ├── motion_drafting/
│   │   │   ├── evidence/
│   │   │   ├── citation/
│   │   │   ├── strategic/
│   │   │   └── outreach/
│   │   │
│   │   ├── integrations/          # Bridge to existing systems
│   │   │   ├── __init__.py
│   │   │   ├── proj344_bridge.py  # Connect to PROJ344 scanners
│   │   │   ├── supabase_bridge.py # Supabase integration
│   │   │   └── dashboard_api.py   # API for dashboards
│   │   │
│   │   ├── data/                  # Data layer
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── database.py
│   │   │   ├── vector_store.py
│   │   │   └── graph_store.py
│   │   │
│   │   ├── api/                   # FastAPI application
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── routes/
│   │   │   └── middleware.py
│   │   │
│   │   └── utils/                 # Utilities
│   │       ├── __init__.py
│   │       ├── logging.py
│   │       └── config.py
│   │
│   ├── templates/                 # [NEW] Legal templates
│   │   ├── motions/
│   │   ├── declarations/
│   │   └── briefs/
│   │
│   ├── tests/                     # [NEW] AGI Protocol tests
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   │
│   ├── scripts/                   # [NEW] AGI-specific scripts
│   │   ├── setup_agi.py
│   │   ├── run_orchestrator.py
│   │   └── process_documents.py
│   │
│   └── docker/                    # [NEW] AGI containerization
│       ├── Dockerfile.agi
│       └── docker-compose.agi.yml
│
├── docs/                          # [EXISTING] Repository docs
│   └── agi-protocol/              # AGI reference docs
│       └── INTEGRATION_GUIDE.md
│
├── scripts/                       # [EXISTING] Global scripts
│   ├── launch-all-dashboards.sh
│   └── launch-agi-api.sh          # [NEW] Launch AGI API
│
└── [EXISTING FILES...]
```

## Integration Points: Bridges Between Systems

### 1. Document Intelligence Bridge

**Purpose:** AGI Protocol's Document Intelligence Agent can leverage existing PROJ344 scoring

**Implementation:**
```python
# agi-protocol/src/integrations/proj344_bridge.py

from typing import Dict, Any
import sys
sys.path.append('../../scanners')  # Access existing scanners

class PROJ344Bridge:
    """Bridge to existing PROJ344 document scoring system"""

    def get_document_scores(self, doc_id: str) -> Dict[str, Any]:
        """Retrieve existing PROJ344 scores from Supabase"""
        # Query existing legal_documents table
        pass

    def enhance_with_agi_analysis(self, doc_id: str, agi_scores: Dict) -> Dict:
        """Add AGI Protocol analysis to existing document"""
        # Augment existing data with new agent insights
        pass

    def sync_document_metadata(self, doc_id: str) -> bool:
        """Sync document metadata between systems"""
        pass
```

**Benefits:**
- No duplicate document processing
- Leverage existing 0-999 scoring system
- Enhance documents with AGI agent insights
- Maintain single source of truth in Supabase

### 2. Database Strategy: Shared + Dedicated

**Shared Database (Supabase):**
- `legal_documents` (existing) - Document metadata & PROJ344 scores
- `court_events` (existing) - Timeline tracking
- `legal_violations` (existing) - Constitutional violations
- `agi_agent_runs` (new) - AGI agent execution logs
- `agi_motion_drafts` (new) - Generated motions
- `agi_research_memos` (new) - Legal research outputs

**AGI-Specific Databases:**
- **Redis:** Caching, task queue for Celery
- **Qdrant/ChromaDB:** Vector embeddings for semantic search
- **Neo4j (optional):** Case relationship graph

**Configuration:**
```python
# agi-protocol/src/utils/config.py

class DatabaseConfig:
    # Use existing Supabase for shared data
    SUPABASE_URL = os.getenv('SUPABASE_URL')  # From existing .env
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')

    # AGI-specific databases
    REDIS_URL = os.getenv('AGI_REDIS_URL', 'redis://localhost:6379')
    VECTOR_DB_URL = os.getenv('AGI_VECTOR_DB_URL', 'http://localhost:6333')
    GRAPH_DB_URL = os.getenv('AGI_GRAPH_DB_URL', 'bolt://localhost:7687')
```

### 3. API Layer: FastAPI for AGI, Streamlit for UI

**Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│  USER INTERFACES                                            │
│  ┌──────────────────┐         ┌──────────────────────┐    │
│  │ Streamlit        │         │ CLI Tools            │    │
│  │ Dashboards       │         │ (scripts/)           │    │
│  │ (Existing)       │         │                      │    │
│  └────────┬─────────┘         └──────────┬───────────┘    │
│           │                              │                 │
│           │  HTTP/REST                   │  Direct Python  │
│           │                              │                 │
│  ┌────────▼──────────────────────────────▼───────────┐    │
│  │  AGI Protocol FastAPI Layer                       │    │
│  │  (agi-protocol/src/api/main.py)                   │    │
│  │                                                    │    │
│  │  Endpoints:                                        │    │
│  │  • POST /agents/document/process                  │    │
│  │  • POST /agents/research/query                    │    │
│  │  • POST /agents/motion/draft                      │    │
│  │  • GET  /cases/{case_id}/documents                │    │
│  │  • GET  /orchestrator/status                      │    │
│  └────────┬───────────────────────────────────────────┘    │
│           │                                                 │
│  ┌────────▼─────────────────────────────────────────┐     │
│  │  Master Orchestrator                             │     │
│  │  (agi-protocol/src/core/orchestrator.py)         │     │
│  └──────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

**Port Allocation:**
- 8501: PROJ344 Master Dashboard (existing)
- 8502: Legal Intelligence Dashboard (existing)
- 8503: CEO Dashboard (existing)
- 8504: Bug Tracker Dashboard (existing)
- **8505: AGI Protocol API (new)**

### 4. Workflow Integration: n8n + AGI Protocol

**Scenario:** Automate document processing pipeline

```
n8n Workflow:
1. Watch folder for new documents
2. Trigger PROJ344 scanner (existing)
3. Call AGI Document Agent (new) via HTTP
4. Update Supabase with combined results
5. Notify user via Telegram (existing MCP)
```

**Implementation:**
```javascript
// n8n HTTP Request Node
POST http://localhost:8505/agents/document/process
{
  "filepath": "{{$json.filepath}}",
  "case_id": "ashe-bucknor-j24-00478",
  "use_proj344_scores": true  // Leverage existing scoring
}
```

### 5. Shared Configuration Management

**Strategy:** Single `.env` file with namespaced variables

```bash
# .env (root of ASEAGI repo)

# ============ EXISTING PROJ344 CONFIG ============
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx
ANTHROPIC_API_KEY=xxx

# ============ AGI PROTOCOL CONFIG ============
# API Configuration
AGI_API_PORT=8505
AGI_API_HOST=0.0.0.0

# Database Configuration
AGI_REDIS_URL=redis://localhost:6379
AGI_VECTOR_DB_URL=http://localhost:6333
AGI_GRAPH_DB_URL=bolt://localhost:7687

# Agent Configuration
AGI_MAX_CONTEXT_TOKENS=100000
AGI_DEFAULT_MODEL=claude-sonnet-4.5

# Westlaw API (for Legal Research Agent)
WESTLAW_API_KEY=xxx
WESTLAW_CLIENT_ID=xxx

# Storage Paths
AGI_DOCUMENT_STORAGE=/Users/dbucknor/Documents/PROJ344_Documents
AGI_CASE_DATABASE=/Users/dbucknor/Documents/PROJ344_Cases
AGI_MOTION_OUTPUT=/Users/dbucknor/Documents/PROJ344_Motions
```

## Conflict Avoidance Checklist

| Potential Conflict | Mitigation Strategy | Status |
|--------------------|---------------------|--------|
| **Port Collisions** | AGI API on port 8505, Streamlit on 8501-8504 | ✅ Resolved |
| **Database Writes** | Shared tables via Supabase, AGI-specific tables separate | ✅ Resolved |
| **Python Dependencies** | Separate `requirements.txt` in `agi-protocol/` | ✅ Resolved |
| **File Naming** | AGI uses PROJ344 naming convention, extends it | ✅ Resolved |
| **Code Imports** | AGI is self-contained in `agi-protocol/src/` | ✅ Resolved |
| **Docker Conflicts** | Separate docker-compose files, different service names | ✅ Resolved |
| **Git Conflicts** | AGI in dedicated folder, won't touch existing files | ✅ Resolved |

## Deployment Strategy

### Phase 1: Development (Local)

```bash
# Terminal 1: Launch existing dashboards
./scripts/launch-all-dashboards.sh

# Terminal 2: Launch AGI Protocol API
cd agi-protocol
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8505 --reload

# Terminal 3: Run AGI orchestrator tasks
cd agi-protocol
python scripts/run_orchestrator.py --task "draft_motion" --motion-type "ccp_473d"
```

### Phase 2: Production (Docker)

```bash
# Launch entire system
docker-compose -f docker-compose.yml \
               -f agi-protocol/docker/docker-compose.agi.yml \
               up -d

# Access services
- PROJ344 Dashboards: http://localhost:8501-8503
- AGI Protocol API: http://localhost:8505
- AGI API Docs: http://localhost:8505/docs
```

## Migration Path

### Step 1: Create AGI Module Structure (Week 1)

```bash
cd /Users/dbucknor/Repositories/Personal/ASEAGI

# Create AGI Protocol directory
mkdir -p agi-protocol/{src,docs,templates,tests,scripts,docker}
mkdir -p agi-protocol/src/{core,agents,integrations,data,api,utils}
mkdir -p agi-protocol/src/agents/{document_intelligence,legal_research,motion_drafting,evidence,citation,strategic,outreach}

# Move PRD to dedicated location
mv AGI_Protocol_Legal_Defense_System_PRD.md agi-protocol/docs/PRD.md

# Create AGI-specific README
touch agi-protocol/README.md

# Create bridge modules
touch agi-protocol/src/integrations/proj344_bridge.py
touch agi-protocol/src/integrations/supabase_bridge.py
```

### Step 2: Implement Base Infrastructure (Week 1-2)

Priority:
1. `base_agent.py` - Foundation for all agents
2. `proj344_bridge.py` - Connect to existing document scores
3. `orchestrator.py` - Master coordinator
4. `context_manager.py` - Context window optimization

### Step 3: First Agent Implementation (Week 2-3)

Start with Document Intelligence Agent:
- Leverage existing PROJ344 scoring
- Add AGI-specific analysis
- Store results in new `agi_agent_runs` table

### Step 4: API Layer (Week 3-4)

Implement FastAPI:
- Basic endpoints for document processing
- Integration with existing Streamlit dashboards
- Add AGI status dashboard (port 8506)

### Step 5: Full Agent Suite (Week 4-8)

Implement remaining agents:
- Legal Research Agent (with Westlaw)
- Motion Drafting Agent
- Evidence Management Agent
- Citation Verification Agent
- Strategic Analysis Agent
- Public Outreach Agent

## Benefits of This Integration Strategy

### 1. **Zero Disruption to Existing Systems**
- PROJ344 dashboards continue working unchanged
- Existing scanners and workflows unaffected
- No migration required for current data

### 2. **Gradual Rollout**
- Build AGI Protocol incrementally
- Test each agent independently
- Fall back to existing tools if needed

### 3. **Resource Efficiency**
- Reuse existing document scores
- Share Supabase database
- Avoid duplicate processing

### 4. **Clear Separation of Concerns**
- PROJ344: Document intelligence + dashboards
- AGI Protocol: Multi-agent orchestration + motion drafting
- Bridges: Well-defined integration points

### 5. **Future-Proof Architecture**
- AGI Protocol can be extracted as standalone tool
- Can support multiple cases/foundations
- Easy to scale horizontally

## Git Strategy

### Branch Structure

```
main (protected)
├── feature/agi-protocol-base          # Base infrastructure
├── feature/agi-document-agent         # First agent
├── feature/agi-research-agent         # Legal research
├── feature/agi-motion-agent           # Motion drafting
└── feature/agi-api-layer              # FastAPI implementation
```

### Commit Strategy

1. **Commit 1:** Add AGI Protocol PRD + Integration Plan
2. **Commit 2:** Create folder structure
3. **Commit 3:** Implement base agent class
4. **Commit 4+:** Incremental agent implementations

## Testing Strategy

### Unit Tests

```python
# agi-protocol/tests/unit/test_base_agent.py
def test_agent_initialization():
    agent = BaseAgent(agent_id="test", config={})
    assert agent.agent_id == "test"

def test_agent_validation():
    agent = TestAgent(agent_id="test", config={})
    with pytest.raises(ValueError):
        agent.validate_input({})  # Missing required fields
```

### Integration Tests

```python
# agi-protocol/tests/integration/test_proj344_bridge.py
def test_proj344_document_retrieval():
    bridge = PROJ344Bridge()
    scores = bridge.get_document_scores("DOC-001")
    assert 'micro_score' in scores
    assert 0 <= scores['micro_score'] <= 999
```

### End-to-End Tests

```python
# agi-protocol/tests/e2e/test_motion_workflow.py
async def test_complete_motion_drafting_workflow():
    orchestrator = MasterOrchestrator(config={})
    result = await orchestrator.draft_comprehensive_motion(
        motion_type="ccp_473d",
        case_id="ashe-bucknor-j24-00478"
    )
    assert result['success'] == True
    assert 'motion' in result
    assert 'evidence_list' in result
```

## Success Metrics

### Technical Metrics
- ✅ No conflicts with existing PROJ344 systems
- ✅ AGI API response time < 2 seconds
- ✅ Document processing reuses PROJ344 scores
- ✅ All tests passing (unit + integration + e2e)

### Integration Metrics
- ✅ Shared Supabase tables accessible from both systems
- ✅ n8n workflows trigger AGI agents successfully
- ✅ Streamlit dashboards can display AGI results
- ✅ Zero downtime during AGI deployment

### Quality Metrics
- ✅ Motion drafts meet professional standards
- ✅ Citation accuracy > 95%
- ✅ Context window optimization working (< 100K tokens)
- ✅ Agent coordination functioning correctly

## Conclusion

This integration strategy ensures:

1. **Safety:** AGI Protocol cannot break existing PROJ344 systems
2. **Interoperability:** Well-defined bridges enable data sharing
3. **Flexibility:** Can be developed incrementally
4. **Scalability:** Clean architecture supports future growth
5. **Maintainability:** Clear separation of concerns

The AGI Protocol will enhance ASEAGI's capabilities without disrupting the proven PROJ344 document intelligence system. Both systems work in harmony, with AGI Protocol handling complex multi-agent orchestration while leveraging PROJ344's established document scoring infrastructure.

## Next Steps

1. Review and approve this integration plan
2. Create AGI Protocol folder structure
3. Move PRD to `agi-protocol/docs/PRD.md`
4. Commit changes to GitHub
5. Begin Phase 1 implementation (BaseAgent + Document Intelligence Agent)

---

**Ready to build AGI Protocol in harmony with PROJ344.**
