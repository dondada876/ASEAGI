#!/usr/bin/env python3
"""
ASEAGI Queue Monitor Dashboard
Real-time monitoring of document processing queue and journal
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

try:
    from supabase import create_client
except ImportError:
    st.error("Supabase not installed. Run: pip install supabase")
    st.stop()

# Page config
st.set_page_config(
    page_title="ASEAGI Queue Monitor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .big-metric {
        font-size: 3rem !important;
        font-weight: bold;
    }
    .status-pending { color: #FFA500; }
    .status-processing { color: #1E90FF; }
    .status-completed { color: #32CD32; }
    .status-failed { color: #DC143C; }
    .status-duplicate { color: #9370DB; }
</style>
""", unsafe_allow_html=True)

# Initialize Supabase
@st.cache_resource
def init_supabase():
    url = os.environ.get('SUPABASE_URL', st.secrets.get('SUPABASE_URL', ''))
    key = os.environ.get('SUPABASE_KEY', st.secrets.get('SUPABASE_KEY', ''))

    if not url or not key:
        st.error("⚠️ Supabase credentials not configured")
        st.stop()

    return create_client(url, key)

supabase = init_supabase()

# ============================================================================
# HEADER
# ============================================================================

st.title("🛡️ ASEAGI Queue Monitor")
st.markdown("**Real-time document processing queue and journal tracker**")
st.markdown("---")

# Auto-refresh
auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=True)
if auto_refresh:
    import time
    time.sleep(30)
    st.rerun()

# ============================================================================
# FETCH DATA
# ============================================================================

@st.cache_data(ttl=30)
def get_queue_stats():
    """Get queue statistics"""
    result = supabase.table('document_journal')\
        .select('queue_status')\
        .execute()

    stats = {}
    for row in result.data:
        status = row['queue_status']
        stats[status] = stats.get(status, 0) + 1

    return stats

@st.cache_data(ttl=30)
def get_queue_dashboard():
    """Get dashboard view"""
    try:
        result = supabase.table('queue_dashboard')\
            .select('*')\
            .execute()
        return result.data
    except:
        return []

@st.cache_data(ttl=30)
def get_recent_documents(limit=50):
    """Get recent documents from journal"""
    result = supabase.table('document_journal')\
        .select('*')\
        .order('date_logged', desc=True)\
        .limit(limit)\
        .execute()

    return result.data

@st.cache_data(ttl=30)
def get_processing_performance():
    """Get processing performance metrics"""
    try:
        result = supabase.table('processing_performance')\
            .select('*')\
            .execute()
        return result.data
    except:
        return []

@st.cache_data(ttl=30)
def get_duplicate_stats():
    """Get duplicate detection statistics"""
    try:
        result = supabase.table('duplicate_detection_stats')\
            .select('*')\
            .execute()
        return result.data
    except:
        return []

# Fetch all data
queue_stats = get_queue_stats()
dashboard_data = get_queue_dashboard()
recent_docs = get_recent_documents()
performance_data = get_processing_performance()
duplicate_stats = get_duplicate_stats()

# ============================================================================
# METRICS ROW
# ============================================================================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total = sum(queue_stats.values())
    st.metric("📊 Total Documents", f"{total:,}")

with col2:
    pending = queue_stats.get('pending', 0) + queue_stats.get('assessing', 0)
    st.metric("⏳ Pending", f"{pending:,}")

with col3:
    queued = queue_stats.get('queued', 0)
    st.metric("📋 Queued", f"{queued:,}")

with col4:
    processing = queue_stats.get('processing', 0)
    st.metric("⚙️ Processing", f"{processing:,}")

with col5:
    completed = queue_stats.get('completed', 0)
    st.metric("✅ Completed", f"{completed:,}")

st.markdown("---")

# ============================================================================
# STATUS BREAKDOWN
# ============================================================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Queue Status Distribution")

    if queue_stats:
        # Create pie chart
        status_df = pd.DataFrame([
            {"status": k, "count": v}
            for k, v in queue_stats.items()
        ])

        fig = px.pie(
            status_df,
            values='count',
            names='status',
            title='Documents by Status',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No documents in queue")

with col2:
    st.subheader("🎯 Document Type Distribution")

    if recent_docs:
        # Count by document type
        type_counts = {}
        for doc in recent_docs:
            doc_type = doc.get('document_type', 'unknown')
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1

        type_df = pd.DataFrame([
            {"type": k, "count": v}
            for k, v in type_counts.items()
        ])

        fig = px.bar(
            type_df,
            x='type',
            y='count',
            title='Documents by Type',
            color='count',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No documents processed")

st.markdown("---")

# ============================================================================
# DUPLICATE DETECTION STATS
# ============================================================================

if duplicate_stats:
    st.subheader("🔍 Duplicate Detection Performance")

    col1, col2, col3 = st.columns(3)

    for tier_data in duplicate_stats:
        tier = tier_data.get('duplicate_detection_tier', 0)
        count = tier_data.get('count', 0)
        avg_similarity = tier_data.get('avg_similarity', 0)

        if tier == 0:
            col_to_use = col1
            tier_name = "Tier 0: Filename"
            emoji = "📝"
        elif tier == 1:
            col_to_use = col2
            tier_name = "Tier 1: OCR"
            emoji = "🔤"
        else:
            col_to_use = col3
            tier_name = "Tier 2: Semantic"
            emoji = "🧠"

        with col_to_use:
            st.metric(f"{emoji} {tier_name}", f"{count:,} duplicates")
            if avg_similarity:
                st.caption(f"Avg similarity: {avg_similarity:.1%}")

    st.markdown("---")

# ============================================================================
# PROCESSING PERFORMANCE
# ============================================================================

if performance_data:
    st.subheader("⚡ Processing Performance by Document Type")

    perf_df = pd.DataFrame(performance_data)

    col1, col2 = st.columns(2)

    with col1:
        if 'avg_confidence' in perf_df.columns:
            fig = px.bar(
                perf_df,
                x='document_type',
                y='avg_confidence',
                title='Average AI Confidence Score',
                color='avg_confidence',
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if 'avg_cost' in perf_df.columns:
            fig = px.bar(
                perf_df,
                x='document_type',
                y='avg_cost',
                title='Average Processing Cost ($)',
                color='avg_cost',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

# ============================================================================
# RECENT DOCUMENTS TABLE
# ============================================================================

st.subheader("📄 Recent Documents")

# Filter options
col1, col2, col3 = st.columns(3)

with col1:
    status_filter = st.selectbox(
        "Filter by Status",
        ["All"] + list(queue_stats.keys())
    )

with col2:
    type_filter = st.selectbox(
        "Filter by Type",
        ["All", "business_card", "legal_document", "court_filing", "photo", "sign", "form", "receipt", "unknown"]
    )

with col3:
    show_duplicates = st.checkbox("Show duplicates only", value=False)

# Apply filters
filtered_docs = recent_docs

if status_filter != "All":
    filtered_docs = [d for d in filtered_docs if d.get('queue_status') == status_filter]

if type_filter != "All":
    filtered_docs = [d for d in filtered_docs if d.get('document_type') == type_filter]

if show_duplicates:
    filtered_docs = [d for d in filtered_docs if d.get('is_duplicate', False)]

# Display table
if filtered_docs:
    df = pd.DataFrame(filtered_docs)

    # Select columns to display
    display_columns = [
        'journal_id',
        'original_filename',
        'document_type',
        'queue_status',
        'queue_priority',
        'is_duplicate',
        'ai_confidence_score',
        'date_logged',
        'source_type'
    ]

    # Only show columns that exist
    display_columns = [col for col in display_columns if col in df.columns]

    st.dataframe(
        df[display_columns],
        use_container_width=True,
        height=400
    )

    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"queue_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
else:
    st.info("No documents match the selected filters")

st.markdown("---")

# ============================================================================
# QUEUE TIMELINE
# ============================================================================

st.subheader("📈 Queue Activity Timeline")

if recent_docs:
    # Group by hour
    timeline_data = []
    for doc in recent_docs:
        if doc.get('date_logged'):
            try:
                dt = pd.to_datetime(doc['date_logged'])
                hour = dt.floor('H')
                timeline_data.append({
                    'hour': hour,
                    'status': doc.get('queue_status', 'unknown')
                })
            except:
                pass

    if timeline_data:
        timeline_df = pd.DataFrame(timeline_data)
        timeline_summary = timeline_df.groupby(['hour', 'status']).size().reset_index(name='count')

        fig = px.line(
            timeline_summary,
            x='hour',
            y='count',
            color='status',
            title='Document Submissions Over Time',
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data for timeline")
else:
    st.info("No documents to display")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("For Ashe. For Justice. For All Children. 🛡️")

# Sidebar info
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This dashboard monitors the ASEAGI document processing queue in real-time.

    **Features:**
    - Queue status tracking
    - Document type distribution
    - Duplicate detection stats
    - Processing performance
    - Recent document activity

    **Status Meanings:**
    - 🟡 **Pending**: Just logged, awaiting assessment
    - 🔵 **Assessing**: Running duplicate detection
    - 🟢 **Queued**: Ready for processing
    - ⚙️ **Processing**: Currently being processed
    - ✅ **Completed**: Successfully processed
    - ❌ **Failed**: Processing error
    - 🟣 **Skipped (Duplicate)**: Duplicate detected

    **Refresh:** Dashboard auto-refreshes every 30 seconds when enabled.
    """)

    st.markdown("---")

    st.header("🔧 Quick Actions")

    if st.button("🔄 Refresh Now"):
        st.cache_data.clear()
        st.rerun()

    if st.button("🗑️ Clear Cache"):
        st.cache_data.clear()
        st.success("Cache cleared!")
