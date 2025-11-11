#!/usr/bin/env python3
"""
System Overview Dashboard - Port 8507
Master health monitoring across ALL Supabase tables and system components
Shows: Database health, bug tracker, court events, documents, violations
UNIQUE PURPOSE: System-wide health - NOT document details (covered by other dashboards)
"""

import streamlit as st
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

try:
    from supabase import create_client
except ImportError:
    st.error("❌ Install supabase: pip3 install supabase")
    st.stop()

st.set_page_config(
    page_title="System Overview Dashboard",
    page_icon="🎛️",
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
# DATA QUERIES - SYSTEM-WIDE HEALTH
# ============================================================================

@st.cache_data(ttl=30)
def get_system_health(_client):
    """Get health metrics across ALL tables"""
    health = {
        'legal_documents': {'count': 0, 'status': 'unknown', 'last_updated': None},
        'court_events': {'count': 0, 'status': 'unknown', 'last_updated': None},
        'bugs': {'count': 0, 'status': 'unknown', 'last_updated': None},
        'error_logs': {'count': 0, 'status': 'unknown', 'last_updated': None},
        'legal_violations': {'count': 0, 'status': 'unknown', 'last_updated': None},
        'legal_citations': {'count': 0, 'status': 'unknown', 'last_updated': None},
    }

    # Legal Documents
    try:
        result = _client.table('legal_documents').select('id,processed_at', count='exact').execute()
        health['legal_documents']['count'] = result.count or 0
        health['legal_documents']['status'] = 'healthy' if result.count > 0 else 'empty'
        if result.data:
            dates = [d.get('processed_at') for d in result.data if d.get('processed_at')]
            health['legal_documents']['last_updated'] = max(dates) if dates else None
    except Exception as e:
        health['legal_documents']['status'] = 'error'
        health['legal_documents']['error'] = str(e)

    # Court Events
    try:
        result = _client.table('court_events').select('id,created_at', count='exact').execute()
        health['court_events']['count'] = result.count or 0
        health['court_events']['status'] = 'healthy' if result.count > 0 else 'empty'
        if result.data:
            dates = [d.get('created_at') for d in result.data if d.get('created_at')]
            health['court_events']['last_updated'] = max(dates) if dates else None
    except Exception as e:
        health['court_events']['status'] = 'error'
        health['court_events']['error'] = str(e)

    # Bugs
    try:
        result = _client.table('bugs').select('id,created_at', count='exact').execute()
        health['bugs']['count'] = result.count or 0
        health['bugs']['status'] = 'healthy' if result.count > 0 else 'empty'
        if result.data:
            dates = [d.get('created_at') for d in result.data if d.get('created_at')]
            health['bugs']['last_updated'] = max(dates) if dates else None
    except Exception as e:
        health['bugs']['status'] = 'error'
        health['bugs']['error'] = str(e)

    # Error Logs
    try:
        result = _client.table('error_logs').select('id,created_at', count='exact').execute()
        health['error_logs']['count'] = result.count or 0
        health['error_logs']['status'] = 'healthy' if result.count > 0 else 'empty'
        if result.data:
            dates = [d.get('created_at') for d in result.data if d.get('created_at')]
            health['error_logs']['last_updated'] = max(dates) if dates else None
    except Exception as e:
        health['error_logs']['status'] = 'error'
        health['error_logs']['error'] = str(e)

    # Legal Violations
    try:
        result = _client.table('legal_violations').select('id,created_at', count='exact').execute()
        health['legal_violations']['count'] = result.count or 0
        health['legal_violations']['status'] = 'healthy' if result.count > 0 else 'empty'
        if result.data:
            dates = [d.get('created_at') for d in result.data if d.get('created_at')]
            health['legal_violations']['last_updated'] = max(dates) if dates else None
    except Exception as e:
        health['legal_violations']['status'] = 'error'
        health['legal_violations']['error'] = str(e)

    # Legal Citations
    try:
        result = _client.table('legal_citations').select('id,created_at', count='exact').execute()
        health['legal_citations']['count'] = result.count or 0
        health['legal_citations']['status'] = 'healthy' if result.count > 0 else 'empty'
        if result.data:
            dates = [d.get('created_at') for d in result.data if d.get('created_at')]
            health['legal_citations']['last_updated'] = max(dates) if dates else None
    except Exception as e:
        health['legal_citations']['status'] = 'error'
        health['legal_citations']['error'] = str(e)

    return health

@st.cache_data(ttl=60)
def get_bug_tracker_stats(_client):
    """Get bug tracker statistics"""
    try:
        # Get all bugs
        bugs_result = _client.table('bugs').select('*').execute()
        bugs = bugs_result.data

        if not bugs:
            return None

        stats = {
            'total': len(bugs),
            'open': len([b for b in bugs if b.get('status') not in ['RESOLVED', 'CLOSED']]),
            'critical': len([b for b in bugs if b.get('severity') == 'CRITICAL']),
            'by_severity': Counter(b.get('severity') for b in bugs),
            'by_status': Counter(b.get('status') for b in bugs),
            'recent_bugs': sorted(bugs, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
        }

        return stats
    except:
        return None

@st.cache_data(ttl=60)
def get_document_summary(_client):
    """Get high-level document statistics (not detailed - that's for other dashboards)"""
    try:
        result = _client.table('legal_documents').select('relevancy_number,api_cost_usd').execute()
        docs = result.data

        if not docs:
            return None

        return {
            'total': len(docs),
            'high_value': len([d for d in docs if d.get('relevancy_number', 0) >= 900]),
            'critical': len([d for d in docs if d.get('relevancy_number', 0) >= 800]),
            'total_cost': sum(d.get('api_cost_usd', 0) for d in docs)
        }
    except:
        return None

@st.cache_data(ttl=60)
def get_recent_activity(_client):
    """Get recent activity across all tables"""
    activity = []

    # Recent documents
    try:
        docs = _client.table('legal_documents').select('processed_at,original_filename,relevancy_number').order('processed_at', desc=True).limit(5).execute()
        for doc in docs.data:
            activity.append({
                'timestamp': doc.get('processed_at'),
                'type': 'Document Processed',
                'description': f"{doc.get('original_filename')} (Relevancy: {doc.get('relevancy_number')})",
                'icon': '📄'
            })
    except:
        pass

    # Recent bugs
    try:
        bugs = _client.table('bugs').select('created_at,title,severity').order('created_at', desc=True).limit(5).execute()
        for bug in bugs.data:
            activity.append({
                'timestamp': bug.get('created_at'),
                'type': 'Bug Reported',
                'description': f"{bug.get('severity')}: {bug.get('title')}",
                'icon': '🐛'
            })
    except:
        pass

    # Recent court events
    try:
        events = _client.table('court_events').select('event_date,event_title,event_type').order('event_date', desc=True).limit(5).execute()
        for event in events.data:
            activity.append({
                'timestamp': event.get('event_date'),
                'type': 'Court Event',
                'description': f"{event.get('event_type')}: {event.get('event_title')}",
                'icon': '⚖️'
            })
    except:
        pass

    # Sort by timestamp
    activity.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return activity[:15]

# ============================================================================
# VISUALIZATIONS
# ============================================================================

def render_health_gauge(health_data):
    """Render system health gauge"""
    total_tables = len(health_data)
    healthy = len([h for h in health_data.values() if h['status'] == 'healthy'])
    health_percentage = (healthy / total_tables * 100) if total_tables > 0 else 0

    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = health_percentage,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "System Health", 'font': {'size': 24}},
        delta = {'reference': 100},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': 'lightcoral'},
                {'range': [50, 80], 'color': 'lightyellow'},
                {'range': [80, 100], 'color': 'lightgreen'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    return fig

def render_table_distribution(health_data):
    """Render table row count distribution"""
    table_names = list(health_data.keys())
    counts = [health_data[t]['count'] for t in table_names]

    fig = px.bar(
        x=table_names,
        y=counts,
        title="Database Table Row Counts",
        labels={'x': 'Table', 'y': 'Row Count'},
        color=counts,
        color_continuous_scale='Viridis'
    )
    fig.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
    return fig

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

def main():
    # Header
    st.title("🎛️ System Overview Dashboard")
    st.markdown(f"**Port 8507** | Master health monitoring across all system components | **Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.markdown("---")

    # Initialize
    client, error = init_supabase()

    if error or not client:
        st.error(f"❌ Supabase connection failed: {error}")
        st.info("💡 Set environment variables: SUPABASE_URL, SUPABASE_KEY")
        st.stop()

    st.success("✅ Connected to Supabase")

    # Get system health
    health = get_system_health(client)
    bug_stats = get_bug_tracker_stats(client)
    doc_summary = get_document_summary(client)
    recent_activity = get_recent_activity(client)

    # ========================================================================
    # SYSTEM HEALTH OVERVIEW
    # ========================================================================

    st.header("🏥 System Health Status")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.plotly_chart(render_health_gauge(health), use_container_width=True)

    with col2:
        st.subheader("📊 Database Tables")

        for table_name, table_health in health.items():
            status = table_health['status']
            count = table_health['count']
            last_updated = table_health.get('last_updated')

            # Status icon
            if status == 'healthy':
                icon = "✅"
                color = "green"
            elif status == 'empty':
                icon = "⚪"
                color = "gray"
            else:
                icon = "❌"
                color = "red"

            # Display
            col_a, col_b, col_c = st.columns([2, 1, 2])
            with col_a:
                st.markdown(f"{icon} **{table_name}**")
            with col_b:
                st.metric("Rows", f"{count:,}")
            with col_c:
                if last_updated:
                    st.caption(f"Updated: {last_updated[:10]}")
                else:
                    st.caption("Never updated")

    st.markdown("---")

    # ========================================================================
    # KEY METRICS
    # ========================================================================

    st.header("📈 Key System Metrics")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("📄 Documents", f"{health['legal_documents']['count']:,}")

    with col2:
        st.metric("⚖️ Court Events", f"{health['court_events']['count']:,}")

    with col3:
        st.metric("🐛 Total Bugs", f"{health['bugs']['count']:,}")

    with col4:
        if bug_stats:
            st.metric("🔓 Open Bugs", bug_stats['open'], delta=f"-{bug_stats['total']-bug_stats['open']} resolved")
        else:
            st.metric("🔓 Open Bugs", "N/A")

    with col5:
        st.metric("🚨 Violations", f"{health['legal_violations']['count']:,}")

    with col6:
        st.metric("📚 Citations", f"{health['legal_citations']['count']:,}")

    st.markdown("---")

    # ========================================================================
    # TABLE DISTRIBUTION
    # ========================================================================

    st.header("📊 Database Distribution")
    st.plotly_chart(render_table_distribution(health), use_container_width=True)

    st.markdown("---")

    # ========================================================================
    # BUG TRACKER STATUS
    # ========================================================================

    if bug_stats:
        st.header("🐛 Bug Tracker Status")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("By Severity")
            if bug_stats['by_severity']:
                severity_data = []
                for severity, count in bug_stats['by_severity'].most_common():
                    severity_data.append({'Severity': severity or 'Unknown', 'Count': count})
                st.dataframe(pd.DataFrame(severity_data), hide_index=True, use_container_width=True)

        with col2:
            st.subheader("By Status")
            if bug_stats['by_status']:
                status_data = []
                for status, count in bug_stats['by_status'].most_common():
                    status_data.append({'Status': status or 'Unknown', 'Count': count})
                st.dataframe(pd.DataFrame(status_data), hide_index=True, use_container_width=True)

        with col3:
            st.subheader("Recent Bugs")
            for bug in bug_stats['recent_bugs']:
                severity = bug.get('severity', 'UNKNOWN')
                icon = "🔴" if severity == 'CRITICAL' else "🟡" if severity == 'HIGH' else "🟢"
                st.caption(f"{icon} {bug.get('title', 'Untitled')[:40]}")

        st.markdown("---")

    # ========================================================================
    # DOCUMENT SUMMARY
    # ========================================================================

    if doc_summary:
        st.header("📄 Document Intelligence Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Documents", f"{doc_summary['total']:,}")

        with col2:
            st.metric("🔥 Smoking Guns", f"{doc_summary['high_value']}", help="Relevancy ≥ 900")

        with col3:
            st.metric("⚠️ Critical", f"{doc_summary['critical']}", help="Relevancy ≥ 800")

        with col4:
            st.metric("💰 Total API Cost", f"${doc_summary['total_cost']:.2f}")

        st.info("💡 For detailed document analysis, use **PROJ344 Master Dashboard** (Port 8501) or **Legal Intelligence Dashboard** (Port 8503)")

        st.markdown("---")

    # ========================================================================
    # RECENT ACTIVITY
    # ========================================================================

    st.header("🔔 Recent System Activity")

    if recent_activity:
        for activity in recent_activity:
            timestamp = activity.get('timestamp', 'Unknown')[:16] if activity.get('timestamp') else 'Unknown'
            icon = activity.get('icon', '📌')
            activity_type = activity.get('type', 'Unknown')
            description = activity.get('description', 'No description')

            col1, col2, col3 = st.columns([1, 2, 6])
            with col1:
                st.caption(timestamp)
            with col2:
                st.markdown(f"{icon} **{activity_type}**")
            with col3:
                st.caption(description)
    else:
        st.info("No recent activity found")

    st.markdown("---")

    # ========================================================================
    # DASHBOARD QUICK LINKS
    # ========================================================================

    st.header("🔗 Other Dashboards")

    st.markdown("""
    - **Port 8501** - PROJ344 Master Dashboard (All documents, comprehensive analysis)
    - **Port 8502** - CEO Dashboard (File organization, PARA structure)
    - **Port 8503** - Legal Intelligence (High-value documents only, relevancy ≥ 700)
    - **Port 8504** - Enhanced Scanning Monitor (Real-time scan monitoring)
    - **Port 8505** - Scanning Monitor (Basic scan monitoring)
    - **Port 8506** - Timeline Violations (Court events timeline)
    - **Port 8507** - System Overview (This dashboard - system health)
    """)

    # Footer
    st.markdown("---")
    st.caption("🎛️ System Overview Dashboard | Monitoring ASEAGI Project Infrastructure")

if __name__ == "__main__":
    main()
