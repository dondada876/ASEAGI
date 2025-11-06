#!/usr/bin/env python3
"""
Check police reports in database with better credential handling
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import from main directory
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from supabase import create_client
except ImportError:
    print("❌ Install supabase: pip install supabase")
    sys.exit(1)

def get_credentials():
    """Try multiple methods to get credentials"""
    url = None
    key = None

    # Method 1: Environment variables
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')

    if url and key:
        print(f"✅ Found credentials in environment variables")
        return url, key

    # Method 2: Streamlit secrets
    try:
        import streamlit as st
        url = st.secrets.get('SUPABASE_URL')
        key = st.secrets.get('SUPABASE_KEY')
        if url and key:
            print(f"✅ Found credentials in Streamlit secrets")
            return url, key
    except:
        pass

    # Method 3: Load from .streamlit/secrets.toml
    try:
        import toml
        secrets_path = Path(__file__).parent.parent / '.streamlit' / 'secrets.toml'
        if secrets_path.exists():
            secrets = toml.load(secrets_path)
            url = secrets.get('SUPABASE_URL')
            key = secrets.get('SUPABASE_KEY')
            if url and key:
                print(f"✅ Found credentials in {secrets_path}")
                return url, key
    except Exception as e:
        print(f"⚠️  Could not load from secrets.toml: {e}")

    # Default URL
    url = 'https://jvjlhxodmbkodzmggwpu.supabase.co'

    print(f"❌ No valid credentials found")
    print(f"Using URL: {url}")
    print(f"Key: Not found")

    return url, None

def main():
    print("=" * 70)
    print("POLICE REPORTS DATABASE CHECK")
    print("=" * 70)
    print()

    url, key = get_credentials()

    if not key:
        print("\n❌ Missing SUPABASE_KEY")
        print("\nTo fix this, create .streamlit/secrets.toml with:")
        print("""
SUPABASE_URL = "https://jvjlhxodmbkodzmggwpu.supabase.co"
SUPABASE_KEY = "your-actual-anon-key-here"
        """)
        return

    try:
        # Create client
        print(f"🔌 Connecting to: {url[:50]}...")
        supabase = create_client(url, key)

        # Test connection
        print("🔍 Testing connection...")
        test = supabase.table('legal_documents').select('id', count='exact').limit(1).execute()
        print(f"✅ Connected successfully!")
        print()

        # Query police reports
        print("📊 QUERYING POLICE REPORTS")
        print("-" * 70)

        # Query 1: Documents with "police" in filename
        police_response = supabase.table('legal_documents')\
            .select('*', count='exact')\
            .ilike('original_filename', '%police%')\
            .execute()

        police_count = police_response.count if hasattr(police_response, 'count') else len(police_response.data)

        print(f"\n🚔 Documents with 'police' in filename: {police_count}")

        if police_response.data:
            print("\n📄 Police Reports Found:")
            print("-" * 70)
            for i, doc in enumerate(police_response.data, 1):
                filename = doc.get('original_filename', 'N/A')
                doc_type = doc.get('document_type', 'N/A')
                relevancy = doc.get('relevancy_number', 'N/A')
                status = doc.get('processing_status', 'N/A')
                created = doc.get('created_at', 'N/A')[:10] if doc.get('created_at') else 'N/A'

                print(f"\n  {i}. {filename}")
                print(f"     Type: {doc_type} | Relevancy: {relevancy} | Status: {status}")
                print(f"     Created: {created}")

                if doc.get('document_title'):
                    print(f"     Title: {doc.get('document_title')}")

                if doc.get('executive_summary'):
                    summary = doc.get('executive_summary')[:150]
                    print(f"     Summary: {summary}...")
        else:
            print("\n⚠️  No documents with 'police' in filename found")

        print("\n" + "-" * 70)

        # Query 2: All reports
        report_response = supabase.table('legal_documents')\
            .select('original_filename', count='exact')\
            .ilike('original_filename', '%report%')\
            .execute()

        report_count = report_response.count if hasattr(report_response, 'count') else len(report_response.data)

        print(f"\n📋 Documents with 'report' in filename: {report_count}")

        if report_response.data:
            print(f"\n   Showing first 10 of {report_count}:")
            for i, doc in enumerate(report_response.data[:10], 1):
                print(f"   {i}. {doc.get('original_filename', 'N/A')}")

            if report_count > 10:
                print(f"   ... and {report_count - 10} more")

        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"  🚔 Police reports: {police_count}")
        print(f"  📋 All reports: {report_count}")
        print(f"  📊 Total documents in DB: {test.count if hasattr(test, 'count') else 'Unknown'}")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"\nFull error details: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
