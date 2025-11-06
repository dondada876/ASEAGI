#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script: Verify Context Preservation Schema Deployment
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

def test_schema_deployment():
    """Verify all tables and views were created"""

    print("=" * 70)
    print("CONTEXT PRESERVATION SCHEMA - VERIFICATION TEST")
    print("=" * 70)
    print()

    # Connect to Supabase - try secrets.toml first
    try:
        import toml
        secrets_path = Path(__file__).parent / '.streamlit' / 'secrets.toml'
        if secrets_path.exists():
            secrets = toml.load(secrets_path)
            url = secrets.get('SUPABASE_URL', 'https://jvjlhxodmbkodzmggwpu.supabase.co')
            key = secrets.get('SUPABASE_KEY')
        else:
            url = os.environ.get('SUPABASE_URL', 'https://jvjlhxodmbkodzmggwpu.supabase.co')
            key = os.environ.get('SUPABASE_KEY')
    except:
        url = os.environ.get('SUPABASE_URL', 'https://jvjlhxodmbkodzmggwpu.supabase.co')
        key = os.environ.get('SUPABASE_KEY')

    if not key:
        print("❌ Error: SUPABASE_KEY not set")
        print("   Either set environment variable or ensure .streamlit/secrets.toml exists")
        return False

    print("🔗 Connecting to Supabase...")
    print(f"   URL: {url}")

    try:
        supabase = create_client(url, key)
        print("   ✅ Connected!")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False

    print()

    # Expected tables
    expected_tables = [
        'system_processing_cache',
        'dashboard_snapshots',
        'ai_analysis_results',
        'query_results_cache',
        'truth_score_history',
        'justice_score_rollups',
        'processing_jobs_log',
        'context_preservation_metadata'
    ]

    print("📊 Testing Tables...")
    print()

    tables_ok = 0
    tables_missing = 0

    for table_name in expected_tables:
        try:
            # Try to query the table (limit 0 to avoid loading data)
            response = supabase.table(table_name).select('*', count='exact').limit(0).execute()
            print(f"   ✅ {table_name:<35} (0 rows)")
            tables_ok += 1
        except Exception as e:
            error_msg = str(e)
            if 'does not exist' in error_msg or '42P01' in error_msg:
                print(f"   ❌ {table_name:<35} NOT FOUND")
                tables_missing += 1
            else:
                print(f"   ⚠️  {table_name:<35} Error: {error_msg[:50]}")
                tables_missing += 1

    print()
    print("=" * 70)
    print(f"RESULTS: {tables_ok}/{len(expected_tables)} tables found")

    if tables_missing > 0:
        print(f"❌ {tables_missing} tables are missing!")
        print()
        print("ACTION REQUIRED:")
        print("1. Go to: https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu/sql")
        print("2. Click 'New Query'")
        print("3. Copy ALL contents from: schemas/context_preservation_schema.sql")
        print("4. Paste into SQL editor")
        print("5. Click 'Run'")
        print()
        return False
    else:
        print("✅ All tables exist! Schema deployment successful!")
        print()
        print("=" * 70)
        print("NEXT STEP: Test ContextManager functionality")
        print("Run: python test_context_manager.py")
        print("=" * 70)
        return True

if __name__ == "__main__":
    success = test_schema_deployment()
    sys.exit(0 if success else 1)
