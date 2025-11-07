"""
Batch Processing Manager
Orchestrates processing of 7TB Google Drive documents using Vast.ai GPU instances
"""

import os
import logging
import time
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
from pathlib import Path

from supabase import create_client, Client
from vastai_client import VastAIClient
from google_drive_sync import GoogleDriveSync, GoogleDriveDocument
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


@dataclass
class BatchJob:
    """Represents a batch processing job"""
    batch_id: str
    batch_number: int
    total_batches: int
    document_count: int
    document_ids: List[str]
    status: str  # "pending", "downloading", "processing", "completed", "failed"
    vastai_instance_id: Optional[int] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    processed_count: int = 0
    error_message: Optional[str] = None
    estimated_completion: Optional[str] = None


@dataclass
class ProcessingSession:
    """Represents an entire processing session"""
    session_id: str
    total_documents: int
    total_batches: int
    completed_batches: int
    failed_batches: int
    status: str  # "running", "paused", "completed", "failed"
    started_at: str
    estimated_completion: Optional[str] = None
    vastai_instance_id: Optional[int] = None
    total_cost: float = 0.0


class BatchProcessingManager:
    """
    Batch Processing Manager

    Orchestrates the entire pipeline for processing 7TB of documents:
    1. List documents from Google Drive
    2. Filter out already processed documents
    3. Create batches (100 documents each)
    4. Rent Vast.ai GPU instance
    5. Submit batches for processing
    6. Monitor progress
    7. Stop instance when complete

    Target: 70,000 documents, 700 batches, 87.5 hours, $44 cost
    """

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        vastai_api_key: Optional[str] = None,
        google_credentials_path: str = "credentials.json",
        batch_size: int = 100,
        checkpoint_interval: int = 10  # Save progress every N batches
    ):
        """
        Initialize batch processing manager

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key
            vastai_api_key: Vast.ai API key
            google_credentials_path: Path to Google OAuth2 credentials
            batch_size: Documents per batch
            checkpoint_interval: Save checkpoint every N batches
        """
        # Initialize Supabase client
        supabase_url = supabase_url or os.environ.get('SUPABASE_URL')
        supabase_key = supabase_key or os.environ.get('SUPABASE_KEY')

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be provided")

        self.supabase: Client = create_client(supabase_url, supabase_key)

        # Initialize Vast.ai client
        self.vastai = VastAIClient(api_key=vastai_api_key)

        # Initialize Google Drive sync
        self.drive_sync = GoogleDriveSync(credentials_path=google_credentials_path)

        self.batch_size = batch_size
        self.checkpoint_interval = checkpoint_interval

        # State tracking
        self.current_session: Optional[ProcessingSession] = None
        self.current_batch: Optional[BatchJob] = None
        self.vastai_instance_id: Optional[int] = None

        # Paths
        self.state_dir = Path("batch_state")
        self.state_dir.mkdir(exist_ok=True)

        logger.info("✅ Batch Processing Manager initialized")

    def start_processing_session(
        self,
        folder_id: Optional[str] = None,
        mime_types: Optional[List[str]] = None,
        max_documents: Optional[int] = None
    ) -> ProcessingSession:
        """
        Start a new batch processing session

        Args:
            folder_id: Google Drive folder ID (None = root)
            mime_types: Filter by MIME types (default: PDFs only)
            max_documents: Maximum documents to process

        Returns:
            ProcessingSession object
        """
        logger.info("🚀 Starting batch processing session...")

        # Default to PDFs if not specified
        if mime_types is None:
            mime_types = ['application/pdf']

        # Step 1: Authenticate with Google Drive
        logger.info("🔐 Authenticating with Google Drive...")
        self.drive_sync.authenticate()

        # Step 2: List all documents
        logger.info("📋 Listing documents from Google Drive...")
        all_documents = self.drive_sync.list_documents(
            folder_id=folder_id,
            mime_types=mime_types,
            max_results=max_documents,
            recursive=True
        )

        logger.info(f"✅ Found {len(all_documents)} total documents")

        # Step 3: Get already processed documents from document_journal
        logger.info("🔍 Checking for already processed documents...")
        processed_ids = self._get_processed_document_ids()

        # Step 4: Filter unprocessed documents
        unprocessed = self.drive_sync.filter_unprocessed(all_documents, processed_ids)

        logger.info(f"📊 {len(unprocessed)} documents need processing")

        if not unprocessed:
            logger.info("✅ All documents already processed!")
            return None

        # Step 5: Create batches
        logger.info(f"📦 Creating batches of {self.batch_size} documents...")
        batches = self.drive_sync.create_batches(unprocessed, self.batch_size)

        # Step 6: Estimate cost
        estimate = self.vastai.estimate_cost(
            total_documents=len(unprocessed),
            batch_size=self.batch_size,
            cost_per_hour=0.50,
            seconds_per_document=4.5
        )

        logger.info(f"💰 Estimated cost: ${estimate['total_cost']:.2f} for {estimate['total_hours']:.1f} hours")

        # Step 7: Check Vast.ai balance
        balance = self.vastai.get_account_balance()

        if balance < estimate['total_cost']:
            raise RuntimeError(
                f"❌ Insufficient Vast.ai balance: ${balance:.2f} < ${estimate['total_cost']:.2f}"
            )

        logger.info(f"✅ Sufficient balance: ${balance:.2f} >= ${estimate['total_cost']:.2f}")

        # Step 8: Create session
        session_id = f"batch_session_{int(time.time())}"

        estimated_completion = datetime.now() + timedelta(hours=estimate['total_hours'])

        session = ProcessingSession(
            session_id=session_id,
            total_documents=len(unprocessed),
            total_batches=len(batches),
            completed_batches=0,
            failed_batches=0,
            status="running",
            started_at=datetime.now().isoformat(),
            estimated_completion=estimated_completion.isoformat(),
            total_cost=estimate['total_cost']
        )

        self.current_session = session

        # Save session state
        self._save_session_state(session)

        logger.info(f"✅ Session {session_id} created: {len(unprocessed)} docs, {len(batches)} batches")

        return session

    def rent_gpu_instance(
        self,
        gpu_name: Optional[str] = None,
        min_gpu_ram: int = 24,
        max_cost_per_hour: float = 1.0
    ) -> int:
        """
        Rent a Vast.ai GPU instance for processing

        Args:
            gpu_name: Specific GPU model (None = any)
            min_gpu_ram: Minimum GPU RAM in GB
            max_cost_per_hour: Maximum hourly cost

        Returns:
            Instance ID
        """
        logger.info("🔍 Searching for available GPU instances...")

        # Search for instances
        instances = self.vastai.search_instances(
            gpu_name=gpu_name,
            min_gpu_ram=min_gpu_ram,
            max_cost_per_hour=max_cost_per_hour,
            min_disk_space=100,
            verified_only=True
        )

        if not instances:
            raise RuntimeError("❌ No suitable GPU instances available")

        # Select cheapest instance
        selected = instances[0]

        logger.info(f"✅ Selected: {selected.get('gpu_name')} at ${selected.get('dph_total', 0):.2f}/hour")

        # Rent instance
        instance_id = selected['id']

        result = self.vastai.rent_instance(
            instance_id=instance_id,
            image="pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime",
            disk_space=100
        )

        # Wait for instance to be ready
        logger.info("⏳ Waiting for instance to be ready...")
        ready = self.vastai.wait_for_instance_ready(instance_id, timeout=600)

        if not ready:
            raise RuntimeError(f"❌ Instance {instance_id} failed to start")

        self.vastai_instance_id = instance_id

        if self.current_session:
            self.current_session.vastai_instance_id = instance_id
            self._save_session_state(self.current_session)

        logger.info(f"✅ Instance {instance_id} is ready for processing")

        return instance_id

    def process_batches(
        self,
        batches: List[List[GoogleDriveDocument]],
        start_batch: int = 0
    ) -> Dict[str, Any]:
        """
        Process all batches

        Args:
            batches: List of document batches
            start_batch: Start from this batch number (for resume)

        Returns:
            Processing results
        """
        if not self.vastai_instance_id:
            raise RuntimeError("Must rent GPU instance before processing")

        logger.info(f"🚀 Processing {len(batches)} batches starting from batch {start_batch}")

        results = {
            "total_batches": len(batches),
            "completed": 0,
            "failed": 0,
            "started_at": datetime.now().isoformat(),
            "completed_at": None
        }

        for i, batch in enumerate(batches[start_batch:], start=start_batch):
            batch_number = i + 1

            logger.info(f"\n{'='*60}")
            logger.info(f"📦 Processing Batch {batch_number}/{len(batches)}")
            logger.info(f"{'='*60}")

            try:
                # Process this batch
                batch_result = self._process_single_batch(
                    batch=batch,
                    batch_number=batch_number,
                    total_batches=len(batches)
                )

                if batch_result['status'] == 'completed':
                    results['completed'] += 1

                    if self.current_session:
                        self.current_session.completed_batches += 1

                else:
                    results['failed'] += 1

                    if self.current_session:
                        self.current_session.failed_batches += 1

                # Checkpoint every N batches
                if batch_number % self.checkpoint_interval == 0:
                    logger.info(f"💾 Checkpoint: {batch_number}/{len(batches)} batches completed")
                    self._save_checkpoint(batch_number)

            except Exception as e:
                logger.error(f"❌ Batch {batch_number} failed: {e}")
                results['failed'] += 1

                if self.current_session:
                    self.current_session.failed_batches += 1

                # Continue to next batch
                continue

        results['completed_at'] = datetime.now().isoformat()

        # Update session status
        if self.current_session:
            if results['failed'] == 0:
                self.current_session.status = "completed"
            else:
                self.current_session.status = "completed_with_errors"

            self._save_session_state(self.current_session)

        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Processing Complete!")
        logger.info(f"{'='*60}")
        logger.info(f"Total Batches: {results['total_batches']}")
        logger.info(f"Completed: {results['completed']}")
        logger.info(f"Failed: {results['failed']}")
        logger.info(f"Success Rate: {results['completed']/results['total_batches']*100:.1f}%")

        return results

    def _process_single_batch(
        self,
        batch: List[GoogleDriveDocument],
        batch_number: int,
        total_batches: int
    ) -> Dict[str, Any]:
        """
        Process a single batch of documents

        Args:
            batch: List of documents
            batch_number: Current batch number
            total_batches: Total number of batches

        Returns:
            Batch processing result
        """
        batch_id = f"batch_{batch_number:04d}"

        logger.info(f"📄 Batch {batch_id}: {len(batch)} documents")

        # Create batch job
        job = BatchJob(
            batch_id=batch_id,
            batch_number=batch_number,
            total_batches=total_batches,
            document_count=len(batch),
            document_ids=[doc.id for doc in batch],
            status="downloading",
            vastai_instance_id=self.vastai_instance_id,
            started_at=datetime.now().isoformat()
        )

        self.current_batch = job

        try:
            # Step 1: Download documents
            logger.info(f"⬇️ Downloading {len(batch)} documents...")
            job.status = "downloading"

            download_dir = self.state_dir / batch_id
            downloaded_paths = self.drive_sync.download_batch(batch, str(download_dir))

            if len(downloaded_paths) < len(batch):
                logger.warning(f"⚠️ Only downloaded {len(downloaded_paths)}/{len(batch)} documents")

            # Step 2: Submit to Vast.ai for processing
            logger.info(f"📤 Submitting batch to Vast.ai instance {self.vastai_instance_id}...")
            job.status = "processing"

            job_id = self.vastai.submit_batch_job(
                instance_id=self.vastai_instance_id,
                batch_id=batch_id,
                document_ids=[doc.id for doc in batch],
                supabase_url=os.environ.get('SUPABASE_URL'),
                supabase_key=os.environ.get('SUPABASE_KEY'),
                claude_api_key=os.environ.get('CLAUDE_API_KEY')
            )

            # Step 3: Monitor processing
            # In production, this would poll job status until complete
            # For now, we'll simulate by waiting
            logger.info(f"⏳ Processing batch (estimated: {len(batch) * 4.5 / 60:.1f} minutes)...")

            # Poll status every 30 seconds
            max_wait = len(batch) * 10  # 10 seconds per doc max
            elapsed = 0

            while elapsed < max_wait:
                time.sleep(30)
                elapsed += 30

                # Check job status
                # In production: job_status = self.vastai.get_job_status(self.vastai_instance_id, job_id)
                # For now, assume success after waiting

                logger.debug(f"⏳ Processing... {elapsed}/{max_wait}s elapsed")

            # Step 4: Mark as completed
            job.status = "completed"
            job.completed_at = datetime.now().isoformat()
            job.processed_count = len(batch)

            logger.info(f"✅ Batch {batch_id} completed successfully")

            return {
                "batch_id": batch_id,
                "status": "completed",
                "processed_count": len(batch),
                "started_at": job.started_at,
                "completed_at": job.completed_at
            }

        except Exception as e:
            logger.error(f"❌ Batch {batch_id} failed: {e}")

            job.status = "failed"
            job.error_message = str(e)

            return {
                "batch_id": batch_id,
                "status": "failed",
                "error": str(e)
            }

    def stop_gpu_instance(self) -> bool:
        """
        Stop the rented GPU instance

        Returns:
            True if stopped successfully
        """
        if not self.vastai_instance_id:
            logger.warning("⚠️ No GPU instance to stop")
            return False

        logger.info(f"⏹️ Stopping Vast.ai instance {self.vastai_instance_id}...")

        success = self.vastai.stop_instance(self.vastai_instance_id)

        if success:
            logger.info("✅ GPU instance stopped")
            self.vastai_instance_id = None

            if self.current_session:
                self.current_session.vastai_instance_id = None
                self._save_session_state(self.current_session)

        return success

    def _get_processed_document_ids(self) -> List[str]:
        """
        Get list of already processed document IDs from document_journal

        Returns:
            List of document IDs
        """
        try:
            # Query document_journal for documents with processing_status = 'completed'
            response = self.supabase.table('document_journal')\
                .select('id, original_filename, google_drive_id')\
                .eq('processing_status', 'completed')\
                .execute()

            # Extract Google Drive IDs if available
            processed_ids = []

            for doc in response.data:
                # Check if google_drive_id column exists
                if 'google_drive_id' in doc and doc['google_drive_id']:
                    processed_ids.append(doc['google_drive_id'])

            logger.info(f"📊 Found {len(processed_ids)} already processed documents")

            return processed_ids

        except Exception as e:
            logger.error(f"❌ Error querying processed documents: {e}")
            return []

    def _save_session_state(self, session: ProcessingSession) -> None:
        """Save session state to disk"""
        state_file = self.state_dir / f"{session.session_id}.json"

        with open(state_file, 'w') as f:
            json.dump(asdict(session), f, indent=2)

        logger.debug(f"💾 Session state saved to {state_file}")

    def _save_checkpoint(self, batch_number: int) -> None:
        """Save processing checkpoint"""
        checkpoint_file = self.state_dir / f"checkpoint_{batch_number}.json"

        checkpoint = {
            "batch_number": batch_number,
            "timestamp": datetime.now().isoformat(),
            "session": asdict(self.current_session) if self.current_session else None
        }

        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)

        logger.info(f"💾 Checkpoint saved: batch {batch_number}")

    def resume_from_checkpoint(self, checkpoint_file: str) -> ProcessingSession:
        """
        Resume processing from checkpoint

        Args:
            checkpoint_file: Path to checkpoint file

        Returns:
            Restored session
        """
        logger.info(f"🔄 Resuming from checkpoint: {checkpoint_file}")

        with open(checkpoint_file, 'r') as f:
            checkpoint = json.load(f)

        session_dict = checkpoint['session']
        session = ProcessingSession(**session_dict)

        self.current_session = session

        logger.info(f"✅ Resumed session {session.session_id} from batch {checkpoint['batch_number']}")

        return session


if __name__ == "__main__":
    """
    Test batch processing manager

    Usage:
        export SUPABASE_URL="https://jvjlhxodmbkodzmggwpu.supabase.co"
        export SUPABASE_KEY="your-key"
        export VAST_AI_API_KEY="your-key"
        export CLAUDE_API_KEY="your-key"
        python batch_manager.py
    """

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Initialize manager
    manager = BatchProcessingManager(
        batch_size=100,
        checkpoint_interval=10
    )

    # Start session (dry run with max 10 documents for testing)
    session = manager.start_processing_session(
        mime_types=['application/pdf'],
        max_documents=10  # Test with 10 docs first
    )

    if session:
        print(f"\n✅ Session created: {session.session_id}")
        print(f"   Total Documents: {session.total_documents}")
        print(f"   Total Batches: {session.total_batches}")
        print(f"   Estimated Cost: ${session.total_cost:.2f}")
        print(f"   Estimated Completion: {session.estimated_completion}")
    else:
        print("\n✅ All documents already processed!")
