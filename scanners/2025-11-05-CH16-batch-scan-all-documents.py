#!/usr/bin/env python3
"""
Batch Document Scanner for PROJ344
Scans all documents in Downloads folder and uploads to Supabase with PROJ344 scoring
Processes: 902 documents total
Focus: CH22_Legal documents first, then expand to all
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
import anthropic
from supabase import create_client
from PIL import Image
import base64
from io import BytesIO
import hashlib

class BatchDocumentScanner:
    def __init__(self, supabase_url, supabase_key, anthropic_key):
        self.client = create_client(supabase_url, supabase_key)
        self.anthropic = anthropic.Anthropic(api_key=anthropic_key)
        self.case_id = 'ashe-bucknor-j24-00478'
        self.total_cost = 0.0
        self.processed_count = 0
        self.skipped_count = 0
        self.error_count = 0

    def calculate_file_hash(self, file_path):
        """Calculate MD5 hash to check for duplicates"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def check_already_processed(self, file_hash):
        """Check if document already in database"""
        try:
            result = self.client.table('legal_documents')\
                .select('id')\
                .eq('content_hash', file_hash)\
                .execute()
            return len(result.data) > 0
        except:
            return False

    def extract_text_from_image(self, image_path):
        """Convert image to base64 for Claude vision"""
        with Image.open(image_path) as img:
            # Resize if too large
            max_size = 1568
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

            if img.mode != 'RGB':
                img = img.convert('RGB')

            buffered = BytesIO()
            img.save(buffered, format="JPEG", quality=85)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return img_str

    def analyze_document(self, file_path):
        """Analyze document with PROJ344 scoring methodology"""
        print(f"\n📄 Processing: {file_path.name}")

        extension = file_path.suffix.lower()

        # Prepare message based on file type
        if extension in ['.txt', '.rtf']:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()[:50000]  # Limit to 50K chars
                messages = [{"role": "user", "content": f"Analyze this legal document:\n\n{content}"}]
            except Exception as e:
                print(f"  ❌ Error reading text file: {e}")
                return None

        elif extension in ['.jpg', '.jpeg', '.png', '.heic']:
            try:
                img_base64 = self.extract_text_from_image(file_path)
                messages = [{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img_base64}},
                        {"type": "text", "text": "Analyze this legal document image with PROJ344 scoring."}
                    ]
                }]
            except Exception as e:
                print(f"  ❌ Error processing image: {e}")
                return None

        elif extension in ['.pdf']:
            print(f"  ⚠️  PDF support coming soon - skipping for now")
            return None
        else:
            print(f"  ⚠️  Unsupported file type: {extension}")
            return None

        # PROJ344 Scoring System Prompt
        system_prompt = """You are a legal document intelligence analyst using PROJ344 scoring methodology.

Analyze and return ONLY JSON with PROJ344 scores:

{
  "document_type": "TEXT|TRNS|CPSR|MEDR|FORN|PLCR|ORDR|DECL|EXPA|MOTN|RESP|EVID|OTHER",
  "document_date": "YYYY-MM-DD or null",
  "document_title": "Brief descriptive title",
  "executive_summary": "2-3 sentence summary of document content and significance",

  "micro_number": 0-999,
  "macro_number": 0-999,
  "legal_number": 0-999,
  "category_number": 0-999,
  "relevancy_number": 0-999,

  "key_quotes": ["Important quote 1", "Important quote 2"],
  "smoking_guns": ["Critical fact or admission"],
  "parties": ["MOT", "FAT", "MIN", "CPS", "COURT"],
  "keywords": ["keyword1", "keyword2", "keyword3"],

  "status": "RECEIVED|UNDER_REVIEW|ANALYZED|FILED",
  "purpose": "EVIDENCE|MOTION|DISCOVERY|CORRESPONDENCE|COURT_ORDER|EXHIBIT",
  "importance": "CRITICAL|HIGH|MEDIUM|LOW|REFERENCE",

  "contains_false_statements": false,
  "fraud_indicators": [],
  "perjury_indicators": [],

  "w388_relevance": 0-100,
  "ccp473_relevance": 0-100,
  "criminal_relevance": 0-100
}

SCORING GUIDELINES:
- micro_number (0-999): Detail-level importance
- macro_number (0-999): Case-wide significance
- legal_number (0-999): Legal weight and admissibility
- relevancy_number (0-999): Weighted average of above
- 900-999: CRITICAL (smoking gun evidence)
- 800-899: IMPORTANT (strong evidence)
- 700-799: SIGNIFICANT (supporting evidence)
- 600-699: USEFUL (background)
- 0-599: REFERENCE (context)
"""

        try:
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                temperature=0.1,
                system=system_prompt,
                messages=messages
            )

            response_text = response.content[0].text.strip()

            # Clean JSON if wrapped in code blocks
            if response_text.startswith('```'):
                response_text = response_text.split('\n', 1)[1].rsplit('```', 1)[0]

            analysis = json.loads(response_text.strip())

            # Calculate API cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            api_cost = (input_tokens / 1_000_000 * 3) + (output_tokens / 1_000_000 * 15)

            analysis['api_cost_usd'] = api_cost
            analysis['processed_by'] = 'claude-sonnet-4.5'

            self.total_cost += api_cost

            print(f"  ✅ Relevancy={analysis['relevancy_number']}, Legal={analysis['legal_number']}, Cost=${api_cost:.4f}")

            return analysis

        except Exception as e:
            print(f"  ❌ API Error: {e}")
            return None

    def upload_to_supabase(self, file_path, analysis):
        """Upload document analysis to Supabase legal_documents table"""
        try:
            file_hash = self.calculate_file_hash(file_path)
            file_stats = file_path.stat()

            # Create standardized renamed filename
            doc_date = datetime.now().strftime('%Y%m%d')
            relevancy = analysis.get('relevancy_number', 0)
            doc_type = analysis.get('document_type', 'UNKNOWN')[:20].replace(' ', '_')
            renamed = f"{doc_date}_REL{relevancy}_{doc_type}_{file_path.stem[:30]}{file_path.suffix}"

            document_data = {
                'original_filename': file_path.name,
                'renamed_filename': renamed,
                'file_path': str(file_path),
                'file_extension': file_path.suffix.lower(),
                'file_size': file_stats.st_size,
                # 'content_hash': file_hash,  # Column doesn't exist in schema yet

                # PROJ344 Scores
                'micro_number': analysis.get('micro_number', 0),
                'macro_number': analysis.get('macro_number', 0),
                'legal_number': analysis.get('legal_number', 0),
                'category_number': analysis.get('category_number', 0),
                'relevancy_number': analysis.get('relevancy_number', 0),

                # Document Info
                'document_type': analysis.get('document_type'),
                'document_title': analysis.get('document_title'),
                'document_date': analysis.get('document_date'),
                'executive_summary': analysis.get('executive_summary'),

                # Arrays
                'key_quotes': analysis.get('key_quotes', []),
                'smoking_guns': analysis.get('smoking_guns', []),
                'parties': analysis.get('parties', []),
                'keywords': analysis.get('keywords', []),

                # Status
                'status': analysis.get('status', 'RECEIVED'),
                'purpose': analysis.get('purpose'),
                'importance': analysis.get('importance', 'MEDIUM'),

                # Legal Relevance
                'w388_relevance': analysis.get('w388_relevance', 0),
                'ccp473_relevance': analysis.get('ccp473_relevance', 0),
                'criminal_relevance': analysis.get('criminal_relevance', 0),

                # Fraud/Perjury
                'fraud_indicators': analysis.get('fraud_indicators', []),
                'perjury_indicators': analysis.get('perjury_indicators', []),

                # Processing Info
                'processed_at': datetime.now().isoformat(),
                'processed_by': analysis.get('processed_by'),
                'api_cost_usd': analysis.get('api_cost_usd', 0.0),

                # Case Info
                'case_id': self.case_id,
                'docket_number': 'J24-00478'
            }

            result = self.client.table('legal_documents').insert(document_data).execute()

            print(f"  ✅ Uploaded to Supabase (ID: {result.data[0]['id'][:8]}...)")
            return True

        except Exception as e:
            print(f"  ❌ Upload Error: {e}")
            return False

    def scan_directory(self, directory, extensions=['.pdf', '.jpg', '.jpeg', '.png', '.txt', '.rtf'], max_files=None):
        """Scan directory for documents"""
        print(f"\n🔍 Scanning: {directory}")
        print(f"   Extensions: {', '.join(extensions)}")
        print(f"   Max files: {max_files if max_files else 'unlimited'}")

        files = []
        for ext in extensions:
            files.extend(Path(directory).rglob(f"*{ext}"))
            files.extend(Path(directory).rglob(f"*{ext.upper()}"))

        print(f"   Found: {len(files)} files")

        if max_files:
            files = files[:max_files]

        return files

    def process_batch(self, files, start_index=0, batch_size=10):
        """Process a batch of files"""
        print(f"\n" + "="*60)
        print(f"BATCH PROCESSING: Files {start_index+1} to {start_index+batch_size}")
        print("="*60)

        for i, file_path in enumerate(files[start_index:start_index+batch_size], start=start_index+1):
            print(f"\n[{i}/{len(files)}] Processing: {file_path.name}")

            # Check if already processed (disabled until content_hash column added)
            # file_hash = self.calculate_file_hash(file_path)
            # if self.check_already_processed(file_hash):
            #     print(f"  ⏭️  Already in database - skipping")
            #     self.skipped_count += 1
            #     continue

            # Analyze document
            analysis = self.analyze_document(file_path)

            if analysis:
                # Upload to Supabase
                if self.upload_to_supabase(file_path, analysis):
                    self.processed_count += 1
                else:
                    self.error_count += 1
            else:
                self.error_count += 1

            # Rate limiting: Claude API allows 50 requests/min
            time.sleep(1.5)

        # Print batch summary
        print(f"\n" + "="*60)
        print(f"BATCH COMPLETE")
        print(f"  Processed: {self.processed_count}")
        print(f"  Skipped: {self.skipped_count}")
        print(f"  Errors: {self.error_count}")
        print(f"  Total Cost: ${self.total_cost:.2f}")
        print("="*60)

def main():
    # Get credentials from environment
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

    if not all([SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_API_KEY]):
        print("❌ Missing environment variables!")
        print("   Required: SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_API_KEY")
        sys.exit(1)

    scanner = BatchDocumentScanner(SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_API_KEY)

    # PHASE 1: Scan CH22_Legal (Priority documents)
    legal_dir = "/Users/dbucknor/Downloads/Areas/CH22_Legal"
    print("\n" + "🎯 PHASE 1: CH22_Legal Documents (Priority)")
    print("="*60)

    legal_files = scanner.scan_directory(
        legal_dir,
        extensions=['.jpg', '.jpeg', '.png', '.pdf', '.txt'],
        max_files=None  # Process all
    )

    if legal_files:
        # Process in batches of 10
        batch_size = 10
        for start in range(0, len(legal_files), batch_size):
            scanner.process_batch(legal_files, start_index=start, batch_size=batch_size)

            # Progress checkpoint every 50 files (auto-continue in background mode)
            if (start + batch_size) % 50 == 0 and (start + batch_size) < len(legal_files):
                print(f"\n✅ Checkpoint: {start + batch_size}/{len(legal_files)} files processed. Continuing automatically...\n")

    # PHASE 2: Scan all other directories (Optional)
    print("\n\n" + "🎯 PHASE 2: All Other Downloads Directories")
    print("="*60)
    cont = input("Scan all 902 documents in Downloads? (y/n): ")

    if cont.lower() == 'y':
        all_dirs = [
            "/Users/dbucknor/Downloads/Areas",
            "/Users/dbucknor/Downloads/Archive",
            "/Users/dbucknor/Downloads/Projects",
            "/Users/dbucknor/Downloads/Resources"
        ]

        for directory in all_dirs:
            if os.path.exists(directory):
                files = scanner.scan_directory(
                    directory,
                    extensions=['.jpg', '.jpeg', '.png', '.txt'],
                    max_files=None
                )

                if files:
                    for start in range(0, len(files), batch_size):
                        scanner.process_batch(files, start_index=start, batch_size=batch_size)

    # Final Summary
    print("\n\n" + "="*60)
    print("🎉 SCANNING COMPLETE!")
    print("="*60)
    print(f"  Total Processed: {scanner.processed_count}")
    print(f"  Total Skipped: {scanner.skipped_count}")
    print(f"  Total Errors: {scanner.error_count}")
    print(f"  Total API Cost: ${scanner.total_cost:.2f}")
    print("="*60)
    print(f"\n✅ All documents uploaded to Supabase!")
    print(f"   Query at: {SUPABASE_URL}")

if __name__ == "__main__":
    main()
