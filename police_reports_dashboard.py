#!/usr/bin/env python3
"""
Police Reports Dashboard
Comprehensive view of police reports with status tracking, source documents, and processing information
"""

import streamlit as st
import os
import sys
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import base64
from pathlib import Path

try:
    from supabase import create_client
except ImportError:
    st.error("❌ Install supabase: pip3 install supabase")
    st.stop()

try:
    from proj344_style import inject_custom_css, render_header, render_metric_card, render_document_card, render_alert, render_footer
    HAS_STYLE = True
except ImportError:
    HAS_STYLE = False

st.set_page_config(
    page_title="Police Reports Dashboard",
    page_icon="🚔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SUPABASE CONNECTION
# ============================================================================

@st.cache_resource
def init_supabase():
    """Initialize Supabase client"""
    # Try Streamlit secrets first, then environment variables
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")
    except (KeyError, FileNotFoundError):
        url = os.environ.get('SUPABASE_URL', 'https://jvjlhxodmbkodzmggwpu.supabase.co')
        key = os.environ.get('SUPABASE_KEY')

    if not url or not key:
        return None, "Missing SUPABASE_URL or SUPABASE_KEY"

    try:
        client = create_client(url, key)
        return client, None
    except Exception as e:
        return None, str(e)

# ============================================================================
# DATA QUERIES
# ============================================================================

@st.cache_data(ttl=60)
def get_police_reports(_client):
    """Get all police reports from legal_documents table"""
    try:
        # Query 1: Documents with "police" in filename
        response = _client.table('legal_documents')\
            .select('*')\
            .ilike('original_filename', '%police%')\
            .order('created_at', desc=True)\
            .execute()

        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching police reports: {e}")
        return []

@st.cache_data(ttl=60)
def get_all_reports(_client):
    """Get all documents with 'report' in filename"""
    try:
        response = _client.table('legal_documents')\
            .select('*')\
            .ilike('original_filename', '%report%')\
            .order('created_at', desc=True)\
            .execute()

        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching reports: {e}")
        return []

@st.cache_data(ttl=60)
def get_document_pages(_client, document_id):
    """Get all pages for a specific document"""
    try:
        response = _client.table('document_pages')\
            .select('*')\
            .eq('document_id', document_id)\
            .order('page_number')\
            .execute()

        return response.data if response.data else []
    except Exception as e:
        return []

@st.cache_data(ttl=60)
def get_report_statistics(_client):
    """Calculate statistics for police reports"""
    police_reports = get_police_reports(_client)
    all_reports = get_all_reports(_client)

    if not police_reports and not all_reports:
        return None

    stats = {
        'total_police_reports': len(police_reports),
        'total_reports': len(all_reports),
        'avg_relevancy': sum(d.get('relevancy_number', 0) for d in police_reports) / len(police_reports) if police_reports else 0,
        'avg_legal_score': sum(d.get('legal_number', 0) for d in police_reports) / len(police_reports) if police_reports else 0,
        'critical_count': len([d for d in police_reports if d.get('relevancy_number', 0) >= 900]),
        'high_value_count': len([d for d in police_reports if 800 <= d.get('relevancy_number', 0) < 900]),
        'processed_count': len([d for d in police_reports if d.get('processing_status') == 'completed']),
        'pending_count': len([d for d in police_reports if d.get('processing_status') in ['pending', 'processing']]),
        'document_types': Counter(d.get('document_type') for d in police_reports if d.get('document_type')),
        'total_pages': sum(d.get('total_pages', 0) for d in police_reports),
    }

    return stats

@st.cache_data(ttl=60)
def search_reports(_client, search_term, report_type='police'):
    """Search police reports or all reports"""
    if report_type == 'police':
        reports = get_police_reports(_client)
    else:
        reports = get_all_reports(_client)

    if not search_term:
        return reports

    search_lower = search_term.lower()
    results = []

    for doc in reports:
        # Search in multiple fields
        searchable = ' '.join([
            str(doc.get('original_filename', '')),
            str(doc.get('renamed_filename', '')),
            str(doc.get('document_title', '')),
            str(doc.get('executive_summary', '')),
            ' '.join(doc.get('keywords', []) if doc.get('keywords') else []),
            ' '.join(doc.get('smoking_guns', []) if doc.get('smoking_guns') else [])
        ]).lower()

        if search_lower in searchable:
            results.append(doc)

    return results

# ============================================================================
# UI HELPER FUNCTIONS
# ============================================================================

def render_status_badge(status):
    """Render a colored status badge"""
    status_colors = {
        'completed': ('🟢', '#10B981', 'white'),
        'processing': ('🟡', '#F59E0B', 'white'),
        'pending': ('🔵', '#3B82F6', 'white'),
        'failed': ('🔴', '#DC2626', 'white'),
        'error': ('🔴', '#DC2626', 'white'),
    }

    icon, bg_color, text_color = status_colors.get(status, ('⚪', '#64748B', 'white'))

    return f"""
    <span style="
        background-color: {bg_color};
        color: {text_color};
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.875rem;
        display: inline-block;
    ">
        {icon} {status.upper() if status else 'UNKNOWN'}
    </span>
    """

def render_score_badge(score, label="REL"):
    """Render a score badge with appropriate color"""
    if score >= 900:
        bg_color = '#DC2626'
    elif score >= 800:
        bg_color = '#F59E0B'
    elif score >= 700:
        bg_color = '#3B82F6'
    else:
        bg_color = '#64748B'

    return f"""
    <span style="
        background-color: {bg_color};
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.875rem;
        display: inline-block;
    ">
        {label}-{score}
    </span>
    """

def display_document_viewer(doc, client):
    """Display document with source images/PDFs if available"""
    st.markdown("---")
    st.subheader("📄 Document Details")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"**Original Filename:** {doc.get('original_filename', 'N/A')}")
        st.markdown(f"**Document Type:** {doc.get('document_type', 'N/A')}")
        st.markdown(f"**Total Pages:** {doc.get('total_pages', 'N/A')}")
        st.markdown(f"**Created:** {doc.get('created_at', 'N/A')}")

        if doc.get('document_title'):
            st.markdown(f"**Title:** {doc.get('document_title')}")

        if doc.get('executive_summary'):
            st.markdown("**Executive Summary:**")
            st.info(doc.get('executive_summary'))

    with col2:
        # Status
        status = doc.get('processing_status', 'unknown')
        st.markdown("**Processing Status:**")
        st.markdown(render_status_badge(status), unsafe_allow_html=True)

        # Scores
        st.markdown("**Scores:**")
        if doc.get('relevancy_number') is not None:
            st.markdown(render_score_badge(doc.get('relevancy_number'), 'REL'), unsafe_allow_html=True)
        if doc.get('legal_number') is not None:
            st.markdown(render_score_badge(doc.get('legal_number'), 'LEG'), unsafe_allow_html=True)
        if doc.get('micro_number') is not None:
            st.markdown(render_score_badge(doc.get('micro_number'), 'MIC'), unsafe_allow_html=True)
        if doc.get('macro_number') is not None:
            st.markdown(render_score_badge(doc.get('macro_number'), 'MAC'), unsafe_allow_html=True)

    # Keywords and Smoking Guns
    col1, col2 = st.columns(2)

    with col1:
        if doc.get('keywords'):
            st.markdown("**Keywords:**")
            keywords_html = ' '.join([
                f'<span style="background: #EFF6FF; color: #1E40AF; padding: 0.25rem 0.5rem; border-radius: 0.25rem; margin: 0.25rem; display: inline-block;">{kw}</span>'
                for kw in doc.get('keywords', [])
            ])
            st.markdown(keywords_html, unsafe_allow_html=True)

    with col2:
        if doc.get('smoking_guns'):
            st.markdown("**🔥 Smoking Guns:**")
            for sg in doc.get('smoking_guns', []):
                st.markdown(f"- {sg}")

    # Document pages viewer
    st.markdown("---")
    st.subheader("📑 Document Pages")

    pages = get_document_pages(client, doc.get('id'))

    if pages:
        st.info(f"Found {len(pages)} page(s) in database")

        # Page selector
        page_numbers = [p.get('page_number', i+1) for i, p in enumerate(pages)]
        selected_page_num = st.selectbox("Select Page", page_numbers, key=f"page_select_{doc.get('id')}")

        # Find selected page
        selected_page = next((p for p in pages if p.get('page_number') == selected_page_num), None)

        if selected_page:
            col1, col2 = st.columns([2, 1])

            with col1:
                # Display page image if available
                if selected_page.get('image_url'):
                    st.markdown(f"**Page {selected_page_num} - Image**")
                    try:
                        # Try to load image from Supabase storage
                        st.image(selected_page['image_url'], use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not load image: {e}")
                        st.markdown(f"[View Image]({selected_page['image_url']})")

                elif selected_page.get('image_path'):
                    st.markdown(f"**Page {selected_page_num} - Local Path**")
                    st.code(selected_page['image_path'])

                    # Try to load from local path
                    if os.path.exists(selected_page['image_path']):
                        try:
                            st.image(selected_page['image_path'], use_container_width=True)
                        except Exception as e:
                            st.warning(f"Could not load local image: {e}")
                    else:
                        st.warning("Image file not found at local path")

            with col2:
                st.markdown("**Page Metadata:**")
                st.json({
                    'page_number': selected_page.get('page_number'),
                    'file_type': selected_page.get('file_type'),
                    'created_at': selected_page.get('created_at'),
                })

                # OCR text if available
                if selected_page.get('ocr_text'):
                    with st.expander("📝 View OCR Text"):
                        st.text_area(
                            "Extracted Text",
                            selected_page.get('ocr_text'),
                            height=300,
                            key=f"ocr_{doc.get('id')}_{selected_page_num}"
                        )
    else:
        st.warning("No pages found in database for this document")

        # Show file path if available
        if doc.get('file_path'):
            st.info(f"**File Path:** {doc.get('file_path')}")

        if doc.get('storage_url'):
            st.markdown(f"[📥 Download from Storage]({doc.get('storage_url')})")

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

def main():
    # Apply custom styling if available
    if HAS_STYLE:
        inject_custom_css()

    # Initialize Supabase
    client, error = init_supabase()

    if error or not client:
        st.error(f"❌ Supabase connection failed: {error}")
        st.info("💡 **Fix:** Create `.streamlit/secrets.toml` with your Supabase credentials")
        st.code("""
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
        """)
        st.stop()

    # Header
    if HAS_STYLE:
        render_header("🚔 Police Reports Dashboard", "Comprehensive view of police reports with status tracking and source documents", "🚔")
    else:
        st.title("🚔 Police Reports Dashboard")
        st.markdown("**Comprehensive view of police reports with status tracking and source documents**")

    st.markdown(f"**Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Sidebar navigation
    st.sidebar.title("📊 Navigation")
    page = st.sidebar.radio("Select View", [
        "🏠 Overview",
        "📄 All Police Reports",
        "📋 All Reports",
        "🔍 Search Reports",
        "📊 Analytics",
    ])

    # Load statistics
    stats = get_report_statistics(client)

    # ========================================================================
    # PAGE: OVERVIEW
    # ========================================================================
    if page == "🏠 Overview":
        st.header("📊 System Overview")

        if not stats:
            st.warning("No police reports found in the database.")
            st.info("Run the count_police_reports.py script or upload police reports to the system.")
            return

        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🚔 Police Reports", stats['total_police_reports'])
        col2.metric("📋 Total Reports", stats['total_reports'])
        col3.metric("📄 Total Pages", stats['total_pages'])
        col4.metric("⚖️ Critical Reports", stats['critical_count'], help="Relevancy ≥ 900")

        col5, col6, col7, col8 = st.columns(4)
        col5.metric("🟢 Processed", stats['processed_count'])
        col6.metric("🟡 Pending", stats['pending_count'])
        col7.metric("📊 Avg Relevancy", f"{stats['avg_relevancy']:.0f}")
        col8.metric("⚖️ Avg Legal Score", f"{stats['avg_legal_score']:.0f}")

        st.markdown("---")

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Score Distribution")

            score_data = {
                'Tier': ['Critical (900+)', 'High Value (800-899)', 'Others'],
                'Count': [
                    stats['critical_count'],
                    stats['high_value_count'],
                    stats['total_police_reports'] - stats['critical_count'] - stats['high_value_count']
                ],
                'Color': ['#DC2626', '#F59E0B', '#64748B']
            }

            fig = px.pie(
                score_data,
                values='Count',
                names='Tier',
                color='Tier',
                color_discrete_map={
                    'Critical (900+)': '#DC2626',
                    'High Value (800-899)': '#F59E0B',
                    'Others': '#64748B'
                },
                title="Reports by Relevancy Score"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("📋 Document Types")

            if stats['document_types']:
                type_df = pd.DataFrame([
                    {'Type': k, 'Count': v}
                    for k, v in stats['document_types'].items()
                ]).sort_values('Count', ascending=False)

                fig = px.bar(
                    type_df,
                    x='Type',
                    y='Count',
                    title="Reports by Document Type",
                    color='Count',
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig, use_container_width=True)

        # Recent reports
        st.markdown("---")
        st.subheader("🔥 Recent Police Reports")

        police_reports = get_police_reports(client)
        if police_reports:
            recent_reports = police_reports[:5]

            for report in recent_reports:
                with st.expander(f"📄 {report.get('original_filename', 'Untitled')} - {render_status_badge(report.get('processing_status', 'unknown'))}", expanded=False):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"**Type:** {report.get('document_type', 'N/A')}")
                        st.markdown(f"**Created:** {report.get('created_at', 'N/A')}")
                        if report.get('executive_summary'):
                            st.markdown(f"**Summary:** {report.get('executive_summary')[:200]}...")

                    with col2:
                        if report.get('relevancy_number') is not None:
                            st.markdown(render_score_badge(report.get('relevancy_number'), 'REL'), unsafe_allow_html=True)
                        if report.get('legal_number') is not None:
                            st.markdown(render_score_badge(report.get('legal_number'), 'LEG'), unsafe_allow_html=True)

    # ========================================================================
    # PAGE: ALL POLICE REPORTS
    # ========================================================================
    elif page == "📄 All Police Reports":
        st.header("📄 All Police Reports")

        police_reports = get_police_reports(client)

        if not police_reports:
            st.warning("No police reports found.")
            return

        st.info(f"Found {len(police_reports)} police report(s)")

        # Filters
        col1, col2, col3 = st.columns(3)

        with col1:
            status_filter = st.multiselect(
                "Filter by Status",
                options=['completed', 'processing', 'pending', 'failed'],
                default=None
            )

        with col2:
            doc_types = list(set([r.get('document_type') for r in police_reports if r.get('document_type')]))
            type_filter = st.multiselect(
                "Filter by Type",
                options=doc_types,
                default=None
            )

        with col3:
            min_relevancy = st.slider(
                "Min Relevancy Score",
                min_value=0,
                max_value=999,
                value=0,
                step=50
            )

        # Apply filters
        filtered_reports = police_reports

        if status_filter:
            filtered_reports = [r for r in filtered_reports if r.get('processing_status') in status_filter]

        if type_filter:
            filtered_reports = [r for r in filtered_reports if r.get('document_type') in type_filter]

        filtered_reports = [r for r in filtered_reports if r.get('relevancy_number', 0) >= min_relevancy]

        st.markdown(f"**Showing {len(filtered_reports)} report(s)**")

        # Display reports
        for i, report in enumerate(filtered_reports):
            with st.expander(f"📄 {report.get('original_filename', 'Untitled')}", expanded=False):
                display_document_viewer(report, client)

    # ========================================================================
    # PAGE: ALL REPORTS
    # ========================================================================
    elif page == "📋 All Reports":
        st.header("📋 All Reports")

        all_reports = get_all_reports(client)

        if not all_reports:
            st.warning("No reports found.")
            return

        st.info(f"Found {len(all_reports)} report(s) with 'report' in filename")

        # Simple table view
        df = pd.DataFrame([
            {
                'Filename': r.get('original_filename'),
                'Type': r.get('document_type'),
                'Relevancy': r.get('relevancy_number'),
                'Status': r.get('processing_status'),
                'Created': r.get('created_at'),
            }
            for r in all_reports
        ])

        st.dataframe(df, use_container_width=True, height=600)

        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"all_reports_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    # ========================================================================
    # PAGE: SEARCH REPORTS
    # ========================================================================
    elif page == "🔍 Search Reports":
        st.header("🔍 Search Reports")

        search_term = st.text_input("Search for reports", placeholder="Enter keywords...")

        col1, col2 = st.columns([1, 3])

        with col1:
            search_type = st.radio("Search in", ["Police Reports Only", "All Reports"])

        if search_term:
            report_type = 'police' if search_type == "Police Reports Only" else 'all'
            results = search_reports(client, search_term, report_type)

            st.success(f"Found {len(results)} result(s)")

            for result in results:
                with st.expander(f"📄 {result.get('original_filename', 'Untitled')}", expanded=False):
                    display_document_viewer(result, client)
        else:
            st.info("Enter a search term to find reports")

    # ========================================================================
    # PAGE: ANALYTICS
    # ========================================================================
    elif page == "📊 Analytics":
        st.header("📊 Analytics")

        if not stats:
            st.warning("No data available for analytics")
            return

        police_reports = get_police_reports(client)

        if not police_reports:
            return

        # Score analysis
        st.subheader("📊 Score Analysis")

        df = pd.DataFrame([
            {
                'Filename': r.get('original_filename'),
                'Relevancy': r.get('relevancy_number', 0),
                'Legal': r.get('legal_number', 0),
                'Micro': r.get('micro_number', 0),
                'Macro': r.get('macro_number', 0),
                'Created': r.get('created_at'),
            }
            for r in police_reports
        ])

        # Score correlation
        col1, col2 = st.columns(2)

        with col1:
            fig = px.scatter(
                df,
                x='Legal',
                y='Relevancy',
                hover_data=['Filename'],
                title="Legal Score vs Relevancy Score",
                color='Relevancy',
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.scatter(
                df,
                x='Micro',
                y='Macro',
                hover_data=['Filename'],
                title="Micro Score vs Macro Score",
                color='Relevancy',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)

        # Timeline
        st.subheader("📅 Upload Timeline")

        df['Created_Date'] = pd.to_datetime(df['Created']).dt.date
        timeline_df = df.groupby('Created_Date').size().reset_index(name='Count')

        fig = px.line(
            timeline_df,
            x='Created_Date',
            y='Count',
            title="Reports Uploaded Over Time",
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)

    # Footer
    if HAS_STYLE:
        render_footer()
    else:
        st.markdown("---")
        st.markdown("**Police Reports Dashboard** | Powered by PROJ344 System")

if __name__ == "__main__":
    main()
