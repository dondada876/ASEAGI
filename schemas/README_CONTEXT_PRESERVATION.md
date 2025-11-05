# Context Preservation & State Management System

**Created:** 2025-11-05
**Purpose:** Save all dashboard processing results, AI analysis, and system state to Supabase for efficient querying and context preservation

---

## 🎯 Overview

This system provides comprehensive state management and caching for the PROJ344 legal intelligence platform. It eliminates the need to reprocess expensive operations by storing results in Supabase for fast retrieval.

### Key Benefits:

✅ **Context Preservation** - Save full conversation and analysis context
✅ **Processing Cache** - Avoid recomputing expensive AI analyses
✅ **Dashboard Snapshots** - Save and restore complete dashboard states
✅ **Truth Score History** - Track all truth scores with 5W+H context
✅ **Justice Score Rollups** - Calculate and store justice scores
✅ **Cost Tracking** - Monitor AI API costs and token usage
✅ **Query Optimization** - Cache expensive database queries

---

## 📊 Database Schema

### Tables Created (8 Total):

| Table | Purpose | Key Features |
|-------|---------|--------------|
| `system_processing_cache` | Cache expensive AI results | Auto-expiration, hit counting |
| `dashboard_snapshots` | Full dashboard state saves | Filters, metrics, auto-snapshots |
| `ai_analysis_results` | AI model outputs | Cost tracking, token usage |
| `query_results_cache` | Database query caching | Expiration, execution timing |
| `truth_score_history` | All truth scores | 5W+H tracking, evidence links |
| `justice_score_rollups` | Justice score calculations | Weighted averages, breakdowns |
| `processing_jobs_log` | Long-running job tracking | Progress, status, cost |
| `context_preservation_metadata` | Conversation context | Token estimation, archiving |

### Views Created (5 Total):

- `active_cache_entries` - Non-expired cache entries
- `recent_dashboard_snapshots` - Last 100 snapshots
- `truth_score_summary` - Truth scores by category
- `processing_cost_summary` - AI processing costs
- `active_processing_jobs` - Currently running jobs

### Functions Created (3 Total):

- `clean_expired_cache()` - Remove expired cache entries
- `increment_cache_hit(cache_key)` - Increment hit counter
- `archive_old_contexts(days_old)` - Archive old context data

---

## 🚀 Deployment

### Step 1: Deploy Schema to Supabase

```bash
# Run the deployment helper (informational only)
python schemas/deploy_context_schema.py
```

**Manual Deployment Required:**

1. Go to Supabase SQL Editor: https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu/sql
2. Click **"New Query"**
3. Copy contents of `schemas/context_preservation_schema.sql`
4. Paste into editor
5. Click **"Run"** to execute

### Step 2: Verify Deployment

```sql
-- Check tables were created
SELECT tablename FROM pg_tables
WHERE schemaname = 'public'
AND tablename LIKE '%cache%' OR tablename LIKE '%snapshot%'
OR tablename LIKE '%truth%' OR tablename LIKE '%justice%'
ORDER BY tablename;

-- Should show 8 new tables
```

### Step 3: Test Context Manager

```bash
python utilities/context_manager.py
```

---

## 💻 Usage Examples

### Initialize Context Manager

```python
from utilities.context_manager import ContextManager

# Initialize
cm = ContextManager()

# Or with explicit credentials
cm = ContextManager(
    supabase_url="https://your-project.supabase.co",
    supabase_key="your-key"
)
```

### 1. Caching Expensive Operations

```python
# Check if cached
cache_key = "timeline_analysis_2024_Q4"
cached_data = cm.get_cache(cache_key, cache_type="timeline_build")

if cached_data:
    # Use cached result
    timeline_df = pd.DataFrame(cached_data['events'])
else:
    # Expensive operation
    timeline_df = build_complex_timeline()

    # Cache for 24 hours
    cm.set_cache(
        cache_key=cache_key,
        cache_type="timeline_build",
        result_data={'events': timeline_df.to_dict('records')},
        expires_in_hours=24,
        metadata={'date_range': '2024-10-01 to 2024-12-31'}
    )
```

### 2. Saving Dashboard Snapshots

```python
# Save current dashboard state
snapshot_id = cm.save_dashboard_snapshot(
    dashboard_name="truth_justice_timeline",
    snapshot_data={
        'data': timeline_data,
        'config': dashboard_config,
        'state': user_filters
    },
    snapshot_name="Q4 2024 Review",
    filters_applied={
        'date_range': ['2024-10-01', '2024-12-31'],
        'min_relevancy': 700
    },
    metrics={
        'total_events': 150,
        'justice_score': 67.5,
        'avg_truth_score': 72.3
    },
    notes="Complete Q4 analysis for filing"
)

print(f"Snapshot saved: {snapshot_id}")
```

### 3. Loading Snapshots

```python
# Load latest snapshot
snapshot = cm.load_dashboard_snapshot(
    dashboard_name="truth_justice_timeline",
    latest=True
)

if snapshot:
    # Restore dashboard state
    timeline_data = snapshot['snapshot_data']['data']
    filters = snapshot['filters_applied']
    print(f"Loaded: {snapshot['snapshot_name']} with {snapshot['row_count']} rows")

# List available snapshots
snapshots = cm.list_snapshots(dashboard_name="truth_justice_timeline", limit=10)
for snap in snapshots:
    print(f"- {snap['snapshot_name']} ({snap['snapshot_date']})")
```

### 4. Tracking Truth Scores

```python
# Save truth scores
truth_scores = [
    {
        'item_id': 'evt_001',
        'item_type': 'MOTION',
        'item_title': 'Ex Parte Motion Filed by Mother',
        'truth_score': 25.0,  # Low truth score
        'when_happened': '2024-08-10T10:00:00',
        'where_happened': 'Alameda County Superior Court',
        'who_involved': ['Mother', 'Judge', 'Bailiff'],
        'what_occurred': 'Ex parte motion filed without notice',
        'why_occurred': 'Attempt to gain emergency custody',
        'how_occurred': 'Filed false emergency declaration',
        'importance_level': 'CRITICAL',
        'category': 'FILING',
        'evidence_count': 5,
        'supporting_evidence': {'police_reports': 0, 'declarations': 1},
        'contradicting_evidence': {'police_reports': 3, 'declarations': 2}
    }
]

cm.save_truth_scores(truth_scores)
```

### 5. Querying Truth Scores

```python
from datetime import datetime

# Get all truth scores for Q3 2024
scores = cm.get_truth_scores(
    date_from=datetime(2024, 7, 1),
    date_to=datetime(2024, 9, 30),
    min_score=0,
    max_score=50  # Only false/low truth items
)

print(f"Found {len(scores)} false statements in Q3 2024")

# Get specific item's truth history
item_scores = cm.get_truth_scores(
    item_id='evt_001',
    item_type='MOTION'
)
```

### 6. Saving Justice Score Rollups

```python
# Calculate and save justice score
rollup_id = cm.save_justice_score_rollup(
    rollup_name="Full Case Justice Score",
    justice_score=67.5,
    score_breakdown={
        'critical_items': 45,
        'high_items': 120,
        'medium_items': 80,
        'low_items': 30,
        'avg_truth_score': 62.3,
        'truthful_items': 150,
        'neutral_items': 85,
        'false_items': 40,
        'by_category': {
            'MOTION': {'count': 25, 'avg_score': 45.2},
            'FILING': {'count': 30, 'avg_score': 38.7},
            'STATEMENT': {'count': 120, 'avg_score': 72.1}
        }
    },
    items_included=['evt_001', 'evt_002', ...],
    date_range_start=datetime(2022, 8, 1),
    date_range_end=datetime(2024, 11, 5)
)

print(f"Justice score rollup saved: {rollup_id}")
```

### 7. Logging AI Analysis

```python
import time

start = time.time()

# Call AI model
response = claude_api.analyze_document(document_text)

processing_time = int((time.time() - start) * 1000)

# Log the analysis
cm.log_ai_analysis(
    analysis_type="document_fraud_detection",
    model_name="claude-sonnet-4.5",
    prompt_text=prompt,
    response_text=response['text'],
    structured_output=response['structured_data'],
    source_id=document_id,
    source_table="legal_documents",
    confidence_score=response['confidence'],
    tokens_used=response['usage']['total_tokens'],
    processing_time_ms=processing_time,
    api_cost_usd=0.05,
    metadata={'document_type': 'DECL', 'relevancy': 875}
)
```

### 8. Tracking Processing Jobs

```python
# Create a job
job_id = cm.create_processing_job(
    job_type="document_scan",
    job_name="Scan All Police Reports",
    items_total=16
)

# Process documents
for i, doc in enumerate(documents):
    process_document(doc)

    # Update progress
    cm.update_processing_job(
        job_id=job_id,
        status="running",
        items_processed=i + 1,
        progress_percentage=int(((i + 1) / 16) * 100)
    )

# Mark complete
cm.update_processing_job(
    job_id=job_id,
    status="completed",
    result_summary={
        'documents_processed': 16,
        'fraud_detected': 8,
        'total_cost': 1.25
    }
)
```

---

## 📈 Querying Saved Data

### SQL Queries

```sql
-- Get most hit cache entries
SELECT cache_key, cache_type, hit_count, last_hit_at
FROM active_cache_entries
ORDER BY hit_count DESC
LIMIT 10;

-- Get recent snapshots
SELECT * FROM recent_dashboard_snapshots
WHERE dashboard_name = 'truth_justice_timeline'
ORDER BY snapshot_date DESC;

-- Truth score summary
SELECT * FROM truth_score_summary
ORDER BY avg_truth_score ASC;  -- Worst truth scores first

-- Processing costs
SELECT * FROM processing_cost_summary
WHERE processing_date >= '2024-11-01'
ORDER BY total_cost_usd DESC;

-- Get all false statements (truth score < 25)
SELECT
    item_title,
    truth_score,
    when_happened,
    who_involved,
    what_occurred
FROM truth_score_history
WHERE truth_score < 25
ORDER BY when_happened DESC;

-- Justice score over time
SELECT
    rollup_date,
    rollup_name,
    justice_score,
    total_items,
    false_items
FROM justice_score_rollups
ORDER BY rollup_date DESC;
```

### Python Queries

```python
# Direct Supabase queries
from supabase import create_client

supabase = create_client(url, key)

# Get all critical false statements
response = supabase.table('truth_score_history')\
    .select('*')\
    .eq('importance_level', 'CRITICAL')\
    .lt('truth_score', 25)\
    .order('when_happened', desc=True)\
    .execute()

critical_false_statements = response.data

# Get justice score trend
response = supabase.table('justice_score_rollups')\
    .select('rollup_date, justice_score')\
    .order('rollup_date', desc=False)\
    .execute()

justice_trend = response.data
```

---

## 🔧 Maintenance

### Clean Expired Caches

```sql
-- Manual cleanup
SELECT clean_expired_cache();

-- Or via Python
cm = ContextManager()
deleted = cm.clean_expired_caches()
print(f"Deleted {deleted} expired cache entries")
```

### Archive Old Contexts

```sql
-- Archive contexts older than 30 days
SELECT archive_old_contexts(30);
```

### Monitor Storage

```sql
-- Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN (
    'system_processing_cache',
    'dashboard_snapshots',
    'ai_analysis_results',
    'truth_score_history'
)
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 🎨 Integration with Existing Dashboards

### Example: Truth & Justice Timeline

```python
import streamlit as st
from utilities.context_manager import ContextManager

st.set_page_config(page_title="Truth & Justice Timeline")

# Initialize
cm = ContextManager()

# Try to load cached timeline
cache_key = f"truth_timeline_{st.session_state.get('filters_hash', 'default')}"
cached_timeline = cm.get_cache(cache_key, cache_type="truth_timeline")

if cached_timeline:
    st.success("Loaded from cache!")
    timeline_df = pd.DataFrame(cached_timeline['data'])
else:
    # Build timeline (expensive)
    timeline_df = build_truth_timeline()

    # Cache for 1 hour
    cm.set_cache(
        cache_key=cache_key,
        cache_type="truth_timeline",
        result_data={'data': timeline_df.to_dict('records')},
        expires_in_hours=1
    )

# Auto-save snapshot every 5 minutes
if 'last_snapshot' not in st.session_state or \
   (datetime.now() - st.session_state.last_snapshot).seconds > 300:

    cm.save_dashboard_snapshot(
        dashboard_name="truth_justice_timeline",
        snapshot_data={'data': timeline_df.to_dict('records')},
        filters_applied=st.session_state.filters,
        metrics=st.session_state.metrics,
        auto_snapshot=True
    )

    st.session_state.last_snapshot = datetime.now()

# Display timeline
st.plotly_chart(create_timeline_viz(timeline_df))
```

---

## 📊 Cost Tracking

### Monitor AI Processing Costs

```sql
-- Total costs by analysis type
SELECT
    analysis_type,
    COUNT(*) as analysis_count,
    SUM(tokens_used) as total_tokens,
    SUM(api_cost_usd) as total_cost_usd
FROM ai_analysis_results
GROUP BY analysis_type
ORDER BY total_cost_usd DESC;

-- Daily costs
SELECT
    DATE(created_at) as date,
    SUM(api_cost_usd) as daily_cost
FROM ai_analysis_results
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

### Cost Optimization Tips

1. **Cache aggressively** - Set longer expiration for stable data
2. **Use snapshots** - Avoid rebuilding dashboards from scratch
3. **Batch processing** - Process multiple items in one AI call
4. **Monitor hit rates** - Low hit rates indicate poor cache keys

---

## 🔐 Security Notes

- All data stored in Supabase with Row Level Security (RLS)
- Cache entries expire automatically
- Sensitive data should be encrypted before caching
- API keys never stored in cache/snapshots

---

## 📝 Changelog

### 2025-11-05 - Initial Release
- Created 8-table schema
- Built ContextManager utility
- Added deployment scripts
- Created comprehensive documentation

---

## 🚀 Future Enhancements

- [ ] Automatic cache warming on dashboard load
- [ ] Smart cache invalidation on data updates
- [ ] Compression for large snapshots
- [ ] Export snapshots to JSON/CSV
- [ ] Snapshot diffing tool
- [ ] Cache analytics dashboard
- [ ] Automated cost alerts

---

## 📞 Support

For issues or questions:
1. Check error logs: `check_error_logs.py`
2. Run diagnostic: `supabase_data_diagnostic.py`
3. Review system summary: `PROJ344_SYSTEM_SUMMARY.md`

---

**System Status:** ✅ READY FOR DEPLOYMENT
**Last Updated:** 2025-11-05
