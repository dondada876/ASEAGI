#!/usr/bin/env python3
"""
ASEAGI Extended API Server
FastAPI backend with BOTH Telegram bot and Web interface endpoints
Includes comprehensive error checking for NON-NEGOTIABLE tables

Features:
- Telegram bot API (existing /telegram/* endpoints)
- Web interface API (new /api/* endpoints)
- Schema validation on startup
- Error handling middleware
- Data quality monitoring
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from datetime import datetime, timedelta
from supabase import create_client, Client
import uvicorn
import logging
from pathlib import Path

# Import our schema validator
from schema_validator import validate_schema, get_schema_status, SchemaValidationError

# ============================================================================
# CONFIGURATION & LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ASEAGI Extended API",
    description="Backend API for both Telegram bot and Web interface",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase connection
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://jvjlhxodmbkodzmggwpu.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY environment variable is required")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Schema validation on startup
try:
    logger.info("🔍 Validating database schema...")
    validate_schema(supabase, strict=False)  # Don't fail startup, just warn
    logger.info("✅ Schema validation completed")
except SchemaValidationError as e:
    logger.error(f"⚠️ Schema validation warnings: {e}")
except Exception as e:
    logger.error(f"❌ Schema validation error: {e}")

# ============================================================================
# ERROR HANDLING MIDDLEWARE
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with detailed logging"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "path": str(request.url),
            "timestamp": datetime.now().isoformat()
        }
    )

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add response time header"""
    start_time = datetime.now()
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    response.headers["X-Process-Time"] = str(process_time)
    return response

# ============================================================================
# MODELS
# ============================================================================

class HealthResponse(BaseModel):
    status: str
    database: str
    schema_valid: bool
    timestamp: str
    process_time: Optional[float] = None

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None

# ============================================================================
# HELPER FUNCTIONS WITH ERROR HANDLING
# ============================================================================

def safe_query(table_name: str, select: str = "*", filters: Optional[Dict] = None, limit: Optional[int] = None):
    """
    Safe database query with error handling

    Args:
        table_name: Name of table to query
        select: Columns to select
        filters: Dictionary of filters (e.g., {'significance_score__gte': 800})
        limit: Maximum number of records

    Returns:
        Query result or None if error

    Raises:
        HTTPException: If table doesn't exist or query fails
    """
    try:
        query = supabase.table(table_name).select(select)

        # Apply filters
        if filters:
            for key, value in filters.items():
                if '__gte' in key:
                    col = key.replace('__gte', '')
                    query = query.gte(col, value)
                elif '__lte' in key:
                    col = key.replace('__lte', '')
                    query = query.lte(col, value)
                elif '__eq' in key:
                    col = key.replace('__eq', '')
                    query = query.eq(col, value)
                else:
                    query = query.eq(key, value)

        # Apply limit
        if limit:
            query = query.limit(limit)

        result = query.execute()
        return result.data

    except Exception as e:
        error_msg = f"Error querying table '{table_name}': {str(e)}"
        logger.error(error_msg)

        # Check if it's a "table doesn't exist" error
        if "does not exist" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"CRITICAL: Table '{table_name}' does not exist. "
                       f"This is a NON-NEGOTIABLE table that must exist. "
                       f"Please run: mcp-servers/aseagi-mvp-server/database/01_create_critical_tables.sql"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )

# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    try:
        # Test database connection
        supabase.table('events').select('id').limit(1).execute()

        # Get schema status
        schema_summary = get_schema_status(supabase)

        return HealthResponse(
            status="online",
            database="connected",
            schema_valid=schema_summary['overall_status'] == 'valid',
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        return HealthResponse(
            status="degraded",
            database="error",
            schema_valid=False,
            timestamp=datetime.now().isoformat()
        )

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test database
        supabase.table('events').select('id').limit(1).execute()

        # Get schema status
        schema_summary = get_schema_status(supabase)

        return {
            "status": "healthy",
            "database": "connected",
            "schema": schema_summary,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/schema/validate")
async def validate_schema_endpoint():
    """Validate database schema"""
    try:
        validate_schema(supabase, strict=True)
        return {"status": "valid", "message": "All NON-NEGOTIABLE tables validated successfully"}
    except SchemaValidationError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

@app.get("/schema/status")
async def schema_status():
    """Get schema validation status"""
    return get_schema_status(supabase)

# ============================================================================
# TELEGRAM BOT ENDPOINTS (Existing from api_server.py)
# ============================================================================

@app.get("/telegram/status")
async def telegram_status():
    """
    /status command - Case status overview
    """
    try:
        events_count = supabase.table('events').select('id', count='exact').execute()
        docs_count = supabase.table('document_journal').select('id', count='exact').execute()
        comms_count = supabase.table('communications').select('id', count='exact').execute()

        recent_events = safe_query(
            'events',
            filters={'significance_score__gte': 800},
            limit=3
        )

        message = f"""📊 **ASEAGI Case Status**

📅 Events: {events_count.count}
📄 Documents: {docs_count.count}
💬 Communications: {comms_count.count}

🔥 **Recent Critical Events:**
"""
        for event in recent_events:
            message += f"\n• {event['event_title']} ({event['event_date']})"

        return {"success": True, "message": message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/telegram/events")
async def telegram_events(limit: int = 10, days: int = 30):
    """
    /events command - Recent court events
    """
    since_date = (datetime.now() - timedelta(days=days)).isoformat()

    events = safe_query(
        'events',
        filters={'event_date__gte': since_date},
        limit=limit
    )

    if not events:
        return {"success": True, "message": "📅 No events found", "data": []}

    message = f"📅 **Recent Events** (last {days} days)\n\n"
    for event in events:
        message += f"• {event['event_title']} ({event['event_date']})\n"

    return {"success": True, "message": message, "data": events}

# ============================================================================
# WEB INTERFACE API ENDPOINTS (NEW)
# ============================================================================

@app.get("/api/dashboard/overview")
async def dashboard_overview():
    """
    Overview dashboard data
    Distinct from other dashboards - focuses on overall metrics
    """
    try:
        # Get counts
        events_count = supabase.table('events').select('id', count='exact').execute()
        docs_count = supabase.table('document_journal').select('id', count='exact').execute()
        comms_count = supabase.table('communications').select('id', count='exact').execute()

        # Get critical items
        critical_events = safe_query(
            'events',
            filters={'significance_score__gte': 900},
            limit=5
        )

        critical_docs = safe_query(
            'document_journal',
            filters={'relevancy_score__gte': 900},
            limit=5
        )

        high_truth_comms = safe_query(
            'communications',
            filters={'truthfulness_score__gte': 900},
            limit=5
        )

        return APIResponse(
            success=True,
            message="Overview data retrieved",
            data={
                "counts": {
                    "events": events_count.count,
                    "documents": docs_count.count,
                    "communications": comms_count.count
                },
                "critical": {
                    "events": critical_events,
                    "documents": critical_docs,
                    "communications": high_truth_comms
                },
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Error in dashboard_overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/truth-timeline")
async def dashboard_truth_timeline(days: int = 90):
    """
    Truth & Justice Timeline dashboard data
    DISTINCT: Focuses on truth scoring and justice metrics
    """
    try:
        since_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Get items with truth implications
        events = safe_query('events', filters={'event_date__gte': since_date})
        docs = safe_query('document_journal', filters={'upload_date__gte': since_date})
        comms = safe_query('communications', filters={'communication_date__gte': since_date})

        # Calculate truth scores
        def calculate_truth_score(item, item_type):
            if item_type == 'event':
                return item.get('significance_score', 0) / 10  # Convert to 0-100
            elif item_type == 'document':
                return item.get('relevancy_score', 0) / 10
            elif item_type == 'communication':
                return item.get('truthfulness_score', 0) / 10
            return 50  # Neutral

        # Build timeline
        timeline = []
        for event in events:
            timeline.append({
                'date': event['event_date'],
                'type': 'event',
                'title': event['event_title'],
                'truth_score': calculate_truth_score(event, 'event'),
                'significance': event.get('significance_score', 0)
            })

        for doc in docs:
            timeline.append({
                'date': doc.get('upload_date') or doc.get('scan_date'),
                'type': 'document',
                'title': doc['original_filename'],
                'truth_score': calculate_truth_score(doc, 'document'),
                'relevancy': doc.get('relevancy_score', 0)
            })

        for comm in comms:
            timeline.append({
                'date': comm['communication_date'],
                'type': 'communication',
                'title': f"{comm['sender']} → {comm['recipient']}",
                'truth_score': calculate_truth_score(comm, 'communication'),
                'truthfulness': comm.get('truthfulness_score', 0)
            })

        # Sort by date
        timeline.sort(key=lambda x: x['date'], reverse=True)

        # Calculate justice score
        truth_scores = [item['truth_score'] for item in timeline]
        justice_score = sum(truth_scores) / len(truth_scores) if truth_scores else 50

        return APIResponse(
            success=True,
            message="Truth timeline data retrieved",
            data={
                "timeline": timeline[:100],  # Limit to 100 items
                "justice_score": round(justice_score, 1),
                "true_count": len([s for s in truth_scores if s >= 75]),
                "questionable_count": len([s for s in truth_scores if 25 <= s < 75]),
                "false_count": len([s for s in truth_scores if s < 25]),
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Error in dashboard_truth_timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/violations")
async def dashboard_violations():
    """
    Constitutional Violations dashboard data
    DISTINCT: Focuses on legal violations and constitutional issues
    """
    try:
        # Get events with violations
        violation_events = safe_query(
            'events',
            filters={'violations_occurred': True}  # Assuming this column exists
        )

        # Group by violation type
        violations_by_type = {}
        for event in (violation_events or []):
            violations = event.get('violations_occurred', [])
            if isinstance(violations, list):
                for v in violations:
                    violations_by_type[v] = violations_by_type.get(v, 0) + 1

        # Get critical violation events
        critical_violations = [
            e for e in (violation_events or [])
            if e.get('significance_score', 0) >= 800
        ]

        return APIResponse(
            success=True,
            message="Violations data retrieved",
            data={
                "total_violations": len(violation_events) if violation_events else 0,
                "by_type": violations_by_type,
                "critical": critical_violations[:10],
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Error in dashboard_violations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/court-events")
async def dashboard_court_events():
    """
    Court Events dashboard data
    DISTINCT: Focuses on case management and deadlines
    """
    try:
        # Get upcoming events (requires_action = True)
        upcoming = safe_query(
            'events',
            filters={'requires_action': True, 'event_date__gte': datetime.now().isoformat()},
            limit=20
        )

        # Get recent completed events
        recent = safe_query(
            'events',
            filters={'event_date__lte': datetime.now().isoformat()},
            limit=20
        )

        # Calculate urgency
        for event in (upcoming or []):
            event_date = datetime.fromisoformat(event['event_date'])
            days_until = (event_date - datetime.now()).days
            if days_until <= 3:
                event['urgency'] = 'URGENT'
            elif days_until <= 7:
                event['urgency'] = 'HIGH'
            else:
                event['urgency'] = 'NORMAL'

        return APIResponse(
            success=True,
            message="Court events data retrieved",
            data={
                "upcoming": upcoming or [],
                "recent": recent or [],
                "urgent_count": len([e for e in (upcoming or []) if e.get('urgency') == 'URGENT']),
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Error in dashboard_court_events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))

    print(f"""
╔═══════════════════════════════════════════════════════╗
║   ASEAGI Extended API Server v2.0                     ║
║   For Ashe - Protecting children through AI          ║
╚═══════════════════════════════════════════════════════╝

🚀 Starting extended server on port {port}...

📊 NON-NEGOTIABLE tables:
   • events (timeline - MOST IMPORTANT)
   • document_journal (processing & growth)
   • communications (evidence tracking)

🔗 Telegram Bot API: http://localhost:{port}/telegram/*
🌐 Web Interface API: http://localhost:{port}/api/dashboard/*
📖 API Docs: http://localhost:{port}/docs
🏥 Health Check: http://localhost:{port}/health
✅ Schema Validation: http://localhost:{port}/schema/validate
""")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
