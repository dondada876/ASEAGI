"""
ASEAGI Vast.ai Worker
GPU-accelerated document processing worker
Pulls jobs from queue, processes, uploads results, auto-destroys when idle
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from pathlib import Path
import subprocess

from supabase import create_client, Client
import boto3
import redis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
S3_ENDPOINT = os.getenv("S3_ENDPOINT")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_REGION = os.getenv("S3_REGION", "nyc3")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
IDLE_TIMEOUT = int(os.getenv("IDLE_TIMEOUT", "300"))  # 5 minutes default

# Validate environment
required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "S3_ENDPOINT",
                "S3_ACCESS_KEY", "S3_SECRET_KEY", "S3_BUCKET"]
missing = [v for v in required_vars if not os.getenv(v)]
if missing:
    logger.error(f"Missing required environment variables: {missing}")
    sys.exit(1)

# Initialize clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
s3_client = boto3.client(
    's3',
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION
)

# Import processing function
from process_document import process_document


class VastWorker:
    """Vast.ai GPU worker"""

    def __init__(self):
        self.instance_id = os.getenv("VAST_INSTANCE_ID", "unknown")
        self.last_job_time = time.time()
        self.jobs_processed = 0

    def get_job_from_queue(self) -> dict:
        """Get next job from Supabase queue"""
        try:
            # Get oldest queued job
            result = supabase.table('processing_jobs')\
                .select('*')\
                .eq('status', 'queued')\
                .order('created_at')\
                .limit(1)\
                .execute()

            if result.data:
                job = result.data[0]

                # Update status to processing
                supabase.table('processing_jobs')\
                    .update({
                        'status': 'processing',
                        'started_at': datetime.utcnow().isoformat(),
                        'worker_id': self.instance_id
                    })\
                    .eq('job_id', job['job_id'])\
                    .execute()

                logger.info(f"Retrieved job: {job['job_id']}")
                return job
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to get job: {e}")
            return None

    def download_from_s3(self, s3_key: str, local_path: str) -> bool:
        """Download file from S3"""
        try:
            s3_client.download_file(S3_BUCKET, s3_key, local_path)
            logger.info(f"Downloaded: {s3_key} -> {local_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download {s3_key}: {e}")
            return False

    def upload_to_s3(self, local_path: str, s3_key: str) -> bool:
        """Upload file to S3"""
        try:
            s3_client.upload_file(local_path, S3_BUCKET, s3_key)
            logger.info(f"Uploaded: {local_path} -> {s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload {s3_key}: {e}")
            return False

    def process_job(self, job: dict) -> bool:
        """Process a single job"""
        job_id = job['job_id']
        file_path = job['file_path']

        try:
            logger.info(f"Processing job {job_id}: {file_path}")

            # Create temp directory
            temp_dir = Path("/tmp/processing")
            temp_dir.mkdir(exist_ok=True)

            # Download file from S3
            local_file = temp_dir / Path(file_path).name
            if not self.download_from_s3(file_path, str(local_file)):
                raise Exception("Failed to download file")

            # Process document (calls process_document.py)
            result = process_document(str(local_file))

            if not result:
                raise Exception("Processing failed")

            # Upload processed results to S3
            processed_key = file_path.replace('/raw/', '/processed/')
            result_file = temp_dir / f"{local_file.stem}_result.json"

            with open(result_file, 'w') as f:
                json.dump(result, f)

            if not self.upload_to_s3(str(result_file), processed_key):
                raise Exception("Failed to upload results")

            # Update Supabase with results
            supabase.table('processing_jobs').update({
                'status': 'completed',
                'completed_at': datetime.utcnow().isoformat(),
                'result': result
            }).eq('job_id', job_id).execute()

            # Insert into legal_documents table
            supabase.table('legal_documents').insert({
                'file_name': Path(file_path).name,
                's3_path': file_path,
                'extracted_text': result.get('text', ''),
                'category': result.get('category', ''),
                'relevancy_number': result.get('relevancy_number', 0),
                'macro_score': result.get('macro_score', 0),
                'legal_score': result.get('legal_score', 0),
                'micro_score': result.get('micro_score', 0),
                'category_score': result.get('category_score', 0),
                'metadata': job.get('metadata', {}),
                'created_at': datetime.utcnow().isoformat()
            }).execute()

            # Clean up
            local_file.unlink(missing_ok=True)
            result_file.unlink(missing_ok=True)

            logger.info(f"✅ Job {job_id} completed successfully")
            self.jobs_processed += 1
            self.last_job_time = time.time()

            return True

        except Exception as e:
            logger.error(f"❌ Job {job_id} failed: {e}")

            # Update job status to error
            supabase.table('processing_jobs').update({
                'status': 'error',
                'completed_at': datetime.utcnow().isoformat(),
                'error': str(e)
            }).eq('job_id', job_id).execute()

            return False

    def check_idle_timeout(self) -> bool:
        """Check if worker has been idle too long"""
        idle_time = time.time() - self.last_job_time
        return idle_time > IDLE_TIMEOUT

    def self_destruct(self):
        """Destroy this Vast.ai instance"""
        logger.info("🔥 No jobs for 5 minutes, self-destructing...")

        # Update Supabase
        supabase.table('vastai_instances').update({
            'status': 'auto_destroyed',
            'destroyed_at': datetime.utcnow().isoformat(),
            'jobs_processed': self.jobs_processed
        }).eq('instance_id', self.instance_id).execute()

        # Destroy instance using Vast.ai CLI
        try:
            subprocess.run(['vastai', 'destroy', 'instance', self.instance_id], check=True)
            logger.info("Instance destroyed successfully")
        except Exception as e:
            logger.error(f"Failed to destroy instance: {e}")
            # Exit anyway - instance will be destroyed manually
            sys.exit(0)

    def run(self):
        """Main worker loop"""
        logger.info(f"🚀 Worker started (Instance: {self.instance_id})")

        while True:
            # Get next job
            job = self.get_job_from_queue()

            if job:
                # Process job
                self.process_job(job)
            else:
                # No jobs available
                logger.info("No jobs in queue, waiting...")

                # Check if idle too long
                if self.check_idle_timeout():
                    self.self_destruct()
                    break

                # Wait 30 seconds before checking again
                time.sleep(30)


if __name__ == "__main__":
    worker = VastWorker()
    worker.run()
