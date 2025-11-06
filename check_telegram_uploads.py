#!/usr/bin/env python3
"""
Check for recent Telegram uploads in Supabase
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

from supabase import create_client
import toml
from pathlib import Path
from datetime import datetime, timedelta

# Load credentials
secrets_path = Path(__file__).parent / '.streamlit' / 'secrets.toml'
secrets = toml.load(secrets_path)
supabase = create_client(secrets['SUPABASE_URL'], secrets['SUPABASE_KEY'])

print("=" * 60)
print("TELEGRAM DOCUMENT UPLOADS - VERIFICATION")
print("=" * 60)

# Get documents from the last hour
one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()

result = supabase.table('legal_documents').select('*').gte('created_at', one_hour_ago).order('created_at', desc=True).execute()

if result.data:
    print(f"\nFound {len(result.data)} document(s) uploaded in the last hour:\n")

    for i, doc in enumerate(result.data, 1):
        print(f"{i}. {doc.get('original_filename', 'Untitled')}")
        print(f"   Type: {doc.get('document_type', 'N/A')}")
        print(f"   Date: {doc.get('document_date', 'N/A')}")
        print(f"   Uploaded: {doc.get('created_at', 'N/A')}")
        print(f"   Source: {doc.get('source', 'N/A')}")
        print(f"   Relevancy: {doc.get('relevancy', 'N/A')}")
        if doc.get('notes'):
            print(f"   Notes: {doc.get('notes')[:100]}...")
        print()
else:
    print("\nNo documents uploaded in the last hour")

# Show total count
count = supabase.table('legal_documents').select('id', count='exact').execute()
print(f"Total documents in database: {count.count}")

print("\n" + "=" * 60)
print("HOW TO VERIFY YOUR TELEGRAM BOT:")
print("=" * 60)
print("\n1. In Telegram, send /start to your bot")
print("2. Upload an image or document")
print("3. Follow the conversation prompts")
print("4. After confirming upload, run this script again:")
print("   python check_telegram_uploads.py")
print("\n5. OR check your dashboards:")
print("   - Master Dashboard: http://localhost:8501")
print("   - Timeline: http://localhost:8504")
print()
