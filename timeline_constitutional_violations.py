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
@st.cache_resource
def get_supabase():
    # Try Streamlit secrets first, then environment variables, then defaults
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except (KeyError, FileNotFoundError):
        url = os.environ.get('SUPABASE_URL', 'https://jvjlhxodmbkodzmggwpu.supabase.co')
        key = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2amxoeG9kbWJrb2R6bWdnd3B1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyMjMxOTAsImV4cCI6MjA3Nzc5OTE5MH0.ai65vVW816bNAV56XiuRxp5PE5IhBkMGPx3IbxfPh8c')
    return create_client(url, key)

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
# TAB 1: TIMELINE MATRIX - COMPREHENSIVE VIEW
# ============================================================================
with tab1:
    st.header("📊 Timeline Matrix: Events, Documents & Actions")

    # Filters sidebar
    col_filters, col_main = st.columns([1, 3])

    with col_filters:
        st.subheader("🔍 Filters")

        date_range = st.date_input(
            "Date Range",
            value=(datetime(2022, 8, 1), datetime.now()),
            key="timeline_dates"
        )

        event_types = st.multiselect(
            "Event Types",
            ["HEARING", "FILING", "ORDER", "EX_PARTE", "APPEAL", "SERVICE", "GENERAL"],
            default=["HEARING", "EX_PARTE", "ORDER", "FILING"]
        )

        show_docs = st.checkbox("Include Documents", value=True)
        show_violations = st.checkbox("Include Violations", value=True)

        min_relevancy = st.slider("Min Document Relevancy", 0, 1000, 500)

    with col_main:
        try:
            # Query all data sources
            st.info("📥 Loading data from Supabase...")

            # 1. Get court events
            events_response = supabase.table('court_events')\
                .select('*')\
                .gte('event_date', date_range[0].isoformat())\
                .lte('event_date', date_range[1].isoformat())\
                .order('event_date', desc=True)\
                .execute()

            events_df = pd.DataFrame(events_response.data)

            if not events_df.empty and event_types:
                events_df = events_df[events_df['event_type'].isin(event_types)]

            # 2. Get legal documents
            docs_df = pd.DataFrame()
            if show_docs:
                docs_response = supabase.table('legal_documents')\
                    .select('*')\
                    .gte('relevancy_number', min_relevancy)\
                    .order('created_at', desc=True)\
                    .execute()
                docs_df = pd.DataFrame(docs_response.data)

            # 3. Get violations
            violations_df = pd.DataFrame()
            if show_violations:
                try:
                    violations_response = supabase.table('legal_violations')\
                        .select('*')\
                        .order('violation_date', desc=True)\
                        .execute()
                    violations_df = pd.DataFrame(violations_response.data)
                except:
                    pass  # Table might not exist

            # === SUMMARY METRICS ===
            st.markdown("### 📈 Overview Metrics")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("📅 Court Events", len(events_df))
            with col2:
                st.metric("📄 Documents", len(docs_df) if show_docs else 0)
            with col3:
                st.metric("⚖️ Violations", len(violations_df) if show_violations else 0)
            with col4:
                total_items = len(events_df) + len(docs_df) + len(violations_df)
                st.metric("📊 Total Items", total_items)

            st.markdown("---")

            # === TIMELINE MATRIX ===
            st.markdown("### 📋 Comprehensive Timeline Matrix")

            # Build unified timeline
            timeline_data = []

            # Add events
            for _, event in events_df.iterrows():
                timeline_data.append({
                    'Date': pd.to_datetime(event.get('event_date', '')),
                    'Category': '⚖️ Court Event',
                    'Type': event.get('event_type', 'N/A'),
                    'Title': event.get('event_title', 'Untitled Event'),
                    'Description': event.get('event_description', '')[:100] + '...' if event.get('event_description') else '',
                    'Actor': event.get('judge_name', 'N/A'),
                    'Outcome': event.get('event_outcome', ''),
                    'Score': None,
                    'Status': '✅ Completed' if event.get('event_outcome') else '⏳ Pending'
                })

            # Add documents
            if show_docs and not docs_df.empty:
                for _, doc in docs_df.iterrows():
                    timeline_data.append({
                        'Date': pd.to_datetime(doc.get('created_at', '')),
                        'Category': '📄 Document',
                        'Type': doc.get('document_type', 'Document'),
                        'Title': doc.get('original_filename', 'Unknown')[:50],
                        'Description': f"Relevancy: {doc.get('relevancy_number', 0)}, Micro: {doc.get('micro_number', 0)}",
                        'Actor': doc.get('file_extension', ''),
                        'Outcome': '',
                        'Score': doc.get('relevancy_number', 0),
                        'Status': '🔥 Critical' if doc.get('relevancy_number', 0) >= 800 else '✅ Filed'
                    })

            # Add violations
            if show_violations and not violations_df.empty:
                for _, viol in violations_df.iterrows():
                    timeline_data.append({
                        'Date': pd.to_datetime(viol.get('violation_date', '')),
                        'Category': '🚨 Violation',
                        'Type': viol.get('violation_category', 'Violation'),
                        'Title': viol.get('violation_title', 'Unnamed Violation')[:50],
                        'Description': viol.get('violation_description', '')[:100] + '...' if viol.get('violation_description') else '',
                        'Actor': viol.get('perpetrator', 'Unknown'),
                        'Outcome': '',
                        'Score': viol.get('severity_score', 0),
                        'Status': f"Severity: {viol.get('severity_score', 0)}"
                    })

            # Create DataFrame
            if timeline_data:
                timeline_df = pd.DataFrame(timeline_data)
                timeline_df = timeline_df.sort_values('Date', ascending=False)

                # Display matrix
                st.dataframe(
                    timeline_df,
                    use_container_width=True,
                    height=600,
                    column_config={
                        'Date': st.column_config.DatetimeColumn('Date', format='YYYY-MM-DD'),
                        'Category': st.column_config.TextColumn('Category', width='medium'),
                        'Type': st.column_config.TextColumn('Type', width='medium'),
                        'Title': st.column_config.TextColumn('Title', width='large'),
                        'Score': st.column_config.NumberColumn('Score', format='%.0f'),
                        'Status': st.column_config.TextColumn('Status', width='medium')
                    }
                )

                # === VISUALIZATIONS ===
                st.markdown("---")
                st.markdown("### 📊 Timeline Visualizations")

                viz_col1, viz_col2 = st.columns(2)

                with viz_col1:
                    # Timeline by category
                    st.subheader("Activity by Category")
                    category_counts = timeline_df['Category'].value_counts()
                    st.bar_chart(category_counts)

                with viz_col2:
                    # Activity over time
                    st.subheader("Activity Over Time")
                    timeline_df['Month'] = timeline_df['Date'].dt.to_period('M').astype(str)
                    monthly_activity = timeline_df.groupby('Month').size()
                    st.line_chart(monthly_activity)

                # === DETAILED BREAKDOWN ===
                st.markdown("---")
                st.markdown("### 🔍 Detailed Breakdown by Category")

                breakdown_tabs = st.tabs([
                    f"📅 Events ({len(events_df)})",
                    f"📄 Documents ({len(docs_df)})",
                    f"🚨 Violations ({len(violations_df)})"
                ])

                with breakdown_tabs[0]:
                    if not events_df.empty:
                        st.dataframe(
                            events_df[['event_date', 'event_type', 'event_title', 'judge_name', 'event_outcome']],
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("No court events in selected date range")

                with breakdown_tabs[1]:
                    if not docs_df.empty:
                        st.dataframe(
                            docs_df[['created_at', 'original_filename', 'document_type', 'relevancy_number', 'micro_number']].head(50),
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("No documents match filters")

                with breakdown_tabs[2]:
                    if not violations_df.empty:
                        st.dataframe(
                            violations_df[['violation_date', 'violation_category', 'violation_title', 'perpetrator', 'severity_score']],
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("No violations tracked")

            else:
                st.warning("⚠️ No data found for selected filters")

        except Exception as e:
            st.error(f"❌ Error loading timeline data: {e}")
            import traceback
            with st.expander("Show error details"):
                st.code(traceback.format_exc())

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
            st.dataframe(violations_df, use_container_width=True)
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
            .select('original_filename, relevancy_number, micro_number, document_type, created_at, file_extension')\
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
                high_micro = len(docs_df[docs_df['micro_number'] >= 70]) if 'micro_number' in docs_df.columns else 0
                st.metric("High Micro Score (≥70)", high_micro)

            st.subheader("📄 Documents with Relevancy & Analysis Scores")

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
                use_container_width=True
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
