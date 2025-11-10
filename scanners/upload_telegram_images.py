#!/usr/bin/env python3
"""
Upload existing Telegram images to database
"""
import os
import sys
from pathlib import Path
from supabase import create_client

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Missing credentials")
    sys.exit(1)

client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Get all images from telegram-inbox
inbox_dir = Path('/root/phase0_bug_tracker/data/telegram-inbox/2025-11-10')
images = sorted(inbox_dir.glob('*.jpg'))

print(f"Found {len(images)} images to upload")
print("="*80)

uploaded = 0
for img_path in images:
    filename = img_path.name

    doc_data = {
        'case_id': 'ashe-bucknor-j24-00478',
        'original_filename': filename,
        'file_path': str(img_path),
        'document_type': 'DECL',  # These are declaration/court documents
        'document_date': '2024-08-13',  # August 13 ex parte documents
        'document_title': f'Ex Parte Document - {filename[:30]}',
        'executive_summary': 'August 13, 2024 ex parte proceeding document uploaded via Telegram',
        'status': 'RECEIVED',
        'purpose': 'EVIDENCE',
        'relevancy_number': 850,  # High relevancy for ex parte
        'legal_number': 850,
        'macro_number': 850,
        'micro_number': 800,
    }

    try:
        response = client.table('legal_documents').insert(doc_data).execute()
        doc_id = response.data[0]['id'] if response.data else None
        print(f"✅ {filename[:40]:40} → ID: {doc_id}")
        uploaded += 1
    except Exception as e:
        print(f"❌ {filename[:40]:40} → Error: {e}")

print("="*80)
print(f"✅ Uploaded {uploaded}/{len(images)} images to database")
print(f"📊 View in dashboard: http://137.184.1.91:8501")
