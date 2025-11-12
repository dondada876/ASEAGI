#!/usr/bin/env python3
"""
Query and display Vtiger CRM tickets
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.vtiger_sync import VtigerIntegration
from datetime import datetime

def display_tickets():
    """Fetch and display all Vtiger tickets"""

    print("\n" + "=" * 80)
    print("📋 VTIGER CRM TICKETS")
    print("=" * 80 + "\n")

    # Initialize Vtiger
    vtiger = VtigerIntegration()

    # Check if enabled
    if not vtiger.enabled:
        print("⚠️  Vtiger integration is DISABLED")
        print("\nTo enable, set in .env:")
        print("  VTIGER_ENABLED=true")
        print("  VTIGER_URL=https://your-crm.od2.vtiger.com")
        print("  VTIGER_USERNAME=your_username")
        print("  VTIGER_ACCESS_KEY=your_access_key")
        return

    # Authenticate
    print("🔐 Connecting to Vtiger...")
    if not vtiger.authenticate():
        print("\n❌ Failed to connect to Vtiger")
        print("Check your credentials in .env file")
        return

    print("✅ Connected successfully!\n")

    # Query tickets
    queries = {
        "All Tickets": "SELECT * FROM HelpDesk ORDER BY createdtime DESC LIMIT 50;",
        "Open Tickets": "SELECT * FROM HelpDesk WHERE ticketstatus='Open' ORDER BY createdtime DESC;",
        "In Progress": "SELECT * FROM HelpDesk WHERE ticketstatus='In Progress' ORDER BY createdtime DESC;",
        "Closed Today": "SELECT * FROM HelpDesk WHERE ticketstatus='Closed' AND DATE(modifiedtime) = CURDATE();",
        "High Priority": "SELECT * FROM HelpDesk WHERE ticketpriorities='High' ORDER BY createdtime DESC LIMIT 20;",
    }

    for query_name, query in queries.items():
        print(f"\n{'─' * 80}")
        print(f"📌 {query_name}")
        print('─' * 80)

        tickets = vtiger.query_tickets(query)

        if not tickets:
            print(f"  No tickets found")
            continue

        print(f"  Found {len(tickets)} ticket(s)\n")

        for i, ticket in enumerate(tickets, 1):
            ticket_no = ticket.get('ticket_no', 'N/A')
            title = ticket.get('ticket_title', 'Untitled')
            status = ticket.get('ticketstatus', 'Unknown')
            priority = ticket.get('ticketpriorities', 'Normal')
            severity = ticket.get('ticketseverity', 'N/A')
            created = ticket.get('createdtime', 'N/A')

            # Format created date
            if created != 'N/A':
                try:
                    created_dt = datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
                    created = created_dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass

            # Status emoji
            status_emoji = {
                'Open': '🔴',
                'In Progress': '🟡',
                'Closed': '✅',
                'Wait For Response': '⏸️'
            }.get(status, '📋')

            # Priority emoji
            priority_emoji = {
                'High': '🔥',
                'Normal': '📌',
                'Low': '🟢'
            }.get(priority, '📌')

            print(f"  {i}. {status_emoji} #{ticket_no} - {title[:60]}")
            print(f"     Status: {status} | Priority: {priority_emoji} {priority} | Severity: {severity}")
            print(f"     Created: {created}")

            if ticket.get('description'):
                desc = ticket['description'][:100]
                print(f"     {desc}{'...' if len(ticket.get('description', '')) > 100 else ''}")

            print()

    print("\n" + "=" * 80)
    print("✅ QUERY COMPLETE")
    print("=" * 80 + "\n")

def display_ticket_stats():
    """Display ticket statistics"""

    vtiger = VtigerIntegration()

    if not vtiger.authenticate():
        return

    print("\n" + "=" * 80)
    print("📊 TICKET STATISTICS")
    print("=" * 80 + "\n")

    stats_queries = {
        "Total Tickets": "SELECT COUNT(*) as count FROM HelpDesk;",
        "Open": "SELECT COUNT(*) as count FROM HelpDesk WHERE ticketstatus='Open';",
        "In Progress": "SELECT COUNT(*) as count FROM HelpDesk WHERE ticketstatus='In Progress';",
        "Closed": "SELECT COUNT(*) as count FROM HelpDesk WHERE ticketstatus='Closed';",
        "High Priority": "SELECT COUNT(*) as count FROM HelpDesk WHERE ticketpriorities='High';",
        "Critical Severity": "SELECT COUNT(*) as count FROM HelpDesk WHERE ticketseverity='Critical';",
    }

    for stat_name, query in stats_queries.items():
        try:
            result = vtiger.query_tickets(query)
            if result and len(result) > 0:
                count = result[0].get('count', 0)
                print(f"  {stat_name}: {count}")
        except:
            print(f"  {stat_name}: Error")

    print("\n" + "=" * 80 + "\n")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='View Vtiger CRM tickets')
    parser.add_argument('--stats', action='store_true', help='Show statistics only')
    args = parser.parse_args()

    if args.stats:
        display_ticket_stats()
    else:
        display_tickets()
        display_ticket_stats()
