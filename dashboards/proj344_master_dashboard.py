#!/usr/bin/env python3
"""
PROJ344 Master Dashboard V2
Updated for PROJ344 document scanning with micro/macro/legal/relevancy scoring
Displays: Document intelligence, smoking guns, perjury indicators, legal assessments
"""

import streamlit as st
import os
from datetime import datetime
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
    page_title="PROJ344 Master Dashboard",
    page_icon="⚖️",
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
# DATA QUERIES
# ============================================================================

@st.cache_data(ttl=30)
def get_all_documents(_client):
    """Get all documents"""
    try:
        response = _client.table('legal_documents').select('*').order('relevancy_number', desc=True).execute()
        return response.data
    except:
        return []

@st.cache_data(ttl=30)
def get_stats(_client):
    """Get comprehensive statistics"""
    docs = get_all_documents(_client)

    if not docs:
        return {
            'total': 0,
            'smoking_guns': 0,
            'critical': 0,
            'perjury': 0,
            'avg_relevancy': 0
        }

    stats = {
        'total': len(docs),
        'smoking_guns': len([d for d in docs if d.get('relevancy_number', 0) >= 900]),
        'critical': len([d for d in docs if d.get('importance') == 'CRITICAL']),
        'perjury': len([d for d in docs if d.get('contains_false_statements')]),
        'avg_relevancy': sum(d.get('relevancy_number', 0) for d in docs) / len(docs),
        'avg_legal': sum(d.get('legal_number', 0) for d in docs) / len(docs),
        'total_cost': sum(d.get('api_cost_usd', 0) for d in docs),
        'by_type': Counter(d.get('document_type') for d in docs),
        'by_importance': Counter(d.get('importance') for d in docs),
        'by_purpose': Counter(d.get('purpose') for d in docs),
    }

    return stats

# ============================================================================
# VISUALIZATIONS
# ============================================================================

def render_score_gauge(score, title, max_score=999):
    """Render a gauge chart for PROJ344 scores"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 16}},
        gauge = {
            'axis': {'range': [None, max_score], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 600], 'color': 'lightgray'},
                {'range': [600, 800], 'color': 'lightyellow'},
                {'range': [800, 900], 'color': 'lightgreen'},
                {'range': [900, max_score], 'color': 'lightcoral'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 900
            }
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def render_document_card(doc):
    """Render a document info card"""
    rel = doc.get('relevancy_number', 0)
    legal = doc.get('legal_number', 0)

    # Color code by relevancy
    if rel >= 900:
        border_color = "red"
        badge = "🔥 SMOKING GUN"
    elif rel >= 800:
        border_color = "orange"
        badge = "⚠️ CRITICAL"
    elif rel >= 700:
        border_color = "yellow"
        badge = "📌 IMPORTANT"
    else:
        border_color = "gray"
        badge = "📄 REFERENCE"

    st.markdown(f"""
    <div style="border: 3px solid {border_color}; padding: 15px; border-radius: 10px; margin: 10px 0;">
        <h4 style="margin:0;">{badge} {doc.get('document_title', 'Untitled')}</h4>
        <p style="margin:5px 0;"><b>Type:</b> {doc.get('document_type', 'N/A')} | <b>Date:</b> {doc.get('document_date', 'N/A')}</p>
        <p style="margin:5px 0;"><b>File:</b> {doc.get('original_filename', 'N/A')}</p>
        <hr style="margin:10px 0;">
        <p><b>Relevancy:</b> {rel}/999 | <b>Legal:</b> {legal}/999 | <b>Micro:</b> {doc.get('micro_number', 0)}/999 | <b>Macro:</b> {doc.get('macro_number', 0)}/999</p>
        <p><b>Summary:</b> {doc.get('executive_summary', 'No summary available')}</p>
    </div>
    """, unsafe_allow_html=True)

    # Expandable details
    with st.expander("📋 Full Details"):
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Importance:**", doc.get('importance', 'N/A'))
            st.write("**Purpose:**", doc.get('purpose', 'N/A'))
            st.write("**Status:**", doc.get('status', 'N/A'))

            if doc.get('keywords'):
                st.write("**Keywords:**", ", ".join(doc['keywords']))

        with col2:
            st.write("**W&I 388 Relevance:**", f"{doc.get('w388_relevance', 0)}/100")
            st.write("**CCP 473 Relevance:**", f"{doc.get('ccp473_relevance', 0)}/100")
            st.write("**Criminal Relevance:**", f"{doc.get('criminal_relevance', 0)}/100")
            st.write("**False Statements:**", "✅ Yes" if doc.get('contains_false_statements') else "❌ No")

        if doc.get('smoking_guns'):
            st.markdown("**🔥 Smoking Guns:**")
            for sg in doc['smoking_guns']:
                st.markdown(f"- {sg}")

        if doc.get('key_quotes'):
            st.markdown("**💬 Key Quotes:**")
            for quote in doc['key_quotes'][:5]:
                st.markdown(f"> {quote}")

        if doc.get('perjury_indicators'):
            st.markdown("**⚠️ Perjury Indicators:**")
            for pi in doc['perjury_indicators']:
                st.markdown(f"- {pi}")

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

def main():
    # Initialize
    client, error = init_supabase()

    if error or not client:
        st.error(f"❌ Supabase connection failed: {error}")
        st.info("💡 Set environment variables: SUPABASE_URL, SUPABASE_KEY")
        st.stop()

    # Header
    st.title("⚖️ PROJ344: Legal Case Intelligence Dashboard")
    st.markdown(f"**Case:** In re Ashe B., J24-00478 | **Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Get data
    stats = get_stats(client)
    docs = get_all_documents(client)

    # Sidebar
    st.sidebar.title("📊 Navigation")
    page = st.sidebar.radio("Select View", [
        "🏠 Overview",
        "🔥 Smoking Guns",
        "⚠️ Perjury Indicators",
        "📊 Document Intelligence",
        "🔍 Search & Filter",
        "📈 Statistics & Analytics"
    ])

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Total Documents:** {stats['total']}")
    st.sidebar.markdown(f"**Smoking Guns:** {stats['smoking_guns']}")
    st.sidebar.markdown(f"**Perjury Docs:** {stats['perjury']}")
    st.sidebar.markdown(f"**Total API Cost:** ${stats['total_cost']:.2f}")

    # ========================================================================
    # PAGE: OVERVIEW
    # ========================================================================
    if page == "🏠 Overview":
        st.header("System Overview")

        # Key metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("📄 Total Documents", stats['total'])
        col2.metric("🔥 Smoking Guns", stats['smoking_guns'])
        col3.metric("⚠️ Critical", stats['critical'])
        col4.metric("🚨 Perjury", stats['perjury'])
        col5.metric("💰 API Cost", f"${stats['total_cost']:.2f}")

        st.markdown("---")

        # Average scores
        st.subheader("📊 Average PROJ344 Scores")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.plotly_chart(render_score_gauge(stats['avg_relevancy'], "Relevancy"), use_container_width=True)
        with col2:
            st.plotly_chart(render_score_gauge(stats['avg_legal'], "Legal Weight"), use_container_width=True)
        with col3:
            # Calculate average micro/macro
            avg_micro = sum(d.get('micro_number', 0) for d in docs) / len(docs) if docs else 0
            st.plotly_chart(render_score_gauge(avg_micro, "Micro"), use_container_width=True)
        with col4:
            avg_macro = sum(d.get('macro_number', 0) for d in docs) / len(docs) if docs else 0
            st.plotly_chart(render_score_gauge(avg_macro, "Macro"), use_container_width=True)

        st.markdown("---")

        # Distribution charts
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("By Document Type")
            if stats['by_type']:
                df = pd.DataFrame(list(stats['by_type'].items()), columns=['Type', 'Count'])
                fig = px.pie(df, names='Type', values='Count', hole=0.4)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("By Importance")
            if stats['by_importance']:
                df = pd.DataFrame(list(stats['by_importance'].items()), columns=['Importance', 'Count'])
                fig = px.bar(df, x='Importance', y='Count', color='Importance')
                st.plotly_chart(fig, use_container_width=True)

        with col3:
            st.subheader("Relevancy Distribution")
            if docs:
                relevancy_scores = [d.get('relevancy_number', 0) for d in docs]
                fig = go.Figure(data=[go.Histogram(x=relevancy_scores, nbinsx=20)])
                fig.update_layout(xaxis_title="Relevancy Score", yaxis_title="Count")
                st.plotly_chart(fig, use_container_width=True)

    # ========================================================================
    # PAGE: SMOKING GUNS
    # ========================================================================
    elif page == "🔥 Smoking Guns":
        st.header("🔥 Smoking Gun Documents (Relevancy 900+)")

        smoking_guns = [d for d in docs if d.get('relevancy_number', 0) >= 900]

        if not smoking_guns:
            st.info("No smoking gun documents found yet. Run the scanner to analyze documents.")
        else:
            st.success(f"Found {len(smoking_guns)} smoking gun documents!")

            for doc in smoking_guns:
                render_document_card(doc)

    # ========================================================================
    # PAGE: PERJURY INDICATORS
    # ========================================================================
    elif page == "⚠️ Perjury Indicators":
        st.header("⚠️ Documents with Perjury Indicators")

        perjury_docs = [d for d in docs if d.get('contains_false_statements')]

        if not perjury_docs:
            st.info("No perjury indicators found yet.")
        else:
            st.warning(f"Found {len(perjury_docs)} documents with perjury indicators!")

            for doc in perjury_docs:
                render_document_card(doc)

    # ========================================================================
    # PAGE: DOCUMENT INTELLIGENCE
    # ========================================================================
    elif page == "📊 Document Intelligence":
        st.header("📊 All Documents Ranked by Relevancy")

        if not docs:
            st.info("No documents scanned yet. Run the batch scanner.")
        else:
            # Filters
            col1, col2, col3 = st.columns(3)

            with col1:
                min_relevancy = st.slider("Min Relevancy", 0, 999, 0)
            with col2:
                doc_types = ["ALL"] + list(stats['by_type'].keys())
                selected_type = st.selectbox("Document Type", doc_types)
            with col3:
                importance_levels = ["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"]
                selected_importance = st.selectbox("Importance", importance_levels)

            # Apply filters
            filtered = docs

            if min_relevancy > 0:
                filtered = [d for d in filtered if d.get('relevancy_number', 0) >= min_relevancy]

            if selected_type != "ALL":
                filtered = [d for d in filtered if d.get('document_type') == selected_type]

            if selected_importance != "ALL":
                filtered = [d for d in filtered if d.get('importance') == selected_importance]

            st.markdown(f"**Showing {len(filtered)} of {len(docs)} documents**")

            for doc in filtered:
                render_document_card(doc)

    # ========================================================================
    # PAGE: SEARCH & FILTER
    # ========================================================================
    elif page == "🔍 Search & Filter":
        st.header("🔍 Search Documents")

        search_term = st.text_input("Search by title, keywords, or summary:")

        if search_term:
            results = [d for d in docs if
                search_term.lower() in str(d.get('document_title', '')).lower() or
                search_term.lower() in str(d.get('executive_summary', '')).lower() or
                search_term.lower() in ' '.join(d.get('keywords', [])).lower()
            ]

            st.markdown(f"**Found {len(results)} documents matching '{search_term}'**")

            for doc in results:
                render_document_card(doc)
        else:
            st.info("Enter a search term above")

    # ========================================================================
    # PAGE: STATISTICS
    # ========================================================================
    elif page == "📈 Statistics & Analytics":
        st.header("📈 System Statistics & Analytics")

        if not docs:
            st.info("No data yet. Run the scanner first.")
            return

        # Score distributions
        st.subheader("Score Distributions")

        col1, col2 = st.columns(2)

        with col1:
            # Relevancy vs Legal scatter
            df_scores = pd.DataFrame([{
                'Relevancy': d.get('relevancy_number', 0),
                'Legal': d.get('legal_number', 0),
                'Title': d.get('document_title', 'Untitled')
            } for d in docs])

            fig = px.scatter(df_scores, x='Relevancy', y='Legal', hover_data=['Title'],
                            title="Relevancy vs Legal Weight")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Micro vs Macro scatter
            df_scores2 = pd.DataFrame([{
                'Micro': d.get('micro_number', 0),
                'Macro': d.get('macro_number', 0),
                'Title': d.get('document_title', 'Untitled')
            } for d in docs])

            fig = px.scatter(df_scores2, x='Micro', y='Macro', hover_data=['Title'],
                            title="Micro vs Macro Scores")
            st.plotly_chart(fig, use_container_width=True)

        # Top documents by each score
        st.subheader("Top 10 Documents by Score")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("**By Relevancy**")
            top_rel = sorted(docs, key=lambda x: x.get('relevancy_number', 0), reverse=True)[:10]
            for doc in top_rel:
                st.markdown(f"{doc.get('relevancy_number', 0)} - {doc.get('document_title', 'Untitled')[:40]}...")

        with col2:
            st.markdown("**By Legal**")
            top_legal = sorted(docs, key=lambda x: x.get('legal_number', 0), reverse=True)[:10]
            for doc in top_legal:
                st.markdown(f"{doc.get('legal_number', 0)} - {doc.get('document_title', 'Untitled')[:40]}...")

        with col3:
            st.markdown("**By Micro**")
            top_micro = sorted(docs, key=lambda x: x.get('micro_number', 0), reverse=True)[:10]
            for doc in top_micro:
                st.markdown(f"{doc.get('micro_number', 0)} - {doc.get('document_title', 'Untitled')[:40]}...")

        with col4:
            st.markdown("**By Macro**")
            top_macro = sorted(docs, key=lambda x: x.get('macro_number', 0), reverse=True)[:10]
            for doc in top_macro:
                st.markdown(f"{doc.get('macro_number', 0)} - {doc.get('document_title', 'Untitled')[:40]}...")

if __name__ == "__main__":
    main()
