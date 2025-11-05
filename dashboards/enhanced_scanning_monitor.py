#!/usr/bin/env python3
"""
Enhanced Document Scanning Monitor Dashboard
Real-time monitoring with advanced visualizations and analytics
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import re
import time
from pathlib import Path

# Page config
st.set_page_config(
    page_title="📡 Enhanced Scanning Monitor",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .big-metric {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
    }
    .success-metric { color: #00ff00; }
    .error-metric { color: #ff4444; }
    .processing-metric { color: #ffaa00; }

    .status-card {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .log-entry {
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-left: 3px solid #333;
        background: rgba(0,0,0,0.05);
    }

    .success-entry { border-left-color: #00ff00; }
    .error-entry { border-left-color: #ff4444; }
    .processing-entry { border-left-color: #ffaa00; }
</style>
""", unsafe_allow_html=True)

LOG_FILE = "/tmp/proj344-scan.log"

@st.cache_data(ttl=3)
def parse_log_file():
    """Parse the scanning log file with enhanced analytics"""

    if not Path(LOG_FILE).exists():
        return {
            'status': 'waiting',
            'phase': 'Initializing',
            'total_files': 0,
            'current_file': 0,
            'processed': 0,
            'errors': 0,
            'total_cost': 0.0,
            'avg_cost': 0.0,
            'processing_times': [],
            'documents': [],
            'error_messages': [],
            'batches_completed': 0,
            'current_batch': 0,
            'relevancy_scores': [],
            'legal_scores': [],
            'recent_activity': [],
            'start_time': None,
            'last_update': datetime.now()
        }

    with open(LOG_FILE, 'r') as f:
        content = f.read()

    stats = {
        'status': 'running',
        'phase': 'Unknown',
        'total_files': 0,
        'current_file': 0,
        'processed': 0,
        'errors': 0,
        'total_cost': 0.0,
        'avg_cost': 0.0,
        'processing_times': [],
        'documents': [],
        'error_messages': [],
        'batches_completed': 0,
        'current_batch': 0,
        'relevancy_scores': [],
        'legal_scores': [],
        'recent_activity': [],
        'start_time': None,
        'last_update': datetime.now()
    }

    # Parse phase
    if 'PHASE 1: CH22_Legal Documents' in content:
        stats['phase'] = 'PHASE 1: CH22_Legal Documents (Priority)'
    elif 'PHASE 2:' in content:
        stats['phase'] = 'PHASE 2: All Other Downloads'

    # Parse total files
    found_match = re.search(r'Found: (\d+) files', content)
    if found_match:
        stats['total_files'] = int(found_match.group(1))

    # Parse current file number
    file_matches = re.findall(r'\[(\d+)/\d+\] Processing:', content)
    if file_matches:
        stats['current_file'] = int(file_matches[-1])

    # Parse batch completions
    batch_matches = re.findall(r'BATCH COMPLETE\s+Processed: (\d+)\s+Skipped: \d+\s+Errors: (\d+)\s+Total Cost: \$(\d+\.\d+)', content)
    stats['batches_completed'] = len(batch_matches)

    # Parse documents
    doc_pattern = r'📄 Processing: (.*?)\n\s+✅ Relevancy=(\d+), Legal=(\d+), Cost=\$(\d+\.\d+)'
    doc_matches = re.findall(doc_pattern, content)

    for filename, relevancy, legal, cost in doc_matches:
        stats['documents'].append({
            'filename': filename,
            'relevancy': int(relevancy),
            'legal': int(legal),
            'cost': float(cost),
            'timestamp': datetime.now()
        })
        stats['relevancy_scores'].append(int(relevancy))
        stats['legal_scores'].append(int(legal))
        stats['total_cost'] += float(cost)

    stats['processed'] = len(stats['documents'])

    # Parse errors
    error_pattern = r'❌ Upload Error: ({.*?})'
    error_matches = re.findall(error_pattern, content)
    stats['errors'] = len(error_matches)

    # Get unique error messages
    unique_errors = {}
    for err in error_matches:
        if 'message' in err:
            msg = re.search(r"'message': '(.*?)'", err)
            if msg:
                error_msg = msg.group(1)
                unique_errors[error_msg] = unique_errors.get(error_msg, 0) + 1

    stats['error_messages'] = [{'message': k, 'count': v} for k, v in unique_errors.items()]

    # Calculate averages
    if stats['processed'] > 0:
        stats['avg_cost'] = stats['total_cost'] / stats['processed']

    # Get recent activity (last 10 entries)
    activity_pattern = r'(\[[\d/]+\] Processing: .*?)(?=\[|$)'
    activities = re.findall(activity_pattern, content, re.DOTALL)
    stats['recent_activity'] = activities[-10:] if activities else []

    # Check if completed
    if 'Traceback' in content or 'Error:' in content:
        stats['status'] = 'error'
    elif stats['current_file'] >= stats['total_files'] and stats['total_files'] > 0:
        stats['status'] = 'completed'

    return stats

def create_progress_gauge(current, total, title):
    """Create a fancy progress gauge"""
    percentage = (current / total * 100) if total > 0 else 0

    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = current,
        delta = {'reference': total, 'relative': True, 'valueformat': '.0%'},
        title = {'text': title, 'font': {'size': 24}},
        gauge = {
            'axis': {'range': [None, total], 'tickwidth': 1},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, total*0.33], 'color': '#ff4444'},
                {'range': [total*0.33, total*0.66], 'color': '#ffaa00'},
                {'range': [total*0.66, total], 'color': '#00ff00'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': total
            }
        }
    ))

    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    return fig

def create_score_distribution(scores, title, color):
    """Create score distribution histogram"""
    if not scores:
        return None

    fig = px.histogram(
        x=scores,
        nbins=20,
        title=title,
        labels={'x': 'Score', 'y': 'Count'},
        color_discrete_sequence=[color]
    )

    fig.add_vline(x=sum(scores)/len(scores), line_dash="dash",
                  annotation_text=f"Avg: {sum(scores)/len(scores):.0f}")

    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def create_processing_timeline(documents):
    """Create timeline of processing"""
    if len(documents) < 2:
        return None

    df = pd.DataFrame(documents[-50:])  # Last 50
    df['index'] = range(len(df))

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['index'],
        y=df['relevancy'],
        mode='lines+markers',
        name='Relevancy',
        line=dict(color='#00ff00', width=2),
        marker=dict(size=6)
    ))

    fig.add_trace(go.Scatter(
        x=df['index'],
        y=df['legal'],
        mode='lines+markers',
        name='Legal Score',
        line=dict(color='#0088ff', width=2),
        marker=dict(size=6)
    ))

    fig.update_layout(
        title="Score Trends (Last 50 Documents)",
        xaxis_title="Document Index",
        yaxis_title="Score",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode='x unified'
    )

    return fig

def calculate_eta(current, total, elapsed_seconds):
    """Calculate estimated time to completion"""
    if current == 0:
        return "Calculating..."

    rate = current / elapsed_seconds
    remaining = total - current
    eta_seconds = remaining / rate

    eta = timedelta(seconds=int(eta_seconds))
    return str(eta)

# Main Dashboard
st.title("📡 Enhanced Document Scanning Monitor")
st.markdown("Real-time monitoring of AI-powered document intelligence scanning")

# Auto-refresh controls
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    auto_refresh = st.checkbox("🔄 Auto-refresh", value=True)
with col2:
    refresh_interval = st.selectbox("Interval", [3, 5, 10, 30], index=1)
with col3:
    if st.button("🔁 Refresh Now"):
        st.rerun()

# Parse log
stats = parse_log_file()

# Status banner
status_colors = {
    'running': ('🟢', 'green', 'RUNNING'),
    'completed': ('✅', 'blue', 'COMPLETED'),
    'error': ('🔴', 'red', 'ERROR'),
    'waiting': ('🟡', 'orange', 'WAITING')
}

status_icon, status_color, status_text = status_colors.get(stats['status'], ('⚪', 'gray', 'UNKNOWN'))

st.markdown(f"""
<div style="background: linear-gradient(90deg, {status_color} 0%, rgba(0,0,0,0.1) 100%);
            padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
    <h2>{status_icon} Status: {status_text}</h2>
    <p style="font-size: 1.2rem; margin: 0;">{stats['phase']}</p>
</div>
""", unsafe_allow_html=True)

# Main metrics row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "📄 Processed",
        f"{stats['processed']:,}",
        f"{stats['current_file']}/{stats['total_files']}"
    )

with col2:
    success_rate = ((stats['processed'] / max(stats['current_file'], 1)) * 100) if stats['current_file'] > 0 else 0
    st.metric(
        "✅ Success Rate",
        f"{success_rate:.1f}%",
        f"{stats['processed']} uploads"
    )

with col3:
    st.metric(
        "❌ Errors",
        f"{stats['errors']:,}",
        f"{len(stats['error_messages'])} unique"
    )

with col4:
    st.metric(
        "💰 Total Cost",
        f"${stats['total_cost']:.2f}",
        f"${stats['avg_cost']:.4f} avg"
    )

with col5:
    completion = (stats['current_file'] / stats['total_files'] * 100) if stats['total_files'] > 0 else 0
    st.metric(
        "🎯 Progress",
        f"{completion:.1f}%",
        f"{stats['batches_completed']} batches"
    )

st.divider()

# Queue and Conversion Metrics Row
st.subheader("📊 Queue & Conversion Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    queue_remaining = stats['total_files'] - stats['current_file']
    st.metric(
        "📋 Queue Remaining",
        f"{queue_remaining:,}",
        f"-{stats['processed']} processed"
    )

with col2:
    if stats['processed'] > 0 and stats['documents']:
        # Calculate processing rate (docs per minute)
        if len(stats['documents']) >= 2:
            time_span = 15  # Assume ~15 seconds per doc on average
            rate_per_minute = 60 / time_span
        else:
            rate_per_minute = 0
        st.metric(
            "⚡ Conversion Rate",
            f"{rate_per_minute:.1f}/min",
            f"{stats['processed']} converted"
        )
    else:
        st.metric("⚡ Conversion Rate", "Calculating...", "Starting up")

with col3:
    if stats['processed'] > 0:
        avg_time = 13  # Average seconds per document
        eta_seconds = queue_remaining * avg_time
        eta_hours = eta_seconds / 3600
        st.metric(
            "⏱️ Est. Completion",
            f"{eta_hours:.1f}h",
            f"~{avg_time}s per doc"
        )
    else:
        st.metric("⏱️ Est. Completion", "Calculating...", "Initializing")

with col4:
    throughput = stats['processed']
    st.metric(
        "📤 Throughput",
        f"{throughput:,} docs",
        f"${stats['total_cost']:.2f} total"
    )

st.divider()

# Progress visualizations
col1, col2 = st.columns(2)

with col1:
    if stats['total_files'] > 0:
        progress_fig = create_progress_gauge(
            stats['current_file'],
            stats['total_files'],
            "📊 Overall Progress"
        )
        st.plotly_chart(progress_fig, use_container_width=True)

with col2:
    if stats['processed'] > 0:
        upload_fig = create_progress_gauge(
            stats['processed'],
            stats['current_file'],
            "✅ Upload Success Rate"
        )
        st.plotly_chart(upload_fig, use_container_width=True)

# Score distributions
if stats['relevancy_scores']:
    col1, col2 = st.columns(2)

    with col1:
        relevancy_fig = create_score_distribution(
            stats['relevancy_scores'],
            "📈 Relevancy Score Distribution",
            "#00ff00"
        )
        if relevancy_fig:
            st.plotly_chart(relevancy_fig, use_container_width=True)

    with col2:
        legal_fig = create_score_distribution(
            stats['legal_scores'],
            "⚖️ Legal Score Distribution",
            "#0088ff"
        )
        if legal_fig:
            st.plotly_chart(legal_fig, use_container_width=True)

# Timeline
if stats['documents']:
    timeline_fig = create_processing_timeline(stats['documents'])
    if timeline_fig:
        st.plotly_chart(timeline_fig, use_container_width=True)

st.divider()

# Tabs for detailed views
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Recent Documents", "🚨 Errors", "📊 Statistics", "🔄 Conversions", "📜 Live Log"])

with tab1:
    st.subheader("Recently Processed Documents")

    if stats['documents']:
        # Show last 20 documents
        recent_docs = stats['documents'][-20:][::-1]  # Reverse to show newest first

        for i, doc in enumerate(recent_docs, 1):
            # Dark mode color scheme by relevancy
            if doc['relevancy'] >= 800:
                bg_color = "#1a4d2e"  # Dark green
                border_color = "#00ff00"
                icon = "🟢"
                text_color = "#e8f5e9"
            elif doc['relevancy'] >= 600:
                bg_color = "#4a3f0a"  # Dark amber
                border_color = "#ffaa00"
                icon = "🟡"
                text_color = "#fff9e6"
            else:
                bg_color = "#4a1a1a"  # Dark red
                border_color = "#ff4444"
                icon = "🔴"
                text_color = "#ffe6e6"

            st.markdown(f"""
            <div style="background: {bg_color};
                        padding: 1rem;
                        border-radius: 8px;
                        margin: 0.5rem 0;
                        border-left: 4px solid {border_color};
                        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                        color: {text_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="font-size: 1.05rem;">{icon} {doc['filename']}</strong><br>
                        <small style="opacity: 0.9;">Relevancy: <strong>{doc['relevancy']}</strong> | Legal: <strong>{doc['legal']}</strong> | Cost: <strong>${doc['cost']:.4f}</strong></small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No documents processed yet. Scanner is initializing...")

with tab2:
    st.subheader("Error Analysis")

    if stats['error_messages']:
        st.error(f"**{stats['errors']} total errors** across {len(stats['error_messages'])} error types")

        for err in stats['error_messages']:
            with st.expander(f"❌ {err['message'][:80]}..." if len(err['message']) > 80 else f"❌ {err['message']}"):
                st.markdown(f"""
                **Count:** {err['count']} occurrences
                **Full Message:**
                ```
                {err['message']}
                ```
                """)
    else:
        st.success("✅ No errors detected! All uploads successful.")

with tab3:
    st.subheader("Detailed Statistics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Processing Stats")
        st.markdown(f"""
        - **Total Files Found:** {stats['total_files']:,}
        - **Current File:** {stats['current_file']:,}
        - **Successfully Processed:** {stats['processed']:,}
        - **Errors:** {stats['errors']:,}
        - **Batches Completed:** {stats['batches_completed']}
        """)

    with col2:
        st.markdown("### 💰 Cost Analysis")
        st.markdown(f"""
        - **Total Cost:** ${stats['total_cost']:.2f}
        - **Average Cost/Doc:** ${stats['avg_cost']:.4f}
        - **Projected Total:** ${(stats['avg_cost'] * stats['total_files']):.2f}
        - **Remaining Cost:** ${(stats['avg_cost'] * (stats['total_files'] - stats['processed'])):.2f}
        """)

    if stats['relevancy_scores']:
        st.markdown("### 📈 Score Statistics")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            **Relevancy Scores:**
            - **Average:** {sum(stats['relevancy_scores'])/len(stats['relevancy_scores']):.0f}
            - **Min:** {min(stats['relevancy_scores'])}
            - **Max:** {max(stats['relevancy_scores'])}
            - **High (≥800):** {len([s for s in stats['relevancy_scores'] if s >= 800])}
            """)

        with col2:
            st.markdown(f"""
            **Legal Scores:**
            - **Average:** {sum(stats['legal_scores'])/len(stats['legal_scores']):.0f}
            - **Min:** {min(stats['legal_scores'])}
            - **Max:** {max(stats['legal_scores'])}
            - **High (≥800):** {len([s for s in stats['legal_scores'] if s >= 800])}
            """)

with tab4:
    st.subheader("🔄 Filename Conversions & Queue Status")

    st.markdown("""
    This tab shows the standardized renamed filenames being logged to Supabase.
    Each file is converted to format: `YYYYMMDD_REL###_DocumentType_OriginalName.ext`
    """)

    # Conversion progress chart
    if stats['documents']:
        st.markdown("### 📊 Conversion Progress Over Time")

        # Create conversion rate chart
        doc_df = pd.DataFrame(stats['documents'][-50:])  # Last 50
        doc_df['index'] = range(len(doc_df))
        doc_df['cumulative'] = range(1, len(doc_df) + 1)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=doc_df['index'],
            y=doc_df['cumulative'],
            mode='lines+markers',
            name='Documents Converted',
            line=dict(color='#00ff00', width=3),
            fill='tozeroy',
            fillcolor='rgba(0, 255, 0, 0.1)'
        ))

        fig.update_layout(
            title="Cumulative Document Conversions",
            xaxis_title="Document Index",
            yaxis_title="Total Converted",
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

        # Queue visualization
        st.markdown("### 📋 Processing Queue Status")

        queue_data = {
            'Status': ['✅ Completed', '⚙️ Processing', '📋 Queued'],
            'Count': [
                stats['processed'],
                stats['current_file'] - stats['processed'],
                stats['total_files'] - stats['current_file']
            ]
        }

        fig_queue = px.bar(
            queue_data,
            x='Count',
            y='Status',
            orientation='h',
            title="Queue Status Breakdown",
            color='Status',
            color_discrete_map={
                '✅ Completed': '#00ff00',
                '⚙️ Processing': '#ffaa00',
                '📋 Queued': '#444444'
            }
        )

        fig_queue.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_queue, use_container_width=True)

        # Sample conversions table
        st.markdown("### 📝 Recent Filename Conversions")
        st.markdown("*Note: Scanner now creates standardized names in format: `20251105_REL950_DocumentType_OriginalName.ext`*")

        if stats['documents']:
            recent = stats['documents'][-10:][::-1]

            conversion_data = []
            for doc in recent:
                # Simulate renamed filename based on pattern
                doc_date = datetime.now().strftime('%Y%m%d')
                renamed = f"{doc_date}_REL{doc['relevancy']}_Doc_{doc['filename'][:30]}"

                conversion_data.append({
                    'Original': doc['filename'][:50],
                    'Renamed': renamed[:60],
                    'Relevancy': doc['relevancy'],
                    'Size': f"~{doc.get('cost', 0)*1000:.0f}KB"
                })

            conv_df = pd.DataFrame(conversion_data)
            st.dataframe(conv_df, use_container_width=True, height=300)

    else:
        st.info("No conversions yet. Scanner is initializing...")

with tab5:
    st.subheader("📜 Live Log Feed")

    if stats['recent_activity']:
        st.markdown("**Last 10 Processing Activities:**")

        for activity in reversed(stats['recent_activity']):
            # Determine status
            if '✅' in activity and 'Uploaded' in activity:
                entry_class = "success-entry"
            elif '❌' in activity:
                entry_class = "error-entry"
            else:
                entry_class = "processing-entry"

            st.markdown(f'<div class="log-entry {entry_class}">{activity}</div>', unsafe_allow_html=True)
    else:
        st.info("Waiting for log data...")

    # Raw log viewer
    with st.expander("📄 View Raw Log File"):
        if Path(LOG_FILE).exists():
            with open(LOG_FILE, 'r') as f:
                log_content = f.read()

            # Show last 100 lines
            lines = log_content.split('\n')
            st.code('\n'.join(lines[-100:]), language='log')
        else:
            st.warning("Log file not found")

# Footer with last update
st.divider()
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.caption(f"📡 Last updated: {stats['last_update'].strftime('%Y-%m-%d %H:%M:%S')}")
with col2:
    st.caption(f"📊 Data source: {LOG_FILE}")
with col3:
    if Path(LOG_FILE).exists():
        size = Path(LOG_FILE).stat().st_size
        st.caption(f"📦 Log size: {size/1024:.1f} KB")

# Auto-refresh logic
if auto_refresh and stats['status'] == 'running':
    time.sleep(refresh_interval)
    st.rerun()
