#!/usr/bin/env python3
"""
PROJ344: Court Events Timeline Dashboard
Visualize court filings, hearings, and deadlines with linked documents
"""

import streamlit as st
import os
from datetime import datetime, timedelta
import pandas as pd
from collections import Counter

try:
    from supabase import create_client
except ImportError:
    st.error("❌ Supabase library not installed. Run: pip3 install supabase")
    st.stop()

st.set_page_config(
    page_title="PROJ344: Court Events Tracker",
    page_icon="⚖️",
    layout="wide"
)

# ===== SUPABASE CONNECTION =====

@st.cache_resource
def init_supabase():
    """Initialize Supabase client"""
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')

    if not url or not key:
        return None, "Missing SUPABASE_URL or SUPABASE_KEY"

    try:
        client = create_client(url, key)
        # Test connection
        client.table('court_events').select('id', count='exact').limit(1).execute()
        return client, None
    except Exception as e:
        return None, str(e)

# ===== DATA QUERIES =====

@st.cache_data(ttl=30)
def get_all_events(_client):
    """Get all court events"""
    try:
        response = _client.table('court_events')\
            .select('*')\
            .order('event_date', desc=True)\
            .execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching events: {e}")
        return []

@st.cache_data(ttl=30)
def get_event_documents(_client, event_id):
    """Get all documents for an event"""
    try:
        response = _client.table('event_documents')\
            .select('*, legal_documents(*)')\
            .eq('event_id', event_id)\
            .execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching event documents: {e}")
        return []

@st.cache_data(ttl=30)
def get_upcoming_events(_client):
    """Get upcoming events view"""
    try:
        response = _client.table('upcoming_events')\
            .select('*')\
            .execute()
        return response.data
    except Exception as e:
        return []

@st.cache_data(ttl=30)
def get_events_by_case(_client):
    """Get events grouped by case"""
    try:
        response = _client.table('events_by_case')\
            .select('*')\
            .execute()
        return response.data
    except Exception as e:
        return []

@st.cache_data(ttl=30)
def get_critical_events(_client):
    """Get events requiring action"""
    try:
        response = _client.table('critical_events_action_required')\
            .select('*')\
            .execute()
        return response.data
    except Exception as e:
        return []

# ===== MAIN APP =====

def main():
    # Header
    st.title("⚖️ PROJ344: Court Events Timeline Tracker")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize Supabase
    client, error = init_supabase()

    if error:
        st.error(f"❌ **Supabase Connection Failed**")
        st.code(error)
        st.info("💡 **Fix:** Run `source ~/.supabase_file_system` to load credentials")
        st.stop()

    st.success("✅ Connected to Court Events Database")
    st.markdown("---")

    # ===== SIDEBAR =====
    st.sidebar.header("📊 View Mode")

    mode = st.sidebar.radio(
        "Select View",
        ["Event Timeline", "Upcoming Events", "Case Overview", "Critical Actions", "Event Detail", "Add Event"],
        help="Choose analysis mode"
    )

    # ===== EVENT TIMELINE MODE =====
    if mode == "Event Timeline":
        st.header("📅 Event Timeline")

        events = get_all_events(client)

        if not events:
            st.warning("No events found. Add events using 'Add Event' mode.")
            return

        # Filters
        col1, col2, col3 = st.columns(3)

        with col1:
            cases = list(set(e.get('case_number') for e in events if e.get('case_number')))
            selected_case = st.selectbox("Filter by Case", ["All"] + cases)

        with col2:
            event_types = list(set(e.get('event_type') for e in events if e.get('event_type')))
            selected_type = st.selectbox("Event Type", ["All"] + event_types)

        with col3:
            statuses = list(set(e.get('status') for e in events if e.get('status')))
            selected_status = st.selectbox("Status", ["All"] + statuses)

        # Apply filters
        filtered = events
        if selected_case != "All":
            filtered = [e for e in filtered if e.get('case_number') == selected_case]
        if selected_type != "All":
            filtered = [e for e in filtered if e.get('event_type') == selected_type]
        if selected_status != "All":
            filtered = [e for e in filtered if e.get('status') == selected_status]

        st.success(f"Showing {len(filtered)} events")

        # Timeline visualization
        for event in filtered:
            with st.expander(f"{event['event_date']} | {event['event_title']} ({event['event_type']})"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Case:** {event.get('case_number')} - {event.get('case_name', 'N/A')}")
                    st.write(f"**Jurisdiction:** {event.get('jurisdiction', 'N/A')}")
                    st.write(f"**Court:** {event.get('court_name', 'N/A')}")
                    st.write(f"**Judge:** {event.get('judge_name', 'N/A')}")

                with col2:
                    status_color = {
                        'GRANTED': '🟢',
                        'DENIED': '🔴',
                        'PENDING': '🟡',
                        'FILED': '🔵',
                        'COMPLETED': '✅'
                    }.get(event.get('status'), '⚪')

                    st.write(f"**Status:** {status_color} {event.get('status')}")
                    st.write(f"**Importance:** {event.get('importance')}")
                    st.write(f"**Urgency:** {event.get('urgency')}")

                    if event.get('response_required'):
                        if event.get('response_due_date'):
                            st.warning(f"⏰ Response Due: {event['response_due_date']}")

                if event.get('event_description'):
                    st.info(event['event_description'])

                # Show linked documents
                docs = get_event_documents(client, event['id'])
                if docs:
                    st.write(f"**📎 {len(docs)} Linked Documents:**")
                    for doc in docs:
                        legal_doc = doc.get('legal_documents', {})
                        role = doc.get('document_role', 'N/A')
                        time_rel = doc.get('time_relevance', 'N/A')
                        exhibit = doc.get('exhibit_number', '')

                        doc_title = legal_doc.get('document_title') or legal_doc.get('original_filename', 'Untitled')
                        st.write(f"  - {role}: {doc_title} ({time_rel}){' - ' + exhibit if exhibit else ''}")

    # ===== UPCOMING EVENTS MODE =====
    elif mode == "Upcoming Events":
        st.header("📆 Upcoming Events & Deadlines")

        upcoming = get_upcoming_events(client)

        if not upcoming:
            st.info("No upcoming events scheduled.")
            return

        # Group by urgency
        urgent = [e for e in upcoming if e.get('urgency') == 'URGENT']
        high = [e for e in upcoming if e.get('urgency') == 'HIGH']
        normal = [e for e in upcoming if e.get('urgency') in ('NORMAL', None)]

        if urgent:
            st.error(f"🚨 **{len(urgent)} URGENT Events**")
            for event in urgent:
                with st.expander(f"🔴 {event['event_title']} - Due: {event.get('response_due_date') or event.get('event_date')}"):
                    st.write(f"**Case:** {event['case_number']}")
                    st.write(f"**Type:** {event['event_type']}")
                    st.write(f"**Importance:** {event['importance']}")
                    if event.get('response_required'):
                        st.warning(f"Response Status: {event.get('response_status')}")
                    st.write(f"**Documents:** {event.get('attached_documents', 0)} ({event.get('key_evidence_count', 0)} key evidence)")

        if high:
            st.warning(f"⚠️ **{len(high)} High Priority Events**")
            for event in high:
                st.write(f"- {event['event_title']} ({event['event_date']})")

        if normal:
            st.info(f"📋 **{len(normal)} Normal Priority Events**")

    # ===== CASE OVERVIEW MODE =====
    elif mode == "Case Overview":
        st.header("📂 Case Overview")

        cases = get_events_by_case(client)

        if not cases:
            st.warning("No cases found.")
            return

        for case in cases:
            with st.expander(f"{case['case_number']} - {case['case_name']}"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total Events", case['total_events'])
                    st.metric("Filings", case['filings'])

                with col2:
                    st.metric("Hearings", case['hearings'])
                    st.metric("Orders", case['orders'])

                with col3:
                    st.metric("Pending", case['pending_events'])
                    st.metric("Responses Needed", case['responses_needed'])

                st.write(f"**Jurisdiction:** {case['jurisdiction']}")
                st.write(f"**First Event:** {case.get('first_event', 'N/A')}")
                st.write(f"**Latest Event:** {case.get('latest_event', 'N/A')}")

                if case.get('next_deadline'):
                    st.warning(f"**Next Deadline:** {case['next_deadline']}")

    # ===== CRITICAL ACTIONS MODE =====
    elif mode == "Critical Actions":
        st.header("🚨 Critical Events Requiring Action")

        critical = get_critical_events(client)

        if not critical:
            st.success("✅ No critical actions required!")
            return

        st.error(f"**{len(critical)} events require immediate attention**")

        for event in critical:
            days_status = event.get('days_overdue', 0)
            if days_status < 0:
                status_text = f"⏰ Overdue by {abs(days_status)} days"
                color = 'error'
            else:
                status_text = f"Due in {days_status} days"
                color = 'warning'

            with st.expander(f"{event['event_title']} - {status_text}"):
                st.write(f"**Case:** {event['case_number']}")
                st.write(f"**Response Due:** {event.get('response_due_date')}")
                st.write(f"**Status:** {event.get('response_status')}")
                st.write(f"**Importance:** {event.get('importance')}")
                st.write(f"**Primary Documents:** {event.get('primary_docs', 0)}")
                st.write(f"**Key Evidence:** {event.get('key_evidence', 0)}")

    # ===== EVENT DETAIL MODE =====
    elif mode == "Event Detail":
        st.header("🔍 Event Detail View")

        events = get_all_events(client)

        if not events:
            st.warning("No events found.")
            return

        # Select event
        event_titles = [f"[{e['event_date']}] {e['event_title']}" for e in events]
        selected = st.selectbox("Select Event", event_titles)

        if selected:
            idx = event_titles.index(selected)
            event = events[idx]

            st.subheader(event['event_title'])

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Event Type", event['event_type'])
                st.metric("Status", event['status'])

            with col2:
                st.metric("Importance", event['importance'])
                st.metric("Urgency", event['urgency'])

            with col3:
                st.metric("Event Date", event['event_date'])
                if event.get('response_due_date'):
                    st.metric("Response Due", event['response_due_date'])

            st.markdown("---")

            st.write(f"**Case:** {event['case_number']} - {event.get('case_name', 'N/A')}")
            st.write(f"**Jurisdiction:** {event['jurisdiction']}")
            st.write(f"**Court:** {event.get('court_name', 'N/A')}")
            st.write(f"**Judge:** {event.get('judge_name', 'N/A')}")

            if event.get('event_description'):
                st.info(event['event_description'])

            # Linked documents
            st.markdown("---")
            st.subheader("📎 Linked Documents")

            docs = get_event_documents(client, event['id'])

            if docs:
                for doc in docs:
                    legal_doc = doc.get('legal_documents', {})
                    with st.expander(f"{doc.get('document_role')}: {legal_doc.get('document_title') or legal_doc.get('original_filename')}"):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write(f"**Role:** {doc.get('document_role')}")
                            st.write(f"**Time Relevance:** {doc.get('time_relevance')}")
                            if doc.get('exhibit_number'):
                                st.write(f"**Exhibit:** {doc['exhibit_number']}")

                        with col2:
                            st.write(f"**Filed with Court:** {'Yes' if doc.get('filed_with_court') else 'No'}")
                            if doc.get('filing_date'):
                                st.write(f"**Filing Date:** {doc['filing_date']}")
                            st.write(f"**Key Evidence:** {'Yes' if doc.get('is_key_evidence') else 'No'}")

                        if legal_doc.get('executive_summary'):
                            st.info(legal_doc['executive_summary'])
            else:
                st.warning("No documents linked to this event yet.")

    # ===== ADD EVENT MODE =====
    elif mode == "Add Event":
        st.header("➕ Add New Event")

        with st.form("add_event_form"):
            col1, col2 = st.columns(2)

            with col1:
                case_number = st.text_input("Case Number*", placeholder="e.g., J24-00478")
                case_name = st.text_input("Case Name", placeholder="e.g., In re Ashe B.")
                event_type = st.selectbox("Event Type*", [
                    "FILING", "HEARING", "ORDER", "DEADLINE",
                    "CORRESPONDENCE", "DISCOVERY", "SETTLEMENT", "APPEAL"
                ])
                event_title = st.text_input("Event Title*", placeholder="e.g., Motion to Reopen")

            with col2:
                event_date = st.date_input("Event Date*")
                jurisdiction = st.text_input("Jurisdiction*", placeholder="e.g., Alameda County")
                importance = st.selectbox("Importance", ["CRITICAL", "HIGH", "MEDIUM", "LOW"])
                urgency = st.selectbox("Urgency", ["URGENT", "HIGH", "NORMAL", "LOW"])

            event_description = st.text_area("Event Description")

            col1, col2 = st.columns(2)
            with col1:
                response_required = st.checkbox("Response Required")
            with col2:
                if response_required:
                    response_due_date = st.date_input("Response Due Date")
                else:
                    response_due_date = None

            submitted = st.form_submit_button("Create Event")

            if submitted:
                if not all([case_number, event_type, event_title, event_date, jurisdiction]):
                    st.error("Please fill in all required fields (marked with *)")
                else:
                    try:
                        new_event = {
                            'case_number': case_number,
                            'case_name': case_name,
                            'event_type': event_type,
                            'event_title': event_title,
                            'event_date': str(event_date),
                            'jurisdiction': jurisdiction,
                            'importance': importance,
                            'urgency': urgency,
                            'event_description': event_description,
                            'response_required': response_required,
                            'response_due_date': str(response_due_date) if response_due_date else None,
                            'status': 'PENDING'
                        }

                        result = client.table('court_events').insert(new_event).execute()
                        st.success(f"✅ Event created successfully! ID: {result.data[0]['id'][:8]}...")
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"Error creating event: {e}")

    # Footer
    st.markdown("---")
    st.caption(f"🔗 PROJ344: Multi-Jurisdiction Legal Case Tracker")

if __name__ == "__main__":
    main()
