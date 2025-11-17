#!/usr/bin/env python3
"""
Criminal Complaint Dashboard
============================

Real-time analysis of evidence supporting criminal perjury complaint.
Maps all 601+ documents to specific false statements.

Run:
    streamlit run dashboards/criminal_complaint_dashboard.py --server.port 8506
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
import sys
from pathlib import Path

from supabase import create_client

# Import schema from same directory
from schema import (
    PERJURY_COMPLAINT_2025,
    CorrelationScoring
)

# Page config
st.set_page_config(
    page_title="Criminal Complaint Evidence Dashboard",
    page_icon="⚖️",
    layout="wide"
)

# Initialize Supabase
@st.cache_resource
def init_supabase():
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    if not url or not key:
        st.error("Missing SUPABASE_URL or SUPABASE_KEY environment variables")
        st.stop()
    return create_client(url, key)

supabase = init_supabase()

# Load documents
@st.cache_data(ttl=300)
def load_all_documents():
    """Load all legal documents"""
    try:
        result = supabase.table('legal_documents')\
            .select('*')\
            .eq('case_id', 'ashe-bucknor-j24-00478')\
            .execute()
        return result.data
    except Exception as e:
        st.error(f"Error loading documents: {e}")
        return []

# Analysis functions
def calculate_date_relevance(doc_date: str, claim_date_range: list) -> int:
    """Calculate date relevance score"""
    if not doc_date:
        return 0
    try:
        doc_dt = datetime.fromisoformat(doc_date.split('T')[0])
        start_dt = datetime.fromisoformat(claim_date_range[0])
        end_dt = datetime.fromisoformat(claim_date_range[1])
        if start_dt <= doc_dt <= end_dt:
            return 100
        elif doc_dt < start_dt:
            days_before = (start_dt - doc_dt).days
            return max(0, 100 - days_before)
        else:
            days_after = (doc_dt - end_dt).days
            return max(0, 100 - days_after)
    except:
        return 0

def search_keywords(doc: dict, keywords: list) -> int:
    """Count keyword matches"""
    matches = 0
    search_fields = [
        doc.get('summary', ''),
        str(doc.get('key_quotes', [])),
        doc.get('executive_summary', ''),
        doc.get('file_name', ''),
    ]
    search_text = ' '.join(search_fields).lower()
    for keyword in keywords:
        if keyword.lower() in search_text:
            matches += 1
    return matches

def analyze_claim(claim: dict, all_documents: list) -> dict:
    """Analyze a single claim against all documents"""
    supporting_docs = []

    for doc in all_documents:
        keyword_matches = search_keywords(doc, claim['search_keywords'])
        date_relevance = calculate_date_relevance(doc.get('document_date'), claim['date_range'])
        expected_type = claim['expected_evidence_type']
        doc_type = doc.get('document_type', '')
        type_match = (doc_type == expected_type) if expected_type else True

        contradiction_score = CorrelationScoring.calculate_contradiction_score(
            document_relevancy=doc.get('relevancy_number', 0),
            keyword_matches=keyword_matches,
            date_relevance=date_relevance,
            document_type_match=type_match
        )

        if contradiction_score >= 400 or keyword_matches >= 2:
            supporting_docs.append({
                'document_id': doc['id'],
                'file_name': doc.get('file_name', doc.get('original_filename', 'Unknown')),
                'document_type': doc_type,
                'document_date': doc.get('document_date'),
                'relevancy_number': doc.get('relevancy_number', 0),
                'contradiction_score': contradiction_score,
                'keyword_matches': keyword_matches,
                'date_relevance': date_relevance,
                'key_quotes': doc.get('key_quotes', [])[:3],
                'summary': doc.get('summary', '')[:200],
            })

    supporting_docs.sort(key=lambda x: x['contradiction_score'], reverse=True)

    return {
        'claim': claim,
        'supporting_documents': supporting_docs,
        'total_documents': len(supporting_docs),
        'avg_contradiction_score': sum(d['contradiction_score'] for d in supporting_docs) / len(supporting_docs) if supporting_docs else 0,
        'smoking_guns': [d for d in supporting_docs if d['contradiction_score'] >= 900],
        'critical_evidence': [d for d in supporting_docs if d['contradiction_score'] >= 800],
    }

# Main dashboard
def main():
    # Header
    st.title("⚖️ Criminal Complaint Evidence Dashboard")
    st.markdown(f"**Case:** {PERJURY_COMPLAINT_2025['case_reference']} | **Subject:** {PERJURY_COMPLAINT_2025['subject_name']}")

    # Load data
    with st.spinner("Loading documents..."):
        all_documents = load_all_documents()

    if not all_documents:
        st.error("No documents found")
        st.stop()

    # Analyze all claims
    results = {}
    for claim in PERJURY_COMPLAINT_2025['false_statements']:
        results[claim['id']] = analyze_claim(claim, all_documents)

    # Calculate overall metrics
    total_docs = sum(r['total_documents'] for r in results.values())
    avg_contradiction = sum(r['avg_contradiction_score'] for r in results.values()) / len(results) if results else 0
    direct_contradictions = sum(len(r['smoking_guns']) for r in results.values())

    prosecutability = CorrelationScoring.calculate_prosecutability_score(
        total_documents=total_docs,
        avg_contradiction=int(avg_contradiction),
        direct_contradictions=direct_contradictions,
        witness_statements=0
    )

    # Metrics row
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Documents", f"{len(all_documents):,}")

    with col2:
        st.metric("Supporting Evidence", f"{total_docs:,}")

    with col3:
        st.metric("Smoking Guns (≥900)", direct_contradictions)

    with col4:
        st.metric("Avg Contradiction", f"{avg_contradiction:.0f}/999")

    with col5:
        if prosecutability >= 80:
            st.metric("Prosecutability", f"{prosecutability}/100", delta="STRONG", delta_color="normal")
        elif prosecutability >= 60:
            st.metric("Prosecutability", f"{prosecutability}/100", delta="MODERATE", delta_color="normal")
        else:
            st.metric("Prosecutability", f"{prosecutability}/100", delta="WEAK", delta_color="inverse")

    st.markdown("---")

    # Claim selection
    st.subheader("📋 False Statements Analysis")

    claim_options = {
        f"{claim['id']}: {claim['claim_type']}": claim['id']
        for claim in PERJURY_COMPLAINT_2025['false_statements']
    }

    selected_claim_label = st.selectbox("Select False Statement to Analyze:", list(claim_options.keys()))
    selected_claim_id = claim_options[selected_claim_label]

    # Display selected claim analysis
    result = results[selected_claim_id]
    claim = result['claim']

    st.markdown(f"### {claim['claim_type']}")
    st.markdown(f"**Declaration Date:** {claim['declaration_date']}")
    st.markdown(f"**Penal Code:** {', '.join(claim['penal_code'])}")
    st.markdown(f"**Evidence Weight:** {claim['evidence_weight']}/100")

    with st.expander("📜 False Statement Under Oath", expanded=True):
        st.markdown(f"> {claim['claim_text']}")

    # Evidence metrics for this claim
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Supporting Docs", result['total_documents'])

    with col2:
        st.metric("Smoking Guns", len(result['smoking_guns']))

    with col3:
        st.metric("Critical Evidence", len(result['critical_evidence']))

    with col4:
        st.metric("Avg Score", f"{result['avg_contradiction_score']:.0f}")

    # Score distribution chart
    if result['supporting_documents']:
        st.subheader("📊 Evidence Score Distribution")

        scores = [doc['contradiction_score'] for doc in result['supporting_documents']]
        fig = go.Figure()

        fig.add_trace(go.Histogram(
            x=scores,
            nbinsx=20,
            marker_color='#1f77b4',
            name='Contradiction Scores'
        ))

        fig.update_layout(
            xaxis_title="Contradiction Score",
            yaxis_title="Number of Documents",
            height=300,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

        # Top supporting documents
        st.subheader("🔥 Top Supporting Documents")

        for i, doc in enumerate(result['supporting_documents'][:20], 1):
            score_badge = "🔥" if doc['contradiction_score'] >= 900 else "⚠️" if doc['contradiction_score'] >= 800 else "📌"

            with st.expander(f"{i}. {score_badge} {doc['file_name']} - Score: {doc['contradiction_score']}/999"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown(f"**Type:** {doc['document_type']}")
                    st.markdown(f"**Date:** {doc['document_date'] or 'Unknown'}")

                with col2:
                    st.markdown(f"**Relevancy:** {doc['relevancy_number']}/999")
                    st.markdown(f"**Keywords:** {doc['keyword_matches']} matches")

                with col3:
                    st.markdown(f"**Date Relevance:** {doc['date_relevance']}/100")
                    st.markdown(f"**Contradiction:** {doc['contradiction_score']}/999")

                if doc['summary']:
                    st.markdown(f"**Summary:** {doc['summary']}")

                if doc['key_quotes']:
                    st.markdown("**Key Quotes:**")
                    for quote in doc['key_quotes']:
                        st.markdown(f"- \"{quote}\"")

    # All claims summary
    st.markdown("---")
    st.subheader("📊 All Claims Summary")

    summary_data = []
    for claim_id, result in results.items():
        claim = result['claim']
        summary_data.append({
            'Claim ID': claim['id'],
            'Claim Type': claim['claim_type'],
            'Supporting Docs': result['total_documents'],
            'Smoking Guns': len(result['smoking_guns']),
            'Critical Evidence': len(result['critical_evidence']),
            'Avg Score': f"{result['avg_contradiction_score']:.0f}",
        })

    df = pd.DataFrame(summary_data)
    st.dataframe(df, use_container_width=True)

    # Export options
    st.markdown("---")
    st.subheader("📥 Export Options")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📄 Generate Master Report"):
            st.info("Run: `python3 scanners/criminal_complaint_analyzer.py --export-report MASTER_PERJURY_REPORT.md`")

    with col2:
        if st.button("💾 Export JSON Analysis"):
            st.info("Run: `python3 scanners/criminal_complaint_analyzer.py --export-json criminal_complaint_analysis.json`")

if __name__ == "__main__":
    main()
