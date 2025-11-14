"""
ASEAGI Dashboard - Monitoring & Control
Streamlit interface for hybrid cloud system
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client

# Page configuration
st.set_page_config(
    page_title="ASEAGI Control Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
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
    .status-running {
        color: #10b981;
        font-weight: bold;
    }
    .status-stopped {
        color: #ef4444;
        font-weight: bold;
    }
    .status-queued {
        color: #f59e0b;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Environment variables
API_URL = os.getenv("API_URL", "http://api:5000")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()


# API calls
@st.cache_data(ttl=10)
def get_system_stats() -> Dict:
    """Get system statistics from API"""
    try:
        response = requests.get(f"{API_URL}/stats", timeout=5)
        return response.json()
    except Exception as e:
        st.error(f"Failed to connect to API: {e}")
        return {}


@st.cache_data(ttl=10)
def get_instances() -> List[Dict]:
    """Get Vast.ai instances"""
    try:
        response = requests.get(f"{API_URL}/instances", timeout=5)
        return response.json().get('instances', [])
    except Exception as e:
        st.error(f"Failed to get instances: {e}")
        return []


@st.cache_data(ttl=60)
def get_documents(limit: int = 100) -> pd.DataFrame:
    """Get recent documents"""
    try:
        result = supabase.table('legal_documents')\
            .select('*')\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        return pd.DataFrame(result.data)
    except Exception as e:
        st.error(f"Failed to fetch documents: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=30)
def get_processing_jobs(status: str = None) -> pd.DataFrame:
    """Get processing jobs"""
    try:
        query = supabase.table('processing_jobs').select('*')
        if status:
            query = query.eq('status', status)
        result = query.order('created_at', desc=True).limit(100).execute()
        return pd.DataFrame(result.data)
    except Exception as e:
        st.error(f"Failed to fetch jobs: {e}")
        return pd.DataFrame()


def launch_instance():
    """Launch new Vast.ai instance"""
    try:
        response = requests.post(f"{API_URL}/instances/launch", timeout=10)
        if response.status_code == 201:
            st.success("✅ Instance launched successfully!")
            st.cache_data.clear()
        else:
            st.error(f"❌ Failed to launch instance: {response.text}")
    except Exception as e:
        st.error(f"❌ Error: {e}")


def destroy_instance(instance_id: int):
    """Destroy Vast.ai instance"""
    try:
        response = requests.delete(f"{API_URL}/instances/{instance_id}", timeout=10)
        if response.status_code == 200:
            st.success(f"✅ Instance {instance_id} destroyed!")
            st.cache_data.clear()
        else:
            st.error(f"❌ Failed to destroy instance: {response.text}")
    except Exception as e:
        st.error(f"❌ Error: {e}")


# Sidebar
with st.sidebar:
    st.title("🤖 ASEAGI")
    st.caption("Hybrid Cloud Control Panel")

    st.divider()

    # Navigation
    page = st.radio(
        "Navigation",
        ["📊 Overview", "📁 Documents", "⚙️ Processing Jobs", "🖥️ Instances", "💰 Costs"],
        label_visibility="collapsed"
    )

    st.divider()

    # Quick actions
    st.subheader("Quick Actions")

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    if st.button("🚀 Launch Instance", use_container_width=True):
        launch_instance()

    st.divider()

    # System health
    st.caption("System Health")
    try:
        health = requests.get(f"{API_URL}/health", timeout=5).json()
        st.success("✅ API Online")
        st.caption(f"Last check: {health.get('timestamp', 'N/A')[:19]}")
    except:
        st.error("❌ API Offline")


# Main content
st.title("ASEAGI Control Dashboard")

# Get stats
stats = get_system_stats()

if page == "📊 Overview":
    st.header("System Overview")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Documents",
            stats.get('total_documents', 0),
            delta=None
        )

    with col2:
        st.metric(
            "Queue Size",
            stats.get('queue_size', 0),
            delta=None
        )

    with col3:
        st.metric(
            "Active Instances",
            stats.get('active_instances', 0),
            delta=None
        )

    with col4:
        job_status = stats.get('job_status', {})
        completed = job_status.get('completed', 0)
        st.metric(
            "Completed Jobs",
            completed,
            delta=None
        )

    st.divider()

    # Job status breakdown
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Job Status Distribution")
        if stats.get('job_status'):
            df_status = pd.DataFrame(
                list(stats['job_status'].items()),
                columns=['Status', 'Count']
            )
            fig = px.pie(df_status, values='Count', names='Status',
                        color_discrete_sequence=px.colors.sequential.Purples)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No job data available")

    with col2:
        st.subheader("Processing Timeline")
        # Get recent jobs
        jobs_df = get_processing_jobs()
        if not jobs_df.empty and 'created_at' in jobs_df.columns:
            jobs_df['created_at'] = pd.to_datetime(jobs_df['created_at'])
            jobs_df['date'] = jobs_df['created_at'].dt.date

            timeline = jobs_df.groupby('date').size().reset_index(name='count')
            fig = px.line(timeline, x='date', y='count',
                         labels={'date': 'Date', 'count': 'Jobs'},
                         markers=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No timeline data available")

    # Recent activity
    st.subheader("Recent Activity")
    recent_jobs = get_processing_jobs().head(10)
    if not recent_jobs.empty:
        for _, job in recent_jobs.iterrows():
            status_class = f"status-{job.get('status', 'unknown')}"
            st.markdown(
                f"**{job.get('job_id', 'N/A')}** - "
                f"<span class='{status_class}'>{job.get('status', 'Unknown').upper()}</span> - "
                f"{job.get('file_path', 'N/A')}",
                unsafe_allow_html=True
            )
    else:
        st.info("No recent activity")


elif page == "📁 Documents":
    st.header("Document Browser")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        search_term = st.text_input("🔍 Search", placeholder="Search documents...")

    with col2:
        category_filter = st.selectbox(
            "Category",
            ["All", "Legal", "Financial", "Personal", "Business"]
        )

    with col3:
        min_relevancy = st.slider("Min Relevancy", 0, 1000, 0)

    # Get documents
    docs_df = get_documents(limit=500)

    if not docs_df.empty:
        # Apply filters
        if search_term:
            docs_df = docs_df[
                docs_df['file_name'].str.contains(search_term, case=False, na=False) |
                docs_df['extracted_text'].str.contains(search_term, case=False, na=False)
            ]

        if category_filter != "All":
            docs_df = docs_df[docs_df['category'].str.contains(category_filter, case=False, na=False)]

        if min_relevancy > 0:
            docs_df = docs_df[docs_df['relevancy_number'] >= min_relevancy]

        # Display stats
        st.caption(f"Showing {len(docs_df)} documents")

        # Documents table
        display_cols = ['file_name', 'category', 'relevancy_number',
                       'macro_score', 'legal_score', 'created_at']
        available_cols = [col for col in display_cols if col in docs_df.columns]

        st.dataframe(
            docs_df[available_cols],
            use_container_width=True,
            hide_index=True
        )

        # Document details
        st.subheader("Document Details")
        if not docs_df.empty:
            selected_doc = st.selectbox(
                "Select document",
                docs_df['file_name'].tolist() if 'file_name' in docs_df.columns else [],
                key="doc_select"
            )

            if selected_doc:
                doc = docs_df[docs_df['file_name'] == selected_doc].iloc[0]

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**File Name:**", doc.get('file_name', 'N/A'))
                    st.write("**Category:**", doc.get('category', 'N/A'))
                    st.write("**Relevancy:**", doc.get('relevancy_number', 'N/A'))

                with col2:
                    st.write("**Macro Score:**", doc.get('macro_score', 'N/A'))
                    st.write("**Legal Score:**", doc.get('legal_score', 'N/A'))
                    st.write("**Created:**", doc.get('created_at', 'N/A'))

                if 'extracted_text' in doc and doc['extracted_text']:
                    with st.expander("📄 Extracted Text"):
                        st.text(doc['extracted_text'][:1000])
    else:
        st.info("No documents found")


elif page == "⚙️ Processing Jobs":
    st.header("Processing Jobs")

    # Status filter
    status_filter = st.selectbox(
        "Filter by status",
        ["All", "queued", "processing", "completed", "error"]
    )

    # Get jobs
    if status_filter == "All":
        jobs_df = get_processing_jobs()
    else:
        jobs_df = get_processing_jobs(status=status_filter)

    if not jobs_df.empty:
        st.caption(f"Showing {len(jobs_df)} jobs")

        # Jobs table
        display_cols = ['job_id', 'file_path', 'status', 'created_at', 'completed_at']
        available_cols = [col for col in display_cols if col in jobs_df.columns]

        st.dataframe(
            jobs_df[available_cols],
            use_container_width=True,
            hide_index=True
        )

        # Job details
        st.subheader("Job Details")
        if 'job_id' in jobs_df.columns:
            selected_job = st.selectbox(
                "Select job",
                jobs_df['job_id'].tolist(),
                key="job_select"
            )

            if selected_job:
                job = jobs_df[jobs_df['job_id'] == selected_job].iloc[0]

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Job ID:**", job.get('job_id', 'N/A'))
                    st.write("**File Path:**", job.get('file_path', 'N/A'))
                    st.write("**Status:**", job.get('status', 'N/A'))

                with col2:
                    st.write("**Created:**", job.get('created_at', 'N/A'))
                    st.write("**Completed:**", job.get('completed_at', 'N/A'))

                if 'metadata' in job and job['metadata']:
                    with st.expander("📋 Metadata"):
                        st.json(job['metadata'])
    else:
        st.info(f"No {status_filter} jobs found")


elif page == "🖥️ Instances":
    st.header("Vast.ai Instances")

    instances = get_instances()

    if instances:
        st.caption(f"{len(instances)} instance(s)")

        for instance in instances:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

                with col1:
                    st.write(f"**Instance {instance.get('id', 'N/A')}**")
                    st.caption(f"GPU: {instance.get('gpu_name', 'N/A')}")

                with col2:
                    status = instance.get('actual_status', 'unknown')
                    status_class = 'status-running' if status == 'running' else 'status-stopped'
                    st.markdown(f"<span class='{status_class}'>{status.upper()}</span>",
                              unsafe_allow_html=True)

                with col3:
                    st.metric("Cost/hr", f"${instance.get('dph_total', 0):.3f}")

                with col4:
                    if st.button("🗑️ Destroy", key=f"destroy_{instance.get('id')}"):
                        destroy_instance(instance.get('id'))

                st.divider()
    else:
        st.info("No active instances")

        if st.button("🚀 Launch New Instance", use_container_width=True):
            launch_instance()


elif page == "💰 Costs":
    st.header("Cost Tracking")

    # Cost summary
    costs = stats.get('costs', {})

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Costs", f"${costs.get('total', 0):.2f}")

    with col2:
        st.metric("This Month", f"${costs.get('month', 0):.2f}")

    with col3:
        st.metric("Today", f"${costs.get('today', 0):.2f}")

    st.divider()

    # Cost breakdown
    st.subheader("Cost Breakdown")

    # Get instance history
    try:
        instances = supabase.table('vastai_instances')\
            .select('*')\
            .order('launched_at', desc=True)\
            .limit(100)\
            .execute()

        if instances.data:
            df_instances = pd.DataFrame(instances.data)

            # Calculate runtime and costs
            if 'launched_at' in df_instances.columns and 'destroyed_at' in df_instances.columns:
                df_instances['launched_at'] = pd.to_datetime(df_instances['launched_at'])
                df_instances['destroyed_at'] = pd.to_datetime(df_instances['destroyed_at'])

                df_instances['runtime_hours'] = (
                    df_instances['destroyed_at'] - df_instances['launched_at']
                ).dt.total_seconds() / 3600

                # Estimate costs (assuming $0.40/hr average)
                df_instances['estimated_cost'] = df_instances['runtime_hours'] * 0.40

                # Display table
                st.dataframe(
                    df_instances[['instance_id', 'launched_at', 'destroyed_at',
                                 'runtime_hours', 'estimated_cost']],
                    use_container_width=True,
                    hide_index=True
                )

                # Charts
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Daily Costs")
                    df_instances['date'] = df_instances['launched_at'].dt.date
                    daily_costs = df_instances.groupby('date')['estimated_cost'].sum().reset_index()
                    fig = px.bar(daily_costs, x='date', y='estimated_cost',
                               labels={'date': 'Date', 'estimated_cost': 'Cost ($)'})
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.subheader("Runtime Distribution")
                    fig = px.histogram(df_instances, x='runtime_hours',
                                     labels={'runtime_hours': 'Runtime (hours)'})
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.dataframe(df_instances, use_container_width=True)
        else:
            st.info("No instance history available")
    except Exception as e:
        st.error(f"Failed to load cost data: {e}")

# Footer
st.divider()
st.caption("ASEAGI Hybrid Cloud System - DigitalOcean + Vast.ai")
