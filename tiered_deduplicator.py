#!/usr/bin/env python3
"""
Tiered Deduplication System
Smart content-based duplicate detection with 3 tiers:
- Tier 0: Filename similarity (fast, free)
- Tier 1: OCR content matching (local Tesseract, free)
- Tier 2: AI semantic embeddings (OpenAI, $0.0001)
"""

import os
import re
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher
from dataclasses import dataclass

try:
    from fuzzywuzzy import fuzz
except ImportError:
    print("[WARN] Installing fuzzywuzzy...")
    os.system("pip install fuzzywuzzy python-Levenshtein --quiet")
    from fuzzywuzzy import fuzz

try:
    import pytesseract
    from PIL import Image
except ImportError:
    print("[WARN] Installing pytesseract and PIL...")
    os.system("pip install pytesseract Pillow --quiet")
    import pytesseract
    from PIL import Image

try:
    import openai
except ImportError:
    print("[WARN] Installing openai...")
    os.system("pip install openai --quiet")
    import openai

try:
    from supabase import create_client
except ImportError:
    print("[WARN] Installing supabase...")
    os.system("pip install supabase --quiet")
    from supabase import create_client


@dataclass
class DuplicateMatch:
    """Duplicate match result"""
    is_duplicate: bool
    match_type: str  # 'filename', 'ocr_content', 'semantic', 'none'
    similarity: float
    matched_document: Optional[Dict] = None
    tier: int = 0  # 0, 1, or 2


class TieredDeduplicator:
    """Smart tiered duplicate detection system"""

    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        openai_key: Optional[str] = None
    ):
        self.supabase = create_client(supabase_url, supabase_key)
        self.openai_key = openai_key
        if openai_key:
            openai.api_key = openai_key

        self.stats = {
            'tier0_checks': 0,
            'tier0_duplicates': 0,
            'tier1_checks': 0,
            'tier1_duplicates': 0,
            'tier2_checks': 0,
            'tier2_duplicates': 0,
            'new_documents': 0
        }

    # =========================================================================
    # TIER 0: Filename Matching
    # =========================================================================

    def normalize_filename(self, filename: str) -> str:
        """Normalize filename for comparison"""
        # Remove extension
        name = filename.rsplit('.', 1)[0] if '.' in filename else filename

        # Remove common prefixes/suffixes
        patterns = [
            r'IMG_', r'SCAN_', r'DOC_', r'Copy of ', r'Final ',
            r'Draft ', r'v\d+', r'_\d{4}', r'\d{8}'
        ]
        for pattern in patterns:
            name = re.sub(pattern, '', name, flags=re.IGNORECASE)

        # Remove special chars
        name = re.sub(r'[_\-\.\(\)\[\]]', ' ', name)

        # Remove extra spaces
        name = re.sub(r'\s+', ' ', name)

        # Lowercase and strip
        return name.lower().strip()

    def tier0_filename_check(
        self,
        filename: str,
        threshold: float = 0.7
    ) -> DuplicateMatch:
        """
        Tier 0: Fast filename similarity check
        Cost: $0 | Speed: <1ms
        """
        self.stats['tier0_checks'] += 1

        print(f"\n🔍 TIER 0: Checking filename similarity...")
        print(f"   File: {filename}")

        normalized = self.normalize_filename(filename)
        print(f"   Normalized: '{normalized}'")

        # Get all documents from registry
        try:
            docs = self.supabase.table('master_document_registry')\
                .select('id, file_name, file_hash, processing_status')\
                .execute()
        except Exception as e:
            print(f"   ⚠️ Database query failed: {e}")
            return DuplicateMatch(False, 'none', 0.0, None, 0)

        best_match = None
        best_similarity = 0.0

        for doc in docs.data:
            existing_normalized = self.normalize_filename(doc['file_name'])

            # Calculate similarity
            similarity = fuzz.ratio(normalized, existing_normalized) / 100.0

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = doc

        print(f"   Best match: {best_match['file_name'] if best_match else 'None'}")
        print(f"   Similarity: {best_similarity:.0%}")

        if best_similarity >= threshold:
            self.stats['tier0_duplicates'] += 1
            print(f"   ✅ DUPLICATE FOUND (Tier 0)")
            return DuplicateMatch(
                is_duplicate=True,
                match_type='filename',
                similarity=best_similarity,
                matched_document=best_match,
                tier=0
            )

        print(f"   ⏭️ No filename match, proceeding to Tier 1")
        return DuplicateMatch(False, 'none', best_similarity, None, 0)

    # =========================================================================
    # TIER 1: OCR Content Matching
    # =========================================================================

    def extract_text_ocr(self, file_path: str) -> str:
        """Extract text using Tesseract OCR"""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            print(f"   ⚠️ OCR extraction failed: {e}")
            return ""

    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between texts"""
        # Normalize
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()

        if not text1 or not text2:
            return 0.0

        # Take first 1000 chars (representative sample)
        text1 = text1[:1000]
        text2 = text2[:1000]

        # Split into words
        words1 = set(text1.split())
        words2 = set(text2.split())

        # Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        if union == 0:
            return 0.0

        return intersection / union

    def tier1_ocr_check(
        self,
        file_path: str,
        threshold: float = 0.85
    ) -> DuplicateMatch:
        """
        Tier 1: OCR content similarity check
        Cost: $0 (local Tesseract) | Speed: 2-5s
        """
        self.stats['tier1_checks'] += 1

        print(f"\n🔍 TIER 1: Extracting text with OCR...")

        # Extract text from new document
        new_text = self.extract_text_ocr(file_path)

        if not new_text:
            print(f"   ⚠️ No text extracted, skipping Tier 1")
            return DuplicateMatch(False, 'none', 0.0, None, 1)

        print(f"   Extracted {len(new_text)} characters")
        print(f"   Preview: {new_text[:100]}...")

        # Get all documents with content
        try:
            docs = self.supabase.table('document_repository')\
                .select('id, file_name, content')\
                .execute()
        except Exception as e:
            print(f"   ⚠️ Database query failed: {e}")
            return DuplicateMatch(False, 'none', 0.0, None, 1)

        best_match = None
        best_similarity = 0.0

        print(f"   Comparing against {len(docs.data)} documents...")

        for doc in docs.data:
            existing_text = doc.get('content', '')

            if not existing_text:
                continue

            similarity = self.calculate_text_similarity(new_text, existing_text)

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = doc

        print(f"   Best match: {best_match['file_name'] if best_match else 'None'}")
        print(f"   Similarity: {best_similarity:.0%}")

        if best_similarity >= threshold:
            self.stats['tier1_duplicates'] += 1
            print(f"   ✅ DUPLICATE FOUND (Tier 1 - OCR Content)")
            return DuplicateMatch(
                is_duplicate=True,
                match_type='ocr_content',
                similarity=best_similarity,
                matched_document=best_match,
                tier=1
            )

        print(f"   ⏭️ No OCR match, proceeding to Tier 2")
        return DuplicateMatch(False, 'none', best_similarity, None, 1)

    # =========================================================================
    # TIER 2: AI Semantic Matching
    # =========================================================================

    def generate_embedding(self, text: str) -> List[float]:
        """Generate OpenAI embedding for text"""
        if not self.openai_key:
            raise Exception("OpenAI API key not set")

        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=text[:8000]  # Max ~8k tokens
        )

        return response['data'][0]['embedding']

    def tier2_semantic_check(
        self,
        text: str,
        threshold: float = 0.95
    ) -> DuplicateMatch:
        """
        Tier 2: AI semantic similarity check
        Cost: $0.0001 | Speed: 500ms
        """
        self.stats['tier2_checks'] += 1

        print(f"\n🔍 TIER 2: Checking semantic similarity...")

        if not self.openai_key:
            print(f"   ⚠️ OpenAI key not set, skipping Tier 2")
            return DuplicateMatch(False, 'none', 0.0, None, 2)

        # Generate embedding
        print(f"   Generating embedding...")
        embedding = self.generate_embedding(text)

        # Query pgvector for similar documents
        print(f"   Querying vector database...")

        try:
            result = self.supabase.rpc('match_documents', {
                'query_embedding': embedding,
                'match_threshold': threshold,
                'match_count': 5
            }).execute()
        except Exception as e:
            print(f"   ⚠️ Vector search failed: {e}")
            print(f"   (Make sure match_documents() function exists in Supabase)")
            return DuplicateMatch(False, 'none', 0.0, None, 2)

        if result.data and len(result.data) > 0:
            best_match = result.data[0]
            similarity = best_match['similarity']

            print(f"   Best match: {best_match['file_name']}")
            print(f"   Similarity: {similarity:.0%}")

            if similarity >= threshold:
                self.stats['tier2_duplicates'] += 1
                print(f"   ✅ DUPLICATE FOUND (Tier 2 - Semantic)")
                return DuplicateMatch(
                    is_duplicate=True,
                    match_type='semantic',
                    similarity=similarity,
                    matched_document=best_match,
                    tier=2
                )

        print(f"   ✅ CONFIRMED NEW DOCUMENT")
        return DuplicateMatch(False, 'none', 0.0, None, 2)

    # =========================================================================
    # MAIN CHECK FUNCTION
    # =========================================================================

    def check_duplicate(
        self,
        filename: str,
        file_path: str,
        text: Optional[str] = None
    ) -> DuplicateMatch:
        """
        Run tiered duplicate check
        Returns match information if duplicate found at any tier
        """

        print("=" * 80)
        print("TIERED DUPLICATE DETECTION")
        print("=" * 80)

        # Tier 0: Filename
        result = self.tier0_filename_check(filename, threshold=0.7)
        if result.is_duplicate:
            return result

        # Tier 1: OCR Content
        result = self.tier1_ocr_check(file_path, threshold=0.85)
        if result.is_duplicate:
            return result

        # Tier 2: Semantic
        if text is None:
            text = self.extract_text_ocr(file_path)

        if text and self.openai_key:
            result = self.tier2_semantic_check(text, threshold=0.95)
            if result.is_duplicate:
                return result

        # No duplicate found
        self.stats['new_documents'] += 1
        print(f"\n✅ NEW DOCUMENT CONFIRMED")
        print(f"   Ready for full processing")

        return DuplicateMatch(False, 'none', 0.0, None, 2)

    def print_stats(self):
        """Print deduplication statistics"""
        print()
        print("=" * 80)
        print("DEDUPLICATION STATISTICS")
        print("=" * 80)
        print(f"Tier 0 (Filename) checks: {self.stats['tier0_checks']}")
        print(f"   Duplicates found: {self.stats['tier0_duplicates']}")
        print(f"Tier 1 (OCR) checks: {self.stats['tier1_checks']}")
        print(f"   Duplicates found: {self.stats['tier1_duplicates']}")
        print(f"Tier 2 (Semantic) checks: {self.stats['tier2_checks']}")
        print(f"   Duplicates found: {self.stats['tier2_duplicates']}")
        print(f"New documents: {self.stats['new_documents']}")
        print()

        total_duplicates = (self.stats['tier0_duplicates'] +
                           self.stats['tier1_duplicates'] +
                           self.stats['tier2_duplicates'])
        total_checks = self.stats['tier0_checks']

        if total_checks > 0:
            print(f"Duplicate detection rate: {total_duplicates}/{total_checks} " +
                  f"({total_duplicates/total_checks*100:.1f}%)")
            print()


def main():
    """Test the tiered deduplication system"""

    print()
    print("=" * 80)
    print("TIERED DEDUPLICATION SYSTEM TEST")
    print("=" * 80)
    print()

    # Get credentials
    supabase_url = os.environ.get('SUPABASE_URL',
                                  'https://jvjlhxodmbkodzmggwpu.supabase.co')
    supabase_key = os.environ.get('SUPABASE_KEY', '')
    openai_key = os.environ.get('OPENAI_API_KEY', '')

    if not supabase_key:
        print("❌ SUPABASE_KEY not set")
        return

    # Initialize deduplicator
    deduplicator = TieredDeduplicator(
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        openai_key=openai_key
    )

    # Test with a file
    test_file = input("Enter path to test document (or press Enter to skip): ").strip()

    if test_file and os.path.exists(test_file):
        filename = os.path.basename(test_file)
        result = deduplicator.check_duplicate(filename, test_file)

        print()
        print("=" * 80)
        print("RESULT")
        print("=" * 80)
        print(f"Is duplicate: {result.is_duplicate}")
        if result.is_duplicate:
            print(f"Match type: {result.match_type}")
            print(f"Similarity: {result.similarity:.0%}")
            print(f"Matched document: {result.matched_document['file_name']}")
            print(f"Tier: {result.tier}")
        print()

        deduplicator.print_stats()

    else:
        print("No test file provided")
        print()
        print("Usage:")
        print("  export SUPABASE_KEY='your-key'")
        print("  export OPENAI_API_KEY='your-key'")
        print("  python3 tiered_deduplicator.py")
        print()


if __name__ == "__main__":
    main()
