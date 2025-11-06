#!/usr/bin/env python3
"""
CEO Global Dashboard
====================
Holistic life management dashboard across all areas:
- Business Operations
- Legal Matters (PROJ344 summary)
- Family & Daughter
- Personal Development
- Task Management

Port: 8503
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client

# Try to load dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, will use system environment variables
    pass

# Import custom styling
from proj344_style import inject_custom_css, render_header, render_metric_card

# ============================================
# CONFIGURATION
# ============================================

st.set_page_config(
    page_title="CEO Global Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Supabase
# Try Streamlit secrets first, then environment variables
SUPABASE_URL = st.secrets.get("SUPABASE_URL") if hasattr(st, 'secrets') else os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") if hasattr(st, 'secrets') else os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Missing SUPABASE_URL or SUPABASE_KEY in secrets.toml or environment variables")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Inject custom CSS
inject_custom_css()

# ============================================
# CUSTOM CSS FOR CEO DASHBOARD
# ============================================

st.markdown("""
<style>
    /* CEO Dashboard specific styles */
    .ceo-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        color: white;
        margin: 1rem 0;
    }

    .life-area-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }

    .okr-progress {
        background: #f1f5f9;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }

    .daughter-memory {
        background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #2d3436;
    }

    .priority-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }

    .p1-badge { background: #dc2626; color: white; }
    .p2-badge { background: #f59e0b; color: white; }
    .p3-badge { background: #3b82f6; color: white; }
    .p4-badge { background: #6b7280; color: white; }

    .revenue-chart {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# HELPER FUNCTIONS
# ============================================

@st.cache_data(ttl=300)
def get_cross_system_priorities():
    """Get all active priorities across both systems"""
    try:
        result = supabase.table("cross_system_priorities")\
            .select("*")\
            .in_("status", ["active", "in_progress"])\
            .order("priority_level")\
            .execute()
        return result.data if result.data else []
    except:
        return []

@st.cache_data(ttl=300)
def get_revenue_data():
    """Get revenue log data"""
    try:
        result = supabase.table("revenue_log")\
            .select("*")\
            .order("logged_at", desc=True)\
            .limit(100)\
            .execute()
        return result.data if result.data else []
    except:
        return []

@st.cache_data(ttl=300)
def get_business_documents():
    """Get recent business documents"""
    try:
        result = supabase.table("business_documents")\
            .select("*")\
            .order("created_at", desc=True)\
            .limit(20)\
            .execute()
        return result.data if result.data else []
    except:
        return []

@st.cache_data(ttl=300)
def get_family_documents():
    """Get daughter-related documents"""
    try:
        result = supabase.table("family_documents")\
            .select("*")\
            .order("created_at", desc=True)\
            .limit(20)\
            .execute()
        return result.data if result.data else []
    except:
        return []

@st.cache_data(ttl=300)
def get_ceo_okrs():
    """Get active OKRs"""
    try:
        result = supabase.table("ceo_okrs")\
            .select("*")\
            .eq("status", "active")\
            .order("created_at", desc=True)\
            .execute()
        return result.data if result.data else []
    except:
        return []

def get_proj344_summary():
    """Get PROJ344 status summary"""
    try:
        # Get priority legal items
        legal_priorities = supabase.table("cross_system_priorities")\
            .select("*")\
            .eq("source_system", "proj344")\
            .in_("status", ["active", "in_progress"])\
            .execute()

        # Get recent legal documents
        legal_docs = supabase.table("legal_documents")\
            .select("id")\
            .execute()

        return {
            "active_priorities": len(legal_priorities.data) if legal_priorities.data else 0,
            "total_documents": len(legal_docs.data) if legal_docs.data else 0
        }
    except:
        return {"active_priorities": 0, "total_documents": 0}

# ============================================
# SIDEBAR NAVIGATION
# ============================================

st.sidebar.title("🎯 CEO Global Dashboard")
st.sidebar.markdown("---")

view = st.sidebar.radio(
    "Navigate",
    ["📊 Executive Overview", "💰 Business Operations", "⚖️ Legal Matters",
     "👨‍👧 Family & Daughter", "🏃 Personal Development", "📋 Task Management"],
    index=0
)

st.sidebar.markdown("---")

# Quick stats in sidebar
st.sidebar.markdown("### 📈 Quick Stats")

priorities = get_cross_system_priorities()
p1_count = len([p for p in priorities if p.get("priority_level") == "P1"])
p2_count = len([p for p in priorities if p.get("priority_level") == "P2"])

st.sidebar.metric("P1 Priorities", p1_count, delta=None)
st.sidebar.metric("P2 Priorities", p2_count, delta=None)

# Revenue today (if available)
revenue_data = get_revenue_data()
if revenue_data:
    today_revenue = sum([r.get("amount", 0) for r in revenue_data
                        if r.get("logged_at", "").startswith(datetime.now().strftime("%Y-%m-%d"))])
    st.sidebar.metric("Revenue Today", f"${today_revenue:,.2f}")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔗 Quick Links")
st.sidebar.markdown("- [PROJ344 Dashboard](http://localhost:8501)")
st.sidebar.markdown("- [Timeline View](http://localhost:8502)")
st.sidebar.markdown("- [n8n Workflows](http://localhost:5678)")

# ============================================
# VIEW: EXECUTIVE OVERVIEW
# ============================================

if view == "📊 Executive Overview":
    render_header(
        "CEO Executive Overview",
        "Unified view of all life areas & priorities",
        "🎯"
    )

    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_metric_card(
            "Total Priorities",
            str(len(priorities)),
            f"{p1_count} P1 items",
            "critical" if p1_count > 0 else "medium"
        )

    with col2:
        if revenue_data:
            mtd_revenue = sum([r.get("amount", 0) for r in revenue_data])
            render_metric_card(
                "Revenue MTD",
                f"${mtd_revenue:,.0f}",
                "All companies",
                "high"
            )

    with col3:
        proj344_data = get_proj344_summary()
        render_metric_card(
            "Legal Items",
            str(proj344_data["active_priorities"]),
            f"{proj344_data['total_documents']} docs",
            "medium"
        )

    with col4:
        family_docs = get_family_documents()
        render_metric_card(
            "Daughter Memories",
            str(len(family_docs)),
            "Preserved",
            "high"
        )

    st.markdown("---")

    # Priority breakdown
    st.subheader("🎯 Priority Breakdown")

    if priorities:
        # Group by system and priority
        priority_df = pd.DataFrame(priorities)

        col1, col2 = st.columns(2)

        with col1:
            # By priority level
            priority_counts = priority_df.groupby("priority_level").size().reset_index(name="count")
            fig = px.pie(
                priority_counts,
                values="count",
                names="priority_level",
                title="By Priority Level",
                color="priority_level",
                color_discrete_map={"P1": "#dc2626", "P2": "#f59e0b", "P3": "#3b82f6", "P4": "#6b7280"}
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # By source system
            system_counts = priority_df.groupby("source_system").size().reset_index(name="count")
            fig = px.bar(
                system_counts,
                x="source_system",
                y="count",
                title="By System",
                color="source_system",
                color_discrete_map={"proj344": "#1e3a8a", "ceo": "#667eea"}
            )
            st.plotly_chart(fig, use_container_width=True)

        # Top priorities list
        st.markdown("### 🔥 Top Priorities Across All Areas")

        top_priorities = [p for p in priorities if p.get("priority_level") in ["P1", "P2"]][:10]

        for priority in top_priorities:
            priority_level = priority.get("priority_level", "P3")
            title = priority.get("title", "Untitled")
            category = priority.get("category", "general")
            source = priority.get("source_system", "unknown")
            due_date = priority.get("due_date")

            badge_class = {
                "P1": "p1-badge",
                "P2": "p2-badge",
                "P3": "p3-badge",
                "P4": "p4-badge"
            }.get(priority_level, "p4-badge")

            st.markdown(f"""
            <div class="life-area-card">
                <span class="priority-badge {badge_class}">{priority_level}</span>
                <strong>{title}</strong>
                <br>
                <small>📂 {category} | 🔹 {source.upper()} | 📅 {due_date if due_date else 'No deadline'}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No active priorities found. Create your first priority to get started!")

    st.markdown("---")

    # OKR Progress
    st.subheader("🎯 OKR Progress")

    okrs = get_ceo_okrs()
    if okrs:
        for okr in okrs[:5]:
            objective = okr.get("objective", "Untitled")
            progress = okr.get("progress_percentage", 0)
            category = okr.get("category", "general")

            st.markdown(f"**{objective}** ({category})")
            st.progress(progress / 100)
            st.caption(f"{progress}% complete")
    else:
        st.info("No active OKRs. Set your quarterly objectives to track progress.")

# ============================================
# VIEW: BUSINESS OPERATIONS
# ============================================

elif view == "💰 Business Operations":
    render_header(
        "Business Operations",
        "Revenue, contracts, team delegation & strategic projects",
        "💰"
    )

    # Revenue metrics
    st.subheader("💵 Revenue Tracking")

    if revenue_data:
        revenue_df = pd.DataFrame(revenue_data)
        revenue_df["logged_at"] = pd.to_datetime(revenue_df["logged_at"])
        revenue_df["date"] = revenue_df["logged_at"].dt.date

        # Daily revenue chart
        daily_revenue = revenue_df.groupby("date")["amount"].sum().reset_index()

        fig = px.line(
            daily_revenue,
            x="date",
            y="amount",
            title="Revenue Trend",
            labels={"amount": "Revenue ($)", "date": "Date"}
        )
        fig.update_traces(line_color="#10b981", line_width=3)
        st.plotly_chart(fig, use_container_width=True)

        # Revenue by company/source
        col1, col2 = st.columns(2)

        with col1:
            if "company" in revenue_df.columns:
                company_revenue = revenue_df.groupby("company")["amount"].sum().reset_index()
                fig = px.bar(
                    company_revenue,
                    x="company",
                    y="amount",
                    title="Revenue by Company",
                    color="company"
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if "category" in revenue_df.columns:
                category_revenue = revenue_df.groupby("category")["amount"].sum().reset_index()
                fig = px.pie(
                    category_revenue,
                    values="amount",
                    names="category",
                    title="Revenue by Category"
                )
                st.plotly_chart(fig, use_container_width=True)

        # Recent transactions
        st.markdown("### 📜 Recent Transactions")

        for _, row in revenue_df.head(10).iterrows():
            amount = row.get("amount", 0)
            source = row.get("source", "Unknown")
            company = row.get("company", "N/A")
            date = row.get("logged_at", "")

            st.markdown(f"""
            <div class="life-area-card">
                <strong>${amount:,.2f}</strong> - {source}
                <br>
                <small>🏢 {company} | 📅 {date}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No revenue data yet. Start logging revenue with `/revenue` command in Telegram!")
        st.markdown("""
        **Quick start:**
        ```
        /revenue 500 Lake Merritt parking
        /revenue 1200 Chow Bus integration payment
        ```
        """)

    st.markdown("---")

    # Business documents
    st.subheader("📄 Recent Business Documents")

    biz_docs = get_business_documents()
    if biz_docs:
        for doc in biz_docs[:10]:
            filename = doc.get("filename", "Untitled")
            doc_type = doc.get("document_type", "unknown")
            revenue_amount = doc.get("revenue_amount")
            strategic_importance = doc.get("strategic_importance", 500)

            importance_color = "high" if strategic_importance > 700 else "medium" if strategic_importance > 400 else "low"

            st.markdown(f"""
            <div class="life-area-card">
                <strong>{filename}</strong>
                <br>
                <small>📑 {doc_type} | ⭐ Importance: {strategic_importance}/1000</small>
                {f'<br><small>💰 ${revenue_amount:,.2f}</small>' if revenue_amount else ''}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No business documents yet. Upload invoices, contracts, and proposals to track them here.")

# ============================================
# VIEW: LEGAL MATTERS
# ============================================

elif view == "⚖️ Legal Matters":
    render_header(
        "Legal Matters",
        "PROJ344 summary & all legal priorities",
        "⚖️"
    )

    # PROJ344 Summary Card
    proj344_data = get_proj344_summary()

    st.markdown(f"""
    <div class="ceo-card">
        <h3>⚖️ PROJ344: D22-03244 Case Intelligence</h3>
        <p>Custody case tracking and fraud detection system</p>
        <br>
        <div style="display: flex; gap: 2rem;">
            <div>
                <h2>{proj344_data['active_priorities']}</h2>
                <p>Active Legal Priorities</p>
            </div>
            <div>
                <h2>{proj344_data['total_documents']}</h2>
                <p>Documents Analyzed</p>
            </div>
        </div>
        <br>
        <a href="http://localhost:8501" target="_blank" style="color: white; text-decoration: underline;">
            → Open Full PROJ344 Dashboard
        </a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Legal priorities
    st.subheader("📋 Active Legal Priorities")

    legal_priorities = [p for p in priorities if p.get("category") == "legal" or p.get("source_system") == "proj344"]

    if legal_priorities:
        for priority in legal_priorities:
            priority_level = priority.get("priority_level", "P3")
            title = priority.get("title", "Untitled")
            description = priority.get("description", "")
            due_date = priority.get("due_date")
            status = priority.get("status", "active")

            badge_class = {
                "P1": "p1-badge",
                "P2": "p2-badge",
                "P3": "p3-badge",
                "P4": "p4-badge"
            }.get(priority_level, "p4-badge")

            status_emoji = "🔥" if status == "active" else "⏳" if status == "in_progress" else "✅"

            st.markdown(f"""
            <div class="life-area-card">
                <span class="priority-badge {badge_class}">{priority_level}</span>
                {status_emoji} <strong>{title}</strong>
                <br>
                {f'<p style="margin-top: 0.5rem;">{description}</p>' if description else ''}
                <small>📅 Due: {due_date if due_date else 'No deadline'} | Status: {status}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No active legal priorities. System is working on PROJ344 case analysis.")

    st.markdown("---")

    # Quick actions
    st.subheader("⚡ Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔍 View Timeline"):
            st.markdown("[Open Timeline Dashboard](http://localhost:8502)")

    with col2:
        if st.button("📄 Recent Evidence"):
            st.markdown("[View PROJ344 Documents](http://localhost:8501)")

    with col3:
        if st.button("📊 Fraud Analysis"):
            st.markdown("[Contradiction Detection](http://localhost:8501)")

# ============================================
# VIEW: FAMILY & DAUGHTER
# ============================================

elif view == "👨‍👧 Family & Daughter":
    render_header(
        "Family & Daughter",
        "Ashé's memory journal, milestones & reunion progress",
        "👨‍👧"
    )

    family_docs = get_family_documents()

    # Summary metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        render_metric_card(
            "Total Memories",
            str(len(family_docs)),
            "Preserved for Ashé",
            "high"
        )

    with col2:
        milestones = [d for d in family_docs if d.get("milestone_type")]
        render_metric_card(
            "Milestones",
            str(len(milestones)),
            "Important moments",
            "high"
        )

    with col3:
        memory_book = [d for d in family_docs if d.get("memory_book_include")]
        render_metric_card(
            "Memory Book",
            str(len(memory_book)),
            "For when she's older",
            "high"
        )

    st.markdown("---")

    # Memory journal
    st.subheader("💖 Ashé's Memory Journal")

    if family_docs:
        for doc in family_docs:
            filename = doc.get("filename", "Memory")
            doc_type = doc.get("document_type", "memory")
            document_date = doc.get("document_date", "")
            milestone_type = doc.get("milestone_type")
            sentiment = doc.get("sentiment", "hopeful")
            summary = doc.get("summary", "")
            memory_book = doc.get("memory_book_include", False)

            sentiment_emoji = {
                "happy": "😊",
                "proud": "🌟",
                "hopeful": "🙏",
                "sad": "💙",
                "concerned": "🤔"
            }.get(sentiment, "💝")

            st.markdown(f"""
            <div class="daughter-memory">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4>{sentiment_emoji} {filename}</h4>
                    {f'<span style="background: #e74c3c; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.85rem;">Milestone: {milestone_type}</span>' if milestone_type else ''}
                </div>
                <p style="margin: 0.5rem 0;">{summary if summary else 'Precious memory captured'}</p>
                <div style="display: flex; gap: 1rem; font-size: 0.9rem;">
                    <span>📅 {document_date if document_date else 'Recent'}</span>
                    <span>📖 Type: {doc_type}</span>
                    {f'<span>📚 Memory Book ✓</span>' if memory_book else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("""
        💖 Start preserving memories of Ashé here.

        Upload photos, school reports, or write notes about special moments.
        These will be saved for when you're reunited.
        """)

    st.markdown("---")

    # Reunion progress (if we have priorities related to daughter)
    st.subheader("🎯 Reunion Progress")

    reunion_priorities = [p for p in priorities if p.get("category") == "family" or "daughter" in p.get("title", "").lower()]

    if reunion_priorities:
        for priority in reunion_priorities:
            title = priority.get("title", "")
            status = priority.get("status", "active")

            st.markdown(f"""
            <div class="okr-progress">
                <strong>{title}</strong>
                <br>
                <small>Status: {status}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="okr-progress">
            <strong>Legal Case Progress (PROJ344)</strong>
            <br>
            <small>Working towards custody case resolution</small>
            <br>
            <a href="http://localhost:8501">→ View full legal progress</a>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# VIEW: PERSONAL DEVELOPMENT
# ============================================

elif view == "🏃 Personal Development":
    render_header(
        "Personal Development",
        "Health tracking, goals, pomodoros & personal growth",
        "🏃"
    )

    st.subheader("🎯 Active Goals & OKRs")

    personal_okrs = [okr for okr in get_ceo_okrs() if okr.get("category") in ["personal", "health", "fitness"]]

    if personal_okrs:
        for okr in personal_okrs:
            objective = okr.get("objective", "Untitled")
            progress = okr.get("progress_percentage", 0)
            key_results = okr.get("key_results", [])
            due_date = okr.get("due_date")

            st.markdown(f"""
            <div class="okr-progress">
                <h4>{objective}</h4>
                <div style="background: #e2e8f0; border-radius: 8px; height: 20px; margin: 0.5rem 0;">
                    <div style="background: #10b981; width: {progress}%; height: 100%; border-radius: 8px; transition: width 0.3s;"></div>
                </div>
                <p>{progress}% complete</p>
                {f'<small>📅 Due: {due_date}</small>' if due_date else ''}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Set your personal development goals to track progress here.")
        st.markdown("""
        **Example goals:**
        - Complete 8 Pomodoros daily
        - Exercise 5x per week
        - Read 2 books per month
        - Meditation daily
        """)

    st.markdown("---")

    # Health tracking
    st.subheader("💪 Health & Wellness")

    st.info("Health tracking will be available after personal_documents table is populated with health data.")

    # Placeholder for future health metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Pomodoros This Week", "42", "+6")

    with col2:
        st.metric("Exercise Days", "5/7", "+1")

    with col3:
        st.metric("Sleep Average", "7.2 hrs", "+0.3")

# ============================================
# VIEW: TASK MANAGEMENT
# ============================================

elif view == "📋 Task Management":
    render_header(
        "Task Management",
        "All tasks across business, legal, personal & family",
        "📋"
    )

    # Filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        filter_priority = st.multiselect(
            "Priority Level",
            ["P1", "P2", "P3", "P4"],
            default=["P1", "P2"]
        )

    with col2:
        filter_category = st.multiselect(
            "Category",
            ["legal", "business", "personal", "family", "health"],
            default=None
        )

    with col3:
        filter_status = st.multiselect(
            "Status",
            ["active", "in_progress", "blocked", "completed"],
            default=["active", "in_progress"]
        )

    # Filter priorities
    filtered_priorities = priorities

    if filter_priority:
        filtered_priorities = [p for p in filtered_priorities if p.get("priority_level") in filter_priority]

    if filter_category:
        filtered_priorities = [p for p in filtered_priorities if p.get("category") in filter_category]

    if filter_status:
        filtered_priorities = [p for p in filtered_priorities if p.get("status") in filter_status]

    st.markdown(f"### 📊 {len(filtered_priorities)} Tasks")

    # Group by priority level
    for priority_level in ["P1", "P2", "P3", "P4"]:
        level_tasks = [p for p in filtered_priorities if p.get("priority_level") == priority_level]

        if level_tasks:
            with st.expander(f"{priority_level} Tasks ({len(level_tasks)})", expanded=(priority_level == "P1")):
                for task in level_tasks:
                    title = task.get("title", "Untitled")
                    description = task.get("description", "")
                    category = task.get("category", "general")
                    source = task.get("source_system", "ceo")
                    due_date = task.get("due_date")
                    status = task.get("status", "active")
                    assigned_to = task.get("assigned_to")

                    status_color = {
                        "active": "🔵",
                        "in_progress": "🟡",
                        "blocked": "🔴",
                        "completed": "✅"
                    }.get(status, "⚪")

                    st.markdown(f"""
                    <div class="life-area-card">
                        {status_color} <strong>{title}</strong>
                        {f'<p style="margin-top: 0.5rem;">{description}</p>' if description else ''}
                        <div style="display: flex; gap: 1rem; margin-top: 0.5rem; font-size: 0.9rem;">
                            <span>📂 {category}</span>
                            <span>🔹 {source.upper()}</span>
                            {f'<span>👤 {assigned_to}</span>' if assigned_to else ''}
                            {f'<span>📅 {due_date}</span>' if due_date else ''}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; padding: 2rem 0;">
    <p>CEO Global Dashboard | Powered by Claude Code</p>
    <p style="font-size: 0.875rem;">Managing empire • Being present with Ashé • Building the future</p>
</div>
""", unsafe_allow_html=True)
