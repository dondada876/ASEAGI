#!/usr/bin/env python3
"""
ASEAGI Queue Manager Service
Orchestrates document processing with assessment phase and queue management
"""

import os
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass
from pathlib import Path

try:
    from supabase import create_client
except ImportError:
    print("[ERROR] Supabase not installed")
    exit(1)

from tiered_deduplicator import TieredDeduplicator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class DocumentSubmission:
    """Document submission data"""
    file_path: str
    original_filename: str
    source_type: str  # 'mobile', 'telegram', 'web_upload', etc.
    source_device: Optional[str] = None
    source_user_id: Optional[str] = None


@dataclass
class AssessmentResult:
    """Result of document assessment"""
    journal_id: int
    should_process: bool
    reason: str
    is_duplicate: bool = False
    duplicate_of: Optional[int] = None
    duplicate_tier: Optional[int] = None
    priority: int = 5
    document_type: str = 'unknown'


class QueueManager:
    """
    Manages document submission, assessment, and queueing

    Workflow:
    1. Accept document submission
    2. Add to universal journal (truth table)
    3. Run assessment phase:
       - Check if duplicate (3-tier deduplication)
       - Determine document type
       - Apply document type rules
       - Calculate priority
    4. Decision:
       - If duplicate → Mark and skip
       - If new → Add to processing queue
    5. Track all metrics
    """

    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        openai_key: Optional[str] = None
    ):
        self.supabase = create_client(supabase_url, supabase_key)
        self.deduplicator = TieredDeduplicator(
            supabase_url=supabase_url,
            supabase_key=supabase_key,
            openai_key=openai_key
        )

    # ========================================================================
    # MAIN WORKFLOW
    # ========================================================================

    def submit_document(self, submission: DocumentSubmission) -> AssessmentResult:
        """
        Main entry point for document submission

        Returns AssessmentResult with decision on whether to process
        """
        logger.info("=" * 80)
        logger.info("DOCUMENT SUBMISSION")
        logger.info("=" * 80)
        logger.info(f"File: {submission.original_filename}")
        logger.info(f"Source: {submission.source_type}")
        logger.info("")

        # Step 1: Calculate file hash
        file_hash = self._calculate_file_hash(submission.file_path)
        logger.info(f"File hash: {file_hash[:16]}...")

        # Step 2: Check if already in journal
        existing = self._check_existing_in_journal(file_hash)
        if existing:
            logger.info(f"⚠️  Document already in journal (ID: {existing['journal_id']})")
            logger.info(f"   Status: {existing['queue_status']}")

            return AssessmentResult(
                journal_id=existing['journal_id'],
                should_process=False,
                reason=f"Already in system (status: {existing['queue_status']})",
                is_duplicate=True,
                duplicate_of=existing['journal_id']
            )

        # Step 3: Add to journal
        journal_id = self._add_to_journal(submission, file_hash)
        logger.info(f"✅ Added to journal (ID: {journal_id})")

        # Step 4: Run assessment phase
        logger.info("")
        logger.info("🔍 ASSESSMENT PHASE")
        logger.info("-" * 80)

        assessment = self._run_assessment(journal_id, submission)

        # Step 5: Update journal with assessment results
        self._update_journal_with_assessment(journal_id, assessment)

        # Step 6: If should process, add to processing queue
        if assessment.should_process:
            self._add_to_processing_queue(journal_id, assessment.priority)
            logger.info(f"✅ Added to processing queue (priority: {assessment.priority})")
        else:
            logger.info(f"⏭️  Skipped: {assessment.reason}")

        logger.info("")
        logger.info("=" * 80)

        return assessment

    # ========================================================================
    # ASSESSMENT PHASE
    # ========================================================================

    def _run_assessment(
        self,
        journal_id: int,
        submission: DocumentSubmission
    ) -> AssessmentResult:
        """
        Run comprehensive assessment on document

        Steps:
        1. Detect document type
        2. Run tiered deduplication
        3. Apply document type rules
        4. Calculate priority
        5. Make decision
        """

        # Update status
        self._update_journal_status(journal_id, 'assessing')

        # Step 1: Detect document type
        logger.info("Step 1: Detecting document type...")
        document_type = self._detect_document_type(submission)
        logger.info(f"   Document type: {document_type}")

        self._log_processing_step(
            journal_id,
            'document_type_detection',
            'success',
            {'document_type': document_type}
        )

        # Step 2: Run tiered deduplication
        logger.info("Step 2: Running tiered deduplication...")
        dup_result = self.deduplicator.check_duplicate(
            filename=submission.original_filename,
            file_path=submission.file_path
        )

        if dup_result.is_duplicate:
            logger.info(f"   ⚠️  DUPLICATE DETECTED")
            logger.info(f"   Method: {dup_result.match_type}")
            logger.info(f"   Similarity: {dup_result.similarity:.0%}")
            logger.info(f"   Tier: {dup_result.tier}")

            self._log_processing_step(
                journal_id,
                f'duplicate_detection_tier{dup_result.tier}',
                'duplicate_found',
                {
                    'method': dup_result.match_type,
                    'similarity': float(dup_result.similarity),
                    'matched_document': dup_result.matched_document.get('file_name') if dup_result.matched_document else None
                }
            )

            return AssessmentResult(
                journal_id=journal_id,
                should_process=False,
                reason=f"Duplicate detected ({dup_result.match_type}, {dup_result.similarity:.0%} match)",
                is_duplicate=True,
                duplicate_of=dup_result.matched_document.get('id') if dup_result.matched_document else None,
                duplicate_tier=dup_result.tier,
                document_type=document_type
            )

        logger.info("   ✅ No duplicate found")

        # Step 3: Apply document type rules
        logger.info("Step 3: Applying document type rules...")
        rules = self._get_document_type_rules(document_type)
        logger.info(f"   Rules: {rules}")

        # Step 4: Calculate priority
        priority = rules.get('default_priority', 5)
        logger.info(f"   Priority: {priority}/10")

        # Step 5: Check compliance requirements
        if rules.get('requires_human_review', False):
            logger.info("   ⚠️  Manual review required")
            return AssessmentResult(
                journal_id=journal_id,
                should_process=False,
                reason="Manual review required per document type rules",
                document_type=document_type,
                priority=priority
            )

        # Step 6: Decision
        logger.info("   ✅ Document approved for processing")

        return AssessmentResult(
            journal_id=journal_id,
            should_process=True,
            reason="Assessment passed, ready for processing",
            document_type=document_type,
            priority=priority
        )

    # ========================================================================
    # JOURNAL MANAGEMENT
    # ========================================================================

    def _add_to_journal(
        self,
        submission: DocumentSubmission,
        file_hash: str
    ) -> int:
        """Add document to universal journal"""

        # Get file metadata
        file_stat = Path(submission.file_path).stat()

        journal_data = {
            'file_hash': file_hash,
            'original_filename': submission.original_filename,
            'original_file_path': submission.file_path,
            'original_file_extension': Path(submission.original_filename).suffix,
            'original_file_size': file_stat.st_size,
            'source_type': submission.source_type,
            'source_device': submission.source_device,
            'source_user_id': submission.source_user_id,
            'date_logged': datetime.now().isoformat(),
            'date_uploaded': datetime.now().isoformat(),
            'queue_status': 'pending',
            'queue_priority': 5
        }

        result = self.supabase.table('document_journal')\
            .insert(journal_data)\
            .execute()

        return result.data[0]['journal_id']

    def _check_existing_in_journal(self, file_hash: str) -> Optional[Dict]:
        """Check if document already exists in journal"""

        result = self.supabase.table('document_journal')\
            .select('journal_id, queue_status, is_duplicate')\
            .eq('file_hash', file_hash)\
            .execute()

        if result.data:
            return result.data[0]
        return None

    def _update_journal_status(self, journal_id: int, status: str):
        """Update journal status"""

        self.supabase.table('document_journal')\
            .update({'queue_status': status})\
            .eq('journal_id', journal_id)\
            .execute()

    def _update_journal_with_assessment(
        self,
        journal_id: int,
        assessment: AssessmentResult
    ):
        """Update journal with assessment results"""

        update_data = {
            'document_type': assessment.document_type,
            'queue_priority': assessment.priority,
            'is_duplicate': assessment.is_duplicate,
            'duplicate_detection_tier': assessment.duplicate_tier,
            'queue_status': 'skipped_duplicate' if assessment.is_duplicate else 'queued'
        }

        if assessment.duplicate_of:
            update_data['duplicate_of_journal_id'] = assessment.duplicate_of

        self.supabase.table('document_journal')\
            .update(update_data)\
            .eq('journal_id', journal_id)\
            .execute()

    # ========================================================================
    # PROCESSING QUEUE MANAGEMENT
    # ========================================================================

    def _add_to_processing_queue(self, journal_id: int, priority: int):
        """Add document to processing queue"""

        queue_data = {
            'journal_id': journal_id,
            'priority': priority,
            'status': 'queued',
            'processing_tier': 'full_processing'
        }

        self.supabase.table('processing_queue')\
            .insert(queue_data)\
            .execute()

    def get_next_from_queue(self, worker_id: str) -> Optional[Dict]:
        """Get next document from queue for processing"""

        # Get highest priority queued item
        result = self.supabase.table('processing_queue')\
            .select('*, document_journal(*)')\
            .eq('status', 'queued')\
            .order('priority', desc=True)\
            .order('queued_at', desc=False)\
            .limit(1)\
            .execute()

        if not result.data:
            return None

        queue_item = result.data[0]

        # Assign to worker
        self.supabase.table('processing_queue')\
            .update({
                'status': 'assigned',
                'assigned_to_worker': worker_id,
                'assigned_at': datetime.now().isoformat()
            })\
            .eq('queue_id', queue_item['queue_id'])\
            .execute()

        return queue_item

    def complete_queue_item(
        self,
        queue_id: int,
        success: bool,
        result_data: Optional[Dict] = None,
        error_message: Optional[str] = None
    ):
        """Mark queue item as complete"""

        update_data = {
            'status': 'completed' if success else 'failed',
            'completed_at': datetime.now().isoformat(),
            'result_data': result_data,
            'error_message': error_message
        }

        self.supabase.table('processing_queue')\
            .update(update_data)\
            .eq('queue_id', queue_id)\
            .execute()

        # Update journal
        journal_status = 'completed' if success else 'failed'
        self.supabase.table('document_journal')\
            .update({
                'queue_status': journal_status,
                'date_processing_completed': datetime.now().isoformat()
            })\
            .eq('journal_id', queue_id)\
            .execute()

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of file"""
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
        return md5.hexdigest()

    def _detect_document_type(self, submission: DocumentSubmission) -> str:
        """
        Detect document type from filename and metadata

        Types:
        - business_card
        - legal_document
        - court_filing
        - photo
        - sign
        - form
        - receipt
        - other
        """

        filename_lower = submission.original_filename.lower()

        # Check file extension
        ext = Path(submission.original_filename).suffix.lower()

        # Business card indicators
        if any(x in filename_lower for x in ['business_card', 'card', 'contact']):
            return 'business_card'

        # Legal document indicators
        if any(x in filename_lower for x in ['motion', 'declaration', 'order', 'judgment', 'petition']):
            return 'court_filing'

        if any(x in filename_lower for x in ['legal', 'contract', 'agreement']):
            return 'legal_document'

        # Form indicators
        if any(x in filename_lower for x in ['form', 'jv-', 'fl-']):
            return 'form'

        # Receipt indicators
        if any(x in filename_lower for x in ['receipt', 'invoice']):
            return 'receipt'

        # Sign indicators
        if any(x in filename_lower for x in ['sign', 'signage', 'billboard']):
            return 'sign'

        # Photo indicators
        if ext in ['.jpg', '.jpeg', '.png', '.heic'] and 'img_' in filename_lower:
            return 'photo'

        return 'unknown'

    def _get_document_type_rules(self, document_type: str) -> Dict:
        """Get processing rules for document type"""

        result = self.supabase.table('document_type_rules')\
            .select('*')\
            .eq('document_type', document_type)\
            .execute()

        if result.data:
            return result.data[0]

        # Default rules
        return {
            'default_priority': 5,
            'requires_ocr': True,
            'requires_ai_analysis': True,
            'requires_human_review': False
        }

    def _log_processing_step(
        self,
        journal_id: int,
        step: str,
        status: str,
        metrics: Optional[Dict] = None
    ):
        """Log processing step to metrics table"""

        log_data = {
            'journal_id': journal_id,
            'processing_step': step,
            'step_status': status,
            'metrics': metrics,
            'step_started_at': datetime.now().isoformat()
        }

        self.supabase.table('processing_metrics_log')\
            .insert(log_data)\
            .execute()

    # ========================================================================
    # QUEUE STATISTICS
    # ========================================================================

    def get_queue_stats(self) -> Dict:
        """Get current queue statistics"""

        result = self.supabase.table('document_journal')\
            .select('queue_status')\
            .execute()

        stats = {}
        for row in result.data:
            status = row['queue_status']
            stats[status] = stats.get(status, 0) + 1

        return stats

    def get_processing_performance(self) -> List[Dict]:
        """Get processing performance metrics"""

        # Use the view
        result = self.supabase.table('processing_performance')\
            .select('*')\
            .execute()

        return result.data


def main():
    """Test the queue manager"""

    # Configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    OPENAI_KEY = os.environ.get('OPENAI_API_KEY')

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("ERROR: SUPABASE_URL and SUPABASE_KEY must be set")
        return

    # Initialize queue manager
    manager = QueueManager(SUPABASE_URL, SUPABASE_KEY, OPENAI_KEY)

    # Example: Submit a document
    test_file = input("Enter path to test document: ").strip()

    if test_file and os.path.exists(test_file):
        submission = DocumentSubmission(
            file_path=test_file,
            original_filename=os.path.basename(test_file),
            source_type='test',
            source_device='laptop'
        )

        result = manager.submit_document(submission)

        print()
        print("=" * 80)
        print("ASSESSMENT RESULT")
        print("=" * 80)
        print(f"Journal ID: {result.journal_id}")
        print(f"Should Process: {result.should_process}")
        print(f"Reason: {result.reason}")
        print(f"Is Duplicate: {result.is_duplicate}")
        print(f"Document Type: {result.document_type}")
        print(f"Priority: {result.priority}")
        print()

    # Show queue stats
    stats = manager.get_queue_stats()
    print("Queue Statistics:")
    for status, count in stats.items():
        print(f"  {status}: {count}")


if __name__ == "__main__":
    main()
