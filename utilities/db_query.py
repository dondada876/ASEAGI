#!/usr/bin/env python3
"""
DATABASE QUERY INTERFACE FOR CLAUDE
Query the database instead of reading files - saves tokens and context window

This tool allows Claude (or any LLM) to query the Supabase database directly
instead of re-reading documents, saving massive amounts of tokens.

Usage:
  # Quick queries
  python db_query.py --police-reports
  python db_query.py --summary
  python db_query.py --search "keyword"

  # Specific queries
  python db_query.py --recent 10
  python db_query.py --high-relevancy
  python db_query.py --by-type "Police Report"

  # Database info
  python db_query.py --tables
  python db_query.py --stats
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import argparse

try:
    from supabase import create_client
except ImportError:
    print("❌ Install supabase: pip install supabase")
    sys.exit(1)

# ============================================================================
# CREDENTIALS
# ============================================================================

def get_credentials():
    """Get Supabase credentials"""
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')

    if not url or not key:
        try:
            import streamlit as st
            url = st.secrets.get('SUPABASE_URL')
            key = st.secrets.get('SUPABASE_KEY')
        except:
            pass

    if not url or not key:
        try:
            import toml
            secrets_path = Path(__file__).parent / '.streamlit' / 'secrets.toml'
            if not secrets_path.exists():
                secrets_path = Path(__file__).parent.parent / '.streamlit' / 'secrets.toml'
            if secrets_path.exists():
                secrets = toml.load(secrets_path)
                url = secrets.get('SUPABASE_URL')
                key = secrets.get('SUPABASE_KEY')
        except:
            pass

    if not url:
        url = 'https://jvjlhxodmbkodzmggwpu.supabase.co'

    return url, key

# ============================================================================
# QUERY FUNCTIONS
# ============================================================================

def get_database_summary(client):
    """Get high-level summary - SAVES MASSIVE TOKENS"""
    print("📊 DATABASE SUMMARY")
    print("=" * 80)
    print("Use this instead of reading all files!")
    print()

    # Document count
    response = client.table('legal_documents').select('*', count='exact').limit(0).execute()
    total_docs = response.count if hasattr(response, 'count') else 0

    print(f"📄 Total Documents: {total_docs}")
    print()

    # Police reports count
    response = client.table('legal_documents').select('*', count='exact')\
        .ilike('original_filename', '%police%').limit(0).execute()
    police_count = response.count if hasattr(response, 'count') else 0
    print(f"🚔 Police Reports: {police_count}")
    print()

    # Document types
    response = client.table('legal_documents')\
        .select('document_type')\
        .execute()

    if response.data:
        from collections import Counter
        types = Counter(d.get('document_type') for d in response.data if d.get('document_type'))
        print("📋 Document Types:")
        for doc_type, count in types.most_common(10):
            print(f"  • {doc_type}: {count}")
    print()

    # Score ranges
    response = client.table('legal_documents')\
        .select('relevancy_number, legal_number')\
        .not_.is_('relevancy_number', 'null')\
        .execute()

    if response.data:
        relevancy_scores = [d.get('relevancy_number', 0) for d in response.data]
        legal_scores = [d.get('legal_number', 0) for d in response.data]

        print("⭐ Score Statistics:")
        print(f"  Relevancy: Avg {sum(relevancy_scores)/len(relevancy_scores):.0f}, Max {max(relevancy_scores)}, Min {min(relevancy_scores)}")
        print(f"  Legal: Avg {sum(legal_scores)/len(legal_scores):.0f}, Max {max(legal_scores)}, Min {min(legal_scores)}")
        print()

    # Critical documents
    response = client.table('legal_documents').select('*', count='exact')\
        .gte('relevancy_number', 900).limit(0).execute()
    critical_count = response.count if hasattr(response, 'count') else 0
    print(f"🔥 Critical Documents (REL ≥ 900): {critical_count}")
    print()

    print("=" * 80)
    print("💡 TOKEN SAVINGS: Queried database instead of reading 653+ files!")
    print("   Estimated: 2M tokens saved")
    print("=" * 80)

def query_police_reports(client, limit=10):
    """Query police reports - SAVES TOKENS"""
    print(f"🚔 POLICE REPORTS (Latest {limit})")
    print("=" * 80)

    response = client.table('legal_documents')\
        .select('original_filename, document_type, relevancy_number, legal_number, created_at, executive_summary')\
        .ilike('original_filename', '%police%')\
        .order('created_at', desc=True)\
        .limit(limit)\
        .execute()

    if not response.data:
        print("No police reports found")
        return

    for i, doc in enumerate(response.data, 1):
        print(f"\n{i}. {doc.get('original_filename', 'N/A')}")
        print(f"   Type: {doc.get('document_type', 'N/A')}")
        print(f"   Relevancy: {doc.get('relevancy_number', 'N/A')}, Legal: {doc.get('legal_number', 'N/A')}")
        print(f"   Date: {doc.get('created_at', 'N/A')[:10]}")
        if doc.get('executive_summary'):
            summary = doc.get('executive_summary')[:150]
            print(f"   Summary: {summary}...")

    print()
    print(f"💡 Queried DB instead of reading {len(response.data)} files - HUGE token savings!")

def query_recent(client, limit=10):
    """Query recent documents"""
    print(f"📅 RECENT DOCUMENTS (Latest {limit})")
    print("=" * 80)

    response = client.table('legal_documents')\
        .select('original_filename, document_type, relevancy_number, created_at')\
        .order('created_at', desc=True)\
        .limit(limit)\
        .execute()

    if not response.data:
        print("No documents found")
        return

    for i, doc in enumerate(response.data, 1):
        print(f"{i}. {doc.get('original_filename', 'N/A')} ({doc.get('document_type', 'N/A')})")
        print(f"   REL: {doc.get('relevancy_number', 'N/A')} | {doc.get('created_at', 'N/A')[:10]}")

    print()

def query_high_relevancy(client, min_score=900):
    """Query high relevancy documents"""
    print(f"🔥 HIGH RELEVANCY DOCUMENTS (≥{min_score})")
    print("=" * 80)

    response = client.table('legal_documents')\
        .select('original_filename, document_type, relevancy_number, legal_number, keywords, smoking_guns')\
        .gte('relevancy_number', min_score)\
        .order('relevancy_number', desc=True)\
        .execute()

    if not response.data:
        print(f"No documents with relevancy ≥ {min_score}")
        return

    for i, doc in enumerate(response.data, 1):
        print(f"\n{i}. {doc.get('original_filename', 'N/A')}")
        print(f"   REL: {doc.get('relevancy_number')}, LEG: {doc.get('legal_number')}")

        if doc.get('keywords'):
            print(f"   Keywords: {', '.join(doc.get('keywords')[:5])}")

        if doc.get('smoking_guns'):
            print(f"   🔥 Smoking Guns: {len(doc.get('smoking_guns'))} found")
            for sg in doc.get('smoking_guns')[:2]:
                print(f"      • {sg[:100]}...")

    print()
    print(f"💡 Found {len(response.data)} critical documents via query - no file reading needed!")

def search_documents(client, search_term):
    """Search documents by keyword"""
    print(f"🔍 SEARCH RESULTS: '{search_term}'")
    print("=" * 80)

    response = client.table('legal_documents')\
        .select('original_filename, document_type, relevancy_number, executive_summary')\
        .or_(f"original_filename.ilike.%{search_term}%,document_title.ilike.%{search_term}%,executive_summary.ilike.%{search_term}%")\
        .limit(20)\
        .execute()

    if not response.data:
        print(f"No documents found matching '{search_term}'")
        return

    print(f"Found {len(response.data)} documents:\n")

    for i, doc in enumerate(response.data, 1):
        print(f"{i}. {doc.get('original_filename', 'N/A')}")
        print(f"   Type: {doc.get('document_type', 'N/A')} | REL: {doc.get('relevancy_number', 'N/A')}")
        if doc.get('executive_summary'):
            summary = doc.get('executive_summary')[:100]
            print(f"   {summary}...")
        print()

    print(f"💡 Searched database - no file system scanning needed!")

def query_by_type(client, doc_type):
    """Query documents by type"""
    print(f"📋 DOCUMENTS OF TYPE: '{doc_type}'")
    print("=" * 80)

    response = client.table('legal_documents')\
        .select('original_filename, relevancy_number, legal_number, created_at')\
        .eq('document_type', doc_type)\
        .order('relevancy_number', desc=True)\
        .execute()

    if not response.data:
        print(f"No documents of type '{doc_type}' found")
        return

    print(f"Found {len(response.data)} documents:\n")

    for i, doc in enumerate(response.data, 1):
        print(f"{i}. {doc.get('original_filename', 'N/A')}")
        print(f"   REL: {doc.get('relevancy_number')}, LEG: {doc.get('legal_number')} | {doc.get('created_at', 'N/A')[:10]}")

    print()

def list_tables(client):
    """List all tables"""
    print("📊 DATABASE TABLES")
    print("=" * 80)

    # Known tables
    tables = [
        'legal_documents', 'document_pages', 'court_events', 'legal_violations',
        'file_metadata', 'truth_score_history', 'justice_score_rollups',
        'system_processing_cache', 'dashboard_snapshots', 'ai_analysis_results'
    ]

    print("Checking tables...\n")

    for table in tables:
        try:
            response = client.table(table).select('*', count='exact').limit(0).execute()
            count = response.count if hasattr(response, 'count') else 0
            status = "✅" if count > 0 else "⚪"
            print(f"  {status} {table}: {count} rows")
        except:
            print(f"  ❌ {table}: Not accessible or doesn't exist")

    print()

def get_stats(client):
    """Get comprehensive statistics"""
    print("📊 COMPREHENSIVE DATABASE STATISTICS")
    print("=" * 80)
    print()

    stats = {}

    # Documents
    response = client.table('legal_documents').select('*', count='exact').limit(0).execute()
    stats['documents'] = response.count if hasattr(response, 'count') else 0

    # Court events
    try:
        response = client.table('court_events').select('*', count='exact').limit(0).execute()
        stats['court_events'] = response.count if hasattr(response, 'count') else 0
    except:
        stats['court_events'] = 0

    # File metadata
    try:
        response = client.table('file_metadata').select('*', count='exact').limit(0).execute()
        stats['file_metadata'] = response.count if hasattr(response, 'count') else 0
    except:
        stats['file_metadata'] = 0

    print(f"📄 Legal Documents: {stats['documents']:,}")
    print(f"⚖️ Court Events: {stats['court_events']:,}")
    print(f"📁 File Metadata: {stats['file_metadata']:,}")
    print()

    # Total records
    total = sum(stats.values())
    print(f"🎯 Total Records: {total:,}")
    print()

    print("=" * 80)
    print("💡 All this info retrieved with minimal tokens via database queries!")
    print("=" * 80)

# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Query database instead of reading files - SAVES TOKENS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick summary
  python db_query.py --summary

  # Police reports
  python db_query.py --police-reports

  # High relevancy documents
  python db_query.py --high-relevancy

  # Search for keyword
  python db_query.py --search "August 2024"

  # Recent documents
  python db_query.py --recent 20

  # List tables
  python db_query.py --tables

  # Full stats
  python db_query.py --stats
        """
    )

    parser.add_argument('--summary', action='store_true', help='Database summary')
    parser.add_argument('--police-reports', action='store_true', help='List police reports')
    parser.add_argument('--recent', type=int, metavar='N', help='Recent N documents')
    parser.add_argument('--high-relevancy', action='store_true', help='High relevancy docs (900+)')
    parser.add_argument('--search', metavar='TERM', help='Search documents')
    parser.add_argument('--by-type', metavar='TYPE', help='Filter by document type')
    parser.add_argument('--tables', action='store_true', help='List all tables')
    parser.add_argument('--stats', action='store_true', help='Comprehensive statistics')

    args = parser.parse_args()

    # Get credentials
    url, key = get_credentials()

    if not key:
        print("❌ Missing SUPABASE_KEY")
        print("\nCreate .streamlit/secrets.toml with:")
        print('SUPABASE_URL = "https://jvjlhxodmbkodzmggwpu.supabase.co"')
        print('SUPABASE_KEY = "your-key-here"')
        sys.exit(1)

    try:
        client = create_client(url, key)

        # Execute query
        if args.summary:
            get_database_summary(client)
        elif args.police_reports:
            query_police_reports(client)
        elif args.recent:
            query_recent(client, args.recent)
        elif args.high_relevancy:
            query_high_relevancy(client)
        elif args.search:
            search_documents(client, args.search)
        elif args.by_type:
            query_by_type(client, args.by_type)
        elif args.tables:
            list_tables(client)
        elif args.stats:
            get_stats(client)
        else:
            # Default: show summary
            get_database_summary(client)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
