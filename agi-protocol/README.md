# AGI Protocol: Legal Defense Orchestration System

## Overview

The **AGI Protocol** is a comprehensive multi-agent AI system designed to handle complex legal defense work through intelligent orchestration of specialized agents. This system operates as a separate module within the ASEAGI repository, enhancing the existing PROJ344 document intelligence infrastructure with advanced capabilities for motion drafting, legal research, evidence management, and strategic analysis.

## Architecture

### Multi-Agent System

The AGI Protocol consists of a **Master Orchestrator** that coordinates 8 specialized agents:

1. **Document Intelligence Agent** - Process, analyze, and score legal documents
2. **Legal Research Agent** - Conduct comprehensive research via Westlaw
3. **Motion Drafting Agent** - Generate professional-quality legal motions
4. **Evidence Management Agent** - Organize and track evidence strategically
5. **Citation Verification Agent** - Ensure citation accuracy and Bluebook compliance
6. **Strategic Analysis Agent** - Provide high-level case strategy guidance
7. **Public Outreach Agent** - Generate content for foundation and media
8. **Master Orchestrator** - Central coordinator managing all sub-agents

### System Diagram

```
                    ┌─────────────────────────────────┐
                    │   ORCHESTRATION LAYER           │
                    │  (Master Control Agent)         │
                    │  • Task routing                 │
                    │  • Agent spawning               │
                    │  • Context management           │
                    │  • Quality control              │
                    └────────────┬────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
    ┌───▼───┐              ┌────▼────┐            ┌─────▼─────┐
    │DOCUMENT│              │RESEARCH │            │  MOTION   │
    │ AGENT  │              │  AGENT  │            │  AGENT    │
    └───┬───┘              └────┬────┘            └─────┬─────┘
        │                        │                        │
    ┌───▼───┐              ┌────▼────┐            ┌─────▼─────┐
    │EVIDENCE│              │CITATION │            │STRATEGIC  │
    │ AGENT  │              │  AGENT  │            │  AGENT    │
    └───────┘              └─────────┘            └───────────┘
```

## Integration with PROJ344

The AGI Protocol **complements** the existing PROJ344 system:

- **PROJ344**: Document intelligence, scoring, dashboards, scanning
- **AGI Protocol**: Multi-agent orchestration, motion drafting, legal research
- **Bridge**: Shared Supabase database, integrated workflows

See [Integration Guide](../docs/agi-protocol/INTEGRATION_GUIDE.md) for details.

## Tech Stack

```yaml
Core:
  - Python 3.11+
  - Type hints with mypy
  - Async/await for concurrency

AI/ML:
  - Anthropic Claude API (Sonnet 4.5)
  - Local embedding models

Document Processing:
  - Leverages PROJ344 scanning infrastructure
  - Tesseract OCR, PyMuPDF

Data Layer:
  - Supabase (shared with PROJ344)
  - Redis (caching, task queue)
  - Qdrant (vector search)
  - Neo4j (optional, for relationships)

API:
  - FastAPI (REST API on port 8505)
  - Pydantic (data validation)
  - uvicorn (ASGI server)

Workflow:
  - Celery (task queue)
  - Integration with existing n8n workflows
```

## Project Structure

```
agi-protocol/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── .env.example                   # Configuration template
│
├── src/                           # Source code
│   ├── core/                      # Core orchestration
│   │   ├── orchestrator.py        # Master orchestrator
│   │   ├── base_agent.py          # Base class for agents
│   │   ├── context_manager.py     # Context window optimization
│   │   └── workflow_engine.py     # Workflow coordination
│   │
│   ├── agents/                    # Specialized agents
│   │   ├── document_intelligence/
│   │   ├── legal_research/
│   │   ├── motion_drafting/
│   │   ├── evidence/
│   │   ├── citation/
│   │   ├── strategic/
│   │   └── outreach/
│   │
│   ├── integrations/              # Bridge to PROJ344
│   │   ├── proj344_bridge.py      # PROJ344 integration
│   │   ├── supabase_bridge.py     # Database integration
│   │   └── dashboard_api.py       # Dashboard API
│   │
│   ├── data/                      # Data models
│   ├── api/                       # FastAPI application
│   └── utils/                     # Utilities
│
├── docs/                          # Documentation
│   ├── PRD.md                     # Full Product Requirements Doc
│   ├── architecture.md            # System architecture
│   ├── agent_specs/               # Agent specifications
│   └── deployment.md              # Deployment guide
│
├── templates/                     # Legal templates
│   ├── motions/
│   ├── declarations/
│   └── briefs/
│
├── tests/                         # Test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── scripts/                       # Utility scripts
│   ├── setup_agi.py
│   ├── run_orchestrator.py
│   └── process_documents.py
│
└── docker/                        # Docker configuration
    ├── Dockerfile.agi
    └── docker-compose.agi.yml
```

## Quick Start

### Prerequisites

- Python 3.11+
- Existing ASEAGI/PROJ344 installation
- Supabase database (already configured)
- Anthropic API key

### Installation

```bash
# Navigate to AGI Protocol directory
cd agi-protocol

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Configuration

Add to root `.env` file (or create `agi-protocol/.env`):

```bash
# AGI Protocol Configuration
AGI_API_PORT=8505
AGI_MAX_CONTEXT_TOKENS=100000
AGI_DEFAULT_MODEL=claude-sonnet-4.5

# Westlaw API (for Legal Research Agent)
WESTLAW_API_KEY=your_key_here
WESTLAW_CLIENT_ID=your_id_here

# Database URLs
AGI_REDIS_URL=redis://localhost:6379
AGI_VECTOR_DB_URL=http://localhost:6333

# Storage Paths
AGI_DOCUMENT_STORAGE=/path/to/documents
AGI_MOTION_OUTPUT=/path/to/motions
```

### Launch AGI Protocol API

```bash
# From agi-protocol directory
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8505 --reload

# API will be available at:
# - API: http://localhost:8505
# - Docs: http://localhost:8505/docs
# - Redoc: http://localhost:8505/redoc
```

### Run Orchestrator Tasks

```bash
# Process documents
python scripts/process_documents.py --case-id ashe-bucknor-j24-00478

# Draft motion
python scripts/run_orchestrator.py \
    --task draft_motion \
    --motion-type ccp_473d \
    --case-id ashe-bucknor-j24-00478

# Conduct legal research
python scripts/run_orchestrator.py \
    --task research \
    --query "W&I Code 304 exclusive jurisdiction"
```

## Development Roadmap

### Phase 1: Foundation (Weeks 1-4) - CURRENT

- [x] Create folder structure
- [x] Write PRD and integration plan
- [ ] Implement BaseAgent class
- [ ] Build Document Intelligence Agent
- [ ] Create Master Orchestrator
- [ ] Implement Context Window Optimizer

### Phase 2: Enhancement (Weeks 5-8)

- [ ] Legal Research Agent
- [ ] Motion Drafting Agent
- [ ] Evidence Management Agent
- [ ] Citation Verification Agent
- [ ] Strategic Analysis Agent

### Phase 3: Scale (Weeks 9-16)

- [ ] Public Outreach Agent
- [ ] Foundation website integration
- [ ] Legislative advocacy tools
- [ ] Multi-case support

### Phase 4: Enterprise (Weeks 17-24)

- [ ] Full production deployment
- [ ] Cloud infrastructure
- [ ] Multi-tenancy support
- [ ] Advanced analytics

## API Endpoints

Once the FastAPI layer is implemented, the following endpoints will be available:

```
POST   /agents/document/process         # Process document with Document Agent
POST   /agents/research/query           # Conduct legal research
POST   /agents/motion/draft             # Draft legal motion
POST   /agents/evidence/organize        # Organize evidence package
GET    /cases/{case_id}/documents       # Get all case documents
GET    /cases/{case_id}/motions         # Get all drafted motions
GET    /orchestrator/status             # Check orchestrator status
POST   /orchestrator/workflow           # Execute custom workflow
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html
```

## Contributing

This is part of the ASEAGI Legal Case Intelligence system. Development follows these principles:

1. **Modular Design**: Each agent is self-contained
2. **Type Safety**: Full type hints with mypy checking
3. **Testing**: Comprehensive unit, integration, and e2e tests
4. **Documentation**: Every agent has detailed specs
5. **Quality**: Strict verification protocols, no hallucinations

## Documentation

- [Full PRD](docs/PRD.md) - Complete product requirements document
- [Architecture](docs/architecture.md) - System architecture details
- [Agent Specifications](docs/agent_specs/) - Individual agent specs
- [Integration Guide](../docs/agi-protocol/INTEGRATION_GUIDE.md) - PROJ344 integration
- [API Reference](docs/api_reference.md) - FastAPI endpoint documentation
- [Deployment](docs/deployment.md) - Production deployment guide

## Support

For questions or issues:
- Review documentation in `docs/`
- Check [Integration Plan](../AGI_PROTOCOL_INTEGRATION_PLAN.md)
- Open an issue on GitHub

## Mission

**"No child's voice should be silenced by litigation. No protective parent should be punished for protecting."**

The AGI Protocol was designed to ensure:
- Professional-quality legal work at unprecedented speed
- No critical evidence is ever missed
- Legal arguments are comprehensive and well-cited
- Protective parents have institutional-grade tools
- Truth prevails over legal manipulation

---

**For Ashe. For Justice. For All Children.** 🛡️

**Version:** 1.0
**Status:** Phase 1 - Foundation
**Last Updated:** November 2025
