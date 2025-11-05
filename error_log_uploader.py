#!/usr/bin/env python3
"""
Error Log Uploader for PROJ344
Upload, analyze, and store error logs in Supabase
"""

import streamlit as st
import os
from datetime import datetime
import pandas as pd
import re
from io import StringIO

try:
    from supabase import create_client
except ImportError:
    st.error("❌ Install supabase: pip3 install supabase")
    st.stop()

# Import custom styling if available
try:
    from proj344_style import inject_custom_css, render_alert
    HAS_CUSTOM_STYLE = True
except ImportError:
    HAS_CUSTOM_STYLE = False

st.set_page_config(
    page_title="Error Log Uploader - PROJ344",
    page_icon="📤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SUPABASE CONNECTION
# ============================================================================

@st.cache_resource
def init_supabase():
    """Initialize Supabase client"""
    # Try Streamlit secrets first, then environment variables, then defaults
    url = st.secrets.get('SUPABASE_URL') if hasattr(st, 'secrets') else os.environ.get('SUPABASE_URL', 'https://jvjlhxodmbkodzmggwpu.supabase.co')
    key = st.secrets.get('SUPABASE_KEY') if hasattr(st, 'secrets') else os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2amxoeG9kbWJrb2R6bWdnd3B1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyMjMxOTAsImV4cCI6MjA3Nzc5OTE5MH0.ai65vVW816bNAV56XiuRxp5PE5IhBkMGPx3IbxfPh8c')

    try:
        client = create_client(url, key)
        return client, None
    except Exception as e:
        return None, str(e)

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

def save_log_to_database(client, filename, content, file_size, file_type, analysis_data):
    """Save uploaded log file to Supabase"""
    try:
        log_data = {
            'filename': filename,
            'content': content,
            'file_size': file_size,
            'file_type': file_type,
            'uploaded_at': datetime.now().isoformat(),
            'error_count': analysis_data.get('error_count', 0),
            'warning_count': analysis_data.get('warning_count', 0),
            'total_lines': analysis_data.get('total_lines', 0),
            'analysis_summary': analysis_data.get('summary', '')
        }

        response = client.table('error_logs').insert(log_data).execute()
        return response.data[0] if response.data else None

    except Exception as e:
        st.error(f"❌ Database error: {e}")
        return None

@st.cache_data(ttl=60)
def get_recent_logs(_client, limit=10):
    """Fetch recent uploaded logs"""
    try:
        response = _client.table('error_logs').select('*').order('uploaded_at', desc=True).limit(limit).execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error fetching logs: {e}")
        return pd.DataFrame()

def delete_log(client, log_id):
    """Delete a log entry"""
    try:
        client.table('error_logs').delete().eq('id', log_id).execute()
        return True
    except Exception as e:
        st.error(f"❌ Error deleting log: {e}")
        return False

# ============================================================================
# LOG ANALYSIS
# ============================================================================

def analyze_log_content(content):
    """Analyze log file content and extract metrics"""
    lines = content.split('\n')

    # Count different log levels
    error_count = sum(1 for line in lines if re.search(r'\b(ERROR|CRITICAL|FATAL)\b', line, re.IGNORECASE))
    warning_count = sum(1 for line in lines if re.search(r'\bWARNING\b', line, re.IGNORECASE))
    info_count = sum(1 for line in lines if re.search(r'\bINFO\b', line, re.IGNORECASE))
    debug_count = sum(1 for line in lines if re.search(r'\bDEBUG\b', line, re.IGNORECASE))

    # Extract error patterns
    error_lines = [line for line in lines if re.search(r'\b(ERROR|CRITICAL|FATAL)\b', line, re.IGNORECASE)]
    warning_lines = [line for line in lines if re.search(r'\bWARNING\b', line, re.IGNORECASE)]

    # Extract timestamps if present
    timestamp_pattern = r'\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}'
    timestamps = re.findall(timestamp_pattern, content)

    # Generate summary
    summary = f"Total: {len(lines)} lines | Errors: {error_count} | Warnings: {warning_count} | Info: {info_count}"

    return {
        'total_lines': len(lines),
        'error_count': error_count,
        'warning_count': warning_count,
        'info_count': info_count,
        'debug_count': debug_count,
        'error_lines': error_lines[:50],  # First 50 errors
        'warning_lines': warning_lines[:50],  # First 50 warnings
        'timestamps': timestamps,
        'summary': summary,
        'has_timestamps': len(timestamps) > 0
    }

def display_analysis(analysis):
    """Display log analysis results"""
    st.subheader("📊 Log Analysis")

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Lines", f"{analysis['total_lines']:,}")
    with col2:
        st.metric("Errors", analysis['error_count'], delta=None if analysis['error_count'] == 0 else "Review needed", delta_color="inverse")
    with col3:
        st.metric("Warnings", analysis['warning_count'])
    with col4:
        st.metric("Info/Debug", analysis['info_count'] + analysis['debug_count'])

    # Error details
    if analysis['error_count'] > 0:
        st.markdown("### 🔴 Error Lines")
        if HAS_CUSTOM_STYLE:
            render_alert(f"Found {analysis['error_count']} error(s) in log file", "error")
        else:
            st.error(f"Found {analysis['error_count']} error(s) in log file")

        with st.expander(f"View First {min(50, len(analysis['error_lines']))} Errors", expanded=True):
            for idx, error in enumerate(analysis['error_lines'][:20], 1):
                st.code(f"{idx}. {error.strip()}", language="log")

    # Warning details
    if analysis['warning_count'] > 0:
        st.markdown("### ⚠️ Warning Lines")
        with st.expander(f"View First {min(50, len(analysis['warning_lines']))} Warnings"):
            for idx, warning in enumerate(analysis['warning_lines'][:20], 1):
                st.code(f"{idx}. {warning.strip()}", language="log")

    # Timestamp analysis
    if analysis['has_timestamps']:
        st.markdown("### 🕐 Timeline")
        st.info(f"Found {len(analysis['timestamps'])} timestamped entries")
        if len(analysis['timestamps']) > 0:
            st.write(f"**First entry:** {analysis['timestamps'][0]}")
            st.write(f"**Last entry:** {analysis['timestamps'][-1]}")

# ============================================================================
# FILE UPLOAD UI
# ============================================================================

def upload_section(client):
    """File upload interface"""
    st.header("📤 Upload Error Log File")

    uploaded_file = st.file_uploader(
        "Choose a log file",
        type=['log', 'txt', 'csv', 'out', 'err'],
        help="Supported formats: .log, .txt, .csv, .out, .err (max 200MB)",
        accept_multiple_files=False
    )

    if uploaded_file is not None:
        # Display file info
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**📄 Filename:** {uploaded_file.name}")
        with col2:
            st.info(f"**📊 Size:** {uploaded_file.size / 1024:.2f} KB")
        with col3:
            st.info(f"**📝 Type:** {uploaded_file.type or 'text/plain'}")

        try:
            # Read file content
            content = uploaded_file.read().decode('utf-8', errors='ignore')

            # Analyze content
            st.markdown("---")
            analysis = analyze_log_content(content)
            display_analysis(analysis)

            # Content preview
            st.markdown("---")
            st.subheader("📝 File Content Preview")
            preview_lines = min(100, analysis['total_lines'])
            st.text_area(
                f"First {preview_lines} lines:",
                '\n'.join(content.split('\n')[:preview_lines]),
                height=300
            )

            # Action buttons
            st.markdown("---")
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("💾 Save to Database", type="primary", use_container_width=True):
                    with st.spinner("Saving to database..."):
                        result = save_log_to_database(
                            client,
                            uploaded_file.name,
                            content,
                            uploaded_file.size,
                            uploaded_file.type or 'text/plain',
                            analysis
                        )

                        if result:
                            st.success(f"✅ Successfully saved log to database (ID: {result.get('id')})")
                            st.balloons()
                        else:
                            st.error("❌ Failed to save log to database")

            with col2:
                # Download analyzed report
                report = f"""
ERROR LOG ANALYSIS REPORT
========================
File: {uploaded_file.name}
Upload Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
File Size: {uploaded_file.size / 1024:.2f} KB

SUMMARY
-------
{analysis['summary']}

DETAILS
-------
Total Lines: {analysis['total_lines']:,}
Errors: {analysis['error_count']}
Warnings: {analysis['warning_count']}
Info Messages: {analysis['info_count']}
Debug Messages: {analysis['debug_count']}
Timestamps Found: {len(analysis['timestamps'])}

TOP ERRORS
----------
{''.join([f'{i+1}. {err}\n' for i, err in enumerate(analysis['error_lines'][:10])])}

TOP WARNINGS
------------
{''.join([f'{i+1}. {warn}\n' for i, warn in enumerate(analysis['warning_lines'][:10])])}
                """

                st.download_button(
                    "📥 Download Report",
                    data=report,
                    file_name=f"analysis_{uploaded_file.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            with col3:
                st.download_button(
                    "📄 Download Original",
                    data=content,
                    file_name=uploaded_file.name,
                    mime="text/plain",
                    use_container_width=True
                )

        except UnicodeDecodeError:
            st.error("❌ Unable to decode file. Please ensure it's a text-based log file.")
        except Exception as e:
            st.error(f"❌ Error processing file: {e}")

# ============================================================================
# RECENT LOGS VIEW
# ============================================================================

def recent_logs_section(client):
    """Display recently uploaded logs"""
    st.header("📋 Recently Uploaded Logs")

    df = get_recent_logs(client, limit=20)

    if df.empty:
        st.info("No logs uploaded yet. Upload your first log file above!")
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Logs", len(df))
    with col2:
        st.metric("Total Errors", df['error_count'].sum() if 'error_count' in df.columns else 0)
    with col3:
        st.metric("Total Warnings", df['warning_count'].sum() if 'warning_count' in df.columns else 0)
    with col4:
        total_size = df['file_size'].sum() / (1024 * 1024) if 'file_size' in df.columns else 0
        st.metric("Total Size", f"{total_size:.2f} MB")

    # Display table
    st.markdown("---")

    # Format dataframe for display
    display_df = df.copy()
    if 'uploaded_at' in display_df.columns:
        display_df['uploaded_at'] = pd.to_datetime(display_df['uploaded_at']).dt.strftime('%Y-%m-%d %H:%M')
    if 'file_size' in display_df.columns:
        display_df['file_size_kb'] = (display_df['file_size'] / 1024).round(2)

    # Select columns to display
    display_cols = ['id', 'filename', 'uploaded_at', 'file_size_kb', 'error_count', 'warning_count', 'total_lines']
    available_cols = [col for col in display_cols if col in display_df.columns]

    st.dataframe(
        display_df[available_cols],
        use_container_width=True,
        hide_index=True
    )

    # View/Delete specific log
    st.markdown("---")
    st.subheader("🔍 View Log Details")

    log_ids = df['id'].tolist() if 'id' in df.columns else []
    filenames = df['filename'].tolist() if 'filename' in df.columns else []

    if log_ids:
        selected_idx = st.selectbox(
            "Select a log to view:",
            range(len(log_ids)),
            format_func=lambda x: f"{filenames[x]} (ID: {log_ids[x]})"
        )

        if selected_idx is not None:
            selected_log = df.iloc[selected_idx]

            col1, col2 = st.columns([3, 1])

            with col1:
                st.info(f"**File:** {selected_log.get('filename', 'N/A')}")
                st.info(f"**Uploaded:** {selected_log.get('uploaded_at', 'N/A')}")
                if 'analysis_summary' in selected_log:
                    st.info(f"**Summary:** {selected_log['analysis_summary']}")

            with col2:
                if st.button("🗑️ Delete Log", type="secondary"):
                    if delete_log(client, selected_log['id']):
                        st.success("✅ Log deleted successfully")
                        st.rerun()

            # Display content
            if 'content' in selected_log and selected_log['content']:
                with st.expander("📄 View Full Content"):
                    st.text_area(
                        "Log Content:",
                        selected_log['content'],
                        height=400,
                        key=f"content_{selected_log['id']}"
                    )

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    # Apply custom styling
    if HAS_CUSTOM_STYLE:
        inject_custom_css()

    # Initialize Supabase
    client, error = init_supabase()

    if error or not client:
        st.error(f"❌ Supabase connection failed: {error}")
        st.info("Check your SUPABASE_URL and SUPABASE_KEY environment variables")
        st.stop()

    # Header
    st.title("📤 Error Log Uploader")
    st.markdown(f"**PROJ344 Log Management System** | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.markdown("---")

    # Sidebar
    st.sidebar.title("📊 Navigation")
    page = st.sidebar.radio(
        "Choose a section:",
        ["Upload New Log", "Recent Logs", "Help"]
    )

    st.sidebar.markdown("---")
    st.sidebar.info("""
    **Supported Formats:**
    - .log (Log files)
    - .txt (Text files)
    - .csv (CSV logs)
    - .out (Output files)
    - .err (Error files)

    **Max Size:** 200 MB
    """)

    # Main content
    if page == "Upload New Log":
        upload_section(client)

    elif page == "Recent Logs":
        recent_logs_section(client)

    elif page == "Help":
        st.header("📖 Help & Documentation")

        st.markdown("""
        ## How to Use

        ### 1️⃣ Upload a Log File
        - Click "Browse files" or drag-and-drop
        - Supported formats: .log, .txt, .csv, .out, .err
        - Maximum size: 200 MB

        ### 2️⃣ Review Analysis
        - Automatic analysis shows errors, warnings, and metrics
        - Preview the first 100 lines
        - View detailed error/warning breakdowns

        ### 3️⃣ Save or Export
        - **Save to Database**: Store in Supabase for permanent access
        - **Download Report**: Get a text report of the analysis
        - **Download Original**: Get the original file back

        ### 4️⃣ Manage Logs
        - View recently uploaded logs
        - Search and filter logs
        - Delete old logs
        - View full log content

        ## Database Setup

        Before using this tool, make sure you've created the `error_logs` table in Supabase.
        Run the SQL schema provided in `supabase_error_logs_schema.sql`.

        ## Support

        For issues or questions, contact the PROJ344 development team.
        """)

if __name__ == "__main__":
    main()
