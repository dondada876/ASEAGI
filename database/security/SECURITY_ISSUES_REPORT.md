# Supabase Security Issues Report

**Date:** November 10, 2025
**Severity:** HIGH
**Total Issues:** 140

---

## Summary

Supabase database linter has identified critical security issues:

### Issue Breakdown
- **76 views** with `SECURITY DEFINER` property (ERROR level)
- **64 tables** without Row Level Security (RLS) enabled (ERROR level)

---

## Issue 1: Security Definer Views (76 views)

### What This Means
Views defined with `SECURITY DEFINER` enforce the permissions and RLS policies of the **view creator**, not the querying user. This can bypass intended security controls.

### Risk Level: HIGH
- External users can access data they shouldn't see
- RLS policies are bypassed
- Potential data exposure

### Affected Views (Sample)
- `document_pages_assembly`
- `critical_documents_dashboard`
- `critical_events_action_required`
- `document_event_map`
- `violations_by_perpetrator`
- `ceo_dashboard`
- `bug_stats_by_workspace`
- And 69 more...

### Recommended Fix

**Option 1: Remove SECURITY DEFINER (Recommended)**
```sql
-- For each view, recreate without SECURITY DEFINER
ALTER VIEW public.document_pages_assembly SET (security_invoker = true);
```

**Option 2: Convert to SECURITY INVOKER**
```sql
-- This enforces permissions of the querying user
CREATE OR REPLACE VIEW public.document_pages_assembly
WITH (security_invoker = true)
AS
  SELECT ... -- existing view definition
```

---

## Issue 2: RLS Disabled on Tables (64 tables)

### What This Means
Tables without RLS are **publicly accessible** via PostgREST API with no access control. Anyone with the API key can read/write all data.

### Risk Level: CRITICAL
- **All data in these tables is public**
- No user-level access control
- Anyone with API key has full access
- Major data security breach risk

### Affected Tables (Critical)
1. **Legal Data** (HIGH RISK)
   - `legal_documents` - Contains case documents
   - `legal_violations` - Violation records
   - `legal_citations` - Legal citations
   - `case_law_precedents` - Case law data
   - `court_events` - Court event records

2. **Sensitive Data** (HIGH RISK)
   - `bugs` - Bug tracking data
   - `error_logs` - System error logs
   - `personal_documents` - Personal files
   - `family_documents` - Family records
   - `business_documents` - Business files

3. **System Data** (MEDIUM RISK)
   - `workspaces` - Workspace information
   - `processing_jobs_log` - Job logs
   - `ai_analysis_results` - AI results
   - `revenue_log` - Revenue data
   - And 50 more tables...

### Recommended Fix

**Enable RLS on All Tables**

```sql
-- For each table, enable RLS
ALTER TABLE public.legal_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bugs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.error_logs ENABLE ROW LEVEL SECURITY;
-- ... repeat for all 64 tables
```

**Then Create RLS Policies**

```sql
-- Example: Allow authenticated users to read their own workspace data
CREATE POLICY "Users can view own workspace documents"
  ON public.legal_documents
  FOR SELECT
  USING (auth.uid() IS NOT NULL);

-- Example: Admin full access
CREATE POLICY "Admins have full access"
  ON public.legal_documents
  FOR ALL
  USING (auth.jwt() ->> 'role' = 'admin');
```

---

## Immediate Actions Required

### Priority 1: Enable RLS on Critical Tables (URGENT)
These tables contain sensitive data and MUST be protected immediately:

```sql
-- Enable RLS on most critical tables
ALTER TABLE public.legal_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bugs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.error_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.personal_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.family_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.business_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.legal_violations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.case_law_precedents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.court_events ENABLE ROW LEVEL SECURITY;
```

### Priority 2: Fix Security Definer Views (HIGH)
Review and convert views to SECURITY INVOKER:

```sql
-- Fix critical dashboard views
ALTER VIEW public.ceo_dashboard SET (security_invoker = true);
ALTER VIEW public.critical_documents_dashboard SET (security_invoker = true);
ALTER VIEW public.critical_bugs_view SET (security_invoker = true);
```

### Priority 3: Create RLS Policies (HIGH)
After enabling RLS, create appropriate policies for each table.

---

## Migration Plan

### Step 1: Assessment
1. Review all 64 tables and determine access requirements
2. Identify which users/roles need access to each table
3. Document required RLS policies

### Step 2: Enable RLS
1. Enable RLS on all public tables
2. Verify no data access is broken

### Step 3: Create Policies
1. Create permissive policies for authenticated users
2. Create restrictive policies for sensitive data
3. Test policies with different user roles

### Step 4: Fix Views
1. Convert SECURITY DEFINER views to SECURITY INVOKER
2. Test view access with different users
3. Verify data is still accessible as intended

---

## Impact Analysis

### Current State (INSECURE)
- ❌ All 64 tables are **publicly accessible** via API
- ❌ 76 views bypass RLS policies
- ❌ No access control on sensitive data
- ❌ Major security vulnerability

### After Fix (SECURE)
- ✅ RLS enabled on all tables
- ✅ Access control based on user authentication
- ✅ Views respect user permissions
- ✅ Sensitive data protected

---

## Example RLS Policy Templates

### Template 1: Workspace-Based Access
```sql
-- Users can only access data in their workspace
CREATE POLICY "workspace_isolation"
  ON public.legal_documents
  FOR ALL
  USING (workspace_id IN (
    SELECT workspace_id FROM user_workspaces
    WHERE user_id = auth.uid()
  ));
```

### Template 2: Admin Full Access
```sql
-- Admins can access everything
CREATE POLICY "admin_full_access"
  ON public.legal_documents
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM user_roles
      WHERE user_id = auth.uid()
      AND role = 'admin'
    )
  );
```

### Template 3: Public Read, Authenticated Write
```sql
-- Anyone can read, only authenticated can write
CREATE POLICY "public_read_auth_write_select"
  ON public.legal_documents
  FOR SELECT
  USING (true);

CREATE POLICY "public_read_auth_write_insert"
  ON public.legal_documents
  FOR INSERT
  WITH CHECK (auth.uid() IS NOT NULL);
```

---

## Testing Plan

1. **Enable RLS** on a single test table
2. **Verify access is blocked** for unauthenticated users
3. **Create test policy** to allow specific access
4. **Verify policy works** as expected
5. **Roll out to all tables** systematically

---

## Resources

- Supabase RLS Documentation: https://supabase.com/docs/guides/auth/row-level-security
- Security Definer Views: https://supabase.com/docs/guides/database/database-linter?lint=0010_security_definer_view
- RLS Disabled Warning: https://supabase.com/docs/guides/database/database-linter?lint=0013_rls_disabled_in_public

---

## Next Steps

1. **Review this report** and understand the security implications
2. **Create backup** of database before making changes
3. **Apply Priority 1 fixes** immediately (enable RLS on critical tables)
4. **Create RLS policies** for each table
5. **Test thoroughly** to ensure access control works
6. **Apply Priority 2 fixes** (fix security definer views)
7. **Document policies** for future reference

---

**⚠️ WARNING: Until these issues are fixed, all data in the 64 tables without RLS is publicly accessible to anyone with your Supabase API key!**

---

## Additional Security Warnings (35 warnings)

### Issue 3: Function Search Path Mutable (34 functions)

**Severity:** WARN
**Risk Level:** MEDIUM

#### What This Means
Functions without an explicit `search_path` parameter can be vulnerable to search path attacks where malicious schemas are injected into the search path.

#### Affected Functions
- `get_department_stats`
- `auto_mark_private`
- `update_access_tracking`
- `soft_delete_file`
- `restore_file`
- `get_ceo_urgent_items`
- `update_days_since_filing`
- `get_timeline_range`
- `link_document_pages`
- `calculate_okr_progress`
- `update_okr_progress`
- `update_updated_at_column`
- `calculate_relevancy_score`
- `search_legal_documents`
- `get_document_full`
- `link_document_to_event`
- `create_event_with_documents`
- `get_event_details`
- `log_document_action`
- `get_document_full_proj344`
- `track_status_change`
- `calculate_criminal_evidence_score`
- `extract_page_from_filename`
- `calculate_violation_severity`
- `get_violation_evidence`
- `get_document_citations`
- `get_violation_citations`
- `calculate_precedential_value`
- `calculate_gap_duration`
- `clean_expired_cache`
- `increment_cache_hit`
- `archive_old_contexts`
- `generate_bug_number`
- `update_updated_at`

#### Recommended Fix

Add explicit `search_path` to each function:

```sql
-- Example fix for one function
ALTER FUNCTION public.get_department_stats()
SET search_path TO public, pg_catalog;

-- Or when creating the function
CREATE OR REPLACE FUNCTION public.get_department_stats()
RETURNS TABLE (...)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path TO public, pg_catalog
AS $$
BEGIN
  -- function body
END;
$$;
```

**Batch Fix Script:**

```sql
-- Fix all functions at once
ALTER FUNCTION public.get_department_stats() SET search_path TO public, pg_catalog;
ALTER FUNCTION public.auto_mark_private() SET search_path TO public, pg_catalog;
ALTER FUNCTION public.update_access_tracking() SET search_path TO public, pg_catalog;
ALTER FUNCTION public.soft_delete_file() SET search_path TO public, pg_catalog;
ALTER FUNCTION public.restore_file() SET search_path TO public, pg_catalog;
ALTER FUNCTION public.get_ceo_urgent_items() SET search_path TO public, pg_catalog;
ALTER FUNCTION public.update_days_since_filing() SET search_path TO public, pg_catalog;
ALTER FUNCTION public.get_timeline_range() SET search_path TO public, pg_catalog;
ALTER FUNCTION public.link_document_pages() SET search_path TO public, pg_catalog;
ALTER FUNCTION public.calculate_okr_progress() SET search_path TO public, pg_catalog;
ALTER FUNCTION public.update_okr_progress() SET search_path TO public, pg_catalog;
ALTER FUNCTION public.update_updated_at_column() SET search_path TO public, pg_catalog;
ALTER FUNCTION public.calculate_relevancy_score() SET search_path TO public, pg_catalog;
ALTER FUNCTION public.search_legal_documents(text) SET search_path TO public, pg_catalog;
ALTER FUNCTION public.get_document_full(uuid) SET search_path TO public, pg_catalog;
ALTER FUNCTION public.link_document_to_event(uuid, uuid) SET search_path TO public, pg_catalog;
ALTER FUNCTION public.create_event_with_documents(text, timestamp, text[], uuid[]) SET search_path TO public, pg_catalog;
ALTER FUNCTION public.get_event_details(uuid) SET search_path TO public, pg_catalog;
ALTER FUNCTION public.log_document_action(uuid, text, text) SET search_path TO public, pg_catalog;
ALTER FUNCTION public.get_document_full_proj344(uuid) SET search_path TO public, pg_catalog;
ALTER FUNCTION public.track_status_change() SET search_path TO public, pg_catalog;
ALTER FUNCTION public.calculate_criminal_evidence_score(uuid) SET search_path TO public, pg_catalog;
ALTER FUNCTION public.extract_page_from_filename(text) SET search_path TO public, pg_catalog;
ALTER FUNCTION public.calculate_violation_severity(text[], text[], text[]) SET search_path TO public, pg_catalog;
ALTER FUNCTION public.get_violation_evidence(uuid) SET search_path TO public, pg_catalog;
ALTER FUNCTION public.get_document_citations(uuid) SET search_path TO public, pg_catalog;
ALTER FUNCTION public.get_violation_citations(uuid) SET search_path TO public, pg_catalog;
ALTER FUNCTION public.calculate_precedential_value(text, text, integer) SET search_path TO public, pg_catalog;
ALTER FUNCTION public.calculate_gap_duration(timestamp, timestamp) SET search_path TO public, pg_catalog;
ALTER FUNCTION public.clean_expired_cache() SET search_path TO public, pg_catalog;
ALTER FUNCTION public.increment_cache_hit(text) SET search_path TO public, pg_catalog;
ALTER FUNCTION public.archive_old_contexts() SET search_path TO public, pg_catalog;
ALTER FUNCTION public.generate_bug_number() SET search_path TO public, pg_catalog;
ALTER FUNCTION public.update_updated_at() SET search_path TO public, pg_catalog;
```

---

### Issue 4: Extension in Public Schema (1 extension)

**Severity:** WARN
**Risk Level:** LOW

#### What This Means
The `pg_trgm` extension is installed in the `public` schema. Extensions should be installed in a dedicated schema to avoid potential conflicts and security issues.

#### Affected Extension
- `pg_trgm` (PostgreSQL trigram extension for similarity searches)

#### Recommended Fix

**Option 1: Create new schema and move extension:**

```sql
-- Create extensions schema
CREATE SCHEMA IF NOT EXISTS extensions;

-- Drop from public
DROP EXTENSION IF EXISTS pg_trgm CASCADE;

-- Recreate in extensions schema
CREATE EXTENSION pg_trgm SCHEMA extensions;

-- Update search_path if needed
ALTER DATABASE postgres SET search_path TO public, extensions, pg_catalog;
```

**Option 2: Leave in public but document:**

If `pg_trgm` is heavily used and moving would break functionality, document this as an accepted risk with proper access controls.

---

## Updated Issue Summary

**Total Issues: 175**

### By Severity
- **ERROR** (Critical): 140 issues
  - 76 SECURITY DEFINER views
  - 64 tables without RLS

- **WARN** (Medium): 35 issues
  - 34 functions with mutable search_path
  - 1 extension in public schema

### Priority Order
1. **URGENT**: Enable RLS on 64 tables (CRITICAL data exposure)
2. **HIGH**: Fix 76 SECURITY DEFINER views (bypasses RLS)
3. **MEDIUM**: Fix 34 function search_path issues (potential injection)
4. **LOW**: Move pg_trgm extension to dedicated schema

---

## Complete Remediation Script

### Phase 1: Critical RLS Issues (DO FIRST)

```sql
-- Enable RLS on all critical tables
ALTER TABLE public.legal_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bugs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.error_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.personal_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.family_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.business_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.legal_violations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.case_law_precedents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.court_events ENABLE ROW LEVEL SECURITY;
-- ... repeat for all 64 tables
```

### Phase 2: Fix SECURITY DEFINER Views

```sql
-- Convert critical dashboard views
ALTER VIEW public.ceo_dashboard SET (security_invoker = true);
ALTER VIEW public.critical_documents_dashboard SET (security_invoker = true);
ALTER VIEW public.critical_bugs_view SET (security_invoker = true);
-- ... repeat for all 76 views
```

### Phase 3: Fix Function Search Paths

```sql
-- Set explicit search_path on all functions
ALTER FUNCTION public.generate_bug_number() SET search_path TO public, pg_catalog;
ALTER FUNCTION public.update_updated_at() SET search_path TO public, pg_catalog;
-- ... repeat for all 34 functions (see batch script above)
```

### Phase 4: Move Extension (Optional)

```sql
-- Move pg_trgm to extensions schema
CREATE SCHEMA IF NOT EXISTS extensions;
DROP EXTENSION IF EXISTS pg_trgm CASCADE;
CREATE EXTENSION pg_trgm SCHEMA extensions;
```

---

**📊 Updated Statistics:**
- Total Security Issues: 175
- Critical (ERROR): 140
- Medium (WARN): 35
- Tables at Risk: 64
- Views at Risk: 76
- Functions at Risk: 34
- Extensions at Risk: 1
