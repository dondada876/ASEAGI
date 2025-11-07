"""
Vast.ai API Client
Manages GPU instance rental and job submission for batch document processing
"""

import os
import requests
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


@dataclass
class GPUInstance:
    """Represents a Vast.ai GPU instance"""
    id: int
    status: str  # "running", "stopped", "loading"
    gpu_name: str
    gpu_ram: int
    cpu_cores: int
    ram_gb: int
    disk_space: int
    cost_per_hour: float
    ssh_host: str
    ssh_port: int


@dataclass
class BatchJob:
    """Represents a batch processing job"""
    job_id: str
    instance_id: int
    batch_number: int
    total_documents: int
    processed_documents: int
    status: str  # "pending", "running", "completed", "failed"
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None


class VastAIClient:
    """
    Client for Vast.ai API

    Manages GPU instance lifecycle and job submission for processing
    7TB of documents from Google Drive.

    Target specs:
    - RTX 4090 or A100 GPU
    - 24GB+ VRAM
    - $0.50-1.00/hour
    - Process 100 docs per batch
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Vast.ai client

        Args:
            api_key: Vast.ai API key (or from VAST_AI_API_KEY env var)
        """
        self.api_key = api_key or os.environ.get('VAST_AI_API_KEY')
        if not self.api_key:
            raise ValueError("VAST_AI_API_KEY must be provided or set in environment")

        self.base_url = "https://console.vast.ai/api/v0"
        self.headers = {
            "Accept": "application/json",
        }

        logger.info("✅ Vast.ai client initialized")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=10))
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make authenticated API request with retry logic

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for requests

        Returns:
            Response JSON
        """
        url = f"{self.base_url}{endpoint}"
        kwargs['headers'] = {**self.headers, **kwargs.get('headers', {})}

        # Add API key to params
        params = kwargs.get('params', {})
        params['api_key'] = self.api_key
        kwargs['params'] = params

        response = requests.request(method, url, **kwargs)
        response.raise_for_status()

        return response.json()

    def search_instances(
        self,
        gpu_name: Optional[str] = None,
        min_gpu_ram: int = 24,
        max_cost_per_hour: float = 1.0,
        min_disk_space: int = 100,
        verified_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for available GPU instances

        Args:
            gpu_name: Specific GPU model (e.g., "RTX_4090", "A100")
            min_gpu_ram: Minimum GPU RAM in GB
            max_cost_per_hour: Maximum hourly cost
            min_disk_space: Minimum disk space in GB
            verified_only: Only show verified hosts

        Returns:
            List of available instances
        """
        logger.info(f"🔍 Searching for GPU instances (min {min_gpu_ram}GB VRAM, max ${max_cost_per_hour}/hr)")

        # Build search query
        params = {
            "verified": verified_only,
            "rentable": True,
            "gpu_ram": min_gpu_ram * 1024,  # Convert to MB
            "disk_space": min_disk_space,
        }

        if gpu_name:
            params["gpu_name"] = gpu_name

        results = self._make_request("GET", "/bundles", params=params)

        # Filter by cost
        filtered = [
            instance for instance in results.get("offers", [])
            if instance.get("dph_total", 999) <= max_cost_per_hour
        ]

        # Sort by cost (cheapest first)
        filtered.sort(key=lambda x: x.get("dph_total", 999))

        logger.info(f"✅ Found {len(filtered)} instances matching criteria")

        return filtered

    def rent_instance(
        self,
        instance_id: int,
        image: str = "pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime",
        disk_space: int = 100,
        onstart_cmd: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Rent a GPU instance

        Args:
            instance_id: ID of instance to rent
            image: Docker image to use
            disk_space: Disk space in GB
            onstart_cmd: Command to run on instance startup

        Returns:
            Instance details
        """
        logger.info(f"💰 Renting instance {instance_id}...")

        data = {
            "client_id": "batch_processor",
            "image": image,
            "disk": disk_space,
        }

        if onstart_cmd:
            data["onstart"] = onstart_cmd

        result = self._make_request("PUT", f"/asks/{instance_id}/", json=data)

        logger.info(f"✅ Instance {instance_id} rented successfully")

        return result

    def get_instance_status(self, instance_id: int) -> str:
        """
        Get current status of rented instance

        Args:
            instance_id: Instance ID

        Returns:
            Status string: "running", "loading", "stopped"
        """
        result = self._make_request("GET", f"/instances/{instance_id}")

        status = result.get("status", "unknown")
        logger.debug(f"Instance {instance_id} status: {status}")

        return status

    def wait_for_instance_ready(self, instance_id: int, timeout: int = 600, check_interval: int = 10) -> bool:
        """
        Wait for instance to be ready (status = "running")

        Args:
            instance_id: Instance ID
            timeout: Maximum wait time in seconds
            check_interval: Check status every N seconds

        Returns:
            True if ready, False if timeout
        """
        logger.info(f"⏳ Waiting for instance {instance_id} to be ready...")

        start_time = time.time()

        while time.time() - start_time < timeout:
            status = self.get_instance_status(instance_id)

            if status == "running":
                logger.info(f"✅ Instance {instance_id} is ready!")
                return True
            elif status in ["stopped", "exited"]:
                logger.error(f"❌ Instance {instance_id} stopped unexpectedly")
                return False

            time.sleep(check_interval)

        logger.error(f"❌ Timeout waiting for instance {instance_id}")
        return False

    def submit_batch_job(
        self,
        instance_id: int,
        batch_id: str,
        document_ids: List[str],
        supabase_url: str,
        supabase_key: str,
        claude_api_key: str
    ) -> str:
        """
        Submit batch processing job to GPU instance

        Args:
            instance_id: Vast.ai instance ID
            batch_id: Unique batch identifier
            document_ids: List of document IDs to process
            supabase_url: Supabase project URL
            supabase_key: Supabase API key
            claude_api_key: Claude API key for AI processing

        Returns:
            Job ID
        """
        logger.info(f"📤 Submitting batch {batch_id} with {len(document_ids)} documents to instance {instance_id}")

        # In production, this would SSH into the instance and execute the batch processor
        # For now, we'll use the Vast.ai execute API

        job_data = {
            "batch_id": batch_id,
            "document_ids": document_ids,
            "supabase_url": supabase_url,
            "supabase_key": supabase_key,
            "claude_api_key": claude_api_key,
        }

        # Execute command on instance
        command = f"python /app/process_batch.py '{batch_id}' {len(document_ids)}"

        result = self._make_request("POST", f"/instances/{instance_id}/execute", json={
            "command": command,
            "env": job_data
        })

        job_id = result.get("job_id", batch_id)

        logger.info(f"✅ Job {job_id} submitted successfully")

        return job_id

    def get_job_status(self, instance_id: int, job_id: str) -> Dict[str, Any]:
        """
        Get status of submitted job

        Args:
            instance_id: Instance ID
            job_id: Job ID

        Returns:
            Job status details
        """
        # Query instance for job status
        # In production, this would check a status file or API endpoint

        result = self._make_request("GET", f"/instances/{instance_id}/jobs/{job_id}")

        return result

    def stop_instance(self, instance_id: int) -> bool:
        """
        Stop a running instance

        Args:
            instance_id: Instance ID

        Returns:
            True if stopped successfully
        """
        logger.info(f"⏹️ Stopping instance {instance_id}...")

        try:
            self._make_request("DELETE", f"/instances/{instance_id}")
            logger.info(f"✅ Instance {instance_id} stopped")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to stop instance {instance_id}: {e}")
            return False

    def get_account_balance(self) -> float:
        """
        Get current account balance

        Returns:
            Balance in USD
        """
        result = self._make_request("GET", "/users/current")
        balance = result.get("balance", 0.0)

        logger.info(f"💰 Current balance: ${balance:.2f}")

        return balance

    def estimate_cost(
        self,
        total_documents: int,
        batch_size: int = 100,
        cost_per_hour: float = 0.50,
        seconds_per_document: float = 4.5
    ) -> Dict[str, Any]:
        """
        Estimate processing cost

        Args:
            total_documents: Total number of documents
            batch_size: Documents per batch
            cost_per_hour: GPU cost per hour
            seconds_per_document: Estimated processing time per doc

        Returns:
            Cost estimate breakdown
        """
        total_batches = (total_documents + batch_size - 1) // batch_size
        total_seconds = total_documents * seconds_per_document
        total_hours = total_seconds / 3600
        total_cost = total_hours * cost_per_hour

        estimate = {
            "total_documents": total_documents,
            "batch_size": batch_size,
            "total_batches": total_batches,
            "total_hours": round(total_hours, 2),
            "cost_per_hour": cost_per_hour,
            "total_cost": round(total_cost, 2),
            "seconds_per_document": seconds_per_document,
        }

        logger.info(f"📊 Cost estimate: {total_documents} docs → {total_hours:.1f} hours → ${total_cost:.2f}")

        return estimate


if __name__ == "__main__":
    """
    Test Vast.ai client

    Usage:
        export VAST_AI_API_KEY="your-api-key-here"
        python vastai_client.py
    """

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize client
    client = VastAIClient()

    # Check balance
    balance = client.get_account_balance()
    print(f"\n💰 Account Balance: ${balance:.2f}")

    # Search for instances
    print("\n🔍 Searching for GPU instances...")
    instances = client.search_instances(
        min_gpu_ram=24,
        max_cost_per_hour=1.0,
        min_disk_space=100
    )

    if instances:
        print(f"\n✅ Found {len(instances)} instances:")
        for i, instance in enumerate(instances[:5]):  # Show top 5
            print(f"\n{i+1}. {instance.get('gpu_name', 'Unknown GPU')}")
            print(f"   VRAM: {instance.get('gpu_ram', 0) / 1024:.1f} GB")
            print(f"   Cost: ${instance.get('dph_total', 0):.2f}/hour")
            print(f"   CPU: {instance.get('cpu_cores', 0)} cores")
            print(f"   RAM: {instance.get('ram', 0) / 1024:.1f} GB")

    # Estimate cost for 7TB processing
    print("\n📊 Cost Estimate for 7TB Processing:")
    estimate = client.estimate_cost(
        total_documents=70000,
        batch_size=100,
        cost_per_hour=0.50,
        seconds_per_document=4.5
    )

    print(f"   Total Documents: {estimate['total_documents']:,}")
    print(f"   Batch Size: {estimate['batch_size']}")
    print(f"   Total Batches: {estimate['total_batches']}")
    print(f"   Total Hours: {estimate['total_hours']:.1f}")
    print(f"   Cost per Hour: ${estimate['cost_per_hour']:.2f}")
    print(f"   Total Cost: ${estimate['total_cost']:.2f}")
    print(f"\n✅ Well within $100 budget!")
