# Context Preservation System - Testing Guide

**Created:** 2025-11-05
**Purpose:** Complete testing and verification instructions

---

## 🎯 Testing Overview

This guide walks you through testing the entire context preservation system in the correct order.

---

## ✅ Pre-Test Checklist

Before running any tests, ensure:

- [ ] You have Supabase credentials set in environment variables
- [ ] You're in the ASEAGI directory: `cd c:/Users/DonBucknor_n0ufqwv/GettingStarted/ASEAGI`
- [ ] Python environment is ready

---

## 📋 Testing Steps

### **STEP 1: Deploy Schema to Supabase** (REQUIRED FIRST!)

**This is the most critical step. Nothing will work without this.**

1. **Open the SQL file:**
   - File: `c:\Users\DonBucknor_n0ufqwv\GettingStarted\ASEAGI\schemas\context_preservation_schema.sql`
   - Open with Notepad, VS Code, or any text editor
   - Press **Ctrl+A** to select all 374 lines
   - Press **Ctrl+C** to copy

2. **Go to Supabase SQL Editor:**
   - URL: https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu/sql
   - Click **"New Query"**
   - Press **Ctrl+V** to paste all SQL content
   - Click **"Run"** button (green play button)

3. **Expected result:**
   ```
   Success. No rows returned
   ```

4. **What this creates:**
   - ✅ 8 tables for context preservation
   - ✅ 5 views for quick queries
   - ✅ 3 helper functions

---

### **STEP 2: Verify Schema Deployment**

Run the verification script to check all tables exist:

```bash
cd c:/Users/DonBucknor_n0ufqwv/GettingStarted/ASEAGI
python test_schema_deployment.py
```

**Expected output:**
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
```

**If tables are missing:**
- You skipped Step 1 or ran it incorrectly
- Go back to Step 1 and deploy the schema

---

### **STEP 3: Test ContextManager Functionality**

Run the comprehensive functionality test:

```bash
python test_context_manager.py
```

**This tests 5 core features:**

1. **Cache Set/Get** - Stores and retrieves cached data
2. **Dashboard Snapshots** - Saves and loads complete dashboard states
3. **Truth Scores** - Tracks truth scores with 5W+H context
4. **Justice Scores** - Saves justice score rollups
5. **AI Analysis Logging** - Logs AI API calls with cost tracking

**Expected output:**
```
======================================================================
CONTEXT MANAGER - FUNCTIONALITY TEST
======================================================================

🔧 Initializing ContextManager...
✅ ContextManager initialized

======================================================================
TEST 1: Cache Functionality
======================================================================
📝 Setting cache: test_cache_001
   ✅ Cache set successfully
📥 Getting cache: test_cache_001
   ✅ Cache retrieved successfully
   Data: Hello from cache test!

======================================================================
TEST 2: Dashboard Snapshot Save/Load
======================================================================
📸 Saving dashboard snapshot...
   ✅ Snapshot saved: <uuid>
📥 Loading snapshot...
   ✅ Snapshot loaded successfully
   Name: Test Snapshot 1
   Rows: 2

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
   ✅ Justice score rollup saved: <uuid>

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

---

### **STEP 4: Verify Data in Supabase**

After running the tests, check Supabase to see the test data:

1. **Go to Supabase Table Editor:**
   - URL: https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu/editor

2. **Check each table:**
   - `system_processing_cache` - Should have 1 test cache entry
   - `dashboard_snapshots` - Should have 1 test snapshot
   - `truth_score_history` - Should have 2 test truth scores
   - `justice_score_rollups` - Should have 1 test rollup
   - `ai_analysis_results` - Should have 1 test analysis log

3. **Run SQL queries:**

```sql
-- View active cache entries
SELECT * FROM active_cache_entries;

-- View recent snapshots
SELECT * FROM recent_dashboard_snapshots;

-- View truth scores
SELECT item_title, truth_score, importance_level
FROM truth_score_history
ORDER BY calculated_at DESC;

-- View justice scores
SELECT rollup_name, justice_score, total_items
FROM justice_score_rollups
ORDER BY rollup_date DESC;

-- View AI analysis logs
SELECT analysis_type, model_name, api_cost_usd, tokens_used
FROM ai_analysis_results
ORDER BY created_at DESC;
```

---

### **STEP 5: Clean Up Test Data (Optional)**

To remove test data:

```sql
-- Delete test cache entries
DELETE FROM system_processing_cache WHERE cache_key LIKE 'test_%';

-- Delete test snapshots
DELETE FROM dashboard_snapshots WHERE dashboard_name = 'test_dashboard';

-- Delete test truth scores
DELETE FROM truth_score_history WHERE item_id LIKE 'test_%';

-- Delete test justice scores
DELETE FROM justice_score_rollups WHERE rollup_name LIKE 'Test%';

-- Delete test AI logs
DELETE FROM ai_analysis_results WHERE analysis_type = 'test_analysis';
```

---

## 🎨 Integration Testing (Real Usage)

After all tests pass, integrate into your actual dashboards:

### Example: Add Caching to Truth & Justice Timeline

Edit `truth_justice_timeline.py`:

```python
from utilities.context_manager import ContextManager

# Initialize at top of file
cm = ContextManager()

# Before building timeline (line ~200):
cache_key = f"truth_timeline_{st.session_state.get('date_range', 'all')}"
cached_timeline = cm.get_cache(cache_key, cache_type="truth_timeline")

if cached_timeline:
    st.success("⚡ Loaded from cache!")
    timeline_df = pd.DataFrame(cached_timeline['data'])
else:
    # Build timeline (expensive operation)
    timeline_df = build_timeline_data()

    # Cache for 1 hour
    cm.set_cache(
        cache_key=cache_key,
        cache_type="truth_timeline",
        result_data={'data': timeline_df.to_dict('records')},
        expires_in_hours=1
    )
```

---

## 🔍 Troubleshooting

### Error: "relation does not exist"

**Cause:** Schema not deployed
**Fix:** Go back to Step 1 and deploy the SQL schema

### Error: "SUPABASE_KEY not set"

**Cause:** Missing environment variable
**Fix:** Set environment variable:
```bash
# Windows (PowerShell)
$env:SUPABASE_KEY="your-key-here"

# Windows (CMD)
set SUPABASE_KEY=your-key-here

# Or use .streamlit/secrets.toml
```

### Error: "Connection failed"

**Cause:** Invalid credentials or network issue
**Fix:** Verify Supabase URL and key are correct

---

## 📊 Performance Testing

To test performance improvements:

### Before Context Preservation:
```bash
# Time how long it takes to build timeline
time python -c "from truth_justice_timeline import build_timeline; build_timeline()"
# Result: ~30 seconds
```

### After Context Preservation:
```bash
# First run (no cache): ~30 seconds
# Second run (with cache): ~0.1 seconds ⚡
```

---

## ✅ Testing Checklist

- [ ] Step 1: Schema deployed to Supabase
- [ ] Step 2: Verification test passed (8/8 tables found)
- [ ] Step 3: Functionality test passed (5/5 tests)
- [ ] Step 4: Data visible in Supabase
- [ ] Step 5: Test data cleaned up (optional)
- [ ] Integration: Added caching to at least 1 dashboard
- [ ] Performance: Verified cache speedup

---

## 🎉 Success Criteria

You'll know the system is working when:

✅ All 8 tables exist in Supabase
✅ All 5 functionality tests pass
✅ Test data appears in Supabase tables
✅ Cache retrieval is instant (< 0.1 seconds)
✅ Dashboard snapshots can be saved and restored
✅ Truth scores are stored with 5W+H context

---

## 📞 Next Steps After Testing

Once all tests pass:

1. **Integrate into dashboards** - Add caching to expensive operations
2. **Save snapshots regularly** - Before filing motions, major changes
3. **Track truth scores** - Build historical truth score database
4. **Monitor costs** - Query AI analysis costs in Supabase
5. **Set up maintenance** - Run `clean_expired_cache()` weekly

---

**Ready to test? Start with Step 1!** 🚀
