#!/usr/bin/env python3
"""
Legal Document Intelligence Dashboard
View and analyze documents with micro/macro/legal/category/relevancy scoring
"""

import streamlit as st
import os
from datetime import datetime
import pandas as pd
from collections import Counter

try:
    from supabase import create_client
except ImportError:
    st.error("❌ Supabase library not installed. Run: pip3 install supabase")
    st.stop()

st.set_page_config(
    page_title="Legal Document Intelligence Dashboard",
    page_icon="⚖️",
    layout="wide"
)

# ===== SUPABASE CONNECTION =====

@st.cache_resource
def init_supabase():
    """Initialize Supabase client"""
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')

    if not url or not key:
        return None, "Missing SUPABASE_URL or SUPABASE_KEY"

    try:
        client = create_client(url, key)
        # Test connection
        client.table('legal_documents').select('id', count='exact').limit(1).execute()
        return client, None
    except Exception as e:
        return None, str(e)

# ===== DATA QUERIES =====

@st.cache_data(ttl=30)
def get_all_documents(_client):
    """Get all legal documents with scores"""
    try:
        response = _client.table('legal_documents')\
            .select('*')\
            .order('relevancy_number', desc=True)\
            .execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching documents: {e}")
        return []

@st.cache_data(ttl=30)
def get_statistics(_client):
    """Get system statistics"""
    try:
        docs = get_all_documents(_client)

        if not docs:
            return None

        stats = {
            'total_documents': len(docs),
            'avg_relevancy': sum(d.get('relevancy_number', 0) for d in docs) / len(docs) if docs else 0,
            'avg_micro': sum(d.get('micro_number', 0) for d in docs) / len(docs) if docs else 0,
            'avg_macro': sum(d.get('macro_number', 0) for d in docs) / len(docs) if docs else 0,
            'avg_legal': sum(d.get('legal_number', 0) for d in docs) / len(docs) if docs else 0,
            'critical_count': len([d for d in docs if d.get('relevancy_number', 0) >= 900]),
            'high_value_count': len([d for d in docs if 800 <= d.get('relevancy_number', 0) < 900]),
            'strong_count': len([d for d in docs if 700 <= d.get('relevancy_number', 0) < 800]),
            'total_cost': sum(d.get('api_cost_usd', 0) for d in docs),
            'document_types': Counter(d.get('document_type') for d in docs if d.get('document_type')),
        }

        return stats
    except Exception as e:
        st.error(f"Error calculating statistics: {e}")
        return None

@st.cache_data(ttl=30)
def get_document_by_id(_client, doc_id):
    """Get single document by ID"""
    try:
        response = _client.table('legal_documents')\
            .select('*')\
            .eq('id', doc_id)\
            .execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error fetching document: {e}")
        return None

@st.cache_data(ttl=30)
def search_documents(_client, search_term):
    """Search documents"""
    try:
        docs = get_all_documents(_client)
        search_lower = search_term.lower()

        results = []
        for doc in docs:
            # Search in multiple fields
            searchable = ' '.join([
                str(doc.get('document_title', '')),
                str(doc.get('executive_summary', '')),
                ' '.join(doc.get('keywords', [])),
                ' '.join(doc.get('smoking_guns', []))
            ]).lower()

            if search_lower in searchable:
                results.append(doc)

        return sorted(results, key=lambda x: x.get('relevancy_number', 0), reverse=True)
    except Exception as e:
        st.error(f"Search error: {e}")
        return []

# ===== MAIN APP =====

def main():
    # Header
    st.title("⚖️ Legal Document Intelligence Dashboard")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("**Case:** In re Ashe B. (J24-00478)")

    # Initialize Supabase
    client, error = init_supabase()

    if error:
        st.error(f"❌ **Supabase Connection Failed**")
        st.code(error)

        if "legal_documents" in str(error):
            st.warning("⚠️ Table 'legal_documents' not found. Run the SQL schema first:")
            st.code("Resources/CH16_Technology/API-Integration/create_legal_documents_table.sql")
        else:
            st.info("💡 **Fix:** Run `source ~/.supabase_file_system` to load credentials")
        st.stop()

    st.success("✅ Connected to Legal Documents Database")
    st.markdown("---")

    # ===== SIDEBAR =====
    st.sidebar.header("📊 Analysis Mode")

    mode = st.sidebar.radio(
        "Select View",
        ["Dashboard", "Smoking Guns Pitch Chart", "Critical Documents", "All Documents", "Search", "Document Detail", "Score Analysis"],
        help="Choose analysis mode"
    )

    # ===== DASHBOARD MODE =====
    if mode == "Dashboard":
        st.header("📊 System Overview")

        stats = get_statistics(client)

        if not stats:
            st.warning("No documents found. Run the scanner to analyze documents.")
            st.code("python3 Resources/CH16_Technology/API-Integration/intelligent_document_scanner.py ~/Downloads/Areas/CH22_Legal")
            return

        # Top metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Documents", f"{stats['total_documents']:,}")

        with col2:
            st.metric("Average Relevancy", f"{stats['avg_relevancy']:.0f}/999")

        with col3:
            st.metric("Critical Docs", f"{stats['critical_count']}",
                     help="Relevancy ≥ 900")

        with col4:
            st.metric("Total API Cost", f"${stats['total_cost']:.2f}")

        st.markdown("---")

        # Score breakdown
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Score Tier Distribution")

            tier_data = [
                {"Tier": "🔴 Critical (900-999)", "Count": stats['critical_count']},
                {"Tier": "🟠 High Value (800-899)", "Count": stats['high_value_count']},
                {"Tier": "🟡 Strong (700-799)", "Count": stats['strong_count']},
            ]

            st.dataframe(pd.DataFrame(tier_data), width='stretch', hide_index=True)

        with col2:
            st.subheader("📈 Average Scores")

            score_data = [
                {"Metric": "Micro (Facts/Details)", "Score": f"{stats['avg_micro']:.0f}"},
                {"Metric": "Macro (Strategic)", "Score": f"{stats['avg_macro']:.0f}"},
                {"Metric": "Legal (Relevance)", "Score": f"{stats['avg_legal']:.0f}"},
                {"Metric": "Overall Relevancy", "Score": f"{stats['avg_relevancy']:.0f}"},
            ]

            st.dataframe(pd.DataFrame(score_data), width='stretch', hide_index=True)

        st.markdown("---")

        # Document types
        st.subheader("📄 Document Types")

        if stats['document_types']:
            type_data = []
            for doc_type, count in stats['document_types'].most_common():
                if doc_type:
                    type_data.append({
                        "Type": doc_type,
                        "Count": count,
                        "Percentage": f"{count/stats['total_documents']*100:.1f}%"
                    })

            st.dataframe(pd.DataFrame(type_data), width='stretch', hide_index=True)

    # ===== SMOKING GUNS PITCH CHART MODE =====
    elif mode == "Smoking Guns Pitch Chart":
        st.header("🔥 Smoking Guns Pitch Chart")
        st.markdown("**Visual map of document urgency by legal relevance vs strategic importance**")

        docs = get_all_documents(client)

        if not docs:
            st.warning("No documents found.")
            return

        # Prepare data for chart
        chart_data = []
        for doc in docs:
            rel = doc.get('relevancy_number', 0)

            # Determine urgency category
            if rel >= 900:
                category = "🔴 CRITICAL"
                color = "red"
            elif rel >= 800:
                category = "🟠 IMPORTANT"
                color = "orange"
            elif rel >= 700:
                category = "🟡 SIGNIFICANT"
                color = "gold"
            elif rel >= 600:
                category = "🟢 SUPPORTING"
                color = "green"
            else:
                category = "⚪ CONTEXT"
                color = "gray"

            # Check for smoking guns
            has_smoking_guns = len(doc.get('smoking_guns', [])) > 0
            smoking_gun_indicator = "🔥" if has_smoking_guns else ""

            chart_data.append({
                "Title": (smoking_gun_indicator + " " + doc.get('document_title', doc.get('original_filename', 'Untitled')))[:50],
                "Legal Score": doc.get('legal_number', 0),
                "Strategic Importance": doc.get('macro_number', 0),
                "Evidence Quality": doc.get('micro_number', 0),
                "Relevancy": rel,
                "Category": category,
                "Color": color,
                "Has Smoking Gun": has_smoking_guns,
                "Smoking Guns Count": len(doc.get('smoking_guns', [])),
                "W&I §388": doc.get('w388_relevance', 0),
                "CCP §473": doc.get('ccp473_relevance', 0),
                "Criminal": doc.get('criminal_relevance', 0)
            })

        df_chart = pd.DataFrame(chart_data)

        # Category breakdown
        col1, col2, col3 = st.columns(3)

        with col1:
            critical = len([d for d in chart_data if d['Category'] == "🔴 CRITICAL"])
            st.metric("🔴 CRITICAL (900-999)", critical, help="Smoking gun documents - immediate action")

        with col2:
            important = len([d for d in chart_data if d['Category'] == "🟠 IMPORTANT"])
            st.metric("🟠 IMPORTANT (800-899)", important, help="High priority evidence")

        with col3:
            significant = len([d for d in chart_data if d['Category'] == "🟡 SIGNIFICANT"])
            st.metric("🟡 SIGNIFICANT (700-799)", significant, help="Strong supporting evidence")

        st.markdown("---")

        # Smoking guns highlight
        smoking_gun_docs = [d for d in chart_data if d['Has Smoking Gun']]
        if smoking_gun_docs:
            st.success(f"🔥 **{len(smoking_gun_docs)} documents contain smoking guns!**")

            with st.expander(f"View {len(smoking_gun_docs)} Smoking Gun Documents"):
                for doc in sorted(smoking_gun_docs, key=lambda x: x['Relevancy'], reverse=True):
                    st.write(f"**[{doc['Relevancy']:03d}]** {doc['Title']} - 🔥 {doc['Smoking Guns Count']} smoking gun(s)")
        else:
            st.info("No smoking guns identified yet.")

        st.markdown("---")

        # Scatter plot data
        st.subheader("📊 Legal Relevance vs Strategic Importance")
        st.caption("**Size** = Evidence Quality (Micro Score) | **Color** = Urgency Category | 🔥 = Has Smoking Guns")

        # Create scatter plot data grouped by category for color coding
        for category in ["🔴 CRITICAL", "🟠 IMPORTANT", "🟡 SIGNIFICANT", "🟢 SUPPORTING", "⚪ CONTEXT"]:
            category_docs = df_chart[df_chart['Category'] == category]
            if len(category_docs) > 0:
                st.write(f"**{category}** ({len(category_docs)} documents)")

                # Create a simple scatter representation using dataframe
                display_data = category_docs[['Title', 'Legal Score', 'Strategic Importance', 'Evidence Quality', 'Relevancy', 'Smoking Guns Count']].copy()
                display_data = display_data.sort_values('Relevancy', ascending=False)
                st.dataframe(display_data, width='stretch', hide_index=True)
                st.markdown("")

        st.markdown("---")

        # Legal relevance breakdown
        st.subheader("⚖️ Legal Framework Relevance")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**W&I §388 (Reopen Dependency)**")
            top_w388 = sorted(chart_data, key=lambda x: x['W&I §388'], reverse=True)[:5]
            for i, doc in enumerate(top_w388, 1):
                if doc['W&I §388'] > 0:
                    st.write(f"{i}. [{doc['W&I §388']:03d}/100] {doc['Title'][:35]}")

        with col2:
            st.write("**CCP §473(d) (Void Orders)**")
            top_ccp = sorted(chart_data, key=lambda x: x['CCP §473'], reverse=True)[:5]
            for i, doc in enumerate(top_ccp, 1):
                if doc['CCP §473'] > 0:
                    st.write(f"{i}. [{doc['CCP §473']:03d}/100] {doc['Title'][:35]}")

        with col3:
            st.write("**Criminal (Perjury/Fraud)**")
            top_crim = sorted(chart_data, key=lambda x: x['Criminal'], reverse=True)[:5]
            for i, doc in enumerate(top_crim, 1):
                if doc['Criminal'] > 0:
                    st.write(f"{i}. [{doc['Criminal']:03d}/100] {doc['Title'][:35]}")

    # ===== CRITICAL DOCUMENTS MODE =====
    elif mode == "Critical Documents":
        st.header("🔴 Critical Documents (Score ≥ 900)")

        docs = get_all_documents(client)
        critical = [d for d in docs if d.get('relevancy_number', 0) >= 900]

        if not critical:
            st.warning("No critical documents found yet. Documents with relevancy ≥ 900 will appear here.")
            return

        st.success(f"Found {len(critical)} critical documents")

        for i, doc in enumerate(critical, 1):
            with st.expander(f"#{i} [{doc['relevancy_number']:03d}] {doc.get('document_title', doc.get('original_filename', 'Untitled'))}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Scores:**")
                    st.write(f"- Relevancy: **{doc['relevancy_number']}/999**")
                    st.write(f"- Micro: {doc['micro_number']}/999")
                    st.write(f"- Macro: {doc['macro_number']}/999")
                    st.write(f"- Legal: {doc['legal_number']}/999")

                    st.write(f"\n**Type:** {doc.get('document_type', 'N/A')}")
                    st.write(f"**Date:** {doc.get('document_date', 'N/A')}")

                with col2:
                    st.write("**Legal Relevance:**")
                    st.write(f"- W&I §388: {doc.get('w388_relevance', 0)}/100")
                    st.write(f"- CCP §473(d): {doc.get('ccp473_relevance', 0)}/100")
                    st.write(f"- Criminal: {doc.get('criminal_relevance', 0)}/100")

                    if doc.get('parties'):
                        st.write(f"\n**Parties:** {', '.join(doc['parties'])}")

                st.write(f"\n**Summary:**")
                st.info(doc.get('executive_summary', 'No summary available'))

                if doc.get('smoking_guns'):
                    st.write(f"\n🔥 **Smoking Guns:**")
                    for sg in doc['smoking_guns']:
                        st.write(f"- {sg}")

                if doc.get('key_quotes'):
                    st.write(f"\n💬 **Key Quotes:**")
                    for quote in doc['key_quotes']:
                        st.write(f"> {quote}")

                st.caption(f"ID: {doc['id']} | File: {doc.get('original_filename')}")

    # ===== ALL DOCUMENTS MODE =====
    elif mode == "All Documents":
        st.header("📚 All Documents")

        docs = get_all_documents(client)

        if not docs:
            st.warning("No documents found.")
            return

        # Filters
        col1, col2, col3 = st.columns(3)

        with col1:
            min_score = st.slider("Min Relevancy Score", 0, 999, 0)

        with col2:
            doc_types = list(set(d.get('document_type') for d in docs if d.get('document_type')))
            selected_type = st.selectbox("Document Type", ["All"] + doc_types)

        with col3:
            sort_by = st.selectbox("Sort By", ["Relevancy", "Micro", "Macro", "Legal", "Date"])

        # Apply filters
        filtered = [d for d in docs if d.get('relevancy_number', 0) >= min_score]

        if selected_type != "All":
            filtered = [d for d in filtered if d.get('document_type') == selected_type]

        # Sort
        sort_field = {
            "Relevancy": "relevancy_number",
            "Micro": "micro_number",
            "Macro": "macro_number",
            "Legal": "legal_number",
            "Date": "document_date"
        }[sort_by]

        filtered = sorted(filtered, key=lambda x: x.get(sort_field, 0), reverse=True)

        st.success(f"Showing {len(filtered)} documents")

        # Display table
        table_data = []
        for doc in filtered:
            table_data.append({
                "Title": doc.get('document_title', doc.get('original_filename', 'Untitled'))[:50],
                "Relevancy": doc['relevancy_number'],
                "Micro": doc['micro_number'],
                "Macro": doc['macro_number'],
                "Legal": doc['legal_number'],
                "Type": doc.get('document_type', 'N/A'),
                "Date": doc.get('document_date', 'N/A'),
                "ID": doc['id'][:8] + "..."
            })

        st.dataframe(pd.DataFrame(table_data), width='stretch', hide_index=True)

    # ===== SEARCH MODE =====
    elif mode == "Search":
        st.header("🔍 Search Documents")

        search_term = st.text_input("Search for keywords", placeholder="e.g., grandfather, admission, disclosure, abuse")

        if search_term:
            with st.spinner("Searching..."):
                results = search_documents(client, search_term)

            if results:
                st.success(f"Found {len(results)} documents matching '{search_term}'")

                for i, doc in enumerate(results[:20], 1):  # Top 20
                    with st.expander(f"#{i} [{doc['relevancy_number']:03d}] {doc.get('document_title', doc.get('original_filename'))}"):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write(f"**Scores:** Rel={doc['relevancy_number']}, Micro={doc['micro_number']}, Macro={doc['macro_number']}, Legal={doc['legal_number']}")
                            st.write(f"**Type:** {doc.get('document_type', 'N/A')}")
                            st.write(f"**Date:** {doc.get('document_date', 'N/A')}")

                        with col2:
                            if doc.get('keywords'):
                                st.write(f"**Keywords:** {', '.join(doc['keywords'][:5])}")

                        st.info(doc.get('executive_summary', 'No summary'))

                        if doc.get('smoking_guns'):
                            st.write("🔥 **Smoking Guns:**")
                            for sg in doc['smoking_guns'][:3]:
                                st.write(f"- {sg}")
            else:
                st.warning(f"No documents found matching '{search_term}'")

    # ===== DOCUMENT DETAIL MODE =====
    elif mode == "Document Detail":
        st.header("📄 Document Detail View")

        docs = get_all_documents(client)

        if not docs:
            st.warning("No documents found.")
            return

        # Select document
        doc_titles = [f"[{d['relevancy_number']:03d}] {d.get('document_title', d.get('original_filename'))}" for d in docs]
        selected = st.selectbox("Select Document", doc_titles)

        if selected:
            # Extract index
            idx = doc_titles.index(selected)
            doc = docs[idx]

            # Display full details
            st.subheader(doc.get('document_title', doc.get('original_filename')))

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Relevancy Score", f"{doc['relevancy_number']}/999")
                st.metric("Micro (Facts)", f"{doc['micro_number']}/999")

            with col2:
                st.metric("Macro (Strategy)", f"{doc['macro_number']}/999")
                st.metric("Legal (Relevance)", f"{doc['legal_number']}/999")

            with col3:
                st.metric("Category", f"{doc.get('category_number', 0)}/999")
                st.metric("Document Type", doc.get('document_type', 'N/A'))

            st.markdown("---")

            # Explanations
            st.subheader("📊 Score Explanations")

            if doc.get('micro_explanation'):
                with st.expander("Micro Score Explanation"):
                    st.write(doc['micro_explanation'])

            if doc.get('macro_explanation'):
                with st.expander("Macro Score Explanation"):
                    st.write(doc['macro_explanation'])

            if doc.get('legal_explanation'):
                with st.expander("Legal Score Explanation"):
                    st.write(doc['legal_explanation'])

            st.markdown("---")

            # Content
            st.subheader("📝 Content")

            st.write(f"**Executive Summary:**")
            st.info(doc.get('executive_summary', 'No summary'))

            if doc.get('smoking_guns'):
                st.write(f"\n🔥 **Smoking Guns:**")
                for sg in doc['smoking_guns']:
                    st.error(f"🔥 {sg}")

            if doc.get('key_quotes'):
                st.write(f"\n💬 **Key Quotes:**")
                for quote in doc['key_quotes']:
                    st.write(f"> {quote}")

            st.markdown("---")

            # Legal relevance
            st.subheader("⚖️ Legal Relevance")

            lcol1, lcol2, lcol3 = st.columns(3)

            with lcol1:
                st.metric("W&I §388", f"{doc.get('w388_relevance', 0)}/100",
                         help="Relevance to reopening dependency case")

            with lcol2:
                st.metric("CCP §473(d)", f"{doc.get('ccp473_relevance', 0)}/100",
                         help="Relevance to void orders")

            with lcol3:
                st.metric("Criminal", f"{doc.get('criminal_relevance', 0)}/100",
                         help="Relevance to perjury/fraud claims")

            st.markdown("---")

            # Metadata
            st.subheader("📋 Metadata")

            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**File:** {doc.get('original_filename')}")
                st.write(f"**Type:** {doc.get('document_type', 'N/A')}")
                st.write(f"**Date:** {doc.get('document_date', 'N/A')}")
                st.write(f"**Size:** {doc.get('file_size', 0)/1024:.1f} KB")

            with col2:
                if doc.get('parties'):
                    st.write(f"**Parties:** {', '.join(doc['parties'])}")
                if doc.get('keywords'):
                    st.write(f"**Keywords:** {', '.join(doc['keywords'][:10])}")
                st.write(f"**Processed:** {doc.get('processed_at', 'N/A')[:10]}")
                st.write(f"**API Cost:** ${doc.get('api_cost_usd', 0):.4f}")

            st.caption(f"Document ID: {doc['id']}")

    # ===== SCORE ANALYSIS MODE =====
    elif mode == "Score Analysis":
        st.header("📈 Score Analysis")

        docs = get_all_documents(client)

        if not docs:
            st.warning("No documents found.")
            return

        # Score distribution
        st.subheader("Score Distribution")

        score_data = []
        for doc in docs:
            score_data.append({
                "Document": doc.get('document_title', doc.get('original_filename'))[:40],
                "Relevancy": doc['relevancy_number'],
                "Micro": doc['micro_number'],
                "Macro": doc['macro_number'],
                "Legal": doc['legal_number']
            })

        df = pd.DataFrame(score_data)

        # Display chart
        st.bar_chart(df.set_index('Document')[['Relevancy', 'Micro', 'Macro', 'Legal']])

        st.markdown("---")

        # Top performers
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🏆 Top by Micro Score")
            top_micro = sorted(docs, key=lambda x: x.get('micro_number', 0), reverse=True)[:5]
            for i, doc in enumerate(top_micro, 1):
                st.write(f"{i}. [{doc['micro_number']:03d}] {doc.get('document_title', doc.get('original_filename'))[:40]}")

            st.subheader("🏆 Top by Macro Score")
            top_macro = sorted(docs, key=lambda x: x.get('macro_number', 0), reverse=True)[:5]
            for i, doc in enumerate(top_macro, 1):
                st.write(f"{i}. [{doc['macro_number']:03d}] {doc.get('document_title', doc.get('original_filename'))[:40]}")

        with col2:
            st.subheader("🏆 Top by Legal Score")
            top_legal = sorted(docs, key=lambda x: x.get('legal_number', 0), reverse=True)[:5]
            for i, doc in enumerate(top_legal, 1):
                st.write(f"{i}. [{doc['legal_number']:03d}] {doc.get('document_title', doc.get('original_filename'))[:40]}")

            st.subheader("🏆 Top by Relevancy")
            top_rel = sorted(docs, key=lambda x: x.get('relevancy_number', 0), reverse=True)[:5]
            for i, doc in enumerate(top_rel, 1):
                st.write(f"{i}. [{doc['relevancy_number']:03d}] {doc.get('document_title', doc.get('original_filename'))[:40]}")

    # Footer
    st.markdown("---")
    st.caption(f"🔗 Legal Documents Database • Dashboard refresh: Browser refresh")

if __name__ == "__main__":
    main()
