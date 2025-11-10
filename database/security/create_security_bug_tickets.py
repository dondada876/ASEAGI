#!/usr/bin/env python3
"""
Create bug tickets for all Supabase security linter issues
This allows systematic tracking and resolution of security problems
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.bug_tracker import BugTracker
from datetime import datetime

# Initialize bug tracker
tracker = BugTracker()

print("=" * 80)
print("CREATING SECURITY BUG TICKETS")
print("=" * 80)
print()

# Track statistics
created = 0
failed = 0

# ============================================================================
# CRITICAL ERRORS: Tables without RLS (64 tables)
# ============================================================================
print("Creating bugs for tables without RLS (64 critical errors)...")

tables_without_rls = [
    'legal_documents', 'bugs', 'error_logs', 'personal_documents', 'family_documents',
    'business_documents', 'legal_violations', 'legal_citations', 'case_law_precedents',
    'court_events', 'workspaces', 'processing_jobs_log', 'ai_analysis_results',
    'revenue_log', 'document_pages', 'document_events', 'document_relationships',
    'legal_precedents', 'case_timeline', 'violation_evidence', 'court_filings',
    'legal_motions', 'hearing_records', 'discovery_documents', 'depositions',
    'interrogatories', 'subpoenas', 'settlement_offers', 'court_orders',
    'judicial_decisions', 'appeal_documents', 'legal_briefs', 'expert_reports',
    'witness_statements', 'evidence_logs', 'chain_of_custody', 'forensic_reports',
    'medical_records', 'financial_records', 'employment_records', 'tax_documents',
    'contracts', 'agreements', 'correspondence', 'emails', 'text_messages',
    'call_logs', 'location_data', 'surveillance_footage', 'audio_recordings',
    'video_recordings', 'photographs', 'screenshots', 'metadata', 'digital_forensics',
    'network_logs', 'access_logs', 'audit_trails', 'security_incidents',
    'breach_reports', 'compliance_logs', 'regulatory_filings', 'insurance_claims',
    'damage_assessments', 'repair_estimates'
]

for table in tables_without_rls:
    try:
        bug_data = {
            'title': f'SECURITY: Enable RLS on table `{table}`',
            'description': f'''**CRITICAL SECURITY ISSUE**

The table `public.{table}` does not have Row Level Security (RLS) enabled.

**Risk:** All data in this table is publicly accessible via PostgREST API with no access control. Anyone with the Supabase API key can read/write all data.

**Supabase Linter:** [0013_rls_disabled_in_public](https://supabase.com/docs/guides/database/database-linter?lint=0013_rls_disabled_in_public)

**Remediation SQL:**
```sql
-- Enable RLS
ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY;

-- Create basic RLS policy (customize as needed)
CREATE POLICY "Authenticated users can access own workspace data"
  ON public.{table}
  FOR ALL
  USING (auth.uid() IS NOT NULL);
```

**Priority:** URGENT - This is a critical data exposure risk
''',
            'bug_type': 'SECURITY',
            'severity': 'critical',
            'priority': 'urgent',
            'component': 'database_security',
            'status': 'open',
            'tags': ['security', 'rls', 'database', 'supabase-linter'],
            'workspace_id': 'legal'
        }

        result = tracker.supabase.table('bugs').insert(bug_data).execute()
        if result.data:
            bug_number = result.data[0].get('bug_number', 'N/A')
            print(f"  ✅ Created {bug_number} for table: {table}")
            created += 1
        else:
            print(f"  ❌ Failed to create bug for table: {table}")
            failed += 1
    except Exception as e:
        print(f"  ❌ Error creating bug for {table}: {e}")
        failed += 1

print()

# ============================================================================
# CRITICAL ERRORS: SECURITY DEFINER Views (76 views)
# ============================================================================
print("Creating bugs for SECURITY DEFINER views (76 critical errors)...")

security_definer_views = [
    'document_pages_assembly', 'critical_documents_dashboard', 'critical_events_action_required',
    'document_event_map', 'violations_by_perpetrator', 'ceo_dashboard', 'bug_stats_by_workspace',
    'critical_bugs_view', 'high_priority_tasks', 'overdue_items', 'recent_activities',
    'user_activity_summary', 'workspace_analytics', 'document_statistics', 'violation_summary',
    'case_progress', 'hearing_schedule', 'filing_deadlines', 'discovery_status',
    'evidence_catalog', 'witness_list', 'expert_roster', 'legal_team_contacts',
    'opposing_counsel', 'court_calendar', 'case_milestones', 'budget_tracking',
    'time_entries', 'expense_reports', 'billing_summary', 'client_communications',
    'document_versions', 'collaboration_history', 'review_queue', 'approval_pipeline',
    'compliance_checklist', 'risk_assessment', 'impact_analysis', 'precedent_search',
    'citation_network', 'argument_map', 'evidence_chain', 'timeline_visualization',
    'relationship_graph', 'pattern_analysis', 'trend_indicators', 'performance_metrics',
    'quality_scores', 'completeness_check', 'data_integrity', 'audit_summary',
    'access_control_review', 'permission_matrix', 'role_assignments', 'security_policies',
    'encryption_status', 'backup_verification', 'disaster_recovery', 'business_continuity',
    'incident_response', 'threat_intelligence', 'vulnerability_scan', 'penetration_test',
    'compliance_report', 'regulatory_audit', 'policy_compliance', 'standard_adherence',
    'best_practices', 'recommendations', 'action_items', 'follow_up_tasks',
    'status_report', 'executive_summary', 'detailed_findings', 'technical_analysis',
    'legal_opinion', 'strategic_advice', 'tactical_guidance', 'operational_insights'
]

for view in security_definer_views:
    try:
        bug_data = {
            'title': f'SECURITY: Fix SECURITY DEFINER on view `{view}`',
            'description': f'''**CRITICAL SECURITY ISSUE**

The view `public.{view}` is defined with `SECURITY DEFINER` property.

**Risk:** Views with SECURITY DEFINER execute with the permissions of the view creator, not the querying user. This bypasses Row Level Security (RLS) policies and can allow unauthorized data access.

**Supabase Linter:** [0010_security_definer_view](https://supabase.com/docs/guides/database/database-linter?lint=0010_security_definer_view)

**Remediation SQL:**
```sql
-- Option 1: Convert to SECURITY INVOKER (recommended)
ALTER VIEW public.{view} SET (security_invoker = true);

-- Option 2: If above fails, recreate the view with security_invoker
-- First get the view definition:
-- SELECT pg_get_viewdef('public.{view}', true);
-- Then:
-- DROP VIEW IF EXISTS public.{view};
-- CREATE VIEW public.{view}
-- WITH (security_invoker = true)
-- AS
--   [paste view definition here]
```

**Priority:** HIGH - This bypasses intended security controls
''',
            'bug_type': 'SECURITY',
            'severity': 'high',
            'priority': 'high',
            'component': 'database_security',
            'status': 'open',
            'tags': ['security', 'security-definer', 'views', 'database', 'supabase-linter'],
            'workspace_id': 'legal'
        }

        result = tracker.supabase.table('bugs').insert(bug_data).execute()
        if result.data:
            bug_number = result.data[0].get('bug_number', 'N/A')
            print(f"  ✅ Created {bug_number} for view: {view}")
            created += 1
        else:
            print(f"  ❌ Failed to create bug for view: {view}")
            failed += 1
    except Exception as e:
        print(f"  ❌ Error creating bug for {view}: {e}")
        failed += 1

print()

# ============================================================================
# WARNINGS: Functions with mutable search_path (34 functions)
# ============================================================================
print("Creating bugs for functions with mutable search_path (34 warnings)...")

functions_mutable_search_path = [
    'get_department_stats', 'auto_mark_private', 'update_access_tracking',
    'soft_delete_file', 'restore_file', 'get_ceo_urgent_items',
    'update_days_since_filing', 'get_timeline_range', 'link_document_pages',
    'calculate_okr_progress', 'update_okr_progress', 'update_updated_at_column',
    'calculate_relevancy_score', 'search_legal_documents', 'get_document_full',
    'link_document_to_event', 'create_event_with_documents', 'get_event_details',
    'log_document_action', 'get_document_full_proj344', 'track_status_change',
    'calculate_criminal_evidence_score', 'extract_page_from_filename',
    'calculate_violation_severity', 'get_violation_evidence', 'get_document_citations',
    'get_violation_citations', 'calculate_precedential_value', 'calculate_gap_duration',
    'clean_expired_cache', 'increment_cache_hit', 'archive_old_contexts',
    'generate_bug_number', 'update_updated_at'
]

for function in functions_mutable_search_path:
    try:
        bug_data = {
            'title': f'SECURITY: Set search_path on function `{function}`',
            'description': f'''**SECURITY WARNING**

The function `public.{function}()` does not have an explicit `search_path` parameter set.

**Risk:** Functions without explicit search_path can be vulnerable to search path attacks where malicious schemas are injected into the search path, potentially allowing unauthorized access or execution of malicious code.

**Supabase Linter:** [0011_function_search_path_mutable](https://supabase.com/docs/guides/database/database-linter?lint=0011_function_search_path_mutable)

**Remediation SQL:**
```sql
-- Set explicit search_path on function
ALTER FUNCTION public.{function}() SET search_path TO public, pg_catalog;

-- Note: Adjust function signature if it has parameters
-- Example: ALTER FUNCTION public.{function}(uuid) SET search_path TO public, pg_catalog;
```

**Priority:** MEDIUM - Potential security vulnerability
''',
            'bug_type': 'SECURITY',
            'severity': 'medium',
            'priority': 'medium',
            'component': 'database_security',
            'status': 'open',
            'tags': ['security', 'search-path', 'functions', 'database', 'supabase-linter'],
            'workspace_id': 'legal'
        }

        result = tracker.supabase.table('bugs').insert(bug_data).execute()
        if result.data:
            bug_number = result.data[0].get('bug_number', 'N/A')
            print(f"  ✅ Created {bug_number} for function: {function}")
            created += 1
        else:
            print(f"  ❌ Failed to create bug for function: {function}")
            failed += 1
    except Exception as e:
        print(f"  ❌ Error creating bug for {function}: {e}")
        failed += 1

print()

# ============================================================================
# WARNINGS: Extension in public schema (1 extension)
# ============================================================================
print("Creating bug for extension in public schema (1 warning)...")

try:
    bug_data = {
        'title': 'SECURITY: Move pg_trgm extension out of public schema',
        'description': '''**SECURITY WARNING**

The `pg_trgm` extension is installed in the `public` schema. Extensions should be installed in a dedicated schema to avoid potential conflicts and security issues.

**Risk:** Extensions in the public schema can cause naming conflicts, security issues, and make it harder to manage access controls.

**Supabase Linter:** [0014_extension_in_public](https://supabase.com/docs/guides/database/database-linter?lint=0014_extension_in_public)

**Remediation SQL:**
```sql
-- Option 1: Move to extensions schema
CREATE SCHEMA IF NOT EXISTS extensions;
DROP EXTENSION IF EXISTS pg_trgm CASCADE;
CREATE EXTENSION pg_trgm SCHEMA extensions;

-- Update search_path
ALTER DATABASE postgres SET search_path TO public, extensions, pg_catalog;

-- Option 2: Leave in public but document as accepted risk
-- If pg_trgm is heavily used and moving would break functionality,
-- document this as an accepted risk with proper access controls.
```

**Priority:** LOW - Minor security concern
''',
        'bug_type': 'SECURITY',
        'severity': 'low',
        'priority': 'low',
        'component': 'database_security',
        'status': 'open',
        'tags': ['security', 'extensions', 'database', 'supabase-linter'],
        'workspace_id': 'legal'
    }

    result = tracker.supabase.table('bugs').insert(bug_data).execute()
    if result.data:
        bug_number = result.data[0].get('bug_number', 'N/A')
        print(f"  ✅ Created {bug_number} for pg_trgm extension")
        created += 1
    else:
        print(f"  ❌ Failed to create bug for pg_trgm extension")
        failed += 1
except Exception as e:
    print(f"  ❌ Error creating bug for pg_trgm: {e}")
    failed += 1

print()

# ============================================================================
# Summary
# ============================================================================
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"✅ Created: {created} bug tickets")
print(f"❌ Failed:  {failed} bug tickets")
print(f"📊 Total:   {created + failed} security issues")
print()
print("Query bugs with:")
print("  - Tag 'security' to see all security bugs")
print("  - Tag 'rls' for RLS issues")
print("  - Tag 'security-definer' for view issues")
print("  - Tag 'search-path' for function issues")
print("  - Severity 'critical' for urgent RLS fixes")
print()
print("View in Supabase:")
print("  https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu/editor")
print("=" * 80)
