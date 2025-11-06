#!/usr/bin/env python3
"""
ASEAGI Mobile Document Ingestion System
Complete workflow: Mobile → AI Analysis → Smart Filename → Database → Source of Truth

This module provides utilities for:
1. Generating smart filenames with embedded scores
2. Processing mobile-uploaded documents
3. Ingesting into database as source of truth
4. Query/reference system to save context windows

Usage:
  from mobile_document_ingestion import process_mobile_document, generate_smart_filename
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import hashlib
import json
from typing import Dict, Optional, Tuple

try:
    from supabase import create_client
except ImportError:
    print("❌ Install supabase: pip install supabase")
    sys.exit(1)

# ============================================================================
# CONFIGURATION
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
            secrets_path = Path(__file__).parent.parent / '.streamlit' / 'secrets.toml'
            if secrets_path.exists():
                secrets = toml.load(secrets_path)
                url = secrets.get('SUPABASE_URL')
                key = secrets.get('SUPABASE_KEY')
        except:
            pass

    return url, key

# ============================================================================
# SMART FILENAME GENERATION
# ============================================================================

def generate_smart_filename(
    original_filename: str,
    document_type: str,
    date: str,
    relevancy: int,
    legal: int,
    micro: int,
    macro: int,
    title: Optional[str] = None,
    include_timestamp: bool = True
) -> str:
    """
    Generate intelligent filename with embedded scoring

    Format: {DocType}_{Title}_{Date}_REL{score}_LEG{score}_MIC{score}_MAC{score}_{timestamp}.{ext}

    Example:
      PoliceReport_AugustIncident_20240810_REL950_LEG920_MIC880_MAC910_1730849234.pdf

    Args:
        original_filename: Original file name
        document_type: Type of document (PoliceReport, CourtFiling, etc.)
        date: Document date (YYYYMMDD or YYYY-MM-DD)
        relevancy: Relevancy score (0-999)
        legal: Legal score (0-999)
        micro: Micro score (0-999)
        macro: Macro score (0-999)
        title: Optional short title (sanitized)
        include_timestamp: Include unix timestamp for uniqueness

    Returns:
        Smart filename string
    """
    # Get file extension
    ext = Path(original_filename).suffix or '.pdf'

    # Sanitize document type
    doc_type = ''.join(c for c in document_type if c.isalnum())
    if not doc_type:
        doc_type = 'Document'

    # Sanitize title
    if title:
        # Remove special characters, limit length
        title_clean = ''.join(c for c in title if c.isalnum() or c in [' ', '-', '_'])
        title_clean = title_clean.replace(' ', '')[:30]
        title_part = f"_{title_clean}" if title_clean else ""
    else:
        title_part = ""

    # Format date
    date_clean = date.replace('-', '').replace('/', '')[:8]

    # Build scores part
    scores = f"REL{relevancy:03d}_LEG{legal:03d}_MIC{micro:03d}_MAC{macro:03d}"

    # Add timestamp for uniqueness
    timestamp_part = f"_{int(datetime.now().timestamp())}" if include_timestamp else ""

    # Construct filename
    filename = f"{doc_type}{title_part}_{date_clean}_{scores}{timestamp_part}{ext}"

    return filename

def parse_smart_filename(filename: str) -> Dict:
    """
    Parse a smart filename to extract embedded metadata

    Args:
        filename: Smart filename to parse

    Returns:
        Dict with extracted metadata
    """
    parts = Path(filename).stem.split('_')

    metadata = {
        'original_filename': filename,
        'document_type': None,
        'title': None,
        'date': None,
        'relevancy': None,
        'legal': None,
        'micro': None,
        'macro': None,
        'timestamp': None,
    }

    for part in parts:
        if part.startswith('REL') and len(part) >= 6:
            try:
                metadata['relevancy'] = int(part[3:6])
            except:
                pass
        elif part.startswith('LEG') and len(part) >= 6:
            try:
                metadata['legal'] = int(part[3:6])
            except:
                pass
        elif part.startswith('MIC') and len(part) >= 6:
            try:
                metadata['micro'] = int(part[3:6])
            except:
                pass
        elif part.startswith('MAC') and len(part) >= 6:
            try:
                metadata['macro'] = int(part[3:6])
            except:
                pass
        elif part.isdigit() and len(part) == 8:
            # Likely a date YYYYMMDD
            metadata['date'] = part
        elif part.isdigit() and len(part) == 10:
            # Likely a unix timestamp
            metadata['timestamp'] = int(part)

    # First part is usually document type
    if parts:
        metadata['document_type'] = parts[0]

    return metadata

# ============================================================================
# DOCUMENT PROCESSING
# ============================================================================

def process_mobile_document(
    image_path: str,
    ai_analysis: Dict,
    save_to_db: bool = True,
    return_smart_filename: bool = True
) -> Dict:
    """
    Process a document from mobile upload

    Workflow:
    1. Receive image and AI analysis results
    2. Generate smart filename with embedded scores
    3. Save to database as source of truth
    4. Return filename for user to organize/archive

    Args:
        image_path: Path to uploaded image
        ai_analysis: Dict with AI analysis results containing:
            - document_type
            - date
            - title
            - relevancy
            - legal_score
            - micro_score
            - macro_score
            - executive_summary
            - keywords
            - smoking_guns
        save_to_db: Whether to save to database
        return_smart_filename: Whether to generate smart filename

    Returns:
        Dict with:
            - smart_filename
            - database_id (if saved)
            - status
            - message
    """

    result = {
        'status': 'success',
        'smart_filename': None,
        'database_id': None,
        'message': None,
        'errors': []
    }

    try:
        # Extract metadata from AI analysis
        original_filename = Path(image_path).name
        document_type = ai_analysis.get('document_type', 'Document')
        date = ai_analysis.get('date', datetime.now().strftime('%Y%m%d'))
        title = ai_analysis.get('title')

        # Scores
        relevancy = ai_analysis.get('relevancy', 500)
        legal = ai_analysis.get('legal_score', 500)
        micro = ai_analysis.get('micro_score', 500)
        macro = ai_analysis.get('macro_score', 500)

        # Generate smart filename
        if return_smart_filename:
            smart_filename = generate_smart_filename(
                original_filename=original_filename,
                document_type=document_type,
                date=date,
                relevancy=relevancy,
                legal=legal,
                micro=micro,
                macro=macro,
                title=title,
                include_timestamp=True
            )
            result['smart_filename'] = smart_filename
        else:
            smart_filename = original_filename

        # Save to database
        if save_to_db:
            url, key = get_credentials()

            if not url or not key:
                result['errors'].append("Missing Supabase credentials")
                result['status'] = 'partial'
            else:
                try:
                    client = create_client(url, key)

                    # Prepare document record
                    document_record = {
                        'original_filename': original_filename,
                        'renamed_filename': smart_filename,
                        'document_type': document_type,
                        'document_date': date,
                        'document_title': title or 'Untitled',
                        'relevancy_number': relevancy,
                        'legal_number': legal,
                        'micro_number': micro,
                        'macro_number': macro,
                        'executive_summary': ai_analysis.get('executive_summary'),
                        'keywords': ai_analysis.get('keywords', []),
                        'smoking_guns': ai_analysis.get('smoking_guns', []),
                        'processing_status': 'completed',
                        'source': 'mobile_upload',
                        'file_path': image_path,
                        'created_at': datetime.now().isoformat(),
                    }

                    # Insert into database
                    response = client.table('legal_documents').insert(document_record).execute()

                    if response.data:
                        result['database_id'] = response.data[0].get('id')
                        result['message'] = f"✅ Saved to database with ID: {result['database_id']}"
                    else:
                        result['errors'].append("Database insert returned no data")
                        result['status'] = 'partial'

                except Exception as e:
                    result['errors'].append(f"Database error: {str(e)}")
                    result['status'] = 'partial'

        # Generate user message
        if result['status'] == 'success' and not result['message']:
            result['message'] = f"✅ Generated smart filename: {smart_filename}"

    except Exception as e:
        result['status'] = 'error'
        result['errors'].append(f"Processing error: {str(e)}")

    return result

# ============================================================================
# SOURCE OF TRUTH QUERY SYSTEM
# ============================================================================

def query_source_of_truth(
    query_type: str,
    **filters
) -> list:
    """
    Query the source of truth database instead of reprocessing

    This saves context windows and tokens by referencing existing processed data

    Args:
        query_type: Type of query (by_date, by_type, by_score, by_keyword, recent)
        **filters: Additional filters based on query type

    Returns:
        List of matching documents
    """
    url, key = get_credentials()

    if not url or not key:
        print("❌ Missing Supabase credentials")
        return []

    try:
        client = create_client(url, key)

        # Build query based on type
        query = client.table('legal_documents').select('*')

        if query_type == 'by_date':
            date_from = filters.get('date_from')
            date_to = filters.get('date_to')
            if date_from:
                query = query.gte('document_date', date_from)
            if date_to:
                query = query.lte('document_date', date_to)

        elif query_type == 'by_type':
            doc_type = filters.get('document_type')
            if doc_type:
                query = query.eq('document_type', doc_type)

        elif query_type == 'by_score':
            min_relevancy = filters.get('min_relevancy', 0)
            query = query.gte('relevancy_number', min_relevancy)

        elif query_type == 'by_keyword':
            keyword = filters.get('keyword')
            if keyword:
                query = query.ilike('keywords', f'%{keyword}%')

        elif query_type == 'recent':
            limit = filters.get('limit', 10)
            query = query.order('created_at', desc=True).limit(limit)

        # Execute query
        response = query.execute()
        return response.data if response.data else []

    except Exception as e:
        print(f"❌ Query error: {e}")
        return []

def get_document_by_filename(filename: str) -> Optional[Dict]:
    """
    Retrieve document from source of truth by filename

    Args:
        filename: Original or renamed filename

    Returns:
        Document record or None
    """
    url, key = get_credentials()

    if not url or not key:
        return None

    try:
        client = create_client(url, key)

        # Try original filename first
        response = client.table('legal_documents')\
            .select('*')\
            .eq('original_filename', filename)\
            .execute()

        if response.data:
            return response.data[0]

        # Try renamed filename
        response = client.table('legal_documents')\
            .select('*')\
            .eq('renamed_filename', filename)\
            .execute()

        if response.data:
            return response.data[0]

        return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# ============================================================================
# MOBILE BOT INTEGRATION HELPERS
# ============================================================================

def format_mobile_response(
    smart_filename: str,
    document_type: str,
    relevancy: int,
    legal: int,
    micro: int,
    macro: int,
    title: str,
    summary: str,
    next_steps: str = None
) -> str:
    """
    Format a nice response for mobile bot

    Returns:
        Formatted message string
    """

    # Relevancy emoji
    if relevancy >= 900:
        rel_emoji = '🔴'
    elif relevancy >= 800:
        rel_emoji = '🟠'
    elif relevancy >= 700:
        rel_emoji = '🟡'
    else:
        rel_emoji = '⚪'

    message = f"""
✅ **Document Processed Successfully!**

📄 **{title}**
📝 Type: {document_type}

**Scores:**
{rel_emoji} Relevancy: {relevancy}/999
⚖️ Legal: {legal}/999
🔬 Micro: {micro}/999
🌐 Macro: {macro}/999

📋 **Summary:**
{summary[:200]}{'...' if len(summary) > 200 else ''}

💾 **Smart Filename:**
`{smart_filename}`

**Next Steps:**
{next_steps or '''1. Save image with this filename
2. Move to appropriate folder
3. Upload to Google Drive for archival
4. System has recorded in database'''}

✨ Source of truth updated! Can reference instead of reprocessing.
"""

    return message.strip()

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    """CLI for testing"""
    import argparse

    parser = argparse.ArgumentParser(description='ASEAGI Mobile Document Ingestion')
    parser.add_argument('command', choices=['generate', 'parse', 'process', 'query'])
    parser.add_argument('--image', help='Path to image file')
    parser.add_argument('--type', help='Document type')
    parser.add_argument('--date', help='Document date (YYYYMMDD)')
    parser.add_argument('--title', help='Document title')
    parser.add_argument('--rel', type=int, default=500, help='Relevancy score')
    parser.add_argument('--leg', type=int, default=500, help='Legal score')
    parser.add_argument('--mic', type=int, default=500, help='Micro score')
    parser.add_argument('--mac', type=int, default=500, help='Macro score')
    parser.add_argument('--filename', help='Filename to parse or query')

    args = parser.parse_args()

    if args.command == 'generate':
        filename = generate_smart_filename(
            original_filename=args.image or 'document.pdf',
            document_type=args.type or 'Document',
            date=args.date or datetime.now().strftime('%Y%m%d'),
            relevancy=args.rel,
            legal=args.leg,
            micro=args.mic,
            macro=args.mac,
            title=args.title
        )
        print(f"Smart Filename: {filename}")

    elif args.command == 'parse':
        if not args.filename:
            print("❌ --filename required")
            return
        metadata = parse_smart_filename(args.filename)
        print(json.dumps(metadata, indent=2))

    elif args.command == 'query':
        if args.filename:
            doc = get_document_by_filename(args.filename)
            if doc:
                print(json.dumps(doc, indent=2))
            else:
                print("❌ Document not found")
        else:
            docs = query_source_of_truth('recent', limit=5)
            print(f"Found {len(docs)} recent documents:")
            for doc in docs:
                print(f"  - {doc.get('renamed_filename', doc.get('original_filename'))}")

if __name__ == "__main__":
    main()
