#!/usr/bin/env python3
"""
PROJ344 Master Dashboard
Comprehensive visualization of all legal case data across 39 tables and 52 views
"""

import streamlit as st
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import json

try:
    from supabase import create_client
except ImportError:
    st.error("❌ Install supabase: pip3 install supabase")
    st.stop()

st.set_page_config(
    page_title="PROJ344 Master Dashboard",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SUPABASE CONNECTION
# ============================================================================

@st.cache_resource
def init_supabase():
    """Initialize Supabase client"""
    url = os.environ.get('SUPABASE_URL', 'https://jvjlhxodmbkodzmggwpu.supabase.co')
    key = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2amxoeG9kbWJrb2R6bWdnd3B1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyMjMxOTAsImV4cCI6MjA3Nzc5OTE5MH0.ai65vVW816bNAV56XiuRxp5PE5IhBkMGPx3IbxfPh8c')

    try:
        client = create_client(url, key)
        return client, None
    except Exception as e:
        return None, str(e)

# ============================================================================
# DATA QUERIES
# ============================================================================

@st.cache_data(ttl=60)
def query_table(_client, table_name, limit=1000):
    """Generic table query"""
    try:
        response = _client.table(table_name).select('*').limit(limit).execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def query_view(_client, view_name, limit=1000):
    """Generic view query"""
    return query_table(_client, view_name, limit)

@st.cache_data(ttl=60)
def get_system_stats(_client):
    """Get system-wide statistics"""
    stats = {}

    # Count records in key tables
    tables_to_count = [
        'legal_documents', 'court_events', 'legal_violations',
        'document_pages', 'communications_matrix', 'dvro_violations_tracker',
        'court_case_tracker', 'legal_citations'
    ]

    for table in tables_to_count:
        try:
            response = _client.table(table).select('id', count='exact').limit(0).execute()
            stats[f'{table}_count'] = response.count
        except:
            stats[f'{table}_count'] = 0

    return stats

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

def main():
    # Initialize
    client, error = init_supabase()

    if error or not client:
        st.error(f"❌ Supabase connection failed: {error}")
        st.stop()

    st.title("⚖️ PROJ344: Legal Case Intelligence Dashboard")
    st.markdown(f"**Case:** In re Ashe B., J24-00478 | **Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Sidebar navigation
    st.sidebar.title("📊 Navigation")
    page = st.sidebar.radio("Select View", [
        "🏠 Overview",
        "📄 Documents Intelligence",
        "⚖️ Legal Violations",
        "📅 Court Events & Timeline",
        "🔬 Micro Document Analysis",
        "👥 Multi-Jurisdiction Tracker",
        "💬 Communications Analysis",
        "🎯 Critical Actions Required"
    ])

    # Load system stats
    stats = get_system_stats(client)

    # ========================================================================
    # PAGE: OVERVIEW
    # ========================================================================
    if page == "🏠 Overview":
        st.header("System Overview")

        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📄 Legal Documents", stats.get('legal_documents_count', 0))
        col2.metric("⚖️ Violations Tracked", stats.get('legal_violations_count', 0))
        col3.metric("📅 Court Events", stats.get('court_events_count', 0))
        col4.metric("🔬 Pages Analyzed", stats.get('document_pages_count', 0))

        col5, col6, col7, col8 = st.columns(4)
        col5.metric("💬 Communications", stats.get('communications_matrix_count', 0))
        col6.metric("🚫 DVRO Violations", stats.get('dvro_violations_tracker_count', 0))
        col7.metric("🏛️ Court Cases", stats.get('court_case_tracker_count', 0))
        col8.metric("📚 Legal Citations", stats.get('legal_citations_count', 0))

        # Critical documents
        st.subheader("🔥 Critical Documents (Relevancy 900+)")
        critical_docs = query_view(client, 'critical_documents', limit=10)
        if not critical_docs.empty:
            # Use actual column names from the view
            display_cols = []
            if 'renamed_filename' in critical_docs.columns:
                display_cols.append('renamed_filename')
            if 'document_type' in critical_docs.columns:
                display_cols.append('document_type')
            if 'relevancy_number' in critical_docs.columns:
                display_cols.append('relevancy_number')
            if 'micro_number' in critical_docs.columns:
                display_cols.append('micro_number')
            if 'macro_number' in critical_docs.columns:
                display_cols.append('macro_number')
            if 'legal_number' in critical_docs.columns:
                display_cols.append('legal_number')
            if 'executive_summary' in critical_docs.columns:
                display_cols.append('executive_summary')

            st.dataframe(critical_docs[display_cols].head(10), use_container_width=True)
        else:
            st.info("No critical documents found")

        # Recent activity
        st.subheader("📊 Recent Activity")
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**Recent Court Events**")
            recent_events = query_table(client, 'court_events', limit=5)
            if not recent_events.empty:
                for _, event in recent_events.iterrows():
                    st.markdown(f"- **{event.get('event_date')}**: {event.get('event_title')}")

        with col_b:
            st.markdown("**Critical Violations**")
            critical_violations = query_view(client, 'critical_violations', limit=5)
            if not critical_violations.empty:
                for _, vio in critical_violations.iterrows():
                    st.markdown(f"- **{vio.get('violation_title')}** (Score: {vio.get('severity_score')})")

    # ========================================================================
    # PAGE: DOCUMENTS INTELLIGENCE
    # ========================================================================
    elif page == "📄 Documents Intelligence":
        st.header("📄 Documents Intelligence")

        # Document distribution
        docs = query_table(client, 'legal_documents')

        if not docs.empty:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Documents by Type")
                type_counts = docs['document_type'].value_counts()
                fig = px.pie(values=type_counts.values, names=type_counts.index, title="Document Types")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Documents by Importance")
                importance_counts = docs['importance'].value_counts()
                fig = px.bar(x=importance_counts.index, y=importance_counts.values, title="Importance Distribution")
                st.plotly_chart(fig, use_container_width=True)

            # Relevancy score distribution
            st.subheader("Relevancy Score Distribution")
            fig = px.histogram(docs, x='relevancy_number', nbins=20, title="Relevancy Scores")
            st.plotly_chart(fig, use_container_width=True)

            # Top scoring documents
            st.subheader("Top 20 Documents by Relevancy")
            top_docs = docs.nlargest(20, 'relevancy_number')

            # Select available columns
            display_cols = ['relevancy_number', 'micro_number', 'macro_number', 'legal_number']
            if 'original_filename' in docs.columns:
                display_cols.insert(0, 'original_filename')
            elif 'renamed_filename' in docs.columns:
                display_cols.insert(0, 'renamed_filename')
            if 'document_type' in docs.columns:
                display_cols.append('document_type')
            if 'importance' in docs.columns:
                display_cols.append('importance')

            st.dataframe(top_docs[display_cols], use_container_width=True)

    # ========================================================================
    # PAGE: LEGAL VIOLATIONS
    # ========================================================================
    elif page == "⚖️ Legal Violations":
        st.header("⚖️ Legal Violations Tracker")

        violations = query_table(client, 'legal_violations')

        if not violations.empty:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Violations", len(violations))
            col2.metric("Avg Severity", f"{violations['severity_score'].mean():.1f}")
            col3.metric("Avg Proof Strength", f"{violations['proof_strength_score'].mean():.1f}")

            # Violations by category
            st.subheader("Violations by Category")
            if 'violation_category' in violations.columns:
                category_counts = violations['violation_category'].value_counts()
                fig = px.bar(x=category_counts.index, y=category_counts.values, title="Violation Categories")
                st.plotly_chart(fig, use_container_width=True)

            # Violations by perpetrator
            st.subheader("Violations by Perpetrator")
            violations_by_perp = query_view(client, 'violations_by_perpetrator')
            if not violations_by_perp.empty:
                st.dataframe(violations_by_perp, use_container_width=True)

            # Timeline
            st.subheader("Violations Timeline")
            violations_timeline = query_view(client, 'violations_timeline')
            if not violations_timeline.empty and 'violation_date' in violations_timeline.columns:
                # Check which columns are available
                size_col = 'proof_strength_score' if 'proof_strength_score' in violations_timeline.columns else None
                hover_cols = ['violation_title'] if 'violation_title' in violations_timeline.columns else None

                fig = px.scatter(violations_timeline, x='violation_date', y='severity_score',
                               size=size_col, hover_data=hover_cols,
                               title="Violations Over Time")
                st.plotly_chart(fig, use_container_width=True)

    # ========================================================================
    # PAGE: COURT EVENTS & TIMELINE
    # ========================================================================
    elif page == "📅 Court Events & Timeline":
        st.header("📅 Court Events & Timeline")

        events = query_table(client, 'court_events')

        if not events.empty:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Events", len(events))
            col2.metric("Upcoming Events", len(events[events['event_date'] >= str(datetime.now().date())]))
            col3.metric("Past Events", len(events[events['event_date'] < str(datetime.now().date())]))

            # Events by type
            st.subheader("Events by Type")
            type_counts = events['event_type'].value_counts()
            fig = px.pie(values=type_counts.values, names=type_counts.index, title="Event Types")
            st.plotly_chart(fig, use_container_width=True)

            # Upcoming events
            st.subheader("🔔 Upcoming Events")
            upcoming = query_view(client, 'upcoming_events')
            if not upcoming.empty:
                st.dataframe(upcoming, use_container_width=True)

            # Complete timeline
            st.subheader("Complete Case Timeline")
            timeline = query_view(client, 'complete_case_timeline')
            if not timeline.empty:
                st.dataframe(timeline.head(50), use_container_width=True)

    # ========================================================================
    # PAGE: MICRO DOCUMENT ANALYSIS
    # ========================================================================
    elif page == "🔬 Micro Document Analysis":
        st.header("🔬 Micro Document Analysis")

        # Document pages
        pages = query_table(client, 'document_pages')

        if not pages.empty:
            col1, col2, col3 = st.columns(3)
            col1.metric("Pages Analyzed", len(pages))
            col2.metric("Avg Fraud Score", f"{pages['fraud_relevance_score'].mean():.1f}")
            col3.metric("Avg Perjury Score", f"{pages['perjury_risk_score'].mean():.1f}")

            # False statements
            st.subheader("🚨 False Statements on Forms")
            false_statements = query_view(client, 'false_statements_on_forms')
            if not false_statements.empty:
                st.dataframe(false_statements, use_container_width=True)

            # Checkbox perjury
            st.subheader("☑️ Checkbox Perjury Summary")
            checkbox_perjury = query_view(client, 'checkbox_perjury_summary')
            if not checkbox_perjury.empty:
                st.dataframe(checkbox_perjury, use_container_width=True)

            # Actions vs Intentions discrepancies
            st.subheader("⚠️ Actions vs. Intentions Discrepancies")
            discrepancies = query_view(client, 'actions_intentions_discrepancies')
            if not discrepancies.empty:
                st.dataframe(discrepancies, use_container_width=True)

            # Documents by fraud score
            st.subheader("Documents by Fraud Score")
            docs_by_fraud = query_view(client, 'documents_by_fraud_score')
            if not docs_by_fraud.empty:
                st.dataframe(docs_by_fraud, use_container_width=True)

    # ========================================================================
    # PAGE: MULTI-JURISDICTION TRACKER
    # ========================================================================
    elif page == "👥 Multi-Jurisdiction Tracker":
        st.header("👥 Multi-Jurisdiction Tracker")

        # Court cases
        cases = query_table(client, 'court_case_tracker')

        if not cases.empty:
            col1, col2, col3 = st.columns(3)
            col1.metric("Active Cases", len(cases))
            col2.metric("Jurisdictions", cases['jurisdiction_text'].nunique())
            col3.metric("Total Parties", 0)  # Calculate from parties_registry

            # Cases by jurisdiction
            st.subheader("Cases by Jurisdiction")
            if 'jurisdiction_text' in cases.columns:
                juris_counts = cases['jurisdiction_text'].value_counts()
                fig = px.bar(x=juris_counts.index, y=juris_counts.values, title="Cases by Jurisdiction")
                st.plotly_chart(fig, use_container_width=True)

            # Complete case map
            st.subheader("Complete Case Map")
            case_map = query_view(client, 'complete_case_map')
            if not case_map.empty:
                st.dataframe(case_map, use_container_width=True)

            # Agency performance
            st.subheader("Agency Performance")
            agency_perf = query_view(client, 'agency_performance')
            if not agency_perf.empty:
                st.dataframe(agency_perf, use_container_width=True)

            # Cross-jurisdiction violations
            st.subheader("Cross-Jurisdiction Violations")
            cross_violations = query_view(client, 'cross_jurisdiction_violations')
            if not cross_violations.empty:
                st.dataframe(cross_violations, use_container_width=True)

    # ========================================================================
    # PAGE: COMMUNICATIONS ANALYSIS
    # ========================================================================
    elif page == "💬 Communications Analysis":
        st.header("💬 Communications Analysis")

        comms = query_table(client, 'communications_matrix')

        if not comms.empty:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Communications", len(comms))
            col2.metric("Participants", comms['sender'].nunique() if 'sender' in comms.columns else 0)
            col3.metric("Smoking Guns", 0)

            # Smoking gun communications
            st.subheader("🔥 Smoking Gun Communications")
            smoking_guns = query_view(client, 'smoking_gun_communications')
            if not smoking_guns.empty:
                st.dataframe(smoking_guns, use_container_width=True)

            # Communications by participant
            st.subheader("Communications by Participant")
            comms_by_participant = query_view(client, 'communications_by_participant')
            if not comms_by_participant.empty:
                st.dataframe(comms_by_participant, use_container_width=True)

            # Timeline gaps
            st.subheader("⚠️ Critical Timeline Gaps")
            gaps = query_view(client, 'critical_timeline_gaps')
            if not gaps.empty:
                st.dataframe(gaps, use_container_width=True)

    # ========================================================================
    # PAGE: CRITICAL ACTIONS REQUIRED
    # ========================================================================
    elif page == "🎯 Critical Actions Required":
        st.header("🎯 Critical Actions Required")

        # Upcoming deadlines
        st.subheader("⏰ Upcoming Deadlines")
        deadlines = query_view(client, 'upcoming_deadlines')
        if not deadlines.empty:
            st.dataframe(deadlines, use_container_width=True)
        else:
            st.success("✅ No upcoming deadlines")

        # Critical events action required
        st.subheader("🚨 Critical Events - Action Required")
        critical_events = query_view(client, 'critical_events_action_required')
        if not critical_events.empty:
            st.dataframe(critical_events, use_container_width=True)

        # Documents needing action
        st.subheader("📄 Documents Needing Action")
        doc_actions = query_table(client, 'document_actions')
        if not doc_actions.empty:
            pending_actions = doc_actions[doc_actions['action_status'] == 'PENDING']
            st.dataframe(pending_actions, use_container_width=True)

        # DVRO violations to report
        st.subheader("🚫 DVRO Violations - Report to Court")
        dvro_violations = query_view(client, 'dvro_violations_timeline')
        if not dvro_violations.empty:
            # Check if reported_to_court column exists
            if 'reported_to_court' in dvro_violations.columns:
                unreported = dvro_violations[dvro_violations['reported_to_court'] == False]
                if not unreported.empty:
                    st.dataframe(unreported, use_container_width=True)
                else:
                    st.success("✅ All DVRO violations have been reported")
            else:
                # Just show all DVRO violations if column doesn't exist
                st.dataframe(dvro_violations, use_container_width=True)
        else:
            st.info("No DVRO violations tracked yet")

if __name__ == '__main__':
    main()
