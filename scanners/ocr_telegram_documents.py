#!/usr/bin/env python3
"""
OCR and Violation Analysis for Telegram Documents
Uses pytesseract for OCR and Claude for violation analysis
"""
import os
import sys
from pathlib import Path
from supabase import create_client
from PIL import Image
import pytesseract
import anthropic
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Bug Tracker
from core.bug_tracker import BugTracker

# Initialize bug tracker
bug_tracker = BugTracker()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

if not all([SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_API_KEY]):
    print("Missing credentials")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

print("="*80)
print("📄 OCR AND VIOLATION ANALYSIS")
print("="*80)

# Get documents uploaded today from Telegram
result = supabase.table('legal_documents')\
    .select('*')\
    .eq('document_date', '2024-08-13')\
    .eq('status', 'RECEIVED')\
    .execute()

documents = result.data
print(f"\nFound {len(documents)} documents to process")
bug_tracker.log('info', f'Starting OCR analysis on {len(documents)} documents',
               'ocr_analyzer', workspace_id='legal')

total_cost = 0.0

for i, doc in enumerate(documents, 1):
    doc_id = doc['id']
    filename = doc['original_filename']
    file_path = doc['file_path']

    print(f"\n{'='*80}")
    print(f"[{i}/{len(documents)}] {filename}")
    print(f"{'='*80}")

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        bug_tracker.log('error', f'File not found: {file_path}', 'ocr_analyzer',
                       details={'doc_id': doc_id, 'filename': filename},
                       workspace_id='legal')
        continue

    # Step 1: OCR
    print("🔍 Running OCR...")
    try:
        image = Image.open(file_path)
        ocr_text = pytesseract.image_to_string(image)
        text_length = len(ocr_text)
        print(f"✅ Extracted {text_length} characters")

        if text_length < 100:
            print("⚠️  Very short text, may be low quality scan")
    except Exception as e:
        print(f"❌ OCR Error: {e}")
        bug_tracker.log('critical', f'OCR failed for {filename}', 'ocr_analyzer',
                       error=e, details={'doc_id': doc_id, 'filename': filename},
                       workspace_id='legal')
        continue

    # Step 2: Analyze for violations
    print("🤖 Analyzing for violations with Claude...")

    system_prompt = """You are a legal violation analyst reviewing court documents for August 13, 2024 ex parte proceedings. Analyze for:

1. Constitutional violations (4th/5th/14th Amendment, due process, unlawful seizure)
2. Perjury indicators (false statements, contradictions, misrepresentations under oath)
3. Fraud indicators (falsification, forgery, fraudulent statements, coercion)
4. Procedural violations (improper ex parte, lack of notice, denial of rights)

Return ONLY valid JSON:
{
  "document_type": "DECL|ORDR|MOTN|OTHER",
  "document_title": "Brief descriptive title",
  "constitutional_violations": ["Specific violation with page/quote reference"],
  "perjury_indicators": ["False statement with evidence"],
  "fraud_indicators": ["Fraudulent activity with evidence"],
  "procedural_violations": ["Procedural error with citation"],
  "key_quotes": ["Important verbatim quotes"],
  "summary": "Executive summary of document and violations",
  "severity": "CRITICAL|HIGH|MEDIUM|LOW"
}"""

    try:
        # Limit text to 15K chars for cost
        analysis_text = ocr_text[:15000] if len(ocr_text) > 15000 else ocr_text

        message = anthropic_client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=2000,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": f"Analyze this August 13, 2024 ex parte document for violations:\n\n{analysis_text}"
            }]
        )

        # Calculate cost
        input_tokens = message.usage.input_tokens
        output_tokens = message.usage.output_tokens
        cost = (input_tokens * 0.003 / 1000) + (output_tokens * 0.015 / 1000)
        total_cost += cost

        print(f"💰 Cost: ${cost:.4f} | Tokens: {input_tokens}+{output_tokens}")

        # Parse response
        response_text = message.content[0].text
        import json
        import re

        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            analysis = json.loads(json_match.group(0))
        else:
            print("⚠️  Could not parse JSON, using defaults")
            analysis = {}

        # Display findings
        const_v = analysis.get('constitutional_violations', [])
        perjury = analysis.get('perjury_indicators', [])
        fraud = analysis.get('fraud_indicators', [])
        proc_v = analysis.get('procedural_violations', [])

        print(f"\n📊 VIOLATIONS FOUND:")
        print(f"   🏛️  Constitutional: {len(const_v)}")
        print(f"   ⚖️  Perjury: {len(perjury)}")
        print(f"   🚨 Fraud: {len(fraud)}")
        print(f"   📋 Procedural: {len(proc_v)}")
        print(f"   ⚠️  Severity: {analysis.get('severity', 'UNKNOWN')}")

        # Step 3: Update database
        print("💾 Updating database...")

        update_data = {
            'full_text': ocr_text,
            'document_type': analysis.get('document_type', 'DECL'),
            'document_title': analysis.get('document_title', f'Ex Parte Document - {filename[:30]}'),
            'executive_summary': analysis.get('summary', 'Ex parte document analysis'),
            'constitutional_violations': const_v,
            'perjury_indicators': perjury,
            'fraud_indicators': fraud,
            'key_quotes': analysis.get('key_quotes', []),
            'status': 'ANALYZED',
            'importance': analysis.get('severity', 'HIGH'),
            'api_cost_usd': cost
        }

        supabase.table('legal_documents').update(update_data).eq('id', doc_id).execute()
        print(f"✅ Updated document {doc_id}")
        bug_tracker.log('info', f'Successfully analyzed {filename}', 'ocr_analyzer',
                       details={'doc_id': doc_id, 'violations': len(const_v) + len(perjury) + len(fraud) + len(proc_v)},
                       workspace_id='legal')

    except Exception as e:
        print(f"❌ Analysis Error: {e}")
        bug_tracker.log('critical', f'Analysis failed for {filename}', 'ocr_analyzer',
                       error=e, details={'doc_id': doc_id, 'filename': filename},
                       workspace_id='legal')
        continue

print(f"\n{'='*80}")
print(f"🎉 ANALYSIS COMPLETE")
print(f"{'='*80}")
print(f"✅ Processed: {len(documents)} documents")
print(f"💰 Total cost: ${total_cost:.2f}")
print(f"📊 View in dashboard: http://137.184.1.91:8501")

bug_tracker.log('info', f'OCR analysis completed - {len(documents)} documents processed',
               'ocr_analyzer', details={'total_cost': total_cost},
               workspace_id='legal')
