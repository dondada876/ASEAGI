"""
Batch Processor API Endpoints
FastAPI server for controlling batch processing operations
"""

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse

from batch_manager import BatchProcessingManager, ProcessingSession
from vastai_client import VastAIClient
from google_drive_sync import GoogleDriveSync

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ASEAGI Batch Processor API",
    description="API for orchestrating batch processing of 7TB Google Drive documents using Vast.ai GPU",
    version="1.0.0"
)

# Global batch manager instance
batch_manager: Optional[BatchProcessingManager] = None


# Request/Response Models

class StartSessionRequest(BaseModel):
    """Request to start a new batch processing session"""
    folder_id: Optional[str] = Field(None, description="Google Drive folder ID (None = root)")
    mime_types: Optional[List[str]] = Field(['application/pdf'], description="File types to process")
    max_documents: Optional[int] = Field(None, description="Maximum documents to process")
    batch_size: int = Field(100, description="Documents per batch")
    gpu_name: Optional[str] = Field(None, description="Specific GPU model (e.g., 'RTX_4090')")
    max_cost_per_hour: float = Field(1.0, description="Maximum GPU cost per hour")


class SessionStatusResponse(BaseModel):
    """Response with current session status"""
    session_id: str
    status: str
    total_documents: int
    total_batches: int
    completed_batches: int
    failed_batches: int
    progress_percentage: float
    started_at: str
    estimated_completion: Optional[str]
    vastai_instance_id: Optional[int]
    total_cost: float
    current_batch: Optional[Dict[str, Any]] = None


class GPUInstanceInfo(BaseModel):
    """GPU instance information"""
    instance_id: int
    gpu_name: str
    cost_per_hour: float
    status: str


# Startup/Shutdown Events

@app.on_event("startup")
async def startup_event():
    """Initialize batch manager on startup"""
    global batch_manager

    logger.info("🚀 Starting Batch Processor API...")

    # Check required environment variables
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'VAST_AI_API_KEY']
    missing = [var for var in required_vars if not os.environ.get(var)]

    if missing:
        logger.error(f"❌ Missing required environment variables: {missing}")
        raise RuntimeError(f"Missing environment variables: {missing}")

    # Initialize batch manager
    try:
        batch_manager = BatchProcessingManager(
            batch_size=100,
            checkpoint_interval=10
        )
        logger.info("✅ Batch manager initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize batch manager: {e}")
        raise

    logger.info("✅ Batch Processor API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("⏹️ Shutting down Batch Processor API...")

    # Stop GPU instance if running
    if batch_manager and batch_manager.vastai_instance_id:
        logger.info("🛑 Stopping GPU instance...")
        batch_manager.stop_gpu_instance()

    logger.info("✅ Batch Processor API shut down")


# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "batch_manager_initialized": batch_manager is not None,
        "current_session": batch_manager.current_session.session_id if batch_manager and batch_manager.current_session else None
    }


@app.post("/batch/start", response_model=SessionStatusResponse)
async def start_batch_session(
    request: StartSessionRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a new batch processing session

    This will:
    1. List documents from Google Drive
    2. Filter out already processed documents
    3. Estimate cost
    4. Rent GPU instance
    5. Start processing batches in background
    """
    if not batch_manager:
        raise HTTPException(status_code=500, detail="Batch manager not initialized")

    if batch_manager.current_session and batch_manager.current_session.status == "running":
        raise HTTPException(
            status_code=409,
            detail=f"Session {batch_manager.current_session.session_id} is already running"
        )

    logger.info("📋 Starting new batch processing session...")

    try:
        # Start session
        session = batch_manager.start_processing_session(
            folder_id=request.folder_id,
            mime_types=request.mime_types,
            max_documents=request.max_documents
        )

        if not session:
            return JSONResponse(
                status_code=200,
                content={
                    "message": "All documents already processed",
                    "status": "complete"
                }
            )

        # Rent GPU instance
        logger.info("💰 Renting GPU instance...")
        instance_id = batch_manager.rent_gpu_instance(
            gpu_name=request.gpu_name,
            max_cost_per_hour=request.max_cost_per_hour
        )

        logger.info(f"✅ GPU instance {instance_id} rented")

        # Start processing in background
        # background_tasks.add_task(run_batch_processing)

        return SessionStatusResponse(
            session_id=session.session_id,
            status=session.status,
            total_documents=session.total_documents,
            total_batches=session.total_batches,
            completed_batches=session.completed_batches,
            failed_batches=session.failed_batches,
            progress_percentage=0.0,
            started_at=session.started_at,
            estimated_completion=session.estimated_completion,
            vastai_instance_id=instance_id,
            total_cost=session.total_cost
        )

    except Exception as e:
        logger.error(f"❌ Failed to start session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/batch/status", response_model=SessionStatusResponse)
async def get_batch_status():
    """Get current batch processing status"""
    if not batch_manager:
        raise HTTPException(status_code=500, detail="Batch manager not initialized")

    if not batch_manager.current_session:
        raise HTTPException(status_code=404, detail="No active session")

    session = batch_manager.current_session

    progress = (session.completed_batches / session.total_batches * 100) if session.total_batches > 0 else 0

    current_batch = None
    if batch_manager.current_batch:
        current_batch = {
            "batch_id": batch_manager.current_batch.batch_id,
            "batch_number": batch_manager.current_batch.batch_number,
            "document_count": batch_manager.current_batch.document_count,
            "processed_count": batch_manager.current_batch.processed_count,
            "status": batch_manager.current_batch.status
        }

    return SessionStatusResponse(
        session_id=session.session_id,
        status=session.status,
        total_documents=session.total_documents,
        total_batches=session.total_batches,
        completed_batches=session.completed_batches,
        failed_batches=session.failed_batches,
        progress_percentage=round(progress, 2),
        started_at=session.started_at,
        estimated_completion=session.estimated_completion,
        vastai_instance_id=session.vastai_instance_id,
        total_cost=session.total_cost,
        current_batch=current_batch
    )


@app.post("/batch/stop")
async def stop_batch_session():
    """Stop current batch processing session"""
    if not batch_manager:
        raise HTTPException(status_code=500, detail="Batch manager not initialized")

    if not batch_manager.current_session:
        raise HTTPException(status_code=404, detail="No active session")

    logger.info("🛑 Stopping batch processing session...")

    try:
        # Stop GPU instance
        if batch_manager.vastai_instance_id:
            success = batch_manager.stop_gpu_instance()
            if not success:
                logger.warning("⚠️ Failed to stop GPU instance")

        # Update session status
        if batch_manager.current_session:
            batch_manager.current_session.status = "stopped"
            batch_manager._save_session_state(batch_manager.current_session)

        logger.info("✅ Session stopped")

        return {"message": "Session stopped successfully"}

    except Exception as e:
        logger.error(f"❌ Failed to stop session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/batch/estimate")
async def estimate_batch_cost(
    total_documents: int = 70000,
    batch_size: int = 100,
    cost_per_hour: float = 0.50
):
    """
    Estimate batch processing cost

    Args:
        total_documents: Total documents to process
        batch_size: Documents per batch
        cost_per_hour: GPU cost per hour
    """
    if not batch_manager:
        raise HTTPException(status_code=500, detail="Batch manager not initialized")

    estimate = batch_manager.vastai.estimate_cost(
        total_documents=total_documents,
        batch_size=batch_size,
        cost_per_hour=cost_per_hour
    )

    return estimate


@app.get("/vastai/balance")
async def get_vastai_balance():
    """Get current Vast.ai account balance"""
    if not batch_manager:
        raise HTTPException(status_code=500, detail="Batch manager not initialized")

    try:
        balance = batch_manager.vastai.get_account_balance()

        return {
            "balance": balance,
            "currency": "USD"
        }

    except Exception as e:
        logger.error(f"❌ Failed to get balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/vastai/instances")
async def search_gpu_instances(
    gpu_name: Optional[str] = None,
    min_gpu_ram: int = 24,
    max_cost_per_hour: float = 1.0
):
    """
    Search for available GPU instances

    Args:
        gpu_name: Specific GPU model (e.g., 'RTX_4090')
        min_gpu_ram: Minimum GPU RAM in GB
        max_cost_per_hour: Maximum hourly cost
    """
    if not batch_manager:
        raise HTTPException(status_code=500, detail="Batch manager not initialized")

    try:
        instances = batch_manager.vastai.search_instances(
            gpu_name=gpu_name,
            min_gpu_ram=min_gpu_ram,
            max_cost_per_hour=max_cost_per_hour
        )

        # Format response
        formatted = []
        for inst in instances[:10]:  # Limit to top 10
            formatted.append({
                "id": inst.get('id'),
                "gpu_name": inst.get('gpu_name'),
                "gpu_ram_gb": inst.get('gpu_ram', 0) / 1024,
                "cpu_cores": inst.get('cpu_cores'),
                "ram_gb": inst.get('ram', 0) / 1024,
                "cost_per_hour": inst.get('dph_total', 0),
                "disk_space_gb": inst.get('disk_space', 0)
            })

        return {
            "total_found": len(instances),
            "showing": len(formatted),
            "instances": formatted
        }

    except Exception as e:
        logger.error(f"❌ Failed to search instances: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/drive/documents")
async def list_drive_documents(
    folder_id: Optional[str] = None,
    max_results: int = 100
):
    """
    List documents from Google Drive

    Args:
        folder_id: Specific folder ID (None = root)
        max_results: Maximum documents to return
    """
    if not batch_manager:
        raise HTTPException(status_code=500, detail="Batch manager not initialized")

    try:
        # Authenticate if needed
        if not batch_manager.drive_sync.service:
            batch_manager.drive_sync.authenticate()

        # List documents
        documents = batch_manager.drive_sync.list_documents(
            folder_id=folder_id,
            mime_types=['application/pdf'],
            max_results=max_results,
            recursive=False
        )

        # Format response
        formatted = []
        for doc in documents:
            formatted.append({
                "id": doc.id,
                "name": doc.name,
                "size_mb": round(doc.size / (1024 * 1024), 2),
                "modified_time": doc.modified_time,
                "web_view_link": doc.web_view_link
            })

        return {
            "total_documents": len(formatted),
            "documents": formatted
        }

    except Exception as e:
        logger.error(f"❌ Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/checkpoints")
async def list_checkpoints():
    """List available processing checkpoints"""
    if not batch_manager:
        raise HTTPException(status_code=500, detail="Batch manager not initialized")

    state_dir = Path("batch_state")

    if not state_dir.exists():
        return {"checkpoints": []}

    checkpoint_files = list(state_dir.glob("checkpoint_*.json"))

    checkpoints = []
    for file in sorted(checkpoint_files):
        import json
        with open(file, 'r') as f:
            data = json.load(f)

        checkpoints.append({
            "file": file.name,
            "batch_number": data.get('batch_number'),
            "timestamp": data.get('timestamp'),
            "session_id": data.get('session', {}).get('session_id')
        })

    return {"checkpoints": checkpoints}


@app.post("/batch/resume/{checkpoint_file}")
async def resume_from_checkpoint(checkpoint_file: str):
    """
    Resume processing from a checkpoint

    Args:
        checkpoint_file: Checkpoint filename (e.g., 'checkpoint_100.json')
    """
    if not batch_manager:
        raise HTTPException(status_code=500, detail="Batch manager not initialized")

    checkpoint_path = Path("batch_state") / checkpoint_file

    if not checkpoint_path.exists():
        raise HTTPException(status_code=404, detail=f"Checkpoint {checkpoint_file} not found")

    try:
        session = batch_manager.resume_from_checkpoint(str(checkpoint_path))

        return {
            "message": "Session resumed successfully",
            "session_id": session.session_id,
            "completed_batches": session.completed_batches,
            "total_batches": session.total_batches
        }

    except Exception as e:
        logger.error(f"❌ Failed to resume from checkpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Run server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api_endpoints:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
