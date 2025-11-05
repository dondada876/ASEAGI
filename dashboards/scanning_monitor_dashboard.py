#!/usr/bin/env python3
"""
PROJ344 Document Scanning Monitor Dashboard
Real-time monitoring of document scanning progress, costs, and results
"""

import streamlit as st
import os
import time
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import re

try:
    from supabase import create_client
except ImportError:
    st.error("❌ Install supabase: pip3 install supabase")
    st.stop()

st.set_page_config(
    page_title="PROJ344 Scanning Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CONFIGURATION
# ============================================================================

LOG_FILE = "/tmp/proj344-scan.log"
REFRESH_INTERVAL = 5  # seconds

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
# LOG PARSING
# ============================================================================

def parse_log_file():
    """Parse the scanning log file"""
    if not Path(LOG_FILE).exists():
        return {
            'status': 'not_started',
            'total_processed': 0,
            'total_skipped': 0,
            'total_errors': 0,
            'total_cost': 0.0,
            'recent_logs': [],
            'documents': [],
            'phase': 'Not Started'
        }

    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()

        stats = {
            'status': 'running',
            'total_processed': 0,
            'total_skipped': 0,
            'total_errors': 0,
            'total_cost': 0.0,
            'recent_logs': lines[-50:] if lines else [],
            'documents': [],
            'phase': 'Unknown'
        }

        # Parse statistics
        for line in lines:
            if 'Processed:' in line:
                match = re.search(r'Processed: (\d+)', line)
                if match:
                    stats['total_processed'] = int(match.group(1))

            if 'Skipped:' in line:
                match = re.search(r'Skipped: (\d+)', line)
                if match:
                    stats['total_skipped'] = int(match.group(1))

            if 'Errors:' in line:
                match = re.search(r'Errors: (\d+)', line)
                if match:
                    stats['total_errors'] = int(match.group(1))

            if 'Total Cost:' in line:
                match = re.search(r'Total Cost: \$([0-9.]+)', line)
                if match:
                    stats['total_cost'] = float(match.group(1))

            if 'PHASE 1:' in line:
                stats['phase'] = 'Phase 1: CH22_Legal'
            elif 'PHASE 2:' in line:
                stats['phase'] = 'Phase 2: All Downloads'

            # Extract document processing info
            if '📄 Processing:' in line:
                match = re.search(r'Processing: (.+)', line)
                if match:
                    stats['documents'].append({
                        'filename': match.group(1),
                        'status': 'processing',
                        'timestamp': datetime.now()
                    })

            if '✅ Relevancy=' in line:
                match = re.search(r'Relevancy=(\d+), Legal=(\d+), Cost=\$([0-9.]+)', line)
                if match and stats['documents']:
                    stats['documents'][-1].update({
                        'status': 'completed',
                        'relevancy': int(match.group(1)),
                        'legal': int(match.group(2)),
                        'cost': float(match.group(3))
                    })

            if '❌' in line:
                if stats['documents']:
                    stats['documents'][-1]['status'] = 'error'

        # Check if completed
        if 'SCANNING COMPLETE' in ''.join(lines):
            stats['status'] = 'completed'

        return stats

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'total_processed': 0,
            'total_skipped': 0,
            'total_errors': 0,
            'total_cost': 0.0,
            'recent_logs': [],
            'documents': [],
            'phase': 'Error'
        }

# ============================================================================
# DATABASE QUERIES
# ============================================================================

@st.cache_data(ttl=10)
def get_recent_documents(_client, limit=20):
    """Get recently processed documents from Supabase"""
    try:
        response = _client.table('legal_documents')\
            .select('*')\
            .order('processed_at', desc=True)\
            .limit(limit)\
            .execute()
        return response.data
    except:
        return []

@st.cache_data(ttl=10)
def get_db_stats(_client):
    """Get database statistics"""
    try:
        # Total count
        result = _client.table('legal_documents').select('id', count='exact').execute()
        total = result.count

        # Count by hour (last 24 hours)
        response = _client.table('legal_documents')\
            .select('processed_at')\
            .execute()

        timestamps = [doc.get('processed_at') for doc in response.data if doc.get('processed_at')]

        # Average scores
        avg_response = _client.table('legal_documents')\
            .select('relevancy_number,legal_number,micro_number,macro_number,api_cost_usd')\
            .execute()

        docs = avg_response.data
        if docs:
            avg_relevancy = sum(d.get('relevancy_number', 0) for d in docs) / len(docs)
            avg_legal = sum(d.get('legal_number', 0) for d in docs) / len(docs)
            avg_micro = sum(d.get('micro_number', 0) for d in docs) / len(docs)
            avg_macro = sum(d.get('macro_number', 0) for d in docs) / len(docs)
            total_cost = sum(d.get('api_cost_usd', 0) for d in docs)
        else:
            avg_relevancy = avg_legal = avg_micro = avg_macro = total_cost = 0

        return {
            'total': total,
            'timestamps': timestamps,
            'avg_relevancy': avg_relevancy,
            'avg_legal': avg_legal,
            'avg_micro': avg_micro,
            'avg_macro': avg_macro,
            'total_cost': total_cost
        }
    except Exception as e:
        return {
            'total': 0,
            'timestamps': [],
            'avg_relevancy': 0,
            'avg_legal': 0,
            'avg_micro': 0,
            'avg_macro': 0,
            'total_cost': 0,
            'error': str(e)
        }

# ============================================================================
# VISUALIZATIONS
# ============================================================================

def render_progress_bar(current, total, label):
    """Render a progress bar"""
    percentage = (current / total * 100) if total > 0 else 0
    st.metric(label, f"{current} / {total}", f"{percentage:.1f}%")
    st.progress(min(percentage / 100, 1.0))

def render_cost_gauge(cost, max_cost=50):
    """Render cost gauge"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = cost,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Total API Cost ($)", 'font': {'size': 20}},
        delta = {'reference': 0, 'increasing': {'color': "red"}},
        gauge = {
            'axis': {'range': [None, max_cost], 'tickwidth': 1},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 10], 'color': 'lightgreen'},
                {'range': [10, 25], 'color': 'lightyellow'},
                {'range': [25, max_cost], 'color': 'lightcoral'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 40
            }
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    return fig

def render_processing_rate(timestamps):
    """Render processing rate over time"""
    if not timestamps:
        return None

    # Group by minute
    from collections import Counter
    minutes = [t[:16] for t in timestamps if t]  # YYYY-MM-DD HH:MM
    counts = Counter(minutes)

    if not counts:
        return None

    df = pd.DataFrame(list(counts.items()), columns=['Time', 'Count'])
    df = df.sort_values('Time')

    fig = px.line(df, x='Time', y='Count',
                  title='Documents Processed Per Minute',
                  labels={'Count': 'Documents', 'Time': 'Time'})
    fig.update_layout(height=300)
    return fig

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

def main():
    # Header
    st.title("📊 PROJ344 Document Scanning Monitor")
    st.markdown(f"**Real-time monitoring** | Last updated: {datetime.now().strftime('%H:%M:%S')}")

    # Auto-refresh
    if st.sidebar.checkbox("Auto-refresh", value=True):
        st.markdown(f"*Refreshing every {REFRESH_INTERVAL} seconds...*")
        time.sleep(REFRESH_INTERVAL)
        st.rerun()

    # Initialize
    client, error = init_supabase()
    if error:
        st.sidebar.error(f"⚠️ Supabase: {error}")
    else:
        st.sidebar.success("✅ Supabase Connected")

    # Parse log
    log_stats = parse_log_file()

    # Get DB stats
    if client:
        db_stats = get_db_stats(client)
    else:
        db_stats = {'total': 0}

    # ========================================================================
    # STATUS BANNER
    # ========================================================================

    status = log_stats['status']
    if status == 'not_started':
        st.warning("⏳ Scanning not started yet")
    elif status == 'running':
        st.success(f"🚀 SCANNING IN PROGRESS - {log_stats['phase']}")
    elif status == 'completed':
        st.success("✅ SCANNING COMPLETED!")
    else:
        st.error(f"❌ Error: {log_stats.get('error', 'Unknown')}")

    st.markdown("---")

    # ========================================================================
    # KEY METRICS
    # ========================================================================

    st.header("📊 Real-Time Statistics")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("✅ Processed", log_stats['total_processed'])

    with col2:
        st.metric("⏭️ Skipped", log_stats['total_skipped'])

    with col3:
        st.metric("❌ Errors", log_stats['total_errors'])

    with col4:
        st.metric("💰 Log Cost", f"${log_stats['total_cost']:.2f}")

    with col5:
        st.metric("🗄️ In Database", db_stats['total'])

    st.markdown("---")

    # ========================================================================
    # PROGRESS & COST
    # ========================================================================

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📈 Progress")

        # Overall progress (estimated)
        ESTIMATED_TOTAL = 902
        current = log_stats['total_processed'] + log_stats['total_skipped']
        render_progress_bar(current, ESTIMATED_TOTAL, "Overall Progress")

        st.markdown("**Phase Progress:**")
        st.info(f"Current Phase: {log_stats['phase']}")

        # Success rate
        total_attempted = log_stats['total_processed'] + log_stats['total_errors']
        if total_attempted > 0:
            success_rate = (log_stats['total_processed'] / total_attempted * 100)
            st.metric("Success Rate", f"{success_rate:.1f}%")

    with col2:
        st.subheader("💰 Cost Tracking")
        st.plotly_chart(render_cost_gauge(log_stats['total_cost']), use_container_width=True)

        # Estimated completion cost
        if current > 0:
            cost_per_doc = log_stats['total_cost'] / current
            estimated_total_cost = cost_per_doc * ESTIMATED_TOTAL
            st.metric("Estimated Total", f"${estimated_total_cost:.2f}")

    st.markdown("---")

    # ========================================================================
    # RECENT DOCUMENTS
    # ========================================================================

    st.header("📄 Recently Processed Documents")

    if client:
        recent_docs = get_recent_documents(client, limit=10)

        if recent_docs:
            for doc in recent_docs:
                rel = doc.get('relevancy_number', 0)

                # Color code
                if rel >= 900:
                    badge = "🔥 SMOKING GUN"
                    color = "red"
                elif rel >= 800:
                    badge = "⚠️ CRITICAL"
                    color = "orange"
                elif rel >= 700:
                    badge = "📌 IMPORTANT"
                    color = "yellow"
                else:
                    badge = "📄 REFERENCE"
                    color = "gray"

                with st.expander(f"{badge} {doc.get('document_title', 'Untitled')} - Score: {rel}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write("**File:**", doc.get('original_filename', 'N/A'))
                        st.write("**Type:**", doc.get('document_type', 'N/A'))
                    with col2:
                        st.write("**Relevancy:**", f"{doc.get('relevancy_number', 0)}/999")
                        st.write("**Legal:**", f"{doc.get('legal_number', 0)}/999")
                    with col3:
                        st.write("**Micro:**", f"{doc.get('micro_number', 0)}/999")
                        st.write("**Macro:**", f"{doc.get('macro_number', 0)}/999")

                    if doc.get('executive_summary'):
                        st.write("**Summary:**", doc['executive_summary'])

                    if doc.get('smoking_guns'):
                        st.markdown("**🔥 Smoking Guns:**")
                        for sg in doc['smoking_guns']:
                            st.markdown(f"- {sg}")
        else:
            st.info("No documents in database yet. Scanning in progress...")

    st.markdown("---")

    # ========================================================================
    # PROCESSING RATE
    # ========================================================================

    if client and db_stats['timestamps']:
        st.header("📈 Processing Rate")
        rate_chart = render_processing_rate(db_stats['timestamps'])
        if rate_chart:
            st.plotly_chart(rate_chart, use_container_width=True)

    st.markdown("---")

    # ========================================================================
    # AVERAGE SCORES
    # ========================================================================

    if client and db_stats['total'] > 0:
        st.header("📊 Average PROJ344 Scores")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Relevancy", f"{db_stats['avg_relevancy']:.0f}/999")
        with col2:
            st.metric("Legal", f"{db_stats['avg_legal']:.0f}/999")
        with col3:
            st.metric("Micro", f"{db_stats['avg_micro']:.0f}/999")
        with col4:
            st.metric("Macro", f"{db_stats['avg_macro']:.0f}/999")

        st.markdown("---")

    # ========================================================================
    # LIVE LOG
    # ========================================================================

    st.header("📜 Live Log (Last 50 Lines)")

    with st.expander("View Live Log", expanded=False):
        if log_stats['recent_logs']:
            log_text = ''.join(log_stats['recent_logs'])
            st.code(log_text, language='log')
        else:
            st.info("No log entries yet")

    # ========================================================================
    # SIDEBAR
    # ========================================================================

    st.sidebar.title("⚙️ Monitor Settings")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Quick Stats")
    st.sidebar.metric("Total Processed", log_stats['total_processed'])
    st.sidebar.metric("In Database", db_stats['total'])
    st.sidebar.metric("Total Cost", f"${log_stats['total_cost']:.2f}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔄 Actions")

    if st.sidebar.button("🔄 Refresh Now"):
        st.rerun()

    if st.sidebar.button("📥 Download Log"):
        if Path(LOG_FILE).exists():
            with open(LOG_FILE, 'r') as f:
                log_content = f.read()
            st.sidebar.download_button(
                label="Download Log File",
                data=log_content,
                file_name=f"proj344-scan-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log",
                mime="text/plain"
            )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔗 Quick Links")
    st.sidebar.markdown("[View on GitHub](https://github.com/dondada876/proj344-dashboards)")
    st.sidebar.markdown("[Supabase Dashboard](https://jvjlhxodmbkodzmggwpu.supabase.co)")

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Status:** " + ("🟢 Running" if status == 'running' else "🔴 Stopped"))

if __name__ == "__main__":
    main()
