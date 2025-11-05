#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deploy Context Preservation Schema to Supabase
"""

import os
import sys
from pathlib import Path
from supabase import create_client

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def deploy_schema():
    """Deploy the context preservation schema to Supabase"""

    print("=" * 70)
    print("CONTEXT PRESERVATION SCHEMA DEPLOYMENT")
    print("=" * 70)
    print()

    # Get credentials
    url = os.environ.get('SUPABASE_URL', 'https://jvjlhxodmbkodzmggwpu.supabase.co')
    key = os.environ.get('SUPABASE_KEY')

    if not key:
        print("❌ Error: SUPABASE_KEY environment variable not set")
        print()
        print("Please set it with:")
        print("  export SUPABASE_KEY='your-key'")
        return False

    # Read schema file
    schema_file = Path(__file__).parent / 'context_preservation_schema.sql'

    if not schema_file.exists():
        print(f"❌ Error: Schema file not found: {schema_file}")
        return False

    print(f"📄 Reading schema from: {schema_file}")
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    print(f"   File size: {len(schema_sql)} bytes")
    print()

    # Connect to Supabase
    print("🔗 Connecting to Supabase...")
    print(f"   URL: {url}")

    try:
        supabase = create_client(url, key)
        print("   ✅ Connected!")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False

    print()

    # Note about deployment
    print("=" * 70)
    print("IMPORTANT: Schema Deployment")
    print("=" * 70)
    print()
    print("⚠️  The SQL schema must be deployed via the Supabase SQL Editor.")
    print()
    print("Steps to deploy:")
    print("1. Go to: https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu/sql")
    print("2. Click 'New Query'")
    print(f"3. Copy the contents of: {schema_file}")
    print("4. Paste into the SQL editor")
    print("5. Click 'Run' to execute")
    print()
    print("Tables that will be created:")
    print("  1. system_processing_cache")
    print("  2. dashboard_snapshots")
    print("  3. ai_analysis_results")
    print("  4. query_results_cache")
    print("  5. truth_score_history")
    print("  6. justice_score_rollups")
    print("  7. processing_jobs_log")
    print("  8. context_preservation_metadata")
    print()
    print("Views that will be created:")
    print("  - active_cache_entries")
    print("  - recent_dashboard_snapshots")
    print("  - truth_score_summary")
    print("  - processing_cost_summary")
    print("  - active_processing_jobs")
    print()
    print("Functions that will be created:")
    print("  - clean_expired_cache()")
    print("  - increment_cache_hit()")
    print("  - archive_old_contexts()")
    print()
    print("=" * 70)
    print()

    # Verify we can access existing tables
    print("🔍 Verifying database access...")
    try:
        response = supabase.table('legal_documents').select('id', count='exact').limit(1).execute()
        print(f"   ✅ Can access legal_documents table ({response.count} records)")
    except Exception as e:
        print(f"   ⚠️  Warning: Could not access legal_documents: {e}")

    print()
    print("=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print()
    print("After deploying the schema:")
    print("1. Test the ContextManager utility:")
    print("   python utilities/context_manager.py")
    print()
    print("2. Use it in your dashboards:")
    print("   from utilities.context_manager import ContextManager")
    print("   cm = ContextManager()")
    print("   cm.save_dashboard_snapshot('truth_justice_timeline', data)")
    print()
    print("3. Query cached results:")
    print("   cached = cm.get_cache('my_expensive_query')")
    print()
    print("=" * 70)
    print()

    return True


if __name__ == "__main__":
    success = deploy_schema()
    sys.exit(0 if success else 1)
