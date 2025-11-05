# PROJ344 Data Sync Analysis

## Current Status Summary

Based on your dashboard showing:
- ✅ **653 Legal Documents** - Good
- ✅ **253 Court Events** - Good
- ⚠️ **3 Pages Analyzed** - CRITICALLY LOW
- ⚠️ **1 Violation Tracked** - CRITICALLY LOW
- ⚠️ **0 Communications** - MISSING
- ✅ **1 DVRO Violation** - Present
- ⚠️ **0 Court Cases** - MISSING
- ✅ **3 Legal Citations** - Present

---

## 🔍 Problem Identified

**Your Mac Mini is uploading METADATA but NOT uploading ANALYSIS DATA**

### What's Working:
✅ Basic document records (`legal_documents` table)
✅ Court events (`court_events` table)
✅ Supabase connection from both machines

### What's NOT Working:
❌ **Page-level analysis** (`document_pages` table) - Only 3 pages vs. expected thousands
❌ **Detailed violation tracking** (`legal_violations` table) - Only 1 violation vs. expected dozens
❌ **Communications matrix** (`communications_matrix` table) - 0 records
❌ **Multi-jurisdiction tracking** (`court_case_tracker` table) - 0 records
❌ **False statements analysis** (micro analysis tables) - Missing
❌ **Checkbox perjury tracking** - Missing
❌ **Actions vs intentions analysis** - Missing

---

## 📊 Expected vs. Actual Data

According to your PROJ344 documentation, the system should have:

| Data Type | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Legal Documents | 500-1000 | 653 | ✅ Good |
| Document Pages | 5,000-10,000+ | 3 | 🚨 **CRITICAL** |
| Court Events | 200-300 | 253 | ✅ Good |
| Legal Violations | 50-100+ | 1 | 🚨 **CRITICAL** |
| Communications | 100-500 | 0 | 🚨 **CRITICAL** |
| DVRO Violations | 5-20 | 1 | ⚠️ Low |
| Court Cases | 3-10 | 0 | 🚨 **CRITICAL** |
| Legal Citations | 50-200 | 3 | 🚨 **CRITICAL** |

---

## 🔧 Root Causes

### Most Likely Issues on Mac Mini:

#### 1. **Processing Scripts Not Running All Modules**
Your Mac Mini may be running the document upload script but NOT running:
- `micro_analysis_processor.py` (or similar)
- `violation_tracker.py`
- `communications_analyzer.py`
- `page_level_processor.py`

#### 2. **Incomplete Data Pipeline**
The processing flow should be:
```
Document Upload → Page Extraction → Content Analysis → Violation Detection → Supabase Upload
```

Your pipeline is stopping after "Document Upload"

#### 3. **Script Errors Being Silently Ignored**
- Check Mac Mini logs for errors
- Analysis scripts may be crashing but basic upload succeeds
- Error handling might be swallowing exceptions

#### 4. **Database Table Permissions**
- Some tables might have write restrictions
- Check Supabase RLS (Row Level Security) policies
- Anon key may not have INSERT permissions on analysis tables

---

## 🔎 Diagnostic Steps

### Step 1: Check Running Processes on Mac Mini
```bash
# SSH into Mac Mini or check locally
ps aux | grep python
ps aux | grep PROJ344
```

Look for processes like:
- ✅ `document_uploader.py` (running - this is why you have 653 docs)
- ❓ `page_analyzer.py` (probably NOT running)
- ❓ `violation_processor.py` (probably NOT running)
- ❓ `micro_analysis.py` (probably NOT running)

### Step 2: Check Mac Mini Logs
Look in these locations:
- `~/PROJ344/logs/`
- `~/logs/`
- `/var/log/PROJ344/`
- Check for files like:
  - `document_processor.log`
  - `page_analysis.log`
  - `violation_tracker.log`
  - `supabase_upload.log`

Look for errors like:
- "Permission denied"
- "Table not found"
- "Connection refused"
- "Module not found"
- "Timeout"

### Step 3: Verify Supabase Table Permissions
Run this diagnostic:
```python
# Test INSERT permissions on each table
from supabase import create_client

supabase = create_client(URL, KEY)

tables = ['document_pages', 'legal_violations', 'communications_matrix']

for table in tables:
    try:
        # Try to insert a test record
        result = supabase.table(table).insert({'test': 'value'}).execute()
        print(f"✅ {table}: INSERT allowed")
    except Exception as e:
        print(f"❌ {table}: INSERT FAILED - {e}")
```

### Step 4: Check Mac Mini Script Configuration
Look for configuration files:
- `.env` - Check SUPABASE_URL and SUPABASE_KEY match Windows
- `config.toml`
- `settings.json`
- `proj344_config.py`

Verify:
- Database credentials are correct
- All processing modules are enabled
- No "skip_analysis" or "metadata_only" flags set

---

## 🛠️ Solutions

### Solution 1: Verify Mac Mini Processing Scripts

On your Mac Mini, check which scripts are scheduled to run:

```bash
# Check cron jobs
crontab -l

# Check launchd (macOS scheduler)
ls ~/Library/LaunchAgents/
launchctl list | grep proj344

# Check running processes
ps aux | grep -i proj344
```

### Solution 2: Manually Run Analysis Scripts

Try running these manually on Mac Mini:

```bash
# Navigate to PROJ344 directory
cd ~/PROJ344  # or wherever your project is

# Run page-level analysis
python3 page_analyzer.py --process-all

# Run violation detection
python3 violation_processor.py --scan-documents

# Run communications analysis
python3 communications_parser.py --sync

# Run micro-level analysis
python3 micro_analysis_processor.py --full-scan
```

Watch for errors during execution.

### Solution 3: Check Supabase Dashboard

1. Go to: https://supabase.com/dashboard
2. Sign in to your project
3. Navigate to: **Table Editor**
4. Check these tables exist:
   - ✅ `legal_documents`
   - ❓ `document_pages`
   - ❓ `legal_violations`
   - ❓ `communications_matrix`
   - ❓ `dvro_violations_tracker`
   - ❓ `court_case_tracker`

5. Check **Database → Policies** (RLS):
   - Verify INSERT policies exist for all tables
   - Check if anon key has write permissions

### Solution 4: Re-run Full Processing Pipeline

On Mac Mini, run complete reprocessing:

```bash
# Full system reprocess (this may take hours)
python3 proj344_master_processor.py --full-reprocess --upload-all

# Or process incrementally
python3 proj344_master_processor.py --process-new --analyze --upload
```

---

## 📋 Quick Checklist for Mac Mini

Run through this checklist on your Mac Mini:

- [ ] Verify all processing scripts are installed
- [ ] Check cron jobs or scheduled tasks are running
- [ ] Review logs for errors in last 24 hours
- [ ] Confirm Supabase credentials match Windows
- [ ] Test INSERT permissions on all tables
- [ ] Manually run page analyzer script
- [ ] Manually run violation processor script
- [ ] Check disk space (low space can cause silent failures)
- [ ] Verify Python dependencies are installed
- [ ] Check network connectivity to Supabase
- [ ] Review any "skip" or "disabled" configuration flags
- [ ] Ensure file paths to documents are correct

---

## 🎯 Expected Behavior After Fix

Once Mac Mini processing is fully working, you should see:

### Immediate Changes:
- `document_pages`: 5,000-10,000+ records (one per page of each document)
- `legal_violations`: 50-100+ records (constitutional violations identified)
- `communications_matrix`: 100-500+ records (emails, texts, etc.)
- `false_statements`: 20-50+ records (perjury instances)
- `checkbox_perjury`: 10-30+ records (false checkboxes on forms)

### Dashboard Impact:
- **Overview page**: All 8 metrics show substantial numbers
- **Documents Intelligence**: Full scoring (micro/macro/legal numbers populate)
- **Legal Violations**: Dozens of tracked violations with perpetrator analysis
- **Micro Analysis**: False statements, checkbox perjury, actions vs intentions
- **Communications**: Full matrix of party interactions
- **Timeline**: Rich, multi-dimensional timeline with all events

---

## 🔍 Diagnostic Tool

**I've created a diagnostic dashboard for you:**

**Local Access**: http://localhost:8502
**Network Access**: http://192.168.4.24:8502

This tool will:
- ✅ Check all 15+ core tables
- ✅ Show exact row counts for each table
- ✅ Display sample data from each table
- ✅ Identify which tables are empty
- ✅ Provide specific recommendations
- ✅ Show last update timestamps

**Run it now to see detailed analysis!**

---

## 💡 Recommendations

### Immediate Actions (Do These First):

1. **Open diagnostic dashboard** at http://localhost:8502
2. **Review which specific tables are empty**
3. **Check Mac Mini logs** for processing errors
4. **Verify Mac Mini scripts are running** (check processes)
5. **Test Supabase INSERT permissions** on empty tables

### Short-term Actions:

6. **Manually run analysis scripts** on Mac Mini
7. **Review Mac Mini cron jobs** to ensure scheduled execution
8. **Check configuration files** for "skip_analysis" flags
9. **Verify file paths** to document directories are correct
10. **Monitor logs** during next processing cycle

### Long-term Actions:

11. **Set up monitoring** for Mac Mini processing health
12. **Create alerts** for failed uploads
13. **Implement retry logic** for failed analysis
14. **Schedule regular full reprocessing**
15. **Document Mac Mini setup** for reproducibility

---

## 📞 Next Steps

### For You:
1. **Access diagnostic dashboard**: http://localhost:8502
2. **Screenshot the results** (especially empty tables)
3. **Check Mac Mini**:
   - What scripts are running?
   - Any errors in logs?
   - When was last processing run?
4. **Report back findings** so we can provide specific fixes

### For Mac Mini:
- Identify which processing scripts exist
- Determine which are running vs. not running
- Fix or restart missing analysis processes
- Monitor next processing cycle

---

## 🔐 Security Note

Your Supabase **anon key** (currently in use) typically has:
- ✅ SELECT permissions (reading data) - Working
- ❓ INSERT permissions (writing data) - May be restricted on some tables

If INSERT permissions are blocked by RLS policies:
- Document uploads work (basic metadata)
- Detailed analysis uploads fail silently

**Solution**: Check Supabase RLS policies or use service_role key for processing.

---

*Dashboard Last Updated: 2025-11-05 20:54*
*Analysis Generated: 2025-11-05 21:00*
