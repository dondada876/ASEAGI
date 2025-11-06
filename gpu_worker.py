#!/usr/bin/env python3
"""
Vast.ai GPU Worker
Processes documents from Redis queue with GPU acceleration
"""

import os
import time
import redis
import json
from pathlib import Path
from typing import Dict, Optional
import logging

try:
    from supabase import create_client
except ImportError:
    print("[ERROR] Supabase not installed")
    exit(1)

from tiered_deduplicator import TieredDeduplicator
from document_extractor import DocumentExtractor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '')
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

# Initialize services
redis_client = redis.from_url(REDIS_URL, password=REDIS_PASSWORD, decode_responses=True)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

deduplicator = TieredDeduplicator(
    supabase_url=SUPABASE_URL,
    supabase_key=SUPABASE_KEY,
    openai_key=OPENAI_API_KEY
)

extractor = DocumentExtractor()

# Temp directory
TEMP_DIR = Path("/app/temp")
TEMP_DIR.mkdir(exist_ok=True)


class GPUWorker:
    """GPU-accelerated document processing worker"""

    def __init__(self):
        self.worker_id = os.environ.get('HOSTNAME', 'gpu-worker-1')
        self.processed_count = 0
        self.error_count = 0
        self.start_time = time.time()

    def process_job(self, job_data: Dict) -> Dict:
        """
        Process a single document job

        Job data format:
        {
            "job_id": "uuid",
            "file_url": "supabase storage url",
            "file_name": "document.pdf",
            "source": "mobile"
        }
        """
        job_id = job_data['job_id']
        file_url = job_data['file_url']
        file_name = job_data['file_name']

        logger.info(f"[{job_id}] Processing: {file_name}")

        try:
            # Step 1: Download file from Supabase
            logger.info(f"[{job_id}] Downloading file...")
            temp_file = TEMP_DIR / f"{job_id}_{file_name}"

            # Download file (simplified - add actual download logic)
            # For now, assume file_url is a local path or implement download

            # Step 2: Run tiered deduplication
            logger.info(f"[{job_id}] Checking for duplicates...")
            dup_result = deduplicator.check_duplicate(
                filename=file_name,
                file_path=str(temp_file)
            )

            if dup_result.is_duplicate:
                logger.info(f"[{job_id}] ⚠️  Duplicate detected ({dup_result.match_type})")

                return {
                    "status": "duplicate",
                    "match_type": dup_result.match_type,
                    "similarity": dup_result.similarity,
                    "matched_document_id": dup_result.matched_document.get('id') if dup_result.matched_document else None
                }

            # Step 3: Extract text and metadata
            logger.info(f"[{job_id}] Extracting content...")
            extracted = extractor.extract_document(str(temp_file))

            if not extracted['extraction_success']:
                raise Exception(extracted.get('extraction_error', 'Unknown extraction error'))

            # Step 4: AI Analysis (with Claude)
            logger.info(f"[{job_id}] Running AI analysis...")
            analysis = self.run_ai_analysis(extracted['content'])

            # Step 5: Store in Supabase
            logger.info(f"[{job_id}] Storing results...")
            doc_data = {
                'file_name': file_name,
                'file_type': extracted['metadata']['file_type'],
                'file_size': extracted['metadata']['file_size'],
                'file_hash': extracted['metadata']['file_hash'],
                'content': extracted['content'],
                'word_count': extracted['metadata']['word_count'],
                'processing_status': 'complete',
                'truth_score': analysis['truth_score'],
                'justice_score': analysis['justice_score'],
                'legal_credit_score': analysis['legal_credit_score'],
                'fraud_score': analysis['fraud_score'],
                'relevancy_number': analysis['relevancy_number']
            }

            result = supabase.table('master_document_registry')\
                .insert(doc_data)\
                .execute()

            # Clean up temp file
            temp_file.unlink()

            logger.info(f"[{job_id}] ✅ Complete")

            return {
                "status": "success",
                "document_id": result.data[0]['id'],
                "scores": {
                    "truth_score": analysis['truth_score'],
                    "justice_score": analysis['justice_score'],
                    "legal_credit_score": analysis['legal_credit_score']
                }
            }

        except Exception as e:
            logger.error(f"[{job_id}] ❌ Error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def run_ai_analysis(self, content: str) -> Dict:
        """
        Run AI analysis on document content
        (Simplified - integrate with actual scoring functions)
        """

        # Placeholder - replace with actual scoring logic
        return {
            'truth_score': 85,
            'justice_score': 90,
            'legal_credit_score': 750,
            'fraud_score': 15,
            'relevancy_number': 850
        }

    def run(self):
        """Main worker loop"""

        logger.info(f"🚀 GPU Worker started: {self.worker_id}")
        logger.info(f"   Redis: {REDIS_URL}")
        logger.info(f"   Supabase: {SUPABASE_URL}")
        logger.info("")

        # Health check endpoint (simple HTTP server)
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import threading

        class HealthHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/health':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "status": "healthy",
                        "worker_id": self.server.worker_id,
                        "processed": self.server.processed_count,
                        "errors": self.server.error_count,
                        "uptime": time.time() - self.server.start_time
                    }).encode())

        health_server = HTTPServer(('0.0.0.0', 8080), HealthHandler)
        health_server.worker_id = self.worker_id
        health_server.processed_count = self.processed_count
        health_server.error_count = self.error_count
        health_server.start_time = self.start_time

        health_thread = threading.Thread(target=health_server.serve_forever, daemon=True)
        health_thread.start()

        # Main processing loop
        while True:
            try:
                # Block and wait for job from queue
                job_raw = redis_client.blpop('aseagi:jobs', timeout=5)

                if job_raw is None:
                    # No jobs, check if we should shutdown
                    idle_time = time.time() - self.start_time

                    # Auto-shutdown after 5 minutes of idle (save costs)
                    if self.processed_count == 0 and idle_time > 300:
                        logger.info("⚠️  No jobs for 5 minutes, shutting down to save costs")
                        break

                    continue

                # Parse job
                _, job_json = job_raw
                job_data = json.loads(job_json)

                # Process job
                result = self.process_job(job_data)

                # Update stats
                if result['status'] == 'success':
                    self.processed_count += 1
                else:
                    self.error_count += 1

                # Store result in Redis
                result_key = f"aseagi:result:{job_data['job_id']}"
                redis_client.setex(result_key, 3600, json.dumps(result))  # 1 hour TTL

                # Update health server stats
                health_server.processed_count = self.processed_count
                health_server.error_count = self.error_count

            except KeyboardInterrupt:
                logger.info("⚠️  Shutting down gracefully...")
                break

            except Exception as e:
                logger.error(f"Worker error: {e}")
                self.error_count += 1
                time.sleep(1)

        logger.info(f"👋 Worker stopped. Processed: {self.processed_count}, Errors: {self.error_count}")


if __name__ == "__main__":
    worker = GPUWorker()
    worker.run()
