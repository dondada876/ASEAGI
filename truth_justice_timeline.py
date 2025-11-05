#!/usr/bin/env python3
"""
Master Truth Timeline & Justice Score Dashboard
Comprehensive truth-scoring system tracking every statement, event, action, motion, and filing.
Answers: When, Where, How, Why, Who + What
Rolls up into Justice Score (Truth vs. Lies)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from supabase import create_client
import numpy as np

# ============================================================================
# CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Truth & Justice Timeline",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
# TRUTH SCORING FUNCTIONS
# ============================================================================

def calculate_truth_score(item_data):
    """
    Calculate truth score (0-100) for any timeline item
    100 = Completely True (verified)
    50 = Unverified / Unknown
    0 = Completely False (proven lie)
    """
    # Default base score
    score = 50  # Neutral until proven

    # Evidence of truth
    if item_data.get('has_supporting_evidence'):
        score += 25
    if item_data.get('verified_by_official_record'):
        score += 25
    if item_data.get('witness_corroboration'):
        score += 10
    if item_data.get('timestamp_verified'):
        score += 10

    # Evidence of falsehood
    if item_data.get('contradicted_by_evidence'):
        score -= 40
    if item_data.get('proven_false'):
        score = 0
    if item_data.get('inconsistent_statements'):
        score -= 20
    if item_data.get('missing_required_evidence'):
        score -= 15

    # Fraud/perjury indicators
    fraud_score = item_data.get('fraud_score', 0)
    if fraud_score > 70:
        score -= 30
    elif fraud_score > 50:
        score -= 15

    return max(0, min(100, score))

def calculate_justice_score(truth_scores):
    """
    Calculate overall Justice Score from all truth scores
    Weighted average emphasizing critical items
    """
    if not truth_scores:
        return 50  # Neutral

    weights = []
    scores = []

    for item in truth_scores:
        weight = 1.0

        # Weight critical items more heavily
        if item.get('importance') == 'CRITICAL':
            weight = 3.0
        elif item.get('importance') == 'HIGH':
            weight = 2.0

        # Weight court filings even more
        if item.get('category') in ['MOTION', 'FILING', 'DECLARATION']:
            weight *= 1.5

        weights.append(weight)
        scores.append(item.get('truth_score', 50))

    weighted_score = np.average(scores, weights=weights)
    return round(weighted_score, 1)

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data(ttl=300)
def load_master_timeline():
    """Load and score all timeline items"""
    timeline_items = []

    try:
        # 1. Court Events
        events = supabase.table('court_events').select('*').execute()
        for event in events.data:
            truth_data = {
                'has_supporting_evidence': bool(event.get('event_outcome')),
                'verified_by_official_record': True,  # Court events are official
                'timestamp_verified': True,
            }

            timeline_items.append({
                'id': f"EVENT-{event.get('id')}",
                'date': pd.to_datetime(event.get('event_date')),
                'category': 'COURT EVENT',
                'type': event.get('event_type', 'GENERAL'),
                'title': event.get('event_title', 'Untitled'),
                'description': event.get('event_description', ''),
                'when': event.get('event_date'),
                'where': event.get('court_location', 'Court'),
                'who': event.get('judge_name', 'Unknown'),
                'what': event.get('event_title'),
                'why': event.get('event_description', ''),
                'how': 'Court Proceeding',
                'truth_score': calculate_truth_score(truth_data),
                'importance': 'HIGH',
                'source': 'court_events'
            })

        # 2. Legal Documents (Filings, Motions, Declarations)
        docs = supabase.table('legal_documents').select('*').execute()
        for doc in docs.data:
            truth_data = {
                'fraud_score': doc.get('micro_number', 0),
                'has_supporting_evidence': doc.get('relevancy_number', 0) > 700,
            }

            timeline_items.append({
                'id': f"DOC-{doc.get('id')}",
                'date': pd.to_datetime(doc.get('created_at')),
                'category': 'FILING' if 'filing' in doc.get('document_type', '').lower() else 'DOCUMENT',
                'type': doc.get('document_type', 'Document'),
                'title': doc.get('original_filename', 'Unknown'),
                'description': f"Relevancy: {doc.get('relevancy_number')}, Micro: {doc.get('micro_number')}",
                'when': doc.get('created_at'),
                'where': 'Court Filing',
                'who': doc.get('party_author', 'Unknown'),
                'what': doc.get('original_filename'),
                'why': f"Case documentation - Relevancy {doc.get('relevancy_number')}",
                'how': 'Filed with court',
                'truth_score': calculate_truth_score(truth_data),
                'importance': 'CRITICAL' if doc.get('relevancy_number', 0) >= 800 else 'HIGH' if doc.get('relevancy_number', 0) >= 600 else 'MEDIUM',
                'source': 'legal_documents'
            })

        # 3. Violations (Lies, False Statements, Perjury)
        violations = supabase.table('legal_violations').select('*').execute()
        for viol in violations.data:
            truth_data = {
                'proven_false': True,  # Violations are proven falsehoods
                'contradicted_by_evidence': True,
            }

            timeline_items.append({
                'id': f"VIOL-{viol.get('id')}",
                'date': pd.to_datetime(viol.get('violation_date')),
                'category': 'VIOLATION',
                'type': viol.get('violation_category', 'Violation'),
                'title': viol.get('violation_title', 'Unnamed'),
                'description': viol.get('violation_description', ''),
                'when': viol.get('violation_date'),
                'where': viol.get('violation_location', 'Unknown'),
                'who': viol.get('perpetrator', 'Unknown'),
                'what': viol.get('violation_title'),
                'why': viol.get('violation_description'),
                'how': 'Proven false statement or action',
                'truth_score': 0,  # Violations are lies by definition
                'importance': 'CRITICAL' if viol.get('severity_score', 0) >= 80 else 'HIGH',
                'source': 'legal_violations'
            })

        # 4. Communications (Statements made)
        try:
            comms = supabase.table('communications_matrix').select('*').execute()
            for comm in comms.data:
                truth_data = {
                    'has_supporting_evidence': True,  # Communication is documented
                    'timestamp_verified': True,
                }

                timeline_items.append({
                    'id': f"COMM-{comm.get('id')}",
                    'date': pd.to_datetime(comm.get('communication_date')),
                    'category': 'STATEMENT',
                    'type': comm.get('communication_type', 'Communication'),
                    'title': comm.get('subject', 'Untitled'),
                    'description': comm.get('summary', ''),
                    'when': comm.get('communication_date'),
                    'where': comm.get('communication_method', 'Unknown'),
                    'who': f"{comm.get('sender')} → {comm.get('recipient')}",
                    'what': comm.get('subject'),
                    'why': comm.get('summary'),
                    'how': comm.get('communication_method'),
                    'truth_score': 75,  # Communications are generally factual records
                    'importance': 'MEDIUM',
                    'source': 'communications_matrix'
                })
        except:
            pass  # Table might not exist

    except Exception as e:
        st.error(f"Error loading timeline: {e}")

    return pd.DataFrame(timeline_items)

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

st.title("⚖️ Master Truth Timeline & Justice Score")
st.markdown("**Case:** In re Ashe B., J24-00478 | **Comprehensive Truth Analysis**")

# Load data
with st.spinner("📥 Loading Master Timeline..."):
    timeline_df = load_master_timeline()

if timeline_df.empty:
    st.warning("No timeline data found")
    st.stop()

# Sort by date
timeline_df = timeline_df.sort_values('date', ascending=False)

# ============================================================================
# JUSTICE SCORE - MAIN METRIC
# ============================================================================

st.markdown("---")
st.header("🎯 Justice Score: Truth vs. Lies")

col1, col2, col3, col4 = st.columns(4)

# Calculate overall justice score
justice_score = calculate_justice_score(timeline_df.to_dict('records'))

# Count truth vs lies
true_items = len(timeline_df[timeline_df['truth_score'] >= 75])
questionable_items = len(timeline_df[(timeline_df['truth_score'] >= 25) & (timeline_df['truth_score'] < 75)])
false_items = len(timeline_df[timeline_df['truth_score'] < 25])

with col1:
    st.metric(
        "⚖️ Justice Score",
        f"{justice_score}%",
        delta="Truth Weighted Average",
        help="Overall case justice score (100=all truth, 0=all lies)"
    )

with col2:
    st.metric(
        "✅ Truthful",
        true_items,
        delta=f"{true_items/len(timeline_df)*100:.1f}%",
        help="Items with truth score ≥75%"
    )

with col3:
    st.metric(
        "⚠️ Questionable",
        questionable_items,
        delta=f"{questionable_items/len(timeline_df)*100:.1f}%",
        help="Items with truth score 25-75%"
    )

with col4:
    st.metric(
        "❌ False",
        false_items,
        delta=f"{false_items/len(timeline_df)*100:.1f}%",
        delta_color="inverse",
        help="Items with truth score <25% (proven lies)"
    )

# Justice Score Gauge
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=justice_score,
    title={'text': "Justice Score", 'font': {'size': 24}},
    delta={'reference': 50, 'increasing': {'color': "green"}},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "darkblue"},
        'steps': [
            {'range': [0, 25], 'color': "red"},
            {'range': [25, 50], 'color': "orange"},
            {'range': [50, 75], 'color': "yellow"},
            {'range': [75, 100], 'color': "green"}
        ],
        'threshold': {
            'line': {'color': "black", 'width': 4},
            'thickness': 0.75,
            'value': 50
        }
    }
))

st.plotly_chart(fig_gauge, use_container_width=True)

# ============================================================================
# TRUTH DISTRIBUTION
# ============================================================================

st.markdown("---")
st.header("📊 Truth Distribution Analysis")

col_viz1, col_viz2 = st.columns(2)

with col_viz1:
    # Truth score distribution by category
    st.subheader("Truth Scores by Category")
    fig_box = px.box(
        timeline_df,
        x='category',
        y='truth_score',
        color='category',
        points='all',
        title='Truth Score Distribution'
    )
    fig_box.add_hline(y=50, line_dash="dash", line_color="gray", annotation_text="Neutral")
    st.plotly_chart(fig_box, use_container_width=True)

with col_viz2:
    # Truth vs Lies pie chart
    st.subheader("Truth vs Lies Breakdown")
    truth_breakdown = pd.DataFrame({
        'Status': ['Truthful (≥75%)', 'Questionable (25-75%)', 'False (<25%)'],
        'Count': [true_items, questionable_items, false_items],
        'Color': ['green', 'orange', 'red']
    })
    fig_pie = px.pie(
        truth_breakdown,
        values='Count',
        names='Status',
        title='Overall Truth Distribution',
        color='Status',
        color_discrete_map={
            'Truthful (≥75%)': 'green',
            'Questionable (25-75%)': 'orange',
            'False (<25%)': 'red'
        }
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ============================================================================
# TIMELINE VISUALIZATION
# ============================================================================

st.markdown("---")
st.header("📅 Master Truth Timeline")

# Map importance to numeric values for size parameter
importance_map = {'CRITICAL': 3, 'HIGH': 2, 'MEDIUM': 1, 'LOW': 0.5}
timeline_df['importance_size'] = timeline_df['importance'].map(importance_map).fillna(1)

# Timeline scatter plot
fig_timeline = px.scatter(
    timeline_df,
    x='date',
    y='truth_score',
    color='category',
    size='importance_size',
    size_max=20,
    hover_data=['title', 'who', 'type', 'importance'],
    title='Truth Timeline: Every Statement, Event & Action'
)
fig_timeline.add_hline(y=75, line_dash="dash", line_color="green", annotation_text="Truthful Threshold")
fig_timeline.add_hline(y=25, line_dash="dash", line_color="red", annotation_text="False Threshold")
fig_timeline.add_hline(y=50, line_dash="dot", line_color="gray", annotation_text="Neutral")

st.plotly_chart(fig_timeline, use_container_width=True)

# ============================================================================
# 5W+H ANALYSIS MATRIX
# ============================================================================

st.markdown("---")
st.header("🔍 5W+H Master Reference Matrix")
st.markdown("**Source of Truth**: Every item analyzed for When, Where, Who, What, Why, How")

# Filters
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    category_filter = st.multiselect(
        "Category",
        options=timeline_df['category'].unique(),
        default=timeline_df['category'].unique()
    )

with col_f2:
    truth_filter = st.select_slider(
        "Truth Score Range",
        options=[0, 25, 50, 75, 100],
        value=(0, 100)
    )

with col_f3:
    importance_filter = st.multiselect(
        "Importance",
        options=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
        default=['CRITICAL', 'HIGH']
    )

# Apply filters
filtered_df = timeline_df[
    (timeline_df['category'].isin(category_filter)) &
    (timeline_df['truth_score'] >= truth_filter[0]) &
    (timeline_df['truth_score'] <= truth_filter[1]) &
    (timeline_df['importance'].isin(importance_filter))
]

st.info(f"📊 Showing {len(filtered_df)} of {len(timeline_df)} timeline items")

# Display comprehensive matrix
st.dataframe(
    filtered_df[[
        'date', 'category', 'type', 'title',
        'when', 'where', 'who', 'what', 'why', 'how',
        'truth_score', 'importance'
    ]],
    use_container_width=True,
    height=600,
    column_config={
        'date': st.column_config.DatetimeColumn('Date', format='YYYY-MM-DD HH:mm'),
        'truth_score': st.column_config.NumberColumn(
            'Truth Score',
            format='%d%%',
            help='100=True, 0=False'
        )
    }
)

# ============================================================================
# LIES & FALSE STATEMENTS ANALYSIS
# ============================================================================

st.markdown("---")
st.header("🚨 Lies & False Statements (Truth Score <25%)")

lies_df = timeline_df[timeline_df['truth_score'] < 25].sort_values('date', ascending=False)

if not lies_df.empty:
    st.error(f"⚠️ Found {len(lies_df)} proven false statements or actions")

    for idx, lie in lies_df.iterrows():
        with st.expander(f"🔴 {lie['date'].strftime('%Y-%m-%d')}: {lie['title'][:60]}..."):
            col_lie1, col_lie2 = st.columns([2, 1])

            with col_lie1:
                st.markdown(f"**Category:** {lie['category']}")
                st.markdown(f"**Type:** {lie['type']}")
                st.markdown(f"**What:** {lie['what']}")
                st.markdown(f"**Who:** {lie['who']}")
                st.markdown(f"**When:** {lie['when']}")
                st.markdown(f"**Where:** {lie['where']}")
                st.markdown(f"**Why:** {lie['why']}")
                st.markdown(f"**How:** {lie['how']}")

            with col_lie2:
                st.metric("Truth Score", f"{lie['truth_score']}%", delta="PROVEN FALSE", delta_color="inverse")
                st.metric("Importance", lie['importance'])
                st.markdown(f"**Source:** {lie['source']}")
else:
    st.success("✅ No proven false statements found")

# ============================================================================
# EXPORT & REPORTING
# ============================================================================

st.markdown("---")
st.header("📥 Export Justice Report")

col_export1, col_export2 = st.columns(2)

with col_export1:
    if st.button("📄 Generate Justice Report"):
        report = f"""
JUSTICE SCORE REPORT
Case: In re Ashe B., J24-00478
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL JUSTICE SCORE: {justice_score}%

SUMMARY:
- Total Timeline Items: {len(timeline_df)}
- Truthful Items (≥75%): {true_items} ({true_items/len(timeline_df)*100:.1f}%)
- Questionable Items (25-75%): {questionable_items} ({questionable_items/len(timeline_df)*100:.1f}%)
- False Items (<25%): {false_items} ({false_items/len(timeline_df)*100:.1f}%)

PROVEN FALSE STATEMENTS:
"""
        for idx, lie in lies_df.iterrows():
            report += f"\n{lie['date'].strftime('%Y-%m-%d')} - {lie['title']}"
            report += f"\n  Who: {lie['who']}"
            report += f"\n  Truth Score: {lie['truth_score']}%\n"

        st.download_button(
            "⬇️ Download Report",
            data=report,
            file_name=f"justice_report_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

with col_export2:
    if st.button("📊 Export Timeline CSV"):
        csv = timeline_df.to_csv(index=False)
        st.download_button(
            "⬇️ Download CSV",
            data=csv,
            file_name=f"truth_timeline_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.caption(f"**Master Truth Timeline** | Data Sources: court_events, legal_documents, legal_violations, communications_matrix | Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
