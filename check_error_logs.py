"""
Quick script to check error logs from Supabase
"""
import streamlit as st
from supabase import create_client
import os
import pandas as pd

st.set_page_config(page_title="Error Logs Checker", layout="wide", page_icon="🔍")

# Initialize Supabase
@st.cache_resource
def init_supabase():
    url = st.secrets.get('SUPABASE_URL') if hasattr(st, 'secrets') else os.environ.get('SUPABASE_URL', 'https://jvjlhxodmbkodzmggwpu.supabase.co')
    key = st.secrets.get('SUPABASE_KEY') if hasattr(st, 'secrets') else os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2amxoeG9kbWJrb2R6bWdnd3B1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyMjMxOTAsImV4cCI6MjA3Nzc5OTE5MH0.ai65vVW816bNAV56XiuRxp5PE5IhBkMGPx3IbxfPh8c')

    try:
        client = create_client(url, key)
        return client, None
    except Exception as e:
        return None, str(e)

supabase, error = init_supabase()

st.title("🔍 PROJ344 Error Logs Viewer")
st.markdown("### Check error logs from Mac Mini processing")

if error:
    st.error(f"Connection Error: {error}")
    st.stop()

st.success("✅ Connected to Supabase")
st.markdown("---")

# Check if error_logs table exists and fetch data
try:
    st.subheader("📋 Error Logs Table")

    # Get count first
    count_response = supabase.table('error_logs').select('*', count='exact').limit(0).execute()
    total_logs = count_response.count if hasattr(count_response, 'count') else 0

    st.metric("Total Error Logs", total_logs)

    if total_logs > 0:
        # Fetch recent logs
        response = supabase.table('error_logs').select('*').order('uploaded_at', desc=True).limit(50).execute()

        if response.data:
            df = pd.DataFrame(response.data)

            # Summary stats
            st.markdown("#### Summary Statistics")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if 'error_count' in df.columns:
                    st.metric("Total Errors", df['error_count'].sum())

            with col2:
                if 'warning_count' in df.columns:
                    st.metric("Total Warnings", df['warning_count'].sum())

            with col3:
                if 'total_lines' in df.columns:
                    st.metric("Total Log Lines", df['total_lines'].sum())

            with col4:
                st.metric("Log Files", len(df))

            st.markdown("---")
            st.markdown("#### Recent Error Logs")

            # Display table
            display_cols = ['filename', 'uploaded_at', 'error_count', 'warning_count', 'total_lines', 'analysis_summary']
            available_cols = [col for col in display_cols if col in df.columns]

            st.dataframe(df[available_cols], use_container_width=True)

            st.markdown("---")
            st.markdown("#### View Log Content")

            # Select a log to view
            log_options = df.apply(lambda row: f"{row['filename']} - {row['uploaded_at']} ({row['error_count']} errors)", axis=1).tolist()
            selected_idx = st.selectbox("Select log to view:", range(len(log_options)), format_func=lambda x: log_options[x])

            if selected_idx is not None:
                selected_log = df.iloc[selected_idx]

                st.markdown(f"**File:** {selected_log['filename']}")
                st.markdown(f"**Uploaded:** {selected_log['uploaded_at']}")
                st.markdown(f"**Errors:** {selected_log['error_count']} | **Warnings:** {selected_log['warning_count']}")

                if 'analysis_summary' in selected_log:
                    st.info(f"**Summary:** {selected_log['analysis_summary']}")

                if 'content' in selected_log and selected_log['content']:
                    st.markdown("#### Full Log Content")

                    # Parse content to highlight errors
                    content = selected_log['content']
                    lines = content.split('\n')

                    # Show error lines first
                    error_lines = [line for line in lines if any(keyword in line.upper() for keyword in ['ERROR', 'CRITICAL', 'FATAL'])]

                    if error_lines:
                        st.markdown("##### 🔴 Error Lines")
                        with st.expander(f"View {len(error_lines)} error line(s)", expanded=True):
                            for i, line in enumerate(error_lines[:30], 1):
                                st.code(f"{i}. {line}", language="log")

                    # Show warning lines
                    warning_lines = [line for line in lines if 'WARNING' in line.upper()]

                    if warning_lines:
                        st.markdown("##### ⚠️ Warning Lines")
                        with st.expander(f"View {len(warning_lines)} warning line(s)"):
                            for i, line in enumerate(warning_lines[:30], 1):
                                st.code(f"{i}. {line}", language="log")

                    # Show full content
                    st.markdown("##### 📄 Full Log")
                    with st.expander("View complete log content"):
                        st.text_area("Full Content", content, height=500)
        else:
            st.info("No error logs found in database")
    else:
        st.info("No error logs have been uploaded yet")
        st.markdown("""
        **To upload error logs:**
        1. Use the error_log_uploader.py dashboard
        2. Or upload logs manually from Mac Mini processing scripts
        """)

except Exception as e:
    st.error(f"❌ Error accessing error_logs table: {e}")
    st.markdown("""
    **Possible issues:**
    - The `error_logs` table doesn't exist in Supabase
    - You don't have permission to read from the table
    - The table schema doesn't match expected columns

    **To fix:**
    1. Check if table exists in Supabase dashboard
    2. Run the schema creation script: `supabase_error_logs_schema.sql`
    3. Verify RLS policies allow reading
    """)

st.markdown("---")
st.caption(f"Connected to: {os.environ.get('SUPABASE_URL', 'N/A')[:40]}...")

# Refresh button
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()
