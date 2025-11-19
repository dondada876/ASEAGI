# Timeline Hub - Integration Boundaries & Guidelines

**Version:** 1.0
**Date:** 2025-11-17
**Purpose:** Define safe integration patterns and boundaries
**Status:** Official Integration Policy

---

## 🎯 Integration Philosophy

**Timeline Hub is designed to be:**
- ✅ **Independently Deployable** - Works without any other ASEAGI systems
- ✅ **Optionally Integrable** - Can link to other systems via soft references
- ✅ **Never Dependent** - Never requires external tables to function
- ✅ **Safely Removable** - Can be rolled back without affecting other systems

**Key Principle:** Timeline Hub is a **standalone system** that can OPTIONALLY receive data from or provide data to other ASEAGI components, but NEVER depends on them.

---

## 🔒 Non-Negotiable Boundaries

### What Timeline Hub WILL NEVER DO:

1. ❌ **Create foreign key constraints to external tables**
   - No FK to `legal_documents.id`
   - No FK to `bugs.id`
   - No FK to `document_statements.id`
   - No FK to any production ASEAGI table

2. ❌ **Require external tables to function**
   - Must work even if `legal_documents` doesn't exist
   - Must work even if criminal complaint system isn't deployed
   - Must work in a fresh Supabase project with no other tables

3. ❌ **Modify or write to external tables**
   - Cannot INSERT into `legal_documents`
   - Cannot UPDATE `bugs` table
   - Cannot DELETE from production tables
   - Read-only access to external systems (if integrated)

4. ❌ **Block removal or rollback**
   - Rolling back timeline hub must never break other systems
   - No cascading deletes to production data
   - Clean removal via `002_rollback.sql`

5. ❌ **Share critical functions other systems depend on**
   - Helper functions are timeline hub internal only
   - No shared stored procedures with production systems
   - No shared triggers

---

## ✅ Allowed Integration Patterns

### 1. Soft Reference Linking (Recommended)

**Mechanism:** Use nullable UUID fields without foreign key constraints

**Example:**
```sql
-- In timeline_events table
source_external_id UUID NULL  -- Soft link to legal_documents.id (no FK)
```

**Benefits:**
- Timeline hub works with or without external IDs
- External tables can be deleted without affecting timeline
- Timeline can be rolled back without affecting external tables
- Optional cross-referencing when both systems exist

**Use Cases:**
- Link timeline event to source legal document
- Reference criminal complaint from timeline event
- Connect to bug tracking system for error correlation

**Implementation:**
```python
# When processing a legal document
event_record = {
    'event_type': 'COURT_HEARING',
    'event_date': '2024-08-12',
    'event_title': 'Dependency Hearing',
    'source_external_id': legal_doc_id,  # Optional soft link
    # ... other fields
}
supabase.table('timeline_events').insert(event_record).execute()
```

### 2. Read-Only Queries (Safe)

**Mechanism:** Timeline hub queries can READ from external tables

**Example:**
```python
# Timeline dashboard can query legal_documents if it exists
try:
    legal_docs = supabase.table('legal_documents').select('*').execute()
    # Use for enhanced display
except Exception:
    # Gracefully degrade if table doesn't exist
    legal_docs = None
```

**Benefits:**
- Enhanced functionality when external systems exist
- Graceful degradation when they don't
- No hard dependencies created

**Use Cases:**
- Dashboard shows legal document titles for events with source_external_id
- Analyzer correlates timeline events with complaint data
- Statistics include document type breakdown

**Implementation Guidelines:**
```python
def get_event_with_source_document(event_id):
    """Get event with optional legal document details"""
    # Get event (always works)
    event = supabase.table('timeline_events')\
        .select('*')\
        .eq('id', event_id)\
        .single()\
        .execute()

    # Try to get source document (optional)
    if event.data.get('source_external_id'):
        try:
            doc = supabase.table('legal_documents')\
                .select('file_name, document_type')\
                .eq('id', event.data['source_external_id'])\
                .single()\
                .execute()
            event.data['source_document'] = doc.data
        except Exception:
            # Legal documents table doesn't exist or doc not found
            event.data['source_document'] = None

    return event.data
```

### 3. Event Publishing (One-Way Data Flow)

**Mechanism:** Other systems INSERT into timeline hub tables

**Example:**
```python
# Criminal complaint analyzer publishes findings to timeline
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Analyzer discovers false statement
false_stmt_event = {
    'event_type': 'DECLARATION_FILED',
    'event_date': '2024-08-12',
    'event_title': 'Mother files false Jamaica claim',
    'contains_false_statement': True,
    'source_external_id': complaint_id,  # Optional link
    'keywords': ['jamaica', 'false statement', 'perjury']
}

supabase.table('timeline_events').insert(false_stmt_event).execute()
```

**Benefits:**
- Multiple systems can contribute to timeline
- Timeline becomes central event log
- Each system remains independently deployable

**Use Cases:**
- Document scanner publishes events after processing
- Criminal complaint system publishes perjury detections
- Bug tracker publishes system errors to timeline
- Telegram bot publishes uploaded documents

**Permitted Publishers:**
| System | Can Publish To | Purpose |
|--------|---------------|---------|
| Document Processor | timeline_events, timeline_communications | Upload documents and extract events |
| Telegram Bot | timeline_events, timeline_communications | User-uploaded screenshots |
| Criminal Complaint Analyzer | timeline_events, timeline_relationships | Perjury detections and contradictions |
| Bug Tracker | timeline_processing_queue | Processing errors and retries |
| Dashboard | ❌ None (read-only) | Dashboards should never write |

### 4. Query APIs (Timeline as Data Source)

**Mechanism:** Other systems query timeline hub for analysis

**Example:**
```python
# Criminal complaint analyzer queries timeline for contradiction detection
def find_jamaica_mentions(date_range_start, date_range_end):
    """Query timeline for Jamaica mentions to detect false statements"""
    events = supabase.table('timeline_events')\
        .select('*')\
        .gte('event_date', date_range_start)\
        .lte('event_date', date_range_end)\
        .ilike('event_description', '%jamaica%')\
        .execute()

    return events.data
```

**Benefits:**
- Timeline becomes queryable fact repository
- Other systems leverage timeline data for analysis
- No tight coupling required

**Use Cases:**
- Complaint analyzer queries timeline for statement verification
- Dashboard displays event statistics
- Reports pull timeline data for narrative building
- Export tools generate chronologies

**Permitted Consumers:**
| System | Can Query | Purpose |
|--------|-----------|---------|
| Criminal Complaint Analyzer | timeline_events, timeline_communications | Contradiction detection |
| Dashboards | All timeline tables | Visualization and reporting |
| Export Tools | All timeline tables | PDF/Word report generation |
| Search Tools | timeline_events (search_vector) | Full-text search |

---

## 🏗️ Integration Architecture Patterns

### Pattern 1: Hub-and-Spoke (Recommended)

```
                    Timeline Hub (Central)
                           |
        +------------------+------------------+
        |                  |                  |
   Document          Criminal            Telegram
   Processor         Complaint             Bot
   (Publisher)       (Publisher +      (Publisher)
                     Consumer)
```

**How it works:**
- Timeline hub is the central event repository
- Other systems publish events TO timeline hub
- Other systems query events FROM timeline hub
- No system depends on timeline hub existing
- Timeline hub doesn't depend on any other system

**Benefits:**
- Clear data flow
- Easy to understand
- Simple to debug
- Safe to modify any component

### Pattern 2: Optional Enhancement

```
Timeline Hub (Standalone)
    |
    +---> Optional Link to legal_documents
    |     (via source_external_id)
    |
    +---> Optional Link to criminal_complaints
          (via source_external_id)
```

**How it works:**
- Timeline hub functions perfectly alone
- When legal_documents exists, timeline can link to it
- When criminal complaints exist, timeline can correlate
- If either is removed, timeline continues working

**Benefits:**
- Progressive enhancement
- Graceful degradation
- Safe deployment order
- Easy rollback

### Pattern 3: Microservices Communication (Future)

```
Timeline Hub API ←→ REST/GraphQL ←→ External Systems
```

**How it works:**
- Timeline hub exposes API endpoints
- Other services call endpoints to read/write
- Clear contract-based integration
- No direct database coupling

**Benefits:**
- Technology agnostic
- Network isolation
- Clear versioning
- Easy to swap implementations

---

## 📝 Integration Contract Template

When integrating a new system with timeline hub, use this contract:

### System Integration Contract

**System Name:** [Your System Name]
**Integration Type:** [ ] Publisher [ ] Consumer [ ] Both
**Timeline Tables Accessed:** [List tables: timeline_events, etc.]
**External Tables Referenced:** [List any non-timeline tables]

#### Write Operations (if Publisher)
- **Inserts to:** [timeline_events / timeline_communications / etc.]
- **Updates to:** [None recommended]
- **Deletes from:** [None recommended]
- **Frequency:** [Per document / hourly / on-demand / etc.]

#### Read Operations (if Consumer)
- **Queries:** [Describe query patterns]
- **Frequency:** [Real-time / batch / dashboard refresh / etc.]
- **Fallback if timeline hub doesn't exist:** [Describe graceful degradation]

#### Dependencies
- **Required tables:** [None - timeline hub must work standalone]
- **Optional tables:** [legal_documents, etc. with soft references]
- **Can function if timeline hub is removed:** [ ] Yes [ ] No

#### Rollback Safety
- **Timeline hub rollback affects this system:** [ ] Yes [ ] No
- **This system rollback affects timeline hub:** [ ] Yes [ ] No
- **Safe removal order:** [Describe]

**Approval:** ✅ Follows integration boundaries
**Date:** [YYYY-MM-DD]

---

## 🚨 Integration Anti-Patterns (DO NOT DO)

### ❌ Anti-Pattern 1: Hard Foreign Key Dependency

**Bad:**
```sql
CREATE TABLE timeline_events (
    id UUID PRIMARY KEY,
    source_document_id UUID NOT NULL REFERENCES legal_documents(id)  -- ❌ BAD
);
```

**Why it's bad:**
- Timeline hub can't function without legal_documents table
- Can't deploy timeline hub to fresh database
- Can't roll back legal_documents without breaking timeline
- Violates independence principle

**Good Alternative:**
```sql
CREATE TABLE timeline_events (
    id UUID PRIMARY KEY,
    source_external_id UUID NULL  -- ✅ GOOD - Optional, no FK constraint
);
```

### ❌ Anti-Pattern 2: Shared Critical Functions

**Bad:**
```python
# In timeline_hub/utils.py
def calculate_importance_score(event):
    """This function is used by both timeline hub AND criminal complaint system"""
    # If timeline hub is removed, complaint system breaks ❌
    pass
```

**Why it's bad:**
- Creates hidden dependency
- Removing timeline hub breaks other systems
- Hard to track dependencies

**Good Alternative:**
```python
# Each system has its own copy of shared logic
# timeline_hub/utils.py
def calculate_timeline_importance(event):
    """Timeline hub's importance calculator"""
    pass

# criminal_complaint/utils.py
def calculate_complaint_importance(complaint):
    """Complaint system's importance calculator (can differ)"""
    pass
```

### ❌ Anti-Pattern 3: Cascading Deletes to External Tables

**Bad:**
```sql
-- Timeline event deletion triggers external table deletion
CREATE TRIGGER delete_source_document
AFTER DELETE ON timeline_events
FOR EACH ROW
EXECUTE FUNCTION delete_legal_document();  -- ❌ Deletes production data!
```

**Why it's bad:**
- Rolling back timeline hub deletes production legal documents
- Catastrophic data loss risk
- Violates separation of concerns

**Good Alternative:**
```sql
-- No triggers that affect external tables
-- Timeline hub rollback only affects timeline_ tables
```

### ❌ Anti-Pattern 4: Required External Configuration

**Bad:**
```python
# timeline_hub/config.py
LEGAL_DOCUMENTS_TABLE = 'legal_documents'  # Required to exist ❌
COMPLAINT_SYSTEM_API = 'http://complaints.local'  # Required ❌

def init_timeline():
    # Fails if external systems don't exist
    check_table_exists(LEGAL_DOCUMENTS_TABLE)  # ❌ Breaks in isolation
    ping_api(COMPLAINT_SYSTEM_API)  # ❌ Fails if complaint system down
```

**Why it's bad:**
- Can't deploy timeline hub independently
- Can't test in isolation
- Breaks if external systems are down

**Good Alternative:**
```python
# timeline_hub/config.py
OPTIONAL_INTEGRATIONS = {
    'legal_documents': {
        'enabled': False,  # ✅ Disabled by default
        'table_name': 'legal_documents'
    },
    'complaint_system': {
        'enabled': False,  # ✅ Optional
        'api_url': None
    }
}

def init_timeline():
    # Works independently
    setup_timeline_tables()

    # Optional: Check for integrations
    if can_integrate_with('legal_documents'):
        enable_document_linking()  # ✅ Optional enhancement
```

---

## 📊 Integration Decision Matrix

Use this matrix to evaluate proposed integrations:

| Integration Proposal | Allowed? | Reasoning |
|---------------------|----------|-----------|
| Timeline hub reads from legal_documents | ✅ Yes | Read-only, graceful degradation |
| Timeline hub has FK to legal_documents | ❌ No | Creates hard dependency |
| Document processor writes to timeline_events | ✅ Yes | Publisher pattern, one-way flow |
| Timeline hub updates legal_documents | ❌ No | Violates read-only principle |
| Timeline hub uses source_external_id (nullable) | ✅ Yes | Soft reference, optional |
| Shared trigger between systems | ❌ No | Hidden coupling |
| Criminal complaint queries timeline | ✅ Yes | Consumer pattern, timeline as API |
| Timeline hub requires complaint system | ❌ No | Must work independently |
| Telegram bot inserts to timeline_communications | ✅ Yes | Publisher pattern |
| Timeline hub deletes from legal_documents | ❌ No | Never modify external tables |

---

## 🧪 Integration Testing Checklist

Before deploying an integration, verify:

- [ ] Timeline hub works without the external system
- [ ] External system works without timeline hub
- [ ] Timeline hub rollback doesn't affect external system
- [ ] External system rollback doesn't affect timeline hub
- [ ] No foreign key constraints to external tables
- [ ] All external references are nullable
- [ ] Queries include try/except for missing tables
- [ ] Documentation updated with integration details
- [ ] Integration contract created and approved
- [ ] Rollback procedure documented and tested

---

## 🔮 Future Integration Scenarios

### Scenario 1: Criminal Complaint Integration (Planned)

**Goal:** Link timeline events to false statement complaints

**Safe Integration:**
```python
# In criminal complaint analyzer
def analyze_complaint(complaint_id):
    # Query timeline for contradiction detection
    events = supabase.table('timeline_events')\
        .select('*')\
        .contains('keywords', ['jamaica'])\
        .execute()

    # Publish perjury detection to timeline
    perjury_event = {
        'event_type': 'VIOLATION_DETECTED',
        'event_title': 'Perjury detected in Jamaica claim',
        'source_external_id': complaint_id,  # Soft link
        'contains_false_statement': True
    }
    supabase.table('timeline_events').insert(perjury_event).execute()
```

**Boundaries Maintained:**
- ✅ Timeline works without complaint system
- ✅ Complaint system works without timeline
- ✅ Optional soft linking via source_external_id
- ✅ One-way data flow (complaint → timeline)

### Scenario 2: Dashboard Integration (Current)

**Goal:** Visualize timeline data in dashboard

**Safe Integration:**
```python
# In timeline dashboard
@st.cache_data(ttl=30)
def get_timeline_data():
    # Always works - only queries timeline tables
    events = supabase.table('timeline_events').select('*').execute()

    # Optional enhancement
    if legal_documents_table_exists():
        # Show document titles for events with source_external_id
        for event in events.data:
            if event.get('source_external_id'):
                try:
                    doc = get_legal_document(event['source_external_id'])
                    event['source_doc_title'] = doc['file_name']
                except:
                    event['source_doc_title'] = 'Unknown'

    return events.data
```

**Boundaries Maintained:**
- ✅ Dashboard works without legal_documents
- ✅ Enhanced display when legal_documents exists
- ✅ Graceful degradation
- ✅ Read-only access

### Scenario 3: Export Tool Integration (Future)

**Goal:** Generate PDF reports from timeline

**Safe Integration:**
```python
# In export tool
def generate_timeline_report(start_date, end_date):
    # Query timeline hub (consumer pattern)
    events = supabase.table('timeline_events')\
        .select('*')\
        .gte('event_date', start_date)\
        .lte('event_date', end_date)\
        .order('event_date')\
        .execute()

    # Optional: Enhance with legal document details
    for event in events.data:
        if event.get('source_external_id'):
            try:
                doc = get_legal_document(event['source_external_id'])
                event['source_file'] = doc['file_name']
            except:
                event['source_file'] = 'Not available'

    # Generate PDF
    return create_pdf_report(events.data)
```

**Boundaries Maintained:**
- ✅ Export tool only reads from timeline
- ✅ Works without legal_documents (degraded)
- ✅ No writes to timeline tables
- ✅ Can be removed without affecting timeline

---

## 📞 Integration Support

### Before Integrating

1. Read this entire document
2. Review SEGMENTATION_VERIFICATION.md
3. Create integration contract (template above)
4. Test in isolation first
5. Test rollback scenarios

### Questions to Ask

- **Does my integration require timeline hub to exist?** ❌ Should be No
- **Does timeline hub require my system to exist?** ❌ Should be No
- **Can I remove my system without breaking timeline hub?** ✅ Should be Yes
- **Can I remove timeline hub without breaking my system?** ✅ Should be Yes
- **Am I using soft references (nullable) instead of FKs?** ✅ Should be Yes

### Integration Review

Before deploying production integration:
1. Submit integration contract
2. Review with system architect
3. Test independence scenarios
4. Test rollback scenarios
5. Document integration in CHANGELOG.md

---

## ✅ Integration Approval Checklist

- [ ] Integration contract completed
- [ ] No foreign key constraints to external tables
- [ ] Timeline hub works without external system
- [ ] External system works without timeline hub
- [ ] Soft references used (source_external_id pattern)
- [ ] Graceful degradation implemented
- [ ] Rollback tested (both directions)
- [ ] Documentation updated
- [ ] Tests passing
- [ ] No anti-patterns detected

**Approved by:** _________________
**Date:** __________

---

**Remember:** Timeline Hub is a **standalone system** that can OPTIONALLY integrate, but NEVER depends on other systems.

**For Ashe. For Justice. For Timeline Truth.** 📅⚖️
