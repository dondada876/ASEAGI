#!/usr/bin/env python3
"""
CEO Dashboard - File Organization Overview
No Supabase required - uses file_inventory.json
"""

import streamlit as st
import json
import pandas as pd
import plotly.express as px
from datetime import datetime
from collections import Counter
import os

# Page config
st.set_page_config(
    page_title="CEO Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    """Load file inventory"""
    inventory_path = os.path.expanduser("~/Downloads/file_inventory.json")
    with open(inventory_path, 'r') as f:
        data = json.load(f)
    return data

# Load data
try:
    data = load_data()
    files = data['files']
    stats = data['statistics']
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Header
st.title("📊 CEO Dashboard")
st.markdown(f"**File Organization Overview** | {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
st.markdown("---")

# Top metrics
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Files", f"{stats['total_files']:,}")

with col2:
    st.metric("Total Size", f"{stats['total_size_mb']:.1f} MB")

with col3:
    compliance_pct = (stats['naming_compliant'] / stats['total_files'] * 100) if stats['total_files'] > 0 else 0
    st.metric("Naming Compliance", f"{compliance_pct:.0f}%")

with col4:
    st.metric("Duplicates", stats['duplicate_groups'])

with col5:
    organized = sum(v for k, v in stats['by_para_category'].items() if k != 'Unorganized')
    organized_pct = (organized / stats['total_files'] * 100) if stats['total_files'] > 0 else 0
    st.metric("Organized", f"{organized_pct:.0f}%")

st.markdown("---")

# Two columns
col_left, col_right = st.columns(2)

with col_left:
    # Company distribution
    st.subheader("📁 Files by Company")
    company_data = pd.DataFrame(
        list(stats['by_company'].items()),
        columns=['Company', 'Files']
    ).sort_values('Files', ascending=False)

    fig = px.bar(company_data, x='Company', y='Files', color='Files',
                 color_continuous_scale='Blues', text='Files')
    fig.update_traces(textposition='outside')
    fig.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    # File types
    st.subheader("📄 File Types")
    type_data = pd.DataFrame(
        list(stats['by_file_type'].items()),
        columns=['Type', 'Count']
    ).sort_values('Count', ascending=False)

    fig2 = px.pie(type_data, names='Type', values='Count', hole=0.4)
    fig2.update_layout(height=350)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# PARA distribution
st.subheader("🗂️ PARA Organization")
para_data = pd.DataFrame(
    list(stats['by_para_category'].items()),
    columns=['Category', 'Files']
).sort_values('Files', ascending=False)

col1, col2 = st.columns([2, 1])

with col1:
    fig3 = px.bar(para_data, x='Category', y='Files', color='Files',
                  color_continuous_scale='Greens', text='Files')
    fig3.update_traces(textposition='outside')
    fig3.update_layout(showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.metric("Projects", stats['by_para_category'].get('Projects', 0))
    st.metric("Areas", stats['by_para_category'].get('Areas', 0))
    st.metric("Resources", stats['by_para_category'].get('Resources', 0))
    st.metric("Archive", stats['by_para_category'].get('Archive', 0))
    st.metric("⚠️ Unorganized", stats['by_para_category'].get('Unorganized', 0))

st.markdown("---")

# Action items
st.subheader("⚠️ Action Items")

col1, col2, col3 = st.columns(3)

# Calculate percentages for context
unorganized = stats['by_para_category'].get('Unorganized', 0)
naming_issue_pct = (stats['naming_issues'] / stats['total_files'] * 100) if stats['total_files'] > 0 else 0
unorganized_pct = (unorganized / stats['total_files'] * 100) if stats['total_files'] > 0 else 0

with col1:
    # Color-coded naming metric
    if naming_issue_pct > 50:
        st.metric("Naming Issues", stats['naming_issues'], delta=f"-{naming_issue_pct:.0f}%", delta_color="inverse")
    else:
        st.metric("Naming Issues", stats['naming_issues'])

    if stats['naming_issues'] > 0:
        if naming_issue_pct > 50:
            st.error(f"🔴 {stats['naming_issues']} files need YYYY-MM-DD-CH##.#-Description.ext format")
        elif naming_issue_pct > 20:
            st.warning(f"🟡 {stats['naming_issues']} files need proper format")
        else:
            st.info(f"🔵 {stats['naming_issues']} files to rename")

with col2:
    # Color-coded organization metric
    if unorganized_pct > 50:
        st.metric("Needs Organization", unorganized, delta=f"-{unorganized_pct:.0f}%", delta_color="inverse")
    else:
        st.metric("Needs Organization", unorganized)

    if unorganized > 0:
        if unorganized_pct > 50:
            st.error(f"🔴 {unorganized} files not in PARA folders")
        elif unorganized_pct > 20:
            st.warning(f"🟡 {unorganized} files need organization")
        else:
            st.info(f"🔵 {unorganized} files to organize")

with col3:
    # Color-coded duplicates metric
    st.metric("Duplicate Groups", stats['duplicate_groups'])
    if stats['duplicate_groups'] > 20:
        st.error(f"🔴 {stats['duplicate_groups']} duplicate groups - high priority")
    elif stats['duplicate_groups'] > 5:
        st.warning(f"🟡 Review {stats['duplicate_groups']} duplicate groups to save space")
    elif stats['duplicate_groups'] > 0:
        st.info(f"🔵 {stats['duplicate_groups']} minor duplicates to review")

st.markdown("---")

# Recent files
st.subheader("🕐 Recent Files (Last 10)")
recent = sorted(files, key=lambda x: x['modified_date'], reverse=True)[:10]
recent_df = pd.DataFrame([{
    'File': f['filename'][:50],
    'Company': f['company'],
    'Type': f['file_type'],
    'Size': f"{f['size_mb']:.1f} MB",
    'Modified': datetime.fromisoformat(f['modified_date']).strftime('%Y-%m-%d'),
    '✓': '✅' if f['naming_compliant'] else '❌'
} for f in recent])

st.dataframe(recent_df, use_container_width=True, hide_index=True)

st.markdown("---")

# Recommendations
st.subheader("💡 Priority Actions")

# Calculate percentages for better thresholds
naming_issue_pct = (stats['naming_issues'] / stats['total_files'] * 100) if stats['total_files'] > 0 else 0
unorganized_pct = (unorganized / stats['total_files'] * 100) if stats['total_files'] > 0 else 0

# Naming compliance status
if naming_issue_pct > 50:
    st.error(f"🔴 **Critical:** {stats['naming_issues']} files need renaming ({naming_issue_pct:.0f}% non-compliant)")
elif naming_issue_pct > 20:
    st.warning(f"🟡 **Action Needed:** {stats['naming_issues']} files to rename ({naming_issue_pct:.0f}% non-compliant)")
elif naming_issue_pct > 0:
    st.info(f"🔵 **Minor:** {stats['naming_issues']} files to rename ({naming_issue_pct:.0f}% non-compliant)")
else:
    st.success(f"✅ **Excellent:** All files follow naming convention")

# Organization status
if unorganized_pct > 50:
    st.error(f"🔴 **Critical:** {unorganized} files to organize ({unorganized_pct:.0f}% unorganized)")
elif unorganized_pct > 20:
    st.warning(f"🟡 **Action Needed:** {unorganized} files to move to PARA folders ({unorganized_pct:.0f}% unorganized)")
elif unorganized_pct > 0:
    st.info(f"🔵 **Minor:** {unorganized} files to organize ({unorganized_pct:.0f}% unorganized)")
else:
    st.success(f"✅ **Excellent:** All files organized in PARA structure")

# Duplicates status
if stats['duplicate_groups'] > 20:
    st.error(f"🔴 **High Priority:** {stats['duplicate_groups']} duplicate groups to review")
elif stats['duplicate_groups'] > 5:
    st.warning(f"🟡 **Action Needed:** {stats['duplicate_groups']} duplicate groups to review")
elif stats['duplicate_groups'] > 0:
    st.info(f"🔵 **Minor:** {stats['duplicate_groups']} duplicate groups to review")
else:
    st.success(f"✅ **Excellent:** No duplicate files detected")

st.markdown("---")
st.caption(f"Data from file_inventory.json | Last scan: {data['generated_at']}")
