import streamlit as st
import glob
import os

st.set_page_config(page_title="Log File Viewer", layout="wide")

st.title("📋 Log File Viewer")

# Find log files
log_files = []
if os.path.exists("department_organizer.log"):
    log_files.append("department_organizer.log")

# Find file_changes files
changes_files = sorted(glob.glob("dept_changes_*.txt"), reverse=True)
log_files.extend(changes_files)

if not log_files:
    st.error("No log files found!")
else:
    # Sidebar for file selection
    st.sidebar.header("Select File")
    selected_file = st.sidebar.radio("Available files:", log_files)

    # Display file info
    if selected_file and os.path.exists(selected_file):
        file_size = os.path.getsize(selected_file)
        file_modified = os.path.getmtime(selected_file)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("File Size", f"{file_size:,} bytes")
        with col2:
            from datetime import datetime
            st.metric("Last Modified", datetime.fromtimestamp(file_modified).strftime("%Y-%m-%d %H:%M:%S"))

        st.divider()

        # Read and display file content
        try:
            with open(selected_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Add search functionality
            search_term = st.text_input("🔍 Search in file:", "")

            if search_term:
                lines = content.split('\n')
                matching_lines = [line for line in lines if search_term.lower() in line.lower()]
                st.info(f"Found {len(matching_lines)} matching lines")
                content_to_display = '\n'.join(matching_lines)
            else:
                content_to_display = content

            # Display content
            st.subheader(f"📄 {selected_file}")
            st.text_area("File Content", content_to_display, height=600, disabled=True)

            # Download button
            st.download_button(
                label="⬇️ Download File",
                data=content,
                file_name=selected_file,
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        st.warning("File not found!")
