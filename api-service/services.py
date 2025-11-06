"""
ASEAGI Shared Service Layer
===========================

This module provides a shared service layer for all ASEAGI communication channels:
- MCP servers (Claude Desktop)
- FastAPI (Telegram, mobile apps)
- n8n (automation workflows)

By centralizing database access and business logic, we avoid code duplication
and ensure consistent behavior across all channels.
"""

import os
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from supabase import create_client, Client
from dataclasses import dataclass


@dataclass
class CommunicationResult:
    """Result from searching communications"""
    communication_id: int
    sender: str
    recipient: str
    sent_date: str
    content: str
    truthfulness_score: Optional[float]
    contains_contradiction: bool
    contradiction_details: List[Dict]


@dataclass
class TimelineEvent:
    """Event in the case timeline"""
    event_id: int
    event_date: str
    event_type: str
    title: str
    description: str
    parties_involved: List[str]
    related_documents: List[int]


@dataclass
class ActionItem:
    """Pending action item"""
    action_id: int
    title: str
    description: str
    priority: str
    due_date: Optional[str]
    status: str
    assigned_to: Optional[str]
    related_hearings: List[int]


@dataclass
class ViolationResult:
    """Detected legal violation"""
    violation_id: int
    violation_type: str
    severity: str
    description: str
    evidence: List[str]
    related_documents: List[int]
    detected_date: str


@dataclass
class DocumentResult:
    """Document search result"""
    journal_id: int
    document_type: str
    original_filename: str
    date_logged: str
    summary: Optional[str]
    ai_confidence_score: Optional[float]


class ASEAGIService:
    """
    Shared service layer for ASEAGI system.

    All database queries and business logic should go through this service
    to ensure consistency across MCP servers, FastAPI, and n8n.
    """

    def __init__(self):
        """Initialize service with Supabase client"""
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        self.supabase: Client = create_client(supabase_url, supabase_key)

    # ========================================================================
    # COMMUNICATIONS
    # ========================================================================

    def search_communications(
        self,
        query: Optional[str] = None,
        sender: Optional[str] = None,
        recipient: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        has_contradictions: Optional[bool] = None,
        limit: int = 50
    ) -> List[CommunicationResult]:
        """
        Search communications (text messages, emails, calls).

        Args:
            query: Text search in content
            sender: Filter by sender
            recipient: Filter by recipient
            start_date: Filter by date range (ISO format)
            end_date: Filter by date range (ISO format)
            has_contradictions: Filter for messages with contradictions
            limit: Max results (default 50)

        Returns:
            List of communication results
        """
        db_query = self.supabase.table("communications").select("*")

        # Apply filters
        if query:
            db_query = db_query.ilike("content", f"%{query}%")
        if sender:
            db_query = db_query.ilike("sender", f"%{sender}%")
        if recipient:
            db_query = db_query.ilike("recipient", f"%{recipient}%")
        if start_date:
            db_query = db_query.gte("sent_date", start_date)
        if end_date:
            db_query = db_query.lte("sent_date", end_date)
        if has_contradictions is not None:
            db_query = db_query.eq("contains_contradiction", has_contradictions)

        result = db_query.order("sent_date", desc=True).limit(limit).execute()

        # Convert to dataclass
        communications = []
        for row in result.data:
            communications.append(CommunicationResult(
                communication_id=row["communication_id"],
                sender=row["sender"],
                recipient=row["recipient"],
                sent_date=row["sent_date"],
                content=row["content"],
                truthfulness_score=row.get("truthfulness_score"),
                contains_contradiction=row.get("contains_contradiction", False),
                contradiction_details=row.get("contradiction_details", [])
            ))

        return communications

    # ========================================================================
    # TIMELINE
    # ========================================================================

    def get_timeline(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[TimelineEvent]:
        """
        Get chronological timeline of case events.

        Args:
            start_date: Filter by date range (ISO format)
            end_date: Filter by date range (ISO format)
            event_type: Filter by event type ('hearing', 'filing', 'incident', etc.)
            limit: Max results (default 100)

        Returns:
            List of timeline events
        """
        db_query = self.supabase.table("events").select("*")

        # Apply filters
        if start_date:
            db_query = db_query.gte("event_date", start_date)
        if end_date:
            db_query = db_query.lte("event_date", end_date)
        if event_type:
            db_query = db_query.eq("event_type", event_type)

        result = db_query.order("event_date", desc=True).limit(limit).execute()

        # Convert to dataclass
        events = []
        for row in result.data:
            events.append(TimelineEvent(
                event_id=row["event_id"],
                event_date=row["event_date"],
                event_type=row["event_type"],
                title=row["title"],
                description=row.get("description", ""),
                parties_involved=row.get("parties_involved", []),
                related_documents=row.get("related_documents", [])
            ))

        return events

    # ========================================================================
    # ACTION ITEMS
    # ========================================================================

    def get_action_items(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_soon: bool = False,
        limit: int = 50
    ) -> List[ActionItem]:
        """
        Get pending action items and tasks.

        Args:
            status: Filter by status ('pending', 'in_progress', 'completed')
            priority: Filter by priority ('urgent', 'high', 'medium', 'low')
            due_soon: Show only items due within 7 days
            limit: Max results (default 50)

        Returns:
            List of action items
        """
        db_query = self.supabase.table("action_items").select("*")

        # Apply filters
        if status:
            db_query = db_query.eq("status", status)
        if priority:
            db_query = db_query.eq("priority", priority)
        if due_soon:
            seven_days_from_now = (datetime.now() + timedelta(days=7)).isoformat()
            db_query = db_query.lte("due_date", seven_days_from_now)

        result = db_query.order("due_date", desc=False).limit(limit).execute()

        # Convert to dataclass
        items = []
        for row in result.data:
            items.append(ActionItem(
                action_id=row["action_id"],
                title=row["title"],
                description=row.get("description", ""),
                priority=row["priority"],
                due_date=row.get("due_date"),
                status=row["status"],
                assigned_to=row.get("assigned_to"),
                related_hearings=row.get("related_hearings", [])
            ))

        return items

    # ========================================================================
    # VIOLATIONS
    # ========================================================================

    def get_violations(
        self,
        severity: Optional[str] = None,
        violation_type: Optional[str] = None,
        limit: int = 50
    ) -> List[ViolationResult]:
        """
        Get detected legal violations.

        Args:
            severity: Filter by severity ('critical', 'high', 'medium', 'low')
            violation_type: Filter by type ('perjury', 'fraud', 'due_process', etc.)
            limit: Max results (default 50)

        Returns:
            List of violations
        """
        db_query = self.supabase.table("violations").select("*")

        # Apply filters
        if severity:
            db_query = db_query.eq("severity", severity)
        if violation_type:
            db_query = db_query.eq("violation_type", violation_type)

        result = db_query.order("detected_date", desc=True).limit(limit).execute()

        # Convert to dataclass
        violations = []
        for row in result.data:
            violations.append(ViolationResult(
                violation_id=row["violation_id"],
                violation_type=row["violation_type"],
                severity=row["severity"],
                description=row["description"],
                evidence=row.get("evidence", []),
                related_documents=row.get("related_documents", []),
                detected_date=row["detected_date"]
            ))

        return violations

    # ========================================================================
    # DOCUMENTS
    # ========================================================================

    def search_documents(
        self,
        query: Optional[str] = None,
        document_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 50
    ) -> List[DocumentResult]:
        """
        Search case documents.

        Args:
            query: Text search in filename or content
            document_type: Filter by document type
            start_date: Filter by date logged (ISO format)
            end_date: Filter by date logged (ISO format)
            limit: Max results (default 50)

        Returns:
            List of documents
        """
        db_query = self.supabase.table("document_journal").select("*")

        # Apply filters
        if query:
            db_query = db_query.or_(
                f"original_filename.ilike.%{query}%,"
                f"normalized_filename.ilike.%{query}%"
            )
        if document_type:
            db_query = db_query.eq("document_type", document_type)
        if start_date:
            db_query = db_query.gte("date_logged", start_date)
        if end_date:
            db_query = db_query.lte("date_logged", end_date)

        result = db_query.order("date_logged", desc=True).limit(limit).execute()

        # Convert to dataclass
        documents = []
        for row in result.data:
            documents.append(DocumentResult(
                journal_id=row["journal_id"],
                document_type=row.get("document_type", "unknown"),
                original_filename=row["original_filename"],
                date_logged=row["date_logged"],
                summary=row.get("summary"),
                ai_confidence_score=row.get("ai_confidence_score")
            ))

        return documents

    # ========================================================================
    # HEARINGS
    # ========================================================================

    def get_upcoming_hearings(self, days: int = 30) -> List[Dict]:
        """
        Get upcoming court hearings.

        Args:
            days: Number of days to look ahead (default 30)

        Returns:
            List of hearings
        """
        end_date = (datetime.now() + timedelta(days=days)).isoformat()

        result = self.supabase.table("hearings").select("*")\
            .gte("hearing_date", datetime.now().isoformat())\
            .lte("hearing_date", end_date)\
            .order("hearing_date", desc=False)\
            .execute()

        return result.data

    def get_hearing_details(self, hearing_id: int) -> Optional[Dict]:
        """
        Get detailed information about a specific hearing.

        Args:
            hearing_id: ID of the hearing

        Returns:
            Hearing details or None if not found
        """
        result = self.supabase.table("hearings").select("*")\
            .eq("hearing_id", hearing_id)\
            .execute()

        if result.data:
            return result.data[0]
        return None

    # ========================================================================
    # DAILY REPORTS
    # ========================================================================

    def generate_daily_report(self) -> Dict[str, Any]:
        """
        Generate daily summary report.

        Returns:
            Dictionary with report sections
        """
        today = datetime.now().date().isoformat()
        seven_days = (datetime.now() + timedelta(days=7)).isoformat()

        # Get urgent action items
        urgent_actions = self.get_action_items(
            status="pending",
            priority="urgent",
            limit=10
        )

        # Get upcoming deadlines
        upcoming_actions = self.get_action_items(
            status="pending",
            due_soon=True,
            limit=10
        )

        # Get upcoming hearings
        upcoming_hearings = self.get_upcoming_hearings(days=14)

        # Get recent violations
        recent_violations = self.get_violations(limit=5)

        # Get recent contradictions
        contradictions = self.search_communications(
            has_contradictions=True,
            limit=5
        )

        return {
            "date": today,
            "urgent_actions": [
                {
                    "title": item.title,
                    "priority": item.priority,
                    "due_date": item.due_date
                }
                for item in urgent_actions
            ],
            "upcoming_deadlines": [
                {
                    "title": item.title,
                    "due_date": item.due_date,
                    "status": item.status
                }
                for item in upcoming_actions
            ],
            "upcoming_hearings": [
                {
                    "hearing_date": h["hearing_date"],
                    "hearing_type": h["hearing_type"],
                    "judge_name": h.get("judge_name")
                }
                for h in upcoming_hearings
            ],
            "recent_violations": [
                {
                    "type": v.violation_type,
                    "severity": v.severity,
                    "description": v.description
                }
                for v in recent_violations
            ],
            "recent_contradictions": [
                {
                    "sender": c.sender,
                    "date": c.sent_date,
                    "content_preview": c.content[:100] + "..." if len(c.content) > 100 else c.content
                }
                for c in contradictions
            ]
        }

    # ========================================================================
    # MOTION GENERATION (Placeholder)
    # ========================================================================

    def generate_motion_outline(
        self,
        motion_type: str,
        issue: str,
        related_violations: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Generate motion outline (full PDF generation in Phase 2).

        Args:
            motion_type: Type of motion ('reconsideration', 'vacate', 'quash', etc.)
            issue: Issue being addressed
            related_violations: List of violation IDs to include

        Returns:
            Motion outline structure
        """
        # This is a placeholder - full implementation will generate PDF
        return {
            "motion_type": motion_type,
            "issue": issue,
            "structure": {
                "caption": f"Motion for {motion_type.title()}",
                "notice_of_motion": f"NOTICE OF MOTION AND MOTION FOR {motion_type.upper()}",
                "memorandum": "To be generated with case law and arguments",
                "declaration": "To be generated with facts and evidence",
                "proposed_order": "To be generated"
            },
            "next_steps": [
                "Gather supporting evidence",
                "Search for relevant case law",
                "Identify witnesses",
                "Review related documents"
            ],
            "related_violations": related_violations or []
        }
