#!/usr/bin/env python3
"""
Telegram Uploads Dashboard
View and manage document uploads from Telegram bot
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from supabase import create_client
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Telegram Uploads Dashboard",
    page_icon="📱",
    layout="wide"
)

# ===== SUPABASE CONNECTION =====

@st.cache_resource
def init_supabase():
    """Initialize Supabase client"""
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')

    # Fallback to secrets.toml
    if not url or not key:
        try:
            url = st.secrets.get('SUPABASE_URL')
            key = st.secrets.get('SUPABASE_KEY')
        except:
            pass

    if not url or not key:
        return None, "Missing SUPABASE_URL or SUPABASE_KEY"

    try:
        client = create_client(url, key)
        # Test connection
        client.table('telegram_uploads').select('id', count='exact').limit(1).execute()
        return client, None
    except Exception as e:
        return None, str(e)

# ===== HELPER FUNCTIONS =====

def get_status_icon(status):
    """Get emoji for status"""
    icons = {
        'received': '📥',
        'validating': '🔍',
        'processing': '⏳',
        'storing': '💾',
        'completed': '✅',
        'failed': '❌',
        'partial': '⚠️'
    }
    return icons.get(status, '❓')

def get_status_color(status):
    """Get color for status"""
    colors = {
        'received': '#3498db',
        'validating': '#f39c12',
        'processing': '#9b59b6',
        'storing': '#1abc9c',
        'completed': '#27ae60',
        'failed': '#e74c3c',
        'partial': '#f39c12'
    }
    return colors.get(status, '#95a5a6')

def format_file_size(bytes):
    """Format file size"""
    if bytes is None:
        return 'N/A'
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f'{bytes:.1f} {unit}'
        bytes /= 1024
    return f'{bytes:.1f} TB'

def format_duration(seconds):
    """Format duration"""
    if seconds is None:
        return 'N/A'
    if seconds < 60:
        return f'{seconds}s'
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f'{minutes}m {remaining_seconds}s'

# ===== DATA QUERIES =====

@st.cache_data(ttl=30)
def get_uploads(_client, status_filter=None, date_range=None, file_type=None, limit=100):
    """Get telegram uploads"""
    try:
        query = _client.table('telegram_uploads')\
            .select('*')\
            .eq('is_deleted', False)\
            .order('uploaded_at', desc=True)\
            .limit(limit)

        if status_filter and status_filter != 'All':
            query = query.eq('status', status_filter.lower())

        if file_type and file_type != 'All':
            query = query.eq('file_type', file_type.lower())

        if date_range:
            start_date, end_date = date_range
            query = query.gte('uploaded_at', start_date.isoformat())\
                        .lte('uploaded_at', end_date.isoformat())

        response = query.execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching uploads: {e}")
        return []

@st.cache_data(ttl=60)
def get_statistics(_client):
    """Get upload statistics"""
    try:
        # Total uploads
        total_response = _client.table('telegram_uploads')\
            .select('id', count='exact')\
            .eq('is_deleted', False)\
            .execute()
        total = total_response.count if hasattr(total_response, 'count') else len(total_response.data)

        # By status
        status_counts = {}
        for status in ['received', 'processing', 'completed', 'failed', 'partial']:
            response = _client.table('telegram_uploads')\
                .select('id', count='exact')\
                .eq('status', status)\
                .eq('is_deleted', False)\
                .execute()
            count = response.count if hasattr(response, 'count') else len(response.data)
            status_counts[status] = count

        # Today's uploads
        today = datetime.now().date()
        today_response = _client.table('telegram_uploads')\
            .select('id', count='exact')\
            .gte('uploaded_at', today.isoformat())\
            .eq('is_deleted', False)\
            .execute()
        today_count = today_response.count if hasattr(today_response, 'count') else len(today_response.data)

        return {
            'total': total,
            'status_counts': status_counts,
            'today': today_count,
            'success_rate': (status_counts['completed'] / total * 100) if total > 0 else 0
        }
    except Exception as e:
        st.error(f"Error fetching statistics: {e}")
        return None

@st.cache_data(ttl=30)
def get_processing_logs(_client, upload_id):
    """Get processing logs for an upload"""
    try:
        response = _client.table('processing_logs')\
            .select('*')\
            .eq('telegram_upload_id', upload_id)\
            .order('logged_at', desc=False)\
            .execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching logs: {e}")
        return []

@st.cache_data(ttl=60)
def get_storage_usage(_client):
    """Get storage usage statistics"""
    try:
        response = _client.table('storage_registry')\
            .select('primary_storage_provider, file_size')\
            .eq('is_deleted', False)\
            .execute()

        df = pd.DataFrame(response.data)
        if not df.empty:
            usage = df.groupby('primary_storage_provider')['file_size'].sum().to_dict()
            return usage
        return {}
    except Exception as e:
        return {}

# ===== MAIN APP =====

def main():
    # Header
    st.title("📱 Telegram Uploads Dashboard")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize Supabase
    client, error = init_supabase()

    if error:
        st.error(f"❌ **Supabase Connection Failed**")
        st.code(error)
        st.info("💡 **Fix:** Check your SUPABASE_URL and SUPABASE_KEY credentials")
        st.stop()

    st.success("✅ Connected to Supabase")
    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview",
        "📋 Upload History",
        "📝 Processing Logs",
        "💾 Storage Management",
        "⚡ Quick Actions"
    ])

    # ===== TAB 1: OVERVIEW =====
    with tab1:
        st.header("📊 System Overview")

        stats = get_statistics(client)

        if stats:
            # Top metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Uploads", f"{stats['total']:,}")

            with col2:
                st.metric("Today's Uploads", stats['today'])

            with col3:
                st.metric("Success Rate", f"{stats['success_rate']:.1f}%")

            with col4:
                in_progress = stats['status_counts']['received'] + stats['status_counts']['processing']
                st.metric("In Progress", in_progress)

            st.markdown("---")

            # Status breakdown
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📈 Upload Status")
                status_data = pd.DataFrame([
                    {'Status': f"{get_status_icon(k)} {k.title()}", 'Count': v}
                    for k, v in stats['status_counts'].items()
                ])

                fig = px.bar(
                    status_data,
                    x='Status',
                    y='Count',
                    color='Status',
                    text='Count',
                    color_discrete_map={
                        f"{get_status_icon(k)} {k.title()}": get_status_color(k)
                        for k in stats['status_counts'].keys()
                    }
                )
                fig.update_traces(textposition='outside')
                fig.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("💾 Storage Usage")
                storage_usage = get_storage_usage(client)

                if storage_usage:
                    storage_df = pd.DataFrame([
                        {'Provider': k.title(), 'Size (GB)': v / (1024**3)}
                        for k, v in storage_usage.items()
                    ])

                    fig = px.pie(
                        storage_df,
                        values='Size (GB)',
                        names='Provider',
                        hole=0.4
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No storage data available yet")

    # ===== TAB 2: UPLOAD HISTORY =====
    with tab2:
        st.header("📋 Upload History")

        # Filters
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            status_filter = st.selectbox(
                "Status",
                ['All', 'Received', 'Processing', 'Completed', 'Failed', 'Partial']
            )

        with col2:
            file_type_filter = st.selectbox(
                "File Type",
                ['All', 'Photo', 'Document', 'Audio', 'Video', 'Voice']
            )

        with col3:
            days_back = st.number_input("Days Back", min_value=1, max_value=90, value=7)

        with col4:
            limit = st.number_input("Max Results", min_value=10, max_value=500, value=100)

        date_range = (
            datetime.now() - timedelta(days=days_back),
            datetime.now()
        )

        # Get uploads
        uploads = get_uploads(
            client,
            status_filter=status_filter if status_filter != 'All' else None,
            date_range=date_range,
            file_type=file_type_filter if file_type_filter != 'All' else None,
            limit=limit
        )

        if uploads:
            st.success(f"Found {len(uploads)} uploads")

            # Display as table
            for upload in uploads:
                status_icon = get_status_icon(upload['status'])

                with st.expander(
                    f"{status_icon} {upload.get('file_name', 'Unnamed')} - "
                    f"{upload.get('document_type', 'N/A')} - "
                    f"{upload['uploaded_at'][:10]}"
                ):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown("**📄 File Info**")
                        st.write(f"**ID:** `{upload['id'][:8]}...`")
                        st.write(f"**File:** {upload.get('file_name', 'N/A')}")
                        st.write(f"**Type:** {upload.get('file_type', 'N/A')}")
                        st.write(f"**Size:** {format_file_size(upload.get('file_size'))}")

                    with col2:
                        st.markdown("**📝 Document Info**")
                        st.write(f"**Type:** {upload.get('document_type', 'N/A')}")
                        st.write(f"**Date:** {upload.get('document_date', 'N/A')}")
                        st.write(f"**Title:** {upload.get('document_title', 'N/A')}")
                        st.write(f"**Relevancy:** {upload.get('relevancy_score', 'N/A')}")

                    with col3:
                        st.markdown("**⚙️ Processing**")
                        st.write(f"**Status:** {status_icon} {upload['status'].title()}")
                        st.write(f"**Stage:** {upload.get('processing_stage', 'N/A')}")
                        st.write(f"**Duration:** {format_duration(upload.get('processing_duration_seconds'))}")
                        st.write(f"**Retries:** {upload.get('retry_count', 0)}")

                    if upload.get('user_notes'):
                        st.markdown("**💬 Notes:**")
                        st.info(upload['user_notes'])

                    if upload.get('error_message'):
                        st.markdown("**❌ Error:**")
                        st.error(upload['error_message'])

                    # Action buttons
                    action_col1, action_col2, action_col3 = st.columns(3)

                    with action_col1:
                        if st.button("View Logs", key=f"logs_{upload['id']}"):
                            st.session_state[f"show_logs_{upload['id']}"] = True

                    with action_col2:
                        if upload['status'] == 'failed' and st.button("Retry", key=f"retry_{upload['id']}"):
                            st.info("Retry functionality coming soon!")

                    with action_col3:
                        if upload.get('permanent_storage_url') and st.button("Download", key=f"download_{upload['id']}"):
                            st.info(f"Download: {upload['permanent_storage_url']}")
        else:
            st.info("No uploads found matching your filters")

    # ===== TAB 3: PROCESSING LOGS =====
    with tab3:
        st.header("📝 Processing Logs")

        upload_id = st.text_input("Enter Upload ID", placeholder="UUID of the upload")

        if upload_id:
            logs = get_processing_logs(client, upload_id)

            if logs:
                st.success(f"Found {len(logs)} log entries")

                # Timeline visualization
                log_df = pd.DataFrame(logs)
                log_df['logged_at'] = pd.to_datetime(log_df['logged_at'])

                fig = go.Figure()

                for i, log in enumerate(logs):
                    color = {
                        'started': '#3498db',
                        'completed': '#27ae60',
                        'failed': '#e74c3c',
                        'warning': '#f39c12',
                        'info': '#95a5a6'
                    }.get(log['status'], '#95a5a6')

                    fig.add_trace(go.Scatter(
                        x=[log['logged_at']],
                        y=[i],
                        mode='markers+text',
                        name=log['stage'],
                        text=[log['stage']],
                        textposition='middle right',
                        marker=dict(size=15, color=color)
                    ))

                fig.update_layout(
                    title="Processing Timeline",
                    xaxis_title="Time",
                    yaxis_title="Stage",
                    showlegend=False,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

                # Detailed logs
                st.subheader("Detailed Logs")
                for log in logs:
                    status_icon = {
                        'started': '▶️',
                        'completed': '✅',
                        'failed': '❌',
                        'warning': '⚠️',
                        'info': 'ℹ️'
                    }.get(log['status'], '•')

                    with st.expander(f"{status_icon} {log['stage']} - {log['status']} - {log['logged_at']}"):
                        st.write(f"**Message:** {log['message']}")
                        if log.get('duration_ms'):
                            st.write(f"**Duration:** {log['duration_ms']}ms")
                        if log.get('error_details'):
                            st.error(log['error_details'])
                        if log.get('details'):
                            st.json(log['details'])
            else:
                st.info("No logs found for this upload ID")

    # ===== TAB 4: STORAGE MANAGEMENT =====
    with tab4:
        st.header("💾 Storage Management")

        st.info("Storage management features coming soon!")

        # Storage usage overview
        storage_usage = get_storage_usage(client)

        if storage_usage:
            st.subheader("Storage by Provider")
            for provider, size in storage_usage.items():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{provider.title()}**")
                with col2:
                    st.write(f"{size / (1024**3):.2f} GB")

    # ===== TAB 5: QUICK ACTIONS =====
    with tab5:
        st.header("⚡ Quick Actions")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🔄 Retry Failed Uploads")
            if st.button("Retry All Failed"):
                st.info("Retry functionality coming soon!")

        with col2:
            st.subheader("🗑️ Cleanup")
            if st.button("Delete Old Temp Files"):
                st.info("Cleanup functionality coming soon!")

        st.markdown("---")

        st.subheader("📊 Generate Report")
        report_type = st.selectbox("Report Type", ["Daily Summary", "Weekly Report", "Custom Range"])

        if st.button("Generate Report"):
            st.info("Report generation coming soon!")

if __name__ == "__main__":
    main()
