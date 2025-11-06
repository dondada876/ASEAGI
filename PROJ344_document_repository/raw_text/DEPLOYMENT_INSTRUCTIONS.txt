# Context Preservation System - Deployment Instructions

**Created:** 2025-11-05
**Status:** ✅ TESTED & VERIFIED (5/5 tests passing)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step-by-Step Deployment](#step-by-step-deployment)
4. [Verification & Testing](#verification--testing)
5. [Integration Guide](#integration-guide)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

---

## 🎯 Overview

This system provides:
- **Caching** - Store expensive AI/processing results to avoid recomputation
- **Dashboard Snapshots** - Save and restore complete dashboard states
- **Truth Score Tracking** - Historical tracking with 5W+H context (When, Where, Who, What, Why, How)
- **Justice Score Rollups** - Aggregate truth scores into justice scores
- **AI Cost Tracking** - Monitor all AI API calls and costs

**Database:** 8 tables, 5 views, 3 functions in Supabase
**Python API:** `ContextManager` class with easy-to-use methods

---

## ✅ Prerequisites

Before starting, ensure you have:

1. **Supabase Account & Project**
   - Project URL: `https://jvjlhxodmbkodzmggwpu.supabase.co`
   - Anon key available in `.streamlit/secrets.toml`

2. **Python Environment**
   - Python 3.8+
   - Required packages: `supabase`, `pandas`, `toml`

3. **File Access**
   - Working directory: `c:\Users\DonBucknor_n0ufqwv\GettingStarted\ASEAGI`
   - Write access to Supabase database

---

## 🚀 Step-by-Step Deployment

### **STEP 1: Deploy Database Schema (5 minutes)**

This is the **MOST CRITICAL** step. Nothing works without the schema deployed.

#### 1.1 Open the SQL Schema File

**Location:** `c:\Users\DonBucknor_n0ufqwv\GettingStarted\ASEAGI\schemas\context_preservation_schema.sql`

**How to open:**
- Option A: Right-click → Open with → Notepad
- Option B: Right-click → Open with → VS Code
- Option C: Double-click (if associated with a text editor)

#### 1.2 Copy ALL Schema Contents

1. Open the file
2. Press **Ctrl+A** (select all 374 lines)
3. Press **Ctrl+C** (copy)

**⚠️ IMPORTANT:** Copy ALL lines - from line 1 to line 374. Missing any part will cause errors.

#### 1.3 Open Supabase SQL Editor

1. Go to: https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu/sql
2. Click the **"New Query"** button (top right)
3. You should see an empty SQL editor

#### 1.4 Paste and Execute

1. Click in the SQL editor
2. Press **Ctrl+V** (paste the schema)
3. Verify you see all 374 lines
4. Click the **"Run"** button (green play button, or F5)

#### 1.5 Verify Success

**Expected result:**
```
Success. No rows returned
```

**If you see an error:**
- Make sure you copied ALL 374 lines
- Check that you're in the correct Supabase project
- Verify you have database write permissions

#### 1.6 Confirm Tables Were Created

1. Go to: https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu/editor
2. Look for these 8 new tables:
   - ✅ `system_processing_cache`
   - ✅ `dashboard_snapshots`
   - ✅ `ai_analysis_results`
   - ✅ `query_results_cache`
   - ✅ `truth_score_history`
   - ✅ `justice_score_rollups`
   - ✅ `processing_jobs_log`
   - ✅ `context_preservation_metadata`

**✅ CHECKPOINT:** If you see all 8 tables, proceed to Step 2. If not, repeat Step 1.

---

### **STEP 2: Verify Schema Deployment (2 minutes)**

Run the automated verification test to confirm everything is set up correctly.

#### 2.1 Open Terminal/Command Prompt

**Windows:**
- Press `Win+R`
- Type `cmd`
- Press Enter

#### 2.2 Navigate to ASEAGI Directory

```bash
cd c:\Users\DonBucknor_n0ufqwv\GettingStarted\ASEAGI
```

#### 2.3 Run Verification Test

```bash
python test_schema_deployment.py
```

#### 2.4 Expected Output

```
======================================================================
CONTEXT PRESERVATION SCHEMA - VERIFICATION TEST
======================================================================

🔗 Connecting to Supabase...
   URL: https://jvjlhxodmbkodzmggwpu.supabase.co
   ✅ Connected!

📊 Testing Tables...

   ✅ system_processing_cache             (0 rows)
   ✅ dashboard_snapshots                  (0 rows)
   ✅ ai_analysis_results                  (0 rows)
   ✅ query_results_cache                  (0 rows)
   ✅ truth_score_history                  (0 rows)
   ✅ justice_score_rollups                (0 rows)
   ✅ processing_jobs_log                  (0 rows)
   ✅ context_preservation_metadata        (0 rows)

======================================================================
RESULTS: 8/8 tables found
✅ All tables exist! Schema deployment successful!

======================================================================
NEXT STEP: Test ContextManager functionality
Run: python test_context_manager.py
======================================================================
```

**✅ CHECKPOINT:** If you see `8/8 tables found`, proceed to Step 3.

**❌ If tables are missing:**
- Go back to Step 1
- Ensure you copied ALL SQL content
- Re-run the SQL in Supabase

---

### **STEP 3: Test Full Functionality (3 minutes)**

Run comprehensive tests to verify all features work correctly.

#### 3.1 Run Full Test Suite

```bash
python test_context_manager.py
```

#### 3.2 Expected Output

```
======================================================================
CONTEXT MANAGER - FUNCTIONALITY TEST
======================================================================

🔧 Initializing ContextManager...
✅ ContextManager initialized

======================================================================
TEST 1: Cache Functionality
======================================================================
📝 Setting cache: test_cache_20251105_155917_762983
   ✅ Cache set successfully
📥 Getting cache: test_cache_20251105_155917_762983
   ✅ Cache retrieved successfully
   Data: Hello from cache test!

======================================================================
TEST 2: Dashboard Snapshot Save/Load
======================================================================
📸 Saving dashboard snapshot...
   ✅ Snapshot saved: 1585c238-63a5-480c-bcd4-49de298d2925
📥 Loading snapshot...
   ✅ Snapshot loaded successfully
   Name: Test Snapshot 1
   Rows: 0

======================================================================
TEST 3: Truth Score Tracking
======================================================================
📊 Saving 2 truth scores...
   ✅ Truth scores saved
🔍 Querying truth scores...
   ✅ Retrieved 2 truth scores

======================================================================
TEST 4: Justice Score Rollup
======================================================================
📈 Saving justice score rollup...
   ✅ Justice score rollup saved: ca86b3fd-f624-40f0-9168-cac841f495b6

======================================================================
TEST 5: AI Analysis Logging
======================================================================
🤖 Logging AI analysis...
   ✅ AI analysis logged

======================================================================
TEST RESULTS
======================================================================
✅ Tests Passed: 5/5
❌ Tests Failed: 0/5

🎉 ALL TESTS PASSED! Context preservation system is working!
```

**✅ CHECKPOINT:** If you see `5/5 tests passed`, the system is **READY FOR USE**!

---

## ✅ Verification & Testing

### Verify Data in Supabase

1. Go to: https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu/editor

2. Click on each table to verify test data:

**`system_processing_cache`** - Should have test cache entries
```sql
SELECT cache_key, cache_type, hit_count FROM system_processing_cache;
```

**`dashboard_snapshots`** - Should have test snapshots
```sql
SELECT snapshot_name, snapshot_date, row_count FROM dashboard_snapshots;
```

**`truth_score_history`** - Should have test truth scores
```sql
SELECT item_title, truth_score, importance_level FROM truth_score_history;
```

**`justice_score_rollups`** - Should have test rollups
```sql
SELECT rollup_name, justice_score, total_items FROM justice_score_rollups;
```

**`ai_analysis_results`** - Should have test AI logs
```sql
SELECT analysis_type, model_name, api_cost_usd FROM ai_analysis_results;
```

### Clean Up Test Data (Optional)

If you want to remove test data before production use:

```sql
-- Delete test cache entries
DELETE FROM system_processing_cache WHERE cache_key LIKE 'test_%';

-- Delete test snapshots
DELETE FROM dashboard_snapshots WHERE dashboard_name = 'test_dashboard';

-- Delete test truth scores
DELETE FROM truth_score_history WHERE item_type = 'TEST_EVENT';

-- Delete test justice scores
DELETE FROM justice_score_rollups WHERE rollup_name LIKE 'Test%';

-- Delete test AI logs
DELETE FROM ai_analysis_results WHERE analysis_type = 'test_analysis';
```

---

## 🎨 Integration Guide

### Basic Integration Example

Here's how to add context preservation to an existing dashboard:

#### Example: Add Caching to Truth & Justice Timeline

**File:** `truth_justice_timeline.py`

**Before (without caching):**
```python
import streamlit as st
import pandas as pd

# Build timeline (expensive - 30 seconds)
timeline_df = build_truth_timeline()

# Display
st.plotly_chart(create_timeline_viz(timeline_df))
```

**After (with caching):**
```python
import streamlit as st
import pandas as pd
from utilities.context_manager import ContextManager

# Initialize ContextManager
cm = ContextManager()

# Generate cache key based on filters
filters = st.session_state.get('filters', {})
cache_key = f"truth_timeline_{hash(str(filters))}"

# Try to get cached data
cached_data = cm.get_cache(cache_key, cache_type="timeline_build")

if cached_data:
    # Load from cache - instant! ⚡
    st.success("⚡ Loaded from cache!")
    timeline_df = pd.DataFrame(cached_data['events'])
else:
    # Build timeline (expensive - 30 seconds)
    st.info("Building timeline...")
    timeline_df = build_truth_timeline()

    # Cache for 1 hour
    cm.set_cache(
        cache_key=cache_key,
        cache_type="timeline_build",
        result_data={'events': timeline_df.to_dict('records')},
        expires_in_hours=1
    )
    st.success("Timeline built and cached!")

# Display
st.plotly_chart(create_timeline_viz(timeline_df))
```

**Result:**
- First load: 30 seconds (builds timeline)
- Subsequent loads: 0.1 seconds (loads from cache) ⚡
- Cache expires after 1 hour

---

### Save Dashboard Snapshots

Add auto-save functionality to preserve dashboard state:

```python
from utilities.context_manager import ContextManager
from datetime import datetime

cm = ContextManager()

# Save snapshot every 5 minutes
if 'last_snapshot_time' not in st.session_state:
    st.session_state.last_snapshot_time = datetime.now()

time_since_last = (datetime.now() - st.session_state.last_snapshot_time).seconds

if time_since_last > 300:  # 5 minutes
    snapshot_id = cm.save_dashboard_snapshot(
        dashboard_name="truth_justice_timeline",
        snapshot_data={
            'timeline_data': timeline_df.to_dict('records'),
            'filters': st.session_state.filters,
            'view_state': st.session_state.view_config
        },
        filters_applied=st.session_state.filters,
        metrics={
            'total_events': len(timeline_df),
            'avg_truth_score': timeline_df['truth_score'].mean()
        },
        auto_snapshot=True
    )
    st.session_state.last_snapshot_time = datetime.now()
    st.toast(f"Auto-saved snapshot: {snapshot_id[:8]}...", icon="💾")
```

---

### Track Truth Scores Historically

Save truth scores as you calculate them:

```python
from utilities.context_manager import ContextManager

cm = ContextManager()

# Calculate truth scores for events
truth_scores = []
for event in timeline_events:
    score = calculate_truth_score(event)

    truth_scores.append({
        'item_id': event['id'],
        'item_type': event['type'],  # 'MOTION', 'FILING', 'STATEMENT', etc.
        'item_title': event['title'],
        'truth_score': score,
        'when_happened': event['date'],
        'where_happened': event['location'],
        'who_involved': event['parties'],
        'what_occurred': event['description'],
        'why_occurred': event.get('motive', ''),
        'how_occurred': event.get('method', ''),
        'importance_level': event['importance'],  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
        'category': event['category'],
        'evidence_count': len(event.get('evidence', []))
    })

# Save all scores to Supabase
cm.save_truth_scores(truth_scores)

st.success(f"Saved {len(truth_scores)} truth scores to history!")
```

**Query historical scores:**

```python
from datetime import datetime

# Get all false statements from August 2024
false_statements = cm.get_truth_scores(
    date_from=datetime(2024, 8, 1),
    date_to=datetime(2024, 8, 31),
    max_score=25  # Truth score < 25 = false
)

st.write(f"Found {len(false_statements)} false statements in August 2024")
```

---

### Calculate and Save Justice Scores

```python
from utilities.context_manager import ContextManager
from datetime import datetime

cm = ContextManager()

# Calculate overall justice score
justice_score = calculate_justice_score(timeline_df)

# Save the calculation
rollup_id = cm.save_justice_score_rollup(
    rollup_name="Full Case Justice Score - November 2024",
    justice_score=justice_score,
    score_breakdown={
        'critical_items': critical_count,
        'high_items': high_count,
        'medium_items': medium_count,
        'low_items': low_count,
        'avg_truth_score': avg_truth,
        'truthful_items': truthful_count,
        'neutral_items': neutral_count,
        'false_items': false_count
    },
    items_included=[event['id'] for event in timeline_events],
    date_range_start=datetime(2022, 8, 1),
    date_range_end=datetime.now()
)

st.success(f"Justice score saved: {justice_score:.1f}%")
```

---

### Log AI Analysis Calls

Track all AI API usage and costs:

```python
from utilities.context_manager import ContextManager
import time

cm = ContextManager()

# Before AI call
start_time = time.time()

# Call AI model
response = anthropic_client.messages.create(
    model="claude-sonnet-4.5",
    max_tokens=2000,
    messages=[{"role": "user", "content": prompt}]
)

# Calculate processing time
processing_time_ms = int((time.time() - start_time) * 1000)

# Log the analysis
cm.log_ai_analysis(
    analysis_type="fraud_detection",
    model_name="claude-sonnet-4.5",
    prompt_text=prompt,
    response_text=response.content[0].text,
    structured_output=parsed_response,
    source_id=document_id,
    source_table="legal_documents",
    confidence_score=parsed_response.get('confidence', 0),
    tokens_used=response.usage.total_tokens,
    processing_time_ms=processing_time_ms,
    api_cost_usd=calculate_cost(response.usage),
    metadata={
        'document_type': document_type,
        'relevancy': relevancy_score
    }
)
```

**Query AI costs:**

```sql
-- Total costs by analysis type
SELECT
    analysis_type,
    COUNT(*) as call_count,
    SUM(tokens_used) as total_tokens,
    SUM(api_cost_usd) as total_cost
FROM ai_analysis_results
GROUP BY analysis_type
ORDER BY total_cost DESC;

-- Daily costs
SELECT
    DATE(created_at) as date,
    SUM(api_cost_usd) as daily_cost
FROM ai_analysis_results
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

---

## 🔧 Troubleshooting

### Issue: "Table does not exist"

**Symptom:** Error messages like `relation "system_processing_cache" does not exist`

**Cause:** Schema not deployed to Supabase

**Solution:**
1. Go back to [Step 1](#step-1-deploy-database-schema-5-minutes)
2. Ensure you copied ALL 374 lines from the SQL file
3. Re-run the SQL in Supabase SQL Editor
4. Verify tables exist in Table Editor

---

### Issue: "SUPABASE_KEY not set"

**Symptom:** Error: `SUPABASE_KEY environment variable not set`

**Cause:** Missing credentials

**Solution:**
1. Check that `.streamlit/secrets.toml` exists
2. Verify it contains `SUPABASE_KEY` and `SUPABASE_URL`
3. If using environment variables, set them:
   ```bash
   # Windows PowerShell
   $env:SUPABASE_KEY="your-key-here"

   # Windows CMD
   set SUPABASE_KEY=your-key-here
   ```

---

### Issue: Cache GET returns None

**Symptom:** Cache SET works, but GET returns None

**Cause:** Timezone mismatch (already fixed in current version)

**Solution:**
- Update to latest `context_manager.py` (uses UTC timestamps)
- If still failing, check that `datetime.now(timezone.utc)` is used on lines 84 and 113

---

### Issue: Test failures

**Symptom:** Some tests fail with errors

**Cause:** Various issues (UUIDs, database connection, etc.)

**Solutions:**
1. **Check database connection:**
   ```python
   from utilities.context_manager import ContextManager
   cm = ContextManager()
   print("✅ Connected successfully!")
   ```

2. **Verify tables exist:**
   ```bash
   python test_schema_deployment.py
   ```

3. **Check error details:**
   - Read the full error message
   - Check stack trace
   - Look for specific table/column names

---

## 🔄 Maintenance

### Clean Expired Caches

Run weekly to remove expired cache entries:

```sql
SELECT clean_expired_cache();
```

Or via Python:

```python
from utilities.context_manager import ContextManager

cm = ContextManager()
deleted_count = cm.client.rpc('clean_expired_cache').execute()
print(f"Deleted {deleted_count} expired cache entries")
```

---

### Archive Old Contexts

Archive contexts older than 30 days:

```sql
SELECT archive_old_contexts(30);
```

---

### Monitor Storage

Check table sizes:

```sql
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size('public.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN (
    'system_processing_cache',
    'dashboard_snapshots',
    'ai_analysis_results',
    'truth_score_history'
)
ORDER BY pg_total_relation_size('public.'||tablename) DESC;
```

---

### Monitor Cache Hit Rates

```sql
SELECT
    cache_type,
    COUNT(*) as entry_count,
    AVG(hit_count) as avg_hits,
    SUM(hit_count) as total_hits
FROM system_processing_cache
GROUP BY cache_type
ORDER BY total_hits DESC;
```

Low hit counts indicate:
- Cache keys may be too specific
- Cache expiration may be too short
- Feature not being used effectively

---

## 📊 Success Criteria

Your deployment is successful if:

- ✅ All 8 tables exist in Supabase
- ✅ Schema verification test passes (8/8 tables found)
- ✅ Functionality test passes (5/5 tests)
- ✅ Test data appears in Supabase tables
- ✅ Cache SET and GET work correctly
- ✅ Dashboard snapshots save and load
- ✅ Truth scores are stored with 5W+H context
- ✅ Justice scores calculate correctly
- ✅ AI analysis logs track costs

---

## 🎉 You're Done!

The context preservation system is now:
- ✅ Deployed to Supabase
- ✅ Tested and verified
- ✅ Ready for integration

### Next Steps:

1. **Integrate into dashboards** - Start with caching expensive operations
2. **Save snapshots** - Add auto-save to critical dashboards
3. **Track truth scores** - Build historical truth database
4. **Monitor costs** - Query AI analysis costs regularly

### Documentation:

- **Full Guide:** `schemas/README_CONTEXT_PRESERVATION.md`
- **Quick Start:** `CONTEXT_PRESERVATION_SUMMARY.md`
- **Testing:** `TESTING_GUIDE.md`
- **This File:** `DEPLOYMENT_INSTRUCTIONS.md`

---

**Questions or Issues?**
- Review error messages carefully
- Check the troubleshooting section
- Verify all prerequisites are met
- Re-run verification tests

**System Status:** ✅ READY FOR PRODUCTION USE

---

*Last Updated: 2025-11-05*
*Version: 1.0*
*Test Status: 5/5 Passing*
