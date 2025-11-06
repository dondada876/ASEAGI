#!/usr/bin/env python3
"""
Bulk Ingestion Progress Dashboard
==================================
Real-time monitoring dashboard for bulk document ingestion
Shows progress, costs, errors, and allows resume
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Bulk Ingestion Monitor",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .success-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .warning-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .info-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATABASE CONNECTION
# ============================================================================

@st.cache_resource
def get_db_connection():
    """Get SQLite connection"""
    db_path = Path(__file__).parent / "bulk_ingestion_progress.db"
    if not db_path.exists():
        st.error(f"❌ Progress database not found: {db_path}")
        st.info("💡 Run `python bulk_document_ingestion.py` to start ingestion first")
        st.stop()
    return sqlite3.connect(db_path, check_same_thread=False)


# ============================================================================
# DATA FETCHING
# ============================================================================

def fetch_all_batches(conn):
    """Fetch all batches"""
    query = """
        SELECT
            b.batch_id,
            b.batch_name,
            b.source_directory,
            b.started_at,
            b.completed_at,
            b.total_files,
            b.status,
            COUNT(CASE WHEN f.status = 'success' THEN 1 END) as processed,
            COUNT(CASE WHEN f.status = 'skipped' THEN 1 END) as skipped,
            COUNT(CASE WHEN f.status = 'error' THEN 1 END) as errors,
            SUM(f.api_cost) as total_cost
        FROM batches b
        LEFT JOIN file_processing f ON b.batch_id = f.batch_id
        GROUP BY b.batch_id
        ORDER BY b.started_at DESC
    """
    return pd.read_sql_query(query, conn)


def fetch_batch_files(conn, batch_id):
    """Fetch files for a specific batch"""
    query = """
        SELECT
            file_path,
            status,
            document_id,
            processed_at,
            error_message,
            api_cost
        FROM file_processing
        WHERE batch_id = ?
        ORDER BY processed_at DESC
    """
    return pd.read_sql_query(query, conn, params=(batch_id,))


def fetch_overall_stats(conn):
    """Fetch overall statistics"""
    query = """
        SELECT
            COUNT(DISTINCT batch_id) as total_batches,
            SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as total_processed,
            SUM(CASE WHEN status = 'skipped' THEN 1 ELSE 0 END) as total_skipped,
            SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as total_errors,
            SUM(api_cost) as total_cost
        FROM file_processing
    """
    return pd.read_sql_query(query, conn).iloc[0]


# ============================================================================
# DASHBOARD
# ============================================================================

def main():
    """Main dashboard"""

    # Header
    st.title("📊 Bulk Document Ingestion Monitor")
    st.markdown("Real-time progress tracking for 10,000+ document ingestion")

    # Connect to database
    conn = get_db_connection()

    # Fetch data
    batches_df = fetch_all_batches(conn)
    overall_stats = fetch_overall_stats(conn)

    # Auto-refresh
    refresh_interval = st.sidebar.slider(
        "Auto-refresh (seconds)",
        min_value=5,
        max_value=60,
        value=10,
        step=5
    )
    st.sidebar.button("🔄 Refresh Now")

    # ========================================================================
    # OVERALL STATISTICS
    # ========================================================================

    st.markdown("## 📈 Overall Statistics")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Total Batches",
            overall_stats['total_batches'],
            delta=None
        )

    with col2:
        st.metric(
            "✅ Processed",
            overall_stats['total_processed'],
            delta=None
        )

    with col3:
        st.metric(
            "⏭️ Skipped",
            overall_stats['total_skipped'],
            delta=None
        )

    with col4:
        st.metric(
            "❌ Errors",
            overall_stats['total_errors'],
            delta=None
        )

    with col5:
        st.metric(
            "💰 Total Cost",
            f"${overall_stats['total_cost']:.2f}",
            delta=None
        )

    # ========================================================================
    # BATCH LIST
    # ========================================================================

    st.markdown("## 📦 Batch History")

    if batches_df.empty:
        st.info("No batches found. Start a new ingestion with `python bulk_document_ingestion.py`")
        return

    # Process batch data
    batches_df['progress'] = (batches_df['processed'] / batches_df['total_files'] * 100).round(1)
    batches_df['started_at'] = pd.to_datetime(batches_df['started_at'])
    batches_df['completed_at'] = pd.to_datetime(batches_df['completed_at'])

    # Display batches
    for idx, batch in batches_df.iterrows():
        with st.expander(
            f"**{batch['batch_name']}** | "
            f"Progress: {batch['progress']:.1f}% | "
            f"Status: {batch['status']} | "
            f"Cost: ${batch['total_cost']:.2f}",
            expanded=(idx == 0)
        ):
            # Batch details
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"**Source:** `{batch['source_directory']}`")
                st.markdown(f"**Started:** {batch['started_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                if pd.notna(batch['completed_at']):
                    duration = (batch['completed_at'] - batch['started_at']).total_seconds()
                    st.markdown(f"**Duration:** {duration:.1f}s")

            with col2:
                st.markdown(f"**Total Files:** {batch['total_files']}")
                st.markdown(f"**✅ Processed:** {batch['processed']}")
                st.markdown(f"**⏭️ Skipped:** {batch['skipped']}")

            with col3:
                st.markdown(f"**❌ Errors:** {batch['errors']}")
                st.markdown(f"**💰 Cost:** ${batch['total_cost']:.2f}")
                if batch['processed'] > 0:
                    avg_cost = batch['total_cost'] / batch['processed']
                    st.markdown(f"**Avg Cost:** ${avg_cost:.4f}/file")

            # Progress bar
            progress = batch['processed'] / batch['total_files']
            st.progress(progress)

            # File list
            if st.checkbox(f"Show files for batch {batch['batch_id']}", key=f"files_{batch['batch_id']}"):
                files_df = fetch_batch_files(conn, batch['batch_id'])

                if not files_df.empty:
                    # Status filter
                    status_filter = st.multiselect(
                        "Filter by status",
                        options=['success', 'skipped', 'error'],
                        default=['success', 'skipped', 'error'],
                        key=f"filter_{batch['batch_id']}"
                    )

                    filtered_files = files_df[files_df['status'].isin(status_filter)]

                    # Display files
                    st.dataframe(
                        filtered_files[['file_path', 'status', 'document_id', 'api_cost', 'error_message']],
                        use_container_width=True,
                        height=400
                    )

                    # Download button
                    csv = filtered_files.to_csv(index=False)
                    st.download_button(
                        "📥 Download CSV",
                        csv,
                        f"batch_{batch['batch_id']}_files.csv",
                        "text/csv"
                    )

    # ========================================================================
    # CHARTS
    # ========================================================================

    st.markdown("## 📊 Analytics")

    col1, col2 = st.columns(2)

    with col1:
        # Status distribution
        status_data = {
            'Status': ['Processed', 'Skipped', 'Errors'],
            'Count': [
                overall_stats['total_processed'],
                overall_stats['total_skipped'],
                overall_stats['total_errors']
            ]
        }
        status_df = pd.DataFrame(status_data)

        fig_status = px.pie(
            status_df,
            values='Count',
            names='Status',
            title='File Status Distribution',
            color='Status',
            color_discrete_map={
                'Processed': '#38ef7d',
                'Skipped': '#4facfe',
                'Errors': '#f5576c'
            }
        )
        st.plotly_chart(fig_status, use_container_width=True)

    with col2:
        # Cost over batches
        fig_cost = px.bar(
            batches_df,
            x='batch_name',
            y='total_cost',
            title='Cost per Batch',
            labels={'batch_name': 'Batch', 'total_cost': 'Cost ($)'},
            color='total_cost',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_cost, use_container_width=True)

    # Progress over time
    if not batches_df.empty:
        fig_progress = go.Figure()

        for idx, batch in batches_df.iterrows():
            fig_progress.add_trace(go.Bar(
                name=batch['batch_name'],
                x=['Processed', 'Skipped', 'Errors'],
                y=[batch['processed'], batch['skipped'], batch['errors']],
                text=[batch['processed'], batch['skipped'], batch['errors']],
                textposition='auto'
            ))

        fig_progress.update_layout(
            title='Files by Status Across Batches',
            barmode='group',
            xaxis_title='Status',
            yaxis_title='Count'
        )

        st.plotly_chart(fig_progress, use_container_width=True)

    # ========================================================================
    # ACTIVE BATCH MONITORING
    # ========================================================================

    active_batches = batches_df[batches_df['status'] == 'in_progress']

    if not active_batches.empty:
        st.markdown("## 🔄 Active Batches")

        for idx, batch in active_batches.iterrows():
            st.markdown(f"### {batch['batch_name']}")

            # Live progress
            progress = batch['processed'] / batch['total_files']
            remaining = batch['total_files'] - batch['processed'] - batch['skipped'] - batch['errors']

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Files Remaining", remaining)

            with col2:
                elapsed = (datetime.now() - batch['started_at']).total_seconds()
                if batch['processed'] > 0:
                    avg_time = elapsed / batch['processed']
                    eta_seconds = avg_time * remaining
                    eta = timedelta(seconds=int(eta_seconds))
                    st.metric("ETA", str(eta))
                else:
                    st.metric("ETA", "Calculating...")

            with col3:
                if batch['processed'] > 0:
                    rate = batch['processed'] / elapsed * 60
                    st.metric("Processing Rate", f"{rate:.1f} files/min")
                else:
                    st.metric("Processing Rate", "Calculating...")

            st.progress(progress, text=f"{progress*100:.1f}% complete")

    # Auto-refresh
    import time
    time.sleep(refresh_interval)
    st.rerun()


if __name__ == "__main__":
    main()
