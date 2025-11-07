#!/usr/bin/env python3
"""
ASEAGI Telegram Bot API Backend
Provides endpoints for Telegram bot commands
Uses NON-NEGOTIABLE tables: communications, events, document_journal
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from datetime import datetime, timedelta
from supabase import create_client, Client
import uvicorn

# ============================================================================
# CONFIGURATION
# ============================================================================

app = FastAPI(
    title="ASEAGI Telegram Bot API",
    description="Backend API for ASEAGI legal case management Telegram bot",
    version="1.0.0"
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

# ============================================================================
# MODELS
# ============================================================================

class StatusResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None

class EventSummary(BaseModel):
    id: str
    event_date: str
    event_title: str
    event_type: str
    significance_score: Optional[int] = None
    importance: Optional[str] = None

class DocumentSummary(BaseModel):
    id: str
    original_filename: str
    relevancy_score: Optional[int] = None
    processing_status: Optional[str] = None
    insights_extracted: Optional[int] = None

class CommunicationSummary(BaseModel):
    id: str
    communication_date: str
    sender: str
    recipient: str
    subject: Optional[str] = None
    truthfulness_score: Optional[int] = None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_event_for_telegram(event: Dict[str, Any]) -> str:
    """Format event data for Telegram message"""
    date = event.get('event_date', 'Unknown')
    title = event.get('event_title', 'Untitled')
    event_type = event.get('event_type', 'N/A')
    significance = event.get('significance_score', 0)

    emoji = "🔴" if significance >= 800 else "🟡" if significance >= 600 else "🟢"

    return f"{emoji} **{title}**\n📅 {date}\n🏷️ Type: {event_type}\n⭐ Significance: {significance}/1000"

def format_document_for_telegram(doc: Dict[str, Any]) -> str:
    """Format document data for Telegram message"""
    filename = doc.get('original_filename', 'Unknown')
    relevancy = doc.get('relevancy_score', 0)
    status = doc.get('processing_status', 'unknown')
    insights = doc.get('insights_extracted', 0)

    emoji = "🔥" if relevancy >= 800 else "📄" if relevancy >= 600 else "📋"

    return f"{emoji} **{filename}**\n📊 Relevancy: {relevancy}/1000\n⚙️ Status: {status}\n💡 Insights: {insights}"

def format_communication_for_telegram(comm: Dict[str, Any]) -> str:
    """Format communication data for Telegram message"""
    date = comm.get('communication_date', 'Unknown')
    sender = comm.get('sender', 'Unknown')
    recipient = comm.get('recipient', 'Unknown')
    subject = comm.get('subject', 'No subject')
    truth_score = comm.get('truthfulness_score', None)

    emoji = "✅" if truth_score and truth_score >= 750 else "⚠️" if truth_score and truth_score >= 500 else "❌" if truth_score else "❓"

    msg = f"{emoji} **{subject}**\n📅 {date}\n👤 {sender} → {recipient}"
    if truth_score is not None:
        msg += f"\n🎯 Truth: {truth_score}/1000"

    return msg

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "ASEAGI Telegram Bot API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check including database connection"""
    try:
        # Test Supabase connection
        supabase.table('events').select('id').limit(1).execute()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ============================================================================
# TELEGRAM ENDPOINTS
# ============================================================================

@app.get("/telegram/status")
async def telegram_status():
    """
    /status command - Get case status overview
    Returns: Total events, documents, communications
    """
    try:
        # Count events (NON-NEGOTIABLE TABLE)
        events_count = supabase.table('events').select('id', count='exact').execute()

        # Count document journal entries (NON-NEGOTIABLE TABLE)
        docs_count = supabase.table('document_journal').select('id', count='exact').execute()

        # Count communications (NON-NEGOTIABLE TABLE)
        comms_count = supabase.table('communications').select('id', count='exact').execute()

        # Get recent critical events
        recent_events = supabase.table('events')\
            .select('event_date, event_title, significance_score')\
            .gte('significance_score', 800)\
            .order('event_date', desc=True)\
            .limit(3)\
            .execute()

        message = f"""📊 **ASEAGI Case Status**

📅 Events: {events_count.count}
📄 Documents: {docs_count.count}
💬 Communications: {comms_count.count}

🔥 **Recent Critical Events:**
"""

        for event in recent_events.data:
            message += f"\n• {event['event_title']} ({event['event_date']})"

        return StatusResponse(
            status="success",
            message=message,
            data={
                "events_count": events_count.count,
                "documents_count": docs_count.count,
                "communications_count": comms_count.count,
                "critical_events": recent_events.data
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching status: {str(e)}")

@app.get("/telegram/events")
async def telegram_events(limit: int = 10, days: int = 30):
    """
    /events command - Get recent court events
    Query params:
    - limit: Number of events to return (default: 10)
    - days: Number of days to look back (default: 30)
    """
    try:
        since_date = (datetime.now() - timedelta(days=days)).isoformat()

        events = supabase.table('events')\
            .select('*')\
            .gte('event_date', since_date)\
            .order('event_date', desc=True)\
            .limit(limit)\
            .execute()

        if not events.data:
            return StatusResponse(
                status="success",
                message="📅 No events found in the specified time period.",
                data={"events": []}
            )

        message = f"📅 **Recent Events** (last {days} days)\n\n"
        for event in events.data:
            message += format_event_for_telegram(event) + "\n\n"

        return StatusResponse(
            status="success",
            message=message,
            data={"events": events.data}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")

@app.get("/telegram/documents")
async def telegram_documents(min_relevancy: int = 700, limit: int = 10):
    """
    /documents command - Get high-relevancy documents
    Query params:
    - min_relevancy: Minimum relevancy score (default: 700)
    - limit: Number of documents to return (default: 10)
    """
    try:
        docs = supabase.table('document_journal')\
            .select('*')\
            .gte('relevancy_score', min_relevancy)\
            .order('relevancy_score', desc=True)\
            .limit(limit)\
            .execute()

        if not docs.data:
            return StatusResponse(
                status="success",
                message=f"📄 No documents found with relevancy ≥ {min_relevancy}.",
                data={"documents": []}
            )

        message = f"📄 **High-Relevancy Documents** (≥{min_relevancy}/1000)\n\n"
        for doc in docs.data:
            message += format_document_for_telegram(doc) + "\n\n"

        return StatusResponse(
            status="success",
            message=message,
            data={"documents": docs.data}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching documents: {str(e)}")

@app.get("/telegram/communications")
async def telegram_communications(limit: int = 10, days: int = 30):
    """
    /communications command - Get recent communications
    Query params:
    - limit: Number of communications to return (default: 10)
    - days: Number of days to look back (default: 30)
    """
    try:
        since_date = (datetime.now() - timedelta(days=days)).isoformat()

        comms = supabase.table('communications')\
            .select('*')\
            .gte('communication_date', since_date)\
            .order('communication_date', desc=True)\
            .limit(limit)\
            .execute()

        if not comms.data:
            return StatusResponse(
                status="success",
                message=f"💬 No communications found in the last {days} days.",
                data={"communications": []}
            )

        message = f"💬 **Recent Communications** (last {days} days)\n\n"
        for comm in comms.data:
            message += format_communication_for_telegram(comm) + "\n\n"

        return StatusResponse(
            status="success",
            message=message,
            data={"communications": comms.data}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching communications: {str(e)}")

@app.get("/telegram/evidence")
async def telegram_evidence():
    """
    /evidence command - Get critical evidence summary
    Returns: High-truth communications, high-relevancy documents, critical events
    """
    try:
        # High-truth communications
        truth_comms = supabase.table('communications')\
            .select('*')\
            .gte('truthfulness_score', 800)\
            .order('truthfulness_score', desc=True)\
            .limit(5)\
            .execute()

        # Critical documents
        critical_docs = supabase.table('document_journal')\
            .select('*')\
            .gte('relevancy_score', 900)\
            .order('relevancy_score', desc=True)\
            .limit(5)\
            .execute()

        # Critical events
        critical_events = supabase.table('events')\
            .select('*')\
            .gte('significance_score', 900)\
            .order('significance_score', desc=True)\
            .limit(5)\
            .execute()

        message = "🔥 **Critical Evidence Summary**\n\n"

        message += "**High-Truth Communications:**\n"
        for comm in truth_comms.data:
            message += f"• {comm.get('subject', 'No subject')} (Truth: {comm.get('truthfulness_score')}/1000)\n"

        message += "\n**Critical Documents:**\n"
        for doc in critical_docs.data:
            message += f"• {doc.get('original_filename')} (Relevancy: {doc.get('relevancy_score')}/1000)\n"

        message += "\n**Critical Events:**\n"
        for event in critical_events.data:
            message += f"• {event.get('event_title')} (Significance: {event.get('significance_score')}/1000)\n"

        return StatusResponse(
            status="success",
            message=message,
            data={
                "high_truth_communications": truth_comms.data,
                "critical_documents": critical_docs.data,
                "critical_events": critical_events.data
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching evidence: {str(e)}")

@app.get("/telegram/help")
async def telegram_help():
    """
    /help command - Show available commands
    """
    help_text = """🤖 **ASEAGI Bot Commands**

/status - Case status overview
/events - Recent court events
/documents - High-relevancy documents
/communications - Recent communications
/evidence - Critical evidence summary
/cases - Case information (future)
/help - Show this help message

**For Ashe - Protecting children through intelligent legal assistance** ⚖️
"""

    return StatusResponse(
        status="success",
        message=help_text,
        data={"commands": [
            "/status", "/events", "/documents",
            "/communications", "/evidence", "/cases", "/help"
        ]}
    )

@app.get("/telegram/cases")
async def telegram_cases():
    """
    /cases command - Get case information
    Note: This is a placeholder for future multi-case support
    """
    return StatusResponse(
        status="info",
        message="📁 **Active Case:**\n\nIn re Ashe B., J24-00478\nAlameda County Juvenile Court\n\nMulti-case tracking coming in Phase 2.",
        data={
            "case_number": "J24-00478",
            "case_name": "In re Ashe B.",
            "jurisdiction": "Alameda County Juvenile Court"
        }
    )

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    # Get port from environment or default to 8000
    port = int(os.environ.get('PORT', 8000))

    print(f"""
╔═══════════════════════════════════════════════════════╗
║   ASEAGI Telegram Bot API Server                     ║
║   For Ashe - Protecting children through AI          ║
╚═══════════════════════════════════════════════════════╝

🚀 Starting server on port {port}...
📊 Using NON-NEGOTIABLE tables:
   • events (timeline)
   • document_journal (processing)
   • communications (evidence)

🔗 API Documentation: http://localhost:{port}/docs
""")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
