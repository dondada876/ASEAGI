#!/usr/bin/env python3
"""
Code Repository Sentinel Dashboard
====================================
Streamlit dashboard for visualizing and managing code repository inventory

Features:
- Repository overview with statistics
- Language and framework breakdown
- Quality score distribution
- Dependency tracking
- Health assessment
- Search and filter
- Scan new repositories

Author: ASEAGI Team
Date: 2025-11-18
Version: 1.0.0
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import subprocess

try:
    from supabase import create_client, Client
except ImportError:
    st.error("Supabase not installed. Install with: pip install supabase")
    st.stop()

# ============================================================================
# Configuration
# ============================================================================

st.set_page_config(
    page_title="Code Repository Sentinel",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Supabase connection
@st.cache_resource
def init_supabase():
    """Initialize Supabase client"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        st.error("⚠️ SUPABASE_URL and SUPABASE_KEY must be set in environment")
        st.stop()

    return create_client(url, key)

supabase = init_supabase()

# ============================================================================
# Data Loading
# ============================================================================

@st.cache_data(ttl=300)
def load_repositories():
    """Load all repositories from database"""
    try:
        result = supabase.table("repositories").select("*").execute()
        if result.data:
            return pd.DataFrame(result.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading repositories: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_repository_stats():
    """Load aggregate statistics"""
    df = load_repositories()

    if df.empty:
        return {}

    stats = {
        'total_repos': len(df),
        'total_files': df['total_files'].sum(),
        'total_loc': df['total_lines_of_code'].sum(),
        'avg_quality': df['code_quality_score'].mean(),
        'languages': df['primary_language'].value_counts().to_dict(),
        'frameworks': df[df['framework'].notna()]['framework'].value_counts().to_dict(),
        'status_breakdown': df['current_status'].value_counts().to_dict(),
        'with_tests': len(df[df['has_tests'] == True]),
        'with_docs': len(df[df['has_documentation'] == True]),
        'with_cicd': len(df[df['has_ci_cd'] == True]),
    }

    return stats

@st.cache_data(ttl=300)
def load_health_data():
    """Load repository health view"""
    try:
        result = supabase.table("v_repository_health").select("*").execute()
        if result.data:
            return pd.DataFrame(result.data)
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# ============================================================================
# Helper Functions
# ============================================================================

def format_number(num):
    """Format large numbers with commas"""
    return f"{num:,}" if num else "0"

def format_percentage(value, total):
    """Format as percentage"""
    if total == 0:
        return "0%"
    return f"{(value/total)*100:.1f}%"

def get_health_emoji(health):
    """Get emoji for health status"""
    return {
        'excellent': '🟢',
        'good': '🟡',
        'fair': '🟠',
        'poor': '🔴'
    }.get(health, '⚪')

def get_status_color(status):
    """Get color for status"""
    return {
        'active': 'green',
        'production': 'blue',
        'experimental': 'orange',
        'archived': 'gray',
        'deprecated': 'red'
    }.get(status, 'gray')

# ============================================================================
# Header
# ============================================================================

st.title("🛡️ Code Repository Sentinel")
st.markdown("### Central inventory and health monitoring for all code repositories")

# ============================================================================
# Sidebar - Controls
# ============================================================================

with st.sidebar:
    st.header("🔧 Controls")

    # Refresh data
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    # Filters
    st.subheader("🔍 Filters")

    df = load_repositories()

    if not df.empty:
        # Language filter
        languages = ['All'] + sorted(df['primary_language'].dropna().unique().tolist())
        selected_language = st.selectbox("Language", languages)

        # Framework filter
        frameworks = ['All'] + sorted(df[df['framework'].notna()]['framework'].unique().tolist())
        selected_framework = st.selectbox("Framework", frameworks)

        # Status filter
        statuses = ['All'] + sorted(df['current_status'].unique().tolist())
        selected_status = st.selectbox("Status", statuses)

        # Quality filter
        min_quality = st.slider("Minimum Quality Score", 0, 100, 0)

        # Apply filters
        filtered_df = df.copy()

        if selected_language != 'All':
            filtered_df = filtered_df[filtered_df['primary_language'] == selected_language]

        if selected_framework != 'All':
            filtered_df = filtered_df[filtered_df['framework'] == selected_framework]

        if selected_status != 'All':
            filtered_df = filtered_df[filtered_df['current_status'] == selected_status]

        if min_quality > 0:
            filtered_df = filtered_df[filtered_df['code_quality_score'] >= min_quality]
    else:
        filtered_df = df
        selected_language = 'All'
        selected_framework = 'All'
        selected_status = 'All'
        min_quality = 0

    st.divider()

    # Scan new repository
    st.subheader("➕ Scan New Repository")

    repo_path = st.text_input("Repository Path", placeholder="/path/to/repo")

    if st.button("🔍 Scan Repository", use_container_width=True):
        if repo_path:
            with st.spinner("Scanning repository..."):
                try:
                    result = subprocess.run(
                        ['python3', '/home/user/ASEAGI/scanners/repository_scanner.py', repo_path],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )

                    if result.returncode == 0:
                        st.success("✅ Repository scanned successfully!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {result.stderr}")
                except Exception as e:
                    st.error(f"❌ Error scanning: {e}")
        else:
            st.warning("Please enter a repository path")

# ============================================================================
# Main Content
# ============================================================================

# Load data
stats = load_repository_stats()

if not stats or stats.get('total_repos', 0) == 0:
    st.warning("⚠️ No repositories in inventory. Scan your first repository using the sidebar!")
    st.info("""
    **To get started:**
    1. Enter a repository path in the sidebar
    2. Click "Scan Repository"
    3. View your code inventory here

    **Example:**
    ```
    /home/user/ASEAGI
    ```
    """)
    st.stop()

# ============================================================================
# Overview Statistics
# ============================================================================

st.header("📊 Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Repositories",
        format_number(stats['total_repos']),
        help="Total number of repositories in inventory"
    )

with col2:
    st.metric(
        "Total Lines of Code",
        format_number(stats['total_loc']),
        help="Total lines of code across all repositories"
    )

with col3:
    st.metric(
        "Average Quality Score",
        f"{stats['avg_quality']:.1f}/100" if stats['avg_quality'] else "N/A",
        help="Average code quality score"
    )

with col4:
    st.metric(
        "Total Files",
        format_number(stats['total_files']),
        help="Total number of files across all repositories"
    )

# ============================================================================
# Best Practices Metrics
# ============================================================================

st.subheader("✅ Best Practices Adherence")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "With Tests",
        f"{stats['with_tests']}/{stats['total_repos']}",
        format_percentage(stats['with_tests'], stats['total_repos']),
        help="Repositories with test suites"
    )

with col2:
    st.metric(
        "With Documentation",
        f"{stats['with_docs']}/{stats['total_repos']}",
        format_percentage(stats['with_docs'], stats['total_repos']),
        help="Repositories with documentation"
    )

with col3:
    st.metric(
        "With CI/CD",
        f"{stats['with_cicd']}/{stats['total_repos']}",
        format_percentage(stats['with_cicd'], stats['total_repos']),
        help="Repositories with CI/CD pipelines"
    )

# ============================================================================
# Visualizations
# ============================================================================

st.divider()
st.header("📈 Analytics")

# Language breakdown
col1, col2 = st.columns(2)

with col1:
    st.subheader("Languages")

    if stats['languages']:
        lang_df = pd.DataFrame({
            'Language': stats['languages'].keys(),
            'Count': stats['languages'].values()
        })

        fig = px.pie(
            lang_df,
            values='Count',
            names='Language',
            title='Repositories by Language',
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No language data available")

with col2:
    st.subheader("Frameworks")

    if stats['frameworks']:
        fw_df = pd.DataFrame({
            'Framework': stats['frameworks'].keys(),
            'Count': stats['frameworks'].values()
        })

        fig = px.bar(
            fw_df,
            x='Framework',
            y='Count',
            title='Repositories by Framework',
            color='Count',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No framework data available")

# Quality score distribution
st.subheader("Quality Score Distribution")

if not filtered_df.empty and 'code_quality_score' in filtered_df.columns:
    fig = px.histogram(
        filtered_df,
        x='code_quality_score',
        nbins=20,
        title='Code Quality Score Distribution',
        labels={'code_quality_score': 'Quality Score'},
        color_discrete_sequence=['#1f77b4']
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# Repository Health
# ============================================================================

st.divider()
st.header("🏥 Repository Health")

health_df = load_health_data()

if not health_df.empty:
    # Health status summary
    health_counts = health_df['health_status'].value_counts()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        excellent = health_counts.get('excellent', 0)
        st.metric("🟢 Excellent", excellent)

    with col2:
        good = health_counts.get('good', 0)
        st.metric("🟡 Good", good)

    with col3:
        fair = health_counts.get('fair', 0)
        st.metric("🟠 Fair", fair)

    with col4:
        poor = health_counts.get('poor', 0)
        st.metric("🔴 Poor", poor)

    # Health details table
    st.subheader("Health Details")

    display_df = health_df[[
        'repository_name',
        'health_status',
        'code_quality_score',
        'has_readme',
        'has_tests',
        'has_ci_cd',
        'has_documentation'
    ]].copy()

    display_df['health_status'] = display_df['health_status'].apply(
        lambda x: f"{get_health_emoji(x)} {x.title()}"
    )

    display_df.columns = ['Repository', 'Health', 'Quality', 'README', 'Tests', 'CI/CD', 'Docs']

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Quality": st.column_config.ProgressColumn(
                "Quality",
                help="Code quality score out of 100",
                format="%d",
                min_value=0,
                max_value=100,
            ),
        }
    )

# ============================================================================
# Repository List
# ============================================================================

st.divider()
st.header("📚 Repository List")

if not filtered_df.empty:
    st.caption(f"Showing {len(filtered_df)} of {len(df)} repositories")

    # Search
    search_query = st.text_input("🔍 Search repositories", placeholder="Search by name or description...")

    if search_query:
        filtered_df = filtered_df[
            filtered_df['repository_name'].str.contains(search_query, case=False, na=False) |
            filtered_df['description'].str.contains(search_query, case=False, na=False)
        ]

    # Display repositories
    for idx, repo in filtered_df.iterrows():
        with st.expander(f"📦 {repo['repository_name']} ({repo.get('primary_language', 'Unknown')})"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.write(f"**ID:** {repo['repository_id']}")

                if repo.get('description'):
                    st.write(f"**Description:** {repo['description']}")

                if repo.get('repository_url'):
                    st.write(f"**URL:** {repo['repository_url']}")

                st.write(f"**Path:** {repo.get('local_path', 'N/A')}")

                # Technology
                tech_parts = []
                if repo.get('primary_language'):
                    tech_parts.append(f"Language: {repo['primary_language']}")
                if repo.get('framework'):
                    tech_parts.append(f"Framework: {repo['framework']}")
                if tech_parts:
                    st.write(f"**Technology:** {' | '.join(tech_parts)}")

                # Stats
                stats_parts = []
                if repo.get('total_files'):
                    stats_parts.append(f"{format_number(repo['total_files'])} files")
                if repo.get('total_lines_of_code'):
                    stats_parts.append(f"{format_number(repo['total_lines_of_code'])} LOC")
                if repo.get('total_commits'):
                    stats_parts.append(f"{format_number(repo['total_commits'])} commits")
                if stats_parts:
                    st.write(f"**Stats:** {' | '.join(stats_parts)}")

            with col2:
                # Quality score
                quality = repo.get('code_quality_score', 0)
                st.metric("Quality Score", f"{quality}/100")

                # Status
                status = repo.get('current_status', 'unknown')
                st.markdown(f"**Status:** :{get_status_color(status)}[{status}]")

                # Badges
                badges = []
                if repo.get('has_readme'):
                    badges.append("📖 README")
                if repo.get('has_tests'):
                    badges.append("✅ Tests")
                if repo.get('has_ci_cd'):
                    badges.append("🔄 CI/CD")
                if repo.get('has_documentation'):
                    badges.append("📚 Docs")

                if badges:
                    st.write(" | ".join(badges))

                # Last scanned
                if repo.get('last_scanned_at'):
                    last_scan = pd.to_datetime(repo['last_scanned_at'])
                    st.caption(f"Scanned: {last_scan.strftime('%Y-%m-%d %H:%M')}")

            # Dependencies (if available)
            if repo.get('dependencies'):
                with st.container():
                    st.write("**Dependencies:**")
                    deps = repo['dependencies']
                    dep_items = [f"`{k}`: {v}" for k, v in list(deps.items())[:10]]
                    st.write(", ".join(dep_items))
                    if len(deps) > 10:
                        st.caption(f"... and {len(deps) - 10} more")

else:
    st.info("No repositories match the current filters")

# ============================================================================
# Footer
# ============================================================================

st.divider()
st.caption("""
**Code Repository Sentinel** | Track and monitor all your code repositories in one place
For Ashe. For Justice. For All Children. 🛡️
""")
