"""
ASEAGI Admin Dashboard
Multi-jurisdiction case management with DuckDB analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics.duckdb_engine import create_analytics_engine

# Page configuration
st.set_page_config(
    page_title="ASEAGI Admin Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize analytics engine
@st.cache_resource
def get_analytics_engine():
    return create_analytics_engine()

engine = get_analytics_engine()


# ═══════════════════════════════════════════════════════════════
# SIDEBAR - Navigation & Filters
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.title("🛡️ ASEAGI Admin")
    st.caption("Jurisdiction-Agnostic Case Management")

    st.divider()

    # Sync controls
    st.subheader("Data Sync")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Sync Now"):
            with st.spinner("Syncing..."):
                status = engine.sync_from_supabase()
                if status.success:
                    st.success(f"Synced {status.documents_synced} docs")
                else:
                    st.error(f"Sync failed: {status.error}")
    with col2:
        if st.button("🔄 Full Sync"):
            with st.spinner("Full sync..."):
                status = engine.sync_from_supabase(full_sync=True)
                if status.success:
                    st.success(f"Synced {status.documents_synced} docs")

    if engine.last_sync:
        st.caption(f"Last sync: {engine.last_sync.strftime('%H:%M:%S')}")

    st.divider()

    # Filters
    st.subheader("Filters")

    # Get available jurisdictions
    try:
        jurisdictions_df = engine.query("SELECT DISTINCT code FROM jurisdictions ORDER BY code")
        jurisdictions = ["All"] + jurisdictions_df['code'].tolist()
    except:
        jurisdictions = ["All"]

    selected_jurisdiction = st.selectbox(
        "Jurisdiction",
        options=jurisdictions
    )

    # Get available cases
    try:
        case_filter = ""
        if selected_jurisdiction != "All":
            case_filter = f"WHERE jurisdiction_code = '{selected_jurisdiction}'"
        cases_df = engine.query(f"SELECT DISTINCT case_number FROM cases {case_filter} ORDER BY case_number")
        cases = ["All"] + cases_df['case_number'].tolist()
    except:
        cases = ["All"]

    selected_case = st.selectbox(
        "Case",
        options=cases
    )

    # Document type filter
    doc_types = ["All", "Motion", "Declaration", "Order", "Letter", "Report", "Email", "Other"]
    selected_type = st.selectbox("Document Type", doc_types)

    # Score range filter
    min_score, max_score = st.slider(
        "Relevancy Score Range",
        0, 1000, (0, 1000)
    )

    # Date range
    st.subheader("Date Range")
    date_option = st.selectbox(
        "Period",
        ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days", "Custom"]
    )

    if date_option == "Custom":
        date_from = st.date_input("From")
        date_to = st.date_input("To")
    else:
        date_to = datetime.now()
        if date_option == "Last 7 Days":
            date_from = date_to - timedelta(days=7)
        elif date_option == "Last 30 Days":
            date_from = date_to - timedelta(days=30)
        elif date_option == "Last 90 Days":
            date_from = date_to - timedelta(days=90)
        else:
            date_from = None


# ═══════════════════════════════════════════════════════════════
# MAIN CONTENT - TABS
# ═══════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📄 Documents",
    "📁 Cases",
    "📊 Analytics",
    "📝 Custom Reports",
    "⚙️ Settings"
])


# ═══════════════════════════════════════════════════════════════
# TAB 1: DOCUMENT INSPECTOR
# ═══════════════════════════════════════════════════════════════

with tab1:
    st.header("Document Inspector")

    # Get stats
    jur_filter = None if selected_jurisdiction == "All" else selected_jurisdiction
    stats = engine.get_dashboard_stats(jur_filter)

    # Metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Documents", f"{stats.get('total_docs', 0):,}")
    with col2:
        st.metric("Smoking Guns (900+)", stats.get('smoking_guns', 0))
    with col3:
        st.metric("This Week", stats.get('new_this_week', 0))
    with col4:
        st.metric("Avg Relevancy", f"{stats.get('avg_relevancy', 0):.0f}")
    with col5:
        st.metric("Cases", stats.get('total_cases', 0))

    st.divider()

    # Search bar
    search_query = st.text_input(
        "🔍 Search documents...",
        placeholder="Enter keywords, case number, or document type"
    )

    # View mode toggle
    view_mode = st.radio(
        "View",
        ["Table", "Grid", "Timeline"],
        horizontal=True
    )

    # Get documents based on filters
    case_id_filter = None
    if selected_case != "All":
        try:
            case_result = engine.query(f"SELECT id FROM cases WHERE case_number = '{selected_case}'")
            if not case_result.empty:
                case_id_filter = case_result.iloc[0]['id']
        except:
            pass

    doc_type_filter = None if selected_type == "All" else selected_type

    if search_query:
        documents = engine.search_documents(
            query=search_query,
            case_id=case_id_filter,
            jurisdiction=jur_filter,
            doc_type=doc_type_filter,
            min_score=min_score,
            max_score=max_score
        )
    else:
        # Build query for all documents with filters
        filters = []
        if jur_filter:
            filters.append(f"jurisdiction_code = '{jur_filter}'")
        if case_id_filter:
            filters.append(f"case_id = '{case_id_filter}'")
        if doc_type_filter:
            filters.append(f"document_type = '{doc_type_filter}'")
        filters.append(f"relevancy_number BETWEEN {min_score} AND {max_score}")

        where = " AND ".join(filters) if filters else "1=1"

        documents = engine.query(f"""
            SELECT
                id, title, original_filename, document_type, date,
                relevancy_number, micro_number, macro_number, legal_number,
                summary, case_number, jurisdiction_code, contains_false_statements
            FROM documents
            WHERE {where}
            ORDER BY relevancy_number DESC NULLS LAST
            LIMIT 200
        """)

    # Display documents
    if view_mode == "Table":
        if not documents.empty:
            # Format the dataframe for display
            display_df = documents[['title', 'document_type', 'date', 'relevancy_number',
                                     'case_number', 'jurisdiction_code', 'contains_false_statements']].copy()
            display_df.columns = ['Title', 'Type', 'Date', 'Relevancy', 'Case', 'Jurisdiction', 'Perjury']

            # Add score badges
            def score_badge(score):
                if pd.isna(score):
                    return "⚪ N/A"
                if score >= 900:
                    return f"🔥 {int(score)}"
                elif score >= 800:
                    return f"⚠️ {int(score)}"
                elif score >= 700:
                    return f"📌 {int(score)}"
                else:
                    return f"📄 {int(score)}"

            display_df['Relevancy'] = display_df['Relevancy'].apply(score_badge)
            display_df['Perjury'] = display_df['Perjury'].apply(lambda x: "⚠️ Yes" if x else "")

            st.dataframe(
                display_df,
                use_container_width=True,
                height=500
            )

            st.caption(f"Showing {len(documents)} documents")
        else:
            st.info("No documents found matching your filters.")

    elif view_mode == "Grid":
        if not documents.empty:
            cols = st.columns(4)
            for i, (_, doc) in enumerate(documents.head(20).iterrows()):
                with cols[i % 4]:
                    with st.container(border=True):
                        # Score badge
                        score = doc.get('relevancy_number')
                        if pd.notna(score):
                            if score >= 900:
                                st.markdown(f"🔥 **{int(score)}** - Smoking Gun")
                            elif score >= 800:
                                st.markdown(f"⚠️ **{int(score)}** - Critical")
                            else:
                                st.markdown(f"📄 **{int(score)}**")
                        else:
                            st.markdown("⚪ Unscored")

                        # Title
                        title = doc.get('title', 'Untitled')
                        if len(str(title)) > 40:
                            title = str(title)[:37] + "..."
                        st.markdown(f"**{title}**")

                        # Metadata
                        st.caption(f"{doc.get('document_type', 'Unknown')} | {doc.get('date', 'N/A')}")
                        st.caption(f"{doc.get('case_number', 'N/A')} | {doc.get('jurisdiction_code', 'N/A')}")

                        if st.button("View", key=f"view_{doc['id']}"):
                            st.session_state.selected_doc = doc['id']
        else:
            st.info("No documents found matching your filters.")

    else:  # Timeline
        if not documents.empty and 'date' in documents.columns:
            # Group by date
            timeline_df = documents.copy()
            timeline_df['date'] = pd.to_datetime(timeline_df['date'], errors='coerce')
            timeline_df = timeline_df.dropna(subset=['date'])

            if not timeline_df.empty:
                timeline_df = timeline_df.sort_values('date')

                fig = px.scatter(
                    timeline_df,
                    x='date',
                    y='relevancy_number',
                    color='document_type',
                    size='relevancy_number',
                    hover_data=['title', 'case_number'],
                    title="Document Timeline"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No documents with valid dates found.")
        else:
            st.info("No documents found matching your filters.")


# ═══════════════════════════════════════════════════════════════
# TAB 2: CASE MANAGEMENT
# ═══════════════════════════════════════════════════════════════

with tab2:
    st.header("Case Management")

    # Get cases
    try:
        case_filter = ""
        if selected_jurisdiction != "All":
            case_filter = f"WHERE jurisdiction_code = '{selected_jurisdiction}'"

        cases_data = engine.query(f"""
            SELECT
                c.*,
                COUNT(d.id) as document_count,
                COUNT(d.id) FILTER (WHERE d.relevancy_number >= 900) as smoking_guns
            FROM cases c
            LEFT JOIN documents d ON d.case_id = c.id
            {case_filter}
            GROUP BY c.id
            ORDER BY c.updated_at DESC NULLS LAST
        """)
    except Exception as e:
        cases_data = pd.DataFrame()
        st.error(f"Error loading cases: {e}")

    if not cases_data.empty:
        # Group by status for Kanban view
        statuses = ['active', 'pending', 'closed']
        cols = st.columns(len(statuses))

        for col, status in zip(cols, statuses):
            with col:
                status_cases = cases_data[cases_data['status'] == status]
                st.markdown(f"### {'🟢' if status == 'active' else '🟡' if status == 'pending' else '⚫'} {status.title()}")
                st.caption(f"{len(status_cases)} cases")

                for _, case in status_cases.head(10).iterrows():
                    with st.container(border=True):
                        st.markdown(f"**{case.get('case_number', 'N/A')}**")
                        st.caption(f"{case.get('court_case_number', 'N/A')}")
                        st.caption(f"{case.get('jurisdiction_code', 'N/A')}")

                        # Document count
                        doc_count = case.get('document_count', 0)
                        smoking_guns = case.get('smoking_guns', 0)
                        st.caption(f"📄 {doc_count} docs | 🔥 {smoking_guns} smoking guns")

                        # Scores
                        if pd.notna(case.get('truth_score')):
                            st.progress(int(case['truth_score']) / 1000, text=f"Truth: {int(case['truth_score'])}")

                        # Next hearing
                        if pd.notna(case.get('next_hearing_date')):
                            hearing = pd.to_datetime(case['next_hearing_date'])
                            days_until = (hearing - datetime.now()).days
                            if days_until <= 7:
                                st.error(f"⏰ Hearing in {days_until} days")
                            elif days_until <= 30:
                                st.warning(f"📅 Hearing in {days_until} days")
    else:
        st.info("No cases found. Create a new case to get started.")

    st.divider()

    # Create new case
    with st.expander("➕ Create New Case"):
        col1, col2 = st.columns(2)
        with col1:
            new_jurisdiction = st.selectbox("Jurisdiction", jurisdictions[1:] if len(jurisdictions) > 1 else ["US-CA"], key="new_case_jur")
            new_case_type = st.selectbox("Case Type", ["family", "civil", "criminal", "probate"])
            court_case_number = st.text_input("Court Case Number")
        with col2:
            court_name = st.text_input("Court Name")
            filed_date = st.date_input("Filed Date", key="new_case_date")
            next_hearing = st.date_input("Next Hearing", key="new_case_hearing")

        if st.button("Create Case"):
            st.info("Case creation requires Supabase connection. Apply the migration first.")


# ═══════════════════════════════════════════════════════════════
# TAB 3: ANALYTICS
# ═══════════════════════════════════════════════════════════════

with tab3:
    st.header("📊 Analytics Dashboard")

    # Refresh stats
    stats = engine.get_dashboard_stats(jur_filter)

    # Metric cards
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Documents", f"{stats.get('total_docs', 0):,}")
    with col2:
        st.metric("Cases", stats.get('total_cases', 0))
    with col3:
        st.metric("Avg Relevancy", f"{stats.get('avg_relevancy', 0):.0f}")
    with col4:
        st.metric("Smoking Guns", stats.get('smoking_guns', 0))
    with col5:
        st.metric("Perjury Docs", stats.get('perjury_docs', 0))
    with col6:
        st.metric("API Cost", f"${stats.get('total_api_cost', 0):.2f}")

    st.divider()

    # Charts row 1
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Documents by Jurisdiction")
        jurisdiction_data = engine.get_documents_by_jurisdiction()
        if not jurisdiction_data.empty:
            fig = px.pie(jurisdiction_data, names='jurisdiction_code', values='count')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No jurisdiction data available")

    with col_right:
        st.subheader("Score Distribution")
        score_data = engine.get_score_distribution()
        if not score_data.empty:
            fig = px.bar(score_data, x='category', y='count', color='category')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No score data available")

    # Charts row 2
    st.subheader("Document Processing Timeline")
    timeline_data = engine.get_processing_timeline(days=30)
    if not timeline_data.empty:
        fig = px.line(timeline_data, x='date', y='documents', markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No timeline data available")

    # Cross-jurisdiction comparison
    st.subheader("Cross-Jurisdiction Comparison")
    comparison_data = engine.get_cross_jurisdiction_analysis()
    if not comparison_data.empty:
        st.dataframe(comparison_data, use_container_width=True)
    else:
        st.info("No cross-jurisdiction data available")


# ═══════════════════════════════════════════════════════════════
# TAB 4: CUSTOM REPORTS
# ═══════════════════════════════════════════════════════════════

with tab4:
    st.header("📝 Custom Reports")

    # Report templates
    st.subheader("Quick Reports")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Case Summary Report", use_container_width=True):
            if selected_case != "All":
                try:
                    case_result = engine.query(f"SELECT id FROM cases WHERE case_number = '{selected_case}'")
                    if not case_result.empty:
                        summary = engine.get_case_summary(case_result.iloc[0]['id'])
                        st.json(summary)
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please select a specific case first")

    with col2:
        if st.button("🔥 Smoking Guns Report", use_container_width=True):
            smoking_guns = engine.get_smoking_guns(jurisdiction=jur_filter)
            if not smoking_guns.empty:
                st.dataframe(smoking_guns, use_container_width=True)

                # Download button
                csv = smoking_guns.to_csv(index=False)
                st.download_button(
                    "📥 Download CSV",
                    csv,
                    file_name="smoking_guns_report.csv",
                    mime="text/csv"
                )
            else:
                st.info("No smoking guns found")

    with col3:
        if st.button("⚖️ Perjury Report", use_container_width=True):
            perjury = engine.get_perjury_evidence(jurisdiction=jur_filter)
            if not perjury.empty:
                st.dataframe(perjury, use_container_width=True)

                csv = perjury.to_csv(index=False)
                st.download_button(
                    "📥 Download CSV",
                    csv,
                    file_name="perjury_report.csv",
                    mime="text/csv"
                )
            else:
                st.info("No perjury evidence found")

    st.divider()

    # Custom SQL Query
    st.subheader("Custom SQL Query")
    st.caption("Write SQL queries against DuckDB for real-time analysis")

    # Pre-built query templates
    query_templates = {
        "Select template...": "",
        "Documents by case and score": """SELECT
    case_number,
    document_type,
    COUNT(*) as doc_count,
    AVG(relevancy_number) as avg_score
FROM documents
GROUP BY case_number, document_type
ORDER BY avg_score DESC""",
        "Smoking guns by jurisdiction": """SELECT
    jurisdiction_code,
    COUNT(*) as smoking_gun_count
FROM documents
WHERE relevancy_number >= 900
GROUP BY jurisdiction_code
ORDER BY smoking_gun_count DESC""",
        "Perjury evidence summary": """SELECT
    case_number,
    title,
    date,
    perjury_indicators
FROM documents
WHERE contains_false_statements = true
ORDER BY date DESC""",
        "Processing activity": """SELECT
    DATE_TRUNC('day', processed_at) as day,
    COUNT(*) as docs_processed,
    AVG(relevancy_number) as avg_score,
    SUM(api_cost_usd) as daily_cost
FROM documents
WHERE processed_at IS NOT NULL
GROUP BY day
ORDER BY day DESC
LIMIT 30"""
    }

    query_template = st.selectbox(
        "Start from template",
        list(query_templates.keys())
    )

    # SQL editor
    sql_query = st.text_area(
        "SQL Query",
        value=query_templates[query_template],
        height=200,
        help="Query runs against DuckDB with synced data"
    )

    # Available tables reference
    with st.expander("📚 Available Tables & Fields"):
        st.markdown("""
        **documents**
        - id, case_id, jurisdiction_id, jurisdiction_code, case_number
        - document_type, date, title, original_filename, summary
        - relevancy_number, micro_number, macro_number, legal_number
        - truth_score, justice_score, contains_false_statements
        - key_quotes, fraud_indicators, perjury_indicators
        - api_cost_usd, processed_at, created_at

        **cases**
        - id, case_number, court_case_number, court_name
        - jurisdiction_id, jurisdiction_code, case_type, case_subtype
        - status, petitioner, respondent
        - truth_score, justice_score, legal_credit_score, urgency_level
        - filed_date, next_hearing_date

        **jurisdictions**
        - id, code, name, country_code, subdivision_code
        - legal_system, timezone
        """)

    col1, col2 = st.columns([1, 4])
    with col1:
        run_query = st.button("▶️ Run Query", type="primary")

    if run_query and sql_query:
        try:
            result = engine.query(sql_query)
            st.success(f"Query returned {len(result)} rows")
            st.dataframe(result, use_container_width=True)

            # Export options
            col1, col2 = st.columns(2)
            with col1:
                csv = result.to_csv(index=False)
                st.download_button(
                    "📥 Download CSV",
                    csv,
                    file_name="query_result.csv",
                    mime="text/csv"
                )
            with col2:
                json_data = result.to_json(orient='records')
                st.download_button(
                    "📥 Download JSON",
                    json_data,
                    file_name="query_result.json",
                    mime="application/json"
                )

        except Exception as e:
            st.error(f"Query error: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# TAB 5: SETTINGS
# ═══════════════════════════════════════════════════════════════

with tab5:
    st.header("⚙️ Settings")

    st.subheader("Database Status")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**DuckDB Analytics**")
        st.markdown(f"- Path: `{engine.db_path}`")
        st.markdown(f"- Last Sync: {engine.last_sync.strftime('%Y-%m-%d %H:%M:%S') if engine.last_sync else 'Never'}")

        # Table counts
        try:
            doc_count = engine.query("SELECT COUNT(*) as count FROM documents").iloc[0]['count']
            case_count = engine.query("SELECT COUNT(*) as count FROM cases").iloc[0]['count']
            jur_count = engine.query("SELECT COUNT(*) as count FROM jurisdictions").iloc[0]['count']

            st.markdown(f"- Documents: {doc_count:,}")
            st.markdown(f"- Cases: {case_count}")
            st.markdown(f"- Jurisdictions: {jur_count}")
        except:
            st.warning("Could not retrieve table counts")

    with col2:
        st.markdown("**Supabase Connection**")
        if engine.supabase:
            st.success("Connected")
        else:
            st.warning("Not connected - using local DuckDB only")
            st.markdown("Set `SUPABASE_URL` and `SUPABASE_KEY` environment variables to enable sync.")

    st.divider()

    st.subheader("Migration")
    st.markdown("""
    To set up the jurisdiction-agnostic schema, run the migration:

    ```bash
    # Via Supabase SQL Editor or psql
    psql $DATABASE_URL -f database/migrations/001_jurisdiction_agnostic_schema.sql
    ```

    This will create:
    - `jurisdictions` table with initial US states + UK
    - `cases` table with auto-numbering
    - Add `case_id` and `jurisdiction_id` to `legal_documents`
    - Migrate existing J24-00478 case
    """)

    st.divider()

    st.subheader("Environment Variables")
    st.code("""
# Required for Supabase sync
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Optional
ANTHROPIC_API_KEY=your-key  # For document analysis
    """, language="bash")


# Footer
st.divider()
st.caption("ASEAGI Admin Dashboard v2.0 - Jurisdiction-Agnostic Case Management")
st.caption("*For Ashe. For Justice. For All Children.*")
