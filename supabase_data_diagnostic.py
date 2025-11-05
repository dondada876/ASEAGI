"""
Supabase Data Diagnostic Tool
Checks all tables and their row counts to verify data sync from Mac Mini
"""

import streamlit as st
from supabase import create_client
import os
from datetime import datetime

st.set_page_config(page_title="Supabase Data Diagnostic", layout="wide", page_icon="🔍")

# Initialize Supabase
@st.cache_resource
def init_supabase():
    """Initialize Supabase client"""
    url = st.secrets.get('SUPABASE_URL') if hasattr(st, 'secrets') else os.environ.get('SUPABASE_URL', 'https://jvjlhxodmbkodzmggwpu.supabase.co')
    key = st.secrets.get('SUPABASE_KEY') if hasattr(st, 'secrets') else os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2amxoeG9kbWJrb2R6bWdnd3B1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyMjMxOTAsImV4cCI6MjA3Nzc5OTE5MH0.ai65vVW816bNAV56XiuRxp5PE5IhBkMGPx3IbxfPh8c')

    try:
        client = create_client(url, key)
        return client, None
    except Exception as e:
        return None, str(e)

supabase, error = init_supabase()

st.title("🔍 Supabase Data Diagnostic")
st.markdown("### Checking all tables for data from Mac Mini processing")

if error:
    st.error(f"Connection Error: {error}")
    st.stop()

st.success("✅ Connected to Supabase")

# Define all expected tables based on PROJ344 documentation
CORE_TABLES = [
    'legal_documents',
    'document_pages',
    'legal_violations',
    'court_events',
    'communications_matrix',
    'dvro_violations_tracker',
    'court_case_tracker',
    'legal_citations',
    'file_metadata',
    'file_cross_references',
    'action_items',
    'micro_analysis',
    'checkbox_perjury',
    'false_statements',
    'actions_vs_intentions'
]

# Additional tables that might exist
ADDITIONAL_TABLES = [
    'document_analysis',
    'evidence_tracker',
    'timeline_events',
    'violations_by_perpetrator',
    'critical_documents'
]

st.markdown("---")
st.subheader("📊 Core Tables Analysis")

results = {}
total_rows = 0

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("#### Table Row Counts")

    for table in CORE_TABLES:
        try:
            response = supabase.table(table).select('*', count='exact').limit(0).execute()
            count = response.count if hasattr(response, 'count') else 0
            results[table] = count
            total_rows += count

            # Visual indicator
            if count == 0:
                status = "🔴"
                color = "red"
            elif count < 10:
                status = "🟡"
                color = "orange"
            else:
                status = "🟢"
                color = "green"

            st.markdown(f"{status} **{table}**: <span style='color: {color}; font-weight: bold'>{count:,} rows</span>", unsafe_allow_html=True)

        except Exception as e:
            st.warning(f"❌ **{table}**: Table not found or error - {str(e)}")
            results[table] = 0

with col2:
    st.metric("Total Rows Across All Tables", f"{total_rows:,}")
    st.metric("Tables with Data", f"{sum(1 for v in results.values() if v > 0)}/{len(CORE_TABLES)}")
    st.metric("Empty Tables", f"{sum(1 for v in results.values() if v == 0)}")

st.markdown("---")
st.subheader("🔬 Detailed Table Analysis")

# Check tables that should have the most data
priority_tables = ['legal_documents', 'document_pages', 'legal_violations', 'court_events']

for table in priority_tables:
    with st.expander(f"🔍 Inspect {table} ({results.get(table, 0):,} rows)"):
        if results.get(table, 0) > 0:
            try:
                # Get sample data
                sample = supabase.table(table).select('*').limit(5).execute()

                if sample.data:
                    st.success(f"✅ Found {len(sample.data)} sample records")

                    # Show first record structure
                    st.markdown("**First Record Structure:**")
                    st.json(sample.data[0])

                    # Show all records
                    st.markdown("**Sample Data:**")
                    import pandas as pd
                    df = pd.DataFrame(sample.data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("Table exists but returned no data")

            except Exception as e:
                st.error(f"Error fetching sample data: {str(e)}")
        else:
            st.warning("⚠️ This table is empty. Mac Mini may not be syncing data to Supabase.")

st.markdown("---")
st.subheader("🔄 Data Sync Status")

# Check if data looks fresh
if results.get('legal_documents', 0) > 0:
    try:
        recent = supabase.table('legal_documents').select('created_at, updated_at').order('created_at', desc=True).limit(1).execute()

        if recent.data and len(recent.data) > 0:
            latest = recent.data[0]
            st.success(f"✅ Most recent document added: {latest.get('created_at', 'Unknown')}")

            # Check for updated_at field
            if 'updated_at' in latest:
                st.info(f"📅 Last updated: {latest.get('updated_at', 'Unknown')}")
    except Exception as e:
        st.warning(f"Could not determine last update time: {str(e)}")

# Overall assessment
st.markdown("---")
st.subheader("📋 Assessment & Recommendations")

if total_rows == 0:
    st.error("""
    🚨 **CRITICAL: No data found in any tables**

    **Possible Issues:**
    1. Mac Mini processing scripts are not running
    2. Mac Mini is not uploading to Supabase
    3. Mac Mini is connected to a different Supabase instance
    4. Credentials on Mac Mini are incorrect

    **Recommended Actions:**
    1. Check Mac Mini - verify scripts are running
    2. Verify Mac Mini Supabase credentials match Windows
    3. Check Mac Mini logs for upload errors
    4. Manually test Supabase connection from Mac Mini
    """)

elif total_rows < 100:
    st.warning("""
    ⚠️ **WARNING: Very little data found**

    Expected: Hundreds or thousands of documents, pages, violations
    Found: Only a few records

    **Possible Issues:**
    1. Mac Mini is only partially syncing data
    2. Data processing is still in progress
    3. Database tables need to be populated

    **Recommended Actions:**
    1. Check Mac Mini processing status
    2. Review Mac Mini logs for errors
    3. Verify all data types are being uploaded
    """)

else:
    st.success(f"""
    ✅ **Data sync appears healthy**

    - Found {total_rows:,} total rows across all tables
    - {sum(1 for v in results.values() if v > 0)} tables have data
    - Dashboard should display comprehensive information

    If dashboard still shows incomplete data, check:
    1. Dashboard query filters
    2. Data visualization code
    3. Cache issues (try clearing cache)
    """)

# Connection info
st.markdown("---")
st.caption(f"""
**Connection Details**
- Database: {os.environ.get('SUPABASE_URL', st.secrets.get('SUPABASE_URL', 'Unknown'))[:40]}...
- Diagnostic run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")

# Add refresh button
if st.button("🔄 Refresh Diagnostic"):
    st.cache_resource.clear()
    st.rerun()
