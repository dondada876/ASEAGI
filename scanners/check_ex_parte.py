#!/usr/bin/env python3
"""
Check for August 13, 2024 Ex Parte Document
"""
import os
from supabase import create_client

def safe_len(val):
    """Safely get length of value that might be None"""
    if val is None:
        return 0
    return len(val)

def main():
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Search for August 13, 2024 documents
    response = client.table('legal_documents').select('*').or_(
        'document_date.eq.2024-08-13,'
        'original_filename.ilike.%2024-08-13%,'
        'original_filename.ilike.%08-13-2024%,'
        'document_title.ilike.%august 13%,'
        'document_title.ilike.%ex parte%'
    ).execute()

    print(f'\n📄 Found {len(response.data)} documents matching search')
    print('='*80)

    ex_parte_docs = []

    for doc in response.data:
        title = (doc.get('document_title') or '').lower()
        filename = (doc.get('original_filename') or '').lower()

        # Look for ex parte documents
        is_ex_parte = 'ex parte' in title or 'exparte' in title or 'ex_parte' in filename

        print(f'\nID: {doc["id"]}')
        print(f'Filename: {doc.get("original_filename", "N/A")}')
        print(f'Title: {doc.get("document_title", "N/A")}')
        print(f'Date: {doc.get("document_date", "N/A")}')
        print(f'Type: {doc.get("document_type", "N/A")}')
        print(f'Status: {doc.get("status", "N/A")}')

        if is_ex_parte:
            print('🔍 *** EX PARTE DOCUMENT ***')
            ex_parte_docs.append(doc)

        summary = doc.get('executive_summary') or 'N/A'
        if len(str(summary)) > 200:
            summary = str(summary)[:200] + '...'
        print(f'Summary: {summary}')

        # Safely check violations
        const_v = doc.get('constitutional_violations') or []
        perjury = doc.get('perjury_indicators') or []
        fraud = doc.get('fraud_indicators') or []

        print(f'Violations: Constitutional={safe_len(const_v)}, Perjury={safe_len(perjury)}, Fraud={safe_len(fraud)}')

        # Check for declaration page
        if doc.get('declaration_page'):
            print(f'✅ Declaration Page: {doc["declaration_page"]}')

        full_text = doc.get('full_text') or ''
        print(f'Full Text: {safe_len(full_text)} chars')

        # Check file path
        file_path = doc.get('file_path')
        if file_path and os.path.exists(file_path):
            print(f'✅ File exists: {file_path}')
        elif file_path:
            print(f'⚠️  File not found: {file_path}')

        print('-'*80)

    print(f'\n\n🔍 EX PARTE DOCUMENTS FOUND: {len(ex_parte_docs)}')
    if ex_parte_docs:
        print('\n' + '='*80)
        print('EX PARTE DOCUMENT DETAILS')
        print('='*80)
        for doc in ex_parte_docs:
            print(f'\nID: {doc["id"]}')
            print(f'Title: {doc.get("document_title")}')
            print(f'Filename: {doc.get("original_filename")}')
            print(f'Date: {doc.get("document_date")}')
            print(f'Type: {doc.get("document_type")}')
            print(f'File Path: {doc.get("file_path")}')

            # Show full summary
            summary = doc.get('executive_summary') or 'No summary'
            print(f'\nExecutive Summary:\n{summary}')

            # Show violations in detail
            const_v = doc.get('constitutional_violations') or []
            perjury = doc.get('perjury_indicators') or []
            fraud = doc.get('fraud_indicators') or []

            if const_v:
                print(f'\n🏛️  Constitutional Violations ({len(const_v)}):')
                for v in const_v:
                    print(f'   - {v}')

            if perjury:
                print(f'\n⚖️  Perjury Indicators ({len(perjury)}):')
                for p in perjury:
                    print(f'   - {p}')

            if fraud:
                print(f'\n🚨 Fraud Indicators ({len(fraud)}):')
                for f in fraud:
                    print(f'   - {f}')

            print('\n' + '-'*80)
    else:
        print('\n⚠️  No ex parte documents found for August 13, 2024')

if __name__ == '__main__':
    main()
