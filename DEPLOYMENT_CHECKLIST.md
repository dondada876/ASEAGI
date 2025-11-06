# Context Preservation System - Deployment Checklist

**Review this checklist before, during, and after deployment**

---

## 📋 Pre-Deployment Checklist

### Environment Setup
- [ ] Python 3.8+ installed
- [ ] Required packages installed (`supabase`, `pandas`, `toml`)
- [ ] Working directory is `ASEAGI` folder
- [ ] Access to Supabase dashboard
- [ ] `.streamlit/secrets.toml` exists with credentials

### File Verification
- [ ] `schemas/context_preservation_schema.sql` exists (374 lines)
- [ ] `utilities/context_manager.py` exists (660+ lines)
- [ ] `test_schema_deployment.py` exists
- [ ] `test_context_manager.py` exists
- [ ] Documentation files exist:
  - [ ] `DEPLOYMENT_INSTRUCTIONS.md`
  - [ ] `QUICK_START.md`
  - [ ] `TESTING_GUIDE.md`
  - [ ] `schemas/README_CONTEXT_PRESERVATION.md`

### Supabase Access
- [ ] Can log into Supabase dashboard
- [ ] Project URL correct: `https://jvjlhxodmbkodzmggwpu.supabase.co`
- [ ] Have anon key available
- [ ] Have database write permissions

---

## 🚀 Deployment Steps Checklist

### STEP 1: Deploy Database Schema

- [ ] **1.1** Opened `schemas/context_preservation_schema.sql`
- [ ] **1.2** Selected ALL text (Ctrl+A)
- [ ] **1.3** Copied all 374 lines (Ctrl+C)
- [ ] **1.4** Opened Supabase SQL Editor
- [ ] **1.5** Clicked "New Query"
- [ ] **1.6** Pasted SQL (Ctrl+V)
- [ ] **1.7** Verified all 374 lines visible
- [ ] **1.8** Clicked "Run" button
- [ ] **1.9** Saw success message: `Success. No rows returned`

### STEP 2: Verify Schema Deployment

- [ ] **2.1** Opened terminal/command prompt
- [ ] **2.2** Navigated to ASEAGI directory
- [ ] **2.3** Ran `python test_schema_deployment.py`
- [ ] **2.4** Saw success: `8/8 tables found`
- [ ] **2.5** All 8 tables reported as existing:
  - [ ] `system_processing_cache`
  - [ ] `dashboard_snapshots`
  - [ ] `ai_analysis_results`
  - [ ] `query_results_cache`
  - [ ] `truth_score_history`
  - [ ] `justice_score_rollups`
  - [ ] `processing_jobs_log`
  - [ ] `context_preservation_metadata`

### STEP 3: Test Full Functionality

- [ ] **3.1** Ran `python test_context_manager.py`
- [ ] **3.2** ContextManager initialized successfully
- [ ] **3.3** TEST 1 passed: Cache Functionality
- [ ] **3.4** TEST 2 passed: Dashboard Snapshot Save/Load
- [ ] **3.5** TEST 3 passed: Truth Score Tracking
- [ ] **3.6** TEST 4 passed: Justice Score Rollup
- [ ] **3.7** TEST 5 passed: AI Analysis Logging
- [ ] **3.8** Final result: `5/5 tests passed`

---

## ✅ Post-Deployment Verification

### Supabase Table Editor Verification

Go to: https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu/editor

Check each table has test data:

#### system_processing_cache
- [ ] Table exists
- [ ] Has at least 1 test entry
- [ ] Columns visible: `cache_key`, `cache_type`, `result_data`, `expires_at`
- [ ] Test cache key visible (starts with `test_cache_`)

#### dashboard_snapshots
- [ ] Table exists
- [ ] Has test snapshots
- [ ] Columns visible: `dashboard_name`, `snapshot_data`, `snapshot_date`
- [ ] Test dashboard visible (`test_dashboard`)

#### truth_score_history
- [ ] Table exists
- [ ] Has test truth scores
- [ ] Columns visible: `item_title`, `truth_score`, `when_happened`, `who_involved`
- [ ] Test scores visible (type = `TEST_EVENT`)

#### justice_score_rollups
- [ ] Table exists
- [ ] Has test rollups
- [ ] Columns visible: `rollup_name`, `justice_score`, `total_items`
- [ ] Test rollup visible (name contains `Test`)

#### ai_analysis_results
- [ ] Table exists
- [ ] Has test AI logs
- [ ] Columns visible: `analysis_type`, `model_name`, `api_cost_usd`, `tokens_used`
- [ ] Test log visible (type = `test_analysis`)

### Views Verification

- [ ] `active_cache_entries` view exists
- [ ] `recent_dashboard_snapshots` view exists
- [ ] `truth_score_summary` view exists
- [ ] `processing_cost_summary` view exists
- [ ] `active_processing_jobs` view exists

### Functions Verification

Run these SQL commands to verify functions work:

- [ ] `SELECT clean_expired_cache();` - Returns integer
- [ ] `SELECT archive_old_contexts(30);` - Returns integer
- [ ] `SELECT increment_cache_hit('test_cache_001');` - Completes without error

---

## 🧪 Functional Testing

### Cache Test
```python
from utilities.context_manager import ContextManager
cm = ContextManager()

# Set cache
cm.set_cache('test_key_123', 'test', {'data': 'hello'}, expires_in_hours=1)

# Get cache
result = cm.get_cache('test_key_123')
assert result == {'data': 'hello'}, "Cache GET failed"
print("✅ Cache test passed")
```

- [ ] Set cache works
- [ ] Get cache works
- [ ] Returns correct data

### Snapshot Test
```python
# Save snapshot
id = cm.save_dashboard_snapshot(
    'my_test',
    {'test': 'data'},
    metrics={'count': 10}
)

# Load snapshot
loaded = cm.load_dashboard_snapshot('my_test', latest=True)
assert loaded['snapshot_data'] == {'test': 'data'}, "Snapshot load failed"
print("✅ Snapshot test passed")
```

- [ ] Save snapshot works
- [ ] Load snapshot works
- [ ] Returns correct data

---

## 🔧 Troubleshooting Verification

### If "Table does not exist" error:
- [ ] Re-checked Step 1 was completed
- [ ] Verified ALL 374 lines were copied
- [ ] Confirmed SQL ran successfully
- [ ] Checked correct Supabase project

### If "SUPABASE_KEY not set" error:
- [ ] Verified `.streamlit/secrets.toml` exists
- [ ] Checked file contains `SUPABASE_KEY`
- [ ] Confirmed key is valid (no extra spaces/quotes)

### If tests fail:
- [ ] Re-ran `python test_schema_deployment.py`
- [ ] Checked error messages carefully
- [ ] Verified database connection works
- [ ] Reviewed full stack trace

---

## 📊 Performance Verification

### Cache Performance Test
```python
import time

# Without cache (first run)
start = time.time()
result = expensive_operation()
first_run_time = time.time() - start
print(f"First run: {first_run_time:.2f}s")

# With cache (second run)
start = time.time()
result = cm.get_cache('cached_result')
second_run_time = time.time() - start
print(f"Second run: {second_run_time:.4f}s")

speedup = first_run_time / second_run_time
print(f"Speedup: {speedup:.0f}x faster")
```

Expected results:
- [ ] First run: 5-30 seconds (depends on operation)
- [ ] Second run: < 0.1 seconds
- [ ] Speedup: > 50x faster

---

## 📝 Documentation Review

### Review Each Document
- [ ] Read `DEPLOYMENT_INSTRUCTIONS.md` - Clear and complete?
- [ ] Read `QUICK_START.md` - Easy to follow?
- [ ] Review `TESTING_GUIDE.md` - All tests covered?
- [ ] Scan `schemas/README_CONTEXT_PRESERVATION.md` - Comprehensive?

### Key Sections Present
- [ ] Overview explains what system does
- [ ] Prerequisites clearly listed
- [ ] Step-by-step instructions are detailed
- [ ] Code examples are practical
- [ ] Troubleshooting covers common issues
- [ ] SQL queries provided for verification

---

## 🎯 Integration Readiness

### Before Integrating into Dashboards

- [ ] All tests passing (5/5)
- [ ] Understanding of cache expiration strategy
- [ ] Knowledge of when to save snapshots
- [ ] Plan for truth score tracking
- [ ] Strategy for justice score calculation
- [ ] Method for AI cost monitoring

### Integration Plan

Dashboard to integrate first:
- [ ] Dashboard name: _______________
- [ ] Feature to add: Cache / Snapshot / Truth / Justice / AI
- [ ] Expected performance gain: _______________
- [ ] Rollback plan if issues: _______________

---

## 🔒 Security & Maintenance

### Security Checks
- [ ] Supabase credentials not committed to git
- [ ] `.streamlit/secrets.toml` in `.gitignore`
- [ ] No API keys in source code
- [ ] Row Level Security (RLS) reviewed in Supabase

### Maintenance Schedule
- [ ] Weekly: Run `clean_expired_cache()`
- [ ] Monthly: Check table sizes
- [ ] Monthly: Review cache hit rates
- [ ] Quarterly: Archive old contexts
- [ ] Quarterly: Review AI cost trends

---

## 📈 Success Metrics

### Deployment Success
- [x] Schema deployed successfully
- [x] All tables exist (8/8)
- [x] All tests pass (5/5)
- [x] Test data in Supabase
- [x] Documentation complete

### Performance Targets
- [ ] Cache hit rate > 50% after 1 week
- [ ] Dashboard load time reduced by > 80%
- [ ] Zero reprocessing of cached data
- [ ] Snapshot restore < 1 second
- [ ] AI cost tracking 100% complete

### Usage Targets (1 month)
- [ ] At least 1 dashboard using caching
- [ ] Regular snapshots being saved
- [ ] Truth scores accumulating
- [ ] Justice scores calculated weekly
- [ ] AI costs monitored

---

## ✅ Final Sign-Off

### System Status
- [ ] ✅ Schema deployed to Supabase
- [ ] ✅ Tables verified (8/8)
- [ ] ✅ Tests passing (5/5)
- [ ] ✅ Performance verified
- [ ] ✅ Documentation complete
- [ ] ✅ Security reviewed
- [ ] ✅ Ready for production

### Deployment Approval

**Deployed by:** _______________
**Date:** _______________
**Test Results:** 5/5 Passing
**Status:** ✅ APPROVED FOR PRODUCTION

---

## 🎉 Next Steps

After completing this checklist:

1. **Clean up test data** (optional)
2. **Integrate into first dashboard**
3. **Monitor performance**
4. **Iterate and improve**
5. **Expand to more dashboards**

---

**Checklist Version:** 1.0
**Last Updated:** 2025-11-05
**System Status:** ✅ Production Ready
