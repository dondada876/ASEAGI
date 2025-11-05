#!/usr/bin/env python3
"""
Timeline Constitutional Violations Tracker
Cross-references court events with evidence to identify violations
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from supabase import create_client

# Supabase connection
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://jvjlhxodmbkodzmggwpu.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2amxoeG9kbWJrb2R6bWdnd3B1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyMjMxOTAsImV4cCI6MjA3Nzc5OTE5MH0.ai65vVW816bNAV56XiuRxp5PE5IhBkMGPx3IbxfPh8c')

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

st.set_page_config(page_title="Timeline & Constitutional Violations", layout="wide")

# Header
st.title("⚖️ Timeline & Constitutional Violations Tracker")
st.markdown("**Case D22-03244** | Cross-referencing court events with evidence")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📅 Timeline Analysis",
    "🚨 August 2024 Incident",
    "⚠️ Constitutional Violations",
    "📊 Evidence Cross-Reference"
])

# ============================================================================
# TAB 1: TIMELINE ANALYSIS
# ============================================================================
with tab1:
    st.header("Complete Timeline: Events + Evidence")

    col1, col2 = st.columns([3, 1])

    with col2:
        st.subheader("Filters")
        date_range = st.date_input(
            "Date Range",
            value=(datetime(2022, 8, 1), datetime.now()),
            key="timeline_dates"
        )

        event_types = st.multiselect(
            "Event Types",
            ["HEARING", "FILING", "ORDER", "EX_PARTE", "APPEAL", "SERVICE", "GENERAL"],
            default=["HEARING", "EX_PARTE", "ORDER"]
        )

    with col1:
        # Get court events
        try:
            events_response = supabase.table('court_events')\
                .select('event_date, event_type, event_title, event_description, judge_name, event_outcome')\
                .gte('event_date', date_range[0].isoformat())\
                .lte('event_date', date_range[1].isoformat())\
                .order('event_date', desc=True)\
                .execute()

            events_df = pd.DataFrame(events_response.data)

            if not events_df.empty and event_types:
                events_df = events_df[events_df['event_type'].isin(event_types)]

            # Get legal documents with relevancy scores
            docs_response = supabase.table('legal_documents')\
                .select('processed_at, original_filename, relevancy_number, fraud_score, document_type')\
                .execute()

            docs_df = pd.DataFrame(docs_response.data)

            # Display timeline
            st.subheader(f"📊 {len(events_df)} Court Events")

            if not events_df.empty:
                # Add indicator column
                events_df['type'] = '⚖️ Court Event'

                display_df = events_df[['event_date', 'type', 'event_type', 'event_title', 'judge_name', 'event_outcome']]
                display_df.columns = ['Date', 'Category', 'Type', 'Event', 'Judge', 'Outcome']

                st.dataframe(display_df, width='stretch', height=500)

                # Timeline chart
                st.subheader("📈 Event Frequency Over Time")
                events_df['event_date'] = pd.to_datetime(events_df['event_date'])
                events_by_month = events_df.groupby(events_df['event_date'].dt.to_period('M')).size()
                st.bar_chart(events_by_month)
            else:
                st.info("No events found for selected filters")

        except Exception as e:
            st.error(f"Error loading timeline: {e}")

# ============================================================================
# TAB 2: AUGUST 2024 INCIDENT
# ============================================================================
with tab2:
    st.header("🚨 August 10-13, 2024: Constitutional Violation Analysis")

    st.markdown("""
    ### Incident Summary
    - **August 10, 2024 (midnight)**: Police report documents child was **SAFE** with father
    - **August 13, 2024**: Ex Parte filed claiming violation
    - **Issue**: Police report contradicts ex parte claims, proves child was safe
    - **Constitutional Concern**: Evidence of false claims in restraining order proceedings
    """)

    # Get events from Aug 10-20, 2024
    try:
        aug_events = supabase.table('court_events')\
            .select('*')\
            .gte('event_date', '2024-08-10')\
            .lte('event_date', '2024-08-20')\
            .order('event_date')\
            .execute()

        aug_df = pd.DataFrame(aug_events.data)

        if not aug_df.empty:
            st.subheader("📅 Court Events During Incident Period")

            # Highlight the key events
            for _, event in aug_df.iterrows():
                event_date = event['event_date']
                event_title = event['event_title']

                if 'Ex Parte' in event_title or 'Exparte' in event_title:
                    st.error(f"**{event_date}** - 🚨 {event_title}")
                    st.markdown(f"- Type: {event.get('event_type', 'N/A')}")
                    st.markdown(f"- Description: {event.get('event_description', 'N/A')}")
                    st.markdown("---")
                elif 'Request for Order' in event_title:
                    st.warning(f"**{event_date}** - ⚠️ {event_title}")
                    st.markdown(f"- Type: {event.get('event_type', 'N/A')}")
                    st.markdown("---")
                else:
                    st.info(f"**{event_date}** - {event_title}")

            st.subheader("🔍 Evidence Analysis")
            st.markdown("""
            **Police Report (August 10, 2024 - midnight)**
            - Documents: Child was **SAFE** with father
            - Contradicts: Ex parte filed 3 days later on August 13
            - Constitutional Issue: Filing made false claims despite police documentation
            - Violation Type: **Due Process** - False evidence in restraining order proceedings
            - Statute: **Penal Code 273.6** violation claims contradicted by official police report
            """)

            # Check for related documents
            docs_check = supabase.table('legal_documents')\
                .select('*')\
                .ilike('original_filename', '%police%')\
                .execute()

            if docs_check.data:
                st.success(f"✅ Found {len(docs_check.data)} police report(s) in database")
                for doc in docs_check.data:
                    st.markdown(f"- **{doc['original_filename']}** (Relevancy: {doc.get('relevancy_number', 'N/A')})")
            else:
                st.warning("⚠️ Police report not yet in database - needs to be uploaded and analyzed")
        else:
            st.info("No court events found during this period")

    except Exception as e:
        st.error(f"Error loading August 2024 data: {e}")

# ============================================================================
# TAB 3: CONSTITUTIONAL VIOLATIONS
# ============================================================================
with tab3:
    st.header("⚠️ Constitutional Violations Tracker")

    # Violation categories
    st.subheader("📋 Violation Categories")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Due Process Violations:**
        - False evidence in court filings
        - Denial of parental rights without hearing
        - Improper service of documents
        - Violation of discovery rules
        """)

    with col2:
        st.markdown("""
        **Equal Protection Violations:**
        - Gender bias in custody decisions
        - Disparate treatment of parties
        - Unequal access to evidence
        """)

    # Get events with constitutional issues
    try:
        violations_response = supabase.table('court_events')\
            .select('event_date, event_title, event_description, event_type, judge_name')\
            .or_('event_title.ilike.%false%,event_title.ilike.%violation%,event_title.ilike.%contempt%')\
            .order('event_date', desc=True)\
            .execute()

        violations_df = pd.DataFrame(violations_response.data)

        if not violations_df.empty:
            st.subheader(f"🚨 {len(violations_df)} Potential Constitutional Issues")
            st.dataframe(violations_df, width='stretch')
        else:
            st.info("No flagged violations found in event titles")

        # Manual violation tracking
        st.subheader("➕ Add Constitutional Violation")

        with st.form("add_violation"):
            viol_date = st.date_input("Date of Violation")
            viol_type = st.selectbox("Violation Type", [
                "Due Process - False Evidence",
                "Due Process - Denial of Hearing",
                "Equal Protection - Gender Bias",
                "Fourth Amendment - Unlawful Search",
                "First Amendment - Speech Restriction",
                "Other"
            ])
            viol_desc = st.text_area("Description")
            related_event = st.text_input("Related Court Event")
            evidence_refs = st.text_input("Evidence References (file names)")

            submitted = st.form_submit_button("Add Violation")
            if submitted:
                st.success("✅ Violation logged (feature in development)")

    except Exception as e:
        st.error(f"Error loading violations: {e}")

# ============================================================================
# TAB 4: EVIDENCE CROSS-REFERENCE
# ============================================================================
with tab4:
    st.header("📊 Evidence Cross-Reference: Documents × Events")

    st.markdown("""
    This view links **legal documents** (with relevancy scores) to **court events**
    to identify which evidence supports or contradicts court filings.
    """)

    try:
        # Get all documents with scores
        docs_response = supabase.table('legal_documents')\
            .select('original_filename, relevancy_number, fraud_score, document_type, processed_at, file_extension')\
            .order('relevancy_number', desc=True)\
            .execute()

        docs_df = pd.DataFrame(docs_response.data)

        if not docs_df.empty:
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Documents", len(docs_df))
            with col2:
                high_relevancy = len(docs_df[docs_df['relevancy_number'] >= 700])
                st.metric("High Relevancy (≥700)", high_relevancy)
            with col3:
                high_fraud = len(docs_df[docs_df['fraud_score'] >= 70])
                st.metric("High Fraud Score (≥70)", high_fraud)

            st.subheader("📄 Documents with Relevancy & Fraud Scores")

            # Add filters
            min_relevancy = st.slider("Minimum Relevancy Score", 0, 999, 500)

            filtered_docs = docs_df[docs_df['relevancy_number'] >= min_relevancy]

            # Display with color coding
            def color_relevancy(val):
                if val >= 800:
                    return 'background-color: #d4edda'  # Green
                elif val >= 600:
                    return 'background-color: #fff3cd'  # Yellow
                else:
                    return 'background-color: #f8d7da'  # Red

            st.dataframe(
                filtered_docs.style.applymap(color_relevancy, subset=['relevancy_number']),
                width='stretch'
            )

            # Cross-reference builder
            st.subheader("🔗 Link Document to Court Event")

            col1, col2 = st.columns(2)

            with col1:
                selected_doc = st.selectbox(
                    "Select Document",
                    docs_df['original_filename'].tolist() if not docs_df.empty else []
                )

            with col2:
                # Get recent events
                events_response = supabase.table('court_events')\
                    .select('event_date, event_title')\
                    .order('event_date', desc=True)\
                    .limit(50)\
                    .execute()

                event_options = [f"{e['event_date']} - {e['event_title']}" for e in events_response.data]
                selected_event = st.selectbox("Select Court Event", event_options)

            link_type = st.selectbox("Relationship", [
                "Supports Event",
                "Contradicts Event",
                "Filed With Event",
                "Evidence For Event",
                "Referenced In Event"
            ])

            if st.button("Create Link"):
                st.success("✅ Link created (feature in development - will add to junction table)")

        else:
            st.info("No documents found in database")

    except Exception as e:
        st.error(f"Error loading evidence: {e}")

# Footer
st.markdown("---")
st.markdown("**Data Sources:** Supabase (court_events + legal_documents) | **Last Updated:** " + datetime.now().strftime("%Y-%m-%d %H:%M"))
