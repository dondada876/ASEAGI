#!/usr/bin/env python3
"""
ASEAGI MVP MCP Server
=====================
Model Context Protocol server for ASEAGI legal case management.
Provides 5 core tools for Claude to interact with Supabase database.

For Ashe - Protecting children through intelligent legal assistance.

Version: 1.0.0 (MVP - Phase 1)
Schema: Adapted to existing database (legal_documents, court_events, etc.)
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Supabase client (version 2.12.0+)
try:
    from supabase import create_client, Client
except ImportError:
    print("ERROR: supabase package not installed. Run: pip install supabase>=2.12.0")
    exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize MCP server
app = Server("aseagi-mvp-server")

# Global Supabase client
supabase_client: Client = None


def get_supabase_client() -> Client:
    """Get or create Supabase client instance."""
    global supabase_client

    if supabase_client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            raise ValueError(
                "Missing Supabase credentials. Set SUPABASE_URL and SUPABASE_KEY "
                "environment variables."
            )

        supabase_client = create_client(url, key)
        logger.info("Supabase client initialized successfully")

    return supabase_client


def format_date(date_val: Any) -> str:
    """Format date value for display."""
    if not date_val:
        return "N/A"
    if isinstance(date_val, str):
        try:
            dt = datetime.fromisoformat(date_val.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return date_val
    return str(date_val)


def safe_get(data: dict, key: str, default: Any = "N/A") -> Any:
    """Safely get value from dictionary."""
    return data.get(key, default) if data.get(key) is not None else default


# ============================================================================
# TOOL DEFINITIONS
# ============================================================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="search_communications",
            description=(
                "Search through case communications (texts, emails, letters). "
                "Searches the communications_matrix table for sender, recipient, "
                "content, and dates. Useful for finding specific conversations, "
                "tracking communication patterns, and identifying contradictions."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term to find in communication content"
                    },
                    "sender": {
                        "type": "string",
                        "description": "Filter by sender name or email"
                    },
                    "recipient": {
                        "type": "string",
                        "description": "Filter by recipient name or email"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Filter communications after this date (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Filter communications before this date (YYYY-MM-DD)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 50)",
                        "default": 50
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_timeline",
            description=(
                "Get chronological timeline of case events. Retrieves events from "
                "court_events table including hearings, filings, motions, and "
                "significant case milestones. Useful for understanding case history "
                "and identifying key dates."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Get events after this date (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Get events before this date (YYYY-MM-DD)"
                    },
                    "event_type": {
                        "type": "string",
                        "description": "Filter by event type (e.g., 'hearing', 'filing', 'motion')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of events to return (default: 100)",
                        "default": 100
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="search_documents",
            description=(
                "Search legal documents by filename, content, or metadata. "
                "Searches the legal_documents table (601 documents) with relevancy "
                "scores, micro scores, and categories. Useful for finding specific "
                "filings, declarations, or evidence."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term for filename or content"
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by document category"
                    },
                    "min_relevancy": {
                        "type": "integer",
                        "description": "Minimum relevancy score (0-1000)"
                    },
                    "party": {
                        "type": "string",
                        "description": "Filter by party (e.g., 'mother', 'father', 'court')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of documents to return (default: 20)",
                        "default": 20
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_action_items",
            description=(
                "Get pending action items and deadlines. Returns upcoming tasks, "
                "court deadlines, and required actions. (Phase 2: Will connect to "
                "action_items table when available)"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Filter by status ('pending', 'completed', 'overdue')",
                        "enum": ["pending", "completed", "overdue", "all"]
                    },
                    "priority": {
                        "type": "string",
                        "description": "Filter by priority level",
                        "enum": ["high", "medium", "low", "all"]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of items to return (default: 50)",
                        "default": 50
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="generate_motion",
            description=(
                "Generate motion outline based on case facts and legal arguments. "
                "(Phase 1: Returns structured outline. Phase 2: Will generate full "
                "PDF with proper formatting and citations)"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "motion_type": {
                        "type": "string",
                        "description": "Type of motion (e.g., 'W&I 388', 'CCP 473(d)', 'RFO')"
                    },
                    "grounds": {
                        "type": "string",
                        "description": "Legal grounds and factual basis for the motion"
                    },
                    "relief_requested": {
                        "type": "string",
                        "description": "Specific relief being requested from the court"
                    },
                    "supporting_evidence": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of document IDs or evidence references"
                    }
                },
                "required": ["motion_type", "grounds", "relief_requested"]
            }
        ),
    ]


# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================

async def search_communications_impl(
    query: str = None,
    sender: str = None,
    recipient: str = None,
    start_date: str = None,
    end_date: str = None,
    limit: int = 50
) -> str:
    """
    Search communications in database.
    Uses communications_matrix table (or creates helpful message if missing).
    """
    try:
        supabase = get_supabase_client()

        # Try to query communications_matrix table
        try:
            db_query = supabase.table("communications_matrix").select("*")

            # Apply filters
            if query:
                db_query = db_query.ilike("summary", f"%{query}%")
            if sender:
                db_query = db_query.ilike("sender", f"%{sender}%")
            if recipient:
                db_query = db_query.ilike("recipient", f"%{recipient}%")
            if start_date:
                db_query = db_query.gte("communication_date", start_date)
            if end_date:
                db_query = db_query.lte("communication_date", end_date)

            db_query = db_query.order("communication_date", desc=True).limit(limit)
            result = supabase.table("communications_matrix").select("*").limit(limit).execute()

            if not result.data:
                return "No communications found matching your criteria."

            # Format results
            output = [f"Found {len(result.data)} communication(s):\n"]

            for i, comm in enumerate(result.data, 1):
                output.append(f"\n{i}. {safe_get(comm, 'communication_date', 'Unknown date')}")
                output.append(f"   From: {safe_get(comm, 'sender', 'Unknown')}")
                output.append(f"   To: {safe_get(comm, 'recipient', 'Unknown')}")
                output.append(f"   Subject: {safe_get(comm, 'subject', 'No subject')}")
                output.append(f"   Summary: {safe_get(comm, 'summary', 'No summary')[:200]}")
                output.append(f"   Method: {safe_get(comm, 'communication_method', 'Unknown')}")

            return "\n".join(output)

        except Exception as table_error:
            # Table might not exist yet
            if "does not exist" in str(table_error).lower() or "relation" in str(table_error).lower():
                return (
                    "Communications tracking is not yet set up in the database.\n\n"
                    "To enable this feature:\n"
                    "1. Create 'communications_matrix' table in Supabase\n"
                    "2. Add columns: id, sender, recipient, subject, summary, "
                    "communication_date, communication_method\n\n"
                    "Or this tool will be available in Phase 2."
                )
            else:
                raise table_error

    except Exception as e:
        logger.error(f"Error searching communications: {e}")
        return f"Error searching communications: {str(e)}"


async def get_timeline_impl(
    start_date: str = None,
    end_date: str = None,
    event_type: str = None,
    limit: int = 100
) -> str:
    """
    Get case timeline from court_events table.
    Adapted to use existing court_events table (not 'events').
    """
    try:
        supabase = get_supabase_client()

        db_query = supabase.table("court_events").select("*")

        # Apply filters
        if start_date:
            db_query = db_query.gte("event_date", start_date)
        if end_date:
            db_query = db_query.lte("event_date", end_date)
        if event_type:
            db_query = db_query.ilike("event_type", f"%{event_type}%")

        db_query = db_query.order("event_date", desc=True).limit(limit)
        result = db_query.execute()

        if not result.data:
            return "No events found matching your criteria."

        # Format timeline
        output = [f"Case Timeline ({len(result.data)} events):\n"]
        output.append("=" * 60)

        for event in result.data:
            output.append(f"\n📅 {format_date(safe_get(event, 'event_date'))}")
            output.append(f"   Type: {safe_get(event, 'event_type', 'Unknown')}")
            output.append(f"   Title: {safe_get(event, 'event_title', 'Untitled')}")

            if event.get('event_description'):
                desc = event['event_description'][:150]
                output.append(f"   Description: {desc}...")

            if event.get('judge_name'):
                output.append(f"   Judge: {event['judge_name']}")

            if event.get('event_outcome'):
                output.append(f"   Outcome: {event['event_outcome']}")

            output.append("")

        return "\n".join(output)

    except Exception as e:
        logger.error(f"Error getting timeline: {e}")
        return f"Error retrieving timeline: {str(e)}"


async def search_documents_impl(
    query: str = None,
    category: str = None,
    min_relevancy: int = None,
    party: str = None,
    limit: int = 20
) -> str:
    """
    Search legal documents.
    Uses legal_documents table (601 documents with relevancy/micro scoring).
    """
    try:
        supabase = get_supabase_client()

        db_query = supabase.table("legal_documents").select("*")

        # Apply filters
        if query:
            db_query = db_query.or_(
                f"original_filename.ilike.%{query}%,"
                f"document_type.ilike.%{query}%"
            )

        if category:
            db_query = db_query.contains("categories", [category])

        if min_relevancy:
            db_query = db_query.gte("relevancy_number", min_relevancy)

        if party:
            db_query = db_query.ilike("party_author", f"%{party}%")

        db_query = db_query.order("relevancy_number", desc=True).limit(limit)
        result = db_query.execute()

        if not result.data:
            return "No documents found matching your criteria."

        # Format results
        output = [f"Found {len(result.data)} document(s):\n"]
        output.append("=" * 60)

        for i, doc in enumerate(result.data, 1):
            output.append(f"\n{i}. {safe_get(doc, 'original_filename', 'Unknown filename')}")
            output.append(f"   Type: {safe_get(doc, 'document_type', 'Unknown')}")
            output.append(f"   Party: {safe_get(doc, 'party_author', 'Unknown')}")
            output.append(f"   Relevancy: {safe_get(doc, 'relevancy_number', 0)}/1000")
            output.append(f"   Micro Score: {safe_get(doc, 'micro_number', 0)}/1000")

            if doc.get('categories'):
                cats = ', '.join(doc['categories'][:3])
                output.append(f"   Categories: {cats}")

            if doc.get('created_at'):
                output.append(f"   Date: {format_date(doc['created_at'])}")

            if doc.get('supabase_path'):
                output.append(f"   Path: {doc['supabase_path']}")

            output.append("")

        return "\n".join(output)

    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        return f"Error searching documents: {str(e)}"


async def get_action_items_impl(
    status: str = "all",
    priority: str = "all",
    limit: int = 50
) -> str:
    """
    Get action items and deadlines.
    Phase 1: Returns helpful message about Phase 2.
    Phase 2: Will connect to action_items table.
    """
    return (
        "📋 Action Items Feature - Coming in Phase 2\n"
        "=" * 50 + "\n\n"
        "This feature will track:\n"
        "• Court deadlines and filing dates\n"
        "• Required responses to motions\n"
        "• Evidence collection tasks\n"
        "• Witness interview scheduling\n"
        "• Document review priorities\n\n"
        "In the meantime, you can:\n"
        "1. Use get_timeline to see upcoming court dates\n"
        "2. Use search_documents to find recent filings\n"
        "3. Ask me to help you identify urgent tasks based on the case timeline\n\n"
        "Would you like me to check the timeline for upcoming deadlines?"
    )


async def generate_motion_impl(
    motion_type: str,
    grounds: str,
    relief_requested: str,
    supporting_evidence: list[str] = None
) -> str:
    """
    Generate motion outline.
    Phase 1: Returns structured template.
    Phase 2: Will generate full PDF with formatting.
    """
    output = [
        "=" * 70,
        "MOTION OUTLINE (Phase 1 - Template)",
        "=" * 70,
        "",
        f"MOTION TYPE: {motion_type}",
        "",
        "I. INTRODUCTION",
        f"   {motion_type} is filed on the following grounds:",
        f"   {grounds[:200]}...",
        "",
        "II. STATEMENT OF FACTS",
        "   [AI Analysis Note: Use search_documents to gather relevant evidence]",
        "   [AI Analysis Note: Use get_timeline to establish chronology]",
        "",
        "III. LEGAL ARGUMENT",
        f"   A. Grounds for Relief",
        f"      {grounds[:300]}...",
        "",
        "IV. RELIEF REQUESTED",
        f"   {relief_requested}",
        "",
        "V. SUPPORTING EVIDENCE",
    ]

    if supporting_evidence:
        for i, evidence in enumerate(supporting_evidence, 1):
            output.append(f"   {i}. {evidence}")
    else:
        output.append("   [Use search_documents to identify supporting evidence]")

    output.extend([
        "",
        "VI. CONCLUSION",
        "   For the foregoing reasons, the Court should grant this motion.",
        "",
        "=" * 70,
        "NOTE: This is a Phase 1 outline template.",
        "Phase 2 will generate full PDF with:",
        "  • Proper legal formatting and citations",
        "  • Integrated evidence references",
        "  • Automatic fact checking against database",
        "  • Truth scoring for all factual claims",
        "=" * 70
    ])

    return "\n".join(output)


# ============================================================================
# TOOL CALL HANDLER
# ============================================================================

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
    """Handle tool calls from Claude."""
    try:
        logger.info(f"Tool called: {name} with arguments: {arguments}")

        if name == "search_communications":
            result = await search_communications_impl(**arguments)
        elif name == "get_timeline":
            result = await get_timeline_impl(**arguments)
        elif name == "search_documents":
            result = await search_documents_impl(**arguments)
        elif name == "get_action_items":
            result = await get_action_items_impl(**arguments)
        elif name == "generate_motion":
            result = await generate_motion_impl(**arguments)
        else:
            result = f"Unknown tool: {name}"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        logger.error(f"Error in tool {name}: {e}", exc_info=True)
        error_msg = f"Error executing {name}: {str(e)}"
        return [TextContent(type="text", text=error_msg)]


# ============================================================================
# MAIN SERVER
# ============================================================================

async def main():
    """Run the MCP server."""
    logger.info("Starting ASEAGI MVP MCP Server...")
    logger.info("For Ashe - Protecting children through intelligent legal assistance")

    # Verify Supabase credentials
    try:
        get_supabase_client()
        logger.info("✓ Supabase connection verified")
    except Exception as e:
        logger.error(f"✗ Supabase connection failed: {e}")
        logger.error("Set SUPABASE_URL and SUPABASE_KEY environment variables")
        return

    # Run server
    async with stdio_server() as (read_stream, write_stream):
        logger.info("✓ MCP server ready - waiting for connections...")
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        exit(1)
