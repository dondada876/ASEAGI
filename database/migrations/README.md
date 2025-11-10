# Bug Tracker Database Migration

## Overview
This migration adds the missing columns to the `bugs` table that are required for automatic bug ticket creation from critical errors.

## Missing Columns
- `occurrence_count` - Tracks how many times this error has occurred
- `first_occurred_at` - Timestamp when error first occurred
- `last_occurred_at` - Timestamp when error most recently occurred

## How to Apply Migration

### Option 1: Supabase SQL Editor (RECOMMENDED)

1. **Open Supabase SQL Editor**
   - Go to: https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu/sql/new

2. **Copy SQL from `add_bug_tracking_columns.sql`**
   - The SQL is in this same directory

3. **Paste and Execute**
   - Click "Run" to execute the migration

4. **Verify**
   - Check that the columns were added:
   ```sql
   SELECT column_name, data_type, column_default
   FROM information_schema.columns
   WHERE table_name = 'bugs'
   AND column_name IN ('occurrence_count', 'first_occurred_at', 'last_occurred_at')
   ORDER BY column_name;
   ```

### Option 2: Python Script with Database Password

If you have the Supabase database password:

```bash
# Install psycopg2 if needed
pip install psycopg2-binary

# Run migration
SUPABASE_DB_PASSWORD='your-password' python3 apply_bug_tracking_migration.py
```

To get your database password:
1. Go to: https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu/settings/database
2. Look for "Database password" or reset it if needed

## What This Fixes

### Before Migration
- ❌ Critical errors logged to `error_logs` table
- ❌ Automatic bug creation fails with: `column bugs.occurrence_count does not exist`
- ❌ No bug tickets created automatically

### After Migration
- ✅ Critical errors logged to `error_logs` table
- ✅ Automatic bug creation succeeds
- ✅ Bug tickets created with error details
- ✅ Duplicate error detection (updates occurrence_count instead of creating new bugs)
- ✅ Full error tracking and bug management

## Testing After Migration

After applying the migration, test automatic bug creation:

```bash
ssh root@137.184.1.91
cd /root/phase0_bug_tracker

# Run bug tracker test
SUPABASE_URL='https://jvjlhxodmbkodzmggwpu.supabase.co' \
SUPABASE_KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2amxoeG9kbWJrb2R6bWdnd3B1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyMjMxOTAsImV4cCI6MjA3Nzc5OTE5MH0.ai65vVW816bNAV56XiuRxp5PE5IhBkMGPx3IbxfPh8c' \
python3 -c "
from core.bug_tracker import BugTracker

tracker = BugTracker()
print('Testing bug tracker...')

# Test critical error with auto-bug creation
try:
    raise RuntimeError('Test error for automatic bug creation')
except Exception as e:
    log_id = tracker.log('critical', 'Test critical error', 'test', error=e, workspace_id='legal')
    print(f'✅ Critical error logged: {log_id}')

print('✅ Check Supabase bugs table for new bug ticket!')
"
```

Expected result: A new bug ticket should be created in the `bugs` table with:
- Title like: "Critical: test - RuntimeError"
- `occurrence_count` = 1
- `first_occurred_at` and `last_occurred_at` timestamps set
- Error message and stack trace captured

## Rollback

If you need to rollback this migration:

```sql
ALTER TABLE bugs
DROP COLUMN IF EXISTS occurrence_count,
DROP COLUMN IF EXISTS first_occurred_at,
DROP COLUMN IF EXISTS last_occurred_at;

DROP INDEX IF EXISTS idx_bugs_error_message_status;
DROP INDEX IF EXISTS idx_bugs_last_occurred;
```
