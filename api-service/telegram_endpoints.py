"""
ASEAGI Telegram Bot Endpoints
==============================

FastAPI endpoints for Telegram bot integration.

These endpoints provide simple, fast access to ASEAGI data for:
- Quick queries via Telegram commands
- Mobile notifications
- Automated alerts via n8n

All endpoints use the shared service layer (services.py) to ensure
consistency with MCP servers and other channels.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from services import ASEAGIService


# Create router for Telegram endpoints
router = APIRouter(prefix="/telegram", tags=["telegram"])

# Initialize shared service
service = ASEAGIService()


# ============================================================================
# Request/Response Models
# ============================================================================

class TelegramResponse(BaseModel):
    """Standard response format for Telegram bot"""
    success: bool
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None


class SearchRequest(BaseModel):
    """Request for search operations"""
    query: str
    sender: Optional[str] = None
    limit: int = 10


class TimelineRequest(BaseModel):
    """Request for timeline"""
    days: int = 30
    event_type: Optional[str] = None


# ============================================================================
# SEARCH COMMUNICATIONS
# ============================================================================

@router.post("/search", response_model=TelegramResponse)
async def search_communications(request: SearchRequest):
    """
    Search communications for specific content.

    Telegram usage: /search <query>

    Examples:
        /search visitation denial
        /search pickup verification
        /search Cal OES 2-925
    """
    try:
        results = service.search_communications(
            query=request.query,
            sender=request.sender,
            limit=request.limit
        )

        if not results:
            return TelegramResponse(
                success=True,
                message=f"No communications found matching '{request.query}'",
                data={"results": []}
            )

        # Format results for Telegram
        formatted_results = []
        for comm in results:
            formatted_results.append({
                "id": comm.communication_id,
                "from": comm.sender,
                "to": comm.recipient,
                "date": comm.sent_date,
                "content": comm.content[:200] + "..." if len(comm.content) > 200 else comm.content,
                "truthfulness": comm.truthfulness_score,
                "has_contradictions": comm.contains_contradiction
            })

        message = f"Found {len(results)} communications matching '{request.query}'"

        return TelegramResponse(
            success=True,
            message=message,
            data={
                "count": len(results),
                "results": formatted_results
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TIMELINE
# ============================================================================

@router.get("/timeline", response_model=TelegramResponse)
async def get_timeline(
    days: int = Query(30, description="Number of days to look back"),
    event_type: Optional[str] = Query(None, description="Filter by event type")
):
    """
    Get case timeline.

    Telegram usage: /timeline [days]

    Examples:
        /timeline
        /timeline 60
        /timeline hearing
    """
    try:
        # Calculate date range
        start_date = (datetime.now() - __import__('datetime').timedelta(days=days)).isoformat()

        results = service.get_timeline(
            start_date=start_date,
            event_type=event_type,
            limit=50
        )

        if not results:
            return TelegramResponse(
                success=True,
                message=f"No events found in the last {days} days",
                data={"results": []}
            )

        # Format results
        formatted_results = []
        for event in results:
            formatted_results.append({
                "id": event.event_id,
                "date": event.event_date,
                "type": event.event_type,
                "title": event.title,
                "description": event.description[:150] + "..." if len(event.description) > 150 else event.description
            })

        message = f"Timeline: {len(results)} events in last {days} days"

        return TelegramResponse(
            success=True,
            message=message,
            data={
                "count": len(results),
                "days": days,
                "results": formatted_results
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ACTION ITEMS
# ============================================================================

@router.get("/actions", response_model=TelegramResponse)
async def get_action_items(
    priority: Optional[str] = Query(None, description="Filter by priority"),
    due_soon: bool = Query(False, description="Show only items due within 7 days")
):
    """
    Get pending action items.

    Telegram usage: /actions

    Examples:
        /actions
        /actions urgent
        /actions due_soon
    """
    try:
        results = service.get_action_items(
            status="pending",
            priority=priority,
            due_soon=due_soon,
            limit=20
        )

        if not results:
            return TelegramResponse(
                success=True,
                message="No pending action items",
                data={"results": []}
            )

        # Format results
        formatted_results = []
        for item in results:
            formatted_results.append({
                "id": item.action_id,
                "title": item.title,
                "priority": item.priority,
                "due_date": item.due_date,
                "status": item.status
            })

        # Count urgent items
        urgent_count = sum(1 for item in results if item.priority == "urgent")
        message = f"Found {len(results)} action items"
        if urgent_count > 0:
            message += f" ({urgent_count} URGENT)"

        return TelegramResponse(
            success=True,
            message=message,
            data={
                "count": len(results),
                "urgent_count": urgent_count,
                "results": formatted_results
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# VIOLATIONS
# ============================================================================

@router.get("/violations", response_model=TelegramResponse)
async def get_violations(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    violation_type: Optional[str] = Query(None, description="Filter by type")
):
    """
    Get detected legal violations.

    Telegram usage: /violations

    Examples:
        /violations
        /violations critical
        /violations perjury
    """
    try:
        results = service.get_violations(
            severity=severity,
            violation_type=violation_type,
            limit=20
        )

        if not results:
            return TelegramResponse(
                success=True,
                message="No violations detected",
                data={"results": []}
            )

        # Format results
        formatted_results = []
        for violation in results:
            formatted_results.append({
                "id": violation.violation_id,
                "type": violation.violation_type,
                "severity": violation.severity,
                "description": violation.description[:200] + "..." if len(violation.description) > 200 else violation.description,
                "detected_date": violation.detected_date
            })

        # Count critical violations
        critical_count = sum(1 for v in results if v.severity == "critical")
        message = f"Found {len(results)} violations"
        if critical_count > 0:
            message += f" ({critical_count} CRITICAL)"

        return TelegramResponse(
            success=True,
            message=message,
            data={
                "count": len(results),
                "critical_count": critical_count,
                "results": formatted_results
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DEADLINES
# ============================================================================

@router.get("/deadline", response_model=TelegramResponse)
async def get_deadlines():
    """
    Get upcoming deadlines (next 7 days).

    Telegram usage: /deadline
    """
    try:
        results = service.get_action_items(
            status="pending",
            due_soon=True,
            limit=20
        )

        if not results:
            return TelegramResponse(
                success=True,
                message="No upcoming deadlines in the next 7 days",
                data={"results": []}
            )

        # Format results sorted by due date
        formatted_results = []
        for item in sorted(results, key=lambda x: x.due_date or "9999-99-99"):
            formatted_results.append({
                "title": item.title,
                "due_date": item.due_date,
                "priority": item.priority,
                "days_until_due": (
                    (__import__('datetime').datetime.fromisoformat(item.due_date).date() -
                     datetime.now().date()).days
                    if item.due_date else None
                )
            })

        message = f"⚠️ {len(results)} deadlines in the next 7 days"

        return TelegramResponse(
            success=True,
            message=message,
            data={
                "count": len(results),
                "results": formatted_results
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DAILY REPORT
# ============================================================================

@router.get("/report", response_model=TelegramResponse)
async def daily_report():
    """
    Get daily summary report.

    Telegram usage: /report
    """
    try:
        report = service.generate_daily_report()

        # Build summary message
        urgent_count = len(report["urgent_actions"])
        deadline_count = len(report["upcoming_deadlines"])
        hearing_count = len(report["upcoming_hearings"])
        violation_count = len(report["recent_violations"])
        contradiction_count = len(report["recent_contradictions"])

        summary_parts = []
        if urgent_count > 0:
            summary_parts.append(f"{urgent_count} urgent actions")
        if deadline_count > 0:
            summary_parts.append(f"{deadline_count} upcoming deadlines")
        if hearing_count > 0:
            summary_parts.append(f"{hearing_count} upcoming hearings")
        if violation_count > 0:
            summary_parts.append(f"{violation_count} recent violations")
        if contradiction_count > 0:
            summary_parts.append(f"{contradiction_count} contradictions")

        message = f"📊 Daily Report - {report['date']}\n" + ", ".join(summary_parts) if summary_parts else "All clear"

        return TelegramResponse(
            success=True,
            message=message,
            data=report
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HEARING INFORMATION
# ============================================================================

@router.get("/hearing", response_model=TelegramResponse)
async def get_hearing_info(
    hearing_id: Optional[int] = Query(None, description="Specific hearing ID"),
    days: int = Query(30, description="Days to look ahead")
):
    """
    Get hearing information.

    Telegram usage: /hearing [hearing_id]

    Examples:
        /hearing
        /hearing 123
    """
    try:
        if hearing_id:
            # Get specific hearing
            hearing = service.get_hearing_details(hearing_id)
            if not hearing:
                return TelegramResponse(
                    success=False,
                    message=f"Hearing {hearing_id} not found",
                    data=None
                )

            return TelegramResponse(
                success=True,
                message=f"Hearing on {hearing['hearing_date']}",
                data={"hearing": hearing}
            )
        else:
            # Get upcoming hearings
            hearings = service.get_upcoming_hearings(days=days)

            if not hearings:
                return TelegramResponse(
                    success=True,
                    message=f"No hearings scheduled in the next {days} days",
                    data={"results": []}
                )

            formatted_results = []
            for hearing in hearings:
                formatted_results.append({
                    "id": hearing["hearing_id"],
                    "date": hearing["hearing_date"],
                    "type": hearing["hearing_type"],
                    "judge": hearing.get("judge_name", "TBD")
                })

            message = f"📅 {len(hearings)} hearings in the next {days} days"

            return TelegramResponse(
                success=True,
                message=message,
                data={
                    "count": len(hearings),
                    "results": formatted_results
                }
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MOTION GENERATION
# ============================================================================

@router.post("/motion", response_model=TelegramResponse)
async def generate_motion(
    motion_type: str = Query(..., description="Type of motion"),
    issue: str = Query(..., description="Issue being addressed")
):
    """
    Generate motion outline.

    Telegram usage: /motion <type> <issue>

    Examples:
        /motion reconsideration "Cal OES 2-925 not verified"
        /motion vacate "Fraudulent testimony by social worker"
    """
    try:
        outline = service.generate_motion_outline(
            motion_type=motion_type,
            issue=issue
        )

        message = f"📝 Motion for {motion_type.title()} - Outline generated"

        return TelegramResponse(
            success=True,
            message=message,
            data=outline
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ASEAGI Telegram API",
        "timestamp": datetime.now().isoformat()
    }
