# Framework Comparison Guide for ASEAGI

## 🎯 Overview

This guide compares different frameworks and tools used in ASEAGI to help you choose the right tool for each task.

---

## 📊 Dashboard Frameworks

### **Streamlit** ⭐ **Currently Used**

**What it is:** Python framework for building data dashboards with minimal code

**Pros:**
- ✅ Very fast development (5-10x faster than traditional web frameworks)
- ✅ Native Python - no HTML/CSS/JavaScript needed
- ✅ Auto-refreshes on code changes
- ✅ Built-in caching with `@st.cache_data`
- ✅ Great for data visualization (Plotly, Altair support)
- ✅ Perfect for internal tools and prototypes

**Cons:**
- ❌ Limited customization (harder to match exact designs)
- ❌ Can be slow with large datasets (need caching strategies)
- ❌ Single-user focused (multi-user requires session state management)
- ❌ Not great for public-facing production apps

**Best for:**
- Internal dashboards (current: 7 dashboards on ports 8501-8507)
- Data exploration and visualization
- Rapid prototyping
- Admin panels

**Example:**
```python
import streamlit as st

st.title("Legal Intelligence Dashboard")
docs = get_documents()
st.dataframe(docs)
```

---

### **Dash (Plotly)**

**What it is:** React-based Python framework for analytical web applications

**Pros:**
- ✅ More control than Streamlit
- ✅ Better for complex layouts
- ✅ Production-ready
- ✅ Great for interactive visualizations

**Cons:**
- ❌ Steeper learning curve
- ❌ More boilerplate code
- ❌ Requires understanding of callbacks

**Best for:**
- Production dashboards with complex interactions
- When you need more control than Streamlit
- Multi-page analytical apps

**When to switch:**
- If Streamlit performance becomes a bottleneck
- If you need more granular control over UI
- If deploying to external users at scale

---

### **Gradio**

**What it is:** Framework for building ML model demos and interactive apps

**Pros:**
- ✅ Even simpler than Streamlit for ML demos
- ✅ Great for prototyping ML interfaces
- ✅ Easy to share (built-in public URL)

**Cons:**
- ❌ Less flexible than Streamlit
- ❌ Focused on ML demos, not general dashboards

**Best for:**
- ML model demos
- Quick prototypes to share with non-technical users
- Testing model outputs

**Use case in ASEAGI:**
- Could use for testing document scoring models
- Demo OCR processing
- Test legal document classification

---

## 🗄️ Database Options

### **Supabase** ⭐ **Currently Used**

**What it is:** Open-source Firebase alternative (PostgreSQL + REST API)

**Pros:**
- ✅ PostgreSQL under the hood (powerful SQL)
- ✅ Real-time subscriptions
- ✅ Built-in authentication
- ✅ Auto-generated REST API
- ✅ Row-level security
- ✅ Generous free tier

**Cons:**
- ❌ Vendor lock-in (though can self-host)
- ❌ Limited complex queries via REST API
- ❌ Need to use raw SQL for advanced features

**Current tables:**
- legal_documents (745 rows)
- court_events (253 rows)
- bugs (179 rows)
- + 8 more system tables

**Best for:**
- MVP and prototyping (current use)
- Apps needing auth + database
- Real-time features

---

### **PostgreSQL (Self-hosted)**

**What it is:** Open-source relational database

**Pros:**
- ✅ No vendor lock-in
- ✅ Full control
- ✅ All PostgreSQL features
- ✅ Better for complex queries

**Cons:**
- ❌ Need to manage hosting
- ❌ Need to build own API
- ❌ More DevOps overhead

**When to switch:**
- When outgrowing Supabase free tier
- Need advanced PostgreSQL features
- Want full data ownership

---

### **SQLite**

**What it is:** Embedded file-based database

**Pros:**
- ✅ Zero configuration
- ✅ Perfect for local development
- ✅ Single file (easy backups)
- ✅ Very fast for small datasets

**Cons:**
- ❌ Not for multi-user production
- ❌ Limited concurrency
- ❌ No built-in auth

**Best for:**
- Local development and testing
- Single-user desktop apps
- Embedded in scripts

---

## 🤖 AI Framework Comparison

### **Anthropic Claude API** ⭐ **Currently Used**

**What it is:** Direct API access to Claude models

**Current usage:**
- Telegram bot using Claude 3.5 Sonnet
- Document analysis
- Legal document scoring

**Pros:**
- ✅ Latest models immediately
- ✅ 200K context window
- ✅ Best for legal/document analysis
- ✅ Strong instruction following

**Cons:**
- ❌ Pay per token
- ❌ Rate limits on free tier
- ❌ Internet required

**Cost:** ~$3 per 1M input tokens, $15 per 1M output tokens

---

### **LangChain**

**What it is:** Framework for building LLM applications

**Pros:**
- ✅ Abstracts away API differences
- ✅ Built-in vector stores, chains, agents
- ✅ Good for complex workflows
- ✅ Ecosystem of integrations

**Cons:**
- ❌ Adds complexity layer
- ❌ Frequent breaking changes
- ❌ Can be overkill for simple use cases

**When to use:**
- Multi-step LLM workflows
- Need to switch between LLM providers
- Building retrieval-augmented generation (RAG)

**Use case in ASEAGI:**
- Could use for document Q&A with vector search
- Chaining analysis tasks
- Agent-based document processing

---

### **LlamaIndex**

**What it is:** Framework for LLM data ingestion and querying

**Pros:**
- ✅ Specialized for document/data indexing
- ✅ Better for RAG than LangChain
- ✅ Multiple index types

**Cons:**
- ❌ Focused mainly on RAG
- ❌ Less general than LangChain

**Best for:**
- Building search over large document collections
- RAG applications
- Data ingestion pipelines

**Use case in ASEAGI:**
- Could index all 745 legal documents for semantic search
- Answer questions about case law
- Find similar documents

---

## 🔌 Integration Frameworks

### **MCP (Model Context Protocol)**

**What it is:** Open protocol by Anthropic for AI integration with external systems

**Current status:**
- Found in git history (commit f6c9569) but not in current branch
- MCP server exists at https://glama.ai/mcp/servers/@harsh-softsolvers/mcp (Vtiger)

**Pros:**
- ✅ Standardized way to connect AI to tools
- ✅ Natural language interface to systems
- ✅ Growing ecosystem
- ✅ Reusable across AI applications

**Cons:**
- ❌ Still new (launched Oct 2024)
- ❌ Limited server availability
- ❌ Requires server implementation

**Use cases in ASEAGI:**
1. **Vtiger MCP Server**: Natural language CRM queries
   - "Show me open high-priority tickets"
   - "Create ticket for bug #179"

2. **Playwright MCP Server**: Browser automation testing
   - "Test all dashboard ports"
   - "Take screenshots of each dashboard"

3. **Filesystem MCP Server**: File operations
   - "List all Python files in dashboards/"
   - "Search for TODO comments"

**When to implement:**
- Want natural language interface to existing systems
- Building AI agents that need tool access
- Standardizing integrations

---

### **REST APIs** ⭐ **Currently Used**

**What it is:** Traditional HTTP-based APIs

**Current usage:**
- Supabase REST API
- Vtiger REST API (`integrations/vtiger_sync.py`)
- WordPress REST API (in PROJ344 upload)

**Pros:**
- ✅ Well-understood
- ✅ Works everywhere
- ✅ Direct control
- ✅ No additional dependencies

**Cons:**
- ❌ More code to write
- ❌ Manual error handling
- ❌ No type safety

**Best for:**
- Production integrations
- When MCP servers don't exist
- Need full control

---

## 🧪 Testing Frameworks

### **Playwright** (Requested but not found in repo)

**What it is:** Browser automation and testing framework

**Pros:**
- ✅ Cross-browser testing
- ✅ Can test Streamlit dashboards
- ✅ Screenshot and video recording
- ✅ Reliable and fast

**Cons:**
- ❌ Requires browser installation
- ❌ More complex than unit tests

**Use case for ASEAGI:**
```python
# Test dashboard ports show unique content
async def test_legal_intelligence_dashboard():
    page = await browser.new_page()
    await page.goto("http://localhost:8503")

    # Verify it shows high-value docs
    content = await page.content()
    assert "relevancy ≥ 700" in content
    assert "745 documents" not in content  # Should NOT show all docs
```

**Should implement?**
- ✅ YES - Would catch the current duplication bug automatically
- ✅ YES - Can verify port 8507 shows System Overview, not PROJ344 Master
- ✅ YES - Automated testing before deployment

---

### **pytest**

**What it is:** Python testing framework

**Best for:**
- Unit tests for core logic
- API integration tests
- Database query tests

**Example:**
```python
def test_legal_intelligence_filter():
    """Test that legal intelligence only gets high-value docs"""
    docs = get_all_documents(client)

    # All docs should have relevancy >= 700
    assert all(doc['relevancy_number'] >= 700 for doc in docs)
```

---

## 🔄 Background Task Processing

### **systemd** ⭐ **Currently Used**

**What it is:** Linux service manager

**Current usage:**
- Dashboards as background processes (nohup + &)

**Pros:**
- ✅ Built into Linux
- ✅ Auto-restart on failure
- ✅ Logging

**Cons:**
- ❌ Linux-only
- ❌ Manual service file creation

---

### **Supervisor**

**What it is:** Process control system

**Pros:**
- ✅ Simpler config than systemd
- ✅ Web UI for monitoring
- ✅ Auto-restart

**When to use:**
- Need centralized process management
- Want web-based monitoring

**Example config:**
```ini
[program:dashboard_8501]
command=streamlit run proj344_master_dashboard.py --server.port 8501
directory=/root/ASEAGI/dashboards
autostart=true
autorestart=true
```

---

### **Docker Compose** (Partially used)

**Current usage:**
- Bug tracker deployed via Docker

**Pros:**
- ✅ Isolated environments
- ✅ Easy deployment
- ✅ Reproducible

**Cons:**
- ❌ Overhead for simple apps
- ❌ Need to rebuild on changes

**Should expand?**
- ✅ YES - Containerize all 7 dashboards
- ✅ YES - Consistent deployment
- ✅ YES - Easier to manage

---

## 🎨 UI/Design Tools

### **Figma**

**What it is:** Design and prototyping tool

**Current usage:**
- Dashboard designs referenced in CLAUDE.md
- Figma file IDs in documentation

**Workflow:**
1. Design in Figma
2. Implement in Streamlit
3. Match colors/layout as closely as possible

**Challenge:** Streamlit has limited styling, can't perfectly match Figma

---

### **Streamlit Custom Components**

**What it is:** React components embedded in Streamlit

**When to use:**
- Need exact Figma match
- Streamlit built-ins insufficient
- Custom interactive widgets

**Examples:**
- Custom timeline visualizations
- Interactive document viewers
- Advanced charts

---

## 📝 Recommendations by Use Case

### **Internal Dashboards** ⭐ **Current Need**
- **Framework:** Streamlit (current choice is correct)
- **Database:** Supabase (good for MVP)
- **Testing:** Add Playwright tests
- **Deployment:** Consider Docker Compose for all dashboards

### **External Client Dashboards**
- **Framework:** Dash or Next.js (more control)
- **Database:** Self-hosted PostgreSQL
- **Testing:** Playwright + pytest
- **Deployment:** Docker + NGINX

### **Document Processing Pipeline**
- **AI:** Claude API (current is good)
- **Framework:** Consider LlamaIndex for RAG
- **Database:** PostgreSQL with pgvector for embeddings
- **Testing:** pytest

### **CRM Integration**
- **Current:** REST API (works well)
- **Future:** Vtiger MCP Server for natural language
- **Testing:** Integration tests

---

## 🚀 Migration Paths

### **From Streamlit to Dash**
**When:** Outgrow Streamlit's limitations
**Effort:** Medium (rewrite UI logic)
**Keep:** Data processing code, database queries

### **From Supabase to Self-hosted PostgreSQL**
**When:** Need advanced features or cost savings
**Effort:** Low (just connection string change + auth layer)
**Keep:** All SQL queries

### **Add LlamaIndex for Document Search**
**When:** Need semantic search over 745 documents
**Effort:** Medium (index creation + API)
**Keep:** Existing document processing

### **Implement MCP Servers**
**When:** Want natural language interfaces
**Effort:** High (server implementation)
**Value:** Enables AI agent workflows

---

## 📊 Decision Matrix

| Need | Current Solution | Alternative | When to Switch |
|------|-----------------|-------------|----------------|
| Internal dashboards | Streamlit ✅ | Dash | Need more control |
| Database | Supabase ✅ | PostgreSQL | >10K documents |
| AI API | Claude ✅ | OpenAI | Cost concerns |
| Document search | Manual | LlamaIndex | >1K documents |
| CRM integration | REST API ✅ | MCP Server | Want AI interface |
| Testing | Manual ❌ | Playwright | ASAP |
| Deployment | nohup ❌ | Docker Compose | ASAP |
| Background jobs | None ❌ | Celery | Need task queue |

---

## 🎯 Immediate Recommendations

### **High Priority**

1. **Add Playwright tests**
   - Would have caught the port 8507 duplication bug
   - Automated regression testing
   - **Effort:** 2-3 hours

2. **Docker Compose for dashboards**
   - Consistent deployment
   - Easy rollback
   - Auto-restart on failure
   - **Effort:** 4-6 hours

3. **Implement Vtiger MCP Server**
   - Already exists at https://glama.ai/mcp/servers/@harsh-softsolvers/mcp
   - Natural language CRM queries
   - **Effort:** 2-3 hours

### **Medium Priority**

4. **Add pytest unit tests**
   - Test database queries
   - Test data transformations
   - **Effort:** Ongoing

5. **Consider LlamaIndex for document search**
   - Semantic search over 745 legal documents
   - Q&A over document corpus
   - **Effort:** 1-2 days

### **Low Priority**

6. **Migrate to self-hosted PostgreSQL**
   - Only if Supabase becomes limiting
   - **Effort:** 1 day

7. **Evaluate Dash for public dashboards**
   - Only for external-facing apps
   - **Effort:** 2-3 days per dashboard

---

## 📚 Resources

**Streamlit:**
- Docs: https://docs.streamlit.io
- Gallery: https://streamlit.io/gallery

**Playwright:**
- Docs: https://playwright.dev/python
- MCP Server: https://github.com/ModelContextProtocol/servers

**MCP (Model Context Protocol):**
- Spec: https://modelcontextprotocol.io
- Servers: https://glama.ai/mcp/servers
- Vtiger MCP: https://glama.ai/mcp/servers/@harsh-softsolvers/mcp

**LlamaIndex:**
- Docs: https://docs.llamaindex.ai
- RAG tutorial: https://docs.llamaindex.ai/en/stable/getting_started/starter_example.html

**Docker Compose:**
- Docs: https://docs.docker.com/compose
- Best practices: https://docs.docker.com/develop/dev-best-practices

---

## 🔄 Version History

- **v1.0** (Nov 13, 2025): Initial framework comparison guide
- Covers dashboards, databases, AI, testing, deployment
- Recommendations based on current ASEAGI architecture

---

**Last Updated:** November 13, 2025
**Branch:** `claude/framework-comparison-guide-011CUyvuditeFNvRT8iUjHoC`
