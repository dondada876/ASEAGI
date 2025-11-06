#!/usr/bin/env python3
"""
Mobile Scanner FastAPI Backend
Provides API endpoints for mobile phone document scanning
"""

import os
import io
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from fastapi import FastAPI, File, UploadFile, Form, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
except ImportError:
    print("[ERROR] FastAPI not installed")
    print("Run: pip install fastapi uvicorn python-multipart")
    exit(1)

try:
    from PIL import Image
    import pytesseract
except ImportError:
    print("[ERROR] PIL/Tesseract not installed")
    print("Run: pip install Pillow pytesseract")
    exit(1)

try:
    from supabase import create_client
except ImportError:
    print("[ERROR] Supabase not installed")
    print("Run: pip install supabase")
    exit(1)

from tiered_deduplicator import TieredDeduplicator
from queue_manager import QueueManager, DocumentSubmission


# Initialize FastAPI
app = FastAPI(
    title="ASEAGI Mobile Scanner API",
    description="Document scanning API with smart deduplication",
    version="1.0.0"
)

# Enable CORS for mobile access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for mobile access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get credentials from environment
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://jvjlhxodmbkodzmggwpu.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')
OPENAI_KEY = os.environ.get('OPENAI_API_KEY', '')

# Initialize services
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_KEY else None
deduplicator = TieredDeduplicator(SUPABASE_URL, SUPABASE_KEY, OPENAI_KEY) if SUPABASE_KEY else None
queue_manager = QueueManager(SUPABASE_URL, SUPABASE_KEY, OPENAI_KEY) if SUPABASE_KEY else None

# Temp directory for uploads
UPLOAD_DIR = Path("mobile_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve mobile scanner web app"""
    html_file = Path(__file__).parent / "mobile_scanner.html"
    if html_file.exists():
        return html_file.read_text()
    return """
    <html>
        <body>
            <h1>🛡️ ASEAGI Mobile Scanner API</h1>
            <p>API is running!</p>
            <ul>
                <li><a href="/docs">API Documentation</a></li>
                <li><a href="/health">Health Check</a></li>
            </ul>
        </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "supabase": "connected" if supabase else "not configured",
        "deduplicator": "ready" if deduplicator else "not configured",
        "queue_manager": "ready" if queue_manager else "not configured",
        "openai": "configured" if OPENAI_KEY else "not configured"
    }


@app.post("/api/upload")
async def upload_document(
    file: UploadFile = File(...),
    source: str = Form("mobile"),
    source_device: Optional[str] = Form(None),
    source_user_id: Optional[str] = Form(None)
):
    """
    Upload document from mobile phone
    - Adds to universal journal
    - Runs assessment phase (duplicate detection, type detection, rules)
    - Queues for processing if approved
    - Returns assessment result
    """

    if not queue_manager:
        raise HTTPException(status_code=500, detail="Queue Manager not configured")

    # Read file
    contents = await file.read()

    # Save to permanent storage (not temp - needed for processing)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    upload_path = UPLOAD_DIR / f"{source}_{timestamp}_{file.filename}"
    upload_path.write_bytes(contents)

    try:
        # Create document submission
        submission = DocumentSubmission(
            file_path=str(upload_path),
            original_filename=file.filename,
            source_type=source,
            source_device=source_device,
            source_user_id=source_user_id
        )

        # Submit to queue manager (runs assessment phase)
        assessment = queue_manager.submit_document(submission)

        # Build response based on assessment
        response_data = {
            "journal_id": assessment.journal_id,
            "should_process": assessment.should_process,
            "reason": assessment.reason,
            "document_type": assessment.document_type,
            "priority": assessment.priority
        }

        # If duplicate, include duplicate info
        if assessment.is_duplicate:
            response_data.update({
                "status": "duplicate",
                "is_duplicate": True,
                "duplicate_tier": assessment.duplicate_tier,
                "duplicate_of": assessment.duplicate_of,
                "message": f"⚠️ Duplicate detected: {assessment.reason}"
            })
        elif assessment.should_process:
            response_data.update({
                "status": "queued",
                "is_duplicate": False,
                "message": f"✅ Added to processing queue (priority {assessment.priority})"
            })
        else:
            response_data.update({
                "status": "skipped",
                "is_duplicate": False,
                "message": f"⏭️ Skipped: {assessment.reason}"
            })

        return JSONResponse(response_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/check-duplicate")
async def check_duplicate(
    text: str = Form(...),
    filename: Optional[str] = Form(None)
):
    """
    Check if text content is a duplicate
    Returns similarity score and matched document if found
    """

    if not deduplicator:
        raise HTTPException(status_code=500, detail="Deduplicator not configured")

    try:
        # For text-only check, we can only use Tier 2 (semantic)
        if OPENAI_KEY and text:
            result = deduplicator.tier2_semantic_check(text, threshold=0.95)

            return {
                "is_duplicate": result.is_duplicate,
                "match_type": result.match_type,
                "similarity": result.similarity,
                "matched_document": result.matched_document
            }
        else:
            # Fallback to Tier 1 if no OpenAI key
            return {
                "is_duplicate": False,
                "match_type": "none",
                "similarity": 0.0,
                "message": "OpenAI key not configured, cannot check semantics"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats():
    """Get deduplication statistics"""

    if not deduplicator:
        raise HTTPException(status_code=500, detail="Deduplicator not configured")

    return {
        "stats": deduplicator.stats,
        "total_checks": deduplicator.stats['tier0_checks'],
        "total_duplicates": (
            deduplicator.stats['tier0_duplicates'] +
            deduplicator.stats['tier1_duplicates'] +
            deduplicator.stats['tier2_duplicates']
        ),
        "new_documents": deduplicator.stats['new_documents']
    }


@app.get("/api/documents")
async def list_documents(
    limit: int = 10,
    status: Optional[str] = None
):
    """List documents from master registry"""

    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    try:
        query = supabase.table('master_document_registry')\
            .select('*')

        if status:
            query = query.eq('processing_status', status)

        result = query.order('first_discovered', desc=True)\
            .limit(limit)\
            .execute()

        return {
            "documents": result.data,
            "count": len(result.data)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/queue/stats")
async def get_queue_stats():
    """Get queue statistics from journal and processing queue"""

    if not queue_manager:
        raise HTTPException(status_code=500, detail="Queue Manager not configured")

    try:
        # Get queue stats
        stats = queue_manager.get_queue_stats()

        # Get processing performance
        performance = queue_manager.get_processing_performance()

        return {
            "queue_stats": stats,
            "processing_performance": performance,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/queue/items")
async def get_queue_items(
    status: Optional[str] = None,
    limit: int = 50
):
    """Get items from document journal"""

    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    try:
        query = supabase.table('document_journal')\
            .select('*')

        if status:
            query = query.eq('queue_status', status)

        result = query.order('date_logged', desc=True)\
            .limit(limit)\
            .execute()

        return {
            "items": result.data,
            "count": len(result.data)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/queue/dashboard")
async def get_queue_dashboard():
    """Get dashboard view of queue"""

    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    try:
        # Use the view created in schema
        result = supabase.table('queue_dashboard')\
            .select('*')\
            .execute()

        return {
            "dashboard": result.data,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/manifest.json")
async def manifest():
    """PWA manifest for mobile installation"""
    return {
        "name": "ASEAGI Document Scanner",
        "short_name": "ASEAGI Scanner",
        "description": "Mobile document scanner with smart deduplication",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#000000",
        "theme_color": "#007AFF",
        "icons": [
            {
                "src": "/icon-192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "/icon-512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }


def get_local_ip():
    """Get local IP address for mobile access"""
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


if __name__ == "__main__":
    import uvicorn

    # Get local IP
    local_ip = get_local_ip()

    print()
    print("=" * 80)
    print("ASEAGI MOBILE SCANNER API")
    print("=" * 80)
    print()
    print(f"🖥️  Local access: http://localhost:8000")
    print(f"📱 Mobile access: http://{local_ip}:8000")
    print()
    print("API Endpoints:")
    print(f"  📄 Docs: http://{local_ip}:8000/docs")
    print(f"  ✅ Health: http://{local_ip}:8000/health")
    print(f"  📤 Upload: http://{local_ip}:8000/api/upload")
    print()
    print("Configuration:")
    print(f"  Supabase: {'✅ Connected' if supabase else '❌ Not configured'}")
    print(f"  OpenAI: {'✅ Configured' if OPENAI_KEY else '❌ Not configured'}")
    print(f"  Deduplicator: {'✅ Ready' if deduplicator else '❌ Not configured'}")
    print()
    print("On your phone:")
    print(f"  1. Open: http://{local_ip}:8000")
    print(f"  2. Tap 'Add to Home Screen'")
    print(f"  3. Start scanning!")
    print()
    print("=" * 80)
    print()

    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",  # Listen on all interfaces for mobile access
        port=8000,
        log_level="info"
    )
