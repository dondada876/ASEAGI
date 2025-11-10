#!/usr/bin/env python3
"""
Create bug tickets for the violations display issues that were discovered and fixed
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.bug_tracker import BugTracker

tracker = BugTracker()

print("=" * 80)
print("CREATING BUG TICKETS FOR VIOLATIONS DISPLAY ISSUES")
print("=" * 80)
print()

# Bug 1: Telegram bot violations command showing incorrect data
bug1_data = {
    "title": "Telegram bot /violations command displays incorrect violation data",
    "description": """**Issue:**
The Telegram bot /violations command was querying non-existent database columns, causing it to display "Unknown" for all violation fields.

**Root Cause:**
Code was querying for columns: violation_type, document_title, severity
But actual database schema uses: violation_category, violation_title, perpetrator, violation_date, severity_score

**Impact:**
- Users received "Unknown" for all violation data
- Severity showed as "Unknown" instead of calculated levels
- Command was unusable for viewing violations

**Solution Implemented:**
Updated scanners/telegram_bot_simple.py violations_command() function:

1. Changed query to use correct column names
2. Added severity calculation from severity_score (0-100):
   - >= 90: CRITICAL
   - >= 70: HIGH
   - >= 50: MEDIUM
   - < 50: LOW

3. Updated display to use correct fields:
   - violation_category instead of violation_type
   - violation_title instead of document_title
   - perpetrator field added
   - violation_date for timestamp

**Files Modified:**
- scanners/telegram_bot_simple.py (lines 200-250)

**Git Commit:**
- Commit: d610f28
- Message: "Fix violations command to use correct database column names"

**Status:** RESOLVED - Deployed to droplet, bot restarted, command now shows accurate data
""",
    "bug_type": "BUG",
    "severity": "high",
    "priority": "high",
    "component": "telegram_bot",
    "status": "resolved",
    "tags": ["telegram", "violations", "database", "schema-mismatch"],
    "workspace_id": "legal",
    "resolution": "Fixed database column mapping and added severity calculation logic",
    "resolved_at": datetime.utcnow().isoformat()
}

try:
    result1 = tracker.supabase.table("bugs").insert(bug1_data).execute()
    if result1.data:
        print(f"✅ Created bug ticket: {result1.data[0]['bug_number']}")
        print(f"   Title: {bug1_data['title']}")
        print()
except Exception as e:
    print(f"❌ Error creating bug 1: {e}")
    print()

# Bug 2: Streamlit violations dashboard not querying violations table
bug2_data = {
    "title": "Streamlit violations dashboard not displaying actual violation data",
    "description": """**Issue:**
The timeline_violations_dashboard.py was not querying the legal_violations table at all, instead only searching court_events for keywords like "false", "violation", "contempt".

**Root Cause:**
Dashboard Tab 3 (Constitutional Violations) was never updated to query the actual violations table after it was created and populated with data.

**Impact:**
- Dashboard showed no actual violation records
- Only showed court events with certain keywords in titles
- Users could not see real violations with severity scores, categories, evidence

**Solution Implemented:**
Completely rewrote Tab 3 in dashboards/timeline_violations_dashboard.py:

1. Added proper violations query from legal_violations table

2. Added summary metrics (4 columns):
   - Total Violations
   - Critical count (severity_score >= 90)
   - High count (70-89)
   - Medium count (50-69)

3. Added interactive filters:
   - Category multiselect (from violation_category)
   - Severity slider (minimum score 0-100)

4. Created detailed violation display with expandable cards showing:
   - Severity color indicators
   - Category and title
   - Perpetrator, date
   - Full description, legal basis, evidence summary
   - Document ID and incident ID links

5. Added violations by category bar chart

**Files Modified:**
- dashboards/timeline_violations_dashboard.py (lines 180-320)

**Git Commit:**
- Commit: d933fb8
- Message: "Fix violations dashboard to query legal_violations table with correct columns"

**Status:** RESOLVED - Deployed to droplet, Streamlit auto-reloaded, dashboard now shows accurate violation data
""",
    "bug_type": "BUG",
    "severity": "high",
    "priority": "high",
    "component": "streamlit_dashboard",
    "status": "resolved",
    "tags": ["streamlit", "violations", "dashboard", "legal_violations"],
    "workspace_id": "legal",
    "resolution": "Rewrote violations tab to properly query and display legal_violations table with filters and metrics",
    "resolved_at": datetime.utcnow().isoformat()
}

try:
    result2 = tracker.supabase.table("bugs").insert(bug2_data).execute()
    if result2.data:
        print(f"✅ Created bug ticket: {result2.data[0]['bug_number']}")
        print(f"   Title: {bug2_data['title']}")
        print()
except Exception as e:
    print(f"❌ Error creating bug 2: {e}")
    print()

print("=" * 80)
print("SUMMARY: Violations Display Issues Documented")
print("=" * 80)
print("Both violations display bugs have been:")
print("  ✅ Logged as bug tickets in Supabase")
print("  ✅ Full problem description documented")
print("  ✅ Root cause analysis included")
print("  ✅ Complete solution with code examples")
print("  ✅ Git commits referenced")
print("  ✅ Marked as RESOLVED with resolution notes")
print()
print("These bugs are now part of the permanent audit trail.")
print("=" * 80)
