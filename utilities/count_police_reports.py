#!/usr/bin/env python3
"""
Quick script to count police reports in the database
"""

import os
import sys
from pathlib import Path
from supabase import create_client

# Try to load credentials from multiple sources
SUPABASE_URL = None
SUPABASE_KEY = None

# Method 1: Try environment variables first
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

# Method 2: Try Streamlit secrets if available
if not SUPABASE_URL or not SUPABASE_KEY:
    try:
        import streamlit as st
        SUPABASE_URL = st.secrets.get('SUPABASE_URL')
        SUPABASE_KEY = st.secrets.get('SUPABASE_KEY')
    except:
        pass

# Method 3: Try loading from .streamlit/secrets.toml directly
if not SUPABASE_URL or not SUPABASE_KEY:
    try:
        import toml
        secrets_path = Path(__file__).parent / '.streamlit' / 'secrets.toml'
        if secrets_path.exists():
            secrets = toml.load(secrets_path)
            SUPABASE_URL = secrets.get('SUPABASE_URL')
            SUPABASE_KEY = secrets.get('SUPABASE_KEY')
    except:
        pass

# Fallback to default URL (you still need to provide the key)
if not SUPABASE_URL:
    SUPABASE_URL = 'https://jvjlhxodmbkodzmggwpu.supabase.co'

def count_police_reports():
    """Count police reports in the database"""
    try:
        # Create Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        print("=" * 60)
        print("POLICE REPORTS COUNT")
        print("=" * 60)
        print()

        # Query 1: Search for files with "police" in the filename
        police_response = supabase.table('legal_documents')\
            .select('*', count='exact')\
            .ilike('original_filename', '%police%')\
            .execute()

        police_count = police_response.count if hasattr(police_response, 'count') else len(police_response.data)

        print(f"📊 Total documents with 'police' in filename: {police_count}")
        print()

        if police_response.data:
            print("Documents found:")
            print("-" * 60)
            for doc in police_response.data:
                filename = doc.get('original_filename', 'N/A')
                doc_type = doc.get('document_type', 'N/A')
                relevancy = doc.get('relevancy_number', 'N/A')
                created = doc.get('created_at', 'N/A')

                print(f"  • {filename}")
                print(f"    Type: {doc_type}")
                print(f"    Relevancy Score: {relevancy}")
                print(f"    Created: {created}")
                print()
        else:
            print("  No police reports found in the database.")
            print()

        # Query 2: Also check for "report" with "police" nearby
        print("-" * 60)
        print("Additional check: Documents with 'report' in filename:")
        print("-" * 60)

        report_response = supabase.table('legal_documents')\
            .select('original_filename', count='exact')\
            .ilike('original_filename', '%report%')\
            .execute()

        report_count = report_response.count if hasattr(report_response, 'count') else len(report_response.data)
        print(f"Total documents with 'report' in filename: {report_count}")
        print()

        # Show a few examples
        if report_response.data:
            print("Sample report documents:")
            for i, doc in enumerate(report_response.data[:10], 1):
                print(f"  {i}. {doc.get('original_filename', 'N/A')}")

            if len(report_response.data) > 10:
                print(f"  ... and {len(report_response.data) - 10} more")

        print()
        print("=" * 60)

        # Summary
        print("SUMMARY:")
        print(f"  Police reports: {police_count}")
        print(f"  Documents with 'report': {report_count}")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Error querying database: {e}")
        print()
        print("Make sure your Supabase credentials are set correctly.")
        print("You can set them with:")
        print("  export SUPABASE_URL='your-url'")
        print("  export SUPABASE_KEY='your-key'")

if __name__ == "__main__":
    count_police_reports()
