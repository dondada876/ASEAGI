#!/usr/bin/env python3
"""
Enhanced Truth Score Dashboard
Comprehensive visualizations for truth scoring, justice analysis, and evidence tracking

Features:
- Truth score heatmaps
- Timeline trend analysis
- Actor comparison charts
- Police report integration
- 5W+H master matrix
- Justice score rollup
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import os
from supabase import create_client

# ============================================================================
# CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Enhanced Truth Score Dashboard",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .truth-metric-high { background-color: #d4edda; padding: 10px; border-radius: 5px; }
    .truth-metric-low { background-color: #f8d7da; padding: 10px; border-radius: 5px; }
    .truth-metric-medium { background-color: #fff3cd; padding: 10px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# Supabase connection
@st.cache_resource
def get_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except (KeyError, FileNotFoundError):
        url = os.environ.get('SUPABASE_URL', 'https://jvjlhxodmbkodzmggwpu.supabase.co')
        key = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2amxoeG9kbWJrb2R6bWdnd3B1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyMjMxOTAsImV4cCI6MjA3Nzc5OTE5MH0.ai65vVW816bNAV56XiuRxp5PE5IhBkMGPx3IbxfPh8c')
    return create_client(url, key)

supabase = get_supabase()

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

@st.cache_data(ttl=300)
def load_master_timeline():
    """Load master timeline with truth scores"""
    try:
        # Try to load from new master_absolute_timeline table first
        response = supabase.table('master_absolute_timeline').select('*').execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df['when_datetime'] = pd.to_datetime(df['when_datetime'])
            return df
    except:
        pass

    # Fallback: aggregate from existing tables
    return load_legacy_timeline()

def load_legacy_timeline():
    """Load timeline from legacy tables and create unified view"""
    timeline_items = []

    try:
        # 1. Court Events
        events = supabase.table('court_events').select('*').execute()
        for event in events.data:
            timeline_items.append({
                'entry_id': f"EVENT-{event.get('id')}",
                'entry_type': 'EVENT',
                'category': 'COURT_EVENT',
                'when_datetime': pd.to_datetime(event.get('event_date')),
                'where_location': event.get('court_location', 'Court'),
                'who_primary': event.get('judge_name', 'Court'),
                'what_title': event.get('event_title', 'Court Event'),
                'what_description': event.get('event_description', ''),
                'truth_score': 95,  # Court events are highly reliable
                'importance_level': 'HIGH',
                'verified_by_official_record': True,
                'fraud_score': 0
            })

        # 2. Legal Documents
        docs = supabase.table('legal_documents').select('*').execute()
        for doc in docs.data:
            fraud_score = doc.get('micro_number', 0)
            truth_score = max(0, min(100, 100 - fraud_score))  # Inverse of fraud

            timeline_items.append({
                'entry_id': f"DOC-{doc.get('id')}",
                'entry_type': 'FILING',
                'category': 'LEGAL_DOCUMENT',
                'when_datetime': pd.to_datetime(doc.get('created_at')),
                'where_location': 'Court Filing',
                'who_primary': doc.get('party_author', 'Unknown'),
                'what_title': doc.get('original_filename', 'Document'),
                'what_description': f"Relevancy: {doc.get('relevancy_number', 0)}",
                'truth_score': truth_score,
                'importance_level': 'CRITICAL' if doc.get('relevancy_number', 0) >= 800 else 'HIGH',
                'verified_by_official_record': True,
                'fraud_score': fraud_score
            })

        # 3. Violations (Lies)
        violations = supabase.table('legal_violations').select('*').execute()
        for viol in violations.data:
            timeline_items.append({
                'entry_id': f"VIOL-{viol.get('id')}",
                'entry_type': 'VIOLATION',
                'category': 'VIOLATION',
                'when_datetime': pd.to_datetime(viol.get('violation_date')),
                'where_location': viol.get('violation_location', 'Unknown'),
                'who_primary': viol.get('perpetrator', 'Unknown'),
                'what_title': viol.get('violation_title', 'Violation'),
                'what_description': viol.get('violation_description', ''),
                'truth_score': 0,  # Violations are proven false
                'importance_level': 'CRITICAL' if viol.get('severity_score', 0) >= 80 else 'HIGH',
                'verified_by_official_record': False,
                'fraud_score': 100
            })

    except Exception as e:
        st.error(f"Error loading data: {e}")

    return pd.DataFrame(timeline_items)

@st.cache_data(ttl=300)
def load_police_reports():
    """Load police reports if table exists"""
    try:
        response = supabase.table('police_reports').select('*').execute()
        if response.data:
            df = pd.DataFrame(response.data)
            if 'incident_date' in df.columns:
                df['incident_date'] = pd.to_datetime(df['incident_date'])
            return df
    except:
        return pd.DataFrame()

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def create_truth_heatmap(timeline_df):
    """Create heatmap showing truth scores over time by category"""

    # Group by date and category
    timeline_df['date_only'] = timeline_df['when_datetime'].dt.date
    timeline_df['month'] = timeline_df['when_datetime'].dt.to_period('M').astype(str)

    heatmap_data = timeline_df.pivot_table(
        values='truth_score',
        index='category',
        columns='month',
        aggfunc='mean'
    )

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale=[
            [0, 'red'],      # 0% = Red (lies)
            [0.25, 'orange'], # 25% = Orange
            [0.5, 'yellow'],  # 50% = Yellow (neutral)
            [0.75, 'lightgreen'], # 75% = Light Green
            [1, 'darkgreen']  # 100% = Dark Green (truth)
        ],
        text=heatmap_data.values,
        texttemplate='%{text:.0f}',
        textfont={"size": 10},
        colorbar=dict(title="Truth Score")
    ))

    fig.update_layout(
        title="Truth Score Heatmap: Category × Time",
        xaxis_title="Month",
        yaxis_title="Category",
        height=400
    )

    return fig

def create_truth_trend_chart(timeline_df):
    """Create trend line showing truth scores over time"""

    # Daily average truth scores
    daily_scores = timeline_df.groupby(
        timeline_df['when_datetime'].dt.date
    ).agg({
        'truth_score': 'mean',
        'entry_id': 'count'
    }).reset_index()
    daily_scores.columns = ['date', 'avg_truth_score', 'count']

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Truth score trend
    fig.add_trace(
        go.Scatter(
            x=daily_scores['date'],
            y=daily_scores['avg_truth_score'],
            name='Average Truth Score',
            mode='lines+markers',
            line=dict(color='blue', width=2),
            marker=dict(size=6)
        ),
        secondary_y=False
    )

    # Entry count bars
    fig.add_trace(
        go.Bar(
            x=daily_scores['date'],
            y=daily_scores['count'],
            name='Entries per Day',
            opacity=0.3,
            marker_color='gray'
        ),
        secondary_y=True
    )

    # Add threshold lines
    fig.add_hline(y=75, line_dash="dash", line_color="green", annotation_text="Truthful Threshold", secondary_y=False)
    fig.add_hline(y=25, line_dash="dash", line_color="red", annotation_text="False Threshold", secondary_y=False)

    fig.update_layout(
        title="Truth Score Trend Over Time",
        xaxis_title="Date",
        height=400
    )

    fig.update_yaxes(title_text="Truth Score (%)", secondary_y=False, range=[0, 100])
    fig.update_yaxes(title_text="Number of Entries", secondary_y=True)

    return fig

def create_actor_comparison_chart(timeline_df):
    """Compare truth scores by actor (who_primary)"""

    actor_stats = timeline_df.groupby('who_primary').agg({
        'truth_score': ['mean', 'count'],
        'fraud_score': 'mean'
    }).reset_index()

    actor_stats.columns = ['Actor', 'Avg_Truth', 'Count', 'Avg_Fraud']
    actor_stats = actor_stats[actor_stats['Count'] >= 2]  # At least 2 entries
    actor_stats = actor_stats.sort_values('Avg_Truth')

    fig = go.Figure()

    # Truth scores
    fig.add_trace(go.Bar(
        y=actor_stats['Actor'],
        x=actor_stats['Avg_Truth'],
        name='Truth Score',
        orientation='h',
        marker=dict(
            color=actor_stats['Avg_Truth'],
            colorscale=[
                [0, 'red'],
                [0.5, 'yellow'],
                [1, 'green']
            ],
            cmin=0,
            cmax=100
        ),
        text=actor_stats['Avg_Truth'].round(1),
        textposition='auto'
    ))

    fig.update_layout(
        title="Truth Score by Actor (Lowest to Highest)",
        xaxis_title="Average Truth Score",
        yaxis_title="Actor",
        height=max(400, len(actor_stats) * 25),
        showlegend=False
    )

    return fig

def create_5wh_matrix_view(timeline_df):
    """Display comprehensive 5W+H matrix"""

    # Select key columns
    display_cols = [
        'when_datetime', 'where_location', 'who_primary',
        'what_title', 'truth_score', 'importance_level', 'category'
    ]

    # Add "why" and "how" if they exist
    if 'why_stated_reason' in timeline_df.columns:
        display_cols.insert(5, 'why_stated_reason')
    if 'how_method' in timeline_df.columns:
        display_cols.insert(6, 'how_method')

    # Filter available columns
    available_cols = [col for col in display_cols if col in timeline_df.columns]

    matrix_df = timeline_df[available_cols].copy()
    matrix_df = matrix_df.sort_values('when_datetime', ascending=False)

    # Color code by truth score
    def highlight_truth(row):
        score = row['truth_score']
        if score >= 75:
            return ['background-color: #d4edda'] * len(row)
        elif score < 25:
            return ['background-color: #f8d7da'] * len(row)
        else:
            return ['background-color: #fff3cd'] * len(row)

    return matrix_df

def create_justice_score_gauge(timeline_df):
    """Create main justice score gauge"""

    # Calculate weighted justice score
    weights = []
    scores = []

    for _, row in timeline_df.iterrows():
        weight = 1.0
        if row['importance_level'] == 'CRITICAL':
            weight = 3.0
        elif row['importance_level'] == 'HIGH':
            weight = 2.0

        weights.append(weight)
        scores.append(row['truth_score'])

    justice_score = round(np.average(scores, weights=weights), 1)

    # Create gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=justice_score,
        title={'text': "⚖️ JUSTICE SCORE", 'font': {'size': 32}},
        delta={'reference': 50, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "black"},
            'bar': {'color': "darkblue", 'thickness': 0.75},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 25], 'color': '#ffcccc'},
                {'range': [25, 50], 'color': '#ffe6cc'},
                {'range': [50, 75], 'color': '#ffffcc'},
                {'range': [75, 100], 'color': '#ccffcc'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': justice_score
            }
        },
        number={'suffix': "%", 'font': {'size': 48}}
    ))

    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=80, b=20)
    )

    return fig, justice_score

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

# Header
st.title("⚖️ Enhanced Truth Score Dashboard")
st.markdown("**Comprehensive Truth Analysis with Justice Score Rollup**")
st.markdown("---")

# Load data
with st.spinner("📥 Loading timeline data..."):
    timeline_df = load_master_timeline()
    police_df = load_police_reports()

if timeline_df.empty:
    st.error("❌ No timeline data found. Please populate the database first.")
    st.stop()

# ============================================================================
# SECTION 1: JUSTICE SCORE - MAIN METRIC
# ============================================================================

st.header("🎯 Justice Score: Overall Case Truth Assessment")

col_gauge, col_stats = st.columns([1, 1])

with col_gauge:
    gauge_fig, justice_score = create_justice_score_gauge(timeline_df)
    st.plotly_chart(gauge_fig, use_container_width=True)

with col_stats:
    st.markdown("### 📊 Truth Distribution")

    true_count = len(timeline_df[timeline_df['truth_score'] >= 75])
    questionable_count = len(timeline_df[(timeline_df['truth_score'] >= 25) & (timeline_df['truth_score'] < 75)])
    false_count = len(timeline_df[timeline_df['truth_score'] < 25])
    total = len(timeline_df)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "✅ Truthful",
            true_count,
            delta=f"{true_count/total*100:.1f}%",
            help="Truth score ≥75%"
        )

    with col2:
        st.metric(
            "⚠️ Questionable",
            questionable_count,
            delta=f"{questionable_count/total*100:.1f}%",
            help="Truth score 25-75%"
        )

    with col3:
        st.metric(
            "❌ False",
            false_count,
            delta=f"{false_count/total*100:.1f}%",
            delta_color="inverse",
            help="Truth score <25% (proven lies)"
        )

    # Pie chart
    pie_data = pd.DataFrame({
        'Status': ['Truthful (≥75%)', 'Questionable (25-75%)', 'False (<25%)'],
        'Count': [true_count, questionable_count, false_count]
    })

    fig_pie = px.pie(
        pie_data,
        values='Count',
        names='Status',
        color='Status',
        color_discrete_map={
            'Truthful (≥75%)': 'green',
            'Questionable (25-75%)': 'orange',
            'False (<25%)': 'red'
        },
        hole=0.3
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# ============================================================================
# SECTION 2: TRUTH SCORE VISUALIZATIONS
# ============================================================================

st.header("📈 Truth Score Analysis & Trends")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Heatmap",
    "📉 Trends",
    "👥 By Actor",
    "📅 Timeline"
])

with tab1:
    st.subheader("Truth Score Heatmap: Category × Time")
    st.plotly_chart(create_truth_heatmap(timeline_df), use_container_width=True)
    st.info("**Interpretation:** Dark green = high truth (verified), Red = low truth (lies). Track patterns across categories and time.")

with tab2:
    st.subheader("Truth Score Trend Over Time")
    st.plotly_chart(create_truth_trend_chart(timeline_df), use_container_width=True)
    st.info("**Interpretation:** Blue line shows daily average truth score. Gray bars show activity volume. Watch for drops below 25% (false threshold).")

with tab3:
    st.subheader("Truth Score by Actor (Who)")
    st.plotly_chart(create_actor_comparison_chart(timeline_df), use_container_width=True)
    st.info("**Interpretation:** Compare credibility across actors. Red bars = frequent liars, Green bars = truthful actors.")

with tab4:
    st.subheader("Timeline Scatter: Truth Score × Time")

    fig_scatter = px.scatter(
        timeline_df,
        x='when_datetime',
        y='truth_score',
        color='category',
        size='importance_level',
        size_max=20,
        hover_data=['who_primary', 'what_title'],
        title='Complete Truth Timeline'
    )

    fig_scatter.add_hline(y=75, line_dash="dash", line_color="green", annotation_text="Truthful")
    fig_scatter.add_hline(y=25, line_dash="dash", line_color="red", annotation_text="False")

    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# ============================================================================
# SECTION 3: 5W+H MASTER MATRIX
# ============================================================================

st.header("🔍 5W+H Master Reference Matrix")
st.markdown("**Source of Truth:** When | Where | Who | What | Why | How + Truth Score")

# Filters
col_f1, col_f2, col_f3, col_f4 = st.columns(4)

with col_f1:
    categories = st.multiselect(
        "Category",
        options=timeline_df['category'].unique(),
        default=timeline_df['category'].unique()
    )

with col_f2:
    truth_range = st.slider(
        "Truth Score Range",
        0, 100, (0, 100)
    )

with col_f3:
    importance = st.multiselect(
        "Importance",
        options=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
        default=['CRITICAL', 'HIGH']
    )

with col_f4:
    entry_types = st.multiselect(
        "Entry Type",
        options=timeline_df['entry_type'].unique(),
        default=timeline_df['entry_type'].unique()
    )

# Filter data
filtered_df = timeline_df[
    (timeline_df['category'].isin(categories)) &
    (timeline_df['truth_score'] >= truth_range[0]) &
    (timeline_df['truth_score'] <= truth_range[1]) &
    (timeline_df['importance_level'].isin(importance)) &
    (timeline_df['entry_type'].isin(entry_types))
]

st.info(f"📊 Showing **{len(filtered_df)}** of {len(timeline_df)} entries")

# Display matrix
matrix_df = create_5wh_matrix_view(filtered_df)
st.dataframe(
    matrix_df,
    use_container_width=True,
    height=600,
    column_config={
        'when_datetime': st.column_config.DatetimeColumn('When', format='YYYY-MM-DD HH:mm'),
        'truth_score': st.column_config.NumberColumn(
            'Truth Score',
            format='%d%%',
            help='0=False, 100=True'
        ),
        'where_location': st.column_config.TextColumn('Where'),
        'who_primary': st.column_config.TextColumn('Who'),
        'what_title': st.column_config.TextColumn('What')
    }
)

st.markdown("---")

# ============================================================================
# SECTION 4: LIES & FALSE STATEMENTS
# ============================================================================

st.header("🚨 Proven Lies & False Statements")

lies_df = timeline_df[timeline_df['truth_score'] < 25].sort_values('when_datetime', ascending=False)

if not lies_df.empty:
    st.error(f"⚠️ **{len(lies_df)} proven false statements detected**")

    for idx, lie in lies_df.iterrows():
        with st.expander(f"🔴 {lie['when_datetime'].strftime('%Y-%m-%d')}: {lie['what_title'][:80]}"):
            col_l1, col_l2 = st.columns([3, 1])

            with col_l1:
                st.markdown(f"**Category:** {lie['category']}")
                st.markdown(f"**Who:** {lie['who_primary']}")
                st.markdown(f"**When:** {lie['when_datetime']}")
                st.markdown(f"**Where:** {lie['where_location']}")
                st.markdown(f"**What:** {lie['what_title']}")
                st.markdown(f"**Description:** {lie.get('what_description', 'N/A')}")

            with col_l2:
                st.metric("Truth Score", f"{lie['truth_score']}%", delta="PROVEN FALSE", delta_color="inverse")
                st.metric("Fraud Score", f"{lie.get('fraud_score', 0)}%")
                st.metric("Importance", lie['importance_level'])
else:
    st.success("✅ No proven false statements found")

st.markdown("---")

# ============================================================================
# SECTION 5: POLICE REPORTS (if available)
# ============================================================================

if not police_df.empty:
    st.header("🚔 Police Reports Integration")

    st.info(f"📁 **{len(police_df)} police reports** in database")

    col_pr1, col_pr2, col_pr3 = st.columns(3)

    with col_pr1:
        smoking_guns = len(police_df[police_df.get('is_smoking_gun', False) == True])
        st.metric("🔥 Smoking Guns", smoking_guns)

    with col_pr2:
        avg_truth = police_df['truth_score'].mean() if 'truth_score' in police_df.columns else 0
        st.metric("📊 Avg Truth Score", f"{avg_truth:.1f}%")

    with col_pr3:
        high_relevancy = len(police_df[police_df.get('relevancy_score', 0) >= 800])
        st.metric("⚡ High Relevancy", high_relevancy)

    # Display police reports
    st.dataframe(
        police_df[[
            'px_code', 'report_number', 'report_type', 'incident_date',
            'truth_score', 'relevancy_score', 'is_smoking_gun'
        ]] if all(col in police_df.columns for col in ['px_code', 'report_number']) else police_df,
        use_container_width=True
    )

st.markdown("---")

# ============================================================================
# SECTION 6: EXPORT & REPORTING
# ============================================================================

st.header("📥 Export Justice Report")

col_export1, col_export2, col_export3 = st.columns(3)

with col_export1:
    if st.button("📄 Generate Full Report"):
        report = f"""
═══════════════════════════════════════════════════════════════
                      JUSTICE SCORE REPORT
═══════════════════════════════════════════════════════════════
Case: In re Ashe B., J24-00478
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL JUSTICE SCORE: {justice_score}%
(Weighted average of all truth scores)

═══════════════════════════════════════════════════════════════
                        TRUTH SUMMARY
═══════════════════════════════════════════════════════════════
Total Timeline Entries: {len(timeline_df)}

✅ Truthful Items (≥75%):        {true_count} ({true_count/total*100:.1f}%)
⚠️  Questionable Items (25-75%):  {questionable_count} ({questionable_count/total*100:.1f}%)
❌ False Items (<25%):           {false_count} ({false_count/total*100:.1f}%)

═══════════════════════════════════════════════════════════════
                    PROVEN FALSE STATEMENTS
═══════════════════════════════════════════════════════════════
"""
        for idx, lie in lies_df.iterrows():
            report += f"""
Date: {lie['when_datetime'].strftime('%Y-%m-%d %H:%M')}
Who: {lie['who_primary']}
What: {lie['what_title']}
Truth Score: {lie['truth_score']}%
Fraud Score: {lie.get('fraud_score', 0)}%
─────────────────────────────────────────────────────────────────
"""

        report += f"""
═══════════════════════════════════════════════════════════════
                        END OF REPORT
═══════════════════════════════════════════════════════════════
"""

        st.download_button(
            "⬇️ Download Full Report",
            data=report,
            file_name=f"justice_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

with col_export2:
    if st.button("📊 Export Timeline CSV"):
        csv = timeline_df.to_csv(index=False)
        st.download_button(
            "⬇️ Download Timeline CSV",
            data=csv,
            file_name=f"timeline_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

with col_export3:
    if st.button("🚨 Export Lies Only"):
        lies_csv = lies_df.to_csv(index=False)
        st.download_button(
            "⬇️ Download Lies CSV",
            data=lies_csv,
            file_name=f"proven_lies_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.caption(f"""
**Enhanced Truth Score Dashboard** | ASEAGI System v2.0
Data Sources: master_absolute_timeline, police_reports, court_events, legal_documents, legal_violations
Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
""")
